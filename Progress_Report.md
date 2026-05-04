# BMDS 210 / CS 270 — Project Progress Report

**Project:** Toward a Computable Ontology of End-of-Life Care Preferences in Advanced Heart Failure

**Date:** May 4, 2026

---

## 1. Progress Made So Far

### a. Introduction / Background

Advance directives (ADs) are legal documents in which patients specify their end-of-life (EOL) care preferences. Despite their importance, current ADs are almost entirely free-text documents that cannot be queried, reasoned over, or transferred reliably across care settings. Clinicians frequently encounter ADs at moments of acute crisis and must interpret ambiguous natural language under time pressure. An estimated 67% of ICU patients cannot speak for themselves at end of life, yet fewer than 30% have advance directives on file, and those that exist are rarely in a form that is interoperable with EHR systems.

This project builds an OWL ontology of EOL care preferences — an Advance Directive Ontology (ADO) — that enables a reasoner to match a patient's documented preferences to their current clinical situation and infer appropriate care decisions. We scope the ontology to **advanced heart failure (HF)**, specifically the five most common clinical decision points where advance directives are consulted:

1. **CPR / Resuscitation** — most time-critical; HF patients frequently arrest, yet free-text ADs use vague language ("no heroic measures")
2. **Mechanical Ventilation / Intubation** — ADs rarely distinguish temporary ventilation (bridge to recovery) from indefinite ventilation
3. **ICD Deactivation** — ~200,000 HF patients in the US have ICDs, but most generic AD templates don't mention them at all
4. **Vasopressor / Inotrope Escalation** — almost never addressed in ADs; usually left to clinical judgment with no patient preference documentation
5. **Dialysis** — ADs that mention dialysis rarely distinguish acute (recoverable) from chronic (maintenance) dialysis

Heart failure was chosen because of its unpredictable trajectory (oscillating between stable and acute states), device-specific decisions (ICDs, LVADs) that most AD templates were never designed to address, and frequent acute presentations that create many time-pressured AD interpretation events.

### b. Methodology

#### i. Dataset(s)

**Advanced Directive Concept Inventory (50 templates).** We compiled and cataloged 50 advance directive templates across 8 categories:

| Category | Count | Examples |
|---|---|---|
| State-specific ADs (US) | 10 | California AHCD, Texas Directive, NY Health Care Proxy |
| POLST/MOLST forms | 6 | National POLST, CA POLST, NY MOLST, OR POLST |
| Specialized population templates | 4 | Five Wishes, Voicing My Choices (adolescent), Dementia-specific |
| Psychiatric/mental health ADs | 7 | Bazelon Center PAD, SAMHSA guide, state-specific PADs |
| Religious/faith-based templates | 9 | Catholic (NCBC, state), Halachic (Orthodox Jewish), Islamic (IMANA) |
| Organizational/institutional | 4 | VA Form 10-0137, AAFP, Mayo Clinic |
| DNR/DNAR forms | 5 | Texas OOH-DNR, California Prehospital DNR |
| International templates | 5 | UK ADRT (NHS), BC "My Voice," Canadian provincial forms |

**Relevance and suitability.** This corpus captures the real-world diversity of AD formats — the semantic gaps across them are exactly what the ontology is designed to bridge. Preliminary analysis of the inventory revealed 9 common decision points across all templates (CPR, ventilation, nutrition/hydration, dialysis, antibiotics, pain management, organ donation, autopsy, disposition), 4 types of activation triggers (incapacity, terminal condition, permanent unconsciousness, disease stage), and population-specific considerations (dementia staging, psychiatric medication preferences, religious authority structures). Critically, the inventory confirmed our hypothesis: the HF-specific decisions we target (ICD deactivation, inotrope/vasopressor escalation) are almost entirely absent from standard AD templates, validating the need for a specialized ontology.

#### ii. Techniques and Algorithms

**OWL Ontology (Protege).** The ADO contains 67 classes, 12 object properties, and 8 data properties organized under 11 top-level classes:

