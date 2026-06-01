# ADO Project Pipeline: Computable Ontology of End-of-Life Care Preferences

## Scope: Five Core Decision Points in Advanced Heart Failure

Rather than attempting to cover all end-of-life care scenarios, the ontology will provide deep coverage of the five most common clinical decision points where advance directives are consulted in advanced heart failure:

| Decision Point | Why It Matters in HF | AD Coverage Gap |
|---|---|---|
| **CPR / Resuscitation** | Most time-critical decision; HF patients frequently arrest | Well-covered by POLST but poorly by free-text ADs that use vague language ("no heroic measures") |
| **Mechanical Ventilation / Intubation** | Second most frequent; often needed during acute decompensation | ADs rarely distinguish temporary ventilation (bridge to recovery) from indefinite ventilation |
| **ICD Deactivation** | HF-specific; ~200,000 HF patients in the US have ICDs | Most generic AD templates don't mention ICDs at all; deactivation is ethically distinct from withdrawal of treatment |
| **Vasopressor / Inotrope Escalation** | Common in cardiogenic shock; escalation decisions happen daily in ICU | Almost never addressed in ADs; usually left to clinical judgment with no patient preference documentation |
| **Dialysis** | Cardiorenal syndrome makes this frequent in advanced HF | ADs that mention dialysis rarely distinguish acute (recoverable) from chronic (maintenance) dialysis |

Nutrition/hydration, antibiotics, hospice transition, and comfort care preferences are acknowledged but deferred to future work.

### Why Heart Failure Specifically

- **Unpredictable trajectory**: Unlike cancer, HF patients oscillate between stable and acute states, making "terminal" hard to define and AD activation triggers ambiguous
- **Device-specific decisions**: LVADs and ICDs create intervention categories that most AD templates were never designed to address
- **Frequent acute presentations**: HF patients cycle through ED/ICU repeatedly, creating many time-pressured AD interpretation events
- **Semantic mismatch**: Standard ADs reference "terminal condition" or "no hope of recovery," but HF patients may live years with NYHA Class IV symptoms — the ontology must bridge this gap

---

## Pipeline Architecture

```
Path A (primary):     Structured Input --> Ontology Population --> Reasoner --> Decision Output
Path B (stretch):     Free-text AD --> NLP Extraction --> Ontology Population --> Reasoner --> Decision Output
```

Path A is the foundation — get it working first. Path B demonstrates that the ontology could be deployed against real documents.

---

## Stage 1: Ontology Design (Weeks 1-2)

### Core Class Hierarchy

Top-level classes: `PreferenceStatement`, `ClinicalCondition`, `Intervention`, `DecisionMaker`, `CareContext`

### HF-Specific Additions

- **Device intervention classes**: `ICDDeactivation`, `LVADWithdrawal`, `InotropeEscalation`, `InotropeWithdrawal` — these are the decisions that actually come up in HF and that generic ADs fail on
- **FunctionalStatus class**: Tied to NYHA classification (I-IV), because HF preferences are almost always conditional on functional status, not just "terminal vs. not terminal"
- **Preference strength**: Model the difference between "I would prefer not to," "I absolutely do not want," and "I would accept if..." — this matters clinically and distinguishes the ontology from a simple yes/no lookup

### Key Object Properties

- `hasProxy` — links to DecisionMaker
- `appliesToCondition` — links PreferenceStatement to ClinicalCondition
- `specifiesIntervention` — links to Intervention (scoped to the five core decision points)
- `hasActivationCondition` — encodes conditional logic (e.g., "only if NYHA Class IV")
- `hasPreferenceStrength` — data property capturing strength/certainty of preference
- `isNegated` — boolean for exclusionary preferences ("I do not want X")

### Negation Strategy

Exclusionary preferences ("I do not want mechanical ventilation") are handled with a `hasPreference` object property paired with a boolean `isNegated` data property, and where necessary, `complementOf` class expressions. Limitations of this approach under OWL's open-world assumption will be documented.

### Vagueness Strategy

A `VaguePreference` class preserves the original patient language as a data property while assigning it to the nearest formal class. The system can acknowledge what it cannot fully represent rather than forcing false precision.

