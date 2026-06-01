"""
Free-text Advance Directive → structured JSON via Claude (Path B).

The ontology and reasoner are the *auditable core* of an EOL decision-support
system. This module is the LLM-powered translation layer at the boundary: it
converts verbatim AD language into the structured JSON schema that
preference_input.py already accepts, so the rest of the pipeline (population,
reasoning, 4-category output) is unchanged.

Architecture:

    free-text AD ──[Claude w/ structured output]──> JSON ──> populate_patient() ──> reasoner

Design choices:
  * Closed-world extraction. The system prompt instructs the model to encode
    ONLY what the patient explicitly stated — never to extrapolate. The
    reasoner's downstream "no coverage" output depends on this discipline.
  * Verbatim original_text. The patient's actual language is preserved for
    each preference, mirroring the ontology's VaguePreference design and the
    Stanford Letter Project's emphasis on patient voice.
  * Vague flagging. Imprecise language ("no heroic measures") is classified
    as type=vague so the reasoner can surface it as VagueMatch rather than
    forcing a binary answer.

Usage:
    python llm_extraction.py --example                   # extract built-in example
    python llm_extraction.py --text "..." [--save out.json]
    python llm_extraction.py --file path/to/ad_text.txt --save out.json

Requires ANTHROPIC_API_KEY in the environment. Install: pip install anthropic pydantic
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Literal, Optional

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic SDK not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)

try:
    from pydantic import BaseModel, Field
except ImportError:
    print("ERROR: pydantic not installed. Run: pip install 'pydantic>=2'", file=sys.stderr)
    sys.exit(1)

from ado.preference_input import (
    INTERVENTIONS,
    CONDITIONS,
    NYHA_CLASSES,
    CARE_CONTEXTS,
    PREFERENCE_STRENGTHS,
)


MODEL = "claude-opus-4-7"


# ── Pydantic schema — mirrors preference_input.py's JSON schema ─────────────

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
    """Conditions under which a preference fires. All fields optional."""

    nyha_class: Optional[NYHAClass] = Field(
        None,
        description="NYHA functional class the preference is conditional on."
    )
    conditions: Optional[List[ConditionKey]] = Field(
        None,
        description="Clinical conditions required for the preference to apply."
    )
    reversible_cause: Optional[bool] = Field(
        None,
        description="If the preference requires a reversible vs irreversible cause."
    )
    time_bound: Optional[str] = Field(
        None,
        description="Human-readable temporal constraint, e.g. 'no improvement after 72 hours'."
    )
    time_bound_hours: Optional[int] = Field(
        None,
        description="The temporal constraint expressed in hours, for numeric reasoning."
    )
    care_context: Optional[CareContextKey] = Field(
        None,
        description="Care setting required for the preference to apply (e.g. hospice)."
    )


class Preference(BaseModel):
    """A single preference statement extracted from the AD text."""

    label: str = Field(description="Short human-readable label.")
    intervention: InterventionKey = Field(description="The specific intervention this preference addresses.")
    negated: bool = Field(description="True if the patient does NOT want this intervention.")
    strength: Strength = Field(description="Strength of the preference.")
    original_text: str = Field(
        description="VERBATIM patient language for this preference. Do not paraphrase."
    )
    type: PreferenceType = Field(description="clear, conditional, or vague.")
    activation_conditions: Optional[ActivationConditions] = Field(
        None,
        description="Activation conditions; omit if the preference is unconditional."
    )


class ExtractedPreferences(BaseModel):
    """The structured output of LLM extraction over an AD excerpt."""

    preferences: List[Preference] = Field(
        description="All preferences extractable from the input text."
    )
    extraction_notes: Optional[str] = Field(
        None,
        description="Brief notes on ambiguities, items deliberately not extracted, or judgment calls."
    )


# ── System prompt ───────────────────────────────────────────────────────────

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

# THE ONTOLOGY

ADO covers five clinical decision points where advance directives are most often consulted in advanced heart failure:
- CPR / resuscitation
- Mechanical ventilation / intubation
- ICD / device management
- Vasopressor / inotrope
- Dialysis

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

# EXAMPLE

Input: "If I am in NYHA Class IV with no chance of recovery and my heart stops, do not perform CPR. I would accept temporary mechanical ventilation if there is a reversible cause."

Output:
```json
{
  "preferences": [
    {
      "label": "No CPR if NYHA IV with no reversible cause",
      "intervention": "cpr",
      "negated": true,
      "strength": "Absolute",
      "original_text": "If I am in NYHA Class IV with no chance of recovery and my heart stops, do not perform CPR.",
      "type": "conditional",
      "activation_conditions": {
        "nyha_class": "IV",
        "conditions": ["cardiac_arrest"],
        "reversible_cause": false
      }
    },
    {
      "label": "Accept temporary ventilation if reversible cause",
      "intervention": "temporary_ventilation",
      "negated": false,
      "strength": "Conditional",
      "original_text": "I would accept temporary mechanical ventilation if there is a reversible cause.",
      "type": "conditional",
      "activation_conditions": {
        "reversible_cause": true
      }
    }
  ],
  "extraction_notes": null
}
```

# OUTPUT

Return a single `ExtractedPreferences` object. Include `extraction_notes` only if a judgment call deserves flagging (e.g. an ambiguous phrase you mapped to a specific intervention, an item you deliberately did not extract). When in doubt, prefer fewer preferences with higher confidence over speculative ones."""