- `Patient`, `DecisionMaker` — the actors
- `PreferenceStatement` (with subclasses `ClearPreference`, `ConditionalPreference`, `VaguePreference`) — the core representational unit
- `Intervention` (with subclass trees for `ResuscitationIntervention`, `VentilationIntervention`, `DeviceIntervention`, `PharmacologicIntervention`, `DialysisIntervention`) — the 21 specific interventions across the 5 decision points
- `ClinicalCondition` — 10 conditions including HF-specific states (cardiogenic shock, acute decompensation, cardiorenal syndrome)
- `FunctionalStatus` — NYHA Classes I–IV, because HF preferences are almost always conditional on functional status
- `ActivationCondition` — encodes conditional logic (NYHA class, clinical conditions, reversible cause, time bounds)
- `CareContext` — 5 settings (ICU, ED, hospice, outpatient, prehospital)
- `DecisionOutcome` — 4-category output (ClearMatch, PartialMatch, NoCoverage, VagueMatch)
- `AdvanceDirectiveDocument` — source document types (LivingWill, HCPOA, POLST, DNR)
- `ClinicalScenario` — encodes a patient's current state for reasoning queries

Key object properties link the ontology together: `hasProxy`, `hasPreference`, `specifiesIntervention`, `appliesToCondition`, `hasActivationCondition`, `requiresFunctionalStatus`, `requiresCondition`, `hasDecisionOutcome`, and `sourceDocument`. Data properties capture `isNegated` (boolean), `hasPreferenceStrength` (Absolute/Strong/Conditional/Weak), `originalText` (preserving patient language), `hasReversibleCause`, `hasTimeBound`, and `dateDocumented`.

**Structured Preference Input Pipeline (Python / owlready2).** We built a complete Python pipeline (`preference_input.py`) that takes patient preferences as structured JSON and programmatically instantiates OWL individuals using owlready2. The pipeline supports three input modes:

- **Interactive CLI**: A guided questionnaire walking through each of the 5 decision points
- **JSON file input**: For batch processing or integration with external tools (e.g., Google Forms)
- **Example generation**: Produces a reference patient with 8 representative preferences for testing

Each preference maps to a `PreferenceStatement` individual linked to its `Intervention`, `ActivationCondition` (with optional NYHA class, clinical conditions, reversible cause flag, time bounds, and care context), `PreferenceStrength`, negation status, original text, and source document. The pipeline validates inputs against controlled vocabularies for all 21 interventions, 10 conditions, 4 NYHA classes, 5 care contexts, and 4 document types.

**HermiT Reasoner (in progress).** The next stage will implement DL queries and SWRL rules to match activation conditions against clinical scenarios. Given a populated patient ontology and a `ClinicalScenario` individual representing the current state (e.g., cardiac arrest + NYHA IV + no reversible cause), the reasoner will classify each preference into one of 4 outcome categories: Clear Match, Partial Match, No Coverage, or Vague.

**Why these techniques are appropriate.** OWL provides the formal expressivity needed for conditional, negatable preferences with graded strength — something that neither free-text ADs nor structured FHIR resources currently support. The class hierarchy with `ActivationCondition` restrictions enables inference rather than simple lookup: the reasoner can determine which preferences apply to a novel clinical scenario that the patient may not have explicitly anticipated. The 4-category output is designed to be clinically honest — a system that says "I don't know, here's the closest preference and the original patient language" is more useful than one that forces an answer.

#### iii. Other Relevant Aspects

**Negation handling.** Exclusionary preferences ("I do not want mechanical ventilation") are represented with a `hasPreference` object property paired with a boolean `isNegated` data property, and where necessary, `complementOf` class expressions. This is a deliberate design choice given OWL's open-world assumption; we document where it breaks down.

**Vagueness as a first-class problem.** The `VaguePreference` subclass preserves the original patient language as a data property (`originalText`) while assigning it to the nearest formal class. This allows the system to acknowledge what it cannot fully represent rather than forcing false precision — itself a contribution to the AD formalization literature.

