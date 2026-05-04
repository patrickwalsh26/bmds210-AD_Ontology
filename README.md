# Toward a Computable Ontology of End-of-Life Care Preferences in Advanced Heart Failure

**BMDS 210 / CS 270 — Spring 2026**

This project builds an OWL ontology (the Advance Directive Ontology, or ADO) that formally represents end-of-life care preferences for patients with advanced heart failure. The ontology covers five clinical decision points: CPR/resuscitation, mechanical ventilation, ICD deactivation, vasopressor/inotrope escalation, and dialysis.

## Repository Structure

```
.
├── advanced_directives.owl              # Base OWL ontology (67 classes, 20 properties)
├── preference_input.py                  # Python pipeline for populating the ontology
├── populated_ontologies/                # Output directory for populated patient ontologies
│   ├── example_input.json              # Example patient preference JSON
│   └── ado_jane_doe_001.owl            # Example populated ontology
├── Advanced_Directive_Concept_Inventory.md  # 50-template concept inventory
├── project_pipeline.md                  # Full project pipeline and design documentation
├── Progress_Report.md                   # Progress report
├── BMDS210_proposal.docx                # Original project proposal
├── Advanced Directives/                 # Reference AD documents
│   └── CA Advanced Directive.pdf
└── ontology-55.owl                      # Earlier ontology draft
```

## Setup

### Requirements

- Python 3.8+
- Java Runtime Environment (required by owlready2's HermiT reasoner)

### Installation

```bash
pip install owlready2
```

## Usage

### 1. Generate and populate the example patient

```bash
python preference_input.py --example
```

This creates `populated_ontologies/example_input.json` (the input data) and `populated_ontologies/ado_jane_doe_001.owl` (the populated ontology). Open the `.owl` file in [Protege](https://protege.stanford.edu/) to inspect individuals and run the HermiT reasoner.

### 2. Populate from a JSON file

```bash
python preference_input.py --json path/to/patient_preferences.json
```

See `populated_ontologies/example_input.json` for the expected schema. Each preference includes:
- `intervention` — one of 21 intervention types (e.g., `cpr`, `icd_deactivation`, `acute_dialysis`)
- `negated` — whether the patient does NOT want this intervention
- `strength` — `Absolute`, `Strong`, `Conditional`, or `Weak`
- `activation_conditions` — optional conditions (NYHA class, clinical conditions, reversible cause, time bounds, care context)

### 3. Interactive CLI questionnaire

```bash
python preference_input.py --interactive
```

Walks through each of the 5 decision points and prompts for preferences interactively.

## Viewing the Ontology

1. Download [Protege](https://protege.stanford.edu/) (free, open source)
2. Open `advanced_directives.owl` to view the base ontology class hierarchy
3. Open any file in `populated_ontologies/` to view a populated patient instance
4. Use Reasoner > HermiT to run classification and consistency checking

## Intervention Types

| Decision Point | Available Interventions |
|---|---|
| CPR / Resuscitation | `cpr`, `defibrillation`, `transcutaneous_pacing` |
| Mechanical Ventilation | `intubation`, `mechanical_ventilation`, `temporary_ventilation`, `indefinite_ventilation`, `non_invasive_ventilation`, `ventilation_withdrawal` |
| ICD / Device Management | `icd_deactivation`, `icd_shock_therapy`, `lvad_withdrawal`, `lvad_continuation`, `pacemaker_deactivation` |
| Vasopressor / Inotrope | `inotrope_escalation`, `inotrope_withdrawal`, `vasopressor_escalation`, `vasopressor_withdrawal` |
| Dialysis | `acute_dialysis`, `chronic_dialysis`, `dialysis_withdrawal` |
