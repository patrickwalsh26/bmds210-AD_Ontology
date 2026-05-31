# ADO Evaluation Roadmap (June 2026)

This document supports the **final report (due Friday)** and honest presentation of results.

## What we claim today (defensible)

| Claim | Evidence | Caveat |
|-------|----------|--------|
| Reasoner handles curated scenarios | Dev **16/16**; held-out **10/10** (single patient ontology) | Gold written by team |
| Conditionality matters | Ablation **11/16** (69%) when activation ignored | Same vignettes |
| Bedside mapping | Track 3 **35/36** vs POLST semantics | P5 divergence principled |
| Closed-world extraction | **0** hallucinations on 2 OOS statements | n=12 clauses |
| Inventory coverage | **14/30** fully representable; gaps enumerated | Not random sample |

## Completed this sprint (2026-06-01)

- [x] Held-out vignette split (`holdout_vignettes.py`, `vignette_eval.py`)
- [x] Condition-blind ablation baseline
- [x] Coverage analysis on 30 inventory clauses (`coverage_analysis.py`)
- [x] Inter-annotator protocol + demo κ (`eval_inter_annotator.py`, `gold_annotations/`)
- [x] Automated summary (`evaluation_suite.py` → `docs/evaluation_results_summary.md`)

## Before Friday (priority order)

### Must-do (report credibility)

1. **Dual annotation (real)** — Patrick and Darren independently fill `gold_annotations/annotator_b.json` from `statements.json` **without** looking at `annotator_a.json`. Run `python eval_inter_annotator.py`. Replace demo disagreements in report.
2. **Blind Track 3 rater** — One classmate completes `python track3_evaluation.py --sheet`. Report agreement with team gold.
3. **Update report** — Use `docs/evaluation_results_summary.md` numbers; reframe abstract (developmental validation, not clinical trial).

### Should-do (competitive)

4. **Expand extraction gold to n=20** — Add 8 harder clauses; re-run `extraction_evaluation.py` if API key available.
5. **Magnus spot-check** — 5 vignettes; note disagreements in appendix.
6. **Presentation slide** — Report dev + holdout + ablation + coverage pie, not only 16/16.

### Post-course (real-world)

7. MIMIC-IV code-status descriptives (HF cohort)
8. IRB-governed ACP note corpus
9. Surrogate-override axis + nutrition decision point

## Commands

```bash
python preference_input.py --example
python evaluation_suite.py          # full summary markdown
python vignette_eval.py --suite all
python vignette_eval.py --suite dev --baseline condition-blind
python coverage_analysis.py
python eval_inter_annotator.py --export-template
python eval_inter_annotator.py
python track3_evaluation.py
python extraction_evaluation.py     # needs ANTHROPIC_API_KEY
```

## Reporting language (use in Discussion)

> Quantitative results reflect **developmental validation** on author-constructed vignettes and template-derived profiles with team-adjudicated gold standards. They demonstrate internal consistency and illustrate conditional reasoning; they do **not** establish clinical safety or superiority to existing workflows.
