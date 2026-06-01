"""
Held-out clinical vignettes (frozen 2026-06-01).

Authored separately from the 16 development vignettes in query_evaluation.VIGNETTES.
Gold labels were written before re-running the reasoner on this split.
Do not tune reasoner logic against these IDs.
"""

HOLDOUT_VIGNETTES = [
    {
        "id": "H1",
        "description": "Cardiac arrest, NYHA IV, no reversible cause. Should defibrillation be performed?",
        "query_intervention": "Defibrillation",
        "scenario_state": {
            "conditions": ["CardiacArrest"],
            "nyha_class": "NYHA_ClassIV",
            "reversible_cause": False,
        },
        "expected": {
            "decision": "no_coverage",
            "match_type": "no_coverage",
            "reasoning": "Jane's AD refuses CPR under these conditions but does not mention defibrillation as a distinct intervention.",
        },
    },
    {
        "id": "H2",
        "description": "Stable outpatient, NYHA Class II. Should CPR be attempted if the patient arrests?",
        "query_intervention": "CPR",
        "scenario_state": {
            "conditions": [],
            "nyha_class": "NYHA_ClassII",
        },
        "expected": {
            "decision": "partial",
            "match_type": "partial",
            "reasoning": "No-CPR preference requires cardiac arrest + NYHA IV + no reversible cause; scenario lacks arrest — conditions not met.",
        },
    },
    {
        "id": "H3",
        "description": "Respiratory failure with reversible pneumonia. Should temporary ventilation be offered?",
        "query_intervention": "TemporaryVentilation",
        "scenario_state": {
            "conditions": ["RespiratoryFailure"],
            "reversible_cause": True,
        },
        "expected": {
            "decision": "yes",
            "match_type": "clear",
            "reasoning": "Patient accepts temporary ventilation when a reversible cause is present.",
        },
    },
    {
        "id": "H4",
        "description": "ICU patient in VT; ICD is about to shock. Should shock therapy be withheld?",
        "query_intervention": "ICDShockTherapy",
        "scenario_state": {
            "conditions": ["VentricularTachycardia"],
            "care_context": "ICUSetting",
        },
        "expected": {
            "decision": "no_coverage",
            "match_type": "no_coverage",
            "reasoning": "Only ICD deactivation in hospice is documented — not shock therapy during arrhythmia.",
        },
    },
    {
        "id": "H5",
        "description": "Should transcutaneous pacing be started during bradyasystolic arrest?",
        "query_intervention": "TranscutaneousPacing",
        "scenario_state": {
            "conditions": ["CardiacArrest"],
            "nyha_class": "NYHA_ClassIV",
            "reversible_cause": False,
        },
        "expected": {
            "decision": "no_coverage",
            "match_type": "no_coverage",
            "reasoning": "No preference addresses transcutaneous pacing.",
        },
    },
    {
        "id": "H6",
        "description": "Patient wants LVAD removed. Should LVAD withdrawal proceed?",
        "query_intervention": "LVADWithdrawal",
        "scenario_state": {
            "conditions": ["CardiogenicShock"],
            "nyha_class": "NYHA_ClassIV",
        },
        "expected": {
            "decision": "no_coverage",
            "match_type": "no_coverage",
            "reasoning": "No LVAD-specific preference in the encoded directive.",
        },
    },
    {
        "id": "H7",
        "description": "Cardiogenic shock without documented LVAD/transplant plan. Should inotropes be escalated?",
        "query_intervention": "InotropeEscalation",
        "scenario_state": {
            "conditions": ["CardiogenicShock"],
        },
        "expected": {
            "decision": "yes",
            "match_type": "clear",
            "reasoning": "Encoded preference fires on cardiogenic shock only (LVAD/transplant qualifier in prose was not encoded as activation).",
        },
    },
    {
        "id": "H8",
        "description": "Enrolled in hospice. Should ICD be deactivated per patient wishes?",
        "query_intervention": "ICDDeactivation",
        "scenario_state": {
            "conditions": [],
            "care_context": "HospiceEnrollment",
        },
        "expected": {
            "decision": "yes",
            "match_type": "clear",
            "reasoning": "Hospice enrollment matches ICD deactivation preference.",
        },
    },
    {
        "id": "H9",
        "description": "Patient on vasopressors 50 hours for cardiogenic shock. Withdraw now?",
        "query_intervention": "VasopressorWithdrawal",
        "scenario_state": {
            "conditions": ["CardiogenicShock"],
            "time_elapsed": "50 hours",
        },
        "expected": {
            "decision": "partial",
            "match_type": "partial",
            "reasoning": "72-hour threshold not yet met — same logic as development vignette V13.",
        },
    },
    {
        "id": "H10",
        "description": "Respiratory failure; patient is not dying. Start BiPAP (NIV)?",
        "query_intervention": "NonInvasiveVentilation",
        "scenario_state": {
            "conditions": ["RespiratoryFailure"],
        },
        "expected": {
            "decision": "vague",
            "match_type": "vague",
            "reasoning": "Only NIV-relevant text is vague ('aggressive measures if dying'); scenario does not include terminal/dying condition.",
        },
    },
]
