"""
ADO Live Demo — Narrated walkthrough of the Advance Directive Ontology reasoner.

Designed for the Magnus expert-review meeting (June 2026). Runs five curated
clinical scenarios against the populated patient ontology and prints, for each:
  - the relevant patient preference (in their own words, via originalText)
  - the clinical scenario in plain English
  - the reasoner's inference path (which activation conditions met / unmet)
  - the 4-category output: Clear / Partial / No coverage / Vague
  - an ethical or clinical note framing what the audience should notice

Usage:
    python demo.py                  # walk through all 5 demo scenarios
    python demo.py --scenario 3     # just one scenario (1-indexed)
    python demo.py --pause          # pause between scenarios (for live demo)
"""

import argparse
import json
import os
import sys
import tempfile
import textwrap
from pathlib import Path

try:
    from owlready2 import get_ontology
except ImportError:
    print("ERROR: owlready2 is not installed. Run: pip install owlready2")
    sys.exit(1)

from query_evaluation import find_matching_preferences, evaluate_vignette


OWL_PATH = Path(__file__).parent / "populated_ontologies" / "ado_jane_doe_001.owl"


# Free-text AD paragraph for Scenario 6. Written to exercise multiple decision
# points and contain a deliberately vague closing line ("no heroic measures").
LLM_DEMO_AD_TEXT = (
    "If I have advanced heart failure (NYHA Class IV) and my heart stops with no "
    "reversible cause, I do not want CPR. I would accept being placed on a "
    "breathing machine temporarily if there is a reversible cause and reasonable "
    "hope of recovery, but I do not want to be kept on a ventilator indefinitely. "
    "If I have been on vasopressors for more than three days with no improvement, "
    "I want them withdrawn. If I am ever enrolled in hospice, please deactivate my "
    "implanted defibrillator. I do not want long-term dialysis. I would accept "
    "short-term dialysis if my kidney function is expected to recover. Above all, "
    "no heroic measures if I am dying."
)


