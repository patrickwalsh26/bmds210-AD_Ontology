# ADO Presentation — Speaker Notes (June 1, 2026)

**Runtime:** ~9 minutes + ~2 minutes Q&A · **17 slides recommended** · Figures in `docs/presentation_figures/` (300 DPI)

**Regenerate deck:** `./scripts/build_presentation_assets.sh` · Placement: `docs/PPT_Figures_Guide.md`

---

## Narrative arc

| Act | Slides | Story beat |
|-----|--------|------------|
| **I — The gap** | 1–3 | Code status at 2 a.m., not the AD. Three layers; conditional HF wishes get lost. |
| **II — The idea** | 4–7 | PreferenceStatement; four honest outputs; LLMs at the boundary only. |
| **III — The evidence** | 8–14 | **Two-layer validation**: spec test + cohort stress; ablation; coverage; POLST. |
| **IV — The placement** | 15–17 | Magnus workflow; limits; takeaways. |

**One-sentence pitch:** *ADO is the auditable inference layer between what patients document and what teams act on—honest enough to say “silent” when the directive is silent.*

**Handoff:** Patrick — Acts I–II (1–7); Darren — Act III–IV (8–17).

---

## Slide 1 — Title (~25 s)

**SAY:** Patrick Walsh & Darren Chan. **Advance Directive Ontology** — computable EOL preferences in advanced HF. Not a legal AD; decision support for ACP documentation.

**TRANSITION:** *“Start where clinicians live—the 2 a.m. crisis.”*

---

## Slide 2 — Clinical problem (~45 s)

**SAY:** Three instruments: AD, POLST, **code status**. Translation loss: conditional wishes → coarse boxes. Forms are often checkboxes, not novels—but **low resolution** and **disease blindness**.

**TRANSITION:** *“HF is where that hurts most.”*

---

## Slide 3 — Why HF (~35 s)

**SAY:** Unpredictable, device-heavy, repeated crises. Five decision points. ICD/LVAD/inotropes rarely in generic templates.

**TRANSITION:** *“What's the smallest object that preserves patient logic?”*

---

## Slide 4 — Approach (~45 s)

**SAY:** **PreferenceStatement** = intervention + activation conditions + strength + negation + verbatim text. Walk 72-hour vasopressor example.

**TRANSITION:** *“How much structure we built.”*

---

## Slide 5 — Ontology scope (~35 s)

**OPTIONAL LIVE — Protégé:** `populated_ontologies/ado_jane_doe_001.owl` · see `docs/Protege_Showcase_Guide.md`.

**SAY:** **67 classes, 22 properties, 21 interventions.** POINT AT `ontology_class_hierarchy.png`.

**TRANSITION:** *“Granularity only helps if we know when NOT to answer.”*

---

## Slide 6 — Four outputs (~40 s)

**SAY:** Clear / Partial / No coverage / Vague. Punchline: overconfident systems can't say **“I don't know.”**

**TRANSITION:** *“How we wired the pipeline.”*

---

## Slide 7 — Architecture (~45 s)

**SAY:** LLMs extract ONLY. Ontology owns truth. Reasoner decides. Closed-world on out-of-scope lines.

**TRANSITION:** *“We tested that six ways—including a large cohort stress test.”*

---

## Slide 8 — Study design (~50 s)

**ROLE:** Earn trust; name all strands before numbers.

**SAY:** Six strands on the figure: (1) **16 dev + 10 held-out vignettes** on one encoded patient; (2) **ablation** without activation conditions; (3) **520-cell cohort** — 20 messy template-inspired profiles × 12 acute scenarios; (4) **extraction** on real template language; (5) **12 profiles → code status/POLST**; (6) **coverage** on 30 inventory clauses. Plus Magnus expert review.

**CAVEAT:** Developmental validation — team gold on vignettes; cohort scored vs simplified reference oracle, not blind chart review.

**POINT AT:** `study_design_strands.png`, `vignette_match_types.png`.

**TRANSITION:** *“Here's the honest picture in two layers.”*

---

## Slide 9 — Quantitative results / two-layer validation (~60 s)

**ROLE:** **Main results slide** — do not oversell 100%.

**SAY — Layer 1 (left):** **16/16** dev and **10/10** held-out on Jane Doe — that's our **spec test**: does the reasoner match the ontology we designed?

