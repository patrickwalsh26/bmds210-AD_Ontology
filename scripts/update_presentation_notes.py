#!/usr/bin/env python3
"""Embed cohesive narrative speaker notes in ADO_powerpoint_presentation.pptx."""

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
PPTX = ROOT / "ADO_powerpoint_presentation.pptx"

# Synced with docs/Presentation_Speaker_Notes.md — narrative arc in header of each note.
NOTES = [
    """NARRATIVE: Act I opens — frame the talk.
SAY: Patrick Walsh & Darren Chan. ADO = computable EOL preferences in advanced HF. Not a legal AD — decision support for ACP documentation.
TRANSITION: "Start where clinicians live—the 2 a.m. crisis."
[~25s]""",

    """NARRATIVE: Act I — three instruments, translation loss.
SAY: AD → POLST → code status. Loss = conditional wishes → coarse boxes. "Free text" cliché is half wrong—CA/UC forms are checkboxes. Real problem: low resolution + disease blindness.
POINT AT: ventilator example on slide.
TRANSITION: "HF is where that blindness hurts most."
[~45s]""",

    """NARRATIVE: Act I — why HF scope.
SAY: Unpredictable, device-heavy, repeated ED/ICU visits. Five decision points. ICD/LVAD/inotropes missing from generic templates.
TRANSITION: "What's the smallest object that preserves patient logic?"
[~35s]""",

    """NARRATIVE: Act II begins — PreferenceStatement.
SAY: Intervention + activation conditions + strength + negation + verbatim text. Reasoner asks: does this apply in THIS scenario? Walk 72h vasopressor example.
TRANSITION: "How much structure we built around that."
[~45s]""",

    """NARRATIVE: Act II — ontology credibility.
SAY: 67 classes, 22 properties, 21 interventions—finer than our 50-form inventory. SNOMED where possible.
TRANSITION: "Granularity only helps if we know when NOT to answer."
[~35s]""",

    """NARRATIVE: Act II — safety thesis (four honest outputs).
SAY: Clear / Partial / No coverage / Vague. Punchline: checkbox or LLM can't say "I don't know." ADO can.
TRANSITION: "How we wired that into a pipeline."
[~40s]""",

    """NARRATIVE: Act II — architecture.
SAY: LLMs extract ONLY. Ontology = auditable truth. Reasoner decides. Closed-world: out-of-scope → extract nothing. Tagline: WITH LLMs, not vs.
OPTIONAL: "We can demo scenario 1 live after results."
TRANSITION: "We tested that three ways."
[~45s]""",

    """NARRATIVE: Act III — earn trust before numbers.
SAY: 5 evaluation strands on slide. Caveat: team gold, grounded in real templates + POLST semantics. Ablation = same 16 vignettes without conditions → 75%.
POINT AT: vignette pie chart (if visible).
TRANSITION: "Here's what we found."
[~45s]""",

    """NARRATIVE: Act III — flagship results.
SAY: Track 1: 16/16. Track 2: F1 0.97, 0 hallucinations on nutrition/antibiotics. Track 3: 35/36 (97%), κ 1.00/1.00/0.88. Ablation: 75% without conditions = 4 false-confident conditional errors.
POINT AT: bar charts on right of slide.
TRANSITION: "One profile pair shows the clinical payoff."
[~55s]""",

    """NARRATIVE: Act III — clinical "aha."
SAY: Same directive, two scenarios → DNR vs Full code. Flat POLST can't carry if/then.
POINT AT: P9/P10 figure if on slide.
TRANSITION: "An ethicist placed this in workflow."
[~40s]""",

    """NARRATIVE: Act IV — Magnus reframe.
SAY: Not a signed AHCD — ACP progress note. Directive → ADO → ACP pre-pop → conversation → POLST/code status.
TRANSITION: "What we didn't solve."
[~40s]""",

    """NARRATIVE: Act IV — limits without retreating.
SAY: No legal force; one-dimensional (who-decides next); coverage gaps; team gold; EHR validation future.
TRANSITION: "Four takeaways."
[~35s]""",

    """NARRATIVE: Close.
SAY: Read four bullets. Repo URL. Questions welcome.
OFFER: "Happy to run demo scenario 1 live."
[~25s]""",
]


def set_notes(prs: Presentation) -> None:
    for i, slide in enumerate(prs.slides):
        if i >= len(NOTES):
            break
        tf = slide.notes_slide.notes_text_frame
        tf.clear()
        tf.text = NOTES[i]


def update_slide_9_metrics(prs: Presentation) -> None:
    slide = prs.slides[8]
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        t = shape.text_frame.text.strip()
        if t == "κ=1.00" or t.startswith("κ=1.00"):
            shape.text_frame.text = "κ=1.00 / 1.00 / 0.88"
        elif t == "code status + POLST A":
            shape.text_frame.text = "code / POLST A / POLST B"


def main() -> None:
    prs = Presentation(str(PPTX))
    set_notes(prs)
    update_slide_9_metrics(prs)
    prs.save(str(PPTX))
    print(f"Updated speaker notes in {PPTX} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