**SNOMED CT grounding.** Clinical concepts (conditions, interventions, functional status) are grounded in SNOMED CT codes to support interoperability with existing clinical systems.

### c. Results / Analysis

**Pipeline validation.** We ran the example patient (Jane Doe) through the full pipeline. All 8 preference statements — spanning all 5 decision points, including both clear and conditional preferences, negated and affirming, with varying strength levels — were successfully instantiated as OWL individuals. The populated ontology contains 47 individuals (1 patient, 2 decision makers, 1 source document, 8 preference statements, 8 interventions, 6 activation conditions, 4 clinical condition instances, 2 NYHA status instances, and pre-existing example individuals). No warnings or class-not-found errors were produced.

**Preliminary coverage analysis.** We assessed how the 9 common decision points identified across our 50-template concept inventory map to the current ontology:

| Decision Point | Ontology Coverage | Notes |
|---|---|---|
| CPR / Resuscitation | Full (3 intervention subclasses) | CPR, defibrillation, transcutaneous pacing |
| Mechanical Ventilation | Full (6 intervention subclasses) | Distinguishes temporary vs. indefinite, invasive vs. non-invasive, withdrawal |
| ICD / Device Management | Full (5 intervention subclasses) | ICD deactivation, shock therapy, LVAD withdrawal/continuation, pacemaker deactivation |
| Vasopressor / Inotrope Support | Full (4 intervention subclasses) | Escalation and withdrawal for both vasopressors and inotropes |
| Dialysis | Full (3 intervention subclasses) | Acute, chronic, withdrawal — distinguishing the key clinical categories |
| Nutrition / Hydration | Not covered | Deferred to future work |
| Antibiotics | Not covered | Deferred to future work |
| Pain Management / Comfort Care | Not covered | Deferred to future work |
| Organ / Tissue Donation | Not covered | Deferred to future work |

For the 5 in-scope decision points, the ontology provides **21 specific intervention classes** — significantly more granular than any single AD template in the concept inventory. For example, standard ADs typically offer a binary yes/no on "mechanical ventilation," while the ontology distinguishes 6 ventilation-related interventions that capture the clinically meaningful distinctions (temporary vs. indefinite, invasive vs. non-invasive, withdrawal).

**Conditional preference representation.** Of the 8 example preferences, 5 are conditional — each with different activation condition structures:

| Preference | Activation Conditions |
|---|---|
| No CPR if NYHA IV without reversible cause | NYHA class + clinical condition + reversible cause flag |
| Accept temporary ventilation if reversible | Reversible cause flag only |
| Deactivate ICD if enrolled in hospice | Care context only |
| Accept acute dialysis if cardiorenal + recoverable | Clinical condition + reversible cause flag |
| Escalate inotropes only if LVAD/transplant plan | Clinical condition only |
| Withdraw vasopressors if no improvement after 72h | Clinical condition + time bound |

This demonstrates that the ontology's `ActivationCondition` class can represent the diverse conditional structures found in real clinical preferences — a capability absent from standard AD templates and POLST forms.

---

## 2. Updates / Changes to Original Proposal

Two significant changes have been made since the original proposal:

1. **Narrowed disease scope with deeper clinical modeling.** The proposal mentioned scoping to heart failure but the current implementation goes substantially deeper, defining 5 specific clinical decision points (CPR, mechanical ventilation, ICD deactivation, vasopressor/inotrope escalation, dialysis) with 21 distinct intervention subclasses. This provides clinical depth over breadth and ensures the ontology addresses the specific decisions that actually arise in advanced HF care.

2. **Full programmatic ontology population via owlready2.** The proposal mentioned using owlready2 for SNOMED CT grounding. The project now includes a complete Python pipeline (`preference_input.py`, ~600 lines) that programmatically instantiates OWL individuals from structured JSON input — including activation conditions, negation, preference strength, and source document linking. This goes beyond what was proposed and establishes a working end-to-end path from patient input to populated ontology.

