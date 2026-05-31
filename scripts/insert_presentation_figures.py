#!/usr/bin/env python3
"""Insert evaluation figures into ADO_powerpoint_presentation.pptx."""

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches

ROOT = Path(__file__).resolve().parents[1]
PPTX = ROOT / "ADO_powerpoint_presentation.pptx"
FIG = ROOT / "docs" / "presentation_figures"


def insert_on_slide(slide, img_path: Path, left, top, width):
    if img_path.exists():
        slide.shapes.add_picture(str(img_path), left, top, width=width)


def enhance_slide_9(prs: Presentation) -> None:
    slide = prs.slides[8]
    insert_on_slide(slide, FIG / "eval_overview.png", Inches(6.8), Inches(1.35), Inches(6.0))
    insert_on_slide(slide, FIG / "ablation_conditions.png", Inches(6.8), Inches(4.05), Inches(6.0))


def enhance_slide_8(prs: Presentation) -> None:
    slide = prs.slides[7]
    insert_on_slide(slide, FIG / "vignette_match_types.png", Inches(8.5), Inches(1.2), Inches(4.5))


def enhance_slide_10(prs: Presentation) -> None:
    slide = prs.slides[9]
    insert_on_slide(slide, FIG / "conditional_p9_p10.png", Inches(7.2), Inches(1.5), Inches(5.8))


def has_figures_slide(prs: Presentation) -> bool:
    for s in prs.slides:
        for sh in s.shapes:
            if sh.has_text_frame and "EVALUATION FIGURES" in sh.text_frame.text:
                return True
    return False


def add_results_figure_slide(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(12), Inches(0.6))
    title_box.text_frame.text = "EVALUATION FIGURES — Track 3 & code-status fidelity"
    left = FIG / "track3_field_agreement.png"
    right = FIG / "code_status_confusion.png"
    if left.exists():
        slide.shapes.add_picture(str(left), Inches(0.4), Inches(1.0), width=Inches(6.2))
    if right.exists():
        slide.shapes.add_picture(str(right), Inches(6.8), Inches(1.0), width=Inches(6.2))
    cap = slide.shapes.add_textbox(Inches(0.5), Inches(6.6), Inches(12.3), Inches(0.5))
    cap.text_frame.text = (
        "12 real-world template profiles • Gold = POLST semantics • "
        "Diagonal confusion matrix = agreement across all observed code-status categories"
    )


def main():
    if not PPTX.exists():
        raise SystemExit(f"Missing {PPTX}")
    prs = Presentation(str(PPTX))
    enhance_slide_8(prs)
    enhance_slide_9(prs)
    enhance_slide_10(prs)
    if not has_figures_slide(prs):
        add_results_figure_slide(prs)
    prs.save(str(PPTX))
    print(f"Updated {PPTX} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
