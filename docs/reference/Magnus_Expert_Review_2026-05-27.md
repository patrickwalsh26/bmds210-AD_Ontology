# Expert Review — Dr. David Magnus (2026-05-27)

**Reviewer:** Dr. David Magnus, Thomas A. Raffin Professor of Medicine and Biomedical Ethics; Director, Stanford Center for Biomedical Ethics; co-chair, Stanford Hospital Ethics Committee.
**Format:** 7 written comments annotated on the *Expert Review Packet* PDF, plus a ~15-minute meeting (Patrick Walsh, Darren Chan, Dr. Magnus).
**Status:** This completes the qualitative / expert-review portion of the evaluation (Track 4). Source artifacts: `Advance_Directive_Ontology__ADO___Expert_Review_Packet DM comments.pdf` (annotations) and live meeting notes.

This document is the faithful record. Verbatim quotes are in quotation marks. It is the source for the "Expert Review" subsection of Section 5 (Evaluation) in the final report.

---

## 1. The headline: this is not an AHCD

The single most consequential piece of feedback is that the project has mis-framed what it is building.

> "You can't think of these as AHCDs from a legal perspective. The patient has not signed anything and it likely does not meet the regulatory requirements. **This is more like a progress note.**" *(PDF comment, p.2)*

In the meeting he expanded on this:

- A legally operative AHCD takes a serious, deliberate process — the Stanford Letter Project becomes a **legal document** only after years of work; an AHCD "must be legally reviewed, notarized," and there is "no obligation for clinicians to be involved."
- Therefore **do not think of ADO as producing or interpreting an AHCD.** What it actually resembles, and where it could plausibly live in a real workflow, is an **Advance Care Planning progress note** — EPIC already has an ACP note type / template, and the natural fit is **pre-populating** what goes into that note, with the **patient or decision-maker** populating it.

**Implication for the project:** reframe ADO from "computable advance *directive*" to a **decision-support / advance-care-planning documentation aid** — explicitly *not* a legal instrument, explicitly *not* a substitute for an AHCD, POLST, or code-status order. This is a framing change that runs through the report's title, abstract, problem statement, and limitations.

---

## 2. The "free-text problem" premise is overstated

The packet's motivating hook — ADs are free-text and unreadable at 2 AM — is only partly right.

> "Many (most?) AHCD directives—especially the good ones, eg the UC designed one—have more or less designed them as check boxes. So does the standard California one, but fewer and more ambiguous, less helpful checks. **But it isn't largely a problem of free text.**" *(PDF comment, p.1)*

From the meeting:

- The **California AD** has only a handful of checkboxes (paraphrased: unable to make decisions; going to die with reasonable certainty; terminal condition; burdens outweigh the benefits).
- The **UC-system directive** is also checkbox-driven and is the better-designed instrument.

**Implication:** the problem ADO addresses is *not* primarily "free text is unparseable." The real gaps are (a) checkbox forms are **low-resolution / lose conditionality**, and (b) **device- and HF-specific decisions (ICD/LVAD/inotropes) are simply absent** from the standard forms. The report's framing should pivot from "free text" to "**existing structured forms are too coarse and HF-blind**," which is actually a *stronger* and better-supported version of our argument and survives Magnus's critique.

---

## 3. What actually governs the bedside: POLST + code status

> "In emergency situations it is code status orders and POLST that matters, not AHCD." *(PDF comment, p.1)*

> "The decision points miss decision about artificial hydration/nutrition. See POLST. But also see our Code status ordering system for a fuller range of options that can be easily accessed." *(PDF comment, p.1)*

Meeting detail on the **code status system** (the thing that is actually actionable in an emergency):

- **POLST** is outpatient — patients "collect and take to the ED"; it feeds the inpatient **code-status system**.
- On a rapid-response call, ~**82% of patients are full-code, ~18% are not**. In HF the non-full-code set splits into **DNR** (do-not-resuscitate) and **DNI** (do-not-intubate); on the floor there is also a **"do not escalate to ICU"** order, i.e. a **no-escalation** status.
- "Most common" documented status is effectively **"did not discuss."** For most patients the right action is "do what you can to make them better"; the population where this kind of structured EOL reasoning matters is the **critically-ill / terminal / frail ~18% of hospitalized patients.**

**Implications:**
- Add an **artificial hydration / nutrition** decision point (currently "deferred to future work" in the coverage table — Magnus flags it as a real miss).
- Add a **"No Escalation"** output / status to the reasoner, mirroring the real code-status taxonomy (full-code / DNR / DNI / do-not-escalate-to-ICU).
- Position ADO **relative to POLST and the code-status system**, not as a replacement for them.

---

## 4. The system is one-dimensional; real preferences are multidimensional

This is the deepest technical critique and ties directly to **Question 2 (surrogate hierarchy)**.

> "Answer to Question 2 is that it depends. Under the law, a capacitous patient's preferences trump. But two major studies show that vast majority of patients say ignore my wishes and do what my family says. And AHCD's normally only come into play when a patient has lost capacity (with the exception when they want their surrogates to make decisions for them even when they have capacity). In reality, it actually depends on the clinical situation and the wishes and the amount of evidence. **One problem with this system is that it is one dimensional. But patient preferences are often two or more dimensional.** E.g., I don't want to be intubated, but I want my family to be comfortable with what happens so do what they say. **The letter project and the UC AHCD directive add that level of dimensionality.**" *(PDF comment, p.2)*

