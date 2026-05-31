# PowerPoint — figures, slide order, and exact numbers

Regenerate all figures (300 DPI) and embed in the deck:

```bash
./scripts/build_presentation_assets.sh
```

Or step by step:

```bash
python3 scripts/generate_presentation_figures.py
python3 scripts/generate_ontology_overview_figure.py
python3 scripts/insert_presentation_figures.py
python3 scripts/update_presentation_notes.py
```

Pull latest: `git pull origin cursor/realistic-evaluation-b880` (or `main` after merge).

---

## Recommended slide order (17 slides + optional appendix)

Drag appended slides into this order after running `insert_presentation_figures.py`.

| # | Slide title (approx.) | Figure file(s) | What to emphasize |
|---|------------------------|----------------|-------------------|
| **1** | Title | — | Not a legal AD; inference layer |
| **2** | Clinical problem | — | AD → POLST → code status translation loss |
| **3** | Why HF | — | Five decision points |
| **4** | Approach | — | PreferenceStatement |
| **5** | Ontology scope | `ontology_class_hierarchy.png` (right) | 67 classes · 22 properties · 21 interventions |
| **6** | Four outputs | — | Clear / Partial / No coverage / Vague |
| **7** | Architecture | — | LLM extracts; ontology decides |
| **8** | Study design | `study_design_strands.png` + `vignette_match_types.png` | **Six strands** including 520-cell cohort |
| **9** | Quantitative results | **`eval_two_layer.png` (full width)** | **Lead with two-layer validation** |
| **10** | Conditional example | `ablation_conditions.png` + `conditional_p9_p10.png` | 69% ablation + P9/P10 flip |
| **11** | **COHORT STRESS TEST** (new) | `cohort_messy_breakdown.png` + `cohort_baseline_comparison.png` | ~47% vs oracle; checkbox overconfidence |
| **12** | **EVALUATION DASHBOARD** (new) | `eval_dashboard.png` | One-slide summary for appendix or backup |
| **13** | **COVERAGE & EXTRACTION** (new) | `coverage_inventory.png` + `extraction_f1.png` | 47% representable; F1 0.97 |
| **14** | **TRACK 3** (new) | `track3_field_agreement.png` + `code_status_confusion.png` | 35/36 fields; P5 divergence |
| **15** | Clinical integration | — | Magnus ACP note framing |
| **16** | Limits | — | Cohort caveat + team gold |
| **17** | Takeaways | — | Four bullets |

**Optional / hide:** older slides titled `STRENGTHENED EVALUATION` or `EVALUATION FIGURES — Track 3` if duplicated.

**Sidebar on slide 9 (if crowded):** `eval_overview.png` instead of two-layer (not recommended for June 1).

---

## Headline numbers (copy-paste)

### Layer 1 — Curated vignettes (spec test)
| Metric | Value |
|--------|--------|
| Development | **16/16** decision & match-type |
| Held-out | **10/10** |
| Ablation (condition-blind) | **11/16 (69%)** |
| Caveat | Single patient (Jane Doe); team gold |

### Layer 2 — Cohort stress test
| Metric | Value |
|--------|--------|
| Scale | **520 cells** = 20 patients × 12 scenarios |
| ADO vs ref. oracle | **~47%** decision agreement |
| Condition-blind | **~45%** |
| Flat checkbox vs oracle | **~19%** (silent → full code) |
| Checkbox overconfident | **421/520** nuanced cells |
| Caveat | Simplified oracle; not blind clinician adjudication |

### Track 2 — Extraction (n=12)
| Metric | Value |
|--------|--------|
| P / R / F1 | **0.94 / 1.00 / 0.97** |
| OOS hallucinations | **0** |

### Track 3 — Code status / POLST (n=12)
| Metric | Value |
|--------|--------|
| Field agreement | **35/36 (97%)** |
| Principled divergence | **P5** |

### Coverage (n=30 clauses)
| Metric | Value |
|--------|--------|
| Fully representable | **14 (47%)** |

---

## Figure catalog (`docs/presentation_figures/`)

| File | Resolution | Primary slide |
|------|------------|---------------|
| `eval_two_layer.png` | 300 DPI | **9** — main honest results |
| `eval_dashboard.png` | 300 DPI | **12** — backup / appendix |
| `study_design_strands.png` | 300 DPI | **8** |
| `cohort_messy_breakdown.png` | 300 DPI | **11** |
| `cohort_baseline_comparison.png` | 300 DPI | **11** |
| `ablation_conditions.png` | 300 DPI | **10** |
| `conditional_p9_p10.png` | 300 DPI | **10** |
| `coverage_inventory.png` | 300 DPI | **13** |
| `extraction_f1.png` | 300 DPI | **13** |
| `vignette_splits.png` | 300 DPI | **13** (secondary) |
| `track3_field_agreement.png` | 300 DPI | **14** |
| `code_status_confusion.png` | 300 DPI | **14** |
| `eval_overview.png` | 300 DPI | Optional compact sidebar |
| `vignette_match_types.png` | 300 DPI | **8** |
| `ontology_class_hierarchy.png` | 300 DPI | **5** |

---

## Opening line for results (recommended)

> “We use **two layers of validation**: perfect scores on **curated vignettes** are a **spec test** on one patient; a **520-cell cohort stress test** with messy template-inspired profiles shows **~47%** agreement with an independent oracle — and flat checkboxes fail on most nuanced cells. The contribution is **conditionality and honesty about silence**, not solved deployment.”

---

## Do NOT claim
- Clinical trial or bedside validation at scale
- Cohort oracle = ground truth (it is simplified rules)
- Multi-patient generalization from vignette 100%
- Legal directive status
