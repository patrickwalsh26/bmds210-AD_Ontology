#!/usr/bin/env python3
"""
Inter-annotator agreement for Track 2 extraction gold.

Annotators fill JSON files (see data/gold/). This script computes Cohen's kappa
on intervention labels and negation for matched statement IDs.

  python eval_inter_annotator.py
  python eval_inter_annotator.py --export-template
"""
import sys
from pathlib import Path as _Path
_ADO_ROOT = _Path(__file__).resolve().parents[1]
_ADO_EVAL = _Path(__file__).resolve().parent
for _p in (_ADO_ROOT, _ADO_EVAL):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANNOT_DIR = ROOT / "data" / "gold"
STATEMENTS = ROOT / "data" / "gold" / "statements.json"


def cohen_kappa(labels_a, labels_b):
    """Cohen's kappa for two parallel label lists."""
    if len(labels_a) != len(labels_b) or not labels_a:
        return float("nan")
    categories = sorted(set(labels_a) | set(labels_b))
    n = len(labels_a)
    agree = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    po = agree / n
    pe = sum(
        (labels_a.count(c) / n) * (labels_b.count(c) / n)
        for c in categories
    )
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def load_annotations(path: Path):
    data = json.loads(path.read_text())
    return {item["id"]: item for item in data["annotations"]}


def export_template():
    ANNOT_DIR.mkdir(parents=True, exist_ok=True)
    from extraction_evaluation import GOLD

    statements = []
    template_ann = []
    for item in GOLD:
        statements.append({"id": item["id"], "source": item["source"], "text": item["text"]})
        for g in item["gold"]:
            interv = g["interv"][0] if g["interv"] and g["interv"][0] != "*vague*" else "vague"
            template_ann.append({
                "id": item["id"],
                "intervention": interv,
                "negated": g["negated"],
                "type": g["type"],
            })

    STATEMENTS.write_text(json.dumps({"statements": statements}, indent=2))
    (ANNOT_DIR / "annotator_a.json").write_text(
        json.dumps({"annotator": "A (primary gold)", "annotations": template_ann}, indent=2)
    )
    # Annotator B: duplicate with two intentional disagreements for protocol demo
    b_ann = [dict(x) for x in template_ann]
    for entry in b_ann:
        if entry["id"] == "E5":
            entry["intervention"] = "cpr"  # single vague bucket vs split
        if entry["id"] == "E8":
            entry["negated"] = False
    (ANNOT_DIR / "annotator_b.json").write_text(
        json.dumps({
            "annotator": "B (independent — replace with real second pass)",
            "note": "Demo file has 2 deliberate disagreements; run dual blind annotation before report.",
            "annotations": b_ann,
        }, indent=2)
    )
    print(f"Wrote {STATEMENTS}, annotator_a.json, annotator_b.json")


def compare(a_path: Path, b_path: Path):
    a = load_annotations(a_path)
    b = load_annotations(b_path)
    common = sorted(set(a) & set(b))
    if not common:
        print("No common statement IDs.")
        return

    interv_a, interv_b = [], []
    neg_a, neg_b = [], []
    for sid in common:
        interv_a.append(a[sid].get("intervention", ""))
        interv_b.append(b[sid].get("intervention", ""))
        neg_a.append(str(a[sid].get("negated", "")))
        neg_b.append(str(b[sid].get("negated", "")))

    print("=" * 72)
    print("  INTER-ANNOTATOR AGREEMENT (statement-level)")
    print("=" * 72)
    print(f"  Annotator A: {a_path.name}")
    print(f"  Annotator B: {b_path.name}")
    print(f"  Statements compared: {len(common)}")
    print(f"  Cohen's κ (intervention): {cohen_kappa(interv_a, interv_b):.2f}")
    print(f"  Cohen's κ (negation):     {cohen_kappa(neg_a, neg_b):.2f}")
    disagreements = [sid for sid in common if a[sid] != b[sid]]
    if disagreements:
        print(f"\n  Disagreements ({len(disagreements)}):")
        for sid in disagreements:
            print(f"    {sid}: A={a[sid]}  B={b[sid]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-template", action="store_true")
    ap.add_argument("--a", type=Path, default=ANNOT_DIR / "annotator_a.json")
    ap.add_argument("--b", type=Path, default=ANNOT_DIR / "annotator_b.json")
    args = ap.parse_args()
    if args.export_template:
        export_template()
        return
    if not args.a.exists() or not args.b.exists():
        print("Run: python eval_inter_annotator.py --export-template")
        return
    compare(args.a, args.b)


if __name__ == "__main__":
    main()
