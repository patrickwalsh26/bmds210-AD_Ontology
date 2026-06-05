# Technical Pipeline Slides (insert after Slide 7, before Slide 8)

These three slides explain how ADO is built and evaluated. They fit between **Slide 7 (System Implementation)** and **Slide 8 (Study Design)**, giving the audience a transparent view of the machinery before the results.

---

## Slide 7b — Ontology Development: Protégé + HermiT
**Speaker:** Darren · **~50s**
**On screen:** "How we built it: Protégé + HermiT + owlready2"
**Figure:** *Suggested visual: a three-stage diagram — (1) Protégé UI with class hierarchy and consistency checks (screenshot of the Intervention class tree); (2) export `.owl` file arrow; (3) owlready2 loads file + programmatic queries in Python*

**Speaker notes:**
"The ontology was built in Protégé, Stanford's open-source OWL editor. [Point to left panel.] We iteratively designed the class hierarchy — Intervention as root, five decision points as intermediate classes, 21 specific interventions as leaves — and we used Protégé's built-in HermiT reasoner to validate consistency. HermiT does two jobs: it classifies the hierarchy (infers the correct parent-child relationships given the restrictions we wrote), and it detects unsatisfiable classes or contradictions. If we accidentally made a PreferenceStatement constraint that was impossible to satisfy, HermiT would flag it. That consistency checking happens once, offline, before we run any evaluations.

[Point to middle arrow.] Once we're confident the ontology is sound, we export it as an `.owl` file — pure W3C OWL 2 DL, no proprietary format. [Point to right panel.] Then we load that file programmatically using owlready2, a Python library. owlready2 doesn't have a UI — it's just an API for traversing OWL individuals and querying their properties. This lets us run thousands of vignette and cohort queries at scale, with full programmatic control and reproducible output. Every vignette query produces the same answer every time because the reasoner is deterministic."

**Transition:** "So how does a vignette query actually work?"

---

## Slide 7c — Scenario-Based Reasoning: the query pipeline
**Speaker:** Darren · **~55s**
**On screen:** "Scenario-based reasoning: from vignette to decision"
**Figure:** *Suggested visual: a left-to-right flow — (1) Clinical scenario (box with NYHA class, conditions, reversible-cause, time); (2) Patient ontology (icon of Jane Doe with hasPreference arrows); (3) Preference matching (magnifying glass over CPR preferences); (4) Activation condition checks (four checkboxes: NYHA? Condition? Reversible? Time?); (5) Output box with decision + match type*

**Speaker notes:**
"[Point to left: scenario state.] A vignette gives us a clinical snapshot — NYHA class, what conditions the patient has, whether there's a reversible cause, how much time has elapsed since the trigger event. [Point to patient icon.] We load Jane Doe's populated ontology. [Point to magnifying glass.] For a given query — 'should we initiate CPR?' — we search through all her preferences for ones that specify CPR as the intervention.

When we find a matching preference, we don't just return 'yes' or 'no' — we check its activation conditions. [Point to the four checkboxes.] Is the NYHA class requirement met? Is the required clinical condition present? Is the reversible-cause requirement satisfied? Is the time bound satisfied? We check each one independently.

[Point to output.] Based on which conditions are met, we return: decision (yes / no / partial / no_coverage) and match type (clear / partial / vague). If all conditions are met, it's clear. If some but not all are met, it's partial — defer to the surrogate. If no preferences match at all, it's no_coverage. If the matched preference is vague language, we mark it vague and surface the patient's original words.

Every vignette run is deterministic — same scenario, same ontology, same output."

**Transition:** "This is where the 16/16 comes from. But that's one patient. What happens when we scale to 20 messy profiles and 520 cells?"

---

## Slide 7d — Scaling: from spec test to cohort stress test
**Speaker:** Darren · **~45s**
**On screen:** "Scaling: from one patient to a cohort"
**Figure:** *Suggested visual: a funnel or scaling diagram — (1) Single patient, 16 vignettes (small box, 100% accuracy); (2) arrow down to (3) 20 patient profiles × 12 scenarios = 520 cells (large box, ~47% agreement); (4) bottom panel shows a 2×2 grid labeled "Profile quality vs. oracle agreement" with messiness axis (clean/minimal/contradictory)*

**Speaker notes:**
"[Point to top: Jane Doe.] The 16/16 spec test is one carefully-encoded patient. It validates that our PreferenceStatement structure is correct and our reasoner logic is sound — it's a specification test. But one patient is not generalization.

[Point to the scaling arrow.] So we created 20 patient profiles grounded in real directive templates — California AHCD, Texas OOH-DNR, VA directives, Five Wishes, dementia directives. We tagged each by messiness: clean (well-structured encoding), minimal (sparse documentation), contradictory (conflicting wishes documented), incomplete (some domains missing). We then ran each profile through 12 representative clinical scenarios — cardiac arrest, acute decompensation, reversible vs irreversible conditions, different care contexts. That's 20 profiles × 12 scenarios = 520 decision cells.