Meeting notes on the same point:

- Patients have preferences about **what** they want **and** about **who** they want making decisions.
- A patient may explicitly **grant the surrogate authority to override** the patient's own stated content preferences — and ~**70% say override.** That override authority is itself a preference "that matters under the law."

**Implication (this is the most important system change):** ADO needs a second dimension — a **who-decides / surrogate-authority** axis layered on top of the **what-intervention** axis. A documented preference should be able to carry an explicit "but defer to my surrogate" qualifier that changes the reasoner's output (e.g., a clear "no intubation" preference paired with "do what my family says" should *not* return a hard `no` — it should surface the override authority). This is exactly the dimensionality the Letter Project and UC AHCD capture and ADO currently flattens.

---

## 5. Question-by-question answers

**Q1 — 4-category output / "No coverage" misread risk.** Not addressed head-on in writing; folded into the broader point that no formal system captures everything (see Q4). The reframing toward code-status semantics (§3) is the more useful response — align outputs with full-code / DNR / DNI / no-escalation rather than inventing bespoke categories.

**Q2 — Surrogate hierarchy.** See §4. *"It depends."* Capacitous patient trumps under law; but most patients defer to family; AHCDs only activate on loss of capacity (except when the patient pre-delegates to a surrogate). Depends on clinical situation, the wishes, and the amount of evidence. → drives the multidimensionality requirement.

**Q3 — Liability and defensibility.**
> "Question 3—liability exists no matter what you do. This will not have the legal force of an actual AHCD, but suits are rare anyway." *(PDF comment, p.2)*

Reassuring on liability, but reinforces §1: the artifact has **no legal force.** Frame ADO as decision support, not a legal safeguard.

**Q4 — Category error / over-formalization.**
> "Question 4—there is always ambiguity in RW management of patients at EOL with patient preferences just one (often vague) input. No formal system will capture everything—for example, nothing in here corresponds to the POLST (and very useful) concept of **'Time limited trial.'**" *(PDF comment, p.2)*

So: it's not a category error per se, but patient preferences are "just one (often vague) input" among many. Concrete miss: the **time-limited trial** — agreeing to an intervention for a bounded period to resolve clinical *prognostic* uncertainty, then reassessing. → add a **time-limited-trial** construct (note this is distinct from our existing `hasTimeBoundHours` withdrawal logic; a TLT is a prospectively-agreed trial window, not a withdrawal threshold).

**Q5 — Documented vs. situational preferences.**
> "I think question 5 assumes incorrectly that this can serve as a legal AHCD. It can't and shouldn't. And the data suggests some limits to the value of AHCD in end of life decision making anyway." *(PDF comment, p.2)*

Reinforces §1 again, and adds a sobering evidence note: the literature shows **limits to the value of AHCDs** in actual EOL decisions. The honest framing is that ADO is one structured input into a relational, evidence-weighed process — not an oracle.

---

## 6. Concrete, named follow-ups from the meeting

- **EPIC Playground** (fake patient / fake chart) to inspect (a) the ACP **note type** and (b) the **SmartPhrase / SmartText template** — to see exactly what a real ACP progress note looks like and what pre-population would target.
- **People to talk to:** Stephanie Harman (palliative care), Shari Nadari. *(spellings to confirm)*
- EPIC has **built-in summarization tools** — be deliberate about limiting what ADO surfaces rather than duplicating EHR features.
- Workflow reality: a **family meeting** is typically followed immediately by an **ACP / progress note** — that note is the natural target artifact for ADO.
- Comparison point: **UCLA CVICU** runs with **no AD, no POLST** in a very tight unit where all physicians share context — a reminder that documentation tooling matters most outside such tightly-coupled teams.

---

## 7. Net assessment and action items

Magnus did **not** dismiss the technical work; he reframed where it sits. The reasoning engine, conditional/negatable/graded encoding, and 4-category honesty are still valuable — but as a **pre-population aid for an Advance Care Planning progress note** that complements POLST and the code-status system, **not** as a computable AHCD.

**Report / framing changes (low risk, high value):**
1. Reframe the artifact: ACP-progress-note pre-population & decision support, explicitly not a legal AHCD. Retitle / rewrite abstract, problem statement, limitations.
2. Replace the "free-text is unreadable" hook with "existing structured forms are too coarse and HF-blind." Acknowledge UC/CA checkbox ADs.
3. Position relative to POLST + code-status system (add to the "Where ADO Fits" layer table).
4. Add the expert-review writeup (this document) as Section 5.

**System changes (design decisions — need scoping):**
5. **Add multidimensionality:** a who-decides / surrogate-override axis (highest-value, hardest).
6. **Add hydration/nutrition** as a 6th decision point.
7. **Add a "No Escalation" output**, aligned to real code-status taxonomy (full-code / DNR / DNI / no-escalate-to-ICU).
8. **Add a time-limited-trial** construct, distinct from withdrawal time-bounds.

**Evaluation:**
9. Qualitative / expert-review track is **complete** (this document).
10. Remaining: the **quantitative** analysis (expanded vignette suite, per-intervention precision/recall, coverage analysis, SWRL ablation, fidelity study).
