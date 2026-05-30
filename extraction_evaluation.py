"""
Track 2 (quantitative): LLM extraction precision / recall on real directive language.

Tests `llm_extraction.py` against a gold-annotated set of statements drawn from real
advance-directive template families (California statutory AHCD, Texas out-of-hospital DNR,
common living wills, Five Wishes-style comfort language, VA full-treatment language, an
ICD/hospice clause, and HF-specific escalation language). Two items are deliberately
**out of scope** (artificial nutrition/hydration; antibiotics) — our intervention vocabulary
does not cover them, so the correct behavior is to extract nothing. These test the
closed-world discipline the reasoner's "no coverage" output depends on.

Metrics: precision, recall, F1 on preferences (matched by intervention), plus an error
taxonomy (missed / over-extracted-or-hallucinated / lost-negation / lost-conditionality) and
per-field accuracy (negation, type, conditionality) on matched pairs.

NOTE on ground truth: the gold annotations below are the reference standard. For the report's
inter-annotator agreement, both teammates should independently annotate this same text set
(see the blind sheet emitted by `--sheet`) and compute Cohen's kappa on the labels.

Run:  python extraction_evaluation.py            # calls the live API (needs ANTHROPIC_API_KEY)
      python extraction_evaluation.py --sheet    # emit a blind annotation sheet, no API calls
"""

import argparse
import sys

import llm_extraction as L

# Each gold preference: acceptable intervention keys (a list tolerates clinically-equivalent
# mappings, e.g. generic "breathing machine" -> intubation OR mechanical_ventilation),
# expected negation, expected type, and whether it should carry activation conditions.
GOLD = [
    {"id": "E1", "source": "Living will (terminal-condition CPR clause)",
     "text": "If I have a terminal condition, I do not want cardiopulmonary resuscitation.",
     "gold": [{"interv": ["cpr"], "negated": True, "type": "conditional", "conditional": True}]},

    {"id": "E2", "source": "Texas Out-of-Hospital DNR",
     "text": "I direct that resuscitation not be initiated, including chest compressions, defibrillation, and artificial ventilation.",
     "gold": [{"interv": ["cpr"], "negated": True, "type": "clear", "conditional": False},
              {"interv": ["defibrillation"], "negated": True, "type": "clear", "conditional": False},
              {"interv": ["mechanical_ventilation", "intubation"], "negated": True, "type": "clear", "conditional": False}]},

    {"id": "E3", "source": "Living will (temporary vs indefinite ventilation)",
     "text": "I would accept a breathing machine temporarily if my doctors expect me to recover, but I do not want to be kept on a ventilator indefinitely.",
     "gold": [{"interv": ["temporary_ventilation"], "negated": False, "type": "conditional", "conditional": True},
              {"interv": ["indefinite_ventilation"], "negated": True, "type": "clear", "conditional": False}]},

    {"id": "E4", "source": "ICD/hospice deactivation clause",
     "text": "If I enroll in hospice, I want my implantable defibrillator turned off.",
     "gold": [{"interv": ["icd_deactivation"], "negated": False, "type": "conditional", "conditional": True}]},

    {"id": "E5", "source": "Five Wishes-style comfort language (vague)",
     "text": "I do not want any heroic measures or to be kept alive by machines if I am dying.",
     "gold": [{"interv": ["*vague*"], "negated": True, "type": "vague", "conditional": None}]},

    {"id": "E6", "source": "VA full-treatment language",
     "text": "I want to receive all treatments necessary to keep me alive, including CPR and a breathing machine.",
     "gold": [{"interv": ["cpr"], "negated": False, "type": "clear", "conditional": False},
              {"interv": ["intubation", "mechanical_ventilation"], "negated": False, "type": "clear", "conditional": False}]},

    {"id": "E7", "source": "Living will (chronic dialysis clause)",
     "text": "If my kidneys fail and recovery is not expected, I do not want long-term dialysis.",
     "gold": [{"interv": ["chronic_dialysis"], "negated": True, "type": "conditional", "conditional": True}]},

    {"id": "E8", "source": "HF-specific escalation clause",
     "text": "Do not escalate medications to support my blood pressure if I would need to be transferred to the intensive care unit.",
     "gold": [{"interv": ["vasopressor_escalation", "inotrope_escalation"], "negated": True, "type": "conditional", "conditional": True}]},

    {"id": "E9", "source": "OUT OF SCOPE — artificial nutrition/hydration",
     "text": "I do not want artificial nutrition or hydration through tubes if I am permanently unconscious.",
     "gold": [], "out_of_scope": True},

    {"id": "E10", "source": "OUT OF SCOPE — antibiotics",
     "text": "I do not wish to receive antibiotics if I am in the final stage of dying.",
     "gold": [], "out_of_scope": True},

    {"id": "E11", "source": "NIV-accept / intubation-refuse clause",
     "text": "I am willing to try BiPAP, but I never want a tube down my throat.",
     "gold": [{"interv": ["non_invasive_ventilation"], "negated": False, "type": "clear", "conditional": False},
              {"interv": ["intubation"], "negated": True, "type": "clear", "conditional": False}]},

    {"id": "E12", "source": "HF conditional-CPR clause",
     "text": "If my heart stops while I am in advanced heart failure with no reversible cause, do not attempt CPR.",
     "gold": [{"interv": ["cpr"], "negated": True, "type": "conditional", "conditional": True}]},
]


