"""
Twenty realistic HF patient preference profiles for large-scale simulation.

Each profile includes verbatim-flavored original_text, template provenance, and a
messy_level tag (clean | typical | incomplete_encoding | contradictory | minimal).
"""


def _p(label, intervention, negated, strength, original, ptype="clear", ac=None):
    d = {"label": label, "intervention": intervention, "negated": negated,
         "strength": strength, "original_text": original, "type": ptype}
    if ac:
        d["activation_conditions"] = ac
    return d


PATIENT_COHORT = [
    {
        "patient_id": "cohort_01_jane",
        "patient_name": "Jane Doe (living will, HF)",
        "messy_level": "clean",
        "template_source": "Composite living will + HF clinic",
        "preferences": [
            _p("No CPR NYHA IV", "cpr", True, "Absolute",
               "If my heart stops and I am in NYHA Class IV with no reversible cause, do not attempt CPR.",
               "conditional", {"nyha_class": "IV", "conditions": ["cardiac_arrest"], "reversible_cause": False}),
            _p("Temp vent OK", "temporary_ventilation", False, "Conditional",
               "I would accept temporary intubation if there is a reversible cause, but not indefinite ventilation.",
               "conditional", {"reversible_cause": True}),
            _p("No indefinite vent", "indefinite_ventilation", True, "Absolute",
               "I would accept temporary intubation if there is a reversible cause, but not indefinite ventilation.", "clear"),
            _p("ICD off hospice", "icd_deactivation", False, "Strong",
               "Deactivate my ICD if I am enrolled in hospice.", "conditional", {"care_context": "hospice"}),
            _p("No chronic dialysis", "chronic_dialysis", True, "Absolute",
               "I do not want long-term maintenance dialysis.", "clear"),
            _p("Withdraw pressors 72h", "vasopressor_withdrawal", False, "Strong",
               "If I am on vasopressors with no improvement after 3 days, withdraw them.",
               "conditional", {"conditions": ["cardiogenic_shock"], "time_bound_hours": 72}),
        ],
    },
    {
        "patient_id": "cohort_02_texas_dnr",
        "patient_name": "Texas OOH-DNR style",
        "messy_level": "typical",
        "template_source": "Texas Out-of-Hospital DNR",
        "preferences": [
            _p("No CPR", "cpr", True, "Absolute", "Do not attempt resuscitation.", "clear"),
            _p("No defib", "defibrillation", True, "Absolute", "No defibrillation.", "clear"),
            _p("No vent", "mechanical_ventilation", True, "Absolute", "No artificial ventilation.", "clear"),
        ],
    },
    {
        "patient_id": "cohort_03_dni_accepts_cpr",
        "patient_name": "DNI but accepts CPR (realistic tension)",
        "messy_level": "typical",
        "template_source": "Clinical DNI order + separate CPR note",
        "preferences": [
            _p("Never intubate", "intubation", True, "Absolute", "I never want to be intubated.", "clear"),
            _p("Accept CPR", "cpr", False, "Strong", "If my heart stops, attempt CPR.", "clear"),
            _p("BiPAP OK", "non_invasive_ventilation", False, "Strong", "BiPAP is acceptable.", "clear"),
        ],
    },
    {
        "patient_id": "cohort_04_five_wishes_vague",
        "patient_name": "Five Wishes comfort language",
        "messy_level": "typical",
        "template_source": "Five Wishes",
        "preferences": [
            _p("No heroic measures", "cpr", True, "Weak",
               "If I am dying, no heroic measures or machines.", "vague"),
            _p("Comfort focus", "inotrope_escalation", True, "Weak",
               "Focus on comfort even if it shortens life.", "vague"),
        ],
    },
    {
        "patient_id": "cohort_05_va_aggressive",
        "patient_name": "VA full treatment",
        "messy_level": "clean",
        "template_source": "VA 10-0137",
        "preferences": [
            _p("Wants CPR", "cpr", False, "Strong", "Do everything including CPR.", "clear"),
            _p("Wants vent", "intubation", False, "Strong", "Use a breathing machine if needed.", "clear"),
            _p("Wants pressors", "vasopressor_escalation", False, "Strong", "Escalate support as needed.", "clear"),
        ],
    },
    {
        "patient_id": "cohort_06_dementia",
        "patient_name": "Dementia directive",
        "messy_level": "typical",
        "template_source": "Dementia-specific AD",
        "preferences": [
            _p("No CPR terminal", "cpr", True, "Absolute", "In advanced dementia, no CPR.", "conditional",
               {"conditions": ["terminal_condition"]}),
            _p("No intubation terminal", "intubation", True, "Absolute", "In advanced dementia, no intubation.", "conditional",
               {"conditions": ["terminal_condition"]}),
        ],
    },
    {
        "patient_id": "cohort_07_conditional_dnr",
        "patient_name": "HF conditional DNR",
        "messy_level": "clean",
        "template_source": "HF clinic addendum",
        "preferences": [
            _p("DNR if NYHA IV no reversible", "cpr", True, "Absolute",
               "No CPR if NYHA IV and no reversible cause.", "conditional",
               {"nyha_class": "IV", "conditions": ["cardiac_arrest"], "reversible_cause": False}),
            _p("Temp vent if reversible", "temporary_ventilation", False, "Conditional",
               "Short-term vent OK if reversible.", "conditional", {"reversible_cause": True}),
        ],
    },
    {
        "patient_id": "cohort_08_hospice_icd",
        "patient_name": "Hospice ICD only",
        "messy_level": "clean",
        "template_source": "Device-specific clause",
        "preferences": [
            _p("ICD off hospice", "icd_deactivation", False, "Strong",
               "Turn off my defibrillator in hospice.", "conditional", {"care_context": "hospice"}),
        ],
    },
    {
        "patient_id": "cohort_09_incomplete_lvad",
        "patient_name": "Incomplete encoding (LVAD qualifier in text only)",
        "messy_level": "incomplete_encoding",
        "template_source": "HF escalation note — encoding fidelity stress test",
        "encoding_note": "Original text mentions LVAD/transplant plan but activation_conditions omit it.",
        "preferences": [
            _p("Inotropes in shock only", "inotrope_escalation", False, "Conditional",
               "Escalate inotropes only if there is a plan for LVAD or transplant evaluation.",
               "conditional", {"conditions": ["cardiogenic_shock"]}),
        ],
    },
    {
        "patient_id": "cohort_10_minimal",
        "patient_name": "One-line minimal directive",
        "messy_level": "minimal",
        "template_source": "Handwritten note",
        "preferences": [
            _p("No machines", "mechanical_ventilation", True, "Weak",
               "No machines.", "vague"),
        ],
    },
    {
        "patient_id": "cohort_11_dialysis_split",
        "patient_name": "Acute OK / chronic no",
        "messy_level": "typical",
        "template_source": "Dialysis clause pair",
        "preferences": [
            _p("Acute dialysis OK", "acute_dialysis", False, "Conditional",
               "Dialysis if kidneys might recover.", "conditional", {"reversible_cause": True}),
            _p("No chronic dialysis", "chronic_dialysis", True, "Absolute",
               "No maintenance dialysis ever.", "clear"),
        ],
    },
    {
        "patient_id": "cohort_12_no_escalate",
        "patient_name": "Floor do-not-escalate",
        "messy_level": "typical",
        "template_source": "HF floor orders",
        "preferences": [
            _p("No pressors", "vasopressor_escalation", True, "Absolute",
               "Do not start pressors or send to ICU.", "clear"),
            _p("No inotrope escalation", "inotrope_escalation", True, "Absolute",
               "Do not escalate drips.", "clear"),
        ],
    },
    {
        "patient_id": "cohort_13_niv_refuse_intubate",
        "patient_name": "BiPAP yes / tube no",
        "messy_level": "clean",
        "template_source": "Common living will phrasing",
        "preferences": [
            _p("BiPAP OK", "non_invasive_ventilation", False, "Strong",
               "I will try BiPAP.", "clear"),
            _p("No intubation", "intubation", True, "Absolute",
               "Never a tube down my throat.", "clear"),
        ],
    },
    {
        "patient_id": "cohort_14_silent_icd",
        "patient_name": "No device preferences documented",
        "messy_level": "typical",
        "template_source": "Generic AD — HF devices absent",
        "preferences": [
            _p("No CPR terminal", "cpr", True, "Conditional",
               "No CPR if terminal.", "conditional", {"conditions": ["terminal_condition"]}),
        ],
    },
    {
        "patient_id": "cohort_15_contradictory_prose",
        "patient_name": "Contradictory family vs patient lines",
        "messy_level": "contradictory",
        "template_source": "Family meeting summary conflated into one note",
        "encoding_note": "Two CPR preferences with opposite negation — tests precedence.",
        "preferences": [
            _p("Wants CPR", "cpr", False, "Strong", "Patient said do everything at last visit.", "clear"),
            _p("No CPR", "cpr", True, "Absolute", "Earlier living will: no CPR if end-stage HF.", "conditional",
               {"conditions": ["advanced_heart_failure"]}),
        ],
    },
    {
        "patient_id": "cohort_16_runon",
        "patient_name": "Run-on statutory paragraph",
        "messy_level": "typical",
        "template_source": "California AHCD-style dense paragraph",
        "preferences": [
            _p("No CPR no vent if brain death", "cpr", True, "Conditional",
               "If permanently unconscious or brain dead no CPR or ventilator.", "conditional",
               {"conditions": ["permanent_unconsciousness"]}),
            _p("No vent if brain death", "mechanical_ventilation", True, "Conditional",
               "If permanently unconscious or brain dead no CPR or ventilator.", "conditional",
               {"conditions": ["permanent_unconsciousness"]}),
        ],
    },
    {
        "patient_id": "cohort_17_ncbc",
        "patient_name": "NCBC full ordinary care",
        "messy_level": "clean",
        "template_source": "NCBC template",
        "preferences": [
            _p("Wants CPR", "cpr", False, "Strong", "Ordinary care including resuscitation.", "clear"),
            _p("Wants vent", "intubation", False, "Strong", "Ordinary means including breathing support.", "clear"),
        ],
    },
    {
        "patient_id": "cohort_18_withdrawal_time",
        "patient_name": "Time-limited vasopressor trial",
        "messy_level": "clean",
        "template_source": "ICU trial language",
        "preferences": [
            _p("Pressor trial 96h", "vasopressor_withdrawal", False, "Conditional",
               "Stop vasopressors after 96 hours if no improvement.", "conditional",
               {"conditions": ["cardiogenic_shock"], "time_bound_hours": 96}),
        ],
    },
    {
        "patient_id": "cohort_19_nhs_unconscious",
        "patient_name": "NHS ADRT unconsciousness",
        "messy_level": "typical",
        "template_source": "NHS Wales ADRT",
        "preferences": [
            _p("No CPR unconscious", "cpr", True, "Absolute",
               "If permanently unconscious, no resuscitation.", "conditional",
               {"conditions": ["permanent_unconsciousness"]}),
            _p("No vent unconscious", "mechanical_ventilation", True, "Absolute",
               "If permanently unconscious, no artificial ventilation.", "conditional",
               {"conditions": ["permanent_unconsciousness"]}),
        ],
    },
    {
        "patient_id": "cohort_20_checkbox_only",
        "patient_name": "Checkbox form — coarse refusals only",
        "messy_level": "minimal",
        "template_source": "Simplified POLST-like checkboxes",
        "preferences": [
            _p("DNAR checked", "cpr", True, "Absolute", "DNAR.", "clear"),
            _p("Comfort care", "inotrope_escalation", True, "Absolute", "Comfort measures only.", "clear"),
        ],
    },
]
