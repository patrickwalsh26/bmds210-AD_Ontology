# AGENTS.md

## Cursor Cloud specific instructions

This is a pure-Python CLI research project (no web server, no database, no Docker). All scripts live at the repository root.

### Dependencies

- **Python 3.8+** and **Java JRE** (for the HermiT OWL reasoner invoked by `owlready2`) must be available.
- Python packages: `owlready2` (required), `anthropic` + `pydantic>=2` (optional, for LLM extraction in `llm_extraction.py` / Scenario 6 of `demo.py`).
- Use `python3` — the `python` alias is not available on this VM.

### Running the project

See `README.md` for full usage. Quick reference:

| Command | Purpose |
|---|---|
| `python3 preference_input.py --example` | Populate the example patient ontology |
| `python3 preference_input.py --json populated_ontologies/example_input.json` | Populate from a JSON file |
| `python3 query_evaluation.py` | Run all 16 clinical vignettes (expect 100% pass) |
| `python3 demo.py` | Run the 6-scenario narrated demo |

### Notes

- `query_evaluation.py` is the closest thing to an automated test suite. It runs 16 vignettes and reports decision + match-type accuracy. All 16 should pass.
- Scenario 6 in `demo.py` requires `ANTHROPIC_API_KEY` to run the live LLM extraction path; without it the demo gracefully falls back to a hand-coded example.
- `preference_input.py --interactive` is an interactive CLI questionnaire — avoid in automated/cloud contexts as it requires TTY input.
- There are no lint or type-checking configurations in this repo (no `pyproject.toml`, `setup.cfg`, `mypy.ini`, etc.).
- Output `.owl` files are written to `populated_ontologies/`.
