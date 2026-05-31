#!/usr/bin/env python3
"""Render a simplified ADO class hierarchy figure for presentations."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ADO_BLUE = "#1e4678"
OUT = Path(__file__).resolve().parents[1] / "docs" / "presentation_figures" / "ontology_class_hierarchy.png"


def box(ax, x, y, w, h, text, fc="white", fs=8, bold=False, text_color="black"):
    p = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.1, edgecolor=ADO_BLUE, facecolor=fc,
    )
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color=text_color, wrap=True)


def main():
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.5)
    ax.axis("off")
    ax.set_title("ADO in Protégé — core structure (67 classes)", fontsize=13, fontweight="bold", color=ADO_BLUE)

    box(ax, 3.0, 5.7, 4.0, 0.5, "OWL 2 ontology (Protégé + HermiT)", fc=ADO_BLUE, fs=10, bold=True, text_color="white")

    # Row 1
    box(ax, 0.2, 4.5, 2.2, 0.55, "Patient\nDecisionMaker", bold=True)
    box(ax, 2.6, 4.5, 2.4, 0.55, "PreferenceStatement\nClear | Conditional | Vague", bold=True)
    box(ax, 5.2, 4.5, 2.3, 0.55, "ActivationCondition\nNYHA • condition • time", bold=True)
    box(ax, 7.7, 4.5, 2.1, 0.55, "ClinicalScenario\n(at query time)", bold=True)

    # Intervention branch
    box(ax, 0.5, 3.35, 9.0, 0.45, "Intervention — five HF decision points", fc="#eef3f9", bold=True)
    branches = [
        "CPR / resuscitation",
        "Ventilation (6 types)",
        "ICD • LVAD • device",
        "Vasopressor / inotrope",
        "Dialysis",
    ]
    for i, b in enumerate(branches):
        box(ax, 0.35 + i * 1.92, 2.55, 1.75, 0.55, b, fs=7)

    # Instance callout
    box(ax, 1.5, 1.35, 7.0, 0.9,
        "Populated example: ado_jane_doe_001.owl\n"
        "Jane Doe → 9× PreferenceStatement → originalText + specifiesIntervention + hasActivationCondition",
        fc="#fff8e6", fs=8)

    ax.text(0.4, 0.2, "Open in Protégé: Entities tab (classes) • Individuals tab (Jane Doe preferences)",
            fontsize=8, color="#555555")
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
