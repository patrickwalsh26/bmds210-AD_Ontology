# ADO Presentation — Speaker Notes (June 1, 2026)

**Runtime:** ~8 minutes + ~2 minutes Q&A · **13 slides** · Figures in `docs/presentation_figures/`

---

## The narrative arc (read this once, then present)

| Act | Slides | Story beat |
|-----|--------|------------|
| **I — The gap** | 1–3 | At 2 a.m. clinicians act on code status, not the AD. Directives, POLST, and orders are three layers—and conditional, HF-specific wishes get lost between them. |
| **II — The idea** | 4–7 | ADO encodes *what the patient said* as testable preference objects, refuses false confidence with four honest outputs, and uses LLMs only to *enter* the system—not to *decide*. |
| **III — The evidence** | 8–10 (+ figs) | We evaluated reasoning, extraction discipline, and whether ADO can populate what actually governs the bedside—then show conditionality is the value-add. |
| **IV — The placement** | 11–13 | Expert review placed ADO in the real workflow (ACP note, not legal AD). Limitations are explicit; the contribution is an auditable inference layer. |

**One-sentence pitch:** *ADO is the missing inference layer between what patients document and what teams act on—honest enough to say “the directive is silent” when it is.*

**Handoff split (suggested):** Patrick — Acts I–II (slides 1–7); Darren — Act III–IV (slides 8–13). Swap freely; use the **TRANSITION** lines to pass the mic.

**Live demo option:** If you have 2–3 extra minutes, skip deep-diving slide 10 and run `python demo.py --pause --scenario 1` after slide 7 or 9. See `docs/Live_Demo_Guide.md`.

**Figures slide:** After running `scripts/insert_presentation_figures.py`, a slide titled **EVALUATION FIGURES** is appended (often slide 14). **Drag it to position 10** (right after Quantitative evaluation) so the flow is: results → charts → conditional example.

---

## Slide 1 — Title (~25 s)

**ROLE:** Hook + frame expectations.

**SAY:** We’re Patrick Walsh and Darren Chan. We built the **Advance Directive Ontology**—a computable layer for end-of-life preferences in **advanced heart failure**. Before we show numbers: ADO is **not** a legal advance directive. It’s decision support that helps teams reason over what patients actually said and pre-populate advance care planning notes.

**TRANSITION → 2:** *“To see why that matters, start where clinicians actually live—the acute crisis.”*

---

## Slide 2 — Clinical problem (~45 s)

**ROLE:** Act I — name the workflow failure.

**SAY:** Preferences flow through **three instruments**: the advance directive (values), POLST (portable orders), and **code status** (what you act on at 2 a.m.). The tragedy isn’t only missing documents—it’s **translation loss**: a patient’s *conditional* wish becomes a coarse checkbox or an order that can’t carry “only if.”

**POINT AT:** The ventilator quote—temporary-if-reversible vs never-indefinitely.

**SAY:** The cliché that “directives are unreadable free text” is only half right. California and UC forms are mostly **checkboxes**. The deeper problem is **low resolution** and **disease blindness**.

**TRANSITION → 3:** *“Heart failure is where that blindness hurts most.”*

---

## Slide 3 — Why HF (~35 s)

**ROLE:** Justify scope; make HF feel inevitable, not arbitrary.

**SAY:** HF is unpredictable, device-heavy, and patients bounce through the ED and ICU—so teams repeatedly face **time-pressured interpretation**. We model five decision points on the slide. Generic templates rarely mention **ICD deactivation, LVAD, or inotropes**—yet hundreds of thousands of HF patients have ICDs.

**TRANSITION → 4:** *“So we asked: what’s the smallest object that preserves the patient’s logic?”*

---

## Slide 4 — Approach (~45 s)

**ROLE:** Act II — introduce PreferenceStatement.

**SAY:** A **PreferenceStatement** links an intervention to **activation conditions**, strength, negation, and the patient’s **verbatim words**. The reasoner’s question is always: *given this scenario, does this preference actually apply?*

**WALK:** The 72-hour vasopressor example on the slide.

**SAY:** Auditable means you never lose the quote behind the inference.

**TRANSITION → 5:** *“Here’s how much structure we built around that idea.”*

---

## Slide 5 — Ontology scope (~35 s)

**ROLE:** Credibility — this is real ontology engineering, not a prompt.

**SAY:** **67 classes, 22 properties, 21 interventions**—finer than any single template in our 50-form inventory. SNOMED grounding where we can. Ventilation alone distinguishes temporary vs indefinite; devices cover ICD/LVAD; dialysis is acute vs chronic vs withdrawal.

**TRANSITION → 6:** *“Granularity only helps if the system knows when not to answer.”*

---

## Slide 6 — Four outputs (~40 s)

**ROLE:** Safety thesis — honest non-answers.

**SAY:** Four outputs: **Clear, Partial, No coverage, Vague.** Partial means defer; no coverage means **do not presume**; vague means show the patient’s imprecise language back.

