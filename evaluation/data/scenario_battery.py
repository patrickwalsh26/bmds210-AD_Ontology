"""
Clinical scenario battery for multi-patient simulation.

Twenty-five scenarios covering canonical cases, boundary conditions,
multi-condition overlaps, and situations intentionally outside the
directive's scope. Designed to expose system limits, not flatter them.

Several scenarios are deliberately designed to produce no_coverage or partial
for most patients — honest evaluation requires knowing when the system
correctly declines to answer.
"""

from __future__ import annotations

SCENARIO_BATTERY = [

    # ── CANONICAL CASES ────────────────────────────────────────────────────────
    {
        "id": "S01",
        "description": "Cardiac arrest, NYHA IV, no reversible cause — core case",
        "scenario_state": {
            "conditions": ["CardiacArrest"],
            "nyha_class": "NYHA_ClassIV",
            "reversible_cause": False,
        },
        "interventions": ["CPR", "Defibrillation", "ICDShockTherapy", "TranscutaneousPacing"],
    },
    {
        "id": "S02",
        "description": "Cardiac arrest, NYHA III, reversible hyperkalemia",
        "scenario_state": {
            "conditions": ["CardiacArrest"],
            "nyha_class": "NYHA_ClassIII",
            "reversible_cause": True,
        },
        "interventions": ["CPR", "Defibrillation"],
    },
    {
        "id": "S03",
        "description": "Respiratory failure with reversible pneumonia",
        "scenario_state": {
            "conditions": ["RespiratoryFailure"],
            "reversible_cause": True,
        },
        "interventions": ["TemporaryVentilation", "NonInvasiveVentilation", "Intubation"],
    },
    {
        "id": "S04",
        "description": "Ventilator day 14, no improvement, no reversible cause",
        "scenario_state": {
            "conditions": ["RespiratoryFailure"],
            "reversible_cause": False,
        },
        "interventions": ["IndefiniteVentilation", "VentilationWithdrawal", "TemporaryVentilation"],
    },
    {
        "id": "S05",
        "description": "Hospice enrollment — device management triggered",
        "scenario_state": {
            "conditions": [],
            "care_context": "HospiceEnrollment",
        },
        "interventions": ["ICDDeactivation", "LVADWithdrawal", "CPR", "NonInvasiveVentilation"],
    },
    {
        "id": "S06",
        "description": "ICU VT storm — ICD firing repeatedly",
        "scenario_state": {
            "conditions": ["VentricularTachycardia"],
            "care_context": "ICUSetting",
        },
        "interventions": ["ICDShockTherapy", "ICDDeactivation", "Defibrillation"],
    },
    {
        "id": "S07",
        "description": "Cardiogenic shock — 96 hours on vasopressors, no improvement",
        "scenario_state": {
            "conditions": ["CardiogenicShock"],
            "time_elapsed": "96 hours",
        },
        "interventions": ["VasopressorWithdrawal", "InotropeEscalation", "VasopressorEscalation"],
    },
    {
        "id": "S08",
        "description": "Cardiogenic shock — 48 hours, time threshold not yet met",
        "scenario_state": {
            "conditions": ["CardiogenicShock"],
            "time_elapsed": "48 hours",
        },
        "interventions": ["VasopressorWithdrawal", "InotropeEscalation"],
    },
    {
        "id": "S09",
        "description": "Cardiorenal syndrome — kidney recovery expected",
        "scenario_state": {
            "conditions": ["CardiorenalSyndrome"],
            "reversible_cause": True,
        },
        "interventions": ["AcuteDialysis", "ChronicDialysis"],
    },
    {
        "id": "S10",
        "description": "Terminal condition confirmed — advanced disease",
        "scenario_state": {
            "conditions": ["TerminalCondition"],
        },
        "interventions": ["CPR", "Intubation", "VasopressorEscalation", "InotropeEscalation"],
    },
    {
        "id": "S11",
        "description": "Permanent unconsciousness — condition clearly met",
        "scenario_state": {
            "conditions": ["PermanentUnconsciousness"],
        },
        "interventions": ["CPR", "MechanicalVentilation", "AcuteDialysis"],
    },

    # ── BOUNDARY CONDITIONS ───────────────────────────────────────────────────
    {
        "id": "S12",
        "description": "Cardiac arrest, NYHA II — condition threshold not met",
        "scenario_state": {
            "conditions": ["CardiacArrest"],
            "nyha_class": "NYHA_ClassII",
            "reversible_cause": False,
        },
        "interventions": ["CPR", "Defibrillation"],
        "note": "Most conditional DNR clauses require NYHA IV. Should return partial for those patients.",
    },
    {
        "id": "S13",
        "description": "Cardiogenic shock — exactly 72 hours (time bound boundary)",
        "scenario_state": {
            "conditions": ["CardiogenicShock"],
            "time_elapsed": "72 hours",
        },
        "interventions": ["VasopressorWithdrawal"],
        "note": "Exactly at threshold. System must evaluate >= not >.",
    },
    {
        "id": "S14",
        "description": "Cardiogenic shock — 71 hours (just under threshold)",
        "scenario_state": {
            "conditions": ["CardiogenicShock"],
            "time_elapsed": "71 hours",
        },
        "interventions": ["VasopressorWithdrawal"],
        "note": "One hour below threshold. Should return partial.",
    },
    {
        "id": "S15",
        "description": "Acute kidney injury — sepsis etiology, NOT cardiorenal",
        "scenario_state": {
            "conditions": [],
            "reversible_cause": True,
        },
        "interventions": ["AcuteDialysis", "ChronicDialysis"],
        "note": "Sepsis-AKI, not cardiorenal. Tests condition specificity — "
                "cardiorenal_syndrome condition should not fire.",
    },
    {
        "id": "S16",
        "description": "Stable outpatient, NYHA II — no acute illness",
        "scenario_state": {
            "conditions": [],
            "nyha_class": "NYHA_ClassII",
        },
        "interventions": ["CPR", "ICDDeactivation", "ChronicDialysis"],
        "note": "Non-acute scenario. Tests that conditional preferences don't fire inappropriately.",
    },

    # ── MULTI-CONDITION OVERLAPS ──────────────────────────────────────────────
    {
        "id": "S17",
        "description": "Advanced HF, cardiac arrest, NYHA IV, reversible hyperkalemia",
        "scenario_state": {
            "conditions": ["CardiacArrest", "AdvancedHeartFailure"],
            "nyha_class": "NYHA_ClassIV",
            "reversible_cause": True,
        },
        "interventions": ["CPR", "Defibrillation", "TemporaryVentilation"],
        "note": "Reversible cause present despite advanced HF — tests whether reversibility "
                "correctly overrides NYHA-IV conditional refusals.",
    },
    {
        "id": "S18",
        "description": "Cardiogenic shock + respiratory failure simultaneously",
        "scenario_state": {
            "conditions": ["CardiogenicShock", "RespiratoryFailure"],
            "reversible_cause": False,
            "time_elapsed": "80 hours",
        },
        "interventions": [
            "VasopressorWithdrawal", "InotropeEscalation",
            "TemporaryVentilation", "IndefiniteVentilation",
        ],
        "note": "Dual active conditions. Multiple preferences may fire simultaneously.",
    },
    {
        "id": "S19",
        "description": "Terminal condition + cardiac arrest — both conditions active",
        "scenario_state": {
            "conditions": ["TerminalCondition", "CardiacArrest"],
            "nyha_class": "NYHA_ClassIV",
            "reversible_cause": False,
        },
        "interventions": ["CPR", "Intubation", "Defibrillation"],
        "note": "Terminal + arrest: tests priority of most specific applicable preference.",
    },

    # ── OUTSIDE STANDARD DIRECTIVE SCOPE ─────────────────────────────────────
    {
        "id": "S20",
        "description": "Pacemaker-dependent patient — bradyasystolic arrest",
        "scenario_state": {
            "conditions": ["CardiacArrest"],
            "nyha_class": "NYHA_ClassIII",
            "reversible_cause": False,
        },
        "interventions": ["TranscutaneousPacing", "PacemakerDeactivation", "ICDShockTherapy"],
        "note": "Pacemaker deactivation and transcutaneous pacing rarely addressed in ADs. "
                "Expect no_coverage for most patients.",
    },
    {
        "id": "S21",
        "description": "LVAD malfunction — deactivation vs continuation decision",
        "scenario_state": {
            "conditions": ["CardiogenicShock"],
            "nyha_class": "NYHA_ClassIV",
        },
        "interventions": ["LVADWithdrawal", "InotropeEscalation", "CPR"],
        "note": "LVAD withdrawal is addressed only in device-specific directives. "
                "Expect no_coverage for most standard templates.",
    },
    {
        "id": "S22",
        "description": "Acute PE with cardiac arrest — reversible cause",
        "scenario_state": {
            "conditions": ["CardiacArrest"],
            "reversible_cause": True,
            "nyha_class": "NYHA_ClassIV",
        },
        "interventions": ["CPR", "TemporaryVentilation", "Defibrillation"],
        "note": "Reversible cause should distinguish from HF-related arrest for conditional DNR patients.",
    },
    {
        "id": "S23",
        "description": "Comfort care floor — no acute deterioration, goals clarification",
        "scenario_state": {
            "conditions": [],
            "care_context": "InpatientFloor",
        },
        "interventions": ["CPR", "ICDDeactivation", "VasopressorEscalation", "InotropeEscalation"],
        "note": "Non-ICU, non-hospice inpatient. Tests whether care context specificity matters.",
    },

    # ── EXPLICIT STRESS TESTS ─────────────────────────────────────────────────
    {
        "id": "S24",
        "description": "Chronic kidney disease — no cardiorenal syndrome, no reversibility",
        "scenario_state": {
            "conditions": [],
            "reversible_cause": False,
        },
        "interventions": ["AcuteDialysis", "ChronicDialysis"],
        "note": "CKD without cardiorenal syndrome, irreversible. Tests boundary of dialysis preferences.",
    },
    {
        "id": "S25",
        "description": "Stable ICU admission — no acute crisis, monitoring only",
        "scenario_state": {
            "conditions": [],
            "care_context": "ICUSetting",
            "nyha_class": "NYHA_ClassIII",
        },
        "interventions": ["CPR", "ICDDeactivation", "InotropeEscalation", "AcuteDialysis"],
        "note": "Monitoring/observation admission. Tests that no acute conditions do not fire "
                "condition-gated preferences.",
    },
]
