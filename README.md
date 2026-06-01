# Advance Directive Ontology (ADO)

**A computable layer between advance care planning documents and bedside decisions in advanced heart failure**

Patrick Walsh & Darren Chan · BMDS 210 / CS 270 · Stanford University · Spring 2026

[![OWL](https://img.shields.io/badge/ontology-OWL-blue)](advanced_directives.owl)
[![Python](https://img.shields.io/badge/python-3.8+-3776AB)](requirements.txt)
[![Evaluation](https://img.shields.io/badge/evaluation-developmental-orange)](docs/Honest_Evaluation_Report.md)

---

## The problem

At 2 a.m. in the ICU, teams act on **code status** and orders—not on the advance directive PDF. Preferences pass through AD → POLST → hospital orders, and **conditional, heart-failure-specific wishes** (temporary vs. indefinite ventilation, ICD deactivation in hospice, time-limited vasopressor trials) are lost when language is flattened to checkboxes.

ADO encodes what the patient actually said as **testable preference objects** and answers, for a given clinical scenario: *does this preference apply, and what should we document?*

---

## What ADO is (and is not)

| | |
|---|---|
| **Is** | An OWL ontology + Python reasoner for HF end-of-life interventions; structured input pipeline; optional LLM extraction at the boundary; honest outputs (clear / partial / no coverage / vague) |
| **Is not** | A legal advance directive, an EHR product, or a clinically validated deployment system |

Expert framing (Dr. Magnus): treat outputs as **ACP progress-note support**, not signed orders—conversation with the patient or surrogate still governs.

---

## Key ideas

1. **PreferenceStatement** — intervention + activation conditions + strength + negation + verbatim `originalText`
2. **Closed-world reasoning** — if the directive is silent, the system reports **no coverage** (does not presume full treatment)
3. **LLMs extract; the ontology decides** — extraction populates JSON; the reasoner owns truth
4. **Two-layer validation** — curated vignettes (spec test) + large cohort stress test (messy real-world profiles)

---

## Results (developmental validation)

Full narrative: **[Honest Evaluation Report](docs/Honest_Evaluation_Report.md)** · Figures: **[docs/presentation_figures/](docs/presentation_figures/)**

| Layer | What we measured | Headline result | Caveat |
|-------|------------------|-----------------|--------|
| **Vignettes** | 16 dev + 10 held-out scenarios | 16/16 · 10/10 accuracy | Single encoded patient (Jane Doe); team gold |
| **Ablation** | Same vignettes, ignore activation conditions | **69%** (11/16) | Shows conditionality is load-bearing |
| **Cohort stress** | 20 profiles × 12 scenarios (520 cells) | **~47%** vs. simplified reference oracle | Not blind clinician adjudication |
| **Track 3** | 12 profiles → code status / POLST | **35/36** fields (97%) | Gold = POLST published semantics |
| **Track 2** | LLM extraction, n=12 clauses | **F1 0.97**; 0 OOS hallucinations | Small gold set |
| **Coverage** | 30 inventory clauses | **47%** fully representable | HF-focused scope |

```bash
python evaluation_suite.py    # refresh docs/evaluation_results_summary.md
```

---

## Quick start

### Requirements

- **Python 3.8+**
- **Java** (for owlready2 / HermiT)
- Optional: **Anthropic API key** for extraction demo

### Install

```bash
git clone https://github.com/patrickwalsh26/bmds210-AD_Ontology.git
cd bmds210-AD_Ontology
pip install -r requirements.txt
```

### Run the pipeline

```bash
# 1. Build example patient ontology (Jane Doe)
python preference_input.py --example

# 2. Reasoner — 16 clinical vignettes
python query_evaluation.py

# 3. Extended vignette eval (dev + held-out + ablation)
python vignette_eval.py --suite all
python vignette_eval.py --suite dev --baseline condition-blind

# 4. Cohort stress test (520 cells)
python realistic_simulation.py --json docs/cohort_simulation_results.json

# 5. Code status / POLST mapping
python track3_evaluation.py

# 6. Live demo (six scenarios)
python demo.py --pause
```

### View in Protégé

Open `advanced_directives.owl` or `populated_ontologies/ado_jane_doe_001.owl` → **Reasoner → HermiT**.  
Walkthrough: [Protégé Showcase Guide](docs/Protege_Showcase_Guide.md).

---

## Repository layout

```
.
├── advanced_directives.owl       # Base ontology (67 classes, 22 properties, 21 interventions)
├── preference_input.py           # JSON / CLI → populated patient OWL
├── query_evaluation.py           # Scenario reasoner + 16 vignettes
├── code_status.py                  # Preferences → hospital code status + POLST
├── demo.py                         # Six-scenario demonstration
│
├── vignette_eval.py              # Dev / held-out vignettes + baselines
├── holdout_vignettes.py            # Frozen held-out gold
├── eval_baselines.py               # Condition-blind matcher
├── realistic_simulation.py       # Multi-patient cohort simulation
├── oracle_gold.py                  # Independent reference oracle (cohort gold)
├── eval_data/                      # 20 patient profiles + 12-scenario battery
├── coverage_analysis.py            # 30-clause inventory coverage
├── evaluation_suite.py             # Run all tracks → summary markdown
│
├── track3_evaluation.py            # Code-status / POLST evaluation
├── llm_extraction.py               # Claude: free text → structured JSON
├── extraction_evaluation.py        # Track 2 precision / recall
├── eval_inter_annotator.py         # Dual-annotation κ tooling
├── gold_annotations/               # Extraction gold JSON
│
├── ablation_evaluation.py          # Optional Gemini vs pipeline comparison
├── gemini_extraction.py            # Optional Gemini extraction
├── llm_direct_reasoning.py         # Optional end-to-end LLM baseline
│
├── populated_ontologies/           # Generated patient OWL + example_input.json
├── reference_ads/                  # Source directive PDFs
├── scripts/                        # Figures, PowerPoint insert, speaker notes
├── ADO_powerpoint_presentation.pptx
│
└── docs/                           # ← Documentation index: docs/README.md
    ├── Honest_Evaluation_Report.md
    ├── presentation_figures/       # 300 DPI evaluation figures + captions
    ├── archive/                    # Superseded drafts & templates
    └── …                           # Reports, guides, Magnus review
```

---

## Ontology scope (five decision points)

| Decision point | Example interventions | Why HF-specific |
|----------------|----------------------|---------------|
| CPR / resuscitation | CPR, defibrillation, pacing | Time-critical; vague “no heroic measures” |
| Mechanical ventilation | Temporary vs. indefinite, BiPAP, intubation | Templates rarely distinguish duration |
| ICD / devices | Deactivation, shock therapy, LVAD | ~200k HF patients with ICDs |
| Vasopressors / inotropes | Escalation, withdrawal, time bounds | Rarely in standard AD forms |
| Dialysis | Acute vs. chronic | Cardiorenal syndrome nuance |

**Four reasoner outputs:** `clear` · `partial` · `no_coverage` · `vague` (preserves `originalText` when language is irreducibly imprecise).

---

## Preference JSON schema (excerpt)

See `populated_ontologies/example_input.json` for a full example.

```json
{
  "intervention": "cpr",
  "negated": true,
  "strength": "Absolute",
  "type": "conditional",
  "original_text": "If my heart stops and I am in NYHA Class IV with no reversible cause, do not attempt CPR.",
  "activation_conditions": {
    "nyha_class": "IV",
    "conditions": ["cardiac_arrest"],
    "reversible_cause": false
  }
}
```

---

## Documentation

| Start here | |
|------------|---|
| **[docs/README.md](docs/README.md)** | Full documentation index |
| [Honest Evaluation Report](docs/Honest_Evaluation_Report.md) | Results, limitations, next steps |
| [project_pipeline.md](docs/project_pipeline.md) | Architecture & design rationale |
| [PPT_Figures_Guide.md](docs/PPT_Figures_Guide.md) | Slide ↔ figure placement |
| [Live Demo Guide](docs/Live_Demo_Guide.md) | Podium demo checklist |
| [Final_Report.tex](docs/Final_Report.tex) | AMIA-format write-up |

---

## Presentation assets

```bash
./scripts/build_presentation_assets.sh
```

Generates `docs/presentation_figures/*.png` (300 DPI) and updates `ADO_powerpoint_presentation.pptx`.  
Captions: [FIGURE_CAPTIONS.md](docs/presentation_figures/FIGURE_CAPTIONS.md).

---

## Limitations & next steps

- Team-authored gold on vignettes; cohort oracle is simplified rules—not external chart review  
- Missing **who-decides** axis (surrogate override); nutrition / antibiotics out of scope  
- Planned: blind adjudication on cohort cells, MIMIC/EHR notes, expanded extraction gold  

Details: [Evaluation Roadmap](docs/Evaluation_Roadmap.md).

---

## Authors

**Patrick Walsh** · **Darren Chan** — Stanford University, Spring 2026.

Questions or replication: open an issue or run `python evaluation_suite.py` and attach `docs/evaluation_results_summary.md`.

---

## Citation

If you use this work academically, cite the repository and the final report:

```bibtex
@misc{ado2026stanford,
  title  = {Advance Directive Ontology: Computable End-of-Life Preferences in Advanced Heart Failure},
  author = {Walsh, Patrick and Chan, Darren},
  year   = {2026},
  url    = {https://github.com/patrickwalsh26/bmds210-AD_Ontology}
}
```
