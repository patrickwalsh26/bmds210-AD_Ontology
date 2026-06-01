# Honest Evaluation Report — Advance Directive Ontology (ADO)

**Patrick Walsh & Darren Chan · BMDS 210 / CS 270 · Spring 2026**

This document is the candid evaluation summary for the class presentation and final report. It separates **developmental checks** (where we wrote the gold standard) from **stress tests** (messy multi-patient simulation) and states **gaps, limitations, and next steps** explicitly.

---

## What we are claiming (and what we are not)

| Claim | Supported? | Evidence |
|--------|------------|----------|
| The reasoner implements our ontology spec on curated vignettes | **Yes, developmental** | 16/16 dev + 10/10 held-out on Jane Doe (`vignette_eval.py`) |
| Condition-aware matching beats ignoring activation logic | **Yes, on dev vignettes** | 11/16 (69%) condition-blind ablation vs 16/16 full (`vignette_eval.py --baseline condition-blind`) |
| HF intervention grammar covers many real template clauses | **Partial** | 14/30 inventory clauses fully representable (`coverage_analysis.py`) |
| Free-text extraction is usable with closed-world discipline | **Promising, small n** | F1 0.97, 0 OOS hallucinations on n=12 (`extraction_evaluation.py`) |
| Bedside code-status mapping aligns with POLST semantics | **Strong on n=12 profiles** | 35/36 fields (97%); one principled divergence P5 | 
| The system is validated on real patient charts at scale | **No** | No MIMIC/chart review; cohort gold is rule-based, not blind clinician adjudication |

---

## Track 1 — Curated vignettes (single patient, team gold)

**Command:** `python evaluation/vignette_eval.py --suite all`

| Suite | Decision | Match type | Notes |
|--------|----------|------------|--------|
| Development (16) | 16/16 (100%) | 16/16 | Jane Doe; gold written alongside ontology design |
| Held-out (10) | 10/10 (100%) | 10/10 | Frozen before final ontology tweaks; still one encoded patient |

**Ablation (condition-blind):** 11/16 (69%) — failures V2, V6, V11, V13, V14 are cases where **activation logic** and **vague-vs-partial** distinctions matter. This is the most honest single-number contrast for “what ADO adds.”

**Limitation:** Perfect held-out scores do *not* prove generalization across patients or messy chart abstraction. They prove consistency on one richly encoded profile.

---

## Track 1b — Multi-patient cohort simulation (messy / real-world stress test)

**Command:** `python evaluation/realistic_simulation.py --json docs/evaluation/cohort_simulation_results.json`

| Metric | Result | Interpretation |
|--------|--------|----------------|
| Cells evaluated | **520** | 20 template-inspired profiles × 12 acute scenarios × clinically queried interventions |
| ADO vs reference oracle (decision) | **~47%** | Reference uses a **simplified, independent** rule set (`oracle_gold.py`), not ADO’s OWL matcher |
| ADO vs reference (match type) | **~49%** | Same; many gaps are **granularity** (e.g. `mechanical_ventilation` refusal vs `TemporaryVentilation` query) |
| Condition-blind | **~45%** | Similar to full ADO on this oracle — oracle does not capture all ADO nuances |
| Checkbox (silent → full code) | **~19%** | Models flat POLST default; over-asserts treatment when AD is silent |
| Checkbox (silent → no coverage) | **~86%** | Better on silence; still ignores conditionality |
| Checkbox “overconfident” cells | **~400+** | Flat yes/no where reference says partial / vague / no coverage |

**By `messy_level` tag** (see `eval_data/patient_cohort.py`): clean profiles score higher than minimal/contradictory/incomplete-encoding profiles, but **no stratum reaches vignette-level accuracy** against the reference oracle.

**Encoding degradation** (`--degrade-encoding`): strips activation conditions → simulates incomplete chart abstraction; match-type accuracy shifts modestly; shows sensitivity to structured encoding quality.

**Why the cohort score is low (on purpose):**

