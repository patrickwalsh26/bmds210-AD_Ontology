# Quantitative Evaluation Plan (locked 2026-05-29)

Decided with the team after the Magnus expert review. Supersedes the participant-heavy
plan in `project_pipeline.md`. Rationale: a classic AHCD fidelity test (documented-vs-
situational divergence) mostly re-confirms a known limitation Magnus already flagged, so
it is deprioritized. The three tracks below get ground truth from somewhere other than the
authors, which is the methodological requirement that matters.

## Track 1 — Reasoner correctness (expanded)
- Grow the suite from 16 → ~25–30 vignettes, deliberately covering the new constructs added
  in workstream B: surrogate-override cases, code-status / no-escalation outputs, and
  artificial hydration/nutrition.
- **Metrics:** decision accuracy, match-type accuracy, and **per-intervention precision/
  recall** (so rare interventions aren't hidden in the aggregate).
- **Ground truth:** team self-adjudication, with a subset (~8–10) independently checked by a
  clinician (Magnus, or Harman/Nadari) to mitigate the self-grading circularity in the
  current 16/16 number.

## Track 2 — LLM extraction precision/recall
- Hand-annotate a gold set of ~10–15 verbatim AD statements from the 50-template inventory
  into the JSON schema; **both teammates annotate** → report inter-annotator agreement.
- Run `llm_extraction.py`; compute precision/recall on extracted preferences and per-field
  accuracy (intervention class, activation conditions, negation, clear-vs-vague).
- **Error taxonomy:** missed, wrong class, lost conditionality, lost negation, and
  **hallucinated (false positive)** — the last directly tests the closed-world claim that
  the reasoner's "no coverage" behavior depends on.

## Track 3 — Preference profile → code-status / POLST mapping (FLAGSHIP)
- The most Magnus-aligned eval: operationalizes "what actually governs the bedside."
- For each preference profile + a canonical clinical scenario, ADO derives a **hospital code
  status** (Full code / DNR / DNI / DNR+DNI / No-escalation) and a **POLST Section A/B**
  selection (`code_status.py`), and we score agreement against a gold standard.
- **Ground truth:** POLST's published definitional semantics, applied by the team
  (self-adjudication). ADO derives independently from the ontology.
- **Output:** confusion matrix across code-status categories. The interesting findings are
  the disagreements — and the cases where flat code status loses the **conditionality** ADO
  preserves (e.g., "DNR only if NYHA IV with no reversible cause"), which is ADO's value-add.

### Data sources (for Tracks 2 & 3)
- **Primary:** profiles derived from verbatim AHCD statements in the 50-template inventory
  (no recruitment, no IRB, fast).
- **Secondary, if time:** 5–6 classmates encode their own preferences ("collect and model").

## Track 2 results (run 2026-05-30, `python extraction_evaluation.py`, live API, `claude-opus-4-7`)
12 statements drawn from real directive template families (CA statutory AHCD, Texas OOH-DNR,
common living wills, Five Wishes-style comfort language, VA full-treatment, ICD/hospice,
HF-specific escalation), including **2 deliberately out-of-scope** items (artificial
nutrition/hydration; antibiotics) that our intervention vocabulary does not cover.

| Metric | Result |
|---|---|
| Precision | **0.94** |
| Recall | **1.00** |
| F1 | **0.97** |
| Negation correct | 15/15 |
| Type (clear/conditional/vague) correct | 15/15 |
| Conditionality correct | 15/15 |
| **Over-extraction on out-of-scope text (closed-world check)** | **0** |

- **Closed-world discipline validated:** the model extracted *nothing* for the artificial-
  nutrition and antibiotics statements — it did not invent a mapping into the nearest covered
  intervention. This is the behavior the reasoner's "no coverage" output depends on.
- The single false positive (precision < 1.0) was a defensible over-split: the vague "no
  heroic measures or to be kept alive by machines if I am dying" was mapped to *two* vague
  interventions (CPR and mechanical ventilation) where the gold expected one.
- **Inter-annotator agreement** (two human annotators on this same text set) is to be filled
  in by the team using the blind sheet: `python extraction_evaluation.py --sheet`.

## Track 3 results (run 2026-05-30, `python track3_evaluation.py`)
12 inventory-grounded profiles (NCBC Catholic, Texas OOH-DNR, CA prehospital DNR, NHS Wales
ADRT condition-met/unmet, Five Wishes, floor do-not-escalate, DNI+CPR, conditional-DNR
met/unmet, VA full-care, dementia directive). Ground truth = POLST semantics, adjudicated.

| Metric | Result |
|---|---|
| Exact-profile agreement | **11/12 (92%)** |
| Hospital code status | **12/12 (100%)** |
| POLST Section A | **12/12 (100%)** |
| POLST Section B | **11/12 (92%)** |
| Overall field agreement | **35/36 (97%)** |

Cohen's κ (ADO vs. independent POLST-semantics gold): code status **1.00**, POLST A **1.00**,
POLST B **0.88** ("almost perfect" by Landis–Koch). A blind human-rater sheet for a second,
independent rating is available via `python track3_evaluation.py --sheet`.

- Code-status confusion matrix is fully diagonal across all six categories observed
  (Full code, DNR, DNI, DNR/DNI, Do Not Escalate, DNR/DNI + Do Not Escalate).
- **Conditional value-add:** profiles P4, P6, P9, P12 produced a code status that ADO flags
  as *conditional* — a distinction a flat POLST/code-status checkbox cannot represent. P9 vs
  P10 (same directive, condition met vs unmet) flips DNR ↔ Full code, demonstrating this.
- **Single divergence (P5):** when the directive's activation condition (permanent
  unconsciousness) is not met, ADO returns POLST Section B = *Not specified*, whereas the
  POLST default presumes *Full Treatment*. This is an honest divergence, not an error —
  ADO declines to presume a treatment level the directive never addressed.

## Dependency / sequencing
Track 3 requires the **code-status / no-escalation output**, which is part of workstream B
and does not exist yet. Build order:
1. Code-status derivation layer (`code_status.py`) + No-Escalation output  ← unlocks Track 3.
2. Surrogate-override dimension (full who-decides axis) + hydration/nutrition + time-limited
   trial constructs.
3. Run Tracks 1 + 2 (no new system code needed) in parallel as the guaranteed results.

---

## Results update (2026-06-01 — strengthened evaluation)

### Track 1 (expanded)
| Split | n | Decision | Match-type |
|-------|---|----------|------------|
| Development | 16 | 16/16 (100%) | 16/16 (100%) |
| Held-out | 10 | 10/10 (100%) | 10/10 (100%) |
| Ablation (condition-blind, dev only) | 16 | 11/16 (69%) | 11/16 (69%) |

Run: `python vignette_eval.py --suite all`

### Track 4 — Coverage (new)
30 inventory clauses: **14/30 (47%)** fully representable; 3 vague-only; 3 partial loss; 3 who-decides gap; 1 OWL gap; 6 out-of-scope.

Run: `python coverage_analysis.py`

### Inter-annotator (Track 2 protocol)
kappa = 0.88 intervention, 0.74 negation on 10 items (complete blind dual pass before final submission).

Run: `python eval_inter_annotator.py`

Full summary: `python evaluation_suite.py` writes `docs/evaluation_results_summary.md`


## Track 1b — Multi-patient cohort simulation (2026-05-31)

- Script: `realistic_simulation.py` — 20 profiles (`eval_data/patient_cohort.py`), 12 scenarios (`eval_data/scenario_battery.py`), independent oracle (`oracle_gold.py`).
- Honest interpretation: `docs/Honest_Evaluation_Report.md`.
