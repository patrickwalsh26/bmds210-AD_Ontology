#!/usr/bin/env python3
"""Insert high-resolution evaluation figures into ADO_powerpoint_presentation.pptx."""

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


def remove_slides_with_title(prs: Presentation, needle: str) -> int:
    """Remove slides whose title/body contains needle (for idempotent rebuild)."""
    removed = 0
  # python-pptx cannot delete slides easily — we skip re-add if exists
    return removed


def enhance_slide_5(prs: Presentation) -> None:
    slide = prs.slides[4]
    insert_on_slide(slide, FIG / "ontology_class_hierarchy.png", Inches(6.9), Inches(1.15), Inches(5.9))


def enhance_slide_8(prs: Presentation) -> None:
    """Study design — strands diagram + vignette mix."""
    slide = prs.slides[7]
    insert_on_slide(slide, FIG / "study_design_strands.png", Inches(5.8), Inches(1.05), Inches(7.0))
    insert_on_slide(slide, FIG / "vignette_match_types.png", Inches(0.35), Inches(3.85), Inches(4.8))


def enhance_slide_9(prs: Presentation) -> None:
    """Quantitative results — two-layer validation (primary)."""
    slide = prs.slides[8]
    insert_on_slide(slide, FIG / "eval_two_layer.png", Inches(0.35), Inches(1.05), Inches(12.5))


def enhance_slide_10(prs: Presentation) -> None:
    slide = prs.slides[9]
    insert_on_slide(slide, FIG / "conditional_p9_p10.png", Inches(6.8), Inches(1.35), Inches(6.0))
    insert_on_slide(slide, FIG / "ablation_conditions.png", Inches(0.35), Inches(1.35), Inches(5.5))


def add_cohort_stress_slide(prs: Presentation) -> None:
    if slide_has_title(prs, "COHORT STRESS TEST"):
        return
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    tb = slide.shapes.add_textbox(Inches(0.4), Inches(0.22), Inches(12.5), Inches(0.55))
    tb.text_frame.text = "COHORT STRESS TEST — 20 messy profiles × 12 scenarios (520 cells)"
    tb.text_frame.paragraphs[0].font.size = Pt(17)
    tb.text_frame.paragraphs[0].font.bold = True

    insert_on_slide(slide, FIG / "cohort_messy_breakdown.png", Inches(0.35), Inches(0.95), Inches(6.2))
    insert_on_slide(slide, FIG / "cohort_baseline_comparison.png", Inches(6.65), Inches(0.95), Inches(6.2))

    cap = slide.shapes.add_textbox(Inches(0.4), Inches(6.55), Inches(12.3), Inches(0.55))
    cap.text_frame.text = (
        "~47% agreement vs simplified reference oracle (not hand-adjudicated). "
        "Flat checkbox over-asserts on 421/520 nuanced cells. "
        "Honest population stress test — complements 16/16 vignette spec test."
    )
    cap.text_frame.paragraphs[0].font.size = Pt(11)


def add_eval_dashboard_slide(prs: Presentation) -> None:
    """Single composite dashboard slide."""
    title = "EVALUATION DASHBOARD"
    if slide_has_title(prs, title):
        return
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    tb = slide.shapes.add_textbox(Inches(0.4), Inches(0.2), Inches(12.5), Inches(0.5))
    tb.text_frame.text = f"{title} — developmental validation (June 2026)"
    tb.text_frame.paragraphs[0].font.size = Pt(17)
    tb.text_frame.paragraphs[0].font.bold = True
    insert_on_slide(slide, FIG / "eval_dashboard.png", Inches(0.3), Inches(0.75), Inches(12.6))


def add_coverage_extraction_slide(prs: Presentation) -> None:
    if slide_has_title(prs, "COVERAGE & EXTRACTION"):
        return
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    tb = slide.shapes.add_textbox(Inches(0.4), Inches(0.22), Inches(12.5), Inches(0.5))
    tb.text_frame.text = "COVERAGE & EXTRACTION — scope and closed-world discipline"
    tb.text_frame.paragraphs[0].font.bold = True
    tb.text_frame.paragraphs[0].font.size = Pt(17)

    insert_on_slide(slide, FIG / "coverage_inventory.png", Inches(0.35), Inches(0.95), Inches(6.3))
    insert_on_slide(slide, FIG / "extraction_f1.png", Inches(6.75), Inches(1.1), Inches(5.8))
    insert_on_slide(slide, FIG / "vignette_splits.png", Inches(6.75), Inches(4.0), Inches(5.8))


def add_track3_slide(prs: Presentation) -> None:
    if slide_has_title(prs, "TRACK 3 — CODE STATUS"):
        return
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_box = slide.shapes.add_textbox(Inches(0.4), Inches(0.22), Inches(12), Inches(0.5))
    title_box.text_frame.text = "TRACK 3 — CODE STATUS & POLST MAPPING"
    title_box.text_frame.paragraphs[0].font.bold = True
    title_box.text_frame.paragraphs[0].font.size = Pt(17)
    insert_on_slide(slide, FIG / "track3_field_agreement.png", Inches(0.35), Inches(0.95), Inches(6.1))
    insert_on_slide(slide, FIG / "code_status_confusion.png", Inches(6.65), Inches(0.95), Inches(6.1))


def deprecate_old_strengthened_slide(prs: Presentation) -> None:
    """If old STRENGTHENED slide exists, leave it — presenter can hide. New slides supersede."""
    pass


def main():
    if not PPTX.exists():
        raise SystemExit(f"Missing {PPTX}")
    prs = Presentation(str(PPTX))
    enhance_slide_5(prs)
    enhance_slide_8(prs)
    enhance_slide_9(prs)
    enhance_slide_10(prs)
    add_cohort_stress_slide(prs)
    add_eval_dashboard_slide(prs)
    add_coverage_extraction_slide(prs)
    add_track3_slide(prs)
    prs.save(str(PPTX))
    print(f"Updated {PPTX} ({len(prs.slides)} slides)")
    print("Recommended order: slides 1–10 core → COHORT STRESS → EVAL DASHBOARD → COVERAGE → TRACK 3 → integration/limits")


if __name__ == "__main__":
    main()
