"""Repository path constants (single source of truth)."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OWL_FILE = PROJECT_ROOT / "advanced_directives.owl"
POPULATED_DIR = PROJECT_ROOT / "data" / "populated"
GOLD_DIR = PROJECT_ROOT / "data" / "gold"
REFERENCE_ADS_DIR = PROJECT_ROOT / "data" / "reference_ads"

DOCS_DIR = PROJECT_ROOT / "docs"
EVAL_DOCS_DIR = DOCS_DIR / "evaluation"
PRESENTATION_DIR = DOCS_DIR / "presentation"
FIGURES_DIR = PRESENTATION_DIR / "presentation_figures"

DEFAULT_POPULATED_OWL = POPULATED_DIR / "ado_jane_doe_001.owl"
EXAMPLE_INPUT_JSON = POPULATED_DIR / "example_input.json"