# Five curated demo scenarios, one per output category plus a recent-fix showcase.
DEMO_SCENARIOS = [
    {
        "title": "Clear match — preference fires unambiguously",
        "category": "CLEAR",
        "description": (
            "Jane Doe is in cardiac arrest. She has advanced heart failure (NYHA "
            "Class IV) and no reversible cause has been identified. The code team "
            "is asking whether to attempt CPR."
        ),
        "patient_said": (
            '"If my heart stops and I am in NYHA Class IV with no reversible cause, '
            'do not attempt CPR."'
        ),
        "query_intervention": "CPR",
        "scenario_state": {
            "conditions": ["CardiacArrest"],
            "nyha_class": "NYHA_ClassIV",
            "reversible_cause": False,
        },
        "ethical_note": (
            "The reasoner returns a clear 'no'. All three activation conditions match. "
            "What the system delivers to the clinician is a decision plus an audit trail "
            "of which conditions matched — defensible documentation that this was the "
            "patient's authorized choice for exactly this situation."
        ),
    },
    {
        "title": "Partial match — preference exists but conditions are not met",
        "category": "PARTIAL",
        "description": (
            "Jane is enrolled in the ICU but is NOT in hospice. The cardiology team "
            "is asking whether to deactivate her ICD."
        ),
        "patient_said": '"Deactivate my ICD if I am enrolled in hospice."',
        "query_intervention": "ICDDeactivation",
        "scenario_state": {
            "conditions": [],
            "care_context": "ICUSetting",
        },
        "ethical_note": (
            "This is the case our May 22 ontology fix addresses. Before adding "
            "requiresCareContext, the reasoner treated the preference as unconditional "
            "and returned a false-positive 'yes'. With the fix, the system honestly "
            "reports: 'AD addresses ICD deactivation only in hospice; patient is in "
            "ICU; this AD does not authorize action — escalate to surrogate.'"
        ),
    },
    {
        "title": "No coverage — the AD never addresses this scenario",
        "category": "NO_COVERAGE",
        "description": (
            "Jane is stable, NYHA Class II. A device-team consult asks whether to "
            "deactivate her pacemaker (she has one in addition to her ICD)."
        ),
        "patient_said": "(Jane's AD does not mention pacemaker deactivation.)",
        "query_intervention": "PacemakerDeactivation",
        "scenario_state": {
            "conditions": [],
            "nyha_class": "NYHA_ClassII",
        },
        "ethical_note": (
            "The system honestly reports 'no coverage' rather than fabricating an answer "
            "or defaulting to the nearest related preference (ICD deactivation). This is "
            "the design choice we'd most value Dr. Magnus's input on: does this output "
            "phrasing risk being read as 'no preference, therefore proceed' rather than "
            "'AD does not authorize action, escalate to surrogate'?"
        ),
    },
    {
        "title": "Vague match — preference exists but the language is irreducibly imprecise",
        "category": "VAGUE",
        "description": (
            "Jane has acute respiratory failure. The team is asking whether to start "
            "non-invasive ventilation (BiPAP)."
        ),
        "patient_said": (
            '"If I am dying, I do not want aggressive measures or to be kept alive '
            'by machines."'
        ),
        "query_intervention": "NonInvasiveVentilation",
        "scenario_state": {
            "conditions": ["RespiratoryFailure"],
        },
        "ethical_note": (
            "The system maps the patient's language to NonInvasiveVentilation as the "
            "nearest formal class but flags the match as VAGUE — and surfaces the "
            "patient's original words verbatim. This is the Letter Project-style "
            "design choice: preserve the patient's voice instead of flattening it. "
            "Decision deferred to a human interpreter with full context."
        ),
    },
    {
        "title": "Temporal reasoning — the May 22 SWRL/temporal fix in action",
        "category": "CLEAR",
        "description": (
            "Jane is in cardiogenic shock. She has been on vasopressors for 96 "
            "hours (4 days) with no clinical improvement. The team is asking "
            "whether to withdraw vasopressors."
        ),
        "patient_said": (
            '"If I am on vasopressors with no improvement after 3 days, '
            'withdraw them."'
        ),
        "query_intervention": "VasopressorWithdrawal",
        "scenario_state": {
            "conditions": ["CardiogenicShock"],
            "time_elapsed": "96 hours",
        },
        "ethical_note": (
            "Before May 22, time bounds were stored as natural-language strings the "
            "reasoner could not evaluate — V10 returned a partial match. With "
            "hasTimeBoundHours (xsd:int), the reasoner now compares 96h >= 72h "
            "directly. This is one of three SWRL-ready improvements (care-context, "
            "temporal, negation-aware classification) called out in the progress report."
        ),
    },
]


# Scenario 6 is structured differently — it runs the full pipeline from
# free-text AD → LLM extraction → populated ontology → reasoner. It's defined
# separately because it needs to do its own ontology population at demo time.
LLM_PIPELINE_SCENARIO = {
    "title": "Full pipeline — free-text AD → LLM extraction → ontology → reasoner",
    "category": "PIPELINE",
    "description": (
        "We hand Claude a verbatim paragraph from an advance directive. "
        "Claude (claude-opus-4-7, structured output) converts it into the "
        "same JSON schema preference_input.py accepts. We pipe that JSON "
        "into the existing pipeline, populate a fresh ontology, and ask the "
        "reasoner: 'Should we attempt CPR for this patient in cardiac arrest "
        "at NYHA IV?'"
    ),
    "query_intervention": "CPR",
    "scenario_state": {
        # Realistic clinical scenario for a NYHA IV cardiac-arrest patient with HF.
        # AdvancedHeartFailure is part of the baseline state, not just a discovery
        # mid-code. The LLM faithfully encodes the patient's "if I have advanced
        # heart failure" qualifier as a separate activation condition, so the
        # scenario must reflect that same condition explicitly.
        "conditions": ["CardiacArrest", "AdvancedHeartFailure"],
        "nyha_class": "NYHA_ClassIV",
        "reversible_cause": False,
    },
    "ethical_note": (
        "The positioning we want Dr. Magnus to leave with: this project is not "
        "ontology vs. LLM, but ontology WITH LLMs at the boundaries. The LLM "
        "extracts; the ontology is the auditable, closed-world source of "
        "truth; the reasoner produces the defensible 4-category output. The "
        "system prompt instructs the LLM to encode ONLY what the patient said "
        "— never to extrapolate — because the reasoner's 'no coverage' "
        "behavior depends entirely on that discipline."
    ),
}


