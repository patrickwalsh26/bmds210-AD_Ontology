# ADO Live Demo Guide (Class Presentation)

Use this when you have **2–4 extra minutes** after slide 7 (architecture) or slide 9 (results). The demo is more memorable than another bullet slide.

## Prerequisites (do this before class)

```bash
cd /path/to/bmds210-AD_Ontology
pip install owlready2
# Java JRE required for HermiT (owlready2)

python preference_input.py --example   # creates populated_ontologies/ado_jane_doe_001.owl
```

**Optional (Scenario 6 — free-text pipeline):**

```bash
pip install anthropic pydantic
export ANTHROPIC_API_KEY="your-key"
```

## Recommended demo paths

### A. Best for 2 minutes — one clear scenario

Shows the **four-category output** on the highest-stakes decision (CPR):

```bash
python demo.py --scenario 1
```

**What to say while it runs:** Jane Doe, cardiac arrest, NYHA IV, no reversible cause. The system returns **no / clear** and prints which activation conditions matched.

### B. Best for 4–5 minutes — three scenarios + pause

```bash
python demo.py --pause --scenario 1
# Enter between scenarios; then run 2 and 3 in separate terminals OR re-run with --scenario N
python demo.py --pause --scenario 2   # partial — reversible cause
python demo.py --pause --scenario 3   # no coverage — silent on ICD
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
python demo.py --pause
```

Reserve for office hours or appendix slides.

## Presentation-day checklist

- [ ] Laptop has **Java** (`java -version`)
- [ ] Terminal font size **18pt+** for audience
- [ ] Run `python preference_input.py --example` once in the room (30 s)
- [ ] Dry-run `python demo.py --scenario 1` 
- [ ] **Backup:** show `docs/presentation_figures/conditional_p9_p10.png` if terminal fails
- [ ] If no Wi‑Fi / no API key: **do not** run scenario 6

## Suggested script (Scenario 1, ~90 seconds)

1. *“Jane Doe encoded her AD in our ontology—nine preferences across five HF decision points.”*
2. Run command. Point at **Patient said** quote.
3. Point at **Scenario** line (arrest, NYHA IV, no reversible cause).
4. Point at **Output: NO / CLEAR** and condition checklist.
5. *“That’s the audit trail a progress note needs—not a black-box yes/no.”*

## Tie-back to slides

| Demo moment | Slide it supports |
|-------------|-------------------|
| Scenario 1 | Slide 6 (clear), Slide 10 (conditional CPR) |
| Scenario 3 | Slide 6 (no coverage) |
| Scenario 4 | Slide 6 (vague) |
| Scenario 6 | Slide 7 (LLM at boundary only) |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `owlready2` not found | `pip install owlready2` |
| Java error | Install JRE; restart terminal |
| Ontology missing | `python preference_input.py --example` |
| LLM scenario fails | Skip scenario 6; use scenarios 1–3 only |

## Evaluation figures (no terminal)

If you skip the live demo, use slides with images from:

```bash
python scripts/generate_presentation_figures.py
```

Figures land in `docs/presentation_figures/`.
