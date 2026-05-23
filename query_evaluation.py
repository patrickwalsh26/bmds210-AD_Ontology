"""
Scenario-Based Query Evaluation for the Advanced Directive Ontology

Defines clinical vignettes (patient state + question) and queries the
populated ontology to determine what care is indicated.  Compares system
output against a human-defined expected answer to measure concordance.

Usage:
    python query_evaluation.py                        # Run against example patient
    python query_evaluation.py --owl path/to/file.owl # Run against a specific populated ontology
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from owlready2 import get_ontology, default_world
except ImportError:
    print("ERROR: owlready2 is not installed. Run: pip install owlready2")
    sys.exit(1)


def parse_duration_to_hours(value):
    """Parse a duration string like '96 hours', '3 days', '4d', '72h' into hours.

    Returns an int or None if unparseable. Pure ints/floats are treated as hours.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    s = str(value).strip().lower()
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([a-z]*)\s*", s)
    if not m:
        return None
    n = float(m.group(1))
    unit = m.group(2)
    if unit in ("", "h", "hr", "hrs", "hour", "hours"):
        return int(n)
    if unit in ("d", "day", "days"):
        return int(n * 24)
    if unit in ("m", "min", "mins", "minute", "minutes"):
        return int(n / 60)
    return None


# ── Clinical Vignettes ──────────────────────────────────────────────────────
# Each vignette defines:
#   - description: plain-language clinical scenario
#   - query_intervention: the intervention type being asked about
#   - scenario_state: the patient's current clinical state
#   - expected: what a clinician would conclude from the AD
#       - decision: "yes" (patient wants it), "no" (patient doesn't), "no_coverage", "partial"
#       - match_type: "clear", "partial", "no_coverage", "vague"
#       - reasoning: why this is the expected answer

