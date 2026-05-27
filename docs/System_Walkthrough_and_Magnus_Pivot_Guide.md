# ADO System Walkthrough & Magnus Pivot Guide

**Prepared for:** Patrick Walsh & Darren Chan
**Context:** Pre-meeting preparation for Dr. David Magnus review, June 2026
**Purpose:** Deep technical walkthrough of the current system, plus concrete questions and information needs for executing the three pivots Magnus's feedback suggests.

---

## Part I: How the System Was Built — A Complete Technical Walkthrough

### 1. The Ontology Layer (`advanced_directives.owl`)

The OWL ontology is the formal backbone of the entire system. It defines the vocabulary and logical structure that everything else is built on.

#### Class hierarchy (67 classes, 11 top-level)

```
owl:Thing
├── Patient                           # The person whose preferences we encode
├── DecisionMaker                     # Healthcare proxy / surrogate
├── PreferenceStatement               # Core unit: a single encoded preference
│   ├── ClearPreference               #   Unambiguous, fully encodable
│   ├── ConditionalPreference         #   Applies only when activation conditions met
│   └── VaguePreference               #   Irreducibly imprecise language preserved
├── Intervention                      # What the preference is about
│   ├── ResuscitationIntervention
│   │   ├── CPR
│   │   ├── Defibrillation
│   │   └── TranscutaneousPacing
│   ├── VentilationIntervention
│   │   ├── Intubation
│   │   ├── MechanicalVentilation
│   │   │   ├── TemporaryVentilation
│   │   │   └── IndefiniteVentilation
│   │   ├── VentilationWithdrawal
│   │   └── NonInvasiveVentilation    # BiPAP/CPAP
│   ├── DeviceIntervention
│   │   ├── ICDDeactivation
│   │   ├── ICDShockTherapy
│   │   ├── LVADWithdrawal
│   │   ├── LVADContinuation
│   │   └── PacemakerDeactivation
│   ├── PharmacologicIntervention
│   │   ├── InotropeEscalation
│   │   ├── InotropeWithdrawal
│   │   ├── VasopressorEscalation
│   │   └── VasopressorWithdrawal
│   └── DialysisIntervention
│       ├── AcuteDialysis
│       ├── ChronicDialysis
│       └── DialysisWithdrawal
├── ClinicalCondition                 # The patient's medical state
│   ├── HeartFailure
│   │   └── AdvancedHeartFailure
│   ├── CardiacArrest
│   ├── CardiogenicShock
│   ├── AcuteDecompensation
│   ├── CardiorenalSyndrome
│   ├── RespiratoryFailure
│   ├── TerminalCondition
│   ├── PermanentUnconsciousness
│   └── Incapacity
├── FunctionalStatus                  # NYHA classification
│   ├── NYHA_ClassI
│   ├── NYHA_ClassII
│   ├── NYHA_ClassIII
│   └── NYHA_ClassIV                  # Mutually disjoint
├── ActivationCondition               # When a preference fires
├── CareContext                       # Where the decision happens
│   ├── ICUSetting
│   ├── EmergencyDepartment
│   ├── HospiceEnrollment
│   ├── OutpatientSetting
│   └── PrehospitalSetting
├── ClinicalScenario                  # Input to the reasoner
├── DecisionOutcome                   # The 4-category output
│   ├── ClearMatch
│   ├── PartialMatch
│   ├── NoCoverage
│   └── VagueMatch                    # Mutually disjoint
└── AdvanceDirectiveDocument          # Source document types
    ├── LivingWill
    ├── HealthCarePowerOfAttorney
    ├── POLSTForm
    └── DNROrder
```

#### Properties (20 total: 12 object, 8 data)

**Object properties** — the "wiring" that links classes together:

| Property | Domain → Range | What it does |
|---|---|---|
| `hasProxy` | Patient → DecisionMaker | Names the healthcare proxy |
| `hasPreference` | Patient → PreferenceStatement | Links patient to each preference |
| `specifiesIntervention` | PreferenceStatement → Intervention | What intervention this preference addresses |
| `appliesToCondition` | PreferenceStatement → ClinicalCondition | What condition triggers this preference |
| `hasActivationCondition` | PreferenceStatement → ActivationCondition | The conditional logic gate |
| `requiresFunctionalStatus` | ActivationCondition → FunctionalStatus | NYHA class required |
| `requiresCondition` | ActivationCondition → ClinicalCondition | Clinical conditions required |
| `requiresCareContext` | ActivationCondition → CareContext | Care setting required (May 22 fix) |
| `hasCurrentCondition` | ClinicalScenario → ClinicalCondition | Scenario's active conditions |
| `hasCurrentFunctionalStatus` | ClinicalScenario → FunctionalStatus | Scenario's NYHA class |
| `hasDecisionOutcome` | PreferenceStatement → DecisionOutcome | Reasoner output |
| `sourceDocument` | PreferenceStatement → AdvanceDirectiveDocument | Provenance |

**Data properties** — scalar values on individuals:

| Property | Domain | Type | What it does |
|---|---|---|---|
| `isNegated` | PreferenceStatement | boolean | "I do NOT want X" |
| `hasPreferenceStrength` | PreferenceStatement | string | Absolute / Strong / Conditional / Weak |
| `originalText` | PreferenceStatement | string | Verbatim patient language |
| `dateDocumented` | PreferenceStatement | date | When the preference was recorded |
| `hasReversibleCause` | ActivationCondition | boolean | Reversible cause flag |
| `hasTimeBound` | ActivationCondition | string | Human-readable time constraint |
| `hasTimeBoundHours` | ActivationCondition | int | Machine-comparable hours (May 22 fix) |
| `proxyName` / `proxyRelationship` | DecisionMaker | string | Proxy metadata |

#### Key design decisions baked into the OWL

1. **NYHA classes are `AllDisjointClasses`** — a patient can only be in one NYHA class at a time, which prevents the reasoner from ever matching both "requires NYHA III" and "requires NYHA IV" simultaneously.

2. **DecisionOutcome categories are `AllDisjointClasses`** — an output is exactly one of Clear / Partial / NoCoverage / Vague. No overlap.

3. **VaguePreference as a first-class subclass** — this is the most philosophically important design choice. Instead of forcing vague language into Clear/Conditional, we give it its own type and preserve `originalText`. The system can say "I found something relevant but I can't resolve it — here are the patient's words."

4. **Intervention granularity** — we distinguish 21 specific interventions where standard ADs offer maybe 5-6. This prevents the over-inference problem: the system won't confuse ICD deactivation (a planned, durable change) with ICD shock therapy (a single event during arrhythmia). V16 tests this explicitly.

5. **ActivationCondition as a composite gate** — a single ActivationCondition can have NYHA class + clinical conditions + reversible cause + time bound + care context. ALL must match for the preference to fire as "clear." Partial matches on any subset produce "partial."

---

### 2. The Preference Input Pipeline (`preference_input.py`)

This is the "Path A" pipeline — structured input to populated ontology.

#### What it does

Takes a JSON object describing a patient's preferences and programmatically creates OWL individuals using owlready2:

```
JSON input → load base ontology → create Patient individual
                                → create Proxy individual
                                → create source document individual
                                → for each preference:
                                    create PreferenceStatement (typed as Clear/Conditional/Vague)
                                    create Intervention individual
                                    create ActivationCondition individual (if present)
                                        wire up NYHA, conditions, reversible cause,
                                        time bounds, care context
                                    link everything via object properties
                                → save populated .owl file
```

#### Controlled vocabularies (the dictionaries)

The file defines five dictionaries that map human-readable keys to OWL class names:

- **`INTERVENTIONS`** — 21 keys (`cpr`, `defibrillation`, ..., `dialysis_withdrawal`) → OWL class names (`CPR`, `Defibrillation`, ..., `DialysisWithdrawal`)
- **`CONDITIONS`** — 10 clinical conditions
- **`NYHA_CLASSES`** — I through IV
- **`CARE_CONTEXTS`** — 5 settings (icu, ed, hospice, outpatient, prehospital)
- **`DOC_TYPES`** — 4 document types

These dictionaries serve as the "contract" between the JSON schema and the OWL ontology. The LLM extraction pipeline (`llm_extraction.py`) imports these same dictionaries to constrain its output, so all three input paths (interactive, JSON, LLM) produce identical ontology structures.

#### Three input modes

1. **`--example`** — generates a hardcoded Jane Doe patient with 9 preferences spanning all 5 decision points. This is the reference patient used by `query_evaluation.py` and `demo.py`.
2. **`--json path/to/file.json`** — loads from a JSON file matching the schema.
3. **`--interactive`** — CLI questionnaire that walks through each of the 5 decision points. (Not useful in automated contexts — requires TTY input.)

#### The JSON schema

Each preference in the JSON has:
```json
{
  "label": "human-readable summary",
  "intervention": "key from INTERVENTIONS dict",
  "negated": true/false,
  "strength": "Absolute|Strong|Conditional|Weak",
  "original_text": "patient's verbatim words",
  "type": "clear|conditional|vague",
  "activation_conditions": {
    "nyha_class": "I|II|III|IV",
    "conditions": ["cardiac_arrest", "cardiogenic_shock"],
    "reversible_cause": true/false,
    "time_bound": "human-readable string",
    "time_bound_hours": 72,
    "care_context": "hospice|icu|ed|outpatient|prehospital"
  }
}
```

#### What to notice about the architecture

The `populate_patient()` function is the single bottleneck that all input paths flow through. This means:
- Every input path (interactive CLI, JSON file, LLM extraction) produces the same ontology structure
- Adding a new decision point means adding entries to the `INTERVENTIONS` dict and corresponding OWL classes — everything downstream "just works"
- Adding a new activation condition type means adding a new field to the `activation_conditions` schema, a new property to `ActivationCondition` in the OWL, and new matching logic in `query_evaluation.py`

---

### 3. The Reasoning / Query Engine (`query_evaluation.py`)

This is the closest thing to an automated test suite AND the core reasoning engine.

#### How the reasoner works

The `find_matching_preferences()` function implements the core inference logic:

```
For a given (patient, intervention, scenario_state):

1. Iterate over all patient.hasPreference
2. For each preference:
   a. Check if specifiesIntervention matches the queried intervention
      (by OWL class name or subclass relationship)
   b. If no match → skip
   c. If match → check activation conditions:
      - No activation conditions → unconditional → "clear" (or "vague" if VaguePreference)
      - Has activation conditions → check each:
        • NYHA class: required vs. scenario
        • Clinical conditions: each required condition vs. scenario
        • Reversible cause: required boolean vs. scenario boolean
        • Care context: required setting vs. scenario setting
        • Time bound: required hours vs. scenario elapsed hours
      - ALL met → "clear"
      - SOME met, SOME unmet → "partial"
      - ALL unmet → "partial"
   d. Special rule for VaguePreference:
      - If activation conditions are UNMET → vague preference does NOT fire
      - If activation conditions are met (or absent) → fires as "vague"

3. If no preferences matched at all → "no_coverage"
4. If multiple preferences matched → priority: clear > vague > partial
5. For clear matches: check isNegated to determine yes/no decision
```

#### The vague-preference precedence rule

This rule (the `is_vague` gate at line ~430 in `query_evaluation.py`) was discovered through the LLM pipeline. When Claude extracted preferences from the example AD paragraph, it correctly identified "no heroic measures if I am dying" and bound it to a `TerminalCondition` activation condition. Without the gate, this vague preference was overriding the specific clear preference for CPR, producing a `vague` result instead of `clear/no`.