# ── ANSI styling for readable terminal output ───────────────────────────────
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
RED = "\033[31m"

CATEGORY_COLOR = {
    "CLEAR": GREEN,
    "PARTIAL": YELLOW,
    "NO_COVERAGE": CYAN,
    "VAGUE": MAGENTA,
}


def hr(char="─", width=80, color=DIM):
    return f"{color}{char * width}{RESET}"


def banner():
    print()
    print(hr("═"))
    print(f"{BOLD}  Advance Directive Ontology (ADO) — Live Reasoner Demo{RESET}")
    print(f"  Computable end-of-life preferences for advanced heart failure")
    print(f"  Patrick Walsh & Darren Chan  |  CS 270 / BMDS 210  |  Spring 2026")
    print(hr("═"))


def print_scenario_header(idx, total, scenario):
    color = CATEGORY_COLOR.get(scenario["category"], "")
    print()
    print(hr("━"))
    print(f"  {BOLD}Scenario {idx} of {total}: {scenario['title']}{RESET}")
    print(f"  Expected output category: {color}{BOLD}{scenario['category']}{RESET}")
    print(hr("━"))


def _wrap_indented(text, indent="    ", width=80):
    """Wrap `text` so each line fits in `width` chars including `indent`."""
    for line in textwrap.wrap(text, width=width - len(indent)) or [""]:
        print(f"{indent}{line}")


