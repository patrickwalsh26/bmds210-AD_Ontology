"""

from __future__ import annotations

import sys
from pathlib import Path as _Path

_ADO_ROOT = _Path(__file__).resolve().parents[1]
_ADO_EVAL = _Path(__file__).resolve().parent
for _p in (_ADO_ROOT, _ADO_EVAL):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

Reference-standard oracle for vignette-level decisions (independent of query_evaluation).

Implements a simplified, explicit rule set for expected decision/match_type so
large-scale simulation gold is not copied from ADO's find_matching_preferences().
Documented limitation: still team-authored clinical rules, not external chart review.
"""


INTERVENTION_KEYS = {
    "CPR": "cpr", "Defibrillation": "defibrillation", "TranscutaneousPacing": "transcutaneous_pacing",
    "Intubation": "intubation", "MechanicalVentilation": "mechanical_ventilation",
    "TemporaryVentilation": "temporary_ventilation", "IndefiniteVentilation": "indefinite_ventilation",
    "VentilationWithdrawal": "ventilation_withdrawal", "NonInvasiveVentilation": "non_invasive_ventilation",
    "ICDDeactivation": "icd_deactivation", "ICDShockTherapy": "icd_shock_therapy",
    "LVADWithdrawal": "lvad_withdrawal", "InotropeEscalation": "inotrope_escalation",
    "VasopressorWithdrawal": "vasopressor_withdrawal", "VasopressorEscalation": "vasopressor_escalation",
    "AcuteDialysis": "acute_dialysis", "ChronicDialysis": "chronic_dialysis",
}

# Broader template language often maps to coarse intervention keys (Texas DNR, etc.)
INTERVENTION_FALLBACKS = {
    "temporary_ventilation": ["mechanical_ventilation", "intubation"],
    "indefinite_ventilation": ["mechanical_ventilation", "intubation"],
    "ventilation_withdrawal": ["mechanical_ventilation"],
    "intubation": ["mechanical_ventilation"],
    "non_invasive_ventilation": ["mechanical_ventilation"],
    "defibrillation": ["cpr"],
    "icd_shock_therapy": ["icd_deactivation"],
    "vasopressor_escalation": ["inotrope_escalation"],
    "inotrope_withdrawal": ["vasopressor_withdrawal"],
}


def _parse_hours(time_elapsed) -> int | None:
    if time_elapsed is None:
        return None
    s = str(time_elapsed).lower()
    if "hour" in s:
        for tok in s.replace("hours", "").replace("hour", "").split():
            if tok.isdigit():
                return int(tok)
    return None


def _ac_met(ac: dict, scenario: dict) -> tuple[bool, bool]:
    """Return (all_required_met, any_required_unmet)."""
    if not ac:
        return True, False
    met, unmet = [], []
    nyha = ac.get("nyha_class")
    if nyha:
        sn = scenario.get("nyha_class", "")
        if sn == f"NYHA_Class{nyha}":
            met.append("nyha")
        else:
            unmet.append("nyha")
    for cond in ac.get("conditions", []):
        key = cond if isinstance(cond, str) else cond
        mapped = {
            "cardiac_arrest": "CardiacArrest", "cardiogenic_shock": "CardiogenicShock",
            "respiratory_failure": "RespiratoryFailure", "terminal_condition": "TerminalCondition",
            "permanent_unconsciousness": "PermanentUnconsciousness",
            "advanced_heart_failure": "AdvancedHeartFailure", "cardiorenal_syndrome": "CardiorenalSyndrome",
        }.get(key, key)
        if mapped in scenario.get("conditions", []):
            met.append(cond)
        else:
            unmet.append(cond)
    if "reversible_cause" in ac:
        rv = ac["reversible_cause"]
        sv = scenario.get("reversible_cause")
        if sv is None:
            unmet.append("reversible_unknown")
        elif sv == rv:
            met.append("reversible")
        else:
            unmet.append("reversible")
    if ac.get("care_context"):
        cc = {"hospice": "HospiceEnrollment", "icu": "ICUSetting"}.get(ac["care_context"], ac["care_context"])
        if scenario.get("care_context") == cc:
            met.append("context")
        else:
            unmet.append("context")
    tb = ac.get("time_bound_hours")
    if tb is not None:
        elapsed = _parse_hours(scenario.get("time_elapsed"))
        if elapsed is None:
            unmet.append("time_unknown")
        elif elapsed >= int(tb):
            met.append("time")
        else:
            unmet.append("time_not_yet")
    if unmet:
        return bool(met), True
    return True, False


def _prefs_for_intervention(prefs: list, intervention: str) -> list:
    key = INTERVENTION_KEYS.get(intervention, intervention)
    keys = [key] + INTERVENTION_FALLBACKS.get(key, [])
    out = []
    seen = set()
    for p in prefs:
        ik = p["intervention"]
        if ik in keys and ik not in seen:
            out.append(p)
            seen.add(ik)
    return out


def reference_expected(patient_data: dict, scenario_state: dict, query_intervention: str) -> dict:
    """
    Reference-standard expected decision and match_type from structured preferences only.
    """
    prefs = patient_data.get("preferences", [])
    relevant = _prefs_for_intervention(prefs, query_intervention)
    if not relevant:
        return {"decision": "no_coverage", "match_type": "no_coverage"}

    results = []
    for p in relevant:
        ac = p.get("activation_conditions") or {}
        all_met, any_unmet = _ac_met(ac, scenario_state)
        ptype = p.get("type", "clear")
        if ptype == "vague":
            if any_unmet:
                continue
            results.append((p, "vague"))
        elif any_unmet and ac:
            results.append((p, "partial"))
        elif all_met or not ac:
            results.append((p, "clear"))
        else:
            results.append((p, "partial"))

    if not results:
        return {"decision": "no_coverage", "match_type": "no_coverage"}

    clear = [r for r in results if r[1] == "clear"]
    vague = [r for r in results if r[1] == "vague"]
    if clear:
        chosen = sorted(clear, key=lambda x: {"Absolute": 0, "Strong": 1, "Conditional": 2, "Weak": 3}.get(
            x[0].get("strength", "Conditional"), 2))[0]
        neg = chosen[0]["negated"]
        return {"decision": "no" if neg else "yes", "match_type": "clear"}
    if vague:
        return {"decision": "vague", "match_type": "vague"}
    return {"decision": "partial", "match_type": "partial"}


def checkbox_baseline(patient_data: dict, scenario_state: dict, query_intervention: str,
                      default_when_no_prefs: str = "full_code_yes") -> dict:
    """
    Crude checkbox heuristic: any documented refusal on this intervention family → 'no';
    any accept → 'yes'; ignores activation conditions (models flat POLST).

    default_when_no_prefs:
      'full_code_yes' — POLST default presumes full treatment when silent (harsh vs ADO honesty)
      'no_coverage' — leave blank when directive silent
    """
    prefs = _prefs_for_intervention(patient_data.get("preferences", []), query_intervention)
    if not prefs:
        if default_when_no_prefs == "no_coverage":
            return {"decision": "no_coverage", "match_type": "no_coverage"}
        return {"decision": "yes", "match_type": "clear"}
    if any(p["negated"] for p in prefs):
        return {"decision": "no", "match_type": "clear"}
    return {"decision": "yes", "match_type": "clear"}