1. **Independent oracle** — we refused to grade ADO against its own `find_matching_preferences()` loop (that would be circular).
2. **Cross-patient × cross-scenario matrix** — most cells are *not* hand-adjudicated; many are “directive silent on this intervention.”
3. **Template coarse language** — e.g. Texas OOH-DNR “no ventilation” vs separate queries for BiPAP, intubation, temporary vs indefinite.
4. **Known ontology limits** — LVAD-plan qualifiers in prose but not in activation conditions (cohort_09); contradictory CPR lines (cohort_15).

**What this stress test *does* show:**

- ADO does **not** collapse to a flat checkbox on nuanced cells (hundreds of overconfident checkbox errors vs reference).
- Performance **varies by messiness** — encoding quality and template family matter.
- Failures are **inspectable** (see `sample_failures` in JSON summary).

---

## Track 2 — LLM extraction (real template text, small gold)

| Metric | Result |
|--------|--------|
| Precision / Recall / F1 | 0.94 / 1.00 / **0.97** (n=12) |
| Out-of-scope hallucinations | **0** |
| Blind dual annotation | Protocol in `eval_inter_annotator.py`; demo κ in repo — **needs real blind pass by both authors** |

---

## Track 3 — Code status / POLST (12 inventory profiles)

| Metric | Result |
|--------|--------|
| Field agreement | **35/36 (97%)** |
| Conditional value-add | P9 vs P10, P4, P6, P12 — flat forms cannot represent conditionality |
| Principled divergence | **P5** — ADO returns “not specified” for POLST B when activation condition unmet; POLST defaults to full treatment |

---

## Coverage — 50-template inventory sample (n=30)

| Label | Count |
|--------|-------|
| Fully representable | **14** |
| Vague / partial loss | 6 |
| Out of scope (nutrition, antibiotics, etc.) | 5 |
| Who-decides / surrogate gap | 3 |
| OWL gap (time-limited trial, etc.) | 2 |

**47% fully representable** is the honest scope statement for HF-focused ADO v1.

---

## Gaps and limitations (say these out loud)

1. **Gold-standard circularity** on vignettes — team-authored expected answers on one patient.
2. **No external chart review** — no MIMIC, no blind intensivist adjudication on cohort cells.
3. **Reference oracle ≠ OWL reasoner** — cohort % is a lower bound on “agreement with simplified rules,” not clinical wrongness rate.
4. **Second dimension missing** — surrogate override / who decides (Magnus feedback); inflates apparent coverage gaps.
5. **Extraction n=12** — not benchmark-scale; inter-annotator agreement still to be run blind.
6. **LLM ablation arms** (Gemini direct vs pipeline) — scripts exist on some branches; not required for core claims.

---

## Next steps (ordered by impact)

1. **Blind adjudication** — 50–100 cohort cells rated by second author + one clinician; replace rule-only oracle for that subset.
2. **Expand cohort gold** — store per-cell `clinical_expected` in `eval_data/cohort_adjudicated.json` for high-disagreement cases.
3. **Intervention-family mapping** — align coarse template language with OWL queries (ventilation umbrella, ICD shock vs deactivation).
4. **MIMIC-IV or synthetic note corpus** — extraction + population at scale.
5. **Surrogate-override axis** — ontology + eval for “agent may override” clauses.
6. **Run `python evaluation/evaluation_suite.py`** before submission to refresh `docs/evaluation/evaluation_results_summary.md`.

---

## Commands cheat sheet

```bash
python evaluation/vignette_eval.py --suite all
python evaluation/vignette_eval.py --suite dev --baseline condition-blind
python evaluation/realistic_simulation.py --json docs/evaluation/cohort_simulation_results.json
python evaluation/realistic_simulation.py --degrade-encoding
python3 coverage_analysis.py
python3 track3_evaluation.py
python3 extraction_evaluation.py   # requires API key
python evaluation/evaluation_suite.py
./scripts/build_presentation_assets.sh
```

---

## Suggested presentation framing (30 seconds)

> “On curated vignettes for one encoded patient we’re at 16/16 development and 10/10 held-out — that’s a **spec test**, not population validation. When we stress-test **20 messy template-inspired profiles** across **520 clinical query cells**, agreement with an independent simplified oracle is under 50%, and a flat checkbox baseline is worse on nuanced cases. That’s the honest picture: ADO adds **conditionality and honesty about silence**, but coverage, encoding fidelity, and external gold still need work.”