def run_llm_pipeline_scenario(idx, total, scenario, pause):
    """Scenario 6: end-to-end free-text → LLM → ontology → reasoner pipeline."""
    color = CATEGORY_COLOR.get(scenario["category"], MAGENTA)
    print()
    print(hr("━"))
    print(f"  {BOLD}Scenario {idx} of {total}: {scenario['title']}{RESET}")
    print(f"  Pipeline category: {color}{BOLD}{scenario['category']}{RESET}")
    print(hr("━"))

    print(f"\n  {BOLD}What we're showing:{RESET}")
    _wrap_indented(scenario["description"])

    print(f"\n  {BOLD}Verbatim AD paragraph (the LLM's input):{RESET}")
    for line in textwrap.wrap(LLM_DEMO_AD_TEXT, width=76):
        print(f"    {DIM}{line}{RESET}")

    # Guarded import — if anthropic or pydantic aren't installed, or the API key
    # is missing, we want a clean fallback rather than crashing the demo.
    extraction_failure = None
    extracted_json = None
    if not os.environ.get("ANTHROPIC_API_KEY"):
        extraction_failure = (
            "ANTHROPIC_API_KEY is not set. Skipping live extraction. "
            "To run the live LLM step: export ANTHROPIC_API_KEY=sk-ant-... "
            "then re-run `python demo.py --scenario 6`."
        )
    else:
        try:
            from llm_extraction import extract_preferences, to_patient_json
            print(f"\n  {BOLD}Extracting with Claude (claude-opus-4-7)…{RESET}")
            extracted = extract_preferences(LLM_DEMO_AD_TEXT)
            extracted_json = to_patient_json(
                extracted,
                patient_id="demo_llm_001",
                patient_name="Demo (LLM-extracted)",
                source_label="LLM-extracted from free-text AD",
            )
        except Exception as exc:
            extraction_failure = f"Live extraction failed: {exc}"

    if extraction_failure:
        print(f"\n  {YELLOW}{BOLD}[Live extraction skipped]{RESET} {YELLOW}{extraction_failure}{RESET}")
        print(f"  {DIM}Falling back to the hand-coded example patient so the rest of the demo runs.{RESET}")
        # Fall back: reload the existing populated ontology so we can still show
        # the reasoner output. This is a graceful degradation, not the demo.
        onto = get_ontology(str(OWL_PATH.resolve())).load()
        patients = list(onto.search(type=onto.Patient))
        patient = max(patients, key=lambda p: len(p.hasPreference) if p.hasPreference else 0)
        scenario_source_label = "FALLBACK (hand-coded ontology)"
    else:
        print(f"\n  {BOLD}LLM extracted {len(extracted_json['preferences'])} preferences:{RESET}")
        for i, p in enumerate(extracted_json["preferences"], 1):
            neg = " (negated)" if p["negated"] else ""
            print(f"    {i}. {GREEN}{p['intervention']}{RESET}{neg}  "
                  f"strength={p['strength']}  type={p['type']}")
            _wrap_indented(f'"{p["original_text"]}"', indent="       ", width=80)

        # Populate a brand-new ontology from the LLM output and run the query.
        from preference_input import load_ontology, populate_patient
        print(f"\n  {BOLD}Piping JSON into populate_patient() → fresh OWL ontology…{RESET}")
        onto = load_ontology()
        with onto:
            patient = populate_patient(onto, extracted_json)
        # Persist to a temp file so future demo runs can inspect it if curious.
        out_path = Path(__file__).parent / "populated_ontologies" / "ado_demo_llm_001.owl"
        out_path.parent.mkdir(exist_ok=True)
        onto.save(file=str(out_path.resolve()), format="rdfxml")
        print(f"    Wrote populated ontology to: {out_path}")
        scenario_source_label = "LLM-extracted ontology"

    # Now query the reasoner — same code path as Scenarios 1-5.
    print(f"\n  {BOLD}Clinical scenario put to the reasoner:{RESET}")
    print("    \"Patient is in cardiac arrest, NYHA IV, no reversible cause.")
    print("     Should CPR be attempted?\"")

    fake_vignette = {
        "id": f"demo_{idx}",
        "description": scenario["description"],
        "query_intervention": scenario["query_intervention"],
        "scenario_state": scenario["scenario_state"],
        "expected": {"decision": "(demo)", "match_type": "(demo)", "reasoning": ""},
    }
    result = evaluate_vignette(onto, patient, fake_vignette)

    decision_color = CATEGORY_COLOR.get(result["system_match_type"].upper(), "")
    print(f"\n  {BOLD}Reasoner output (over {scenario_source_label}):{RESET}")
    print(f"    Decision     : {decision_color}{BOLD}{result['system_decision']}{RESET}")
    print(f"    Match type   : {decision_color}{BOLD}{result['system_match_type']}{RESET}")
    print(f"    Inference    : {result['detail']}")

    print(f"\n  {BOLD}What to notice:{RESET}")
    _wrap_indented(scenario["ethical_note"])

    if pause:
        print()
        input(f"  {DIM}[Enter] to continue …{RESET}")