VIGNETTES = [
    {
        "id": "V1",
        "description": "Patient is in cardiac arrest, NYHA Class IV, no reversible cause identified. Should CPR be initiated?",
        "query_intervention": "CPR",
        "scenario_state": {
            "conditions": ["CardiacArrest"],
            "nyha_class": "NYHA_ClassIV",
            "reversible_cause": False,
        },
        "expected": {
            "decision": "no",
            "match_type": "clear",
            "reasoning": "Patient explicitly stated: no CPR if NYHA IV with no reversible cause. All activation conditions met.",
        },
    },
    {
        "id": "V2",
        "description": "Patient is in cardiac arrest, NYHA Class III, with a potentially reversible cause (hyperkalemia). Should CPR be initiated?",
        "query_intervention": "CPR",
        "scenario_state": {
            "conditions": ["CardiacArrest"],
            "nyha_class": "NYHA_ClassIII",
            "reversible_cause": True,
        },
        "expected": {
            "decision": "partial",
            "match_type": "partial",
            "reasoning": "Patient's no-CPR preference requires NYHA IV AND no reversible cause. Patient is NYHA III with a reversible cause — activation conditions not met. No affirmative CPR preference exists either, so the AD does not clearly address this scenario.",
        },
    },
    {
        "id": "V3",
        "description": "Patient has acute respiratory failure with a reversible cause (pneumonia). Should temporary mechanical ventilation be initiated?",
        "query_intervention": "TemporaryVentilation",
        "scenario_state": {
            "conditions": ["RespiratoryFailure"],
            "reversible_cause": True,
        },
        "expected": {
            "decision": "yes",
            "match_type": "clear",
            "reasoning": "Patient accepts temporary ventilation if there is a reversible cause. Reversible cause is present.",
        },
    },
    {
        "id": "V4",
        "description": "Patient has been on a ventilator for 10 days with no improvement and no reversible cause. Should indefinite ventilation continue?",
        "query_intervention": "IndefiniteVentilation",
        "scenario_state": {
            "conditions": ["RespiratoryFailure"],
            "reversible_cause": False,
        },
        "expected": {
            "decision": "no",
            "match_type": "clear",
            "reasoning": "Patient has an absolute preference against indefinite ventilation (no activation conditions — applies universally).",
        },
    },
    {
        "id": "V5",
        "description": "Patient has been enrolled in hospice. Should the ICD be deactivated?",
        "query_intervention": "ICDDeactivation",
        "scenario_state": {
            "conditions": [],
            "care_context": "HospiceEnrollment",
        },
        "expected": {
            "decision": "yes",
            "match_type": "clear",
            "reasoning": "Patient wants ICD deactivation if enrolled in hospice. With requiresCareContext now populated, the hospice activation condition matches the scenario and the reasoner returns a clear 'yes' via the correct reasoning path.",
        },
    },
    {
        "id": "V6",
        "description": "Patient is in the ICU, not enrolled in hospice. Should the ICD be deactivated?",
        "query_intervention": "ICDDeactivation",
        "scenario_state": {
            "conditions": [],
            "care_context": "ICUSetting",
        },
        "expected": {
            "decision": "partial",
            "match_type": "partial",
            "reasoning": "Patient's only ICD deactivation preference is conditional on hospice enrollment. Scenario is ICU, so the activation condition (HospiceEnrollment) is explicitly unmet. The AD addresses ICD deactivation but provides no guidance for this care context — partial match, decision deferred to surrogate.",
        },
    },
    {
        "id": "V7",
        "description": "Patient has cardiorenal syndrome with expected kidney recovery. Should acute dialysis be initiated?",
        "query_intervention": "AcuteDialysis",
        "scenario_state": {
            "conditions": ["CardiorenalSyndrome"],
            "reversible_cause": True,
        },
        "expected": {
            "decision": "yes",
            "match_type": "clear",
            "reasoning": "Patient accepts acute dialysis if cardiorenal syndrome with reversible cause. Both conditions met.",
        },
    },
    {
        "id": "V8",
        "description": "Patient has progressive kidney failure with no expectation of recovery. Should chronic/maintenance dialysis be initiated?",
        "query_intervention": "ChronicDialysis",
        "scenario_state": {
            "conditions": ["CardiorenalSyndrome"],
            "reversible_cause": False,
        },
        "expected": {
            "decision": "no",
            "match_type": "clear",
            "reasoning": "Patient has an absolute preference against chronic dialysis (no activation conditions — applies universally).",
        },
    },
    {
        "id": "V9",
        "description": "Patient is in cardiogenic shock. Should inotropes be escalated?",
        "query_intervention": "InotropeEscalation",
        "scenario_state": {
            "conditions": ["CardiogenicShock"],
        },
        "expected": {
            "decision": "yes",
            "match_type": "clear",
            "reasoning": "Patient accepts inotrope escalation if cardiogenic shock is present — condition met. Note: the original text specifies 'only if there is a plan for LVAD or transplant evaluation,' but this was not encoded as a formal activation condition. The system correctly matches the encoded conditions but misses the nuance in the original language — a limitation of the structured encoding, not the reasoner.",
        },
    },
    {
        "id": "V10",
        "description": "Patient is in cardiogenic shock, on vasopressors for 4 days with no improvement. Should vasopressors be withdrawn?",
        "query_intervention": "VasopressorWithdrawal",
        "scenario_state": {
            "conditions": ["CardiogenicShock"],
            "time_elapsed": "96 hours",
        },
        "expected": {
            "decision": "yes",
            "match_type": "clear",
            "reasoning": "Patient wants vasopressor withdrawal if cardiogenic shock with no improvement after 72 hours. With hasTimeBoundHours now stored as a numeric property and a comparable scenario time, the reasoner evaluates 96h >= 72h directly and returns a clear 'yes'. Resolves the V10 temporal-reasoning gap from the May 6 progress report.",
        },
    },
    {
        "id": "V11",
        "description": "Patient is in respiratory failure. Should non-invasive ventilation (e.g., BiPAP) be initiated?",
        "query_intervention": "NonInvasiveVentilation",
        "scenario_state": {
            "conditions": ["RespiratoryFailure"],
        },
        "expected": {
            "decision": "vague",
            "match_type": "vague",
            "reasoning": "Patient's only NIV-relevant statement is 'If I am dying, I do not want aggressive measures or to be kept alive by machines.' The system surfaces the original language verbatim and flags the match as vague rather than forcing a binary answer — 'aggressive measures' is broader than the formal NIV class. Demonstrates how the ontology preserves patient voice when language is irreducibly imprecise.",
        },
    },
    {
        "id": "V12",
        "description": "Patient is stable, NYHA Class II. Should the pacemaker be deactivated?",
        "query_intervention": "PacemakerDeactivation",
        "scenario_state": {
            "conditions": [],
            "nyha_class": "NYHA_ClassII",
        },
        "expected": {
            "decision": "no_coverage",
            "match_type": "no_coverage",
            "reasoning": "Patient's AD does not mention pacemaker deactivation at all. No preference exists for this intervention.",
        },
    },
    {
        "id": "V13",
        "description": "Patient is in cardiogenic shock, on vasopressors for only 48 hours, no improvement yet. Should vasopressors be withdrawn?",
        "query_intervention": "VasopressorWithdrawal",
        "scenario_state": {
            "conditions": ["CardiogenicShock"],
            "time_elapsed": "48 hours",
        },
        "expected": {
            "decision": "partial",
            "match_type": "partial",
            "reasoning": "Patient wants vasopressor withdrawal if cardiogenic shock with no improvement after 72 hours. Cardiogenic shock matches, but only 48h elapsed — time threshold not yet met. Reasoner correctly returns partial: 'wait, not yet authorized.' Demonstrates the temporal logic in the 'doesn't fire yet' direction (complement of V10).",
        },
    },
    {
        "id": "V14",
        "description": "Patient has sepsis-induced acute kidney injury (not cardiorenal syndrome); kidney recovery is expected. Should acute dialysis be initiated?",
        "query_intervention": "AcuteDialysis",
        "scenario_state": {
            "conditions": [],
            "reversible_cause": True,
        },
        "expected": {
            "decision": "partial",
            "match_type": "partial",
            "reasoning": "Patient's acute dialysis preference requires both cardiorenal syndrome AND a reversible cause. Reversible cause matches, but the underlying clinical condition is sepsis-AKI, not cardiorenal syndrome. Reasoner correctly flags partial: the AD's authorization is conditioned on a specific HF-related etiology, not generic AKI.",
        },
    },
    {
        "id": "V15",
        "description": "Patient is stable, in an outpatient nephrology consultation about long-term dialysis access. Should chronic dialysis be initiated?",
        "query_intervention": "ChronicDialysis",
        "scenario_state": {
            "conditions": [],
            "care_context": "OutpatientSetting",
        },
        "expected": {
            "decision": "no",
            "match_type": "clear",
            "reasoning": "Patient has an Absolute, unconditional refusal of chronic dialysis. Preference applies regardless of care context, NYHA class, or other state. Demonstrates that an Absolute preference correctly fires in non-acute settings — not just at end of life.",
        },
    },
    {
        "id": "V16",
        "description": "Patient is in ventricular tachycardia and the ICD is about to deliver a shock. Should ICD shock therapy be allowed to proceed?",
        "query_intervention": "ICDShockTherapy",
        "scenario_state": {
            "conditions": [],
            "care_context": "ICUSetting",
        },
        "expected": {
            "decision": "no_coverage",
            "match_type": "no_coverage",
            "reasoning": "Patient's only ICD-related preference addresses deactivation (a planned, durable change) conditional on hospice enrollment. ICD shock therapy is a distinct intervention — a single therapeutic event during an arrhythmia. The reasoner correctly distinguishes the two and reports no coverage rather than defaulting to the nearest ICD preference. Tests that intervention granularity prevents over-inference.",
        },
    },
]


