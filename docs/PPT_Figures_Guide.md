# PowerPoint — exact figures & numbers to use

Regenerate all PNGs and embed in the deck:

```bash
./scripts/build_presentation_assets.sh
python scripts/generate_presentation_figures.py
python scripts/insert_presentation_figures.py
```

Pull latest: `git pull origin main`

---

## Slide-by-slide map (13 core + 2 appendix slides)

| Slide # | Title (approx.) | Figure file(s) | Exact text to say / show |
|---------|-----------------|----------------|---------------------------|
| **5** | Ontology scope | `ontology_class_hierarchy.png` (right) | 67 classes, 22 properties, 21 interventions |
| **8** | Study design | `vignette_match_types.png` (right, optional) | 5 evaluation strands; developmental validation |
| **9** | Quantitative results | `eval_overview.png` + `ablation_conditions.png` (right) | See headline table below |
| **10** | Conditional example | `conditional_p9_p10.png` (right) | P9 vs P10: DNR ↔ Full code |
| **15** | **STRENGTHENED EVALUATION** (new) | 6-panel slide | **Use this as your main results slide for tomorrow** |
| **16** | Track 3 detail (optional) | `track3_field_agreement.png` + `code_status_confusion.png` | 35/36 fields; diagonal confusion matrix |

**Tip:** Drag slide **STRENGTHENED EVALUATION** to position **10** (right after slide 9). Hide or shorten old slide 9 bullets if redundant.

---

## Headline numbers (paste on slides or speaker notes)

### Track 1 — Vignettes
| Metric | Value |
|--------|--------|
| Development set | **16/16** decision & match-type |
| Held-out set (frozen gold) | **10/10** |
| **Ablation** (ignore activation conditions) | **11/16 (69%)** |
| Caveat | Single patient (Jane Doe); team gold |

### Track 2 — LLM extraction
| Metric | Value |
|--------|--------|
| Precision / Recall / F1 | **0.94 / 1.00 / 0.97** |
| Out-of-scope hallucinations | **0** (nutrition, antibiotics) |
| Inter-annotator κ (protocol) | **0.88** intervention, **0.74** negation |

### Track 3 — Code status / POLST
| Metric | Value |
|--------|--------|
| Field agreement | **35/36 (97%)** |
| Code status | 12/12 |
| POLST A | 12/12 |
| POLST B | 11/12 |
| Exact profile | 11/12 |
| Principled divergence | **P5** — Not specified vs Full Treatment |

### Track 4 — Coverage (30 inventory clauses)
| Label | Count |
|--------|-------|
| Fully representable | **14 (47%)** |
| Vague only | 3 |
| Partial loss | 3 |
| Who-decides gap | 3 |
| OWL gap | 1 |
| Out of scope | 6 |

---

## Figure catalog (`docs/presentation_figures/`)

| File | Use |
|------|-----|
| `eval_overview.png` | Slide 9 — 4 headline bars (100/100/97/97) |
| `ablation_conditions.png` | Slide 9 or 15 — **100% vs 69%** |
| `vignette_splits.png` | Slide 15 — dev vs hold-out |
| `coverage_inventory.png` | Slide 15 — **most important honesty slide** |
| `extraction_f1.png` | Slide 15 or slide 7 — F1 bar chart |
| `track3_field_agreement.png` | Slide 15 or 16 — 12/12, 12/12, 11/12, 11/12 |
| `code_status_confusion.png` | Slide 16 — confusion matrix |
| `conditional_p9_p10.png` | Slide 10 — clinical “aha” |
| `vignette_match_types.png` | Slide 8 — pie of match types |
| `ontology_class_hierarchy.png` | Slide 5 — Protégé backup |

---

## One-line framing (recommended opening for results)

> “We report **developmental validation**: perfect scores on small curated vignettes, but the meaningful findings are **ablation to 69% without conditions**, **47% full coverage** on real template language, and a **principled POLST disagreement** on profile P5.”

---

## Do NOT claim
- Clinical trial / bedside validation
- Multi-patient generalization
- Legal directive status
