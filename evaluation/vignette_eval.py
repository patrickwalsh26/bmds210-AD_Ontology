#!/usr/bin/env python3
"""
Vignette evaluation: development (16) + held-out (10) splits and baselines.

  python vignette_eval.py --suite all
  python vignette_eval.py --suite holdout --baseline none
  python vignette_eval.py --suite dev --baseline condition-blind
"""
import sys
from pathlib import Path as _Path
_ADO_ROOT = _Path(__file__).resolve().parents[1]
_ADO_EVAL = _Path(__file__).resolve().parent
for _p in (_ADO_ROOT, _ADO_EVAL):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


import argparse
import sys
from pathlib import Path

from owlready2 import get_ontology

from baselines import find_matching_preferences_condition_blind
from ado.holdout_vignettes import HOLDOUT_VIGNETTES
from ado.query_evaluation import VIGNETTES, evaluate_vignette


def run_suite(onto, patient, vignettes, matcher=None):
    results = [evaluate_vignette(onto, patient, v, matcher=matcher) for v in vignettes]
    return {
        "total": len(results),
        "decision_accuracy": sum(1 for r in results if r["decision_correct"]),
        "match_type_accuracy": sum(1 for r in results if r["match_type_correct"]),
        "results": results,
    }


def print_summary(name, summary):
    total = summary["total"]
    cd, cm = summary["decision_accuracy"], summary["match_type_accuracy"]
    print(f"\n{'#' * 80}\n  {name} (n={total})\n{'#' * 80}")
    for r in summary["results"]:
        ok = r["decision_correct"] and r["match_type_correct"]
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {r['id']}: got {r['system_decision']}/{r['system_match_type']} "
              f"expected {r['expected_decision']}/{r['expected_match_type']}")
    print(f"\n  Decision accuracy   : {cd}/{total} ({100*cd/total:.0f}%)")
    print(f"  Match-type accuracy : {cm}/{total} ({100*cm/total:.0f}%)")
    fails = [r["id"] for r in summary["results"]
             if not (r["decision_correct"] and r["match_type_correct"])]
    if fails:
        print(f"  Failures: {', '.join(fails)}")
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owl", default="data/populated/ado_jane_doe_001.owl")
    ap.add_argument("--suite", choices=("dev", "holdout", "all"), default="all")
    ap.add_argument("--baseline", choices=("none", "condition-blind"), default="none")
    args = ap.parse_args()

    owl_path = Path(args.owl)
    if not owl_path.exists():
        print(f"ERROR: {owl_path} not found. Run: python preference_input.py --example")
        sys.exit(1)

    onto = get_ontology(str(owl_path.resolve())).load()
    patients = list(onto.search(type=onto.Patient))
    patient = max(patients, key=lambda p: len(p.hasPreference) if p.hasPreference else 0)

    matcher = (
        find_matching_preferences_condition_blind
        if args.baseline == "condition-blind"
        else None
    )

    suites = []
    if args.suite in ("dev", "all"):
        suites.append(("Development", VIGNETTES))
    if args.suite in ("holdout", "all"):
        suites.append(("Held-out", HOLDOUT_VIGNETTES))

    print("=" * 80)
    print("  VIGNETTE EVALUATION")
    if args.baseline != "none":
        print(f"  Baseline: {args.baseline}")
    print("=" * 80)

    out = {}
    for name, vigs in suites:
        out[name] = print_summary(name, run_suite(onto, patient, vigs, matcher=matcher))
    return out


if __name__ == "__main__":
    main()