**SAY — Layer 2 (right):** **520-cell cohort** — 20 profiles from Texas DNR, Five Wishes, dementia directives, contradictory CPR lines, incomplete LVAD encoding. Against an **independent simplified oracle**, ADO is **~47%** — not hand-adjudicated, but an honest stress test. Condition-blind is similar (~45%). A **flat checkbox** is worse on nuanced cells.

**SAY — Also:** Track 3 **35/36 (97%)** on POLST semantics; extraction **F1 0.97** on n=12.

**POINT AT:** `eval_two_layer.png` (full slide).

**TRANSITION:** *“Let me show why conditionality matters, then the cohort in detail.”*

---

## Slide 10 — Conditional + ablation (~45 s)

**SAY — Ablation:** Drop activation conditions → **11/16 (69%)** — not 75%; failures are exactly the partial/vague/conditional vignettes.

**SAY — P9/P10:** Same words, two scenarios → **DNR** vs **Full code**. Flat POLST can't carry if/then.

**POINT AT:** `ablation_conditions.png`, `conditional_p9_p10.png`.

**TRANSITION:** *“Zoom in on the cohort stress test.”*

---

## Slide 11 — COHORT STRESS TEST (~50 s)

**ROLE:** Honesty slide — embrace the ~47%.

**SAY:** **20 patients** tagged by messiness: clean, typical, minimal, contradictory, incomplete encoding. **12 scenarios** — arrest, vent, hospice, pressor time trials, dialysis, etc. **520 queried cells.**

**SAY:** Clean profiles score higher; minimal and contradictory fall off — encoding quality matters. **421 cells** where a flat checkbox forces yes/no but the reference says partial, vague, or no coverage — that's ADO's value proposition.

**POINT AT:** `cohort_messy_breakdown.png`, `cohort_baseline_comparison.png`.

**TRANSITION:** *“Dashboard and scope in two more slides if you have time; otherwise jump to workflow.”*

---

## Slide 12 — EVALUATION DASHBOARD (~20 s, optional)

**SAY:** One-panel backup: vignettes, ablation, cohort, coverage **47%**, extraction, POLST. Use if asked “give me all numbers.”

**POINT AT:** `eval_dashboard.png`.

**IF SHORT ON TIME:** Hide this slide.

---

## Slide 13 — COVERAGE & EXTRACTION (~35 s)

**SAY:** **14/30 clauses (47%)** fully representable in our HF grammar. Six out of scope (nutrition, antibiotics…). Extraction **F1 0.97**, **zero** hallucinations on out-of-scope traps.

**POINT AT:** `coverage_inventory.png`, `extraction_f1.png`.

**TRANSITION:** *“Bedside mapping detail.”*

---

## Slide 14 — TRACK 3 (~35 s)

**SAY:** **35/36 fields** against POLST semantics. Code status perfect on 12 profiles. **P5:** when activation condition unmet, ADO says POLST B “not specified” vs default full treatment — principled, not a bug.

**POINT AT:** `track3_field_agreement.png`, `code_status_confusion.png`.

**TRANSITION:** *“Magnus placed this in workflow.”*

---

## Slide 15 — Clinical integration (~40 s)

**SAY:** ACP progress note, not signed AHCD. Directive → ADO → ACP pre-pop → conversation → POLST/code status.

---

## Slide 16 — Limits (~40 s)

**SAY:** No legal force; who-decides axis missing; **cohort oracle ≠ clinical ground truth**; team gold on vignettes; no EHR trial. **Do not** claim multi-patient validation from 16/16 alone.

---

## Slide 17 — Takeaways (~25 s)

**SAY:** Read bullets. Repo. Questions. Optional live demo: `python3 demo.py --scenario 1`.

---

## Q&A cheat sheet

| Question | Answer |
|----------|--------|
| Why only ~47% on cohort? | Independent simplified oracle; 520 cells mostly “directive silent”; not hand-adjudicated. |
| Why still show 16/16? | Spec test on one patient — proves reasoner matches design. |
| Legal AD? | No — ACP documentation support. |
| Weakest evidence? | Team gold; cohort needs blind clinician subset. |
| What's next? | Adjudicate 50–100 cohort cells; surrogate axis; MIMIC. |

---

*Sync embedded notes: `python3 scripts/update_presentation_notes.py`*
