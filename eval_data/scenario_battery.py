"""
Clinical scenario battery for multi-patient simulation.

Twelve acute HF situations reused across the cohort; each entry lists which
interventions are clinically queried in that situation.
"""

SCENARIO_BATTERY = [
    {
        "id": "S01",
        "description": "Cardiac arrest, NYHA IV, no reversible cause",
        "scenario_state": {"conditions": ["CardiacArrest"], "nyha_class": "NYHA_ClassIV", "reversible_cause": False},
        "interventions": ["CPR", "Defibrillation", "ICDShockTherapy"],
    },
    {
        "id": "S02",
        "description": "Cardiac arrest, NYHA III, reversible hyperkalemia",
        "scenario_state": {"conditions": ["CardiacArrest"], "nyha_class": "NYHA_ClassIII", "reversible_cause": True},
        "interventions": ["CPR", "Defibrillation"],
    },
    {
        "id": "S03",
        "description": "Respiratory failure, reversible pneumonia",
        "scenario_state": {"conditions": ["RespiratoryFailure"], "reversible_cause": True},
        "interventions": ["TemporaryVentilation", "NonInvasiveVentilation", "Intubation"],
    },
    {
        "id": "S04",
        "description": "Ventilator day 10, no improvement",
        "scenario_state": {"conditions": ["RespiratoryFailure"], "reversible_cause": False},
        "interventions": ["IndefiniteVentilation", "VentilationWithdrawal"],
    },
    {
        "id": "S05",
        "description": "Enrolled in hospice",
        "scenario_state": {"care_context": "HospiceEnrollment"},
        "interventions": ["ICDDeactivation", "CPR"],
    },
    {
        "id": "S06",
        "description": "ICU, not hospice — VT with ICD firing",
        "scenario_state": {"conditions": ["VentricularTachycardia"], "care_context": "ICUSetting"},
        "interventions": ["ICDShockTherapy", "ICDDeactivation"],
    },
    {
        "id": "S07",
        "description": "Cardiogenic shock, 96h on pressors",
        "scenario_state": {"conditions": ["CardiogenicShock"], "time_elapsed": "96 hours"},
        "interventions": ["VasopressorWithdrawal", "InotropeEscalation", "VasopressorEscalation"],
    },
    {
        "id": "S08",
        "description": "Cardiogenic shock, 48h on pressors",
        "scenario_state": {"conditions": ["CardiogenicShock"], "time_elapsed": "48 hours"},
        "interventions": ["VasopressorWithdrawal"],
    },
    {
        "id": "S09",
        "description": "Cardiorenal syndrome, recovery expected",
        "scenario_state": {"conditions": ["CardiorenalSyndrome"], "reversible_cause": True},
        "interventions": ["AcuteDialysis", "ChronicDialysis"],
    },
    {
        "id": "S10",
        "description": "AKI sepsis, not cardiorenal — reversible",
        "scenario_state": {"conditions": [], "reversible_cause": True},
        "interventions": ["AcuteDialysis"],
    },
    {
        "id": "S11",
        "description": "Terminal condition / advanced dementia",
        "scenario_state": {"conditions": ["TerminalCondition"]},
        "interventions": ["CPR", "Intubation", "VasopressorEscalation"],
    },
    {
        "id": "S12",
        "description": "Permanent unconsciousness — condition met",
        "scenario_state": {"conditions": ["PermanentUnconsciousness"]},
        "interventions": ["CPR", "MechanicalVentilation"],
    },
]
