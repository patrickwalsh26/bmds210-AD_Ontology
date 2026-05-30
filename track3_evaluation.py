"""
Track 3 (flagship quantitative evaluation): preference profile -> code-status / POLST mapping.

Magnus's review established that what governs the bedside is the code-status order and POLST,
not the advance directive. This evaluation asks: when we encode a realistic preference profile
(drawn from the 50-template concept inventory) and ask ADO to derive a code status and POLST
selection, does it agree with what those forms' own published semantics prescribe?

  * Profiles      : 12 archetypes grounded in real templates (CA AHCD, Texas OOH-DNR,
                    NHS Wales ADRT, Five Wishes, POLST, dementia directive, VA form, ...).
  * Ground truth  : POLST definitional semantics, adjudicated by the team (NOT derived from
                    ADO's own logic — that independence is what makes agreement meaningful).
  * Metrics       : per-field agreement (code status, POLST A, POLST B), exact-profile match,
                    and a confusion matrix over hospital code-status categories.

Run:  python track3_evaluation.py
"""

import io
import sys
import contextlib
from collections import defaultdict
from pathlib import Path

try:
    from owlready2 import World
except ImportError:
    print("ERROR: owlready2 is not installed. Run: pip install owlready2")
    sys.exit(1)

import preference_input
from code_status import derive_code_status

BASE_OWL = Path(__file__).parent / "advanced_directives.owl"


def _pref(label, intervention, negated, strength, original, ptype="clear", ac=None):
    d = {"label": label, "intervention": intervention, "negated": negated,
         "strength": strength, "original_text": original, "type": ptype}
    if ac:
        d["activation_conditions"] = ac
    return d