def match_gold_to_extracted(gold_prefs, extracted):
    """Greedy match each gold pref to an extracted pref by acceptable intervention key
    (or by type=='vague' for a vague gold). Returns (matched_pairs, missed, leftover_extracted)."""
    remaining = list(extracted)
    matched = []
    missed = []
    for g in gold_prefs:
        hit = None
        for e in remaining:
            if "*vague*" in g["interv"]:
                if e.type == "vague":
                    hit = e; break
            elif e.intervention in g["interv"]:
                hit = e; break
        if hit is not None:
            remaining.remove(hit)
            matched.append((g, hit))
        else:
            missed.append(g)
    return matched, missed, remaining


def run_eval():
    client = L.anthropic.Anthropic()
    tp = fp = fn = 0
    lost_negation = lost_conditionality = wrong_type = 0
    over_extracted = 0      # FP on out-of-scope items (hallucination / over-extraction)
    wrong_class = 0         # FP on in-scope items
    matched_total = 0
    neg_ok = type_ok = cond_ok = 0

    print("=" * 96)
    print("  TRACK 2 — LLM extraction precision/recall on real directive language")
    print(f"  Model: {L.MODEL}")
    print("=" * 96)

    for item in GOLD:
        out = L.extract_preferences(item["text"], client=client)
        extracted = out.preferences
        gold = item["gold"]
        matched, missed, leftover = match_gold_to_extracted(gold, extracted)

        tp += len(matched)
        fn += len(missed)
        fp += len(leftover)
        if item.get("out_of_scope"):
            over_extracted += len(leftover)
        else:
            wrong_class += len(leftover)

        for g, e in matched:
            matched_total += 1
            if e.negated == g["negated"]:
                neg_ok += 1
            else:
                lost_negation += 1
            if e.type == g["type"]:
                type_ok += 1
            else:
                wrong_type += 1
            has_cond = e.activation_conditions is not None and bool(
                e.activation_conditions.model_dump(exclude_none=True))
            if g["conditional"] is None:
                cond_ok += 1                      # vague: conditionality not scored
            elif has_cond == g["conditional"]:
                cond_ok += 1
            else:
                lost_conditionality += 1

        tag = "  [OUT OF SCOPE]" if item.get("out_of_scope") else ""
        print(f"\n[{item['id']}] {item['source']}{tag}")
        print(f"   text : {item['text']}")
        got = ", ".join(f"{e.intervention}{'(-)' if e.negated else '(+)'}/{e.type}" for e in extracted) or "(none)"
        print(f"   got  : {got}")
        print(f"   score: TP={len(matched)} FN(missed)={len(missed)} FP={len(leftover)}")

    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    print("\n" + "=" * 96)
    print("  SUMMARY")
    print("=" * 96)
    print(f"  Gold preferences (in-scope) : {tp + fn}")
    print(f"  True positives              : {tp}")
    print(f"  False negatives (missed)    : {fn}")
    print(f"  False positives             : {fp}  (over-extraction on out-of-scope: {over_extracted}; wrong-class in-scope: {wrong_class})")
    print(f"  Precision                   : {precision:.2f}")
    print(f"  Recall                      : {recall:.2f}")
    print(f"  F1                          : {f1:.2f}")
    print(f"\n  Per-field accuracy on {matched_total} matched preferences:")
    print(f"    Negation correct          : {neg_ok}/{matched_total}")
    print(f"    Type correct              : {type_ok}/{matched_total}")
    print(f"    Conditionality correct    : {cond_ok}/{matched_total}")
    print(f"\n  Error taxonomy:")
    print(f"    Missed                    : {fn}")
    print(f"    Over-extracted/hallucinated (out-of-scope FP) : {over_extracted}")
    print(f"    Wrong-class (in-scope FP) : {wrong_class}")
    print(f"    Lost negation             : {lost_negation}")
    print(f"    Lost conditionality       : {lost_conditionality}")
    print(f"    Wrong type                : {wrong_type}")
    print(f"\n  Closed-world check: {over_extracted} preference(s) invented for out-of-scope")
    print(f"  text (artificial nutrition, antibiotics) — lower is better; 0 = perfect discipline.")


def emit_sheet():
    """Blind annotation sheet for a second human annotator (inter-annotator agreement)."""
    print("BLIND ANNOTATION SHEET — for each statement, list the preferences a clinician would")
    print("encode: intervention, negated (Y/N), type (clear/conditional/vague). Do NOT look at GOLD.\n")
    for item in GOLD:
        print(f"[{item['id']}] {item['text']}")
        print("     -> \n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", action="store_true", help="Emit blind annotation sheet (no API calls)")
    args = ap.parse_args()
    if args.sheet:
        emit_sheet()
        return
    run_eval()


if __name__ == "__main__":
    main()
