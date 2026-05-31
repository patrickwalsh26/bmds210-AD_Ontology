"""
Free-text Advance Directive → structured JSON via Gemini (Track 1b Arm B).

Mirrors the schema and closed-world prompt from llm_extraction.py but calls Google
Gemini instead of Claude. Does not import llm_extraction.py.

Requires GEMINI_API_KEY or GOOGLE_API_KEY. Install: pip install google-genai pydantic
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from typing import List, Literal, Optional, Type, TypeVar

try:
    from google import genai
    from google.genai import errors as genai_errors
    from google.genai import types
except ImportError:
    print("ERROR: google-genai not installed. Run: pip install google-genai", file=sys.stderr)
    sys.exit(1)

try:
    from pydantic import BaseModel, Field
except ImportError:
    print("ERROR: pydantic not installed. Run: pip install 'pydantic>=2'", file=sys.stderr)
    sys.exit(1)


DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")

T = TypeVar("T", bound=BaseModel)


# ── Pydantic schema (mirrors llm_extraction.py) ─────────────────────────────

InterventionKey = Literal[
    "cpr", "defibrillation", "transcutaneous_pacing",
    "intubation", "mechanical_ventilation", "temporary_ventilation",
    "indefinite_ventilation", "ventilation_withdrawal", "non_invasive_ventilation",
    "icd_deactivation", "icd_shock_therapy", "lvad_withdrawal", "lvad_continuation",
    "pacemaker_deactivation",
    "inotrope_escalation", "inotrope_withdrawal",
    "vasopressor_escalation", "vasopressor_withdrawal",
    "acute_dialysis", "chronic_dialysis", "dialysis_withdrawal",
]

ConditionKey = Literal[
    "heart_failure", "advanced_heart_failure", "cardiac_arrest",
    "cardiogenic_shock", "acute_decompensation", "cardiorenal_syndrome",
    "respiratory_failure", "terminal_condition", "permanent_unconsciousness",
    "incapacity",
]

NYHAClass = Literal["I", "II", "III", "IV"]
CareContextKey = Literal["icu", "ed", "hospice", "outpatient", "prehospital"]
Strength = Literal["Absolute", "Strong", "Conditional", "Weak"]
PreferenceType = Literal["clear", "conditional", "vague"]


class ActivationConditions(BaseModel):
    nyha_class: Optional[NYHAClass] = None
    conditions: Optional[List[ConditionKey]] = None
    reversible_cause: Optional[bool] = None
    time_bound: Optional[str] = None
    time_bound_hours: Optional[int] = None
    care_context: Optional[CareContextKey] = None


class Preference(BaseModel):
    label: str
    intervention: InterventionKey
    negated: bool
    strength: Strength
    original_text: str
    type: PreferenceType
    activation_conditions: Optional[ActivationConditions] = None


class ExtractedPreferences(BaseModel):
    preferences: List[Preference]
    extraction_notes: Optional[str] = None


SYSTEM_PROMPT = """You are an extraction assistant for the Advance Directive Ontology (ADO), a computable representation of end-of-life care preferences scoped to advanced heart failure. Given verbatim text from a patient's advance directive, your job is to convert it into structured preference statements that a downstream OWL reasoner can evaluate against clinical scenarios.

# CRITICAL RULES

1. **Closed-world extraction.** Encode ONLY what the patient explicitly stated. Do NOT extrapolate from related preferences. If the patient said nothing about an intervention, return no preference for it. The reasoner's "no coverage" output depends entirely on this discipline — if you invent preferences the patient never stated, the reasoner will report false matches at the bedside.

2. **Preserve original language verbatim.** For each preference, `original_text` must contain the patient's exact words for that preference (you may quote a sentence or fragment, but do not paraphrase, summarize, or clean up the language).

3. **Vague language is a first-class category.** Phrases like "no heroic measures", "no aggressive treatment", "be kept comfortable", "no machines" are irreducibly imprecise. Classify them as `type: "vague"` with `strength: "Weak"`. Map them to the closest formal intervention so the system has something to anchor on, but the `vague` type tells the reasoner to surface the patient's original words to a human rather than force a binary decision.

4. **Strength inference:**
   - "I absolutely do not want X" / "no X under any circumstances" → `Absolute`
   - "I want X" / "I do not want X" (unqualified) → `Strong`
   - "I would accept X if Y" / "X only if Y" → `Conditional`
   - "I would prefer not to" / vague language → `Weak`

5. **Type classification:**
   - `clear` — unambiguous, no activation conditions, applies in all scenarios
   - `conditional` — applies only when specific conditions are met (NYHA class, reversible cause, time bound, care context, clinical condition)
   - `vague` — language is irreducibly imprecise (see rule 3)

# VOCABULARY (use these keys exactly)