# ── 12 preference profiles, each grounded in a real inventory template ──────
PROFILES = [
    {
        "id": "P1", "template": "National Catholic Bioethics Center directive",
        "patient_data": {"patient_id": "p1_ncbc", "patient_name": "NCBC full-treatment patient",
            "preferences": [
                _pref("Wants CPR", "cpr", False, "Strong", "I wish to receive all obligatory care that my faith teaches."),
                _pref("Wants intubation", "intubation", False, "Strong", "Provide ordinary means including breathing support."),
                _pref("Wants acute dialysis", "acute_dialysis", False, "Strong", "Provide dialysis as ordinary care."),
            ]},
        "scenario": {"conditions": ["RespiratoryFailure"], "nyha_class": "NYHA_ClassIII"},
        "gold": {"code_status": "Full code", "polst_section_a": "Attempt CPR/Full Resuscitation",
                 "polst_section_b": "Full Treatment"},
    },
    {
        "id": "P2", "template": "Texas Out-of-Hospital DNR",
        "patient_data": {"patient_id": "p2_txdnr", "patient_name": "Texas OOH-DNR patient",
            "preferences": [
                _pref("No CPR", "cpr", True, "Absolute", "Do not attempt resuscitation."),
                _pref("No defibrillation", "defibrillation", True, "Absolute", "No defibrillation."),
                _pref("No artificial ventilation", "mechanical_ventilation", True, "Absolute", "No artificial ventilation."),
            ]},
        "scenario": {"conditions": ["CardiacArrest"]},
        "gold": {"code_status": "DNR/DNI", "polst_section_a": "Do Not Attempt Resuscitation (DNAR)",
                 "polst_section_b": "Comfort-Focused Treatment"},
    },
    {
        "id": "P3", "template": "California Prehospital DNR (CPR only)",
        "patient_data": {"patient_id": "p3_cadnr", "patient_name": "CA prehospital DNR patient",
            "preferences": [
                _pref("No CPR", "cpr", True, "Absolute", "Do not attempt CPR if my heart stops."),
                _pref("Accept intubation", "intubation", False, "Strong", "I am willing to be placed on a breathing machine."),
            ]},
        "scenario": {"conditions": ["CardiacArrest"]},
        "gold": {"code_status": "DNR", "polst_section_a": "Do Not Attempt Resuscitation (DNAR)",
                 "polst_section_b": "Full Treatment"},
    },
    {
        "id": "P4", "template": "NHS Wales ADRT — condition MET (permanent unconsciousness)",
        "patient_data": {"patient_id": "p4_adrt_met", "patient_name": "ADRT patient (condition met)",
            "preferences": [
                _pref("No CPR if permanently unconscious", "cpr", True, "Absolute",
                      "If I become permanently unconscious, do not attempt resuscitation.", "conditional",
                      {"conditions": ["permanent_unconsciousness"]}),
                _pref("No ventilation if permanently unconscious", "mechanical_ventilation", True, "Absolute",
                      "If I become permanently unconscious, do not provide artificial ventilation.", "conditional",
                      {"conditions": ["permanent_unconsciousness"]}),
            ]},
        "scenario": {"conditions": ["PermanentUnconsciousness"]},
        "gold": {"code_status": "DNR/DNI", "polst_section_a": "Do Not Attempt Resuscitation (DNAR)",
                 "polst_section_b": "Comfort-Focused Treatment"},
    },
    {
        "id": "P5", "template": "NHS Wales ADRT — condition NOT met (same directive, conscious)",
        "patient_data": {"patient_id": "p5_adrt_unmet", "patient_name": "ADRT patient (condition unmet)",
            "preferences": [
                _pref("No CPR if permanently unconscious", "cpr", True, "Absolute",
                      "If I become permanently unconscious, do not attempt resuscitation.", "conditional",
                      {"conditions": ["permanent_unconsciousness"]}),
                _pref("No ventilation if permanently unconscious", "mechanical_ventilation", True, "Absolute",
                      "If I become permanently unconscious, do not provide artificial ventilation.", "conditional",
                      {"conditions": ["permanent_unconsciousness"]}),
            ]},
        "scenario": {"conditions": ["RespiratoryFailure"]},
        # POLST default presumption when no valid refusal applies is full treatment.
        "gold": {"code_status": "Full code", "polst_section_a": "Attempt CPR/Full Resuscitation",
                 "polst_section_b": "Full Treatment"},
    },
    {
        "id": "P6", "template": "Five Wishes — comfort if terminal",
        "patient_data": {"patient_id": "p6_fivewishes", "patient_name": "Five Wishes comfort patient",
            "preferences": [
                _pref("No CPR if terminal", "cpr", True, "Absolute", "If I am terminally ill, I do not want CPR.", "conditional",
                      {"conditions": ["terminal_condition"]}),
                _pref("No intubation if terminal", "intubation", True, "Absolute", "No breathing machines if I am dying.", "conditional",
                      {"conditions": ["terminal_condition"]}),
                _pref("No inotrope escalation if terminal", "inotrope_escalation", True, "Absolute", "No escalation of drips if I am dying.", "conditional",
                      {"conditions": ["terminal_condition"]}),
            ]},
        "scenario": {"conditions": ["TerminalCondition"]},
        "gold": {"code_status": "DNR/DNI + Do Not Escalate", "polst_section_a": "Do Not Attempt Resuscitation (DNAR)",
                 "polst_section_b": "Comfort-Focused Treatment"},
    },
    {
        "id": "P7", "template": "Floor 'do-not-escalate' HF patient",
        "patient_data": {"patient_id": "p7_noescalate", "patient_name": "Do-not-escalate HF patient",
            "preferences": [
                _pref("No inotrope escalation", "inotrope_escalation", True, "Absolute", "Do not escalate to ICU-level drips."),
                _pref("No vasopressor escalation", "vasopressor_escalation", True, "Absolute", "Do not start pressors / transfer to ICU."),
                _pref("Accept temporary ventilation", "temporary_ventilation", False, "Strong", "A short trial of breathing support on the floor is OK."),
            ]},
        "scenario": {"conditions": ["AcuteDecompensation"], "nyha_class": "NYHA_ClassIV"},
        "gold": {"code_status": "Do Not Escalate", "polst_section_a": "Attempt CPR/Full Resuscitation",
                 "polst_section_b": "Selective Treatment"},
    },
    {
        "id": "P8", "template": "DNI patient who accepts CPR and BiPAP",
        "patient_data": {"patient_id": "p8_dni", "patient_name": "DNI / accept-CPR patient",
            "preferences": [
                _pref("No intubation", "intubation", True, "Absolute", "I never want to be intubated."),
                _pref("No indefinite ventilation", "indefinite_ventilation", True, "Absolute", "No long-term breathing machine."),
                _pref("Accept BiPAP", "non_invasive_ventilation", False, "Strong", "BiPAP is acceptable to me."),
                _pref("Accept CPR", "cpr", False, "Strong", "Attempt CPR if my heart stops."),
            ]},
        "scenario": {"conditions": ["RespiratoryFailure"]},
        "gold": {"code_status": "DNI", "polst_section_a": "Attempt CPR/Full Resuscitation",
                 "polst_section_b": "Selective Treatment"},
    },
    {
        "id": "P9", "template": "Conditional DNR — condition MET (NYHA IV, no reversible cause)",
        "patient_data": {"patient_id": "p9_conddnr_met", "patient_name": "Conditional-DNR patient (met)",
            "preferences": [
                _pref("No CPR if NYHA IV and no reversible cause", "cpr", True, "Absolute",
                      "If my heart stops and I am in NYHA Class IV with no reversible cause, do not attempt CPR.", "conditional",
                      {"nyha_class": "IV", "conditions": ["cardiac_arrest"], "reversible_cause": False}),
                _pref("Accept temporary ventilation if reversible", "temporary_ventilation", False, "Conditional",
                      "I would accept temporary breathing support if the cause is reversible.", "conditional",
                      {"reversible_cause": True}),
            ]},
        "scenario": {"conditions": ["CardiacArrest"], "nyha_class": "NYHA_ClassIV", "reversible_cause": False},
        "gold": {"code_status": "DNR", "polst_section_a": "Do Not Attempt Resuscitation (DNAR)",
                 "polst_section_b": "Selective Treatment"},
    },
    {
        "id": "P10", "template": "Conditional DNR — condition NOT met (same patient, NYHA III, reversible)",
        "patient_data": {"patient_id": "p10_conddnr_unmet", "patient_name": "Conditional-DNR patient (unmet)",
            "preferences": [
                _pref("No CPR if NYHA IV and no reversible cause", "cpr", True, "Absolute",
                      "If my heart stops and I am in NYHA Class IV with no reversible cause, do not attempt CPR.", "conditional",
                      {"nyha_class": "IV", "conditions": ["cardiac_arrest"], "reversible_cause": False}),
                _pref("Accept temporary ventilation if reversible", "temporary_ventilation", False, "Conditional",
                      "I would accept temporary breathing support if the cause is reversible.", "conditional",
                      {"reversible_cause": True}),
            ]},
        "scenario": {"conditions": ["CardiacArrest"], "nyha_class": "NYHA_ClassIII", "reversible_cause": True},
        "gold": {"code_status": "Full code", "polst_section_a": "Attempt CPR/Full Resuscitation",
                 "polst_section_b": "Selective Treatment"},
    },
    {
        "id": "P11", "template": "VA Form 10-0137 — full aggressive care",
        "patient_data": {"patient_id": "p11_va", "patient_name": "VA full-care veteran",
            "preferences": [
                _pref("Wants CPR", "cpr", False, "Strong", "Do everything to save my life."),
                _pref("Wants intubation", "intubation", False, "Strong", "I want a breathing machine if needed."),
                _pref("Wants inotrope escalation", "inotrope_escalation", False, "Strong", "Escalate medications as needed."),
                _pref("Wants acute dialysis", "acute_dialysis", False, "Strong", "Provide dialysis if needed."),
            ]},
        "scenario": {"conditions": ["CardiogenicShock"], "nyha_class": "NYHA_ClassIV"},
        "gold": {"code_status": "Full code", "polst_section_a": "Attempt CPR/Full Resuscitation",
                 "polst_section_b": "Full Treatment"},
    },
    {
        "id": "P12", "template": "Dementia-specific directive — comfort if advanced/terminal",
        "patient_data": {"patient_id": "p12_dementia", "patient_name": "Dementia-directive patient",
            "preferences": [
                _pref("No CPR if terminal", "cpr", True, "Absolute", "In advanced dementia, no CPR.", "conditional",
                      {"conditions": ["terminal_condition"]}),
                _pref("No intubation if terminal", "intubation", True, "Absolute", "In advanced dementia, no intubation.", "conditional",
                      {"conditions": ["terminal_condition"]}),
                _pref("No dialysis if terminal", "acute_dialysis", True, "Absolute", "In advanced dementia, no dialysis.", "conditional",
                      {"conditions": ["terminal_condition"]}),
                _pref("No escalation if terminal", "vasopressor_escalation", True, "Absolute", "In advanced dementia, no pressors.", "conditional",
                      {"conditions": ["terminal_condition"]}),
            ]},
        "scenario": {"conditions": ["TerminalCondition"]},
        "gold": {"code_status": "DNR/DNI + Do Not Escalate", "polst_section_a": "Do Not Attempt Resuscitation (DNAR)",
                 "polst_section_b": "Comfort-Focused Treatment"},
    },
]

