"""
Code-status derivation layer for the Advance Directive Ontology (ADO).

Magnus's expert review (docs/Magnus_Expert_Review_2026-05-27.md) made the point that
what actually governs the bedside in an acute crisis is not the advance directive but the
**code-status order** (full-code / DNR / DNI / do-not-escalate) and the POLST form. This
module sits on top of the per-intervention reasoner in `query_evaluation.py` and aggregates
intervention-level preferences into:

  * a hospital **code status**     — Full code / DNR / DNI / DNR+DNI, with an optional
                                     "Do Not Escalate" qualifier (no ICU transfer /
                                     no escalation of current therapies);
  * a **POLST Section A** order    — Attempt CPR / Do Not Attempt Resuscitation (DNAR);
  * a **POLST Section B** level    — Full / Selective / Comfort-Focused Treatment.

Design note on scope of each axis:
  - Code status / Section A are **scenario-grounded**: a conditional refusal ("no CPR if
    NYHA IV with no reversible cause") only yields DNR when its conditions are met in the
    given scenario. This is exactly the conditionality a flat POLST checkbox cannot express,
    and surfacing it is ADO's value-add (we report it explicitly).
  - Section B (overall treatment goal) is **standing**: it reflects the patient's general
    willingness to accept selective interventions, read from their preference set rather
    than a single acute snapshot.

This is the enabler for Track 3 (the flagship quantitative evaluation): preference profile
-> derived code status, scored against a POLST-semantics gold standard.

Usage:
    python code_status.py                              # example patient, canonical EOL scenario
    python code_status.py --owl path/to/populated.owl
    python code_status.py --eval                       # run the built-in gold-standard check
"""

import argparse
import sys
from pathlib import Path

try:
    from owlready2 import get_ontology
except ImportError:
    print("ERROR: owlready2 is not installed. Run: pip install owlready2")
    sys.exit(1)

from query_evaluation import find_matching_preferences

# ── Intervention groups (OWL class names) ───────────────────────────────────
RESUSCITATION = ["CPR"]
INTUBATION = ["Intubation", "MechanicalVentilation", "IndefiniteVentilation"]
ESCALATION = ["InotropeEscalation", "VasopressorEscalation"]
# "Selective" interventions: time-limited / recoverable measures a patient may accept even
# while refusing full resuscitation.
SELECTIVE = ["TemporaryVentilation", "NonInvasiveVentilation", "AcuteDialysis",
             "InotropeEscalation", "VasopressorEscalation"]

# A canonical advanced-HF end-of-life scenario, used when none is supplied: NYHA IV cardiac
# arrest with no reversible cause — the state in which resuscitation preferences activate.
CANONICAL_EOL_SCENARIO = {
    "conditions": ["CardiacArrest"],
    "nyha_class": "NYHA_ClassIV",
    "reversible_cause": False,
}


def decide_intervention(onto, patient, intervention, scenario):
    """Collapse the reasoner's matches for one intervention into a single decision.

    Returns (decision, match_type, conditional, detail) where decision is one of
    'yes' / 'no' / 'partial' / 'vague' / 'no_coverage', and `conditional` is True when the
    firing preference depended on activation conditions (i.e., is not an unconditional order).
    """
    matches = find_matching_preferences(onto, patient, intervention, scenario)
    if not matches:
        return "no_coverage", "no_coverage", False, "No preference for this intervention"

    # clear > vague > partial, mirroring evaluate_vignette()
    clear = [m for m in matches if m[1] == "clear"]
    vague = [m for m in matches if m[1] == "vague"]
    chosen = clear[0] if clear else (vague[0] if vague else matches[0])
    pref, match_type, detail = chosen
    conditional = "applies unconditionally" not in detail

    if match_type == "clear":
        negated = bool(pref.isNegated and pref.isNegated[0])
        decision = "no" if negated else "yes"
    elif match_type == "vague":
        decision = "vague"
    else:
        decision = "partial"
    return decision, match_type, conditional, detail


def _group_refuses(onto, patient, classes, scenario):
    """True/conditional if the patient clearly refuses any intervention in the group, given
    the scenario. Returns (refuses: bool, conditional: bool, evidence: list)."""
    refuses = False
    conditional = False
    evidence = []
    for cls in classes:
        decision, mt, cond, detail = decide_intervention(onto, patient, cls, scenario)
        if decision == "no" and mt == "clear":
            refuses = True
            conditional = conditional or cond
            evidence.append(f"{cls}: refused ({'conditional' if cond else 'unconditional'})")
    return refuses, conditional, evidence


def _standing_acceptance(patient, classes):
    """True if the patient has any non-negated (accepting) preference for the given
    interventions — read from the preference set, independent of the current scenario."""
    wanted = set(classes)
    for pref in patient.hasPreference:
        if not pref.specifiesIntervention:
            continue
        interv = pref.specifiesIntervention[0]
        cls_name = type(interv).__name__
        negated = bool(pref.isNegated and pref.isNegated[0])
        if cls_name in wanted and not negated:
            return True
    return False


def _surrogate_overridable(patient):
    """Forward-compatible hook for the who-decides axis. Returns True if any preference (or
    the patient) is flagged as surrogate-modifiable. The `surrogateMayOverride` /
    `deferToSurrogate` properties are added in the next workstream-B increment; until then
    this returns False and the qualifier simply does not appear."""
    if getattr(patient, "deferToSurrogate", None):
        return True
    for pref in patient.hasPreference:
        if getattr(pref, "surrogateMayOverride", None):
            return True
    return False