# ── Extraction ──────────────────────────────────────────────────────────────


def extract_preferences(
    ad_text: str,
    client: Optional[anthropic.Anthropic] = None,
    *,
    cache_system_prompt: bool = True,
) -> ExtractedPreferences:
    """Extract structured preferences from a free-text advance directive excerpt.

    Args:
        ad_text: The verbatim AD language to extract from.
        client: Optional pre-built Anthropic client. One is created if omitted.
        cache_system_prompt: If True (default), apply ephemeral cache_control to
            the system prompt so repeated extractions reuse the prefix.

    Returns:
        A validated ExtractedPreferences instance.
    """
    if client is None:
        client = anthropic.Anthropic()

    system_block = {"type": "text", "text": SYSTEM_PROMPT}
    if cache_system_prompt:
        system_block["cache_control"] = {"type": "ephemeral"}

    response = client.messages.parse(
        model=MODEL,
        max_tokens=8000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        system=[system_block],
        messages=[{
            "role": "user",
            "content": (
                "Extract structured preferences from the following advance directive text. "
                "Remember: encode only what the patient explicitly stated; preserve original "
                "language verbatim; flag vague phrasing with type='vague'.\n\n"
                f"---\n{ad_text}\n---"
            ),
        }],
        output_format=ExtractedPreferences,
    )

    return response.parsed_output


# ── Conversion to preference_input.py JSON schema ───────────────────────────


def to_patient_json(
    extracted: ExtractedPreferences,
    *,
    patient_id: str = "llm_extracted_001",
    patient_name: str = "LLM-extracted patient",
    source_label: str = "LLM-extracted from free-text AD",
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


# ── Built-in example ────────────────────────────────────────────────────────


EXAMPLE_AD_TEXT = """\
If I have advanced heart failure (NYHA Class IV) and my heart stops with no
reversible cause, I do not want CPR. I would accept being placed on a
breathing machine temporarily if there is a reversible cause and reasonable
hope of recovery, but I do not want to be kept on a ventilator indefinitely.
If I have been on vasopressors for more than three days with no improvement,
I want them withdrawn. If I am ever enrolled in hospice, please deactivate my
implanted defibrillator. I do not want long-term dialysis. I would accept
short-term dialysis if my kidney function is expected to recover. Above all,
no heroic measures if I am dying.
"""


# ── CLI ─────────────────────────────────────────────────────────────────────


def _format_usage(usage) -> str:
    """Human-readable usage / cache summary."""
    parts = [f"input={usage.input_tokens}", f"output={usage.output_tokens}"]
    if getattr(usage, "cache_creation_input_tokens", 0):
        parts.append(f"cache_write={usage.cache_creation_input_tokens}")
    if getattr(usage, "cache_read_input_tokens", 0):
        parts.append(f"cache_read={usage.cache_read_input_tokens}")
    return ", ".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Extract structured AD preferences via Claude.")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--example", action="store_true",
                     help="Use the built-in example AD paragraph.")
    src.add_argument("--text", type=str,
                     help="AD text passed inline.")
    src.add_argument("--file", type=str,
                     help="Path to a text file containing the AD.")
    parser.add_argument("--save", type=str,
                        help="Optional path to write the resulting JSON.")
    parser.add_argument("--patient-id", type=str, default="llm_extracted_001")
    parser.add_argument("--patient-name", type=str, default="LLM-extracted patient")
    parser.add_argument("--no-cache", action="store_true",
                        help="Disable prompt caching on the system prompt.")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    if args.example:
        ad_text = EXAMPLE_AD_TEXT
    elif args.text:
        ad_text = args.text
    else:
        ad_text = Path(args.file).read_text()

    print(f"Model: {MODEL}")
    print(f"Input length: {len(ad_text)} chars")
    print("Extracting…")

    extracted = extract_preferences(ad_text, cache_system_prompt=not args.no_cache)
    print(f"Extracted {len(extracted.preferences)} preference(s).")
    if extracted.extraction_notes:
        print(f"Notes: {extracted.extraction_notes}")

    patient_data = to_patient_json(
        extracted,
        patient_id=args.patient_id,
        patient_name=args.patient_name,
    )

    if args.save:
        Path(args.save).write_text(json.dumps(patient_data, indent=2))
        print(f"Wrote JSON to: {args.save}")
    else:
        print()
        print(json.dumps(patient_data, indent=2))


if __name__ == "__main__":
    main()