Additional changes:
- **Expanded concept inventory**: From 30–40 templates to 50 templates across 8 categories (adding psychiatric, religious/faith-based, and international templates)
- **Added third evaluation track**: Patient preference fidelity evaluation (Track 2) was added to complement the originally proposed coverage analysis and scenario-based reasoning tests
- **Deferred FHIR expressivity comparison**: Moved from stretch goal to acknowledged future work, focusing evaluation effort on clinical validation instead
- **Timeline adjustment**: The reasoning layer implementation shifted from weeks 2–3 to weeks 3–4; the structured input pipeline was prioritized first to establish ground truth for evaluation

---

## 3. Updated Plan / Timeline

| Week | Milestone | Status |
|---|---|---|
| 1–2 (by Apr 27) | Complete concept inventory (50 templates), finalize ontology design scoped to 5 HF decision points, begin Protege implementation | **Complete** |
| 2–3 (by May 4) | Complete OWL ontology (67 classes, 20 properties), build structured preference input pipeline, ground concepts in SNOMED CT | **Complete** |
| 3–4 (by May 11) | Implement reasoning layer with DL queries and SWRL rules, test on initial clinical vignettes, validate 4-category output | **In progress** |
| 4–5 (by May 18) | Begin NLP extraction pipeline (stretch goal), design 15–20 evaluation vignettes, recruit expert reviewers (2–3 bioethicists/palliative care attendings) and 10–15 study participants | Upcoming |
| 5–6 (by May 27) | Run all three evaluation tracks: expert concordance (Cohen's kappa), patient preference fidelity (agreement rate), coverage analysis (25–30 preference statements) | Upcoming |
| 7 (Presentations: Jun 1, Report: Jun 5) | Synthesize findings, prepare poster/presentation, write final report | Upcoming |

---

## 4. Roadblocks or Challenges

**Negation under OWL's open-world assumption.** OWL assumes that anything not stated is unknown (not false), which complicates the representation of exclusionary preferences. Our workaround — `isNegated` boolean + `complementOf` class expressions — is functional but has known edge cases where the reasoner cannot distinguish "patient said no" from "patient didn't say." We are documenting these limitations as part of the coverage analysis.

**Temporal reasoning limitations.** OWL does not natively support temporal reasoning, yet patient preferences frequently reference time ("if no improvement after 7 days"). We currently model time bounds as string data properties (`hasTimeBound`), which the reasoner cannot evaluate. A more robust solution would require SWRL rules or an external temporal reasoner — acknowledged as future work.

**Evaluation recruitment.** Recruiting 2–3 Stanford bioethicists or palliative care attendings for the expert concordance evaluation (Track 1) may be challenging on the project timeline. We have a backup plan to use published clinical vignettes with established ground-truth answers from the palliative care literature. Similarly, the patient preference fidelity evaluation (Track 2) requires 10–15 participants — we plan to recruit from classmates and the broader Stanford community, pending IRB guidance from the teaching team.

**Reasoning layer complexity.** Writing SWRL rules that correctly handle the interaction between conditional preferences, negation, preference strength, and vague language is the most technically challenging remaining task. We anticipate needing to iterate on rule design based on initial vignette testing.

---

## 5. Questions for the Teaching Team

1. **IRB requirements**: For the patient preference fidelity evaluation (Track 2), we plan to recruit 10–15 participants to encode hypothetical EOL preferences and evaluate the system's output. Does this require IRB approval, or does it fall under course-related educational activity?

2. **Evaluation scope**: Given the timeline, is it acceptable to prioritize the coverage analysis (Track 3) and scenario-based reasoning test (part of Track 1) over the full expert concordance study with recruited clinicians? We want to ensure the evaluation is rigorous but feasible.

3. **NLP stretch goal**: Should we allocate remaining time to the NLP extraction pipeline (demonstrating the system could work on real free-text ADs), or would the time be better spent deepening the reasoning layer and evaluation?