**Interventions** (21):
- CPR: `cpr`, `defibrillation`, `transcutaneous_pacing`
- Ventilation: `intubation`, `mechanical_ventilation`, `temporary_ventilation`, `indefinite_ventilation`, `ventilation_withdrawal`, `non_invasive_ventilation`
- Device: `icd_deactivation`, `icd_shock_therapy`, `lvad_withdrawal`, `lvad_continuation`, `pacemaker_deactivation`
- Vasoactive: `inotrope_escalation`, `inotrope_withdrawal`, `vasopressor_escalation`, `vasopressor_withdrawal`
- Dialysis: `acute_dialysis`, `chronic_dialysis`, `dialysis_withdrawal`

**Clinical conditions:** `heart_failure`, `advanced_heart_failure`, `cardiac_arrest`, `cardiogenic_shock`, `acute_decompensation`, `cardiorenal_syndrome`, `respiratory_failure`, `terminal_condition`, `permanent_unconsciousness`, `incapacity`

**NYHA classes:** `I`, `II`, `III`, `IV`

**Care contexts:** `icu`, `ed`, `hospice`, `outpatient`, `prehospital`

**Strengths:** `Absolute`, `Strong`, `Conditional`, `Weak`

**Types:** `clear`, `conditional`, `vague`

Return a single JSON object matching the ExtractedPreferences schema. Include `extraction_notes` only if a judgment call deserves flagging. When in doubt, prefer fewer preferences with higher confidence over speculative ones."""


def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set."
        )
    return key


def get_gemini_client() -> genai.Client:
    return genai.Client(api_key=get_api_key())


def _retry_delay_seconds(exc: genai_errors.ClientError, attempt: int) -> float:
    """Parse RetryInfo from a 429 or fall back to exponential backoff."""
    message = str(exc)
    m = re.search(r"retry in (\d+(?:\.\d+)?)s", message, re.IGNORECASE)
    if m:
        return float(m.group(1)) + 1.0
    return min(60.0, 15.0 * (attempt + 1))


def generate_structured(
    client: genai.Client,
    *,
    system_prompt: str,
    user_prompt: str,
    schema: Type[T],
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_retries: int = 12,
) -> T:
    """Call Gemini with JSON schema constrained output and validate with Pydantic."""
    last_exc: Optional[Exception] = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model or DEFAULT_MODEL,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=temperature,
                ),
            )
            text = response.text
            if not text:
                raise RuntimeError("Gemini returned empty response")
            return schema.model_validate_json(text)
        except genai_errors.ClientError as exc:
            last_exc = exc
            if getattr(exc, "code", None) == 429 and attempt < max_retries - 1:
                wait = _retry_delay_seconds(exc, attempt)
                print(
                    f"  Gemini rate limit (429); waiting {wait:.0f}s "
                    f"(attempt {attempt + 1}/{max_retries})...",
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue
            raise
    raise last_exc or RuntimeError("Gemini call failed after retries")


def extract_preferences(
    ad_text: str,
    client: Optional[genai.Client] = None,
    *,
    model: Optional[str] = None,
) -> ExtractedPreferences:
    """Extract structured preferences from free-text AD language via Gemini."""
    if client is None:
        client = get_gemini_client()

    user_prompt = (
        "Extract structured preferences from the following advance directive text. "
        "Remember: encode only what the patient explicitly stated; preserve original "
        "language verbatim; flag vague phrasing with type='vague'.\n\n"
        f"---\n{ad_text}\n---"
    )
    return generate_structured(
        client,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=ExtractedPreferences,
        model=model,
    )


def to_patient_json(
    extracted: ExtractedPreferences,
    *,
    patient_id: str = "gemini_extracted_001",
    patient_name: str = "Gemini-extracted patient",
    source_label: str = "Gemini-extracted from free-text AD (Track 1b Arm B)",
) -> dict:
    """Convert ExtractedPreferences into the dict shape populate_patient() expects."""
    return {
        "patient_id": patient_id,
        "patient_name": patient_name,
        "source_document": {"type": "living_will", "label": source_label},
        "preferences": [
            {
                "label": p.label,
                "intervention": p.intervention,
                "negated": p.negated,
                "strength": p.strength,
                "original_text": p.original_text,
                "type": p.type,
                "activation_conditions": (
                    {k: v for k, v in p.activation_conditions.model_dump().items() if v is not None}
                    if p.activation_conditions else {}
                ),
            }
            for p in extracted.preferences
        ],
    }


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Extract AD preferences via Gemini (Track 1b).")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", type=str, help="Path to AD text file.")
    src.add_argument("--text", type=str, help="Inline AD text.")
    parser.add_argument("--save", type=str, help="Write resulting patient JSON here.")
    args = parser.parse_args()

    ad_text = Path(args.file).read_text() if args.file else args.text
    print(f"Model: {DEFAULT_MODEL}")
    extracted = extract_preferences(ad_text)
    patient_data = to_patient_json(extracted)
    print(json.dumps(patient_data, indent=2))
    if args.save:
        Path(args.save).write_text(json.dumps(patient_data, indent=2))
        print(f"Wrote: {args.save}")