---

## Stage 2: Structured Preference Input (Weeks 2-3)

Build a Python interface where a person can encode their preferences in structured form. This is Path A and the ground truth generator for evaluation.

### Input Format

Each preference is a structured statement mapping to ontology individuals:

- "If my heart stops and I am in NYHA Class IV with no reversible cause -> do not attempt CPR"
- "If I am on a ventilator with no improvement after 7 days -> withdraw ventilation"
- "Deactivate my ICD if I am enrolled in hospice"
- "I would accept temporary intubation if there is a reversible cause, but not indefinite ventilation"
- "Escalate inotropes only if there is a plan for LVAD or transplant evaluation"

### Implementation

- Python script using OwlReady2 that takes structured input and instantiates ontology individuals
- Each preference maps to a `PreferenceStatement` individual with associated `ClinicalCondition`, `Intervention`, `ActivationCondition`, and `PreferenceStrength` individuals
- Input can come from a CLI tool, a structured form (Google Form -> JSON), or direct JSON input

---

## Stage 3: Reasoning Layer (Weeks 3-4)

This is the core deliverable — the part that answers "would patient X want to be intubated?"

### Input

A patient's populated ontology instance + a clinical scenario encoded as OWL individuals representing current state (e.g., cardiac arrest, NYHA IV, on inotropes, estimated prognosis)

### Reasoning Process

The HermiT reasoner matches activation conditions to current state using DL queries and SWRL rules.

### Output Categories

For each query, the system returns:

| Category | Meaning | Example |
|---|---|---|
| **Clear match** | Activation conditions fully met, preference unambiguous | Patient said "no CPR if NYHA IV" and patient is NYHA IV in cardiac arrest |
| **Partial match** | Some activation conditions met, others unspecified | Patient said "no ventilator if terminal" but terminal status is uncertain |
| **No coverage** | Patient didn't address this scenario | Patient's AD says nothing about ICD deactivation |
| **Vague** | Preference uses terms that can't be fully resolved | Patient said "no heroic measures" — system returns the original language with its best class mapping |

The "No coverage" and "Vague" categories are clinically important — a system that says "I don't know, here's the closest preference and the original patient language" is more useful and more honest than one that forces an answer.

---

## Stage 4: NLP Extraction (Weeks 4-5, stretch goal)

Take free-text ADs from the 50-template concept inventory and build an extraction pipeline.

### Approach

- Use an LLM (Claude or GPT-4) with structured output to extract preference statements from raw AD text into the ontology's input schema
- This is a **classification + extraction** task — mapping free text to predefined ontology classes, not open-ended generation
- Prompt engineering with few-shot examples drawn from manually annotated ADs

### Evaluation of Extraction (separate from reasoning evaluation)

- Precision: Of extracted preferences, how many correctly map to the intended ontology class?
- Recall: Of all preference statements in the AD, how many were successfully extracted?
- Error analysis: Categorize failures (missed preference, wrong class, lost conditionality, lost negation)

---

## Stage 5: Evaluation (Weeks 5-7)

**Revised May 2026 (post-TA feedback)**: Track priorities have been rebalanced to put scenario-based reasoning and coverage analysis first, with a smaller fidelity study and a lighter-touch expert review. The reasoning layer is the core technical contribution and receives the most evaluation effort.

### Track 1: Scenario-Based Reasoning Evaluation (Primary)

**Question**: Does the reasoner correctly infer care decisions from encoded preferences across diverse clinical scenarios?

- Expand the existing 12-vignette suite to **20-25 vignettes** (4-5 per decision point)
- Deliberate coverage of clear, conditional, vague, and negated preferences; the three known failure modes (temporal, care-context, encoding fidelity); and cases that require SWRL inference rather than pure DL classification
- **Metrics**:
  - Decision accuracy and match-type accuracy (per vignette and aggregate)
  - Per-intervention precision/recall, so coverage of less common decision points (pacemaker deactivation, NIV) is visible
  - **Ablation**: identical vignette set evaluated with and without the new SWRL rule layer, isolating the reasoner's contribution from the Python query engine

