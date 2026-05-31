"""
Track 1b — Architecture ablation: ontology pipeline vs Gemini-only reasoning.

Three arms on the same 16 vignettes (query_evaluation.VIGNETTES gold):
  A — Hand-coded JSON → populate_patient → evaluate_vignette (upper bound, no API)
  B — Canonical AD → gemini_extraction → populate_patient → evaluate_vignette
  C — Canonical AD + vignette → llm_direct_reasoning (falsification baseline)

LLM provider: Gemini (GEMINI_API_KEY or GOOGLE_API_KEY). Track 2 used Claude;
do not compare Arm B extraction F1 to Track 2 numbers.

Usage:
    python ablation_evaluation.py                     # all arms, both C variants
    python ablation_evaluation.py --arm a             # upper bound only (free)
    python ablation_evaluation.py --arm c --prompt minimal
    python ablation_evaluation.py --cache out.json     # save/load raw results
    python ablation_evaluation.py --load out.json     # re-score from cache
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

from query_evaluation import VIGNETTES, evaluate_vignette
from preference_input import load_ontology, populate_patient

from gemini_extraction import (
    DEFAULT_MODEL,
    extract_preferences,
    get_gemini_client,
    to_patient_json,
)
from llm_direct_reasoning import PromptVariant, reason_directly, score_direct_decision


ROOT = Path(__file__).parent
CANONICAL_AD_PATH = ROOT / "populated_ontologies" / "jane_doe_canonical_ad.txt"
GOLD_JSON_PATH = ROOT / "populated_ontologies" / "example_input.json"


def load_canonical_ad() -> str:
    if not CANONICAL_AD_PATH.exists():
        raise FileNotFoundError(f"Canonical AD not found: {CANONICAL_AD_PATH}")
    return CANONICAL_AD_PATH.read_text()


def load_gold_patient_data() -> dict:
    return json.loads(GOLD_JSON_PATH.read_text())


def run_arm_a() -> tuple[list[dict], dict]:
    """Gold JSON → ontology → reasoner."""
    onto = load_ontology()
    patient_data = load_gold_patient_data()
    with onto:
        patient = populate_patient(onto, patient_data)
        results = [evaluate_vignette(onto, patient, v) for v in VIGNETTES]
    return results, patient_data


def run_arm_b(ad_text: str, *, model: Optional[str] = None) -> tuple[list[dict], dict, dict]:
    """Gemini extraction → ontology → reasoner."""
    client = get_gemini_client()
    extracted = extract_preferences(ad_text, client=client, model=model)
    patient_data = to_patient_json(
        extracted,
        patient_id="gemini_ablation_001",
        patient_name="Jane Doe (Gemini-extracted)",
    )
    onto = load_ontology()
    with onto:
        patient = populate_patient(onto, patient_data)
        results = [evaluate_vignette(onto, patient, v) for v in VIGNETTES]
    extraction_payload = {
        "preferences_count": len(extracted.preferences),
        "extraction_notes": extracted.extraction_notes,
        "patient_json": patient_data,
    }
    return results, patient_data, extraction_payload


def run_arm_c(
    ad_text: str,
    *,
    variant: PromptVariant,
    model: Optional[str] = None,
    repeats: int = 1,
    delay_seconds: float = 0.0,
) -> list[dict]:
    """Gemini direct reasoning per vignette."""
    client = get_gemini_client()
    all_runs: list[list[dict]] = []
    total = len(VIGNETTES) * repeats
    call_num = 0
    for run_idx in range(repeats):
        run_results = []
        for vignette in VIGNETTES:
            call_num += 1
            print(
                f"  [{call_num}/{total}] {vignette['id']} ({variant})...",
                flush=True,
            )
            direct = reason_directly(
                ad_text,
                vignette,
                variant=variant,
                client=client,
                model=model,
            )
            row = score_direct_decision(direct, vignette)
            row["run"] = run_idx + 1
            row["prompt_variant"] = variant
            run_results.append(row)
            if delay_seconds > 0 and call_num < total:
                time.sleep(delay_seconds)
        all_runs.append(run_results)
    return all_runs


def summarize_results(results: list[dict], label: str) -> dict:
    total = len(results)
    decision_correct = sum(1 for r in results if r["decision_correct"])
    match_correct = sum(1 for r in results if r["match_type_correct"])
    both_correct = sum(
        1 for r in results if r["decision_correct"] and r["match_type_correct"]
    )
    by_type: dict[str, dict[str, int]] = defaultdict(
        lambda: {"total": 0, "decision_correct": 0, "match_correct": 0}
    )
    for r in results:
        t = r["expected_match_type"]
        by_type[t]["total"] += 1
        if r["decision_correct"]:
            by_type[t]["decision_correct"] += 1
        if r["match_type_correct"]:
            by_type[t]["match_correct"] += 1
    return {
        "label": label,
        "total": total,
        "decision_accuracy": decision_correct,
        "match_type_accuracy": match_correct,
        "both_correct": both_correct,
        "by_expected_match_type": dict(by_type),
        "failures": [
            {
                "id": r["id"],
                "expected": f"{r['expected_decision']}/{r['expected_match_type']}",
                "got": f"{r['system_decision']}/{r['system_match_type']}",
            }
            for r in results
            if not r["decision_correct"] or not r["match_type_correct"]
        ],
    }


def classify_errors(
    arm_a: list[dict],
    arm_b: list[dict],
    arm_c: list[dict],
) -> list[dict]:
    """Ablation-specific error taxonomy."""
    errors = []
    idx = {r["id"]: r for r in arm_a}
    idb = {r["id"]: r for r in arm_b}
    idc = {r["id"]: r for r in arm_c}

    for v in VIGNETTES:
        vid = v["id"]
        gold_decision = v["expected"]["decision"]
        gold_match = v["expected"]["match_type"]
        c = idc[vid]
        b = idb[vid]
        a = idx[vid]

        tags = []
        if c["system_decision"] in ("yes", "no") and gold_decision == "no_coverage":
            tags.append("hallucinated_coverage")
        if c["system_match_type"] == "clear" and gold_match in ("partial", "vague"):
            tags.append("false_certainty")
        if c["system_decision"] in ("no_coverage", "partial") and gold_decision in ("yes", "no"):
            tags.append("missed_authorization")
        if not b["decision_correct"] and a["decision_correct"]:
            tags.append("extraction_cascade")
        if not b["decision_correct"] and not a["decision_correct"]:
            tags.append("reasoner_cascade")

        if tags or not c["decision_correct"] or not c["match_type_correct"]:
            errors.append({
                "id": vid,
                "gold": f"{gold_decision}/{gold_match}",
                "arm_a": f"{a['system_decision']}/{a['system_match_type']}",
                "arm_b": f"{b['system_decision']}/{b['system_match_type']}",
                "arm_c": f"{c['system_decision']}/{c['system_match_type']}",
                "tags": tags,
            })
    return errors


def stability_summary(runs: list[list[dict]]) -> dict:
    """Agreement across repeated Arm C runs."""
    if len(runs) <= 1:
        return {"runs": len(runs), "per_vignette": {}}

    per_vignette = {}
    for vignette in VIGNETTES:
        vid = vignette["id"]
        labels = [
            f"{r['system_decision']}/{r['system_match_type']}"
            for run in runs
            for r in run
            if r["id"] == vid
        ]
        unique = set(labels)
        per_vignette[vid] = {
            "labels": labels,
            "unique_count": len(unique),
            "stable": len(unique) == 1,
        }
    stable_count = sum(1 for v in per_vignette.values() if v["stable"])
    return {
        "runs": len(runs),
        "stable_vignettes": stable_count,
        "total_vignettes": len(VIGNETTES),
        "per_vignette": per_vignette,
    }


def print_summary(summary: dict) -> None:
    t = summary["total"]
    print(f"\n{'=' * 72}")
    print(f"  {summary['label']}")
    print(f"{'=' * 72}")
    print(f"  Decision accuracy    : {summary['decision_accuracy']}/{t} ({100*summary['decision_accuracy']/t:.0f}%)")
    print(f"  Match-type accuracy  : {summary['match_type_accuracy']}/{t} ({100*summary['match_type_accuracy']/t:.0f}%)")
    print(f"  Both correct         : {summary['both_correct']}/{t}")
    print("  By expected match type:")
    for mt, counts in sorted(summary["by_expected_match_type"].items()):
        print(
            f"    {mt:15s}: {counts['decision_correct']}/{counts['total']} decisions, "
            f"{counts['match_correct']}/{counts['total']} match types"
        )
    if summary["failures"]:
        print(f"  Failures ({len(summary['failures'])}):")
        for f in summary["failures"]:
            print(f"    {f['id']}: expected {f['expected']}, got {f['got']}")
    else:
        print("  Failures: none")


def main() -> None:
    parser = argparse.ArgumentParser(description="Track 1b architecture ablation")
    parser.add_argument(
        "--arm", choices=["a", "b", "c", "all"], default="all",
        help="Which arm(s) to run (default: all)",
    )
    parser.add_argument(
        "--prompt", choices=["minimal", "matched", "both"], default="both",
        help="Arm C prompt variant(s)",
    )
    parser.add_argument("--repeats", type=int, default=1,
                        help="Arm C stability repeats (default 1)")
    parser.add_argument("--model", type=str, default=None,
                        help=f"Gemini model override (default {DEFAULT_MODEL})")
    parser.add_argument(
        "--delay", type=float, default=13.0,
        help="Seconds to wait between Arm C API calls (default 13; free tier ~5/min). "
             "Use --delay 0 on paid tiers.",
    )
    parser.add_argument("--cache", type=str,
                        help="Write full results JSON to this path")
    parser.add_argument("--load", type=str,
                        help="Load results JSON and re-print summaries (no API)")
    args = parser.parse_args()

    if args.load:
        payload = json.loads(Path(args.load).read_text())
        for key in ("arm_a", "arm_b_minimal", "arm_b", "arm_c_minimal", "arm_c_matched"):
            if key in payload.get("summaries", {}):
                print_summary(payload["summaries"][key])
        if payload.get("error_taxonomy"):
            print("\nError taxonomy (sample):")
            for row in payload["error_taxonomy"][:10]:
                print(f"  {row['id']}: {row['tags']} — C={row['arm_c']} gold={row['gold']}")
        return

    model = args.model or DEFAULT_MODEL
    ad_text = load_canonical_ad()
    payload: dict[str, Any] = {
        "model": model,
        "canonical_ad_path": str(CANONICAL_AD_PATH),
        "note": "Track 1b uses Gemini; Track 2 extraction used Claude — not cross-comparable.",
    }
    summaries: dict[str, dict] = {}

    arm_a_results: Optional[list[dict]] = None
    arm_b_results: Optional[list[dict]] = None
    arm_c_minimal_runs: Optional[list[list[dict]]] = None
    arm_c_matched_runs: Optional[list[list[dict]]] = None

    if args.arm in ("a", "all"):
        print("Running Arm A (gold JSON → reasoner)...")
        arm_a_results, _ = run_arm_a()
        summaries["arm_a"] = summarize_results(arm_a_results, "Arm A — gold JSON → reasoner")
        print_summary(summaries["arm_a"])

    if args.arm in ("b", "all"):
        print(f"\nRunning Arm B (Gemini extraction → reasoner, model={model})...")
        arm_b_results, patient_json, extraction_info = run_arm_b(ad_text, model=model)
        summaries["arm_b"] = summarize_results(
            arm_b_results, "Arm B — Gemini extract → reasoner"
        )
        payload["arm_b_extraction"] = extraction_info
        print_summary(summaries["arm_b"])

    c_variants: list[PromptVariant] = []
    if args.prompt in ("minimal", "both"):
        c_variants.append("minimal")
    if args.prompt in ("matched", "both"):
        c_variants.append("matched")

    if args.arm in ("c", "all"):
        delay = args.delay
        if delay > 0 and c_variants:
            est_min = (
                len(VIGNETTES) * args.repeats * len(c_variants) * delay
            ) / 60
            print(
                f"\nArm C pacing: {delay}s between calls "
                f"(~{est_min:.0f} min total; free tier is ~5 req/min)"
            )
        for variant in c_variants:
            print(
                f"\nRunning Arm C ({variant} prompt, model={model}, "
                f"repeats={args.repeats})..."
            )
            runs = run_arm_c(
                ad_text,
                variant=variant,
                model=model,
                repeats=args.repeats,
                delay_seconds=delay,
            )
            primary = runs[0]
            key = f"arm_c_{variant}"
            summaries[key] = summarize_results(
                primary,
                f"Arm C — Gemini direct ({variant} prompt, run 1)",
            )
            payload[f"{key}_runs"] = runs
            payload[f"{key}_stability"] = stability_summary(runs)
            print_summary(summaries[key])
            if variant == "minimal":
                arm_c_minimal_runs = runs
            else:
                arm_c_matched_runs = runs

    if (
        arm_a_results is not None
        and arm_b_results is not None
        and arm_c_minimal_runs is not None
    ):
        errors = classify_errors(
            arm_a_results,
            arm_b_results,
            arm_c_minimal_runs[0],
        )
        payload["error_taxonomy"] = errors
        print(f"\n{'=' * 72}")
        print("  Error taxonomy (Arm C minimal vs A/B)")
        print(f"{'=' * 72}")
        for row in errors:
            if row["tags"]:
                print(
                    f"  {row['id']}: {', '.join(row['tags'])} | "
                    f"gold={row['gold']} C={row['arm_c']}"
                )

    payload["summaries"] = summaries
    payload["arm_a_results"] = arm_a_results
    payload["arm_b_results"] = arm_b_results

    if args.cache:
        Path(args.cache).write_text(json.dumps(payload, indent=2, default=str))
        print(f"\nWrote cache: {args.cache}")


if __name__ == "__main__":
    main()
