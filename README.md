# Advance Directive Ontology (ADO)

**A computable layer between advance care planning documents and bedside decisions in advanced heart failure**

Patrick Walsh & Darren Chan · BMDS 210 / CS 270 · Stanford University · Spring 2026

[![OWL](https://img.shields.io/badge/ontology-OWL-blue)](advanced_directives.owl)
[![Python](https://img.shields.io/badge/python-3.8+-3776AB)](requirements.txt)
[![Evaluation](https://img.shields.io/badge/evaluation-developmental-orange)](docs/evaluation/Honest_Evaluation_Report.md)

---

## The problem

At 2 a.m. in the ICU, teams act on **code status** and orders—not on the advance directive PDF. Preferences pass through AD → POLST → hospital orders, and **conditional, heart-failure-specific wishes** are lost when language is flattened to checkboxes.

ADO encodes what the patient actually said as **testable preference objects** and answers, for a given clinical scenario: *does this preference apply, and what should we document?*

---

## What ADO is (and is not)

| | |
|---|---|
| **Is** | OWL ontology + Python reasoner; structured input pipeline; optional LLM extraction; honest outputs (clear / partial / no coverage / vague) |
| **Is not** | A legal advance directive, an EHR product, or a clinically validated deployment system |

---

## Results (developmental validation)

Full narrative: **[Honest Evaluation Report](docs/evaluation/Honest_Evaluation_Report.md)** · Figures: **[presentation_figures](docs/presentation/presentation_figures/)**

| Layer | Headline | Caveat |
|-------|----------|--------|
| Vignettes (dev / hold-out) | 16/16 · 10/10 | Single patient; team gold |
| Ablation (condition-blind) | **69%** | Same 16 vignettes |
| Cohort stress (520 cells) | **~47%** vs. reference oracle | 20 messy profiles × 12 scenarios |
| Track 3 (POLST mapping) | **35/36** fields | n=12 profiles |
| Extraction | **F1 0.97** | n=12 clauses |
| Inventory coverage | **47%** fully representable | 30-clause sample |

```bash
python evaluation/evaluation_suite.py
```

---

## Repository layout

```
.
├── README.md
├── requirements.txt
├── advanced_directives.owl      # Base ontology (open in Protégé)
│
├── ado/                         # Core library (reasoner, pipeline, LLM I/O)
├── evaluation/                  # Benchmarks, cohort simulation, metrics
├── data/                        # Populated OWL, gold annotations, reference PDFs
├── docs/                        # Reports, guides, figures (see docs/README.md)
└── scripts/                     # Demo + presentation build tools
```

<details>
<summary>Directory details</summary>

**`ado/`** — `preference_input.py`, `query_evaluation.py`, `code_status.py`, `holdout_vignettes.py`, `llm_extraction.py`, optional Gemini modules

**`evaluation/`** — `vignette_eval.py`, `realistic_simulation.py`, `track3_evaluation.py`, `coverage_analysis.py`, `extraction_evaluation.py`, `evaluation_suite.py`, `data/` (cohort profiles)

**`data/populated/`** — Example patient OWL + `example_input.json`

**`data/gold/`** — Extraction annotation JSON

**`docs/evaluation/`** — Honest report, quantitative plan, cohort results JSON

**`docs/presentation/`** — PowerPoint deck, speaker notes, 300 DPI figures

**`docs/guides/`** — Live demo & Protégé walkthrough

**`docs/reports/`** — LaTeX/PDF final report & presentation

**`docs/reference/`** — Pipeline design, concept inventory, Magnus review

**`docs/archive/`** — Superseded drafts & templates

</details>

---

## Quick start

```bash
git clone https://github.com/patrickwalsh26/bmds210-AD_Ontology.git
cd bmds210-AD_Ontology
pip install -r requirements.txt
```

**Java** is required for owlready2 / HermiT.

### Build example patient & run reasoner

```bash
python -m ado.preference_input --example
python -m ado.query_evaluation
```

### Run evaluations

```bash
python evaluation/vignette_eval.py --suite all
python evaluation/vignette_eval.py --suite dev --baseline condition-blind
python evaluation/realistic_simulation.py --json docs/evaluation/cohort_simulation_results.json
python evaluation/track3_evaluation.py
python evaluation/coverage_analysis.py
```

### Live demo

```bash
export ANTHROPIC_API_KEY=...   # optional, for LLM scenarios
python scripts/demo.py --pause
```

### Presentation assets

```bash
./scripts/build_presentation_assets.sh
```

Deck: `docs/presentation/ADO_powerpoint_presentation.pptx`

---

## Documentation

| Document | Purpose |
|----------|---------|
| **[docs/README.md](docs/README.md)** | Full documentation index |
| [Honest Evaluation Report](docs/evaluation/Honest_Evaluation_Report.md) | Results, limitations, next steps |
| [project_pipeline.md](docs/reference/project_pipeline.md) | Architecture |
| [Live Demo Guide](docs/guides/Live_Demo_Guide.md) | Podium demo |
| [Figure captions](docs/presentation/presentation_figures/FIGURE_CAPTIONS.md) | Slide text for each chart |

---

## Authors

Patrick Walsh · Darren Chan — Stanford University, Spring 2026.

Questions: open an issue or attach output from `python evaluation/evaluation_suite.py`.
