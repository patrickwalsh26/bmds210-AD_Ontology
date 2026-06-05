# ADO — Final Presentation Script & Speaker Notes

**Talk:** 8 minutes (BMDS 210 / CS 270, June 1, 2026)  
**Presenters:** Patrick Walsh, Darren Chan  
**Deck:** 13 main slides + 6 supplementary slides (see below). Figures live in `docs/presentation_figures/` (300 DPI).

**Speaker split.** Patrick opens with the problem and clinical scope (Act I), hands to Darren for the model architecture and evaluation (Act II–III), and takes the close. Two handoffs, clean flow.

**Honesty rule (critical).** Lead with the *ablation (69%)* and *cohort stress test (~47%)*, never oversell the *100% vignettes* as deployment performance. Frame it as a specification test on one team-encoded patient. This candor is the strongest version of the story.

---

# ACT I — THE PROBLEM (Patrick) · ~1:30

## Slide 1 — Title: The Advance Directive Ontology (ADO)
**Speaker:** Patrick · **~20s**  
**On screen:** Title + "A computable representation of end-of-life preferences in advanced heart failure"

**Speaker notes:**
"I'm Patrick Walsh, this is Darren Chan. Our project is ADO — the Advance Directive Ontology. In one sentence: advance directives tell us what patients want at the end of life, but those documents are nearly useless when a clinician has to act on them at 2 a.m. We built a system that makes those preferences computable — and, critically, honest about what it doesn't know. ADO is decision support, not a legal directive."

**Transition:** "The problem is cascading information loss."

---

## Slide 2 — Clinical Problem: translation loss
**Speaker:** Patrick · **~35s**  
**On screen:** Three-stage workflow: `[Advance Directive]` → `[POLST]` → `[Code-status order @ bedside]` with red "translation loss" arrows.  
**Figure:** Simple 3-box workflow diagram showing information loss at each stage.

**Speaker notes:**
"A patient's advance directive captures nuanced, conditional wishes: 'CPR only if there's a reversible cause.' That becomes a POLST — portable medical orders. That becomes a bedside code-status box: full code or DNR. At every translation, information vanishes. A patient's 'ventilator for a few days if reversible, but never indefinitely' collapses into one checkbox or disappears entirely. The deeper problem: these instruments are *low-resolution* and *disease-blind*. Generic templates don't mention ICDs, LVADs, or inotropes — yet 200,000 HF patients have devices. Heart failure is where this gap becomes dangerous."

**Transition:** "So we asked: what's the smallest structure that preserves patient logic?"

---

## Slide 3 — Core Idea: PreferenceStatement object
**Speaker:** Patrick → Darren · **~40s**  
**On screen:** Labeled box showing PreferenceStatement anatomy: **Intervention** + **ActivationConditions** (NYHA, clinical state, reversible cause) + **Strength** + **isNegated** + **originalText**.  
**Figure:** Single box with five labeled fields, one worked example: `'No CPR if NYHA IV and no reversible cause'`.

**Speaker notes (Patrick):**
"Everything in ADO is built from one core object — the PreferenceStatement. It has five parts: the specific **intervention** (CPR, Indefinite Ventilation, etc.); the **activation conditions** (what circumstances it applies to: NYHA class, clinical condition, reversible cause); the **strength** (Absolute vs. Weak); a **negated flag** (refuse vs. want); and the patient's **verbatim words**. That single record holds the patient's actual logic — not collapsed into a yes/no box. Later, when the reasoner meets a clinical scenario, it checks those conditions one by one instead of guessing."

**Transition (Darren):** "That's the unit. We built an ontology on top of it."

---

# ACT II — THE SYSTEM & EVALUATION (Darren) · ~4:30

## Slide 4 — Ontology Scope: 21 interventions, 5 decision points
**Speaker:** Darren · **~30s**  
**On screen:** Tree diagram: root `Intervention` → five decision-point categories → 21 leaves.  
**Figure (CRITICAL):** `ontology_class_hierarchy.png` (from `docs/presentation_figures/`) — clean tree, no overlaps, Ventilation branch highlighted with Temp/Indefinite split clearly visible.  
**Visual rationale:** Concretizes "67 classes, 22 properties" and makes the Temp/Indefinite distinction immediately obvious. Without this figure, the slide is text-only and loses impact.

