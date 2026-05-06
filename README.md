# Advance Directive Ontology (ADO)

**Toward a Computable Ontology of End-of-Life Care Preferences in Advanced Heart Failure**

Patrick Walsh and Darren Chan | BMDS 210 / CS 270 | Spring 2026 | Stanford University

---

## Overview

Advance directives are almost entirely free-text documents that clinicians must interpret under time pressure during acute crises. This project builds an OWL ontology that formally represents end-of-life care preferences for patients with advanced heart failure, enabling automated reasoning over patient preferences to determine what care is indicated in a given clinical scenario.

The ontology covers **five clinical decision points** commonly encountered in advanced heart failure:

| Decision Point | Intervention Classes | Why It Matters |
|---|---|---|
| CPR / Resuscitation | 3 | Most time-critical; vague AD language fails here |
| Mechanical Ventilation | 6 | ADs rarely distinguish temporary from indefinite |
| ICD / Device Management | 5 | ~200K HF patients have ICDs; most ADs ignore this |
| Vasopressor / Inotrope | 4 | Almost never addressed in standard ADs |
| Dialysis | 3 | ADs don't distinguish acute from chronic |

**Current results:** 92% decision accuracy and 100% match-type accuracy across 12 clinical vignettes (see [Progress Report](docs/Progress_Report.tex)).

---

## Repository Structure

```
.
├── advanced_directives.owl          # Base OWL ontology (67 classes, 20 properties)
├── preference_input.py              # Structured preference input pipeline
├── query_evaluation.py              # Scenario-based query evaluation (12 vignettes)
│
├── populated_ontologies/            # Output: populated patient ontologies
│   ├── example_input.json           #   Example patient preferences (JSON)
│   └── ado_jane_doe_001.owl         #   Example populated ontology
│
├── reference_ads/                   # Reference advance directive documents
│   └── CA Advanced Directive.pdf
│
└── docs/                            # Project documentation and reports
    ├── Progress_Report.tex          #   Progress report (LaTeX)
    ├── Progress_Report.md           #   Progress report (Markdown)
    ├── project_pipeline.md          #   Full pipeline design and architecture
    ├── Advanced_Directive_Concept_Inventory.md  # 50-template concept inventory
    ├── BMDS210_proposal.docx        #   Original project proposal
    ├── CS 270 Project Proposal.pdf  #   Project proposal (PDF)
    ├── Project_Progress_Report_Template-2.pdf   # Report template
    └── ontology_draft_v1.owl        #   Earlier ontology draft
```

---

## Getting Started

### Requirements

- Python 3.8+
- Java Runtime Environment (required by owlready2's HermiT reasoner)

### Installation

```bash
git clone https://github.com/patrickwalsh26/bmds210-AD_Ontology.git
cd bmds210-AD_Ontology
pip install owlready2
```

---

## Usage

### 1. Generate the example patient ontology

```bash
python preference_input.py --example
```

Creates `populated_ontologies/example_input.json` (input data) and `populated_ontologies/ado_jane_doe_001.owl` (populated ontology). Open the `.owl` file in [Protege](https://protege.stanford.edu/) to inspect individuals and run the HermiT reasoner.

### 2. Populate from a JSON file

```bash
python preference_input.py --json path/to/patient_preferences.json
```

See `populated_ontologies/example_input.json` for the expected schema. Each preference includes:

| Field | Description | Example |
|---|---|---|
| `intervention` | One of 21 intervention types | `cpr`, `icd_deactivation`, `acute_dialysis` |
| `negated` | Whether the patient does NOT want this | `true` / `false` |
| `strength` | Preference strength | `Absolute`, `Strong`, `Conditional`, `Weak` |
| `type` | Preference classification | `clear`, `conditional`, `vague` |
| `original_text` | Patient's own words | Free text |
| `activation_conditions` | When the preference applies | NYHA class, conditions, reversibility, time bounds |

### 3. Interactive CLI questionnaire

```bash
python preference_input.py --interactive
```

Walks through each of the 5 decision points and prompts for preferences interactively. Saves both the input JSON and populated ontology.

### 4. Run the scenario-based evaluation

```bash
python query_evaluation.py
python query_evaluation.py --owl path/to/populated_ontology.owl
```

Runs 12 clinical vignettes against the populated ontology and reports decision accuracy and match-type accuracy. Each vignette tests whether the system correctly infers what care is indicated given the patient's encoded preferences and a clinical scenario.

---

## Viewing the Ontology in Protege

1. Download [Protege](https://protege.stanford.edu/) (free, open source)
2. Open `advanced_directives.owl` to view the base class hierarchy
3. Open any file in `populated_ontologies/` to view a populated patient instance
4. Use **Reasoner > HermiT** to run classification and consistency checking

---

## Intervention Reference

| Decision Point | Keys |
|---|---|
| CPR / Resuscitation | `cpr`, `defibrillation`, `transcutaneous_pacing` |
| Mechanical Ventilation | `intubation`, `mechanical_ventilation`, `temporary_ventilation`, `indefinite_ventilation`, `non_invasive_ventilation`, `ventilation_withdrawal` |
| ICD / Device Management | `icd_deactivation`, `icd_shock_therapy`, `lvad_withdrawal`, `lvad_continuation`, `pacemaker_deactivation` |
| Vasopressor / Inotrope | `inotrope_escalation`, `inotrope_withdrawal`, `vasopressor_escalation`, `vasopressor_withdrawal` |
| Dialysis | `acute_dialysis`, `chronic_dialysis`, `dialysis_withdrawal` |

---

## Project Documentation

| Document | Description |
|---|---|
| [Progress Report (LaTeX)](docs/Progress_Report.tex) | Current progress report with evaluation results and citations |
| [Pipeline Design](docs/project_pipeline.md) | Full architecture, design decisions, and evaluation plan |
| [Concept Inventory](docs/Advanced_Directive_Concept_Inventory.md) | 50 advance directive templates across 8 categories |
| [Original Proposal](docs/BMDS210_proposal.docx) | Initial project proposal |