### Track 2: Coverage Analysis (Primary)

**Question**: What can the ontology represent, and what can't it?

- Encode **25-30 verbatim preference statements** drawn from the 50-template concept inventory, focusing on the five core HF decision points
- Each statement classified as:
  - (a) representable without loss
  - (b) representable with documented vagueness (`VaguePreference` with `originalText` preserved)
  - (c) missing ontology class
  - (d) OWL expressivity limitation
  - (e) inherent natural-language vagueness
- Output: concrete enumeration of what the ontology can and cannot represent across real AD templates, plus a prioritized list of additions for future work

### Track 3: Patient Preference Fidelity (Secondary, Reduced Scope)

**Question**: Does the system correctly represent what people actually want?

- Recruit **5-6 classmates** from BMDS 210 / CS 270 (revised from 10-15 per TA guidance)
- Each participant (i) encodes their own HF-specific EOL preferences via the structured input tool, then (ii) answers 5-6 clinical scenarios in their own words
- **Metric**: Agreement rate between system output and participant's stated situational preference
- **Key finding**: Cases where documented preferences diverge from situational preferences — a known limitation of ADs in general, characterized qualitatively

### Track 4: Expert Ontology Review (Light-Touch)

**Question**: Does the ontology pass external clinical face validity?

- Reframed from a vignette survey to a **written ontology review by 1-2 domain experts** (palliative care or bioethics)
- Reviewers receive: the ontology, a one-page summary of the 5 decision points and 21 interventions, and the V5/V6/V10 gap analysis
- Structured feedback requested on class taxonomy, missing concepts, and clinical face validity
- Disagreements documented as future-work items rather than scored quantitatively (Cohen's kappa was deferred since the sample is too small to be meaningful)

---

## What We Are Not Doing (Acknowledged Limitations)

- **FHIR expressivity comparison**: Interesting but doesn't add to the clinical validation story. Noted as future work.
- **Cross-jurisdictional legal variation**: Out of scope. The ontology models clinical preferences, not legal validity.
- **Temporal reasoning**: OWL doesn't natively support it. We acknowledge that preferences change over time and suggest SWRL rules or an external temporal reasoner as future work.
- **Full clinician user study**: Deferred. The expert concordance evaluation (Track 1) provides clinical validation without the overhead of a formal usability study.

---

## Summary of Deliverables

| Deliverable | What It Proves |
|---|---|
| OWL ontology in Protege (scoped to 5 HF decision points) | A formal, computable representation of EOL preferences exists and can handle HF-specific complexity |
| Structured input -> ontology pipeline (Python/OwlReady2) | Patient preferences can be computably encoded |
| Reasoner queries (DL + SWRL) with 4-category output | System can infer care decisions and honestly flag uncertainty |
| NLP extraction pipeline (stretch) | Could work on real free-text AD documents |
| Expanded scenario evaluation (20-25 vignettes) with SWRL ablation | Reasoner correctly infers care decisions across the 5 decision points |
| Coverage analysis on 25-30 real AD statements with failure categorization | Characterizes what the ontology can and cannot represent against real AD templates |
| 5-6 classmate fidelity study | System reflects what people actually want; surfaces documented-vs-situational preference gap |
| Written expert ontology review (1-2 reviewers) | External clinical face validity check on the model |

---

## Revised Timeline

| Week | Milestone |
|---|---|
| 1-2 (by April 27) | Complete concept inventory, finalize ontology design scoped to 5 HF decision points, begin Protege implementation |
| 2-3 (by May 4) | Complete OWL ontology, build structured preference input pipeline, ground concepts in SNOMED CT |
| 3-4 (Progress Report: May 6) | Implement reasoning layer with DL queries and SWRL rules, test on initial vignettes |
| 4-5 (by May 18) | Begin NLP extraction pipeline (stretch), design evaluation vignettes, recruit expert reviewers and participants |
| 5-6 (by May 27) | Run all three evaluation tracks, collect and analyze results |
| 7 (Presentations: June 1, Report: June 5) | Synthesize findings, prepare poster/presentation, write final report |

---

*Compiled for BMDS210/CS270 Final Project, Spring 2026*
