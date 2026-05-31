#!/usr/bin/env python3
"""Insert evaluation figures into ADO_powerpoint_presentation.pptx."""

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
PPTX = ROOT / "ADO_powerpoint_presentation.pptx"
FIG = ROOT / "docs" / "presentation_figures"


def insert_on_slide(slide, img_path: Path, left, top, width):
    if img_path.exists():
        slide.shapes.add_picture(str(img_path), left, top, width=width)


def slide_has_title(prs, needle: str) -> bool:
    for s in prs.slides:
        for sh in s.shapes:
            if sh.has_text_frame and needle in sh.text_frame.text:
                return True
    return False


def enhance_slide_5(prs: Presentation) -> None:
    slide = prs.slides[4]
    insert_on_slide(slide, FIG / "ontology_class_hierarchy.png", Inches(6.9), Inches(1.15), Inches(5.9))


def enhance_slide_8(prs: Presentation) -> None:
    slide = prs.slides[7]
    insert_on_slide(slide, FIG / "vignette_match_types.png", Inches(8.2), Inches(1.15), Inches(4.3))


def enhance_slide_9(prs: Presentation) -> None:
    slide = prs.slides[8]
    insert_on_slide(slide, FIG / "eval_overview.png", Inches(6.7), Inches(1.2), Inches(6.1))
    insert_on_slide(slide, FIG / "ablation_conditions.png", Inches(6.7), Inches(3.95), Inches(6.1))


def enhance_slide_10(prs: Presentation) -> None:
    slide = prs.slides[9]
    insert_on_slide(slide, FIG / "conditional_p9_p10.png", Inches(7.0), Inches(1.45), Inches(5.9))


def add_strengthened_eval_slide(prs: Presentation) -> None:
    """One slide: coverage + ablation + vignette splits + extraction (for tomorrow)."""
    if slide_has_title(prs, "STRENGTHENED EVALUATION"):
        return
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    tb = slide.shapes.add_textbox(Inches(0.4), Inches(0.25), Inches(12.5), Inches(0.55))
    tb.text_frame.text = "STRENGTHENED EVALUATION — developmental validation (report / June 2026)"
    p = tb.text_frame.paragraphs[0]
    p.font.size = Pt(18)
    p.font.bold = True

    panels = [
        (FIG / "vignette_splits.png", Inches(0.35), Inches(0.95), Inches(3.05)),
        (FIG / "ablation_conditions.png", Inches(3.45), Inches(0.95), Inches(3.05)),
        (FIG / "coverage_inventory.png", Inches(6.55), Inches(0.95), Inches(6.0)),
        (FIG / "extraction_f1.png", Inches(0.35), Inches(4.05), Inches(3.05)),
        (FIG / "track3_field_agreement.png", Inches(3.45), Inches(4.05), Inches(3.05)),
        (FIG / "code_status_confusion.png", Inches(6.55), Inches(4.05), Inches(6.0)),
    ]
    for path, left, top, width in panels:
        insert_on_slide(slide, path, left, top, width)

    cap = slide.shapes.add_textbox(Inches(0.4), Inches(6.75), Inches(12.3), Inches(0.45))
    cap.text_frame.text = (
        "Developmental validation — not clinical trial. Team gold; single patient ontology. "
        "Lead with ablation (69%) + coverage (47% fully representable), not only 100% vignettes."
    )


def add_track3_slide(prs: Presentation) -> None:
    if slide_has_title(prs, "EVALUATION FIGURES — Track 3"):
        return
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(12), Inches(0.6))
    title_box.text_frame.text = "EVALUATION FIGURES — Track 3 & code-status fidelity"
    insert_on_slide(slide, FIG / "track3_field_agreement.png", Inches(0.4), Inches(1.0), Inches(6.2))
    insert_on_slide(slide, FIG / "code_status_confusion.png", Inches(6.8), Inches(1.0), Inches(6.2))


def main():
    if not PPTX.exists():
        raise SystemExit(f"Missing {PPTX}")
    prs = Presentation(str(PPTX))
    enhance_slide_5(prs)
    enhance_slide_8(prs)
    enhance_slide_9(prs)
    enhance_slide_10(prs)
    add_strengthened_eval_slide(prs)
    if not slide_has_title(prs, "EVALUATION FIGURES — Track 3"):
        add_track3_slide(prs)
    prs.save(str(PPTX))
    print(f"Updated {PPTX} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
