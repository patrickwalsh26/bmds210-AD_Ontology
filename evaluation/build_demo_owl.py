#!/usr/bin/env python3
"""
Build a rich 3-patient demo OWL file for the Protégé live demo.

Populates the base ADO ontology with three patients chosen to tell a
complete story during a 90-second Protégé walkthrough:

  Patient 1 — Margaret Chen (68yo, LVAD)
      13 preferences across all 5 decision-point domains.
      Rich activation conditions. The "hero" patient.

  Patient 2 — James Okafor (71yo, chronic HF)
      4 preferences — sparse but coherent. Shows the system works
      even when directives are minimal.

  Patient 3 — Elena Vasquez (74yo, device patient)
      3 preferences with vague/conditional language.
      Shows VaguePreference type and how the system surfaces
      original text rather than guessing.

Output: data/populated/ado_demo_presentation.owl

Usage:
    python evaluation/build_demo_owl.py

Then open ado_demo_presentation.owl in Protégé 5.
Protégé demo flow:
  1. Classes tab → Intervention hierarchy (5 branches, 21 leaves)
  2. Object Properties → hasPreference / hasActivationCondition
  3. Individuals → Patient_MargaretChen → Pref_MC_1 (CPR) → AC_MC_1
  4. Run HermiT → confirm consistent
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

from ado.preference_input import load_ontology, populate_patient
from ado.paths import POPULATED_DIR

# ── Patient definitions ────────────────────────────────────────────────────────

MARGARET_CHEN = {
    "patient_id": "margaret_chen",
    "patient_name": "Margaret Chen",
    "proxy": {
        "name": "David Chen",
        "relationship": "Spouse"
    },
    "source_document": {
        "type": "living_will",
        "label": "Margaret Chen Living Will — June 2024 (notarized)"
    },
    "preferences": [
        # ── RESUSCITATION ─────────────────────────────────────────────────────
        {
            "label": "No CPR in end-stage HF without reversible cause",
            "intervention": "cpr",
            "negated": True,
            "strength": "Absolute",
            "type": "conditional",
            "original_text": (
                "I do not wish to receive CPR if I am in end-stage heart failure "
                "with no medically reversible cause. I have thought carefully about "
                "this and understand the low likelihood of meaningful recovery."
            ),
            "activation_conditions": {
                "nyha_class": "IV",
                "conditions": ["cardiac_arrest"],
                "reversible_cause": False,
            },
        },
        {
            "label": "No defibrillation in end-stage HF",
            "intervention": "defibrillation",
            "negated": True,
            "strength": "Absolute",
            "type": "conditional",
            "original_text": (
                "External defibrillation should not be attempted in the setting of "
                "end-stage heart failure unless there is a clear reversible cause such "
                "as electrolyte abnormality or drug toxicity."
            ),
            "activation_conditions": {
                "nyha_class": "IV",
                "reversible_cause": False,
            },
        },

        # ── DEVICE MANAGEMENT ─────────────────────────────────────────────────
        {
            "label": "Deactivate ICD in hospice or end-stage disease",
            "intervention": "icd_deactivation",
            "negated": False,
            "strength": "Strong",
            "type": "conditional",
            "original_text": (
                "If I enroll in hospice care or if my doctors determine I have reached "
                "end-stage heart failure with no further curative options, I want my ICD "
                "turned off. Repeated shocks at the end of life are not acceptable to me."
            ),
            "activation_conditions": {
                "nyha_class": "IV",
                "care_context": "hospice",
            },
        },
        {
            "label": "ICD shock therapy — conditional if firing repeatedly",
            "intervention": "icd_shock_therapy",
            "negated": False,
            "strength": "Conditional",
            "type": "conditional",
            "original_text": (
                "If my ICD fires more than three times in 24 hours without meaningful "
                "improvement in my clinical status, I want a goals-of-care conversation "
                "about turning it off. I do not want to be kept alive by repeated shocks."
            ),
            "activation_conditions": {
                "nyha_class": "IV",
                "conditions": ["ventricular_tachycardia"],
                "care_context": "icu",
            },
        },
        {
            "label": "LVAD withdrawal if permanently unconscious",
            "intervention": "lvad_withdrawal",
            "negated": False,
            "strength": "Absolute",
            "type": "conditional",
            "original_text": (
                "If I reach a state of permanent unconsciousness from which my doctors "
                "believe I cannot recover, I want my LVAD deactivated. I do not wish to "
                "remain alive by mechanical means without any prospect of awareness."
            ),
            "activation_conditions": {
                "conditions": ["permanent_unconsciousness"],
                "reversible_cause": False,
            },
        },

        # ── VENTILATION ───────────────────────────────────────────────────────
        {
            "label": "Temporary ventilation OK if reversible",
            "intervention": "temporary_ventilation",
            "negated": False,
            "strength": "Conditional",
            "type": "conditional",
            "original_text": (
                "I am willing to be placed on a breathing machine for up to two weeks "
                "if there is a genuine medical reason to believe I can be weaned off and "
                "return to a meaningful quality of life. This is a time-limited trial."
            ),
            "activation_conditions": {
                "conditions": ["respiratory_failure"],
                "reversible_cause": True,
                "time_bound": "14 days maximum",
                "time_bound_hours": 336,
            },
        },
        {
            "label": "No indefinite mechanical ventilation — ever",
            "intervention": "indefinite_ventilation",
            "negated": True,
            "strength": "Absolute",
            "type": "clear",
            "original_text": (
                "I absolutely refuse long-term or permanent ventilator dependence. "
                "If I cannot be weaned from a ventilator within two weeks, I want it "
                "withdrawn and to be made comfortable."
            ),
            "activation_conditions": {
                "time_bound": "if cannot be weaned in 14 days",
                "time_bound_hours": 336,
            },
        },
        {
            "label": "Non-invasive ventilation acceptable for comfort",
            "intervention": "non_invasive_ventilation",
            "negated": False,
            "strength": "Strong",
            "type": "clear",
            "original_text": (
                "I am willing to use BiPAP or CPAP if it relieves my shortness of breath "
                "and improves my comfort. This is different from being intubated."
            ),
        },

        # ── PHARMACOLOGIC ─────────────────────────────────────────────────────
        {
            "label": "Inotropes acceptable as bridge — 72 hour limit",
            "intervention": "inotrope_escalation",
            "negated": False,
            "strength": "Conditional",
            "type": "conditional",
            "original_text": (
                "I accept escalation of inotropic support (milrinone, dobutamine) as a "
                "bridge to a decision for up to 72 hours. If I have not improved enough "
                "to discuss longer-term options, I do not want them continued indefinitely."
            ),
            "activation_conditions": {
                "conditions": ["cardiogenic_shock"],
                "reversible_cause": True,
                "time_bound": "72 hours maximum",
                "time_bound_hours": 72,
            },
        },
        {
            "label": "No vasopressor escalation in end-stage disease",
            "intervention": "vasopressor_escalation",
            "negated": True,
            "strength": "Absolute",
            "type": "conditional",
            "original_text": (
                "I do not want escalating doses of vasopressors to keep me alive "
                "in the setting of end-stage heart failure. Comfort is my priority."
            ),
            "activation_conditions": {
                "nyha_class": "IV",
                "conditions": ["cardiogenic_shock"],
                "reversible_cause": False,
            },
        },
        {
            "label": "Withdraw vasopressors if no improvement in 72 hours",
            "intervention": "vasopressor_withdrawal",
            "negated": False,
            "strength": "Strong",
            "type": "conditional",
            "original_text": (
                "If I am on vasopressors and there is no meaningful clinical improvement "
                "after 72 hours, I want them withdrawn and to be made comfortable."
            ),
            "activation_conditions": {
                "conditions": ["cardiogenic_shock"],
                "reversible_cause": False,
                "time_bound": "after 72 hours without improvement",
                "time_bound_hours": 72,
            },
        },

        # ── DIALYSIS ─────────────────────────────────────────────────────────
        {
            "label": "Acute dialysis acceptable if kidneys can recover",
            "intervention": "acute_dialysis",
            "negated": False,
            "strength": "Conditional",
            "type": "conditional",
            "original_text": (
                "I accept short-term dialysis if my doctors believe my kidney function "
                "can recover. This must be revisited after 14 days — I am not consenting "
                "to dialysis indefinitely."
            ),
            "activation_conditions": {
                "conditions": ["cardiorenal_syndrome"],
                "reversible_cause": True,
                "time_bound": "reassess at 14 days",
            },
        },
        {
            "label": "No chronic dialysis — ever",
            "intervention": "chronic_dialysis",
            "negated": True,
            "strength": "Absolute",
            "type": "clear",
            "original_text": (
                "I absolutely do not want permanent or chronic dialysis. "
                "I have seen what that quality of life looks like and it is not "
                "consistent with my values."
            ),
        },
    ],
}


JAMES_OKAFOR = {
    "patient_id": "james_okafor",
    "patient_name": "James Okafor",
    "proxy": {
        "name": "Adaeze Okafor",
        "relationship": "Daughter"
    },
    "source_document": {
        "type": "polst",
        "label": "James Okafor POLST — March 2023"
    },
    "preferences": [
        {
            "label": "DNR — do not attempt resuscitation",
            "intervention": "cpr",
            "negated": True,
            "strength": "Absolute",
            "type": "clear",
            "original_text": (
                "Do not attempt CPR. I have discussed this thoroughly with my cardiologist "
                "and my family. My heart condition makes survival from CPR very unlikely, "
                "and the process is not consistent with a dignified death."
            ),
        },
        {
            "label": "Comfort measures only — no aggressive intervention",
            "intervention": "vasopressor_escalation",
            "negated": True,
            "strength": "Absolute",
            "type": "clear",
            "original_text": (
                "I do not want aggressive interventions to prolong my life. "
                "I want comfort-focused care only."
            ),
        },
        {
            "label": "ICD deactivation — already requested",
            "intervention": "icd_deactivation",
            "negated": False,
            "strength": "Strong",
            "type": "clear",
            "original_text": (
                "My ICD should be turned off. I have already spoken to my electrophysiologist "
                "about this. I do not want shocks at the end of my life."
            ),
        },
        {
            "label": "Temporary ventilation for reversible cause only",
            "intervention": "temporary_ventilation",
            "negated": False,
            "strength": "Weak",
            "type": "conditional",
            "original_text": (
                "I would consider a breathing tube only if there is a clear reversible cause "
                "and a reasonable expectation that I would recover. Not otherwise."
            ),
            "activation_conditions": {
                "reversible_cause": True,
                "time_bound": "short trial only — up to 5 days",
                "time_bound_hours": 120,
            },
        },
    ],
}


ELENA_VASQUEZ = {
    "patient_id": "elena_vasquez",
    "patient_name": "Elena Vasquez",
    "proxy": {
        "name": "Roberto Vasquez",
        "relationship": "Son"
    },
    "source_document": {
        "type": "living_will",
        "label": "Elena Vasquez Directiva Anticipada — Enero 2024 (translated)"
    },
    "preferences": [
        {
            "label": "No heroic measures — vague language (directive as written)",
            "intervention": "cpr",
            "negated": True,
            "strength": "Weak",
            "type": "vague",
            "original_text": (
                "'No quiero medidas heroicas.' [Translation: I do not want heroic measures.] "
                "NOTE: Language is vague. 'Heroic measures' is not a defined medical term. "
                "System surfaces original text for clinician interpretation."
            ),
        },
        {
            "label": "Family should decide about breathing machines",
            "intervention": "temporary_ventilation",
            "negated": False,
            "strength": "Conditional",
            "type": "vague",
            "original_text": (
                "'Dejo en manos de mi familia la decision sobre aparatos para respirar.' "
                "[Translation: I leave the decision about breathing machines to my family.] "
                "NOTE: Surrogate-deference clause. System returns 'vague' — defer to proxy."
            ),
        },
        {
            "label": "No long-term machine support — clear refusal",
            "intervention": "indefinite_ventilation",
            "negated": True,
            "strength": "Absolute",
            "type": "clear",
            "original_text": (
                "'No quiero depender de maquinas para vivir de forma permanente.' "
                "[Translation: I do not want to depend on machines to live permanently.] "
                "This is unambiguous. System returns 'clear'."
            ),
        },
    ],
}


# ── Build the demo OWL ─────────────────────────────────────────────────────────

def build():
    print("=" * 72)
    print("  ADO Demo OWL Builder")
    print("  Building 3-patient presentation ontology...")
    print("=" * 72)

    onto = load_ontology()

    patients = [
        ("Margaret Chen — 13 prefs, all domains, rich conditions", MARGARET_CHEN),
        ("James Okafor — 4 prefs, sparse but coherent", JAMES_OKAFOR),
        ("Elena Vasquez — 3 prefs, vague/cultural language", ELENA_VASQUEZ),
    ]

    for desc, pdata in patients:
        print(f"\n{'─' * 60}")
        print(f"  {desc}")
        print(f"{'─' * 60}")
        with contextlib.redirect_stdout(sys.stdout):
            populate_patient(onto, pdata)

    POPULATED_DIR.mkdir(exist_ok=True)
    out_path = POPULATED_DIR / "ado_demo_presentation.owl"
    onto.save(file=str(out_path.resolve()), format="rdfxml")

    # Count what was created
    all_individuals = list(onto.individuals())
    prefs = [i for i in all_individuals if "Pref_" in i.name]
    patients_created = [i for i in all_individuals if i.name.startswith("Patient_")]
    acs = [i for i in all_individuals if i.name.startswith("AC_")]
    classes = list(onto.classes())
    props = list(onto.properties())

    print(f"\n{'=' * 72}")
    print(f"  Built: {out_path}")
    print(f"{'=' * 72}")
    print(f"  Classes                : {len(classes)}")
    print(f"  Properties             : {len(props)}")
    print(f"  Patient individuals    : {len(patients_created)}")
    print(f"  Preference individuals : {len(prefs)}")
    print(f"  Activation conditions  : {len(acs)}")
    print(f"  Total individuals      : {len(all_individuals)}")
    print()
    print("  Protégé demo flow (≈90 seconds):")
    print("  ─────────────────────────────────────────────────────────")
    print("  1. File → Open → ado_demo_presentation.owl")
    print("  2. Classes tab → expand Intervention → show 5 branches, 21 leaves")
    print("  3. Reasoner → HermiT → Start → confirm 'Consistent' badge")
    print("  4. Individuals tab → Patient_margaret_chen")
    print("       → hasPreference → click Pref_margaret_chen_1 (NoCPR)")
    print("       → isNegated=true, hasPreferenceStrength=Absolute")
    print("       → hasActivationCondition → AC_Pref_margaret_chen_1")
    print("       → requiresFunctionalStatus=NYHA_IV, hasReversibleCause=false")
    print("  5. Switch to Patient_elena_vasquez → show VaguePreference type")
    print("       → originalText shows Spanish original with translation note")
    print("  ─────────────────────────────────────────────────────────")
    print()
    print("  Terminal demo (30 seconds, after Protégé):")
    print("  python evaluation/demo_query.py")
    print(f"{'=' * 72}")


if __name__ == "__main__":
    build()
