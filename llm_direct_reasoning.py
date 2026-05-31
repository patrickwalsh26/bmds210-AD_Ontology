"""
Direct AD + clinical scenario → decision via Gemini (Track 1b Arm C).

Skips ontology extraction and reasoning. One Gemini call per vignette returns
decision, match_type, reasoning, and cited AD text — scored against the same
gold labels as query_evaluation.py.

Requires GEMINI_API_KEY or GOOGLE_API_KEY. Install: pip install google-genai pydantic
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from gemini_extraction import DEFAULT_MODEL, generate_structured, get_gemini_client


Decision = Literal["yes", "no", "partial", "no_coverage", "vague"]
MatchType = Literal["clear", "partial", "no_coverage", "vague"]
PromptVariant = Literal["minimal", "matched"]


INTERVENTION_LABELS = {
    "CPR": "CPR / cardiopulmonary resuscitation",
    "TemporaryVentilation": "temporary mechanical ventilation (bridge therapy)",
    "IndefiniteVentilation": "indefinite / long-term mechanical ventilation",
    "ICDDeactivation": "ICD (implantable defibrillator) deactivation",
    "AcuteDialysis": "acute / short-term dialysis",
    "ChronicDialysis": "chronic / maintenance dialysis",
    "InotropeEscalation": "inotrope escalation",
    "VasopressorWithdrawal": "vasopressor withdrawal",
    "NonInvasiveVentilation": "non-invasive ventilation (e.g., BiPAP)",
    "PacemakerDeactivation": "pacemaker deactivation",
    "ICDShockTherapy": "ICD shock therapy during arrhythmia",
}


MATCHED_DISCIPLINE_RULES = """
# CRITICAL RULES

1. **Closed-world reasoning.** Base your answer ONLY on what the advance directive explicitly states. Do NOT infer preferences the patient never stated. If the directive is silent on the intervention, return decision=no_coverage and match_type=no_coverage.

2. **Vague language is not a binary answer.** Phrases like "no heroic measures", "aggressive treatment", or "kept alive by machines" are irreducibly imprecise. When the directive uses such language for the queried intervention, return decision=vague and match_type=vague — do not force yes or no.

3. **Conditional preferences.** If the directive addresses the intervention only under specific conditions (NYHA class, reversible cause, hospice, time elapsed, etc.) and those conditions are not fully met in the scenario, return decision=partial and match_type=partial unless the directive gives an unconditional answer.

4. **Label definitions:**
   - decision=yes — patient wants the intervention in this scenario
   - decision=no — patient refuses the intervention in this scenario
   - decision=partial — directive touches this topic but does not clearly authorize or refuse in this exact scenario
   - decision=no_coverage — directive says nothing relevant about this intervention
   - decision=vague — relevant language exists but is too imprecise for a binary answer
   - match_type mirrors how confidently the directive applies (clear / partial / no_coverage / vague)
"""


class DirectDecision(BaseModel):
    decision: Decision = Field(
        description="Care decision indicated for this scenario."
    )
    match_type: MatchType = Field(
        description="How well the directive addresses this scenario."
    )
    reasoning: str = Field(
        description="Brief clinical reasoning (2-4 sentences)."
    )
    cited_text: str = Field(
        description="Verbatim AD fragment relied on, or empty string if none."
    )
    confidence: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Self-assessed confidence in the label assignment.",
    )


def _format_scenario_state(scenario_state: dict) -> str:
    if not scenario_state:
        return "- No structured state provided."
    lines = []
    for key, value in scenario_state.items():
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value) if value else "(none)"
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def _build_prompts(
    ad_text: str,
    vignette: dict,
    variant: PromptVariant,
) -> tuple[str, str]:
    intervention_key = vignette["query_intervention"]
    intervention_label = INTERVENTION_LABELS.get(intervention_key, intervention_key)
    scenario_block = _format_scenario_state(vignette.get("scenario_state", {}))

    user_prompt = f"""Advance directive (full text):

---
{ad_text}
---

Clinical scenario:
{vignette["description"]}

Structured patient state:
{scenario_block}

Clinical question: Should {intervention_label} be initiated or allowed in this scenario?

Return a JSON object with decision, match_type, reasoning, cited_text, and confidence."""

    if variant == "minimal":
        system_prompt = (
            "You are a clinical ethics consultant interpreting an advance directive "
            "under time pressure. Answer the clinical question using only the directive text."
        )
    else:
        system_prompt = (
            "You are a clinical ethics consultant interpreting an advance directive "
            "under time pressure. Answer the clinical question using only the directive text.\n"
            + MATCHED_DISCIPLINE_RULES
        )

    return system_prompt, user_prompt


def reason_directly(
    ad_text: str,
    vignette: dict,
    *,
    variant: PromptVariant = "minimal",
    client=None,
    model: Optional[str] = None,
    temperature: float = 0.0,
) -> DirectDecision:
    """Single-call Gemini reasoning for one vignette (Arm C)."""
    if client is None:
        client = get_gemini_client()

    system_prompt, user_prompt = _build_prompts(ad_text, vignette, variant)
    return generate_structured(
        client,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        schema=DirectDecision,
        model=model,
        temperature=temperature,
    )


def score_direct_decision(direct: DirectDecision, vignette: dict) -> dict:
    """Compare a DirectDecision to vignette gold labels."""
    expected = vignette["expected"]
    return {
        "id": vignette["id"],
        "description": vignette["description"],
        "query_intervention": vignette["query_intervention"],
        "system_decision": direct.decision,
        "expected_decision": expected["decision"],
        "decision_correct": direct.decision == expected["decision"],
        "system_match_type": direct.match_type,
        "expected_match_type": expected["match_type"],
        "match_type_correct": direct.match_type == expected["match_type"],
        "detail": direct.reasoning,
        "cited_text": direct.cited_text,
        "confidence": direct.confidence,
        "expected_reasoning": expected["reasoning"],
    }