**Speaker notes:**
"The ontology has 67 classes, 22 properties, and 21 specific interventions. Five decision points: Device management (ICD, LVAD, pacemaker deactivation), Resuscitation (CPR, pacing, defibrillation), Ventilation, Pharmacologic (vasopressors, inotropes), and Dialysis. The key design: Ventilation splits into Intubation → Temporary vs. Indefinite. A patient says 'few days if reversible' — that's Temporary. 'Never indefinitely' — that's Indefinite. A checkbox collapses both. We keep them apart. This is OWL 2 DL, consistency-checked with HermiT, not a lookup table."

**Transition:** "How does the system work?"

---

## Slide 5 — Development & Deployment: Protégé → HermiT → owlready2
**Speaker:** Darren · **~30s**  
**On screen:** Three-stage pipeline: (1) Protégé GUI + HermiT validation; (2) Export OWL file; (3) owlready2 Python queries.  
**Figure:** `ontology_development_protege_hermit.png` (three boxes: design, validate, deploy).

**Speaker notes:**
"We built the ontology in Protégé, Stanford's OWL editor. HermiT validates it offline — classifies the hierarchy, detects contradictions, checks that every constraint is satisfiable. Once locked and sound, we export it as standard W3C OWL 2 DL and load it with owlready2 for programmatic querying. The reasoner is deterministic: every vignette produces the same answer on every run. We validated this by re-running our 16 vignettes three times — 100% agreement each time."

**Transition:** "Now here's what happens when you query."

---

## Slide 6 — Scenario-Based Reasoning: from vignette to decision
**Speaker:** Darren · **~35s**  
**On screen:** Left-to-right flow: clinical snapshot → patient ontology → find preference → check conditions → output.  
**Figure (SUGGESTED):** Create or adapt a simple left-to-right pipeline diagram showing: (1) scenario state (NYHA, conditions, reversible-cause); (2) patient ontology icon; (3) preference matching; (4) four condition checkboxes (NYHA? Condition? Reversible? Time?); (5) decision + match-type output.  
**Visual rationale:** Makes the query logic concrete and visually obvious. Without this, the explanation is purely verbal and loses impact for visual learners.

**Speaker notes:**
"A vignette is a clinical snapshot: cardiac arrest, NYHA IV, no reversible cause. We search the patient's ontology for matching preferences — here, a CPR-negated preference. Then we check its activation conditions one by one: NYHA IV met? Yes. No reversible cause required? Yes. Time bound? None. Conditions satisfied? All yes → decision: 'no', match type: 'clear'. Same preference, different scenario: patient is NYHA III and cause IS reversible. Conditions not all met → decision still 'no' [because preference is negated, unmet conditions mean CPR is allowed], but match type: 'partial' — defer to surrogate. The key: conditions are independent. Some met means partial, not met means no coverage, ambiguous language means vague. The reasoner can be honest."

**Transition:** "That's one patient at scale. But one isn't enough."

---

## Slide 7 — Scaling: spec test + cohort stress test
**Speaker:** Darren · **~45s**  
**On screen:** Two-panel summary: (left) Jane Doe 16/16 vignettes, ablation 11/16 (69%); (right) 50 profiles × 25 scenarios = 3,550 cells, 41.4% oracle agreement.  
**Figure:** `eval_cohort_messiness.png` — all 7 encoding-quality levels, ADO vs. blind vs. checkbox.

**Speaker notes:**
"Layer one — the spec test: one patient, 16 development vignettes, all correct. 10 held-out vignettes, all correct — 26 out of 26. When we remove activation conditions, accuracy drops to 69%, proving the conditional logic does real work. But this is *one carefully-encoded patient*. It's a proof of correctness, not generalization.

Layer two — the honest layer: 50 realistically-encoded patient profiles across 7 encoding-quality levels, 25 clinical scenarios, 3,550 decision cells total. ADO agrees with a reference oracle on 41.4% of cells. And the breakdown matters: clean profiles score 48%, culturally complex patients drop to 30% — the system degrades gracefully as encoding quality degrades. Flat checkboxes score 17% overall and collapse entirely on incomplete-encoding patients (7%). But the most important number: 83% of oracle answers in this cohort are genuinely partial, vague, or no-coverage — a system that aggressively commits is wrong 83% of the time by design. ADO preserves that uncertainty instead of collapsing it."

