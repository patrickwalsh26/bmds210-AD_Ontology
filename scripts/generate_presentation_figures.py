#!/usr/bin/env python3
"""
Generate high-resolution evaluation figures for the ADO presentation.

Output: docs/presentation_figures/*.png at 300 DPI (suitable for 16:9 slides).

Regenerate: python3 scripts/generate_presentation_figures.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "presentation_figures"
COHORT_JSON = ROOT / "docs" / "cohort_simulation_results.json"

# Stanford-adjacent palette (accessible, print-safe)
ADO_BLUE = "#1e4678"
ADO_LIGHT = "#4a7ab0"
ADO_MID = "#7ba3d0"
ADO_ACCENT = "#c45c3e"
ADO_GREEN = "#2d6a4f"
ADO_GRAY = "#6c757d"
ADO_GOLD = "#b8860b"

DPI = 300


def _style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.labelweight": "medium",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.dpi": DPI,
    })


def _footnote(ax, text: str, y: float = 0.02):
    ax.text(0.5, y, text, transform=ax.transAxes, ha="center", fontsize=8.5,
            color="#444444", wrap=True)


def _load_cohort() -> dict:
    if COHORT_JSON.exists():
        return json.loads(COHORT_JSON.read_text(encoding="utf-8"))
    return {}


def fig_eval_two_layer():
    """Primary honest results slide: curated spec test vs cohort stress test."""
    cohort = _load_cohort()
    ado_pct = round(cohort.get("ado_decision_accuracy", 0.47) * 100)
    blind_pct = round(cohort.get("condition_blind_accuracy", 0.45) * 100)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), gridspec_kw={"wspace": 0.28})

    # Left: curated vignettes
    ax = axes[0]
    cats = ["Dev\n(n=16)", "Held-out\n(n=10)", "Ablation\n(condition-blind)"]
    vals = [100, 100, 69]
    colors = [ADO_BLUE, ADO_LIGHT, ADO_ACCENT]
    bars = ax.bar(cats, vals, color=colors, width=0.52, edgecolor="white", linewidth=1.5)
    ax.set_ylim(0, 108)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Layer 1 — Curated vignettes\n(single patient, team gold)")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 2.5, f"{v}%",
                ha="center", fontweight="bold", fontsize=12)
    _footnote(ax, "Spec test: proves reasoner matches ontology design")

    # Right: cohort stress
    ax = axes[1]
    cats = ["ADO\n(full)", "Condition-\nblind", "Flat checkbox\n(vs ref.)"]
    vals = [ado_pct, blind_pct, round(cohort.get("checkbox_accuracy", 0.19) * 100)]
    colors = [ADO_BLUE, ADO_ACCENT, ADO_GRAY]
    bars = ax.bar(cats, vals, color=colors, width=0.52, edgecolor="white", linewidth=1.5)
    ax.set_ylim(0, 108)
    ax.set_ylabel("Decision agreement (%)")
    ax.set_title("Layer 2 — Cohort stress test\n(520 cells · 20 patients · 12 scenarios)")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 2.5, f"{v}%",
                ha="center", fontweight="bold", fontsize=12)
    _footnote(ax, "Independent simplified oracle — not hand-adjudicated")

    fig.suptitle("Two-layer evaluation: spec test vs. messy real-world stress",
                 fontsize=15, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / "eval_two_layer.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_eval_overview():
    """Compact four-metric headline (slide 9 sidebar)."""
    cohort = _load_cohort()
    cohort_pct = round(cohort.get("ado_decision_accuracy", 0.47) * 100)

    labels = ["Vignette\ndev", "Ablation\ndev", "Cohort\n520 cells", "POLST\nfields"]
    values = [100, 69, cohort_pct, 97]
    colors = [ADO_BLUE, ADO_ACCENT, ADO_LIGHT, ADO_BLUE]

    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    bars = ax.bar(labels, values, color=colors, width=0.55, edgecolor="white", linewidth=1.5)
    ax.set_ylim(0, 108)
    ax.set_ylabel("Percent agreement / accuracy")
    ax.set_title("Evaluation headline metrics")
    ax.axhline(50, color="#dddddd", linestyle=":", linewidth=1)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 2, f"{v}%",
                ha="center", fontweight="bold", fontsize=11)
    _footnote(ax, "Cohort = 20 template-inspired profiles · F1 on n=12 extraction statements")
    fig.tight_layout()
    fig.savefig(OUT / "eval_overview.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_cohort_messy():
    """Accuracy by messy_level tag."""
    cohort = _load_cohort()
    by = cohort.get("by_messy_level", {})
    if not by:
        by = {
            "clean": {"ado_decision_pct": 56, "blind_pct": 50},
            "typical": {"ado_decision_pct": 43, "blind_pct": 41},
            "minimal": {"ado_decision_pct": 37, "blind_pct": 44},
            "contradictory": {"ado_decision_pct": 46, "blind_pct": 46},
            "incomplete_encoding": {"ado_decision_pct": 42, "blind_pct": 42},
        }
    levels = list(by.keys())
    ado = [by[l]["ado_decision_pct"] for l in levels]
    blind = [by[l]["blind_pct"] for l in levels]

    x = np.arange(len(levels))
    w = 0.36
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(x - w / 2, ado, w, label="ADO (activation-aware)", color=ADO_BLUE, edgecolor="white")
    ax.bar(x + w / 2, blind, w, label="Condition-blind ablation", color=ADO_ACCENT, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels([l.replace("_", "\n") for l in levels], fontsize=9)
    ax.set_ylabel("Decision agreement vs ref. oracle (%)")
    ax.set_ylim(0, 72)
    ax.set_title("Cohort performance by data quality tag")
    ax.legend(loc="upper right", frameon=True, fontsize=9)
    _footnote(ax, "Reference oracle = simplified clinical rules (independent of OWL matcher)")
    fig.tight_layout()
    fig.savefig(OUT / "cohort_messy_breakdown.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_cohort_baselines():
    """ADO vs checkbox overconfidence — value-add chart."""
    cohort = _load_cohort()
    n = cohort.get("n_cells", 520)
    overconf = cohort.get("checkbox_overconfident_cells", 421)
    ado = round(cohort.get("ado_decision_accuracy", 0.47) * 100)
    cb = round(cohort.get("checkbox_accuracy", 0.19) * 100)
    cb_blank = round(cohort.get("checkbox_blank_accuracy", 0.86) * 100)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), gridspec_kw={"width_ratios": [1.1, 1]})

    ax = axes[0]
    labels = ["ADO", "Checkbox\n(silent→full code)", "Checkbox\n(silent→blank)"]
    vals = [ado, cb, cb_blank]
    colors = [ADO_BLUE, ADO_GRAY, ADO_LIGHT]
    bars = ax.bar(labels, vals, color=colors, width=0.5, edgecolor="white")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Agreement with ref. oracle (%)")
    ax.set_title("Baseline comparison (all 520 cells)")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 2, f"{v}%", ha="center", fontweight="bold")

    ax = axes[1]
    ax.barh(["Flat checkbox\noverconfident"], [overconf / n * 100], color=ADO_ACCENT, height=0.35)
    ax.set_xlim(0, 100)
    ax.set_xlabel("% of cohort cells")
    ax.set_title("Nuanced cases collapsed to flat yes/no")
    ax.text(overconf / n * 100 + 2, 0, f"{overconf}/{n} cells ({round(overconf/n*100)}%)",
            va="center", fontweight="bold", fontsize=11)
    _footnote(ax, "Partial / vague / no-coverage gold → checkbox forced clear yes/no")

    fig.suptitle("Cohort stress test: ADO vs. flat POLST-style forms", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / "cohort_baseline_comparison.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_eval_dashboard():
    """Six-panel composite for one results slide (300 DPI, ~12×7 in)."""
    fig = plt.figure(figsize=(12, 7))
    gs = fig.add_gridspec(2, 3, hspace=0.38, wspace=0.32)

    cohort = _load_cohort()
    cohort_pct = round(cohort.get("ado_decision_accuracy", 0.47) * 100)

    # Panel A: vignette splits
    ax = fig.add_subplot(gs[0, 0])
    ax.bar(["Dev\n16", "Hold\n10"], [100, 100], color=[ADO_BLUE, ADO_LIGHT], width=0.45)
    ax.set_ylim(0, 108)
    ax.set_title("Vignettes", fontsize=11)
    ax.set_ylabel("%")
    for i, v in enumerate([100, 100]):
        ax.text(i, v + 3, f"{v}%", ha="center", fontweight="bold", fontsize=10)

    # Panel B: ablation
    ax = fig.add_subplot(gs[0, 1])
    ax.bar(["Full", "Blind"], [100, 69], color=[ADO_BLUE, ADO_ACCENT], width=0.45)
    ax.set_ylim(0, 108)
    ax.set_title("Ablation (dev)", fontsize=11)
    for i, v in enumerate([100, 69]):
        ax.text(i, v + 3, f"{v}%", ha="center", fontweight="bold", fontsize=10)

    # Panel C: cohort headline
    ax = fig.add_subplot(gs[0, 2])
    ax.bar(["Cohort\n520"], [cohort_pct], color=ADO_LIGHT, width=0.35)
    ax.set_ylim(0, 108)
    ax.set_title("Cohort stress", fontsize=11)
    ax.text(0, cohort_pct + 3, f"{cohort_pct}%", ha="center", fontweight="bold", fontsize=10)

    # Panel D: coverage
    ax = fig.add_subplot(gs[1, 0])
    labels = ["Full", "Vague", "Partial", "Who", "OWL", "OOS"]
    counts = [14, 3, 3, 3, 1, 6]
    colors = [ADO_BLUE, ADO_LIGHT, ADO_MID, ADO_ACCENT, ADO_GOLD, ADO_GRAY]
    ax.bar(labels, counts, color=colors, width=0.65)
    ax.set_title("Coverage (n=30)", fontsize=11)
    ax.set_ylabel("clauses")
    for i, c in enumerate(counts):
        ax.text(i, c + 0.2, str(c), ha="center", fontsize=8, fontweight="bold")

    # Panel E: extraction
    ax = fig.add_subplot(gs[1, 1])
    ax.bar(["P", "R", "F1"], [0.94, 1.0, 0.97], color=ADO_BLUE, width=0.5)
    ax.set_ylim(0, 1.08)
    ax.set_title("Extraction (n=12)", fontsize=11)
    for i, v in enumerate([0.94, 1.0, 0.97]):
        ax.text(i, v + 0.03, f"{v:.2f}", ha="center", fontweight="bold", fontsize=9)

    # Panel F: track 3
    ax = fig.add_subplot(gs[1, 2])
    fields = ["Code", "A", "B", "All"]
    correct = [12, 12, 11, 11]
    ax.bar(fields, [c / 12 * 100 for c in correct], color=ADO_BLUE, width=0.55)
    ax.set_ylim(0, 108)
    ax.set_title("POLST mapping (n=12)", fontsize=11)
    for i, c in enumerate(correct):
        ax.text(i, c / 12 * 100 + 3, f"{c}/12", ha="center", fontsize=8, fontweight="bold")

    fig.suptitle("ADO evaluation dashboard — developmental validation (Spring 2026)",
                 fontsize=14, fontweight="bold")
    fig.savefig(OUT / "eval_dashboard.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_study_design():
    """Six evaluation strands diagram."""
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    strands = [
        (1, 4.5, "Vignettes", "16 dev + 10 held-out\n(single patient)"),
        (3.5, 4.5, "Ablation", "Condition-blind\n69% on dev"),
        (6, 4.5, "Cohort sim", "520 cells · 20 profiles\n12 scenarios"),
        (1, 1.8, "Extraction", "n=12 real templates\nF1 0.97"),
        (3.5, 1.8, "Code / POLST", "12 profiles → orders\n35/36 fields"),
        (6, 1.8, "Coverage", "30 inventory clauses\n47% representable"),
    ]
    for x, y, title, sub in strands:
        rect = mpatches.FancyBboxPatch((x - 0.85, y - 0.55), 1.7, 1.1,
                                       boxstyle="round,pad=0.05,rounding_size=0.08",
                                       facecolor=ADO_LIGHT if "Cohort" in title else "#e8eef5",
                                       edgecolor=ADO_BLUE, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x, y + 0.15, title, ha="center", fontweight="bold", fontsize=10, color=ADO_BLUE)
        ax.text(x, y - 0.25, sub, ha="center", fontsize=8, color="#333333")

    ax.annotate("", xy=(5, 3.2), xytext=(5, 3.55),
                arrowprops=dict(arrowstyle="->", color=ADO_ACCENT, lw=2))
    ax.text(5, 3.35, "Developmental — not clinical trial", ha="center", fontsize=10,
            fontweight="bold", color=ADO_ACCENT)
    ax.set_title("Evaluation design: six complementary strands", fontsize=14, fontweight="bold", pad=12)
    fig.tight_layout()
    fig.savefig(OUT / "study_design_strands.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_track3_fields():
    fields = ["Code status", "POLST A", "POLST B", "Exact profile\n(all 3)"]
    correct = [12, 12, 11, 11]
    n = 12

    fig, ax = plt.subplots(figsize=(7.8, 4.2))
    x = np.arange(len(fields))
    bars = ax.bar(x, [c / n * 100 for c in correct], color=ADO_BLUE, width=0.55, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(fields)
    ax.set_ylim(0, 108)
    ax.set_ylabel(f"Agreement (of {n} profiles)")
    ax.set_title("Track 3: directive profiles → bedside orders")
    for bar, c in zip(bars, correct):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                f"{c}/{n}", ha="center", fontweight="bold")
    _footnote(ax, "Gold = POLST published semantics (independent of ADO)")
    fig.tight_layout()
    fig.savefig(OUT / "track3_field_agreement.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_confusion_matrix():
    short = ["Full", "DNR", "DNI", "DNR/\nDNI", "DNE", "DNR/DNI\n+DNE"]
    matrix = np.array([
        [4, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 2, 0, 0],
        [0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 2],
    ])

    fig, ax = plt.subplots(figsize=(7.5, 5.8))
    im = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=4)
    ax.set_xticks(range(6))
    ax.set_yticks(range(6))
    ax.set_xticklabels(short, fontsize=9)
    ax.set_yticklabels(short, fontsize=9)
    ax.set_xlabel("ADO derived", fontweight="medium")
    ax.set_ylabel("Gold (POLST semantics)", fontweight="medium")
    ax.set_title("Code-status confusion matrix (12 profiles)")
    for i in range(6):
        for j in range(6):
            if matrix[i, j] > 0:
                ax.text(j, i, int(matrix[i, j]), ha="center", va="center",
                        color="white" if matrix[i, j] > 2 else ADO_BLUE, fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Count")
    fig.tight_layout()
    fig.savefig(OUT / "code_status_confusion.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_ablation():
    labels = ["Full reasoner", "Condition-blind"]
    acc = [100, 69]
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    bars = ax.bar(labels, acc, color=[ADO_BLUE, ADO_ACCENT], width=0.48, edgecolor="white")
    ax.set_ylim(0, 108)
    ax.set_ylabel("Vignette accuracy (%)")
    ax.set_title("Activation conditions prevent false confidence")
    for bar, v in zip(bars, acc):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 2, f"{v}%", ha="center", fontweight="bold")
    _footnote(ax, "11/16 vs 16/16 · failures on partial / vague / conditional vignettes")
    fig.tight_layout()
    fig.savefig(OUT / "ablation_conditions.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_vignette_outputs():
    types = ["Clear", "Partial", "No coverage", "Vague"]
    counts = [9, 4, 2, 1]
    colors = [ADO_BLUE, ADO_LIGHT, ADO_MID, "#a8c4e8"]

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    wedges, _, autotexts = ax.pie(
        counts, labels=types, autopct="%1.0f%%", colors=colors,
        startangle=90, textprops={"fontsize": 10},
        wedgeprops={"edgecolor": "white", "linewidth": 1.2},
    )
    for t in autotexts:
        t.set_fontweight("bold")
    ax.set_title("16 vignettes: expected match-type mix")
    fig.tight_layout()
    fig.savefig(OUT / "vignette_match_types.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_conditional_flip():
    scenarios = ["Condition met\n(NYHA IV, no reversible)", "Condition not met\n(NYHA III, reversible)"]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    bars = ax.barh(scenarios, [1, 1], color=[ADO_ACCENT, ADO_BLUE], height=0.42, edgecolor="white")
    ax.set_xlim(0, 1.4)
    ax.set_xticks([])
    ax.set_title('"No CPR if NYHA IV and no reversible cause"')
    for bar, code in zip(bars, ["DNR", "Full code"]):
        ax.text(0.5, bar.get_y() + bar.get_height() / 2, code,
                ha="center", va="center", fontsize=14, fontweight="bold", color="white")
    _footnote(ax, "ADO preserves if/then — flat POLST cannot")
    fig.tight_layout()
    fig.savefig(OUT / "conditional_p9_p10.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_vignette_splits():
    fig, ax = plt.subplots(figsize=(5.8, 4.2))
    bars = ax.bar(["Development\n(n=16)", "Held-out\n(n=10)"], [100, 100],
                  color=[ADO_BLUE, ADO_LIGHT], width=0.45, edgecolor="white")
    ax.set_ylim(0, 108)
    ax.set_ylabel("Decision + match-type accuracy (%)")
    ax.set_title("Track 1: vignette splits")
    for bar, v in zip(bars, [100, 100]):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 2, f"{v}%", ha="center", fontweight="bold")
    _footnote(ax, "Same patient ontology (Jane Doe)")
    fig.tight_layout()
    fig.savefig(OUT / "vignette_splits.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_coverage():
    labels = ["Fully\nrepresentable", "Vague", "Partial\nloss", "Who-\ndecides", "OWL\ngap", "Out of\nscope"]
    counts = [14, 3, 3, 3, 1, 6]
    colors = [ADO_BLUE, ADO_LIGHT, ADO_MID, ADO_ACCENT, ADO_GOLD, ADO_GRAY]
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    x = np.arange(len(labels))
    bars = ax.bar(x, counts, color=colors, width=0.62, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Clauses (of 30)")
    ax.set_title("Inventory coverage — 47% fully representable")
    for bar, c in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
                str(c), ha="center", fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "coverage_inventory.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def fig_extraction_metrics():
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    bars = ax.bar(["Precision", "Recall", "F1"], [0.94, 1.00, 0.97],
                  color=ADO_BLUE, width=0.5, edgecolor="white")
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Score")
    ax.set_title("LLM extraction (n=12 template clauses)")
    for bar, v in zip(bars, [0.94, 1.00, 0.97]):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.02, f"{v:.2f}", ha="center", fontweight="bold")
    _footnote(ax, "0 hallucinations on out-of-scope nutrition & antibiotics")
    fig.tight_layout()
    fig.savefig(OUT / "extraction_f1.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def main():
    _style()
    OUT.mkdir(parents=True, exist_ok=True)
    fig_eval_two_layer()
    fig_eval_overview()
    fig_eval_dashboard()
    fig_study_design()
    fig_cohort_messy()
    fig_cohort_baselines()
    fig_track3_fields()
    fig_confusion_matrix()
    fig_ablation()
    fig_vignette_outputs()
    fig_conditional_flip()
    fig_vignette_splits()
    fig_coverage()
    fig_extraction_metrics()
    print(f"Wrote {len(list(OUT.glob('*.png')))} figures to {OUT}/ at {DPI} DPI")


if __name__ == "__main__":
    main()