**PUNCHLINE:** A checkbox—or an overconfident LLM—can’t say **“I don’t know.”** ADO can. That’s the safety feature.

**TRANSITION → 7:** *“Here’s how we wired that into a pipeline.”*

---

## Slide 7 — Architecture (~45 s)

**ROLE:** Architecture slide — LLM at boundary only.

**SAY:** **LLMs extract; the ontology owns truth; the reasoner decides.** Closed-world extraction: only what the patient stated. Out-of-scope lines—nutrition, antibiotics—must extract as **nothing**, or “no coverage” is meaningless.

**TAGLINE:** Ontology **with** LLMs, not versus LLMs.

**TRANSITION → 8:** *“We tested that claim three ways.”*

**OPTIONAL DEMO TEASE:** *“We can show this live in thirty seconds after the results—scenario 1 is CPR in NYHA IV arrest.”*

---

## Slide 8 — Study design (~45 s)

**ROLE:** Act III — earn trust before numbers.

**SAY:** Five strands: pipeline sanity check; **16 vignettes** with team gold; **ablation** re-scoring the same vignettes without activation conditions; **LLM extraction** on real template language plus two out-of-scope traps; **12 profiles → code status/POLST** against **POLST’s own semantics**; plus **Dr. Magnus** expert review.

**CAVEAT (one breath):** Gold is team-adjudicated but grounded in real templates and independent POLST definitions.

**TRANSITION → 9:** *“Here’s what we found—and the figures make the pattern obvious.”*

**POINT AT FIGURES** (if inserted): overview bars + field agreement.

---

## Slide 9 — Quantitative results (~55 s)

**ROLE:** Flagship — three tracks in one breath, then ablation.

**SAY — Track 1:** **16/16** decisions and match types across clear, partial, no coverage, and vague—including time bounds and care-context gating.

**SAY — Track 2:** Extraction **F1 0.97**; **zero** hallucinations on out-of-scope nutrition and antibiotics.

**SAY — Track 3:** **35/36** fields (**97%**) against POLST-semantics gold; code status and POLST A perfect; POLST B **11/12**; κ **1.00 / 1.00 / 0.88**.

**SAY — Ablation:** Ignore conditions → **75%**—exactly the four conditional vignettes. Conditionality isn’t decoration; it prevents false confidence.

**POINT AT:** `eval_overview.png`, `track3_field_agreement.png`, `ablation_conditions.png` (or embedded charts).

**TRANSITION → 10:** *“One pair of profiles shows why that matters clinically.”*

**IF SHORT ON TIME:** Mention P9/P10 flip verbally; skip slide 10.

---

## Slide 10 — Conditional example (~40 s)

**ROLE:** Clinical “aha” — same words, different scenario.

**SAY:** *“No CPR if NYHA IV and no reversible cause.”* Scenario A → **DNR, clear**. Scenario B → **Full code, partial**. A flat checkbox must over-apply or discard the condition.

**POINT AT:** `conditional_p9_p10.png` if on slide.

**TRANSITION → 11:** *“An ethicist helped us place this in the real workflow.”*

---

## Slide 11 — Clinical integration (~40 s)

**ROLE:** Act IV — Magnus reframe.

**SAY:** Dr. Magnus: you can’t treat this as a signed AHCD—it’s closer to an **ACP progress note**. Workflow: directive → ADO → pre-populated ACP note → **conversation** → POLST/code status. Conversation can override; when it doesn’t happen, structured preferences are the best record of what the patient said.

**TRANSITION → 12:** *“We’re explicit about what we did not solve.”*

---

## Slide 12 — Limits (~35 s)

**ROLE:** Mature science — limits without apologizing away the contribution.

**SAY:** No legal force; **one-dimensional** today (what, not who decides); coverage gaps (nutrition, antibiotics); temporal workarounds; team gold standards; EHR validation future work.

**TRANSITION → 13:** *“Four sentences to leave you with.”*

---

## Slide 13 — Takeaways (~25 s)

**ROLE:** Close + invite questions.

**SAY:** Read the four bullets on the slide. Offer repo URL. Invite questions.

**IF DEMO:** *“Happy to run one live scenario at the podium—CPR in arrest, or the free-text pipeline if we have API access.”*

---

## Q&A cheat sheet

| Question | Answer |
|----------|--------|
| Legal AD? | No — ACP documentation support. |
| Why not ChatGPT end-to-end? | Non-deterministic; over-confident; no auditable “silent.” |
| Weakest evidence? | Team gold; one principled POLST B divergence (P5). |
| Precision &lt; 1? | One over-split of “no heroic measures” into two vague prefs. |
| What’s next? | Who-decides axis; nutrition; time-limited trial; MIMIC/EHR. |

---

*Embedded notes in `ADO_powerpoint_presentation.pptx` are synced via `scripts/update_presentation_notes.py`.*