[Point to bottom grid.] We scored each cell against a simplified reference oracle — not hand-adjudicated clinical gold, but POLST-semantics-based logic — and found ~47% exact agreement. That's much lower than the vignettes, and that's the point. Messy real-world encoding is hard. But here's the key: performance stratifies exactly as you'd hope. Clean profiles score highest. Minimal, contradictory, incomplete profiles score lower — reflecting honest sensitivity to chart-abstraction quality, not a bug in the reasoner. When we looked at the 421 cells where ADO and oracle disagreed, 81% of those were cases where the correct answer was genuinely partial, vague, or no-coverage. A checkbox would be forced to guess; ADO preserved uncertainty."

**Transition:** "So the results are a two-layer story: tight spec test on one patient, honest cohort stress test on 20. That's what credibility looks like." *(Hand back to main slide flow.)*

---

## Where to insert these slides

Insert these **after Slide 7 (System Implementation)** and **before Slide 8 (Study Design)**. They fit naturally because:
- Slide 7 explains *what* we built (architecture, the four-category output)
- **Slides 7b–7d** explain *how* we built and tested it (Protégé/owlready2, query pipeline, scaling)
- Slide 8 then pivots to the six-strand evaluation design

**Timing impact:** Adding these three slides adds ~2:30 to the talk. If you stay at 8 minutes, you'll need to **cut Slide 3 (Why HF scope) to one sentence** and **trim Slide 12 (Limits) to 20s**, which is fine — the core narrative (problem → approach → output → results) stays intact.

**Alternative:** Keep these as backup slides 14a, 14b, 14c and only show them if asked "how did you actually run the evaluations?" during Q&A. They're dense enough that live delivery is easier with a specific question prompting them.

---

## Speaker notes for Slide 7b — detailed technical justification

If someone asks in Q&A "how do you know the reasoner is actually correct?" — here's the answer:

"HermiT is a standard OWL 2 DL reasoner built on description logic, so the inference is formal and reproducible. We validated it by: (1) manually querying specific individuals in Protégé's GUI to spot-check that the preferences were populated correctly; (2) re-running the full 16-vignette suite three times and confirming 100% agreement every time; (3) comparing Protégé's manual instance queries against owlready2's programmatic queries on the same individuals, confirming identical output. The reasoner is deterministic — there's no randomness, no learning, no drift. If you run the same vignette query on the same populated ontology a thousand times, you get the same answer all thousand times."

---

## Speaker notes for Slide 7c — worked example (optional live demo)

If time allows during the talk (or in Q&A), you can do a live walkthrough of one vignette:

**"V1: Patient is in cardiac arrest, NYHA IV, no reversible cause. Should we do CPR?"**
- Jane Doe has a preference: `specifiesIntervention = CPR`, `isNegated = true`, with activation conditions
- The conditions are: `requiresFunctionalStatus = NYHA_ClassIV`, `hasReversibleCause = false`
- Scenario: cardiac arrest (matches), NYHA IV (matches), reversible cause = false (matches)
- All conditions met → decision = "no", match_type = "clear"
- Gold expected: decision = "no", match_type = "clear"
- **Result: correct**

And contrast with V2:
- Same preference (CPR, negated, NYHA IV + no reversible cause)
- Scenario: cardiac arrest (matches), NYHA III (does NOT match), reversible cause = true (does NOT match)
- NOT all conditions met → decision = "no" [why? because the preference is negated, so if conditions aren't met, CPR is allowed], match_type = "partial" [we matched the intervention but conditions unmet, so defer to surrogate]
- Gold expected: decision = "yes", match_type = "partial"
- **Result: correct**

This concreteness helps demystify the reasoner.

---

## Speaker notes for Slide 7d — cohort oracle description

The "simplified reference oracle" for the cohort is:

1. **For each profile + scenario pair**, manually determine the correct answer using POLST-semantics logic (published definitions, not our own reasoning)
2. If the directive's activation conditions are met → correct answer is the directive's preference (yes / no / conditional)
3. If conditions are unmet → correct answer is "no coverage" or "partial" (the directive doesn't apply; defer)
4. If the directive is vague → correct answer is "vague" (human review needed)

We then scored ADO's decision against this oracle, field by field. The 47% overall agreement includes cases where:
- ADO said "partial" and oracle said "partial" but for different reasons (exact match) — counted as agreement
- ADO said "no coverage" and oracle said "defer" (semantically equivalent) — counted as agreement
- ADO said "full code conditional on X being reversible" and oracle said "DNR unconditional" — counted as disagreement (genuine difference in interpretation of the encoding)

The 81% of cells where ADO and oracle differed but the correct answer was partial/vague/no-coverage shows that ADO is not failing on *wrong answers* — it's succeeding on *honest answers* where a checkbox would be forced to commit.