The rule: **a vague preference whose own activation conditions are explicitly unmet does not fire.** This is the closed-world honesty principle applied to vague preferences — if the patient said "if I am dying" and the scenario doesn't include TerminalCondition, the vague preference is not applicable.

This is a concrete example of the ontology + reasoner architecture surfacing a design question that a pure-LLM system would silently paper over.

#### The 16 clinical vignettes

| ID | Tests | Expected | Category |
|---|---|---|---|
| V1 | CPR, NYHA IV, no reversible cause → all conditions met | no / clear | Clear |
| V2 | CPR, NYHA III, reversible cause → conditions not met | partial | Partial |
| V3 | Temporary ventilation, reversible cause → condition met | yes / clear | Clear |
| V4 | Indefinite ventilation, no conditions → unconditional refusal | no / clear | Clear |
| V5 | ICD deactivation, hospice → care context matches | yes / clear | Clear |
| V6 | ICD deactivation, ICU (not hospice) → care context mismatch | partial | Partial |
| V7 | Acute dialysis, cardiorenal + reversible → both met | yes / clear | Clear |
| V8 | Chronic dialysis, unconditional refusal | no / clear | Clear |
| V9 | Inotrope escalation, cardiogenic shock → condition met | yes / clear | Clear |
| V10 | Vasopressor withdrawal, 96h ≥ 72h → time bound met | yes / clear | Clear |
| V11 | NIV, vague language → surfaces original words | vague | Vague |
| V12 | Pacemaker deactivation, not in AD | no_coverage | No coverage |
| V13 | Vasopressor withdrawal, 48h < 72h → time not yet met | partial | Partial |
| V14 | Acute dialysis, sepsis-AKI (not cardiorenal) → condition mismatch | partial | Partial |
| V15 | Chronic dialysis, outpatient → unconditional refusal fires anywhere | no / clear | Clear |
| V16 | ICD shock therapy, not same as ICD deactivation → granularity test | no_coverage | No coverage |

All 16 pass at 100% accuracy for both decision and match type.

**Vignettes that test specific fixes:**
- V5/V6: Test the May 22 `requiresCareContext` fix (was a false-positive before)
- V10/V13: Test the May 22 `hasTimeBoundHours` temporal fix (was string-only before)
- V14: Tests condition specificity (cardiorenal ≠ sepsis-AKI)
- V16: Tests intervention granularity (ICD deactivation ≠ ICD shock therapy)

---

### 4. The LLM Extraction Pipeline (`llm_extraction.py`)

This is "Path B" — free-text AD to structured JSON via Claude.

#### Architecture

```
free-text AD paragraph
        │
        ▼
Claude (claude-opus-4-7) with:
  • System prompt defining closed-world extraction rules
  • Pydantic schema (ExtractedPreferences) for structured output
  • The exact same INTERVENTIONS/CONDITIONS/etc. vocabulary as preference_input.py
        │
        ▼
ExtractedPreferences (validated Pydantic model)
        │
        ▼
to_patient_json() → dict matching preference_input.py schema
        │
        ▼
populate_patient() → fresh OWL ontology → reasoner
```

#### The system prompt's critical rules

1. **Closed-world extraction** — encode ONLY what the patient explicitly stated. Never extrapolate. The reasoner's "no coverage" behavior depends entirely on this.
2. **Verbatim `original_text`** — the patient's exact words, not paraphrased.
3. **Vague flagging** — imprecise language gets `type: "vague"` and `strength: "Weak"`.
4. **Strength inference** — maps language patterns to the four strength levels.

#### The Pydantic schema

