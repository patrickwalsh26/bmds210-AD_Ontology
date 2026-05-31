# Figure captions for ADO presentation

Copy each caption below the corresponding figure on your slide, or into the speaker notes.
Figures are in `docs/presentation_figures/` at **300 DPI**.

---

## Figure 1. `eval_two_layer.png`

**Two-layer validation.** (a) Curated vignettes on one encoded patient: 16/16 development and 10/10 held-out accuracy (spec test); condition-blind ablation drops to 69% (11/16), showing activation logic is essential. (b) Cohort stress test across 20 template-inspired profiles and 12 clinical scenarios (520 query cells): ADO agrees with an independent simplified oracle on ~47% of decisions—far below vignette scores, reflecting messy real-world encoding and granularity gaps, not a deployment-ready error rate.

---

## Figure 2. `eval_overview.png`

**Summary metrics** across evaluation tracks: perfect vignette development accuracy contrasts with 47% cohort agreement; 69% under condition-blind ablation; 97% field agreement mapping 12 directive profiles to hospital code status and POLST (35/36 fields).

---

## Figure 3. `study_design_strands.png`

**Evaluation design:** six complementary strands—curated vignettes, condition-blind ablation, large cohort simulation, LLM extraction on real template language, POLST-semantics mapping, and systematic inventory coverage analysis.

---

## Figure 4. `ablation_conditions.png`

**Ablation:** Re-scoring the same 16 development vignettes while treating every matched preference as unconditionally applicable drops accuracy from 100% to 69% (11/16)—failures align with partial, vague, and conditional cases.

---

## Figure 5. `conditional_p9_p10.png`

**Conditional value-add (profiles P9 vs P10):** Identical preference text yields DNR when activation conditions are met versus full code when they are not—logic a flat POLST checkbox cannot represent.

---

## Figure 6. `cohort_messy_breakdown.png`

**Cohort performance stratified by messiness.** Profiles tagged clean (well-structured encoding) score highest; minimal, contradictory, and incomplete-encoding profiles show lower agreement with the reference oracle—highlighting sensitivity to chart abstraction quality and template ambiguity.

---

## Figure 7. `cohort_baseline_comparison.png`

**(a)** Agreement with the simplified reference oracle: ADO (47%) versus flat checkbox heuristics. **(b)** In 421 of 520 cells (81%), the reference expects partial, vague, or no-coverage answers but a checkbox forces a definitive yes/no—illustrating ADO's value in preserving epistemic honesty.

---

## Figure 8. `eval_dashboard.png`

**Evaluation dashboard** (developmental validation, Spring 2026): vignette splits, ablation, cohort stress (47%), inventory coverage (47% fully representable), LLM extraction F1 0.97, and POLST/code-status field agreement (35/36).

---

## Figure 9. `vignette_splits.png`

**Vignette splits:** 100% decision and match-type accuracy on both development (n=16) and held-out (n=10) sets using the same encoded patient—developmental spec test, not multi-patient generalization.

---

## Figure 10. `vignette_match_types.png`

**Vignette suite composition:** Most gold labels expect clear or partial matches; the suite deliberately includes no-coverage and vague cases to test honest non-answers.

---

## Figure 11. `coverage_inventory.png`

**Coverage analysis** of 30 stratified clauses from a 50-template inventory: 14 (47%) fully representable in the HF-focused ontology; six out of scope (e.g., nutrition, antibiotics); gaps include surrogate-override and time-limited trials.

---

## Figure 12. `extraction_f1.png`

**Track 2 extraction** on 12 verbatim clauses from real template families: F1 0.97 with zero hallucinated preferences on out-of-scope artificial nutrition and antibiotics statements (closed-world discipline).

---

## Figure 13. `track3_field_agreement.png`

**Track 3:** Agreement between ADO-derived hospital code status and POLST sections versus gold labels from published POLST semantics (12 inventory-grounded profiles). One principled divergence on profile P5 (POLST B not specified vs default full treatment).

---

## Figure 14. `code_status_confusion.png`

**Code-status confusion matrix** (n=12 profiles): perfect diagonal agreement—no profile-level misclassification across six observed code-status categories.

---

## One-line slide captions (bullets)

- **eval_two_layer.png:** Two-layer validation.

- **eval_overview.png:** Summary metrics across evaluation tracks: perfect vignette development accuracy contrasts with 47% cohort agreement; 69% under condition-blind ablation; 97% field agreement mapping 12 directive profiles to hospital code status and POLST (35/36 fields).

- **study_design_strands.png:** Evaluation design: six complementary strands—curated vignettes, condition-blind ablation, large cohort simulation, LLM extraction on real template language, POLST-semantics mapping, and systematic inventory coverage analysis.

- **ablation_conditions.png:** Ablation: Re-scoring the same 16 development vignettes while treating every matched preference as unconditionally applicable drops accuracy from 100% to 69% (11/16)—failures align with partial, vague, and conditional cases.

- **conditional_p9_p10.png:** Conditional value-add (profiles P9 vs P10): Identical preference text yields DNR when activation conditions are met versus full code when they are not—logic a flat POLST checkbox cannot represent.

- **cohort_messy_breakdown.png:** Cohort performance stratified by messiness.

- **cohort_baseline_comparison.png:** (a) Agreement with the simplified reference oracle: ADO (47%) versus flat checkbox heuristics.

- **eval_dashboard.png:** Evaluation dashboard (developmental validation, Spring 2026): vignette splits, ablation, cohort stress (47%), inventory coverage (47% fully representable), LLM extraction F1 0.

- **vignette_splits.png:** Vignette splits: 100% decision and match-type accuracy on both development (n=16) and held-out (n=10) sets using the same encoded patient—developmental spec test, not multi-patient generalization.

- **vignette_match_types.png:** Vignette suite composition: Most gold labels expect clear or partial matches; the suite deliberately includes no-coverage and vague cases to test honest non-answers.

- **coverage_inventory.png:** Coverage analysis of 30 stratified clauses from a 50-template inventory: 14 (47%) fully representable in the HF-focused ontology; six out of scope (e.

- **extraction_f1.png:** Track 2 extraction on 12 verbatim clauses from real template families: F1 0.

- **track3_field_agreement.png:** Track 3: Agreement between ADO-derived hospital code status and POLST sections versus gold labels from published POLST semantics (12 inventory-grounded profiles).

- **code_status_confusion.png:** Code-status confusion matrix (n=12 profiles): perfect diagonal agreement—no profile-level misclassification across six observed code-status categories.
