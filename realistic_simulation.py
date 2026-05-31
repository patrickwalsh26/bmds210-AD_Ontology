#!/usr/bin/env python3
"""
Multi-patient, multi-scenario simulation with messy real-world profiles.

Runs ~520 structured query cells (20 patients × 12 scenarios × relevant interventions),
scores ADO against an independent reference oracle and flat checkbox baselines.

Usage:
    python realistic_simulation.py
    python realistic_simulation.py --json docs/cohort_simulation_results.json
    python realistic_simulation.py --degrade-encoding   # strip activation fields (stress test)
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from eval_baselines import find_matching_preferences_condition_blind
from eval_data.patient_cohort import PATIENT_COHORT
from eval_data.scenario_battery import SCENARIO_BATTERY
from oracle_gold import checkbox_baseline, reference_expected
from preference_input import load_ontology, populate_patient
from query_evaluation import evaluate_vignette

ROOT = Path(__file__).resolve().parent


def cohort_to_patient_data(record: dict) -> dict:
    return {
        "patient_id": record["patient_id"],
        "patient_name": record["patient_name"],
        "source_document": {
            "type": "living_will",
            "label": record.get("template_source", "Advance directive"),
        },
        "preferences": copy.deepcopy(record.get("preferences", [])),
    }


def maybe_degrade_preferences(prefs: list) -> list:
    """Simulate incomplete chart abstraction: drop activation_conditions."""
    out = []
    for p in prefs:
        q = copy.deepcopy(p)
        if q.get("activation_conditions"):
            q.pop("activation_conditions", None)
            q["type"] = "clear"
        out.append(q)
    return out


def load_patient_ontology(patient_data: dict):
    onto = load_ontology()
    with contextlib.redirect_stdout(io.StringIO()):
        populate_patient(onto, patient_data)
    patients = list(onto.search(type=onto.Patient))
    if not patients:
        raise RuntimeError("No patient created")
    patient = max(patients, key=lambda p: len(p.hasPreference) if p.hasPreference else 0)
    return onto, patient


def run_simulation(degrade_encoding: bool = False) -> dict:
    rows = []
    for prec in PATIENT_COHORT:
        pdata = cohort_to_patient_data(prec)
        if degrade_encoding:
            pdata["preferences"] = maybe_degrade_preferences(pdata["preferences"])

        onto, patient = load_patient_ontology(pdata)
        messy = prec.get("messy_level", "typical")

        for scenario in SCENARIO_BATTERY:
            state = scenario["scenario_state"]
            for intervention in scenario["interventions"]:
                vignette = {
                    "id": f"{prec['patient_id']}_{scenario['id']}_{intervention}",
                    "description": scenario["description"],
                    "query_intervention": intervention,
                    "scenario_state": state,
                    "expected": reference_expected(pdata, state, intervention),
                }
                ref = vignette["expected"]
                ado = evaluate_vignette(onto, patient, vignette)
                blind = evaluate_vignette(
                    onto, patient, vignette,
                    matcher=find_matching_preferences_condition_blind,
                )
                checkbox = checkbox_baseline(pdata, state, intervention)
                checkbox_blank = checkbox_baseline(
                    pdata, state, intervention, default_when_no_prefs="no_coverage",
                )

                row = {
                    "patient_id": prec["patient_id"],
                    "messy_level": messy,
                    "scenario_id": scenario["id"],
                    "intervention": intervention,
                    "ref_decision": ref["decision"],
                    "ref_match": ref["match_type"],
                    "ado_decision": ado["system_decision"],
                    "ado_match": ado["system_match_type"],
                    "blind_decision": blind["system_decision"],
                    "checkbox_decision": checkbox["decision"],
                    "ado_decision_ok": ado["system_decision"] == ref["decision"],
                    "ado_match_ok": ado["system_match_type"] == ref["match_type"],
                    "blind_decision_ok": blind["system_decision"] == ref["decision"],
                    "checkbox_decision_ok": checkbox["decision"] == ref["decision"],
                    "checkbox_blank_ok": checkbox_blank["decision"] == ref["decision"],
                }
                # Value-add: ADO flags nuance that flat checkbox collapses
                nuanced_ref = ref["match_type"] in ("partial", "vague", "no_coverage") or ref[
                    "decision"
                ] in ("partial", "vague", "no_coverage")
                row["checkbox_overconfident"] = (
                    nuanced_ref and checkbox["decision"] in ("yes", "no")
                    and checkbox["match_type"] == "clear"
                )
                rows.append(row)

    return aggregate(rows, degrade_encoding=degrade_encoding)


def aggregate(rows: list, degrade_encoding: bool) -> dict:
    n = len(rows)
    dec_ok = sum(1 for r in rows if r["ado_decision_ok"])
    mt_ok = sum(1 for r in rows if r["ado_match_ok"])
    blind_ok = sum(1 for r in rows if r["blind_decision_ok"])
    cb_ok = sum(1 for r in rows if r["checkbox_decision_ok"])
    cb_blank_ok = sum(1 for r in rows if r["checkbox_blank_ok"])
    overconf = sum(1 for r in rows if r["checkbox_overconfident"])
    covered = [r for r in rows if r["ref_match"] not in ("no_coverage",)]
    covered_dec = sum(1 for r in covered if r["ado_decision_ok"])

    by_messy = defaultdict(lambda: {"n": 0, "ado_dec": 0, "ado_mt": 0, "blind": 0, "cb": 0})
    for r in rows:
        b = by_messy[r["messy_level"]]
        b["n"] += 1
        b["ado_dec"] += int(r["ado_decision_ok"])
        b["ado_mt"] += int(r["ado_match_ok"])
        b["blind"] += int(r["blind_decision_ok"])
        b["cb"] += int(r["checkbox_decision_ok"])

    failures = [
        r for r in rows
        if not r["ado_decision_ok"] or not r["ado_match_ok"]
    ][:25]

    return {
        "degrade_encoding": degrade_encoding,
        "n_cells": n,
        "n_patients": len(PATIENT_COHORT),
        "n_scenarios": len(SCENARIO_BATTERY),
        "ado_decision_accuracy": dec_ok / n if n else 0,
        "ado_match_type_accuracy": mt_ok / n if n else 0,
        "condition_blind_accuracy": blind_ok / n if n else 0,
        "checkbox_accuracy": cb_ok / n if n else 0,
        "checkbox_blank_accuracy": cb_blank_ok / n if n else 0,
        "checkbox_overconfident_cells": overconf,
        "ado_accuracy_on_covered_cells": covered_dec / len(covered) if covered else 0,
        "n_covered_cells": len(covered),
        "n_no_coverage_cells": n - len(covered),
        "by_messy_level": {
            k: {
                "n": v["n"],
                "ado_decision_pct": round(100 * v["ado_dec"] / v["n"], 1),
                "ado_match_pct": round(100 * v["ado_mt"] / v["n"], 1),
                "blind_pct": round(100 * v["blind"] / v["n"], 1),
                "checkbox_pct": round(100 * v["cb"] / v["n"], 1),
            }
            for k, v in sorted(by_messy.items())
        },
        "sample_failures": failures,
        "rows": rows,
    }


def print_report(summary: dict) -> None:
    n = summary["n_cells"]
    print("=" * 72)
    print("  MULTI-PATIENT COHORT SIMULATION (realistic / messy profiles)")
    print("=" * 72)
    print(f"  Cells evaluated     : {n} ({summary['n_patients']} patients × "
          f"{summary['n_scenarios']} scenarios × queried interventions)")
    if summary["degrade_encoding"]:
        print("  Mode                : DEGRADED (activation conditions stripped)")
    print()
    print(f"  ADO decision vs ref : {summary['ado_decision_accuracy']*100:.1f}%")
    print(f"  ADO match-type vs ref: {summary['ado_match_type_accuracy']*100:.1f}%")
    print(f"  Condition-blind     : {summary['condition_blind_accuracy']*100:.1f}%")
    print(f"  Checkbox (flat POLST, silent→full code): {summary['checkbox_accuracy']*100:.1f}%")
    print(f"  Checkbox (silent→no coverage)          : {summary['checkbox_blank_accuracy']*100:.1f}%")
    print(f"  ADO on cells WITH directive coverage   : "
          f"{summary['ado_accuracy_on_covered_cells']*100:.1f}% "
          f"({summary['n_covered_cells']}/{summary['n_cells']} cells)")
    print(f"  Checkbox overconfident (nuanced gold → flat yes/no): "
          f"{summary['checkbox_overconfident_cells']} cells")
    print()
    print("  By messy_level tag:")
    for level, stats in summary["by_messy_level"].items():
        print(f"    {level:22s} n={stats['n']:3d}  "
              f"ADO dec {stats['ado_decision_pct']:5.1f}%  "
              f"match {stats['ado_match_pct']:5.1f}%  "
              f"blind {stats['blind_pct']:5.1f}%  "
              f"checkbox {stats['checkbox_pct']:5.1f}%")
    print()
    fails = summary["sample_failures"]
    if fails:
        print(f"  Sample ADO≠reference cells (up to {len(fails)}):")
        for r in fails[:12]:
            print(f"    {r['patient_id']} {r['scenario_id']} {r['intervention']}: "
                  f"ref {r['ref_decision']}/{r['ref_match']} → "
                  f"ADO {r['ado_decision']}/{r['ado_match']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Multi-patient cohort simulation")
    parser.add_argument("--json", type=str, help="Write full results JSON to path")
    parser.add_argument("--degrade-encoding", action="store_true",
                        help="Strip activation conditions (encoding fidelity stress)")
    args = parser.parse_args()

    summary = run_simulation(degrade_encoding=args.degrade_encoding)
    print_report(summary)

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {k: v for k, v in summary.items() if k != "rows"}
        payload["row_count"] = len(summary["rows"])
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Wrote summary to {out}")

    # Exit non-zero if ADO decision accuracy very low (sanity for CI)
    if summary["ado_decision_accuracy"] < 0.5:
        sys.exit(1)


if __name__ == "__main__":
    main()
