# ADO Presentation — Speaker Notes (June 1, 2026)

**Target:** ~8 minutes of content + ~2 minutes Q&A (13 slides ≈ 35–50 s each; title and closing shorter).

**Split suggestion:** Patrick — slides 1–4, 8–9; Darren — slides 5–7, 10–13 (swap as you prefer).

**Numbers source of truth:** `query_evaluation.py`, `track3_evaluation.py`, `extraction_evaluation.py`, `docs/Quantitative_Evaluation_Plan.md`, `docs/Final_Report.tex`.

---

## Slide 1 — Title (~30 s)

**Say:** Good morning/afternoon. We are Patrick Walsh and Darren Chan. Today we present the **Advance Directive Ontology (ADO)**: a computable representation of end-of-life care preferences scoped to **advanced heart failure**. ADO is not a legal advance directive—it is a **decision-support layer** that helps clinicians reason over what patients actually said and pre-populate advance care planning documentation.

**Transition:** Start with why the current workflow breaks down at 2 a.m.

**If asked:** “Computable” means OWL 2 + a reasoner, not just NLP paraphrase.

---

## Slide 2 — Clinical problem (~45 s)

**Say:** End-of-life preferences move through **three different instruments**: the advance directive captures values and wishes; POLST turns some of that into portable medical orders; **code status** is what the team acts on in an acute crisis. The loss is in the middle—conditional, graded wishes get flattened.

**Point to diagram:** Directive → POLST → code status, then “acute crisis: what do we do?”

**Say:** The usual story—that directives are unreadable free text—is **only partly true**. California and UC forms are mostly checkboxes. The deeper problem is **low resolution** and **disease blindness**: a checkbox can say ventilator yes/no but not “temporary if reversible, never indefinitely.”

**Transition:** We chose advanced HF because those gaps are impossible to ignore.

---

## Slide 3 — Why HF scope (~40 s)

**Say:** Heart failure is unpredictable, device-heavy, and patients cycle through the ED and ICU repeatedly—so preference interpretation is **time-pressured** and recurring. We model **five decision points**: CPR, ventilation, ICD/device management, vasopressors/inotropes, and dialysis.

**Say:** Generic templates rarely mention **ICD deactivation, LVAD decisions, or inotrope escalation**—yet roughly 200,000 HF patients have ICDs. That is why HF is the right stress test for a new ontology.

---

## Slide 4 — Approach (~45 s)

**Say:** The core unit is a **PreferenceStatement**: intervention + activation conditions + strength + negation + the patient’s **verbatim text**. The reasoner asks: “Given *this* clinical scenario, does this preference actually apply?”

**Walk the example:** “Do not continue vasopressors if no improvement after 72 hours” → vasopressor withdrawal, time bound 72h, strong/conditional, not negated, original quote preserved.

**Say:** Preserving original language keeps the system **auditable**—clinicians see the patient’s words behind the inference.

---

## Slide 5 — Ontology scope (~40 s)

**Say:** ADO has **67 classes, 22 properties, 21 intervention subclasses** across those five decision points—more granular than any single template in our 50-form inventory. Concepts are grounded in **SNOMED CT** where possible for interoperability.

**Quick pass:** ventilation distinguishes temporary vs indefinite; devices include ICD/LVAD/pacemaker; dialysis acute vs chronic vs withdrawal.

---

## Slide 6 — Four outputs (~45 s)

**Say:** We deliberately refuse to force a binary answer. The reasoner returns one of four **honest** outputs:

| Output | Meaning |
|--------|---------|
| **Clear** | Conditions met; preference applies unambiguously |
| **Partial** | Some conditions unmet or uncertain → defer to surrogate |
| **No coverage** | Directive silent for this scenario—do not presume |
| **Vague** | Surface imprecise language (“no heroic measures”) |

**Say:** A checkbox—or an overconfident LLM—cannot say “I don’t know.” **That visibility is the safety feature.**

---

## Slide 7 — Architecture (~45 s)

**Say:** **LLMs only at the boundary.** Closed-world extraction turns structured or free-text directives into validated JSON; we populate OWL individuals; a **deterministic** scenario reasoner produces the four-category output plus **code status and POLST mapping** for bedside alignment.

**Emphasize closed-world rule:** Extract only what the patient explicitly stated—do not map out-of-scope content (nutrition, antibiotics) to the nearest covered class. That discipline is what makes “no coverage” trustworthy.

**Tagline:** Ontology **with** LLMs, not ontology **versus** LLMs.

---

## Slide 8 — Study design (~50 s)

**Say:** We asked two questions: does the reasoner decide correctly on clinical vignettes, and can ADO **derive what actually governs the bedside**—code status and POLST—from realistic preference profiles?

**Walk the five bullets:**