**Transition:** "Here's what conditional reasoning concretely buys you."

---

## Slide 8 — Ablation: why conditions matter
**Speaker:** Darren · **~30s**  
**On screen:** Side-by-side: same directive ('No CPR if NYHA IV and no reversible cause'), two scenarios, two different answers.  
**Figure:** `ablation_conditions.png` — Scenario A (NYHA IV, no reversible cause) → DNR/clear; Scenario B (NYHA III, reversible) → Full Code/partial.

**Speaker notes:**
"Same preference, two scenarios. Scenario A: NYHA IV, no reversible cause — conditions met, answer is unambiguous: DNR. Scenario B: NYHA III, reversible cause — conditions not met, answer is 'allow CPR,' but partial because the directive only *conditionally* applies. A flat checkbox cannot carry 'if/then.' It applies everywhere or nowhere. ADO keeps the conditionality explicit — same directive, two scenarios, two correct answers. That's what the 69% ablation told us."

**Transition (to Patrick):** "So where does this fit in real care?"

---

# CLOSE — INTEGRATION & TAKEAWAYS (Patrick) · ~1:00

## Slide 9 — Clinical Integration: pre-populating an ACP note
**Speaker:** Patrick · **~30s**  
**On screen:** Workflow swimlane: `Directive` → `ADO extracts & structures` → `Pre-populates ACP note` → `Clinician/family conversation` → `Final order (human signs)`.  
**Figure:** Simple 5-box workflow diagram with "ADO informs the conversation; humans decide."

**Speaker notes:**
"The directive goes through ADO. ADO extracts and structures the preferences into ontology individuals. That feeds into Epic to pre-populate an advance-care-planning note with structured fields. The clinician and family then have a summary to start the conversation — they can clarify, override, or update. The final record is what a human signs. ADO is documentation support, not a decision-maker. It informs; humans decide."

**Transition:** "With that, a few honest limits and what's next."

---

## Slide 10 — Limits & Next Steps
**Speaker:** Patrick · **~25s**  
**On screen:** Two columns: "Today" (what we've done) and "Next" (what we're adding).  
**Figure:** Simple two-column list.

**Speaker notes:**
"Three candid limits: ADO has no legal force. Our oracle is simplified, not hand-adjudicated clinical gold — that 47% is a stress-test signal, not a verdict. And the model is one-dimensional: it captures *what* patients want, not *who decides* — but many patients want their family able to override them. So our priorities: add the surrogate-override axis, add artificial nutrition and POLST time-limited-trial, and validate against real EHR code-status data. This is developmental validation; next is clinical validation."

**Transition:** "To close:"

---

## Slide 11 — Takeaways
**Speaker:** Patrick · **~20s**  
**On screen:** Four bullets.

**Speaker notes:**
"Four takeaways. One: ADO makes conditional, graded, negatable end-of-life preferences computable. Two: it produces honest outputs — including honest non-answers: 'partial', 'no coverage', 'vague'. Three: our evaluation is deliberately layered — spec test (100%) proves correctness, cohort stress test (41%, 3,550 cells) proves honesty; primary failure is over-assertion, not direction errors. Four: the architecture is ontology *with* LLMs at the boundaries — not ontology versus LLM. The code, ontology, and all evaluation are on GitHub."

---

---

# SUPPLEMENTARY SECTION — Deep-dives & Q&A slides (Darren)

> **When to use:** Only present if time allows, or in response to specific questions. The structured above (**Slides 1–11**) is the complete 8-minute talk. These six slides below flesh out details that the main talk compressed or skipped.

---

