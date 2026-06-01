# Documentation index

Navigation for the **Advance Directive Ontology (ADO)** repository. Start with the [root README](../README.md) for setup and commands.

---

## Evaluation & results

| Document | Description |
|----------|-------------|
| [Honest Evaluation Report](Honest_Evaluation_Report.md) | **Primary results narrative** — what we claim, cohort stress test, limitations |
| [Quantitative Evaluation Plan](Quantitative_Evaluation_Plan.md) | Tracks 1–3 design, metrics, and recorded numbers |
| [Evaluation Roadmap](Evaluation_Roadmap.md) | Completed vs. planned validation steps |
| [evaluation_results_summary.md](evaluation_results_summary.md) | Auto-generated output of `python evaluation_suite.py` |
| [cohort_simulation_results.json](cohort_simulation_results.json) | Machine-readable cohort simulation summary |

**Figures:** [presentation_figures/](presentation_figures/) · Captions: [FIGURE_CAPTIONS.md](presentation_figures/FIGURE_CAPTIONS.md) · Slide map: [PPT_Figures_Guide.md](PPT_Figures_Guide.md)

---

## Presentations & demos

| Document | Description |
|----------|-------------|
| [Presentation Speaker Notes](Presentation_Speaker_Notes.md) | June 2026 talk script (~9 min) |
| [Live Demo Guide](Live_Demo_Guide.md) | Terminal `demo.py` walkthrough |
| [Protégé Showcase Guide](Protege_Showcase_Guide.md) | Ontology browser live demo |

Root deck: `ADO_powerpoint_presentation.pptx` (regenerate via `scripts/build_presentation_assets.sh`).

---

## Architecture & design

| Document | Description |
|----------|-------------|
| [project_pipeline.md](project_pipeline.md) | End-to-end pipeline, design decisions, evaluation history |
| [Advanced Directive Concept Inventory](Advanced_Directive_Concept_Inventory.md) | 50 real-world template families (scope analysis) |

---

## Reports (course / submission)

| Document | Format |
|----------|--------|
| [Final_Report.tex](Final_Report.tex) | LaTeX — AMIA-style final report |
| [Presentation.tex](Presentation.tex) | LaTeX Beamer |
| [Progress_Report.tex](Progress_Report.tex) | Earlier progress report |
| [Progress_Report.md](Progress_Report.md) | Markdown progress notes |

Prebuilt PDFs: `Final_Report.pdf`, `Presentation.pdf` (if present in clone).

---

## Expert review (Magnus)

| Document | Description |
|----------|-------------|
| [Magnus_Expert_Review_2026-05-27.md](Magnus_Expert_Review_2026-05-27.md) | Written expert feedback |
| [Magnus_Meeting_Notes.md](Magnus_Meeting_Notes.md) | Meeting synthesis |
| [Magnus_Review_Packet.tex](Magnus_Review_Packet.tex) | Short review packet |

---

## Archive & reference materials

| Location | Contents |
|----------|----------|
| [archive/](archive/) | Superseded drafts, templates, one-off build scripts |
| [../reference_ads/](../reference_ads/) | Source advance directive PDFs |
| [../gold_annotations/](../gold_annotations/) | Track 2 dual-annotation JSON templates |

---

## Regenerating assets

```bash
python evaluation_suite.py
python realistic_simulation.py --json docs/cohort_simulation_results.json
./scripts/build_presentation_assets.sh
```
