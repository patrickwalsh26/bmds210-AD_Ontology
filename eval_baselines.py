#!/usr/bin/env python3
"""
Baseline comparators for vignette evaluation.

  * condition_blind — ignores activation-condition gating (ablation)
  * checkbox_cpr    — maps only unconditional CPR refusal to DNR-like answer
"""

from __future__ import annotations

from query_evaluation import find_matching_preferences


def find_matching_preferences_condition_blind(onto, patient, query_intervention, scenario_state):
    """Match intervention class only; treat every matched preference as clear."""
    matches = find_matching_preferences(onto, patient, query_intervention, scenario_state)
    if not matches:
        return []

    blind = []
    for pref, _mt, detail in matches:
        blind.append((pref, "clear", f"[condition-blind] {detail}"))
    return blind


def decision_from_matches_condition_blind(matches):
    """Same aggregation as evaluate_vignette but all matches are 'clear'."""
    if not matches:
        return "no_coverage", "no_coverage"
    pref, match_type, _ = matches[0]
    negated = pref.isNegated[0] if pref.isNegated else False
    if match_type == "clear":
        return ("no" if negated else "yes"), "clear"
    return "partial", "partial"
