# Protégé Showcase Guide (Class Presentation)

Use this when you want the audience to **see the ontology itself**—the class hierarchy, properties, and Jane Doe’s preference individuals—instead of (or in addition to) a terminal `demo.py` run.

**Best moment in the talk:** After slide **5** (ontology scope) or slide **7** (architecture), for **2–4 minutes**.

---

## Choose your showcase mode

| Mode | Time | What the audience sees | When to use |
|------|------|------------------------|-------------|
| **A. Live Protégé** | 3–4 min | Real editor: class tree, one preference individual, optional HermiT | Room has projector; Protégé installed and tested |
| **B. Populated ontology only** | 2–3 min | `ado_jane_doe_001.owl` — full pipeline output, 9 prefs | You built the story on slide 4 already |
| **C. Backup slides** | 0 min live | PNG hierarchy in `docs/presentation_figures/ontology_class_hierarchy.png` | No Protégé on laptop or Java issues |

You can combine **B + A**: open populated file, then show one preference in Protégé.

---

## Before class

### Install

1. Download [Protégé 5.6+](https://protege.stanford.edu/) (free).
2. Install a **Java JRE** (Protégé and HermiT need it).
3. Clone/pull the repo and generate Jane’s populated ontology:

```bash
pip install owlready2
python preference_input.py --example
```

Files to have ready:

| File | Purpose |
|------|---------|
| `advanced_directives.owl` | Base TBox — 67 classes, properties, example individuals |
| `populated_ontologies/ado_jane_doe_001.owl` | **Best for demo** — Jane Doe, 9 preferences from JSON pipeline |

### Optional: pre-open tabs in Protégé

- **Active ontology:** `ado_jane_doe_001.owl`
- **Selected tabs:** Entities (class hierarchy), Individuals by class, Object property hierarchy

---

## Live showcase script (~3 minutes)

### 1. Class hierarchy (45 s) — slide 5 payoff

**Open:** `advanced_directives.owl` (or stay on populated file and switch to **Entities** tab).

**Say:** *“This is OWL 2 in Protégé—the same stack used for SNOMED and OBO ontologies. ADO is scoped to five HF decision points.”*

**Show:**

1. **Entities** → class hierarchy (left panel).
2. Expand **`Intervention`** → five branches:
   - `ResuscitationIntervention` → CPR, defibrillation, …
   - `VentilationIntervention` → temporary vs indefinite, …
   - `DeviceIntervention` → ICD, LVAD, …
   - `VasopressorInotropeIntervention`
   - `DialysisIntervention`
3. Point at **`PreferenceStatement`** and subclasses: `ClearPreference`, `ConditionalPreference`, `VaguePreference`.

**Say:** *“Granularity matters—a generic AD checkbox doesn’t distinguish temporary from indefinite ventilation; we do.”*

---

### 2. One preference individual (90 s) — slide 4 payoff

**Open:** `populated_ontologies/ado_jane_doe_001.owl`

**Say:** *“The Python pipeline turns structured JSON into OWL individuals. Here’s the same CPR preference we showed on slide 4.”*

**Navigate:**

1. **Individuals** tab → class **`ConditionalPreference`** (or search `Pref` / `NoCPR`).
2. Select **`Pref_JaneDoe_NoCPR`** (or populated equivalent — names may be `pref_jane_doe_001_no_cpr` style).

**Point at property assertions (right panel):**

| Property | What to say |
|----------|-------------|
| `specifiesIntervention` | Links to **CPR** |
| `hasActivationCondition` | Click through → NYHA IV, no reversible cause |
| `isNegated` | **true** = refusal |
| `hasPreferenceStrength` | Absolute |
| `originalText` | *“This is the audit trail—patient words in the ontology.”* |

**Optional:** **Window → Views → Ontology views → Object property assertions** if the layout is crowded.

---

### 3. Patient + document (30 s)

1. Individual **`Jane Doe`** / `ExamplePatient_JaneDoe` / `patient_jane_doe_001`.
2. Show **`hasPreference`** list (9 statements).
3. **`hasProxy`** → healthcare proxy individual.

**Say:** *“One patient, many preference objects—each testable against a scenario. That’s what the reasoner walks.”*

---

### 4. HermiT reasoner (30 s) — optional, impressive if it works

**Say:** *“OWL gives us formal semantics—we can check consistency.”*

1. **Reasoner** menu → select **HermiT**.
2. **Reasoner → Start reasoner** (wait for classification).
3. Show no unsatisfiable classes (or explain any inference you pre-planned).

**Caveat if asked:** Scenario matching runs in our **Python query engine** (`query_evaluation.py`), not only in Protégé. Protégé validates the **model**; the vignette suite validates **behavior**.

**If HermiT fails in class:** Skip it. Say: *“Classification is for consistency; our evaluation is scenario-based.”*

---

## Tie-back to slides & terminal demo

| Protégé moment | Slide | Terminal equivalent |
|----------------|-------|---------------------|
| Class tree under `Intervention` | 5 | — |
| `originalText` on preference | 4 | `demo.py --scenario 1` prints patient quote |
| `hasActivationCondition` | 10 | Scenario A/B CPR flip |
| 9 preferences on patient | 7 | `preference_input.py --example` |

**Combined 5-minute segment:** Protégé steps 1–2 (2 min) → switch to terminal → `python demo.py --scenario 1` (90 s).

---

## Presentation-day checklist

- [ ] Protégé opens `ado_jane_doe_001.owl` without errors
- [ ] Font size in Protégé increased (**View → Increase font** or OS zoom)
- [ ] Close unrelated ontologies (only ADO loaded)
- [ ] Backup PNG: `docs/presentation_figures/ontology_class_hierarchy.png`
- [ ] Backup: `demo.py --scenario 1` if Protégé crashes

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| “Ontology not found” | File → Open → select `.owl` from repo path |
| Blank individuals | Open **populated** file, not empty base only |
| HermiT won’t start | Install JRE; Reasoner → HermiT → check log |
| Too many example individuals | Use `ado_jane_doe_001.owl` (pipeline output), not draft files |
| Populated file missing | `python preference_input.py --example` |

---

## What *not* to do in 8 minutes

- Don’t walk all 67 classes.
- Don’t edit axioms live unless you’ve rehearsed.
- Don’t promise Protégé *is* the clinical UI—it’s the **authoring and inspection** layer.

---

## Regenerate hierarchy figure (backup slide)

```bash
python scripts/generate_ontology_overview_figure.py
```

Output: `docs/presentation_figures/ontology_class_hierarchy.png` — optional insert on slide 5.
