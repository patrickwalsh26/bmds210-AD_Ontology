#!/usr/bin/env python3
"""
Live terminal demo — ADO conditional reasoning vs. condition-blind baseline.

Designed for 30-second presentation demo. Runs three clinically distinct
scenarios against Margaret Chen's directive and prints a clean side-by-side
comparison showing exactly where condition-blind reasoning breaks.

Usage:
    python evaluation/demo_query.py

Expected output shows the contrast in ~10 seconds of computation.
"""

from __future__ import annotations
import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = Path(__file__).resolve().parent
for p in (ROOT, EVAL_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from owlready2 import get_ontology
from ado.query_evaluation import evaluate_vignette
from baselines import find_matching_preferences_condition_blind

DEMO_OWL = ROOT / "data" / "populated" / "ado_demo_presentation.owl"

# ── Scenarios chosen to clearly show conditional reasoning ─────────────────────
# Margaret Chen has: "No CPR if NYHA IV and no reversible cause" (Absolute)
#                    "Acute dialysis OK if cardiorenal syndrome is reversible" (Conditional)
#                    "No indefinite ventilation — ever" (Absolute)

DEMO_SCENARIOS = [
    {
        "id": "DEMO-1",
        "title": "Cardiac arrest, NYHA IV, NO reversible cause",
        "description": "Core case: all conditions met → should be unambiguous DNR",
        "query_intervention": "CPR",
        "scenario_state": {
            "conditions": ["CardiacArrest"],
            "nyha_class": "NYHA_ClassIV",
            "reversible_cause": False,
        },
        "expected_decision": "no",
        "expected_match_type": "clear",
    },
    {
        "id": "DEMO-2",
        "title": "Cardiac arrest, NYHA III, reversible hyperkalemia",
        "description": "Conditions NOT met → same directive, opposite answer",
        "query_intervention": "CPR",
        "scenario_state": {
            "conditions": ["CardiacArrest"],
            "nyha_class": "NYHA_ClassIII",
            "reversible_cause": True,
        },
        "expected_decision": "partial",
        "expected_match_type": "partial",
    },
    {
        "id": "DEMO-3",
        "title": "Cardiorenal syndrome, reversible AKI",
        "description": "Acute dialysis conditional preference — conditions met",
        "query_intervention": "AcuteDialysis",
        "scenario_state": {
            "conditions": ["CardiorenalSyndrome"],
            "reversible_cause": True,
        },
        "expected_decision": "yes",
        "expected_match_type": "conditional",
    },
    {
        "id": "DEMO-4",
        "title": "Respiratory failure, day 21 on ventilator",
        "description": "Past 14-day time bound → indefinite ventilation refused",
        "query_intervention": "IndefiniteVentilation",
        "scenario_state": {
            "conditions": ["RespiratoryFailure"],
            "reversible_cause": False,
        },
        "expected_decision": "no",
        "expected_match_type": "clear",
    },
]


# ── Display helpers ────────────────────────────────────────────────────────────

ICON = {"yes": "✓ YES", "no": "✗ NO", "partial": "~ PARTIAL",
        "no_coverage": "— NO COV.", "vague": "? VAGUE"}

def icon(d: str) -> str:
    return ICON.get(d, d.upper())

def match_label(mt: str) -> str:
    labels = {"clear": "CLEAR", "partial": "PARTIAL", "vague": "VAGUE",
              "no_coverage": "NO COV."}
    return labels.get(mt, mt.upper())

def check(system_val, expected_val) -> str:
    return "✓" if system_val == expected_val else "✗"


# ── Main demo ─────────────────────────────────────────────────────────────────

def main():
    if not DEMO_OWL.exists():
        print(f"ERROR: Demo OWL not found at {DEMO_OWL}")
        print("Run first: python evaluation/build_demo_owl.py")
        sys.exit(1)

    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  ADO Live Demo — Margaret Chen, 68yo, LVAD, Advanced HF             ║")
    print("║  Directive: 13 structured preferences, all 5 decision-point domains  ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()

    with contextlib.redirect_stdout(io.StringIO()):
        onto = get_ontology(str(DEMO_OWL.resolve())).load()
    patients = list(onto.search(type=onto.Patient))
    # Use Margaret Chen (most preferences)
    patient = max(patients, key=lambda p: len(p.hasPreference) if p.hasPreference else 0)
    n_prefs = len(patient.hasPreference) if patient.hasPreference else 0
    print(f"  Patient loaded: {patient.label[0] if patient.label else patient.name}")
    print(f"  Preferences encoded: {n_prefs}")
    print()

    header = (
        f"{'Scenario':<6}  {'Intervention':<20}  "
        f"{'ADO Decision':>12}  {'Match':>8}  "
        f"{'Blind Decision':>14}  {'Blind Match':>10}  "
        f"{'ADO wins?':>9}"
    )
    sep = "─" * len(header)
    print(header)
    print(sep)

    for v in DEMO_SCENARIOS:
        ado   = evaluate_vignette(onto, patient, v)
        blind = evaluate_vignette(onto, patient, v,
                                  matcher=find_matching_preferences_condition_blind)

        ado_d  = ado["system_decision"]
        ado_mt = ado["system_match_type"]
        bl_d   = blind["system_decision"]
        bl_mt  = blind["system_match_type"]

        ado_correct   = ado_d == v["expected_decision"]
        blind_correct = bl_d  == v["expected_decision"]

        ado_wins = ado_correct and not blind_correct
        both_correct = ado_correct and blind_correct

        flag = "← ADO WINS" if ado_wins else ("both ok" if both_correct else "both fail")

        print(
            f"{v['id']:<6}  {v['query_intervention']:<20}  "
            f"{icon(ado_d):>12}  {match_label(ado_mt):>8}  "
            f"{icon(bl_d):>14}  {match_label(bl_mt):>10}  "
            f"{flag:>9}"
        )

    print(sep)
    print()
    print("  Key insight: Same directive — DEMO-1 and DEMO-2 query the same CPR preference.")
    print("  ADO checks conditions → two different correct answers.")
    print("  Condition-blind baseline cannot distinguish them → fails on one.")
    print()

    # Detailed printout for DEMO-1 and DEMO-2
    for v in DEMO_SCENARIOS[:2]:
        ado = evaluate_vignette(onto, patient, v)
        print(f"  ┌─ {v['id']}: {v['title']}")
        print(f"  │  {v['description']}")
        print(f"  │  ADO: {v['query_intervention']} → {ado['system_decision'].upper()} ({ado['system_match_type']})")
        if ado.get("matched_preference"):
            pref = ado["matched_preference"]
            print(f"  │  Matched: '{getattr(pref, 'label', [pref.name])[0] if hasattr(pref, 'label') else pref.name}'")
        print(f"  └─ Scenario state: {v['scenario_state']}")
        print()


if __name__ == "__main__":
    main()
