#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
pip install python-pptx matplotlib -q
python3 scripts/generate_presentation_figures.py
python3 scripts/generate_ontology_overview_figure.py
python3 scripts/insert_presentation_figures.py
echo "Done: ADO_powerpoint_presentation.pptx + docs/presentation_figures/*.png"
echo "See docs/PPT_Figures_Guide.md for slide-by-slide placement."