The `ExtractedPreferences` model mirrors the JSON schema from `preference_input.py` exactly:
- `Preference` has `intervention` (Literal type constrained to the 21 keys), `negated`, `strength`, `original_text`, `type`, and optional `ActivationConditions`
- `ActivationConditions` has optional `nyha_class`, `conditions`, `reversible_cause`, `time_bound`, `time_bound_hours`, `care_context`

Using structured output via `client.messages.parse()` means Claude's output is guaranteed to conform to the Pydantic schema — no post-hoc parsing or validation needed.

#### The discovery story (important for Magnus)

When first run, the pipeline surfaced two design gaps:
1. Claude extracted a vague CPR preference from "no heroic measures if I am dying" with an explicit `TerminalCondition` activation. Without a precedence rule, this vague match overrode the specific clear CPR preference.
2. Claude extracted `AdvancedHeartFailure` as a separate activation condition for the CPR preference. The test scenario didn't include this condition, producing `partial` instead of `clear`.

Both were real design questions the structured layer forced the team to name and codify. A pure-LLM system would have produced confident prose in all three runs with no indication of the underlying ambiguity.

---

### 5. The Demo Script (`demo.py`)

Designed for the Magnus meeting. Runs 6 scenarios with narrated explanations:

| # | Category | What it demonstrates |
|---|---|---|
| 1 | CLEAR | CPR preference fires unambiguously |
| 2 | PARTIAL | ICD deactivation conditional on hospice; patient in ICU |
| 3 | NO_COVERAGE | Pacemaker deactivation not in AD |
| 4 | VAGUE | "No aggressive measures" → surfaces patient's words |
| 5 | CLEAR (temporal) | Vasopressor withdrawal time bound (96h ≥ 72h) |
| 6 | PIPELINE | Full free-text → LLM → ontology → reasoner |

Scenario 6 calls the live Anthropic API if `ANTHROPIC_API_KEY` is set; otherwise falls back to the hand-coded ontology with a yellow warning.

---

### 6. Build Timeline & Key Milestones

| When | What was built | Key decision |
|---|---|---|
| Weeks 1-2 (by Apr 27) | 50-template concept inventory; ontology class hierarchy in Protege | Scoped to 5 HF decision points; 21 interventions |
| Weeks 2-3 (by May 4) | Full OWL ontology (67 classes, 20 properties); `preference_input.py` pipeline | VaguePreference as first-class type; NYHA conditioning |
| May 6 | Progress report; 12 vignettes at 92% decision / 100% match-type accuracy | Identified 3 gaps: temporal reasoning, care context, encoding fidelity |
| May 22 | Fixed V5/V6 (added `requiresCareContext`); fixed V10 (added `hasTimeBoundHours`) | Expanded to 16 vignettes, 100% accuracy |
| May 22-25 | Built `llm_extraction.py` + `demo.py`; discovered vague-precedence rule | Full pipeline working end-to-end |
| May 27 | This document; preparing for Magnus meeting | |

---

## Part II: Magnus's Three Critiques and What We Need From Him

### Critique 1: Missing Artificial Nutrition / Hydration (ANH)

#### What he said
> "The decision points miss decision about artificial hydration/nutrition. See POLST."

