# ADO Live Demo Guide (Class Presentation)

Use this when you have **2–4 extra minutes** after slide 7 (architecture) or slide 9 (results).

## Pick your showcase

| Path | Guide | Time | Best after slide |
|------|-------|------|------------------|
| **Terminal reasoner** | This doc, paths A–C below | 2–5 min | 7 or 9 |
| **Protégé / ontology** | [`Protege_Showcase_Guide.md`](Protege_Showcase_Guide.md) | 3–4 min | 5 or 7 |
| **Combined** | Protégé preference individual → `demo.py --scenario 1` | ~5 min | 5 → 7 |

---

## Prerequisites (do this before class)

```bash
cd /path/to/bmds210-AD_Ontology
pip install owlready2
# Java JRE required for owlready2 and Protégé/HermiT

python -m ado.preference_input --example   # creates data/populated/ado_jane_doe_001.owl
```

**Optional (Scenario 6 — free-text pipeline):**

```bash
pip install anthropic pydantic
export ANTHROPIC_API_KEY="your-key"
```

**Optional (Protégé):** Install from https://protege.stanford.edu/ and open `data/populated/ado_jane_doe_001.owl`. See [`Protege_Showcase_Guide.md`](Protege_Showcase_Guide.md).

---

## Terminal demo paths

### A. Best for 2 minutes — one clear scenario

Shows the **four-category output** on the highest-stakes decision (CPR):

```bash
python scripts/demo.py --scenario 1
```

**What to say while it runs:** Jane Doe, cardiac arrest, NYHA IV, no reversible cause. The system returns **no / clear** and prints which activation conditions matched.

### B. Best for 4–5 minutes — three scenarios + pause

```bash
python scripts/demo.py --pause --scenario 1
python scripts/demo.py --pause --scenario 2   # partial — reversible cause
python scripts/demo.py --pause --scenario 3   # no coverage — silent on ICD
```

| Scenario | Category | Clinical hook |
|----------|----------|----------------|
| 1 | Clear | CPR refused when conditions met |
| 2 | Partial | CPR when reversible cause present |
| 3 | No coverage | ICD question — directive silent |
| 4 | Vague | “No heroic measures” surfaced |
| 5 | Care context | Hospice vs ICU gating |
| 6 | LLM pipeline | Free-text AD → extract → reason (needs API key) |

### C. Full demo (~8 min) — not for an 8-minute talk

```bash
python scripts/demo.py --pause
```

---

## Combined Protégé + terminal (~5 min)

1. **Protégé (2 min):** Open `ado_jane_doe_001.owl` → `ConditionalPreference` → show `originalText` + `hasActivationCondition` on the no-CPR preference. ([script](Protege_Showcase_Guide.md))
2. **Terminal (90 s):** `python scripts/demo.py --scenario 1` — *“Same patient, same preference—here’s the reasoner output clinicians would see.”*
3. **One sentence:** *“Protégé holds the auditable model; Python runs scenario queries at scale.”*

---

## Presentation-day checklist

- [ ] Laptop has **Java** (`java -version`)
- [ ] Terminal font size **18pt+** for audience
- [ ] `python -m ado.preference_input --example` run once
- [ ] Dry-run `python scripts/demo.py --scenario 1`
- [ ] **Protégé:** `ado_jane_doe_001.owl` opens; one preference individual bookmarked
- [ ] **Backup:** `docs/presentation/presentation_figures/ontology_class_hierarchy.png` or evaluation charts

---

## Tie-back to slides

| Demo moment | Slide it supports |
|-------------|-------------------|
| Protégé class tree | 5 |
| `originalText` in Protégé | 4 |
| `demo.py` scenario 1 | 6, 10 |
| Scenario 3 | 6 (no coverage) |
| Scenario 6 | 7 (LLM at boundary only) |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `owlready2` not found | `pip install owlready2` |
| Java error | Install JRE; restart terminal |
| Ontology missing | `python -m ado.preference_input --example` |
| LLM scenario fails | Skip scenario 6; use scenarios 1–3 only |
| Protégé issues | Use backup PNG; see Protege_Showcase_Guide.md |

---

## Evaluation figures (no live demo)

```bash
./scripts/build_presentation_assets.sh
```

Figures land in `docs/presentation/presentation_figures/`.
