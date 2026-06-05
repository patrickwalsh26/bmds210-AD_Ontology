"""
Fifty realistic HF patient preference profiles for large-scale simulation.

Design principles:
  - verbatim_text mirrors how patients/families actually write directives
  - messy_level tags: clean | typical | minimal | incomplete_encoding |
      contradictory | outdated | culturally_complex
  - Many profiles intentionally expose system limits: missing activation fields,
    vague language, contradictions, conditions the ontology cannot represent,
    evolving preferences across visits, surrogates overriding patient language.

These profiles are intended to STRESS the system, not flatter it.
"""

from __future__ import annotations
import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _p(label, intervention, negated, strength, original, ptype="clear", ac=None):
    d = {"label": label, "intervention": intervention, "negated": negated,
         "strength": strength, "original_text": original, "type": ptype}
    if ac:
        d["activation_conditions"] = ac
    return d


PATIENT_COHORT = [

    # ── CLEAN (well-encoded, rich activation conditions) ──────────────────────
    {
        "patient_id": "P01_conditional_dnr",
        "patient_name": "Maria G., 71, NYHA IV HF conditional DNR",
        "messy_level": "clean",
        "template_source": "Stanford HF clinic AD addendum",
        "preferences": [
            _p("No CPR NYHA IV no reversible", "cpr", True, "Absolute",
               "If my heart stops and I am in NYHA Class IV heart failure with no reversible cause, do not attempt CPR.",
               "conditional", {"nyha_class": "IV", "conditions": ["cardiac_arrest"], "reversible_cause": False}),
            _p("Temp vent if reversible", "temporary_ventilation", False, "Conditional",
               "I would accept a breathing tube temporarily if doctors believe the cause is reversible.",
               "conditional", {"reversible_cause": True}),
            _p("No indefinite vent", "indefinite_ventilation", True, "Absolute",
               "I do not want to be kept alive indefinitely on a ventilator."),
            _p("ICD off in hospice", "icd_deactivation", False, "Strong",
               "If I enroll in hospice, I want my defibrillator turned off.",
               "conditional", {"care_context": "hospice"}),
            _p("No chronic dialysis", "chronic_dialysis", True, "Absolute",
               "I do not want maintenance dialysis."),
            _p("Withdraw pressors after 72h no improvement", "vasopressor_withdrawal", False, "Strong",
               "If I am on vasopressors with no improvement after 72 hours, withdraw them.",
               "conditional", {"conditions": ["cardiogenic_shock"], "time_bound_hours": 72}),
            _p("Acute dialysis if cardiorenal reversible", "acute_dialysis", False, "Conditional",
               "Short-term dialysis is acceptable if my kidney failure is related to my heart and expected to recover.",
               "conditional", {"conditions": ["cardiorenal_syndrome"], "reversible_cause": True}),
        ],
    },
    {
        "patient_id": "P02_full_treatment",
        "patient_name": "Robert T., 58, VA full aggressive care",
        "messy_level": "clean",
        "template_source": "VA Form 10-0137",
        "preferences": [
            _p("CPR yes", "cpr", False, "Strong", "I want all life-sustaining measures including CPR."),
            _p("Intubation yes", "intubation", False, "Strong", "Use a breathing machine if needed."),
            _p("Pressors yes", "vasopressor_escalation", False, "Strong", "Escalate medications to support my blood pressure."),
            _p("Inotropes yes", "inotrope_escalation", False, "Strong", "Do not limit my drips."),
            _p("Dialysis yes", "acute_dialysis", False, "Strong", "Dialysis if my kidneys need it."),
        ],
    },
    {
        "patient_id": "P03_dni_biPAP_cpr",
        "patient_name": "Sandra W., 64, DNI but wants CPR and BiPAP",
        "messy_level": "clean",
        "template_source": "Clinical DNI + CPR note",
        "preferences": [
            _p("No intubation ever", "intubation", True, "Absolute",
               "I never want a tube placed down my throat under any circumstances."),
            _p("No indefinite vent", "indefinite_ventilation", True, "Absolute",
               "No long-term ventilator."),
            _p("BiPAP acceptable", "non_invasive_ventilation", False, "Strong",
               "BiPAP or CPAP through a mask is acceptable."),
            _p("CPR yes", "cpr", False, "Strong",
               "If my heart stops, I want chest compressions attempted once."),
        ],
    },
    {
        "patient_id": "P04_hospice_device_plan",
        "patient_name": "Eugene F., 79, LVAD + hospice plan",
        "messy_level": "clean",
        "template_source": "VAD coordinator and palliative addendum",
        "preferences": [
            _p("ICD off hospice", "icd_deactivation", False, "Strong",
               "When I transition to hospice, deactivate the ICD.",
               "conditional", {"care_context": "hospice"}),
            _p("LVAD continue unless comfort only", "lvad_withdrawal", True, "Conditional",
               "Keep the LVAD running unless we have agreed on comfort care only.",
               "conditional", {"care_context": "hospice"}),
            _p("No CPR terminal", "cpr", True, "Absolute",
               "No CPR once I am on comfort-focused care."),
            _p("BiPAP OK for comfort", "non_invasive_ventilation", False, "Weak",
               "BiPAP is acceptable if it helps my breathing comfort, not to extend life."),
        ],
    },
    {
        "patient_id": "P05_time_trial_pressors",
        "patient_name": "Dorothy K., 66, explicit time-limited pressor trial",
        "messy_level": "clean",
        "template_source": "ICU shared decision note",
        "preferences": [
            _p("96h pressor trial then withdraw", "vasopressor_withdrawal", False, "Strong",
               "I agree to a 96-hour trial of vasopressors. If there is no meaningful improvement, withdraw them.",
               "conditional", {"conditions": ["cardiogenic_shock"], "time_bound_hours": 96}),
            _p("No indefinite vent", "indefinite_ventilation", True, "Absolute",
               "If I am not improving on the ventilator after two weeks, I do not want to remain on it."),
            _p("ICD shocks OK acute", "icd_shock_therapy", False, "Conditional",
               "ICD shocks are acceptable during an acute arrhythmia."),
            _p("No CPR if NYHA IV irreversible", "cpr", True, "Absolute",
               "No CPR if I am in end-stage heart failure with no reversible cause.",
               "conditional", {"nyha_class": "IV", "reversible_cause": False}),
        ],
    },

    # ── TYPICAL (standard templates, some gaps, some vague) ───────────────────
    {
        "patient_id": "P06_texas_dnr",
        "patient_name": "James H., 82, Texas OOH-DNR",
        "messy_level": "typical",
        "template_source": "Texas Out-of-Hospital DNR",
        "preferences": [
            _p("No CPR", "cpr", True, "Absolute", "Do not attempt resuscitation."),
            _p("No defibrillation", "defibrillation", True, "Absolute", "No defibrillation."),
            _p("No artificial ventilation", "mechanical_ventilation", True, "Absolute",
               "No artificial ventilation of any kind."),
        ],
    },
    {
        "patient_id": "P07_ca_ahcd",
        "patient_name": "Linda P., 74, California AHCD standard form",
        "messy_level": "typical",
        "template_source": "CA AHCD statutory form",
        "preferences": [
            _p("No CPR terminal", "cpr", True, "Absolute",
               "If I have a terminal condition, I do not want CPR.",
               "conditional", {"conditions": ["terminal_condition"]}),
            _p("No vent terminal", "mechanical_ventilation", True, "Absolute",
               "If I have a terminal condition, I do not want artificial ventilation.",
               "conditional", {"conditions": ["terminal_condition"]}),
            _p("No dialysis terminal", "acute_dialysis", True, "Absolute",
               "If I have a terminal condition, I do not want dialysis.",
               "conditional", {"conditions": ["terminal_condition"]}),
        ],
    },
    {
        "patient_id": "P08_five_wishes_comfort",
        "patient_name": "Patricia R., 77, Five Wishes comfort focus",
        "messy_level": "typical",
        "template_source": "Five Wishes",
        "preferences": [
            _p("No heroic measures dying", "cpr", True, "Weak",
               "I do not want heroic measures or to be kept alive by machines if I am dying.",
               "vague"),
            _p("Comfort if dying", "inotrope_escalation", True, "Weak",
               "Focus on my comfort even if this means I will not live as long.",
               "vague"),
            _p("BiPAP for comfort OK", "non_invasive_ventilation", False, "Weak",
               "A mask to help me breathe more easily is OK if it makes me more comfortable.",
               "vague"),
        ],
    },
    {
        "patient_id": "P09_dementia_directive",
        "patient_name": "Franklin O., 83, dementia-specific AD",
        "messy_level": "typical",
        "template_source": "Dementia-specific advance directive template",
        "preferences": [
            _p("No CPR advanced dementia", "cpr", True, "Absolute",
               "When I have advanced dementia and cannot recognize my family, do not attempt CPR.",
               "conditional", {"conditions": ["terminal_condition"]}),
            _p("No intubation advanced dementia", "intubation", True, "Absolute",
               "When I have advanced dementia, do not place a breathing tube.",
               "conditional", {"conditions": ["terminal_condition"]}),
            _p("No dialysis dementia", "acute_dialysis", True, "Absolute",
               "In advanced dementia, no dialysis.",
               "conditional", {"conditions": ["terminal_condition"]}),
            _p("No escalation dementia", "vasopressor_escalation", True, "Absolute",
               "In advanced dementia, do not escalate medications to support my blood pressure.",
               "conditional", {"conditions": ["terminal_condition"]}),
        ],
    },
    {
        "patient_id": "P10_nhs_wales_adrt",
        "patient_name": "Gwyneth C., 69, NHS Wales ADRT — condition met",
        "messy_level": "typical",
        "template_source": "NHS Wales ADRT",
        "preferences": [
            _p("No CPR permanent unconsciousness", "cpr", True, "Absolute",
               "If I become permanently unconscious with no reasonable prospect of recovery, do not attempt CPR.",
               "conditional", {"conditions": ["permanent_unconsciousness"]}),
            _p("No vent permanent unconsciousness", "mechanical_ventilation", True, "Absolute",
               "If permanently unconscious, do not provide artificial ventilation.",
               "conditional", {"conditions": ["permanent_unconsciousness"]}),
            _p("No dialysis permanent unconsciousness", "acute_dialysis", True, "Absolute",
               "If permanently unconscious, no dialysis.",
               "conditional", {"conditions": ["permanent_unconsciousness"]}),
        ],
    },
    {
        "patient_id": "P11_ncbc_full_care",
        "patient_name": "Theresa M., 71, NCBC faith-based full treatment",
        "messy_level": "typical",
        "template_source": "National Catholic Bioethics Center directive",
        "preferences": [
            _p("Wants CPR ordinary care", "cpr", False, "Strong",
               "I wish to receive all obligatory ordinary care that my faith and reason prescribe."),
            _p("Wants intubation ordinary care", "intubation", False, "Strong",
               "Provide ordinary means including respiratory support if there is a reasonable hope of benefit."),
            _p("Wants dialysis if beneficial", "acute_dialysis", False, "Strong",
               "Provide dialysis as ordinary care if reasonably expected to provide benefit."),
        ],
    },
    {
        "patient_id": "P12_dialysis_split",
        "patient_name": "Henry B., 73, acute OK / chronic no",
        "messy_level": "typical",
        "template_source": "Nephrology clinic note + AD",
        "preferences": [
            _p("Acute dialysis cardiorenal", "acute_dialysis", False, "Conditional",
               "Short-term dialysis is OK if my kidneys might recover.",
               "conditional", {"reversible_cause": True}),
            _p("No chronic dialysis ever", "chronic_dialysis", True, "Absolute",
               "I will not accept long-term maintenance dialysis under any circumstances."),
        ],
    },
    {
        "patient_id": "P13_floor_dne",
        "patient_name": "Constance J., 68, floor do-not-escalate",
        "messy_level": "typical",
        "template_source": "HF cardiology note",
        "preferences": [
            _p("No ICU transfer", "vasopressor_escalation", True, "Absolute",
               "Do not transfer me to the ICU or start vasopressors."),
            _p("No drip escalation", "inotrope_escalation", True, "Absolute",
               "Do not escalate my IV medications to ICU-level doses."),
            _p("Temp vent floor only", "temporary_ventilation", False, "Strong",
               "A short trial of breathing support on the medical floor is acceptable."),
            _p("CPR once", "cpr", False, "Weak",
               "Attempt CPR once if it is immediately reversible, but do not transfer to ICU."),
        ],
    },
    {
        "patient_id": "P14_biPAP_no_tube",
        "patient_name": "Arthur S., 70, NIV yes / intubation no",
        "messy_level": "typical",
        "template_source": "Pulmonology + cardiology combined note",
        "preferences": [
            _p("BiPAP acceptable", "non_invasive_ventilation", False, "Strong",
               "I am willing to try BiPAP."),
            _p("No intubation ever", "intubation", True, "Absolute",
               "I never want a tube placed down my throat, under any circumstances."),
            _p("No indefinite vent", "indefinite_ventilation", True, "Absolute",
               "No long-term ventilator."),
            _p("CPR yes", "cpr", False, "Strong",
               "Attempt CPR if my heart stops."),
        ],
    },

    # ── MINIMAL (sparse documentation, one or two vague lines) ────────────────
    {
        "patient_id": "P15_handwritten_note",
        "patient_name": "Wilma T., 88, handwritten two-word note",
        "messy_level": "minimal",
        "template_source": "Handwritten note in chart",
        "encoding_note": "Literally 'no machines' — maximally ambiguous",
        "preferences": [
            _p("No machines", "mechanical_ventilation", True, "Weak",
               "No machines.", "vague"),
        ],
    },
    {
        "patient_id": "P16_comfort_only_verbal",
        "patient_name": "Edward N., 91, family reported 'comfort only'",
        "messy_level": "minimal",
        "template_source": "Verbal report documented by nurse",
        "encoding_note": "No formal directive. Family reported preference verbally.",
        "preferences": [
            _p("Comfort only family reported", "cpr", True, "Weak",
               "Comfort measures only. Family states patient would not want aggressive care.",
               "vague"),
        ],
    },
    {
        "patient_id": "P17_checkbox_dnar",
        "patient_name": "Shirley M., 84, DNAR checkbox only",
        "messy_level": "minimal",
        "template_source": "POLST Section A checkbox",
        "encoding_note": "POLST Section A checked DNAR. No other sections filled.",
        "preferences": [
            _p("DNAR", "cpr", True, "Absolute", "DNAR.", "clear"),
        ],
    },
    {
        "patient_id": "P18_no_heroic_blank",
        "patient_name": "Clarence O., 80, 'no heroic measures' with nothing else",
        "messy_level": "minimal",
        "template_source": "Hospital admission form free text",
        "preferences": [
            _p("No heroic measures", "cpr", True, "Weak",
               "No heroic measures.", "vague"),
            _p("No heroic vent", "mechanical_ventilation", True, "Weak",
               "No heroic measures.", "vague"),
        ],
    },
    {
        "patient_id": "P19_single_clause_vent",
        "patient_name": "Bertha L., 76, only ventilator documented",
        "messy_level": "minimal",
        "template_source": "Discharge summary note",
        "encoding_note": "Only ventilation addressed. CPR, devices not mentioned.",
        "preferences": [
            _p("No vent", "mechanical_ventilation", True, "Absolute",
               "Patient stated she does not want to be put on a breathing machine."),
        ],
    },
    {
        "patient_id": "P20_no_directive_any",
        "patient_name": "Oscar V., 62, no advance directive at all",
        "messy_level": "minimal",
        "template_source": "No AD documented",
        "encoding_note": "No preferences documented. System must return no_coverage for all interventions.",
        "preferences": [],
    },

    # ── INCOMPLETE ENCODING (conditions were dropped during chart abstraction) ─
    {
        "patient_id": "P21_lvad_qualifier_dropped",
        "patient_name": "Nathan P., 61, LVAD qualifier lost in encoding",
        "messy_level": "incomplete_encoding",
        "template_source": "HF escalation note",
        "encoding_note": "Original said 'only if LVAD or transplant plan exists' — condition not encoded.",
        "preferences": [
            _p("Inotropes cardiogenic shock only", "inotrope_escalation", False, "Conditional",
               "Escalate inotropes only if there is a plan for LVAD or transplant evaluation.",
               "conditional", {"conditions": ["cardiogenic_shock"]}),
            # LVAD/transplant plan qualifier deliberately dropped from activation_conditions
        ],
    },
    {
        "patient_id": "P22_nyha_class_dropped",
        "patient_name": "Dolores R., 78, NYHA condition dropped from CPR clause",
        "messy_level": "incomplete_encoding",
        "template_source": "HF clinic note",
        "encoding_note": "Original said 'no CPR if NYHA IV' — NYHA class dropped during encoding.",
        "preferences": [
            _p("No CPR no reversible cause", "cpr", True, "Absolute",
               "Do not attempt CPR if there is no reversible cause.",
               "conditional", {"reversible_cause": False}),
            # NYHA class condition deliberately dropped
        ],
    },
    {
        "patient_id": "P23_time_bound_lost",
        "patient_name": "Gregory W., 67, time bound lost in abstraction",
        "messy_level": "incomplete_encoding",
        "template_source": "ICU goals-of-care note",
        "encoding_note": "Original said 'after 48 hours' — time bound not encoded.",
        "preferences": [
            _p("Withdraw pressors no improvement", "vasopressor_withdrawal", False, "Conditional",
               "If I am on vasopressors with no meaningful improvement, withdraw them.",
               "conditional", {"conditions": ["cardiogenic_shock"]}),
            # time_bound_hours deliberately dropped
        ],
    },
    {
        "patient_id": "P24_hospice_context_dropped",
        "patient_name": "Mabel S., 82, care context dropped from ICD clause",
        "messy_level": "incomplete_encoding",
        "template_source": "Device management addendum",
        "encoding_note": "Original restricted ICD deactivation to hospice — context not encoded.",
        "preferences": [
            _p("ICD deactivation", "icd_deactivation", False, "Strong",
               "I would like my defibrillator turned off when the time comes.",
               "clear"),  # care_context condition dropped → fires everywhere
        ],
    },
    {
        "patient_id": "P25_reversible_cause_dropped_vent",
        "patient_name": "Albert C., 73, reversibility condition dropped from vent clause",
        "messy_level": "incomplete_encoding",
        "template_source": "Medical floor note",
        "encoding_note": "Patient said 'temporary vent if reversible' — reversible_cause not encoded.",
        "preferences": [
            _p("Accept temporary vent", "temporary_ventilation", False, "Conditional",
               "I would accept temporary intubation if it might help me recover.",
               "conditional", {"conditions": ["respiratory_failure"]}),
            # reversible_cause condition deliberately dropped → fires for reversible AND non-reversible
        ],
    },
    {
        "patient_id": "P26_condition_type_wrong",
        "patient_name": "Louise D., 69, clinical condition encoded too broadly",
        "messy_level": "incomplete_encoding",
        "template_source": "Outpatient clinic note",
        "encoding_note": "Patient said 'cardiorenal syndrome' but encoded as generic reversible_cause=True.",
        "preferences": [
            _p("Dialysis if reversible", "acute_dialysis", False, "Conditional",
               "Short-term dialysis is acceptable if the kidney failure might be reversible.",
               "conditional", {"reversible_cause": True}),
            # conditions: cardiorenal_syndrome dropped — now fires for ANY reversible AKI
        ],
    },
    {
        "patient_id": "P27_strength_downgraded",
        "patient_name": "Herman L., 75, absolute refusal encoded as weak",
        "messy_level": "incomplete_encoding",
        "template_source": "Living will transcription error",
        "encoding_note": "Patient wrote 'under no circumstances' but encoded as Weak preference.",
        "preferences": [
            _p("No chronic dialysis weak encoding", "chronic_dialysis", True, "Weak",
               "Under no circumstances do I want long-term dialysis.",
               "clear"),  # strength should be Absolute — encoding error
        ],
    },

    # ── CONTRADICTORY (conflicting preferences from different encounters) ──────
    {
        "patient_id": "P28_changed_mind_cpr",
        "patient_name": "Florence A., 72, changed CPR preference across two visits",
        "messy_level": "contradictory",
        "template_source": "Two hospital admissions 18 months apart",
        "encoding_note": "Both preferences encoded. System must use most recent or return contradiction.",
        "preferences": [
            _p("Old: wants CPR", "cpr", False, "Strong",
               "Patient stated at 2024 admission: Do everything, I'm not ready to give up."),
            _p("New: no CPR", "cpr", True, "Absolute",
               "Patient stated at 2025 admission: I've thought about it and no CPR. I've made peace.",
               "conditional", {"conditions": ["advanced_heart_failure"]}),
        ],
    },
    {
        "patient_id": "P29_family_vs_patient",
        "patient_name": "Victor M., 80, family meeting conflated with patient directive",
        "messy_level": "contradictory",
        "template_source": "Family meeting summary + prior living will",
        "encoding_note": "Family said 'do everything' at meeting. Patient's prior directive says DNR. Both in chart.",
        "preferences": [
            _p("Living will: no CPR end-stage HF", "cpr", True, "Absolute",
               "From living will (2020): No CPR if end-stage heart failure.",
               "conditional", {"conditions": ["advanced_heart_failure"]}),
            _p("Family meeting: full code", "cpr", False, "Strong",
               "Family meeting note (2025): Family requests full resuscitation."),
        ],
    },
    {
        "patient_id": "P30_contradictory_vent",
        "patient_name": "Rosemary F., 66, vent preference changes by clause",
        "messy_level": "contradictory",
        "template_source": "Same document, internal inconsistency",
        "encoding_note": "Patient accepts 'short trial' in one sentence, 'no machines' in next paragraph.",
        "preferences": [
            _p("Temp vent OK short trial", "temporary_ventilation", False, "Conditional",
               "A short trial on a breathing machine is acceptable if there is hope of recovery.",
               "conditional", {"reversible_cause": True}),
            _p("No machines", "mechanical_ventilation", True, "Absolute",
               "I do not want to be kept alive on machines.", "vague"),
        ],
    },
    {
        "patient_id": "P31_double_icd_contradictory",
        "patient_name": "Calvin B., 77, ICD preferences contradictory",
        "messy_level": "contradictory",
        "template_source": "Two different providers documented ICD preferences",
        "encoding_note": "EP cardiologist note says leave ICD on. Palliative note says deactivate in hospice.",
        "preferences": [
            _p("Keep ICD on", "icd_deactivation", True, "Strong",
               "Electrophysiology note: patient wants ICD to remain active for anti-tachycardia pacing."),
            _p("ICD off in hospice", "icd_deactivation", False, "Strong",
               "Palliative care note: patient wants ICD off when in hospice.",
               "conditional", {"care_context": "hospice"}),
        ],
    },
    {
        "patient_id": "P32_dialysis_conflict_reversible",
        "patient_name": "Harriet G., 74, dialysis preference internally inconsistent",
        "messy_level": "contradictory",
        "template_source": "Nephrology + primary care combined",
        "encoding_note": "Nephrologist documented 'no dialysis ever'; primary care noted 'acute OK'.",
        "preferences": [
            _p("Primary care: acute dialysis OK", "acute_dialysis", False, "Conditional",
               "Primary care note: Patient agreed to short-term dialysis if kidneys might recover.",
               "conditional", {"reversible_cause": True}),
            _p("Nephrology: no dialysis absolute", "acute_dialysis", True, "Absolute",
               "Nephrology note: Patient explicitly refused dialysis of any kind."),
        ],
    },
    {
        "patient_id": "P33_full_code_comfort_same_doc",
        "patient_name": "Alvin T., 69, full code and comfort goal in same note",
        "messy_level": "contradictory",
        "template_source": "Goals of care note — internal contradiction",
        "encoding_note": "'Full code' checked on admission. Same note says 'comfort-focused goals'.",
        "preferences": [
            _p("Full code admission order", "cpr", False, "Absolute",
               "Code status: Full code."),
            _p("Comfort-focused goals", "inotrope_escalation", True, "Strong",
               "Patient and family goals are comfort-focused. Minimize invasive interventions.", "vague"),
        ],
    },
    {
        "patient_id": "P34_pressors_vs_withdrawal_conflict",
        "patient_name": "Norma J., 71, pressor conflict: escalate vs withdraw",
        "messy_level": "contradictory",
        "template_source": "Two ICU notes, 3 days apart",
        "encoding_note": "Day 1 ICU note: escalate. Day 3 family meeting: withdraw if no improvement.",
        "preferences": [
            _p("Day 1: escalate pressors", "vasopressor_escalation", False, "Strong",
               "ICU note day 1: Patient and family agree to full hemodynamic support."),
            _p("Day 3: withdraw after 72h", "vasopressor_withdrawal", False, "Strong",
               "Family meeting day 3: Withdraw pressors if no improvement in 72 hours.",
               "conditional", {"conditions": ["cardiogenic_shock"], "time_bound_hours": 72}),
        ],
    },

    # ── OUTDATED (directive written years ago; clinical state has changed) ──────
    {
        "patient_id": "P35_pre_lvad_directive",
        "patient_name": "Stewart H., 59, directive written before LVAD implant",
        "messy_level": "outdated",
        "template_source": "Living will from 2019, LVAD implanted 2023",
        "encoding_note": "Directive makes no mention of LVAD. Device management section entirely absent.",
        "preferences": [
            _p("Old directive: no CPR terminal", "cpr", True, "Absolute",
               "If I have a terminal condition, do not attempt CPR.",
               "conditional", {"conditions": ["terminal_condition"]}),
            _p("Old directive: no vent terminal", "mechanical_ventilation", True, "Absolute",
               "If I have a terminal condition, do not put me on a ventilator.",
               "conditional", {"conditions": ["terminal_condition"]}),
            # LVAD deactivation not addressed — system must return no_coverage
        ],
    },
    {
        "patient_id": "P36_nyha_reclassified",
        "patient_name": "Pauline K., 68, conditional DNR written when NYHA II, now NYHA IV",
        "messy_level": "outdated",
        "template_source": "HF clinic 2021, now NYHA IV in 2025",
        "encoding_note": "Preference was conditional on NYHA IV at time of writing — now always met. "
                         "But the preference was encoded with NYHA IV condition still explicit.",
        "preferences": [
            _p("No CPR NYHA IV no reversible", "cpr", True, "Absolute",
               "If I am in NYHA Class IV and there is no reversible cause, do not attempt CPR.",
               "conditional", {"nyha_class": "IV", "reversible_cause": False}),
        ],
    },
    {
        "patient_id": "P37_outdated_full_code",
        "patient_name": "George M., 77, full code from 10 years ago never updated",
        "messy_level": "outdated",
        "template_source": "Hospital admission 2015 — never revised",
        "encoding_note": "Patient is now NYHA IV, multiple hospitalizations. Full code stands legally.",
        "preferences": [
            _p("Full code 2015", "cpr", False, "Strong",
               "Full code status as documented on hospital admission. No advance directive on file."),
            _p("Full vent 2015", "intubation", False, "Strong",
               "Patient agreed to all life-sustaining measures on admission."),
        ],
    },
    {
        "patient_id": "P38_terminal_cond_resolved",
        "patient_name": "Vivian O., 65, terminal condition condition now resolved",
        "messy_level": "outdated",
        "template_source": "CA AHCD from cancer diagnosis era — cancer now in remission",
        "encoding_note": "All preferences conditioned on terminal condition. Patient is no longer terminal "
                         "— conditions will fail for most scenarios.",
        "preferences": [
            _p("No CPR if terminal", "cpr", True, "Absolute",
               "If I have a terminal condition, do not resuscitate.",
               "conditional", {"conditions": ["terminal_condition"]}),
            _p("No vent if terminal", "mechanical_ventilation", True, "Absolute",
               "If I have a terminal condition, no breathing machine.",
               "conditional", {"conditions": ["terminal_condition"]}),
            _p("Dialysis OK if non-terminal", "acute_dialysis", False, "Strong",
               "Short-term dialysis is acceptable if I am not terminally ill."),
        ],
    },

    # ── CULTURALLY COMPLEX (religious, linguistic, or proxy-centric directives) ─
    {
        "patient_id": "P39_jehovahs_witness",
        "patient_name": "Rebecca L., 62, Jehovah's Witness — no blood products constraint",
        "messy_level": "culturally_complex",
        "template_source": "Patient-authored statement + hospital blood refusal card",
        "encoding_note": "Blood product refusal is out-of-scope for ADO. CPR without blood products "
                         "is a nuanced preference the ontology cannot represent.",
        "preferences": [
            _p("CPR yes but no blood", "cpr", False, "Conditional",
               "CPR is acceptable but do not administer blood products or transfusions during or after.",
               "vague"),  # blood products constraint is not encodable
            _p("No intubation if brain damage expected", "intubation", True, "Conditional",
               "Do not intubate if doctors believe I will not recover meaningful brain function.",
               "conditional", {"reversible_cause": False}),
        ],
    },
    {
        "patient_id": "P40_family_authority",
        "patient_name": "Yun C., 73, family decision-maker cultural deference",
        "messy_level": "culturally_complex",
        "template_source": "Translated summary from family meeting",
        "encoding_note": "Patient explicitly deferred to eldest son for all decisions. "
                         "Surrogate-override axis not modeled in ADO — key identified gap.",
        "preferences": [
            _p("Patient defers to family", "cpr", False, "Weak",
               "My family will make the right decision for me. I trust my son to decide.",
               "vague"),
            _p("Comfort preferred verbally", "mechanical_ventilation", True, "Weak",
               "Patient indicated through interpreter that machines to prolong dying are not desired.",
               "vague"),
        ],
    },
    {
        "patient_id": "P41_religious_ordinary_extraordinary",
        "patient_name": "Father D., 78, Catholic ordinary/extraordinary distinction",
        "messy_level": "culturally_complex",
        "template_source": "NCBC directive + pastoral care addendum",
        "encoding_note": "Extraordinary means refusal is semantically loaded — not a formal boolean. "
                         "ADO encodes the intervention-level preferences but loses the theological framework.",
        "preferences": [
            _p("Ordinary care yes", "cpr", False, "Strong",
               "I wish to receive all ordinary care. Resuscitation is ordinary care if beneficial."),
            _p("No extraordinary means", "indefinite_ventilation", True, "Conditional",
               "I refuse extraordinary means that offer no reasonable hope of benefit, "
               "including indefinite mechanical ventilation.", "vague"),
            _p("Nutrition ordinary", "acute_dialysis", False, "Weak",
               "Dialysis as ordinary care is acceptable if there is a reasonable hope of benefit.", "vague"),
        ],
    },
    {
        "patient_id": "P42_spanish_translated",
        "patient_name": "Carmen R., 81, Spanish directive — translation uncertainty",
        "messy_level": "culturally_complex",
        "template_source": "Translated from Spanish by family member — not certified",
        "encoding_note": "Translation from 'no quiero máquinas' is approximate — "
                         "scope unclear (ventilators only? all devices?). Encoded conservatively.",
        "preferences": [
            _p("No ventilation translated", "mechanical_ventilation", True, "Weak",
               "No quiero máquinas. [Translated: I do not want machines.] Scope uncertain.", "vague"),
            _p("No CPR translated", "cpr", True, "Weak",
               "Family reports patient does not want to be brought back. "
               "Cannot confirm scope from document.", "vague"),
        ],
    },

    # ── COMPLEX CLINICAL COMBINATIONS (multi-condition, real clinical edge cases) ─
    {
        "patient_id": "P43_pe_cardiac_arrest",
        "patient_name": "Kenneth A., 57, PE-triggered cardiac arrest — reversible",
        "messy_level": "clean",
        "template_source": "HF + pulmonary clinic combined AD",
        "encoding_note": "Patient has conditional DNR for irreversible HF arrest but explicitly "
                         "wants full code for PE — reversible_cause is the key discriminator.",
        "preferences": [
            _p("No CPR irreversible HF arrest", "cpr", True, "Absolute",
               "If my heart stops from end-stage heart failure with no reversible cause, no CPR.",
               "conditional", {"nyha_class": "IV", "reversible_cause": False}),
            _p("CPR for reversible causes", "cpr", False, "Strong",
               "If my heart stops from a reversible cause like a blood clot or electrolyte problem, attempt CPR.",
               "conditional", {"reversible_cause": True}),
            _p("Temp vent if reversible", "temporary_ventilation", False, "Conditional",
               "Temporary breathing support is acceptable for a reversible cause.",
               "conditional", {"reversible_cause": True}),
        ],
    },
    {
        "patient_id": "P44_vt_storm_icd",
        "patient_name": "Michelle V., 63, VT storm — explicit ICD shock preference",
        "messy_level": "clean",
        "template_source": "EP cardiology note",
        "preferences": [
            _p("ICD shocks OK for VT", "icd_shock_therapy", False, "Strong",
               "I want my ICD to deliver shocks during life-threatening arrhythmias."),
            _p("ICD deactivation if comfort care", "icd_deactivation", False, "Strong",
               "If we transition to comfort care, deactivate the ICD.",
               "conditional", {"care_context": "hospice"}),
            _p("No CPR in comfort care", "cpr", True, "Absolute",
               "No CPR once on comfort-focused care."),
            _p("Pacing transcutaneous OK acute", "transcutaneous_pacing", False, "Conditional",
               "External pacing during an acute reversible arrhythmia is acceptable.",
               "conditional", {"reversible_cause": True}),
        ],
    },
    {
        "patient_id": "P45_multiorgan_failure",
        "patient_name": "Ralph T., 74, multi-organ failure — no single directive covers it",
        "messy_level": "incomplete_encoding",
        "template_source": "Standard living will — written before multi-organ failure trajectory known",
        "encoding_note": "Patient's directive addresses ventilation and CPR but not dialysis, "
                         "pressors, or inotropes — common real-world gap.",
        "preferences": [
            _p("No indefinite vent", "indefinite_ventilation", True, "Absolute",
               "Do not keep me on a ventilator indefinitely."),
            _p("No CPR terminal", "cpr", True, "Absolute",
               "If I have a terminal condition, no CPR.",
               "conditional", {"conditions": ["terminal_condition"]}),
            # dialysis, pressors, inotropes: no_coverage
        ],
    },
    {
        "patient_id": "P46_lvad_deact_decision",
        "patient_name": "Irene P., 66, explicit LVAD deactivation preference",
        "messy_level": "clean",
        "template_source": "VAD coordinator + palliative combined note",
        "preferences": [
            _p("LVAD continue unless comfort agreed", "lvad_withdrawal", True, "Conditional",
               "Keep the LVAD running unless I and my team have agreed to transition to comfort care.",
               "conditional", {"care_context": "hospice"}),
            _p("LVAD off in comfort care", "lvad_withdrawal", False, "Strong",
               "If we agree on comfort-focused care, the LVAD may be deactivated.",
               "conditional", {"care_context": "hospice"}),
            _p("No defibrillation in comfort care", "defibrillation", True, "Strong",
               "No defibrillation or external shocks once comfort care agreed.",
               "conditional", {"care_context": "hospice"}),
        ],
    },
    {
        "patient_id": "P47_transplant_bridge_preference",
        "patient_name": "Brian O., 52, bridge-to-transplant — full support expected",
        "messy_level": "clean",
        "template_source": "Transplant team AD",
        "encoding_note": "Patient explicitly wants full support during bridge to transplant; "
                         "preferences change if no longer transplant candidate.",
        "preferences": [
            _p("Full support if transplant candidate", "cpr", False, "Strong",
               "While I am being evaluated for transplant, I want full resuscitation."),
            _p("Full vent if transplant candidate", "intubation", False, "Strong",
               "While on the transplant list, use a ventilator if needed."),
            _p("Withdraw if no longer candidate", "vasopressor_withdrawal", False, "Strong",
               "If I am removed from the transplant list, withdraw vasopressors.",
               "conditional", {"conditions": ["cardiogenic_shock"]}),
        ],
    },
    {
        "patient_id": "P48_septic_shock_hf",
        "patient_name": "Darlene F., 69, septic shock + HF — complex scenario",
        "messy_level": "typical",
        "template_source": "General living will",
        "encoding_note": "Directive doesn't distinguish septic shock from cardiogenic shock. "
                         "Conditions in system are HF-specific.",
        "preferences": [
            _p("No CPR if terminal", "cpr", True, "Absolute",
               "If I have a terminal condition or am actively dying, do not attempt CPR.",
               "conditional", {"conditions": ["terminal_condition"]}),
            _p("Pressors acceptable if reversible", "vasopressor_escalation", False, "Conditional",
               "Vasopressors are acceptable if the condition may be reversible.",
               "conditional", {"reversible_cause": True}),
            _p("BiPAP acceptable", "non_invasive_ventilation", False, "Strong",
               "I will accept non-invasive breathing support."),
        ],
    },
    {
        "patient_id": "P49_young_hf_explicit",
        "patient_name": "Marcus W., 38, young HF patient — highly explicit directive",
        "messy_level": "clean",
        "template_source": "Self-authored detailed directive reviewed by cardiologist",
        "preferences": [
            _p("CPR for reversible only", "cpr", False, "Conditional",
               "Attempt CPR only if there is a potentially reversible cause. "
               "Do not attempt CPR for end-stage cardiomyopathy.",
               "conditional", {"reversible_cause": True}),
            _p("No CPR irreversible", "cpr", True, "Absolute",
               "Do not attempt CPR if the cause is irreversible end-stage disease.",
               "conditional", {"reversible_cause": False}),
            _p("Temp vent reversible", "temporary_ventilation", False, "Strong",
               "Temporary mechanical ventilation is acceptable for reversible causes.",
               "conditional", {"reversible_cause": True}),
            _p("No indefinite vent", "indefinite_ventilation", True, "Absolute",
               "I do not want to be maintained indefinitely on a ventilator."),
            _p("ICD shock therapy OK", "icd_shock_therapy", False, "Strong",
               "My ICD should be allowed to function normally including delivering shocks."),
            _p("ICD deactivation comfort care only", "icd_deactivation", False, "Conditional",
               "Deactivate ICD only when we have transitioned to comfort care.",
               "conditional", {"care_context": "hospice"}),
            _p("No chronic dialysis", "chronic_dialysis", True, "Absolute",
               "I will not accept long-term maintenance dialysis."),
            _p("Acute dialysis if reversible", "acute_dialysis", False, "Conditional",
               "Short-term dialysis is acceptable if it may help me recover.",
               "conditional", {"reversible_cause": True}),
            _p("Inotropes for cardiogenic shock trial", "inotrope_escalation", False, "Conditional",
               "Inotrope escalation is acceptable for cardiogenic shock as a bridge to recovery or decision.",
               "conditional", {"conditions": ["cardiogenic_shock"]}),
            _p("Withdraw pressors after 96h no improvement", "vasopressor_withdrawal", False, "Strong",
               "Withdraw vasopressors if there is no meaningful improvement after 96 hours.",
               "conditional", {"conditions": ["cardiogenic_shock"], "time_bound_hours": 96}),
        ],
    },
    {
        "patient_id": "P50_psychiatric_recanted",
        "patient_name": "Annette D., 55, prior directive recanted during psychiatric episode",
        "messy_level": "contradictory",
        "template_source": "Original living will vs. hospital admission note during psychiatric hospitalization",
        "encoding_note": "Patient signed DNR during inpatient psychiatric stay. Capacity questionable at time. "
                         "Living will from 2022 says full code. Both in chart. Legally unresolved.",
        "preferences": [
            _p("2022 living will: full code", "cpr", False, "Strong",
               "Living will 2022: I want full resuscitation including CPR."),
            _p("2024 psych admission: DNAR", "cpr", True, "Absolute",
               "DNAR signed during psychiatric admission 2024. Capacity assessment: limited."),
            _p("2022 living will: intubation yes", "intubation", False, "Strong",
               "Living will 2022: I want a breathing machine if needed."),
        ],
    },
]