#### Why he's right
ANH is arguably the most contested EOL decision in bioethics (Terri Schiavo, Catholic doctrine on "ordinary vs. extraordinary means," the POLST form's dedicated ANH section). The progress report explicitly listed "Nutrition / Hydration: Not covered — Deferred to future work." Magnus is correctly flagging this as a gap that matters, not a deferral.

#### What implementing ANH looks like

**New OWL classes:**
```
Intervention
└── NutritionHydrationIntervention          # New parent
    ├── TubeFeeding                          # PEG tube, NG tube
    ├── ArtificialHydration                  # IV fluids, sub-Q hydration
    ├── TotalParenteralNutrition             # TPN (optional — more granular)
    ├── TubeFeedingWithdrawal                # Withdrawal of tube feeding
    └── ArtificialHydrationWithdrawal        # Withdrawal of IV/sub-Q fluids
```

**New entries in `INTERVENTIONS` dict in `preference_input.py`:**
```python
"tube_feeding": "TubeFeeding",
"artificial_hydration": "ArtificialHydration",
"total_parenteral_nutrition": "TotalParenteralNutrition",
"tube_feeding_withdrawal": "TubeFeedingWithdrawal",
"artificial_hydration_withdrawal": "ArtificialHydrationWithdrawal",
```

**New vignettes for `query_evaluation.py`:**
- V17: Patient with advanced HF, unable to swallow. Should tube feeding be initiated? (Test clear match against ANH preference)
- V18: Patient enrolled in hospice. Should IV hydration continue? (Test care-context gating)
- V19: Catholic patient whose AD says "I want ordinary care including food and water" — how does the ontology handle the ordinary/extraordinary distinction? (Test vague match or new activation condition)

#### Questions for Magnus on ANH

1. **Granularity:** Is the 5-class hierarchy above the right level of granularity? Specifically:
   - Do you distinguish tube feeding (PEG/NG) from IV hydration in your code-status ordering system?
   - Is TPN (total parenteral nutrition) clinically distinct enough to warrant its own class, or is it just a variant of artificial hydration?
   - Should we distinguish "comfort sips" (oral care, ice chips) from artificial hydration? POLST forms typically draw this line.

2. **The Catholic bioethics challenge:** Catholic AHCDs and NCBC forms use "ordinary means" language that classifies nutrition/hydration differently from other interventions. How does Stanford's code-status system handle patients whose religious directive frames ANH as obligatory? Is there a clinical workflow for reconciling that with a physician's assessment that tube feeding is no longer beneficial?

3. **Activation conditions for ANH:** What conditions typically gate ANH decisions?
   - Irreversible swallowing dysfunction?
   - Terminal prognosis timeline (< 6 months, < 2 weeks)?
   - Level of consciousness?
   - Are there any HF-specific ANH considerations (e.g., fluid restriction conflicts with IV hydration)?

4. **POLST ANH section as reference:** The National POLST form has a dedicated Section D for "Artificially Administered Nutrition." Can Magnus walk through how Stanford's version of this section maps to their ordering system? This would directly inform our ontology class design.

---

### Critique 2: AHCD vs. Code-Status Orders / POLST at the Bedside

#### What he said
> "In emergency situations it is code status orders and POLST that matters, not AHCD."

#### Why this is the deepest critique

Magnus is making a workflow observation:

```
Patient writes AHCD ──┐
                      ├──> Clinician writes POLST / code status order ──> Used at bedside
Goals-of-care talk ───┘
```

The AHCD itself is rarely consulted at 2 AM. What fires at the bedside is the code-status order in the EHR and/or the POLST. The AHCD informs the translation, not the execution.

#### What this means for the project

This doesn't kill the project — it **clarifies what it should be doing.** The reframe:

> "An OWL-based reasoning system that translates a patient's AHCD into defensible POLST / code-status orders, with an explicit audit trail from the patient's documented preference through the resulting order."

This keeps everything we've built (the 4-category output, the LLM extraction, the closed-world reasoning) but gives us a customer who actually exists: the palliative care attending writing the POLST, the hospitalist updating code status.

#### What we need from Magnus to implement this pivot

**About Stanford's code-status ordering system:**

1. **What are the code-status categories at Stanford?** Beyond Full Code / DNR, what options does the order set offer? Specifically:
   - Is there a "Limited Code" or "Modified Code" option?
   - Are device-specific orders (ICD on/off, LVAD management) part of the code-status order set or separate?
   - Is there an "Allow Natural Death" option distinct from DNR?
   - Where does intubation / mechanical ventilation fit? Is "DNR/DNI" a single order or two separate orders?
   - Are there vasopressor/inotrope escalation limits in the order set?

2. **What does the code-status order look like in Epic?** Even a verbal description would help:
   - Is it a single order with radio buttons / checkboxes?
   - Or is it a set of individual orders (one for CPR, one for intubation, one for devices, etc.)?
   - How granular is it compared to our 21-intervention ontology?

3. **How does POLST map to code-status orders at Stanford?** When a patient arrives with a POLST, how is it translated into Epic orders? Is it manual re-entry, or is there a structured workflow?

4. **The translation gap:** In Magnus's experience, what are the most common errors or ambiguities when an AHCD is being translated into a code-status order? This is where our reasoner could add the most value.

**Architecture questions for the reframe:**

5. **Output format:** If the reasoner's output were a *draft* code-status order rather than our current 4-category output, what would it need to contain?
   - A yes/no for each intervention?
   - A confidence level?
   - The source preference and original text (audit trail)?
   - A "clinician must review" flag for partial/vague cases?

6. **Does the 4-category output map to code-status workflows?** Specifically:
   - `clear` → auto-populate the order?
   - `partial` → populate with a flag saying "preference exists but conditions don't fully match — clinician review required"?
   - `no_coverage` → leave blank with a note saying "AD does not address this"?
   - `vague` → surface patient's original language for clinician interpretation?

7. **POLST as input OR output?** Two possible framings:
   - **POLST as output:** AHCD → reasoner → draft POLST (the translation tool)
   - **POLST as input:** existing POLST → ontology → scenario evaluation (the interpretation tool)
   - Which is more useful? Both? Magnus's "in emergency situations it is code status orders and POLST that matters" suggests the second — but the AHCD → POLST translation story is where we add the most value, since POLST is already structured.

#### Concrete implementation path (if Magnus confirms the reframe)

1. Add a new top-level class `CodeStatusOrder` to the ontology, with subclasses mapping to the Stanford order set categories.
2. Add an object property `generatesOrder` linking `DecisionOutcome` → `CodeStatusOrder`.
3. Modify `query_evaluation.py` output to produce a draft code-status order for each intervention, with the audit trail (which preference matched, which conditions were evaluated).
4. The 4-category output becomes the *confidence layer* on top of the order: Clear → order auto-generated; Partial/Vague/NoCoverage → order flagged for clinician review.

---

### Critique 3: AHCDs Are Mostly Checkboxes, Not Free Text

#### What he said
> "Many (most?) AHCD directives — especially the good ones, eg the UC designed one — have more or less designed them as check boxes."

#### Why he's partially right

Magnus is correct that state-issued AHCDs (California AHCD, the UC-designed forms) have structured checkbox sections. Our 50-template concept inventory confirms this: POLST forms, state ADs, and many institutional templates are checkbox-based.

Where he's not fully right: the diversity is real. Our inventory includes:
- **Narrative-heavy:** Five Wishes, the Stanford Letter Project, UK ADRT
- **Free-text with checkboxes:** California AHCD (checkboxes + free-text addendum), VA Form 10-0137
- **Fully structured:** POLST, state DNR forms
- **Religious with interpretive language:** Catholic NCBC forms ("ordinary means"), Halachic living wills (defers to rabbinic authority)
- **Psychiatric ADs:** Medication preferences, ECT/restraint decisions — often with detailed free-text sections

#### What this means for the LLM-extraction story

The honest framing: **the reasoning layer is the contribution; extraction is one input pathway among checkboxes, structured forms, and narrative.** We should not position the project as "we cracked the free-text problem." Instead:

1. The LLM extraction demonstrates that the architecture is **source-format-agnostic** — it can accept input from any format (structured form, free text, clinician transcription).
2. The LLM adds value even on checkbox forms by **mapping checkbox semantics to formal intervention classes.** "Comfort care only" on a POLST checkbox maps to a specific set of interventions in our ontology — that mapping is non-trivial.
3. The real contribution is the **closed-world reasoning layer** that produces defensible 4-category outputs regardless of input source.

#### Questions for Magnus on input format

1. **Stanford's AHCD forms:** Which AHCD form does Stanford use or recommend? Is it the California statutory form, the UC-designed one, or something Stanford-specific? What are the checkbox categories?

2. **Checkbox-to-order translation:** When a patient brings in a checkbox AHCD, how does the care team translate those checkboxes into code-status orders? Is there a standard mapping, or is it interpretive?

3. **Where does interpretation fail on checkboxes?** Even with checkboxes, are there common ambiguities? For example:
   - "Comfort care only" — does this mean no antibiotics? No IV fluids? No BiPAP?
   - "Limited interventions" — limited how?
   - Checkboxes that contradict each other (e.g., "no CPR" checked but "full treatment" also checked)

4. **The Letter Project:** Magnus mentioned Periyakoil's work. Does he see the narrative AD format as complementary to checkbox forms, or as a replacement? The Stanford Letter Project RCT found patients preferred it — does he see that as relevant to how we position the LLM extraction?

---

## Part III: Integrated Question Strategy for the Wednesday Meeting

### Priority 1: The code-status reframe (5-7 minutes)

This is the highest-value conversation. Open with:

> "Your note about code-status orders and POLST being what fires at the bedside — that's the critique we want to engage most. If we reframed this as 'a reasoner that translates an AHCD into a defensible POLST or code-status order,' does that address the bedside-workflow critique while preserving what we've built? What would that change about the architecture?"

Then ask him to walk through Stanford's code-status ordering system:
- What are the order categories?
- How granular is it?
- What does the Epic workflow look like?
- Where does translation from AHCD fail?

### Priority 2: ANH addition (2-3 minutes)

> "You flagged that we're missing artificial nutrition/hydration. We agree — it should be a 6th decision point, not deferred. Can you walk us through the clinically meaningful distinctions? Specifically: tube feeding vs. IV hydration vs. TPN, and how those map to POLST Section D and your code-status system."

If ANH has been added before the meeting:
> "You flagged ANH was missing. We've added it as a 6th decision point since your note — tube feeding, artificial hydration, TPN, and withdrawal of each. [Show in ontology.] Did we get the granularity right?"

### Priority 3: Input format positioning (1-2 minutes)

> "You're right that most good AHCDs are checkbox-based. We've been over-indexing on the free-text extraction angle. The more honest positioning is: the reasoning layer is the contribution; LLM extraction is one input pathway among checkboxes, structured forms, and narrative. Does that framing make sense to you?"

### The original five questions (if time remains)

From the Magnus Meeting Notes, in priority order:

1. **4-category output** — "Is Clear / Partial / No coverage / Vague the right ethical shape?"
2. **Category error** — "Is formalizing preferences as graded, conditional logic a category error?"
3. **Surrogate hierarchy** — "Where does reasoner output sit relative to the surrogate?"
4. **Liability** — "What would the system need to produce to be ethically defensible?"
5. **Documented vs. situational preferences** — "Should the system flag high-divergence preferences?"

---

## Part IV: What We Walk Away With

### Best case (all three pivots confirmed)
1. ANH added as 6th decision point with Magnus-validated granularity
2. Project reframed as AHCD → POLST/code-status translation tool
3. LLM extraction honestly positioned as one input pathway
4. Concrete information about Stanford's code-status ordering system to inform the CodeStatusOrder class design

### Minimum viable outcome
1. Magnus's verbal or written assessment of the 4-category output
2. Enough information about code-status ordering to write the "Future Work: AHCD → POLST Translation" section of the final report
3. Confirmation that ANH should be added (even if granularity details come later)

### What to record
For each topic, capture:
- Magnus's direct quotes (verbatim, in quotation marks)
- Specific people/papers/concepts he references
- Disagreements with our framing
- Concrete suggestions for ontology/architecture changes

These become the "Expert Review" subsection of the final report.