def run_scenario(onto, patient, idx, total, scenario, pause):
    print_scenario_header(idx, total, scenario)

    print(f"\n  {BOLD}Clinical scenario:{RESET}")
    print(f"    {scenario['description']}")

    print(f"\n  {BOLD}What the patient said (verbatim from their AD):{RESET}")
    print(f"    {DIM}{scenario['patient_said']}{RESET}")

    print(f"\n  {BOLD}Question asked of the reasoner:{RESET}")
    print(f"    \"Should we proceed with {scenario['query_intervention']}?\"")

    # Run the reasoner
    fake_vignette = {
        "id": f"demo_{idx}",
        "description": scenario["description"],
        "query_intervention": scenario["query_intervention"],
        "scenario_state": scenario["scenario_state"],
        "expected": {
            "decision": "(demo)",
            "match_type": "(demo)",
            "reasoning": "",
        },
    }
    result = evaluate_vignette(onto, patient, fake_vignette)

    color = CATEGORY_COLOR.get(scenario["category"], "")
    print(f"\n  {BOLD}Reasoner output:{RESET}")
    print(f"    Decision     : {color}{BOLD}{result['system_decision']}{RESET}")
    print(f"    Match type   : {color}{BOLD}{result['system_match_type']}{RESET}")
    print(f"    Inference    : {result['detail']}")

    print(f"\n  {BOLD}What to notice:{RESET}")
    # Wrap the ethical note to ~76 chars per line
    note = scenario["ethical_note"]
    line = "    "
    for word in note.split():
        if len(line) + len(word) + 1 > 80:
            print(line)
            line = "    " + word
        else:
            line = f"{line} {word}" if line.strip() else "    " + word
    if line.strip():
        print(line)

    if pause:
        print()
        input(f"  {DIM}[Enter] to continue …{RESET}")


def main():
    parser = argparse.ArgumentParser(description="ADO live demo")
    parser.add_argument("--scenario", type=int, default=None,
                        help="Run only the given 1-indexed demo scenario (1-5).")
    parser.add_argument("--pause", action="store_true",
                        help="Pause between scenarios (useful for live demo).")
    parser.add_argument("--owl", type=str, default=str(OWL_PATH),
                        help="Path to populated ontology (default: example).")
    args = parser.parse_args()

    owl_path = Path(args.owl)
    if not owl_path.exists():
        print(f"{RED}ERROR{RESET}: populated ontology not found at {owl_path}")
        print("       Run: python preference_input.py --example")
        sys.exit(1)

    banner()
    print(f"\n  Loading populated ontology: {owl_path}")
    onto = get_ontology(str(owl_path.resolve())).load()
    patients = list(onto.search(type=onto.Patient))
    if not patients:
        print(f"{RED}ERROR{RESET}: no Patient individuals found.")
        sys.exit(1)
    patient = max(patients, key=lambda p: len(p.hasPreference) if p.hasPreference else 0)
    name = patient.label[0] if patient.label else patient.name
    print(f"  Patient: {BOLD}{name}{RESET} ({len(patient.hasPreference)} encoded preferences)")

    total_scenarios = len(DEMO_SCENARIOS) + 1  # +1 for LLM pipeline scenario
    if args.scenario is not None:
        if not (1 <= args.scenario <= total_scenarios):
            print(f"{RED}ERROR{RESET}: --scenario must be 1..{total_scenarios}")
            sys.exit(1)
        if args.scenario <= len(DEMO_SCENARIOS):
            run_scenario(onto, patient, args.scenario, total_scenarios,
                         DEMO_SCENARIOS[args.scenario - 1], pause=False)
        else:
            run_llm_pipeline_scenario(args.scenario, total_scenarios,
                                      LLM_PIPELINE_SCENARIO, pause=False)
    else:
        for i, sc in enumerate(DEMO_SCENARIOS, 1):
            run_scenario(onto, patient, i, total_scenarios, sc, pause=args.pause)
        run_llm_pipeline_scenario(total_scenarios, total_scenarios,
                                  LLM_PIPELINE_SCENARIO, pause=args.pause)

    print()
    print(hr("═"))
    print(f"  {BOLD}Demo complete.{RESET}")
    print(f"  All four output categories demonstrated, plus a full free-text → LLM → ontology → reasoner pass.")
    print(f"  Repository: https://github.com/patrickwalsh26/bmds210-AD_Ontology")
    print(hr("═"))
    print()


if __name__ == "__main__":
    main()
