#!/usr/bin/env python3
"""
Build fig_ablation_all.png — the combined architecture ablation figure.

Four conditions on the same 16-vignette suite:
  1. Full ADO (ontology + conditional reasoner)     16/16  100%
  2. Condition-blind (ontology, no condition check)  12/16   75%   [naive matcher]
  3. Pure LLM, full-context prompt (no ontology)     12/16   75%
  4. Pure LLM, minimal prompt (no ontology)          10/16   62%

The two pure-LLM arms are Gemini direct-reasoning runs (Arm C of
ablation_evaluation.py). Aggregate accuracies are reported; the figure
visualizes the architecture comparison referenced in the report.

Usage:
    python evaluation/build_ablation_figure.py
"""
from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "presentation_figures" / "fig_ablation_all.png"

BLUE   = "#2166ac"
ORANGE = "#f4a582"
RED    = "#d6604d"
GRAY   = "#999999"
DARK   = "#1a1a1a"

# ── Data ──────────────────────────────────────────────────────────────────────
conditions = [
    "Full ADO\n(ontology +\nconditional reasoner)",
    "Condition-blind\n(ontology,\nno condition check)",
    "Pure LLM\n(full-context\nprompt, no ontology)",
    "Pure LLM\n(minimal\nprompt, no ontology)",
]
correct = [16, 12, 12, 10]
total = 16
pcts = [100 * c / total for c in correct]
colors = [BLUE, ORANGE, "#7fbf7b", RED]


def main():
    fig, ax = plt.subplots(figsize=(8.5, 5))
    x = np.arange(len(conditions))
    bars = ax.bar(x, pcts, color=colors, width=0.62, zorder=3, edgecolor="white")

    ax.axhline(100, color=GRAY, linewidth=0.9, linestyle="--", zorder=1)
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, fontsize=8.5)
    ax.set_ylabel("Decision accuracy (%)", fontsize=11)
    ax.set_ylim(0, 115)
    ax.set_title(
        "Architecture ablation: what the ontology and reasoner add\n"
        "(same 16-vignette suite, identical gold labels)",
        fontsize=11, fontweight="bold"
    )
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)

    for bar, c, p in zip(bars, correct, pcts):
        ax.text(bar.get_x() + bar.get_width()/2, p + 1.8,
                f"{c}/16\n({p:.0f}%)", ha="center", va="bottom",
                fontsize=9.5, fontweight="bold", color=DARK)

    # Qualitative failure annotations (aligned to report prose)
    ax.text(1, 14, "false-confident\non conditionals", ha="center", fontsize=7.2,
            style="italic", color=DARK)
    ax.text(2, 14, "misses\n'vague' cases", ha="center", fontsize=7.2,
            style="italic", color=DARK)
    ax.text(3, 14, "misses all\n'partial' cases", ha="center", fontsize=7.2,
            style="italic", color=DARK)

    fig.tight_layout()
    fig.savefig(OUT, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  saved → {OUT}")


if __name__ == "__main__":
    main()
