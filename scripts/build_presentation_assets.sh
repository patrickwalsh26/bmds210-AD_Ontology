#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
pip install python-pptx matplotlib -q
python3 scripts/generate_presentation_figures.py
python3 scripts/generate_ontology_overview_figure.py
python3 scripts/insert_presentation_figures.py
python3 scripts/update_presentation_notes.py
echo "Done:"
echo "  Deck:  docs/presentation/ADO_powerpoint_presentation.pptx"
echo "  Figures: docs/presentation/presentation_figures/"
echo "  Guide: docs/presentation/PPT_Figures_Guide.md"