def find_matching_preferences(onto, patient, query_intervention, scenario_state):
    """
    Query the ontology to find preferences that match a clinical scenario.

    Returns a list of (preference, match_type, details) tuples.
    """
    matches = []

    # Get the intervention class we're asking about
    intervention_cls = getattr(onto, query_intervention, None)
    if intervention_cls is None:
        return []

    for pref in patient.hasPreference:
        # Check if this preference addresses the queried intervention
        interventions = pref.specifiesIntervention
        if not interventions:
            continue

        # Check if the preference's intervention is the same class or a subclass
        interv = interventions[0]
        interv_types = [t for t in interv.is_a if hasattr(t, "name")]
        interv_class_names = [t.name for t in interv_types]
        interv_class_names.append(type(interv).__name__)

        if query_intervention not in interv_class_names and intervention_cls not in interv_types:
            # Also check if it's the same class by name
            if type(interv).__name__ != query_intervention:
                continue

        # Pre-compute VaguePreference flag so the early-return branch below can honor it.
        is_vague = any(getattr(cls, "name", "") == "VaguePreference" for cls in pref.is_a)

        # This preference addresses the right intervention — now check activation conditions
        activation_conditions = pref.hasActivationCondition
        if not activation_conditions:
            # No activation conditions = unconditional preference (always applies)
            if is_vague:
                orig = pref.originalText[0] if pref.originalText else "(no original text recorded)"
                detail = f"VAGUE preference — original language: \"{orig}\". Applies unconditionally but in irreducibly imprecise language."
                matches.append((pref, "vague", detail))
            else:
                matches.append((pref, "clear", "No activation conditions — applies unconditionally"))
            continue

        ac = activation_conditions[0]
        conditions_met = []
        conditions_unmet = []

        # Check NYHA class
        required_nyha = ac.requiresFunctionalStatus
        if required_nyha:
            req_nyha_name = type(required_nyha[0]).__name__
            scenario_nyha = scenario_state.get("nyha_class")
            if scenario_nyha and scenario_nyha == req_nyha_name:
                conditions_met.append(f"NYHA class: {req_nyha_name}")
            elif scenario_nyha:
                conditions_unmet.append(f"Requires {req_nyha_name}, patient is {scenario_nyha}")
            else:
                conditions_unmet.append(f"Requires {req_nyha_name}, NYHA class unknown")

        # Check clinical conditions
        required_conditions = ac.requiresCondition
        scenario_conditions = scenario_state.get("conditions", [])
        for req_cond in required_conditions:
            req_cond_class = type(req_cond).__name__
            if req_cond_class in scenario_conditions:
                conditions_met.append(f"Condition: {req_cond_class}")
            else:
                conditions_unmet.append(f"Requires condition: {req_cond_class}")

        # Check reversible cause
        required_reversible = ac.hasReversibleCause
        if required_reversible:
            scenario_reversible = scenario_state.get("reversible_cause")
            if scenario_reversible is not None:
                if scenario_reversible == required_reversible[0]:
                    conditions_met.append(f"Reversible cause: {required_reversible[0]}")
                else:
                    conditions_unmet.append(
                        f"Requires reversible_cause={required_reversible[0]}, "
                        f"scenario has {scenario_reversible}"
                    )
            else:
                conditions_unmet.append("Reversible cause status unknown in scenario")

        # Check care context (e.g., HospiceEnrollment, ICUSetting)
        required_ctx = ac.requiresCareContext
        if required_ctx:
            req_ctx_name = type(required_ctx[0]).__name__
            scenario_ctx = scenario_state.get("care_context")
            if scenario_ctx == req_ctx_name:
                conditions_met.append(f"Care context: {req_ctx_name}")
            elif scenario_ctx:
                conditions_unmet.append(
                    f"Requires care context {req_ctx_name}, scenario has {scenario_ctx}"
                )
            else:
                conditions_unmet.append(f"Requires care context {req_ctx_name}, none in scenario")

        # Check time bound: prefer numeric hasTimeBoundHours; fall back to string
        time_bound_hours = ac.hasTimeBoundHours
        scenario_elapsed_hours = parse_duration_to_hours(scenario_state.get("time_elapsed"))
        if time_bound_hours:
            req_hours = int(time_bound_hours[0])
            if scenario_elapsed_hours is not None:
                if scenario_elapsed_hours >= req_hours:
                    conditions_met.append(
                        f"Time bound: scenario {scenario_elapsed_hours}h >= required {req_hours}h"
                    )
                else:
                    conditions_unmet.append(
                        f"Time bound: scenario {scenario_elapsed_hours}h < required {req_hours}h"
                    )
            else:
                conditions_unmet.append(
                    f"Time bound: requires >= {req_hours}h elapsed, scenario time unknown"
                )
        else:
            time_bound = ac.hasTimeBound
            if time_bound:
                conditions_unmet.append(
                    f"Time bound '{time_bound[0]}' requires human interpretation"
                )

        # Determine match type
        if not conditions_unmet:
            match_type = "clear"
            detail = "All activation conditions met: " + "; ".join(conditions_met) if conditions_met else "No activation conditions — applies unconditionally"
        elif conditions_met and conditions_unmet:
            match_type = "partial"
            detail = ("Met: " + "; ".join(conditions_met) +
                      " | Unmet: " + "; ".join(conditions_unmet))
        else:
            match_type = "partial"
            detail = "Unmet: " + "; ".join(conditions_unmet)

        # VaguePreference always carries forward as 'vague' regardless of activation logic,
        # because the underlying preference language is irreducibly imprecise. The original
        # text is surfaced so a human can interpret rather than the reasoner forcing an answer.
        if is_vague:
            orig = pref.originalText[0] if pref.originalText else "(no original text recorded)"
            detail = f"VAGUE preference — original language: \"{orig}\". " + detail
            match_type = "vague"

        matches.append((pref, match_type, detail))

    return matches


