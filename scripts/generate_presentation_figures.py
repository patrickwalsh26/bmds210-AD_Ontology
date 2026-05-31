#!/usr/bin/env python3
"""Generate evaluation figures for the ADO presentation (docs/presentation_figures/)."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ADO_BLUE = "#1e4678"
ADO_LIGHT = "#4a7ab0"
ADO_ACCENT = "#c45c3e"
OUT = Path(__file__).resolve().parents[1] / "docs" / "presentation_figures"


def _style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "figure.facecolor": "white",
    })



def fig_cohort_messy():
    """Cohort simulation accuracy by messy_level (vs independent reference oracle)."""
    import json
    results_path = Path(__file__).resolve().parents[1] / "docs" / "cohort_simulation_results.json"
    if results_path.exists():
        data = json.loads(results_path.read_text())
        by = data.get("by_messy_level", {})
        levels = list(by.keys())
        ado = [by[l]["ado_decision_pct"] for l in levels]
        blind = [by[l]["blind_pct"] for l in levels]
    else:
        levels = ["clean", "typical", "minimal", "contradictory", "incomplete_encoding"]
        ado = [56, 43, 37, 46, 42]
        blind = [50, 41, 44, 46, 42]

    x = np.arange(len(levels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.bar(x - w / 2, ado, w, label="ADO (full)", color=ADO_BLUE)
    ax.bar(x + w / 2, blind, w, label="Condition-blind", color=ADO_ACCENT)
    ax.set_xticks(x)
    ax.set_xticklabels([l.replace("_", "\n") for l in levels], fontsize=9)
    ax.set_ylabel("Decision agreement vs ref. oracle (%)")
    ax.set_ylim(0, 75)
    ax.set_title("520-cell cohort stress test (20 patients x 12 scenarios)")
    ax.legend(loc="upper right", fontsize=9)
    ax.text(0.02, 0.02, "Reference = simplified rules, not OWL matcher",
            transform=ax.transAxes, fontsize=8.5, color="#555555")
    fig.tight_layout()
    fig.savefig(OUT / "cohort_messy_breakdown.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_eval_overview():
    """Headline metrics for slide 9."""
    labels = [
        "Vignette\n(dev)",
        "Ablation\n(dev)",
        "Cohort\n520 cells",
        "POLST\nfields",
    ]
    values = [100, 69, 47, 97]
    colors = [ADO_BLUE, ADO_BLUE, ADO_LIGHT, ADO_LIGHT]

    fig, ax = plt.subplots(figsize=(8, 4.2))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=1.2)
    ax.set_ylim(0, 108)
    ax.set_ylabel("Percent correct / agreement")
    ax.set_title("ADO evaluation summary (Tracks 1–3)")
    ax.axhline(100, color="#cccccc", linestyle="--", linewidth=0.8)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 2, f"{v}%", ha="center", fontweight="bold")
    ax.text(0.02, 0.02, "Vignettes = spec test; cohort = 20 messy profiles vs simplified oracle • F1 n=12 real-template statements • 35/36 POLST-semantics fields",
            transform=ax.transAxes, fontsize=9, color="#555555")
    fig.tight_layout()
    fig.savefig(OUT / "eval_overview.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_track3_fields():
    """Per-field agreement for Track 3."""
    fields = ["Code status", "POLST A", "POLST B", "Exact profile\n(all 3 fields)"]
    correct = [12, 12, 11, 11]
    n = 12

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    x = np.arange(len(fields))
    bars = ax.bar(x, [c / n * 100 for c in correct], color=ADO_BLUE, width=0.55)
    ax.set_xticks(x)
    ax.set_xticklabels(fields)
    ax.set_ylim(0, 108)
    ax.set_ylabel(f"Agreement (of {n} profiles)")
    ax.set_title("Track 3: directive profiles → bedside orders")
    for bar, c in zip(bars, correct):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                f"{c}/{n}", ha="center", fontweight="bold")
    ax.text(0.02, 0.02, "Gold = POLST published semantics (independent of ADO)",
            transform=ax.transAxes, fontsize=9, color="#555555")
    fig.tight_layout()
    fig.savefig(OUT / "track3_field_agreement.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_confusion_matrix():
    """Code-status confusion matrix (diagonal = agreement)."""
    cats = ["Full code", "DNR", "DNI", "DNR/DNI", "DNE", "DNR/DNI+DNE"]
    short = ["Full", "DNR", "DNI", "DNR/\nDNI", "DNE", "DNR/DNI\n+DNE"]
    # rows=gold, cols=derived — from track3_evaluation.py output
    matrix = np.array([
        [4, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 2, 0, 0],
        [0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 2],
    ])

    fig, ax = plt.subplots(figsize=(7.2, 5.5))
    im = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=4)
    ax.set_xticks(range(len(cats)))
    ax.set_yticks(range(len(cats)))
    ax.set_xticklabels(short, fontsize=9)
    ax.set_yticklabels(short, fontsize=9)
    ax.set_xlabel("ADO derived")
    ax.set_ylabel("Gold (POLST semantics)")
    ax.set_title("Code-status confusion matrix (12 profiles)")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if matrix[i, j] > 0:
                ax.text(j, i, int(matrix[i, j]), ha="center", va="center",
                        color="white" if matrix[i, j] > 2 else ADO_BLUE, fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="Count")
    fig.tight_layout()
    fig.savefig(OUT / "code_status_confusion.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_ablation():
    """Full reasoner vs condition-blind sensitivity."""
    labels = ["Full reasoner\n(activation conditions)", "Condition-blind\n(ignore conditions)"]
    acc = [100, 69]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, acc, color=[ADO_BLUE, ADO_ACCENT], width=0.5)
    ax.set_ylim(0, 108)
    ax.set_ylabel("Vignette accuracy (%)")
    ax.set_title("Why conditionality matters (16 vignettes)")
    for bar, v in zip(bars, acc):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 2, f"{v}%", ha="center", fontweight="bold")
    ax.text(0.5, 0.04, "11/16 vs 16/16 when activation conditions ignored (5 partial-case failures) are conditional/partial cases",
            transform=ax.transAxes, ha="center", fontsize=9, color="#555555")
    fig.tight_layout()
    fig.savefig(OUT / "ablation_conditions.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_vignette_outputs():
    """Distribution of expected match types in vignette suite."""
    types = ["Clear", "Partial", "No coverage", "Vague"]
    counts = [9, 4, 2, 1]
    colors = [ADO_BLUE, ADO_LIGHT, "#7ba3d0", "#a8c4e8"]

    fig, ax = plt.subplots(figsize=(6, 4))
    wedges, _, autotexts = ax.pie(
        counts, labels=types, autopct="%1.0f%%", colors=colors,
        startangle=90, textprops={"fontsize": 10},
    )
    for t in autotexts:
        t.set_fontweight("bold")
    ax.set_title("16 vignettes: expected match-type mix")
    fig.tight_layout()
    fig.savefig(OUT / "vignette_match_types.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_conditional_flip():
    """P9 vs P10: same directive, different scenario."""
    scenarios = ["Condition met\n(NYHA IV, no reversible cause)", "Condition not met\n(NYHA III, reversible)"]
    codes = ["DNR", "Full code"]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    bars = ax.barh(scenarios, [1, 1], color=[ADO_ACCENT, ADO_BLUE], height=0.45)
    ax.set_xlim(0, 1.4)
    ax.set_xticks([])
    ax.set_title('Same directive: "No CPR if NYHA IV and no reversible cause"')
    for bar, code in zip(bars, codes):
        ax.text(0.5, bar.get_y() + bar.get_height() / 2, code,
                ha="center", va="center", fontsize=14, fontweight="bold", color="white")
    ax.text(0.5, -0.22, "ADO preserves if/then — flat POLST cannot",
            transform=ax.transAxes, ha="center", fontsize=9, color="#555555")
    fig.tight_layout()
    fig.savefig(OUT / "conditional_p9_p10.png", dpi=180, bbox_inches="tight")
    plt.close(fig)



def fig_vignette_splits():
    labels = ["Development\n(n=16)", "Held-out\n(n=10)"]
    acc = [100, 100]
    fig, ax = plt.subplots(figsize=(5.5, 4))
    bars = ax.bar(labels, acc, color=[ADO_BLUE, ADO_LIGHT], width=0.45)
    ax.set_ylim(0, 108)
    ax.set_ylabel("Decision + match-type accuracy (%)")
    ax.set_title("Track 1: vignette splits (same patient ontology)")
    for bar, v in zip(bars, acc):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 2, f"{v}%", ha="center", fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "vignette_splits.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_coverage():
    labels = ["Fully\nrepresentable", "Vague\nonly", "Partial\nloss", "Who-decides\ngap", "OWL\ngap", "Out of\nscope"]
    counts = [14, 3, 3, 3, 1, 6]
    colors = [ADO_BLUE, ADO_LIGHT, "#7ba3d0", ADO_ACCENT, "#d4a574", "#aaaaaa"]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    x = np.arange(len(labels))
    bars = ax.bar(x, counts, color=colors, width=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Clauses (of 30)")
    ax.set_title("Inventory coverage (30 clauses from 50-template inventory)")
    for bar, c in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15, str(c), ha="center", fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "coverage_inventory.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_extraction_metrics():
    fig, ax = plt.subplots(figsize=(6, 3.8))
    metrics = ["Precision", "Recall", "F1"]
    vals = [0.94, 1.00, 0.97]
    bars = ax.bar(metrics, vals, color=ADO_BLUE, width=0.5)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Score")
    ax.set_title("LLM extraction (n=12 template clauses)")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.02, f"{v:.2f}", ha="center", fontweight="bold")
    ax.text(0.5, 0.02, "0 hallucinations on out-of-scope nutrition & antibiotics", transform=ax.transAxes, ha="center", fontsize=9, color="#555555")
    fig.tight_layout()
    fig.savefig(OUT / "extraction_f1.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    _style()
    OUT.mkdir(parents=True, exist_ok=True)
    fig_eval_overview()
    fig_track3_fields()
    fig_confusion_matrix()
    fig_cohort_messy()
    fig_ablation()
    fig_vignette_outputs()
    fig_conditional_flip()
    fig_vignette_splits()
    fig_coverage()
    fig_extraction_metrics()
    print(f"Wrote figures to {OUT}/")


if __name__ == "__main__":
    main()