1. **Pipeline validation** — example patient populates end-to-end (9 preferences, 50 individuals, no errors).
2. **16 vignettes** — all five decision points, all four output types; gold = team-adjudicated expected decisions.
3. **Ablation (post-hoc)** — same 16 vignettes re-scored **as if activation conditions were ignored**: 12/16 (75%) vs 16/16 (100%). All four errors are on **partial/conditional** cases—false confidence without condition modeling. *(Not a separate SWRL run; document as sensitivity analysis.)*
4. **LLM extraction** — 12 real-template statements, 15 in-scope gold preferences, **2 deliberately out-of-scope** statements.
5. **Track 3 + expert review** — 12 inventory-grounded profiles vs **POLST published semantics** (gold independent of ADO logic); Dr. David Magnus (Stanford Biomedical Ethics).

**Caveat to state if asked:** Gold standards are team-authored but grounded in real templates and POLST definitions; blind second-rater sheets exist in the repo.

---

## Slide 9 — Quantitative results (~60 s) — **FLAGSHIP SLIDE**

**Say:** On **16 vignettes**, we achieved **16/16 decision accuracy and 16/16 match-type accuracy**—including temporal bounds (72h vasopressor), care-context gating (hospice vs ICU), and vague-vs-clear precedence.

**LLM extraction:** **Precision 0.94, recall 1.00, F1 0.97**; negation, preference type, and conditionality **15/15** on matched preferences. Critically: **zero hallucinations** on out-of-scope nutrition and antibiotics text—the model extracted nothing.

**Track 3 (bedside mapping):** Over **12 real-world template profiles** (CA AHCD, Texas OOH-DNR, NHS Wales ADRT, Five Wishes, VA, dementia directive, etc.), ADO agreed with POLST-semantics gold on **35/36 fields (97%)**:

- Hospital code status: **12/12**
- POLST Section A: **12/12**
- POLST Section B: **11/12**
- Exact profile (all three fields): **11/12**
- Cohen’s κ: **1.00 / 1.00 / 0.88** (code status / POLST A / POLST B)

**Ablation punchline:** Ignoring activation conditions drops accuracy to **75%**—exactly the four conditional vignettes—showing conditionality is doing real work, not decoration.

**Optional depth if time:** Profile **P9 vs P10**—same directive, condition met vs unmet → **DNR ↔ Full code**. Profile **P5** divergence: when “permanent unconsciousness” is not met, ADO returns POLST B **Not specified** rather than presuming Full Treatment—honest non-presumption, not a bug.

---

## Slide 10 — Conditional example (~50 s)

**Say:** “No CPR if NYHA IV and no reversible cause.” In **Scenario A** (NYHA IV, no reversible cause), ADO → **DNR, clear match**. In **Scenario B** (NYHA III, reversible cause), conditions fail → **Full code, partial match**.

**Say:** A flat checkbox must either over-apply the refusal or throw the condition away. ADO carries the **if/then** structure that POLST and code status alone cannot represent—and flags when the condition applies.

---

## Slide 11 — Clinical integration (~40 s)

**Say:** Expert review with **Dr. Magnus** reframed the product: *“You can’t think of these as AHCDs… This is more like a progress note.”* ADO’s near-term fit is **pre-populating an Epic-style ACP note** after a family meeting—not replacing a signed legal directive or POLST.

**Walk workflow:** Existing AD → ADO structured preferences → ACP note pre-population → **provider conversation** (can clarify or override) → final ACP + POLST/code status.

**Say:** Source-of-truth priority matters: conversation can supersede the document, but when nobody reopens the question, structured preferences are the best record of what the patient said.

**Magnus quotes if asked:**

- Free text: *“It isn’t largely a problem of free text.”*
- Dimensionality: preferences are **two-dimensional**—what intervention **and** who decides (surrogate override ~54% in studies).

---

## Slide 12 — Limits + priorities (~40 s)

**Say:** Limitations are honest:

- **No legal force** — decision support only.
- **One-dimensional today** — models *what*, not yet *who decides* (highest-priority extension).
- **Coverage gaps** — artificial hydration/nutrition, antibiotics, comfort care not in ontology yet.
- **Temporal limits** — numeric hour bounds, not full temporal logic.
- **Validation** — team gold standards; MIMIC-IV / real EHR validation in progress.

**Design principle:** Surface uncertainty; do not replace clinicians or surrogates.

---

## Slide 13 — Takeaways (~30 s)

**Say:**

1. ADO makes **conditional, graded, negatable** EOL preferences computable in HF.
2. The safest outputs include **honest non-answers**—no coverage, partial, vague.
3. **LLMs extract; the ontology and reasoner own inference.**
4. Near-term product: **ACP documentation support**, not a legal directive.

**Close:** Questions welcome. Repo: `https://github.com/patrickwalsh26/bmds210-AD_Ontology`

---

## Q&A cheat sheet

| Question | Short answer |
|----------|----------------|
| Is this a legal AD? | No — ACP note pre-population; complements POLST/code status. |
| Why not just use an LLM? | Non-deterministic; over-confident; can’t audibly say “silent.” |
| Weakest result? | Team-authored gold; single POLST B miss (P5 principled). |
| Precision &lt; 1? | One over-split: “no heroic measures” → two vague interventions. |
| What’s next? | Who-decides axis; artificial nutrition; time-limited trial; EHR validation. |

---

*Speaker notes are also embedded in `ADO_powerpoint_presentation.pptx` (Notes pane).*