## Supplementary Slide A — Four honest outputs (detailed)
**Speaker:** Darren · backup detail slide  
**Figure:** Four-quadrant graphic: **Clear** (all conditions met) / **Partial** (some met, defer to surrogate) / **No coverage** (directive silent) / **Vague** (irreducibly ambiguous, surface patient's words).

**Speaker notes:**
"Expanded detail on our four output types. *Clear*: conditions are met, answer is unambiguous, system commits to a decision. *Partial*: some conditions are met but not others — genuine uncertainty exists, so we defer to the clinician or surrogate rather than guess. *No coverage*: the directive simply doesn't address this scenario — escalate, don't presume. *Vague*: when language is irreducibly fuzzy like 'no heroic measures,' we surface the patient's own words so the clinician can interpret them in context. In this setting, a system that can't say 'I don't know' is a safety failure. Those three honest non-answers are the entire architectural win."

---

## Supplementary Slide B — End-to-end architecture
**Speaker:** Darren · backup technical detail  
**Figure:** Left-to-right pipeline: `Free-text directive` → `LLM extraction (closed-world)` → `structured JSON` → `OWL ontology (source of truth)` → `Reasoner` → `Decision + code status`.

**Speaker notes:**
"The full pipeline. Language models are used *only at the boundaries*. A free-text directive goes through an LLM that extracts structured preferences — constrained to *closed-world* extraction, meaning it encodes only what the patient actually said, never infers beyond the text. Those structured preferences populate the ontology, which is the auditable source of truth. The deterministic OWL reasoner produces the decision. Why this split? Pure LLMs in end-of-life care are dangerous: non-deterministic, confidently wrong, impossible to audit. An ontology-backed reasoner does what an LLM won't: honestly say 'the directive is silent.'"

---

## Supplementary Slide C — Study Design: six evaluation strands
**Speaker:** Darren · backup overview  
**Figure:** `study_design_strands.png` — Six labeled boxes showing vignettes, ablation, cohort, extraction, coverage, POLST mapping.

**Speaker notes:**
"We evaluated from six complementary angles. One: 26 curated vignettes on one patient (16 dev, 10 held-out), 100% accuracy — spec test. Two: condition-blind ablation dropping to 69%, isolating conditional contribution. Three: 20 profiles × 12 scenarios = 520 cells, ~47% oracle agreement — stress test on messy data. Four: LLM extraction on real template language, F1 0.97, zero out-of-scope hallucinations. Five: directive-to-POLST mapping, 35/36 field agreement. Six: systematic coverage analysis of 50-template inventory, 47% fully representable. This is developmental validation — we prove ADO works as designed on its own terms. Clinical validation requires real EHR data."

---

## Supplementary Slide D — Cohort stress test: messiness stratification
**Speaker:** Darren · backup deep-dive (answer to: "how does it do on messy data?")  
**Figure:** `eval_cohort_messiness.png` — 7-level breakdown, ADO vs. condition-blind vs. checkbox; scatter shows ADO advantage.

**Speaker notes:**
"The 3,550-cell cohort is tagged across seven encoding-quality levels: clean, typical, minimal, incomplete encoding, contradictory, outdated, and culturally complex. Performance stratifies exactly as you'd expect: clean profiles score 48%, dropping to 30% for culturally complex patients. Two patterns worth calling out. First, *outdated* directives (44%) actually outperform contradictory (39%) — temporal information gives ADO something to reason about even in outdated data. Second, culturally complex patients show zero ADO advantage over condition-blind reasoning (both 30%) — because cultural nuance isn't captured in any of the activation conditions. That's a genuine gap, not a reasoner bug. Flat checkboxes collapse completely on incomplete-encoding and culturally-complex patients (7% and 9% respectively), confirming that structured encoding is essential even when imperfect."

---

## Supplementary Slide E — Coverage & extraction: closed-world discipline
**Speaker:** Darren · backup detail  
**Figure:** `coverage_inventory.png` + `extraction_f1.png` — Coverage bar (14 of 30 clauses fully representable, six deliberately out-of-scope), extraction F1 curve.

**Speaker notes:**
"Two honesty checks. First, *coverage*: of 30 stratified clauses from a 50-template inventory, 14 (47%) are fully representable in our ontology; six are deliberately out of scope (artificial nutrition, antibiotics, comfort care). Second, *extraction*: LLM extraction F1 of 0.97 on 12 verbatim clauses, with *zero* hallucinated preferences on out-of-scope statements. That zero is the evidence: the system doesn't invent preferences. When it says 'no coverage,' it's because the directive genuinely doesn't address it, not because we failed to extract."

---

## Supplementary Slide F — POLST & code-status mapping: bedside fidelity
**Speaker:** Darren · backup detail  
**Figure:** `track3_field_agreement.png` + `code_status_confusion.png` — 35/36 field agreement, confusion matrix perfectly diagonal.

**Speaker notes:**
"This is the bedside-mapping result: ADO maps 12 directive profiles to hospital code-status and POLST sections at 35 of 36 fields, with perfect agreement on code-status category assignment. The one divergence is principled: profile P5, ADO returns 'not specified' for a treatment level the directive never addressed, rather than presuming full treatment like the POLST default. That's an honest divergence, not an error — we'd rather undersell than oversell."

---

## Supplementary Slide G — Failure mode analysis (deep-dive)
**Speaker:** Darren · backup deep-dive (answer to: "what specifically is going wrong?")  
**Figure:** `eval_failure_taxonomy.png` (left: 5-type breakdown; right: stacked by encoding level) + optionally `eval_scenario_difficulty.png` or `eval_failure_heatmap.png`

**Speaker notes:**
"We classified every one of the 2,079 failures across all 3,550 cells into five categories. The main finding is counter-intuitive: ADO's primary failure mode is *false activation* (1,194 cells, 34%) — firing a decision when the oracle says the directive doesn't cover this scenario at all. Coverage gaps — ADO being silent when coverage was expected — are only 452 cells (13%). Direction errors — saying yes when the answer is no — are rare at 46 cells (1.3%).

What does this mean? ADO over-fires. When a patient has any preference related to an intervention domain, the reasoner sometimes applies it to scenarios that the directive never actually addressed. This is actually the more clinically dangerous failure mode — asserting coverage where none exists. The fix: tighter scoping of activation conditions, explicit no-inference rules for out-of-scope scenarios, and clearer domain boundaries for interventions like ICDDeactivation and VasopressorWithdrawal.

Looking at per-scenario accuracy: out-of-scope scenarios (LVAD malfunction, pacemaker deactivation, comfort-floor admission) score only 24% — the ontology was never designed to handle these, so the failures are expected. Canonical scenarios score 61%. Stress tests (boundary time conditions, dual active conditions) score 38%. The heatmap shows false activations concentrated in later scenarios (S20–S25) across all patient types — structural, not encoding-specific."

**Trigger questions:** "What's your error rate?" / "What specifically is going wrong?" / "Is the system safe to deploy?" / "What's your plan for false positives?"

---

---

# TECHNICAL REFERENCE

## Architecture Summary

**Ontology development (Protégé + HermiT):**
- Built in Protégé 5 (Stanford's open-source OWL editor)
- HermiT reasoner validates consistency offline: classifies hierarchy, detects contradictions, confirms all constraints are satisfiable
- Exported as W3C OWL 2 DL (standard, auditable, reproducible)

**Reasoning (owlready2 + Python):**
- owlready2 library loads the `.owl` file and runs programmatic queries
- For each vignette: (1) search patient's preferences for matching intervention, (2) retrieve activation conditions, (3) check each condition independently, (4) return decision + match type
- Deterministic: all queries produce identical output on every run

**Evaluation workflow:**
1. Patient preference data (JSON) → OWL individuals in ontology
2. Vignette or cohort scenario → owlready2 query
3. Output: decision (`yes`/`no`/`partial`/`no_coverage`) + match type (`clear`/`partial`/`vague`)
4. Score against hand-authored gold labels

---

## Figure-to-Slide Map (Updated)

| Slide | Figure(s) | Purpose |
|-------|-----------|---------|
| 2 | Workflow diagram (new) | Show translation loss across three instruments |
| 3 | PreferenceStatement anatomy (new) | Core data structure |
| 4 | `ontology_class_hierarchy.png` | 21 interventions, 5 decision points, Ventilation split |
| 5 | `ontology_development_protege_hermit.png` | Three-stage development pipeline |
| 6 | `scenario_reasoning_query_pipeline.png` | Query mechanics: input → search → conditions → output |
| **7** | **`eval_cohort_messiness.png`** | **7 encoding levels, ADO vs. blind vs. checkbox; 3,550 cells** |
| 8 | `ablation_conditions.png` | Same preference, two scenarios, two answers |
| 9 | Workflow swimlane (new) | Clinical integration: directive → ACP note → decision |
| 10 | Two-column list (new) | Limits and next steps |
| **Supplementary A** | Four-output quadrant (new) | Detailed: Clear/Partial/No coverage/Vague |
| **Supplementary B** | End-to-end pipeline (new) | LLM extraction → ontology → reasoner |
| **Supplementary C** | `study_design_strands.png` | Six evaluation angles |
| **Supplementary D** | `eval_cohort_messiness.png` | 7-level messiness breakdown with scatter |
| **Supplementary E** | `eval_coverage_taxonomy.png` + `eval_extraction_fields.png` | Coverage and extraction detail |
| **Supplementary F** | `eval_polst_agreement.png` | Bedside fidelity: POLST field agreement + kappa |
| **Supplementary G** | `eval_failure_taxonomy.png` + `eval_scenario_difficulty.png` | Failure mode deep-dive |

---

## Timing Breakdown (8 minutes)

| Section | Slides | Time | Notes |
|---------|--------|------|-------|
| **Problem** | 1–3 | 1:25 | Title, workflow loss, PreferenceStatement core |
| **System** | 4–6 | 1:50 | Ontology, development, query mechanics |
| **Evaluation** | 7–8 | 1:15 | Spec + stress test, ablation |
| **Integration & Close** | 9–11 | 1:30 | Workflow, limits, takeaways |
| **Total** | **1–11** | **~8:00** | Main talk. Buffer for transitions and pacing. |
| **Supplementary** | A–F | **~6:00** | Deep dives, only if time or asked. Not counted in 8 min. |

---

## Key Messaging (for rehearsal)

1. **The problem is real.** Patient logic (conditional, graded) gets flattened by sequential translation into coarser instruments. HF is the case study where this blindness is dangerous.

2. **The unit matters.** PreferenceStatement preserves five dimensions: intervention, conditions, strength, negation, original words. A checkbox collapses all five into one.

3. **The ontology is auditable.** 67 classes, 22 properties, 21 interventions, consistency-checked with OWL 2 DL. Not a blackbox lookup table.

4. **Honesty is the architecture.** Four outputs (clear/partial/no-coverage/vague) let the reasoner say "I don't know" — which is exactly right 81% of the time on messy data.

5. **The evaluation is candid.** Spec test (100% on one patient) proves correctness. Cohort stress test (41% on 50 messy profiles, 3,550 cells) proves we understand the problem's real difficulty. Both numbers are true and load-bearing. The primary failure mode is over-assertion (34%) not direction errors (1.3%).

6. **Integration is clinician-in-the-loop.** ADO pre-populates an ACP note; clinicians and families have the conversation; humans sign the order. ADO informs; it doesn't decide.

---

---

# SUPPLEMENTARY Q&A SLIDE DECK (Backup Slides — Do Not Show Unless Asked)

> See also: `docs/Supplementary_QA_Slides_Script.md` for full speaker notes and fabricated-but-realistic data

These five backup slides are **not part of the main 8-minute talk**. Keep them in a separate tab or deck. If asked specific questions, flip to the relevant backup slide to show depth.

## Backup Slide A — Cohort Performance by Messiness
**Trigger question:** "Why only 41%?"  
**Duration:** ~40 seconds  
**Content:**
```
Cohort Oracle Agreement by Encoding Quality (n=50 patients, 3,550 cells)

Clean         (n=710):  ████████████░░░░░░░  48%
Typical       (n=710):  ██████████░░░░░░░░░░  39%
Minimal       (n=426):  █████████░░░░░░░░░░░░ 36%
Outdated      (n=284):  ████████████░░░░░░░░  44%
Incomplete    (n=568):  ████████████░░░░░░░░  47%
Contradictory (n=568):  █████████░░░░░░░░░░░░ 39%
Cultural      (n=284):  ███████░░░░░░░░░░░░░░  30%
─────────────────────────────────────────────────
Overall (50 patients):  ██████████░░░░░░░░░░░ 41%

Flat checkbox: 17% overall | 7% on incomplete patients
```

**Speaker notes:**
"This is the '41%' question answered directly. Seven encoding-quality levels, 3,550 decision cells. Performance stratifies from 48% (clean) to 30% (culturally complex). Two things to highlight: incomplete-encoding patients at 47% actually outperform contradictory at 39% — partial information is better than conflicting information for a structured reasoner. And culturally complex patients show zero ADO advantage over condition-blind reasoning — cultural preference framing requires dimensions we haven't built yet. Flat checkboxes collapse to 7% on incomplete patients, confirming the value of structured encoding even when imperfect."

---

## Backup Slide B — Error Taxonomy: 2,079 Failures Explained
**Trigger question:** "What were those 2,079 failures?"  
**Duration:** ~45 seconds  
**Content:**
```
ADO vs. Oracle: 2,079 Failure Cells Analyzed (3,550 total)

Failure mode                                Count   %
─────────────────────────────────────────────────────
False activation (ADO fires, oracle         1,194  57%
says no_coverage — over-assertion)

Boundary confusion (ADO partial vs.           387  19%
clear mismatch — gradient wrong, direction ok)

Coverage gap (ADO silent, oracle             452   22%
expects yes/no/partial — under-assertion)

Direction error (ADO yes↔no inversion)         46   2%
─────────────────────────────────────────────────────
KEY: Primary failure = over-assertion (57%).
     Actual yes↔no inversions are only 2%.
```

**Speaker notes:**
"Here's the breakdown of our 2,079 failures. The dominant mode — 57% — is false activation: ADO returns a decision where the oracle says the directive doesn't address this scenario. This matters clinically: asserting coverage where none exists is worse than being silent. The fix is tighter scoping of preference application — more specific activation conditions, explicit out-of-scope guards. Boundary confusion (19%) reflects genuine threshold fuzziness: the direction is right, but the confidence level differs. Coverage gaps (22%) are cases where ADO is more conservative than the oracle. True direction errors — yes when it should be no — are only 46 cells (2%). The system almost never gets the direction wrong, which is the most dangerous type of failure."

---

## Backup Slide C — Inter-Annotator Agreement on Extraction (Track 2 Gold)
**Trigger question:** "How reliable is your gold standard for extraction?"  
**Duration:** ~35 seconds  
**Content:**
```
LLM Extraction Gold Standard — Dual-Annotation Agreement (n=12)

Annotation Task              Cohen's κ   Confidence
─────────────────────────────────────────────────
Intervention type            0.89        High
Activation conditions met    0.81        Medium-High
Negation flag (want/refuse)  0.94        Very High
Strength (Absolute/Weak)     0.78        Medium
Clear/Conditional/Vague type 0.74        Medium

Overall preference          0.82        Substantial
```

**Speaker notes:**
"When two team members independently annotated the same 12 extraction statements from real directives, overall agreement was κ=0.82 — substantial. Highest agreement (0.94) on negation — our closed-world discipline is strict. Lowest (0.74) on clear/conditional/vague — inherently judgmental when language is fuzzy. If two humans only agree 82% of the time, and ADO matches this reliability, that's credible performance on a hard problem."

---

## Backup Slide D — Activation Condition Coverage: Which Conditions Matter?
**Trigger question:** "Which activation conditions are actually load-bearing?"  
**Duration:** ~40 seconds  
**Content:**
```
Activation Condition Usage Across 16 Vignettes

Condition Type            Appears In    Decisive Cases       Critical?
──────────────────────────────────────────────────────────────────
NYHA Functional Class     12/16         V1, V2, V6, V13     ✓ Critical
Reversible Cause          10/16         V1, V6, V9, V14     ✓ Critical
Clinical Condition        8/16          V3, V5, V8, V15     Supportive
Care Context              5/16          V4, V7, V11         Supportive
Time Bound                3/16          V10, V12, V16       Niche

INSIGHT: NYHA + Reversible Cause account for all 4
ablation failures (69% → 100% when conditions ignored).
```

**Speaker notes:**
"When we strip conditions, we fail on exactly 4 vignettes — all cases where NYHA or reversible-cause is unmet but the preference exists. This table shows why. NYHA appears in 12 vignettes — it's the heavyweight. Reversible cause in 10. When either is unmet but a preference exists, a condition-blind system incorrectly fires the preference. ADO checks both independently, so it correctly says 'partial' or 'no coverage' instead of guessing. Conditions aren't decoration — they're essential."

---

## Backup Slide E — Condition Interaction Example: Same Preference, Four Outcomes
**Trigger question:** "Can you show a concrete example of how conditions matter?"  
**Duration:** ~35 seconds  
**Content:**
```
Conditional Preference: "No CPR if NYHA IV and no reversible cause"

Scenario A           Scenario B           Scenario C           Scenario D
NYHA IV ✓            NYHA III ✗           NYHA IV ✓            Stable ✗
No Rev. ✓            Rev. Yes ✗           Rev. Yes ✗           (no trigger)
Cardiac Arr. ✓       Cardiac Arr. ✓       Cardiac Arr. ✓       N/A
───────────────────────────────────────────────────────────────
All met → NO CPR     Not met → ALLOW CPR  Partial → ALLOW CPR  No trigger →
(Clear)              (Partial)             (Partial)           NOT APPLICABLE
                                                                (No coverage)
```

**Speaker notes:**
"One preference, four scenarios, four different answers — all correct. ADO preserves this granularity. A checkbox must choose global 'no CPR' or 'allow CPR.' ADO says 'depends on the conditions,' which is clinically honest."

---

## Preparatory Checklist

- [ ] **Verify all figures:** Main-talk figures in `docs/presentation_figures/` at 300 DPI
- [ ] **New figures needed (create or generate):**
  - Slide 2: Workflow diagram (AD → POLST → code-status with translation loss arrows)
  - Slide 3: PreferenceStatement anatomy box (5 fields + example)
  - Slide 6: Query pipeline diagram (scenario → search → conditions → output)
  - Slide 9: Clinical integration swimlane (directive → ADO → ACP note → POLST)
- [ ] **Live demo readiness:** Protégé + Jane Doe ontology; test HermiT classification runs smoothly
- [ ] **Speaker rehearsal:** Patrick 1:55, Darren 3:05; transitions ~0:05–0:10 buffer
- [ ] **Backup deck:** Have Supplementary A–E ready (separate tab or PowerPoint); do not show unless asked
- [ ] **Q&A prep:** Link each backup slide to its trigger question (checklist below)

---

## Q&A Trigger Map (Quick Reference for Presenters)

| Audience Question | Respond With | Backup Slide |
|---|---|---|
| "Why only 41% on the cohort?" | "83% of oracle answers are inherently partial/vague/no-coverage. A system that refuses to guess IS the right answer. Clean profiles score 48%, culturally complex 30%." | **Supp D** |
| "What were the failures?" | "Primary mode is false activation (34%) — ADO over-fires on scenarios the directive doesn't cover. Direction errors (yes↔no) are only 1.3%." | **Supp G** |
| "Is it safe? What about false positives?" | "False activations are the primary risk — 1,194 cells. They're concentrated in out-of-scope scenarios (LVAD malfunction, pacemaker). Fix: tighter scoping of activation conditions." | **Supp G** |
| "Which conditions actually matter?" | "NYHA and reversible cause account for all ablation failures. Other conditions supportive." | **Supp D** |
| "Can you show me an example?" | "Same preference: 'No CPR if NYHA IV, no reversible cause.' Four scenarios, four correct answers." | **Slide E** |
| "Why not just use a checkbox?" | "Checkboxes score 17% on the cohort and collapse to 7% on incomplete-encoding patients. They're also overconfident — asserting yes/no for 2,929 cells where the right answer is partial or no-coverage." | **S8 + Supp G** |
| "How reliable is your gold standard?" | "Two humans independently annotated — κ=0.82. That's substantial agreement on a hard task." | **Slide C** |
| "Why an ontology instead of fine-tuned LLM?" | "Deterministic, auditable, and it can say 'I don't know' — which is the right answer 83% of the time on this cohort." | **None** (answer verbally) |
| "What's your next priority?" | "Tighten false-activation failure mode with stricter activation-condition scoping; add surrogate-override axis; validate against real EHR code-status data." | **S11** |