def evaluate_vignette(onto, patient, vignette):
    """Evaluate a single clinical vignette and return the result."""
    matches = find_matching_preferences(
        onto, patient,
        vignette["query_intervention"],
        vignette["scenario_state"],
    )

    if not matches:
        system_decision = "no_coverage"
        system_match_type = "no_coverage"
        detail = "No preferences found for this intervention"
    elif len(matches) == 1:
        pref, match_type, detail = matches[0]
        negated = pref.isNegated[0] if pref.isNegated else False
        if match_type == "clear":
            system_decision = "no" if negated else "yes"
        elif match_type == "vague":
            system_decision = "vague"
        else:
            system_decision = "partial"
        system_match_type = match_type
    else:
        # Multiple matches — clear > vague > partial in priority
        clear_matches = [(p, mt, d) for p, mt, d in matches if mt == "clear"]
        vague_matches = [(p, mt, d) for p, mt, d in matches if mt == "vague"]
        if clear_matches:
            pref, match_type, detail = clear_matches[0]
            negated = pref.isNegated[0] if pref.isNegated else False
            system_decision = "no" if negated else "yes"
            system_match_type = "clear"
        elif vague_matches:
            pref, match_type, detail = vague_matches[0]
            system_decision = "vague"
            system_match_type = "vague"
        else:
            pref, match_type, detail = matches[0]
            system_decision = "partial"
            system_match_type = "partial"
            detail = "; ".join(d for _, _, d in matches)

    expected = vignette["expected"]
    decision_correct = system_decision == expected["decision"]
    match_type_correct = system_match_type == expected["match_type"]

    return {
        "id": vignette["id"],
        "description": vignette["description"],
        "query_intervention": vignette["query_intervention"],
        "system_decision": system_decision,
        "expected_decision": expected["decision"],
        "decision_correct": decision_correct,
        "system_match_type": system_match_type,
        "expected_match_type": expected["match_type"],
        "match_type_correct": match_type_correct,
        "detail": detail,
        "expected_reasoning": expected["reasoning"],
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate ADO against clinical vignettes")
    parser.add_argument("--owl", type=str,
                        default="populated_ontologies/ado_jane_doe_001.owl",
                        help="Path to populated ontology file")
    args = parser.parse_args()

    owl_path = Path(args.owl)
    if not owl_path.exists():
        print(f"ERROR: Ontology file not found: {owl_path}")
        sys.exit(1)

    print("Loading ontology...")
    onto = get_ontology(str(owl_path.resolve())).load()

    # Find the patient with the most preferences (the pipeline-created one)
    patients = list(onto.search(type=onto.Patient))
    if not patients:
        print("ERROR: No Patient individuals found in ontology")
        sys.exit(1)

    patient = max(patients, key=lambda p: len(p.hasPreference) if p.hasPreference else 0)

    print(f"Patient: {patient.label[0] if patient.label else patient.name}")
    print(f"Preferences: {len(patient.hasPreference)}")
    print()

    # Run evaluation
    print("=" * 80)
    print("  SCENARIO-BASED QUERY EVALUATION")
    print("=" * 80)

    results = []
    for vignette in VIGNETTES:
        result = evaluate_vignette(onto, patient, vignette)
        results.append(result)

    # Print results
    correct_decisions = 0
    correct_match_types = 0
    total = len(results)

    for r in results:
        decision_mark = "PASS" if r["decision_correct"] else "FAIL"
        match_mark = "PASS" if r["match_type_correct"] else "FAIL"

        if r["decision_correct"]:
            correct_decisions += 1
        if r["match_type_correct"]:
            correct_match_types += 1

        print(f"\n{'─' * 80}")
        print(f"  {r['id']}: {r['description']}")
        print(f"{'─' * 80}")
        print(f"  Intervention queried : {r['query_intervention']}")
        print(f"  System decision      : {r['system_decision']:12s}  Expected: {r['expected_decision']:12s}  [{decision_mark}]")
        print(f"  System match type    : {r['system_match_type']:12s}  Expected: {r['expected_match_type']:12s}  [{match_mark}]")
        print(f"  Detail               : {r['detail']}")
        print(f"  Expected reasoning   : {r['expected_reasoning']}")

    # Summary
    print(f"\n{'=' * 80}")
    print(f"  SUMMARY")
    print(f"{'=' * 80}")
    print(f"  Total vignettes      : {total}")
    print(f"  Decision accuracy    : {correct_decisions}/{total} ({100*correct_decisions/total:.0f}%)")
    print(f"  Match type accuracy  : {correct_match_types}/{total} ({100*correct_match_types/total:.0f}%)")
    print()

    # Breakdown by match type
    by_type = {}
    for r in results:
        t = r["expected_match_type"]
        if t not in by_type:
            by_type[t] = {"total": 0, "decision_correct": 0, "match_correct": 0}
        by_type[t]["total"] += 1
        if r["decision_correct"]:
            by_type[t]["decision_correct"] += 1
        if r["match_type_correct"]:
            by_type[t]["match_correct"] += 1

    print("  By expected match type:")
    for t, counts in sorted(by_type.items()):
        print(f"    {t:15s}: {counts['decision_correct']}/{counts['total']} decisions correct, "
              f"{counts['match_correct']}/{counts['total']} match types correct")

    # Failure analysis
    failures = [r for r in results if not r["decision_correct"] or not r["match_type_correct"]]
    if failures:
        print(f"\n  Failures ({len(failures)}):")
        for r in failures:
            print(f"    {r['id']}: expected {r['expected_decision']}/{r['expected_match_type']}, "
                  f"got {r['system_decision']}/{r['system_match_type']}")
    else:
        print("\n  No failures.")


if __name__ == "__main__":
    main()
