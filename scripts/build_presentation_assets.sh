#!/usr/bin/env bash
# Regenerate figures, speaker notes, and embedded images for the class deck.
set -euo pipefail
cd "$(dirname "$0")/.."
pip install python-pptx matplotlib -q
python3 scripts/generate_presentation_figures.py
python3 scripts/update_presentation_notes.py
python3 scripts/insert_presentation_figures.py
echo "Done. Open ADO_powerpoint_presentation.pptx — move slide 'EVALUATION FIGURES' to after slide 9 if needed."