def derive_code_status(onto, patient, scenario=None):
    """Aggregate a patient's preferences into a code-status recommendation."""
    scenario = scenario if scenario is not None else CANONICAL_EOL_SCENARIO

    dnr, dnr_cond, dnr_ev = _group_refuses(onto, patient, RESUSCITATION, scenario)
    dni, dni_cond, dni_ev = _group_refuses(onto, patient, INTUBATION, scenario)
    no_esc, esc_cond, esc_ev = _group_refuses(onto, patient, ESCALATION, scenario)

    # Hospital code status
    if dnr and dni:
        code = "DNR/DNI"
    elif dnr:
        code = "DNR"
    elif dni:
        code = "DNI"
    else:
        code = "Full code"
    if no_esc and code != "Full code":
        code += " + Do Not Escalate"
    elif no_esc:
        code = "Do Not Escalate"

    # POLST Section A (resuscitation order)
    polst_a = "Do Not Attempt Resuscitation (DNAR)" if dnr else "Attempt CPR/Full Resuscitation"

    # POLST Section B (overall treatment level) — standing willingness.
    # Turns on refusal of *life-sustaining* treatment (intubation or escalation), NOT on DNR
    # alone: a DNR patient can still be Full Treatment, because resuscitation (Section A) only
    # applies once the patient is pulseless.
    accepts_selective = _standing_acceptance(patient, SELECTIVE)
    accepts_full = decide_intervention(onto, patient, "Intubation", scenario)[0] == "yes"
    refuses_lifesustaining = dni or no_esc
    if refuses_lifesustaining and accepts_selective:
        polst_b = "Selective Treatment"
    elif refuses_lifesustaining and not accepts_selective:
        polst_b = "Comfort-Focused Treatment"
    elif accepts_full:
        polst_b = "Full Treatment"
    elif accepts_selective:
        polst_b = "Selective Treatment"
    else:
        polst_b = "Not specified"

    conditional = dnr_cond or dni_cond or esc_cond

    return {
        "code_status": code,
        "polst_section_a": polst_a,
        "polst_section_b": polst_b,
        "conditional": conditional,
        "surrogate_overridable": _surrogate_overridable(patient),
        "evidence": dnr_ev + dni_ev + esc_ev,
        "accepts_selective": accepts_selective,
    }


def print_code_status(label, result, scenario):
    print(f"\n{'=' * 78}")
    print(f"  CODE STATUS — {label}")
    print(f"{'=' * 78}")
    print(f"  Scenario            : {scenario}")
    print(f"  Hospital code status: {result['code_status']}")
    print(f"  POLST Section A     : {result['polst_section_a']}")
    print(f"  POLST Section B     : {result['polst_section_b']}")
    if result["conditional"]:
        print("  NOTE: derived from a CONDITIONAL preference — a flat POLST/code-status order")
        print("        cannot express this conditionality; ADO preserves it.")
    if result["surrogate_overridable"]:
        print("  NOTE: surrogate is authorized to override — status is surrogate-modifiable.")
    if result["evidence"]:
        print("  Evidence:")
        for e in result["evidence"]:
            print(f"    - {e}")


# ── Track 3 gold-standard harness ───────────────────────────────────────────
# Gold standards derived from POLST's published definitional semantics (self-adjudicated),
# NOT from ADO's own logic — that independence is what makes the agreement meaningful.
GOLD_STANDARD = {
    "jane_doe_001": {
        "scenario": CANONICAL_EOL_SCENARIO,
        "code_status": "DNR/DNI",
        "polst_section_a": "Do Not Attempt Resuscitation (DNAR)",
        "polst_section_b": "Selective Treatment",
    },
}


def run_eval(onto, patient):
    pid = patient.name if patient.name in GOLD_STANDARD else None
    if pid is None:
        # try to match by label substring
        for key in GOLD_STANDARD:
            if key.split("_")[0].lower() in (patient.name or "").lower():
                pid = key
                break
    if pid is None:
        print("No gold standard found for this patient; printing derived status only.")
        result = derive_code_status(onto, patient)
        print_code_status(patient.name, result, CANONICAL_EOL_SCENARIO)
        return

    gold = GOLD_STANDARD[pid]
    result = derive_code_status(onto, patient, gold["scenario"])
    print_code_status(pid, result, gold["scenario"])

    fields = ["code_status", "polst_section_a", "polst_section_b"]
    print(f"\n  {'Field':<20}{'Derived':<42}{'Gold':<42}{'Match'}")
    correct = 0
    for f in fields:
        match = result[f] == gold[f]
        correct += int(match)
        print(f"  {f:<20}{result[f]:<42}{gold[f]:<42}{'PASS' if match else 'FAIL'}")
    print(f"\n  Agreement: {correct}/{len(fields)} fields")


def main():
    parser = argparse.ArgumentParser(description="Derive code status from a populated ADO ontology")
    parser.add_argument("--owl", default="populated_ontologies/ado_jane_doe_001.owl",
                        help="Path to populated ontology file")
    parser.add_argument("--eval", action="store_true",
                        help="Run the Track-3 gold-standard comparison")
    args = parser.parse_args()

    owl_path = Path(args.owl)
    if not owl_path.exists():
        print(f"ERROR: Ontology file not found: {owl_path}")
        sys.exit(1)

    onto = get_ontology(str(owl_path.resolve())).load()
    patients = list(onto.search(type=onto.Patient))
    if not patients:
        print("ERROR: No Patient individuals found in ontology")
        sys.exit(1)
    patient = max(patients, key=lambda p: len(p.hasPreference) if p.hasPreference else 0)

    if args.eval:
        run_eval(onto, patient)
    else:
        result = derive_code_status(onto, patient)
        print_code_status(patient.label[0] if patient.label else patient.name,
                          result, CANONICAL_EOL_SCENARIO)


if __name__ == "__main__":
    main()
