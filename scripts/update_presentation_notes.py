#!/usr/bin/env python3
"""Embed cohesive narrative speaker notes in ADO_powerpoint_presentation.pptx."""

from pathlib import Path

from pptx import Presentation
from pptx.util import Pt

ROOT = Path(__file__).resolve().parents[1]
PPTX = ROOT / "ADO_powerpoint_presentation.pptx"

# Core slides 1–13 (0-indexed 0–12) + appended evaluation slides
NOTES = [
    """NARRATIVE: Act I — frame the talk.
SAY: Patrick Walsh & Darren Chan. ADO = computable EOL preferences in advanced HF. Not a legal AD.
TRANSITION: "Start at the 2 a.m. crisis."
[~25s]""",

    """NARRATIVE: Act I — three instruments, translation loss.
SAY: AD → POLST → code status. Conditional wishes → coarse boxes. Low resolution + disease blindness.
TRANSITION: "HF is where that hurts most."
[~45s]""",

    """NARRATIVE: Act I — why HF scope.
SAY: Five decision points. ICD/LVAD/inotropes missing from generic templates.
TRANSITION: "Smallest object that preserves patient logic?"
[~35s]""",

    """NARRATIVE: Act II — PreferenceStatement.
SAY: Intervention + activation + strength + negation + verbatim. Walk 72h vasopressor example.
TRANSITION: "How much structure we built."
[~45s]""",

    """NARRATIVE: Act II — ontology credibility.
SAY: 67 classes, 22 properties, 21 interventions. POINT AT hierarchy figure.
OPTIONAL LIVE: Protégé — ado_jane_doe_001.owl
TRANSITION: "Know when NOT to answer."
[~35s]""",

    """NARRATIVE: Act II — four honest outputs.
SAY: Clear / Partial / No coverage / Vague. Can't say "I don't know" = safety failure.
TRANSITION: "Pipeline wiring."
[~40s]""",

    """NARRATIVE: Act II — architecture.
SAY: LLMs extract ONLY. Ontology = truth. Reasoner decides. Closed-world extraction.
TRANSITION: "Six evaluation strands including 520-cell cohort."
[~45s]""",

    """NARRATIVE: Act III — study design (six strands).
SAY: Vignettes 16+10 held-out; ablation; cohort 520 cells (20×12); extraction n=12; POLST n=12; coverage 30 clauses. Developmental — not clinical trial.
POINT AT: study_design_strands.png
TRANSITION: "Two-layer validation."
[~50s]""",

    """NARRATIVE: Act III — MAIN RESULTS (two-layer).
SAY: Layer 1: 16/16 dev, 10/10 held-out, 69% ablation — spec test on Jane Doe. Layer 2: cohort ~47% vs simplified oracle; checkbox fails nuanced cells. Also F1 0.97, 35/36 POLST.
POINT AT: eval_two_layer.png (full slide). DO NOT oversell 100%.
TRANSITION: "Conditionality + cohort detail."
[~60s]""",

    """NARRATIVE: Ablation + conditional aha.
SAY: Ablation 11/16 (69%) — activation conditions matter. P9/P10: DNR vs Full code same directive.
POINT AT: ablation_conditions.png, conditional_p9_p10.png
TRANSITION: "Cohort stress test."
[~45s]""",

    """NARRATIVE: Magnus reframe (if slide order = integration before cohort, adjust).
SAY: ACP progress note. Directive → ADO → conversation → POLST.
[~40s]""",

    """NARRATIVE: Limits.
SAY: No legal force; cohort oracle not clinical gold; team gold; EHR future.
TRANSITION: "Takeaways."
[~40s]""",

    """NARRATIVE: Close.
SAY: Four bullets. Repo. Questions. Optional demo scenario 1.
[~25s]""",
]

# Notes for slides appended by insert_presentation_figures.py (match by title)
APPENDED_NOTES = {
    "COHORT STRESS TEST": """NARRATIVE: Cohort honesty slide.
SAY: 20 profiles (messy_level tags) × 12 scenarios = 520 cells. ~47% vs simplified oracle. 421/520 checkbox overconfident. Clean > minimal/contradictory.
POINT AT: cohort_messy_breakdown.png, cohort_baseline_comparison.png
[~50s]""",

    "EVALUATION DASHBOARD": """NARRATIVE: Backup all-in-one numbers.
SAY: Walk six panels if asked for full summary. Optional — skip if short on time.
[~20s]""",

    "COVERAGE & EXTRACTION": """NARRATIVE: Scope + extraction discipline.
SAY: 47% fully representable (14/30). F1 0.97, 0 OOS hallucinations on nutrition/antibiotics.
POINT AT: coverage_inventory.png, extraction_f1.png
[~35s]""",

    "TRACK 3": """NARRATIVE: Bedside mapping.
SAY: 35/36 fields. P5 principled divergence. Confusion matrix diagonal.
POINT AT: track3_field_agreement.png, code_status_confusion.png
[~35s]""",

    "STRENGTHENED EVALUATION": """(Legacy slide — prefer COHORT + DASHBOARD slides.)
SAY: Lead with ablation 69% and cohort 47%, not only 100% vignettes.
[~30s]""",
}


def set_notes(prs: Presentation) -> None:
    for i, slide in enumerate(prs.slides):
        if i < len(NOTES):
            text = NOTES[i]
        else:
            text = None
            for sh in slide.shapes:
                if sh.has_text_frame:
                    for needle, note in APPENDED_NOTES.items():
                        if needle in sh.text_frame.text:
                            text = note
                            break
                if text:
                    break
            if not text:
                continue
        tf = slide.notes_slide.notes_text_frame
        tf.clear()
        tf.text = text


def update_slide_9_metrics(prs: Presentation) -> None:
    if len(prs.slides) < 9:
        return
    slide = prs.slides[8]
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        t = shape.text_frame.text.strip()
        if t.startswith("κ=1.00") and "/" not in t:
            shape.text_frame.text = "κ=1.00 / 1.00 / 0.88"
        if "75%" in t or "75 %" in t:
            shape.text_frame.text = t.replace("75%", "69%").replace("75 %", "69%")


def main() -> None:
    if not PPTX.exists():
        raise SystemExit(f"Missing {PPTX}")
    prs = Presentation(str(PPTX))
    set_notes(prs)
    update_slide_9_metrics(prs)
    prs.save(str(PPTX))
    print(f"Updated speaker notes in {PPTX} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