FIELDS = ["code_status", "polst_section_a", "polst_section_b"]
SHORT = {"code_status": "Code status", "polst_section_a": "POLST A", "polst_section_b": "POLST B"}


def cohen_kappa(labels_a, labels_b):
    """Cohen's kappa between two raters' categorical labels over the same items."""
    n = len(labels_a)
    if n == 0:
        return float("nan")
    cats = set(labels_a) | set(labels_b)
    po = sum(1 for a, b in zip(labels_a, labels_b) if a == b) / n
    pe = 0.0
    for c in cats:
        pa = labels_a.count(c) / n
        pb = labels_b.count(c) / n
        pe += pa * pb
    return 1.0 if pe == 1.0 else (po - pe) / (1 - pe)


def evaluate_profile(profile):
    """Populate a fresh isolated ontology, derive code status, compare to gold."""
    world = World()
    onto = world.get_ontology(str(BASE_OWL.resolve())).load()
    with contextlib.redirect_stdout(io.StringIO()):       # silence populate_patient's prints
        patient = preference_input.populate_patient(onto, profile["patient_data"])
    result = derive_code_status(onto, patient, profile["scenario"])
    gold = profile["gold"]
    field_match = {f: result[f] == gold[f] for f in FIELDS}
    return result, field_match


def emit_sheet():
    """Blind sheet for a second rater to assign code status / POLST orders from preferences."""
    print("BLIND RATING SHEET — for each profile, read the preference statements and assign:")
    print("  code status (Full code / DNR / DNI / DNR/DNI / Do Not Escalate / combinations),")
    print("  POLST Section A (Attempt CPR / DNAR), POLST Section B (Full / Selective / Comfort).")
    print("  Do NOT look at the gold standard or ADO output.\n")
    for p in PROFILES:
        print(f"[{p['id']}] scenario: {p['scenario']}")
        for pref in p["patient_data"]["preferences"]:
            verb = "REFUSES" if pref["negated"] else "WANTS"
            print(f"     - {verb}: \"{pref['original_text']}\"")
        print("     -> code status: ____   POLST A: ____   POLST B: ____\n")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", action="store_true", help="Emit blind rating sheet (no evaluation)")
    if ap.parse_args().sheet:
        emit_sheet()
        return

    print("=" * 100)
    print("  TRACK 3 — Preference profile -> code-status / POLST mapping fidelity")
    print("=" * 100)

    field_correct = defaultdict(int)
    exact = 0
    confusion = defaultdict(int)          # (gold_code, derived_code) -> count
    derived_labels = defaultdict(list)    # field -> [ADO labels]
    gold_labels = defaultdict(list)       # field -> [gold labels]
    rows = []

    for p in PROFILES:
        result, fm = evaluate_profile(p)
        for f in FIELDS:
            field_correct[f] += int(fm[f])
            derived_labels[f].append(result[f])
            gold_labels[f].append(p["gold"][f])
        all_match = all(fm.values())
        exact += int(all_match)
        confusion[(p["gold"]["code_status"], result["code_status"])] += 1
        rows.append((p, result, fm, all_match))

    # Per-profile detail
    for p, result, fm, all_match in rows:
        flag = "EXACT" if all_match else "DIFF"
        cond = " [conditional]" if result["conditional"] else ""
        print(f"\n[{p['id']}] {p['template']}{cond}   -> {flag}")
        for f in FIELDS:
            mark = "ok " if fm[f] else "XX "
            print(f"     {mark}{SHORT[f]:<12} derived: {result[f]:<40} gold: {p['gold'][f]}")

    n = len(PROFILES)
    print("\n" + "=" * 100)
    print("  SUMMARY")
    print("=" * 100)
    print(f"  Profiles                : {n}")
    print(f"  Exact-profile agreement : {exact}/{n} ({100*exact/n:.0f}%)")
    for f in FIELDS:
        print(f"  {SHORT[f]:<24}: {field_correct[f]}/{n} ({100*field_correct[f]/n:.0f}%)")
    total_fields = n * len(FIELDS)
    total_correct = sum(field_correct.values())
    print(f"  Overall field agreement : {total_correct}/{total_fields} ({100*total_correct/total_fields:.0f}%)")

    print("\n  Cohen's kappa (ADO derived vs. independent POLST-semantics gold):")
    for f in FIELDS:
        k = cohen_kappa(derived_labels[f], gold_labels[f])
        print(f"    {SHORT[f]:<24}: kappa = {k:.2f}")

    # Confusion matrix over code-status categories
    cats = sorted({c for pair in confusion for c in pair})
    print("\n  Code-status confusion (rows = gold, cols = derived):")
    w = max(len(c) for c in cats) + 2
    header = " " * (w + 2) + "".join(f"{c[:14]:>16}" for c in cats)
    print(header)
    for g in cats:
        line = f"  {g:<{w}}"
        for d in cats:
            line += f"{confusion.get((g, d), 0):>16}"
        print(line)

    # Off-diagonal (disagreement) notes
    diffs = [(p["id"], p["template"]) for p, r, fm, am in rows if not am]
    if diffs:
        print("\n  Divergences (worth discussing, not necessarily errors):")
        for pid, tmpl in diffs:
            print(f"    {pid}: {tmpl}")


if __name__ == "__main__":
    main()
