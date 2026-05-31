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

**Current results (honest summary):** See [Honest Evaluation Report](docs/Honest_Evaluation_Report.md). Curated vignettes 16/16 dev + 10/10 held-out (single patient); condition-blind ablation 69%; multi-patient cohort stress test (~520 cells) ~47% vs independent reference oracle; Track 3 97% on 12 profiles; extraction F1 0.97 (n=12); inventory coverage 47%. See [Final Report](docs/Final_Report.tex) and [Quantitative Evaluation Plan](docs/Quantitative_Evaluation_Plan.md).

---

## Repository Structure

```
.
├── advanced_directives.owl          # Base OWL ontology (67 classes, 22 properties)
├── preference_input.py              # Structured JSON → populated patient ontology pipeline
├── query_evaluation.py              # Scenario-based reasoner (16 clinical vignettes)
├── code_status.py                   # Aggregates preferences → hospital code status + POLST orders
├── track3_evaluation.py             # Code-status / POLST mapping evaluation (12 profiles)
├── vignette_eval.py                 # Dev + held-out vignettes + condition-blind ablation
├── coverage_analysis.py             # 30-clause inventory representability analysis
├── evaluation_suite.py                # Run all tracks → docs/evaluation_results_summary.md
├── eval_inter_annotator.py          # Dual-annotation κ for extraction gold
├── llm_extraction.py                # Closed-world free-text directive → structured JSON (Claude)
├── extraction_evaluation.py         # LLM extraction precision/recall on real directive text
├── demo.py                          # Six-scenario live demonstration
│
├── populated_ontologies/            # Output: populated patient ontologies
│   ├── example_input.json           #   Example patient preferences (JSON)
│   └── ado_jane_doe_001.owl         #   Example populated ontology
│
├── reference_ads/                   # Reference advance directive documents
│   └── CA Advanced Directive.pdf
│
└── docs/                            # Project documentation and reports
    ├── Final_Report.tex             #   Final report — AMIA format (LaTeX)
    ├── Presentation.tex             #   Final presentation (Beamer)
    ├── Quantitative_Evaluation_Plan.md          # Eval plan + results (Tracks 1–3)
    ├── Magnus_Expert_Review_2026-05-27.md       # Expert review (Dr. Magnus)
    ├── Progress_Report.tex / .md    #   Earlier progress report
    ├── project_pipeline.md          #   Pipeline design and architecture
    ├── Advanced_Directive_Concept_Inventory.md  # 50-template concept inventory
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

### 4. Run the evaluations

```bash
python query_evaluation.py          # Track 1: 16 clinical vignettes (reasoner accuracy)
python track3_evaluation.py         # Track 3: code-status / POLST mapping over 12 profiles
python code_status.py --eval        # derive code status for the example patient vs. gold
python extraction_evaluation.py     # Track 2: LLM extraction precision/recall (needs API key)
```

Track 1 reports decision and match-type accuracy across 16 clinical vignettes. Track 3 derives a hospital code status and POLST orders from each profile and scores them against a POLST-semantics gold standard. Track 2 runs the closed-world LLM extraction over real directive text and reports precision/recall plus an out-of-scope hallucination count.

### 5. Free-text extraction and live demo

```bash
pip install anthropic pydantic      # required for the LLM pipeline
export ANTHROPIC_API_KEY=...        # your Anthropic API key
python demo.py --pause              # walk through the 6 demonstration scenarios
```

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
