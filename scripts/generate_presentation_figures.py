#!/usr/bin/env python3
"""
Publication-quality figures for ADO presentation (Nature-style layout).

Outputs:
  - docs/presentation_figures/*.png  (300 DPI, PNG)
  - docs/presentation_figures/FIGURE_CAPTIONS.md  (slide captions)

Regenerate:
  python3 scripts/generate_presentation_figures.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "presentation_figures"
COHORT_JSON = ROOT / "docs" / "cohort_simulation_results.json"
CAPTIONS_MD = OUT / "FIGURE_CAPTIONS.md"

DPI = 300

# Nature Communications–inspired, colorblind-friendly palette
C = {
    "primary": "#0072B2",      # blue
    "secondary": "#E69F00",    # amber
    "tertiary": "#009E73",     # green
    "accent": "#CC79A7",       # rose
    "neutral": "#56B4E9",      # sky
    "dark": "#2F2F2F",
    "muted": "#7A7A7A",
    "grid": "#E6E6E6",
    "fill_a": "#D5E8F0",
    "fill_b": "#FDF2E3",
    "fill_c": "#E8F5F0",
}

# Populated after each figure is built
CAPTIONS: dict[str, str] = {}


def _style():
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "600",
        "axes.labelsize": 10,
        "axes.labelcolor": C["dark"],
        "axes.edgecolor": "#CCCCCC",
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": C["dark"],
        "ytick.color": C["dark"],
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "legend.frameon": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.dpi": DPI,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.12,
    })


def _load_cohort() -> dict:
    if COHORT_JSON.exists():
        return json.loads(COHORT_JSON.read_text(encoding="utf-8"))
    return {}


def _save(fig: plt.Figure, name: str) -> None:
    path = OUT / name
    fig.savefig(path, dpi=DPI, facecolor="white", edgecolor="none")
    plt.close(fig)


def _annotate_bars(ax, bars, values, y_max: float, fmt=None, inside_min: float = 55):
    """Place value labels above or inside bars without clipping."""
    fmt = fmt or (lambda v: f"{v:.0f}%")
    for bar, v in zip(bars, values):
        x = bar.get_x() + bar.get_width() / 2
        h = bar.get_height()
        if h >= inside_min:
            ax.text(x, h - y_max * 0.06, fmt(v), ha="center", va="top",
                    fontsize=9, fontweight="600", color="white")
        else:
            ax.text(x, h + y_max * 0.03, fmt(v), ha="center", va="bottom",
                    fontsize=9, fontweight="600", color=C["dark"])


def _annotate_bars_frac(ax, bars, values, y_max: float = 1.0):
    for bar, v in zip(bars, values):
        x = bar.get_x() + bar.get_width() / 2
        h = bar.get_height()
        ax.text(x, h + y_max * 0.04, f"{v:.2f}", ha="center", va="bottom",
                fontsize=9, fontweight="600", color=C["dark"])


def _panel_label(ax, letter: str):
    ax.text(-0.12, 1.06, letter, transform=ax.transAxes, fontsize=12,
            fontweight="700", color=C["dark"], va="top", ha="left")


def _format_messy_label(key: str) -> str:
    return {
        "clean": "Clean",
        "typical": "Typical",
        "minimal": "Minimal",
        "contradictory": "Contradictory",
        "incomplete_encoding": "Incomplete\nencoding",
    }.get(key, key.replace("_", " ").title())


# ── Figures ───────────────────────────────────────────────────────────────────


def fig_eval_two_layer():
    cohort = _load_cohort()
    ado_pct = round(cohort.get("ado_decision_accuracy", 0.47) * 100)
    blind_pct = round(cohort.get("condition_blind_accuracy", 0.45) * 100)
    cb_pct = round(cohort.get("checkbox_accuracy", 0.19) * 100)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), constrained_layout=True)

    ax = axes[0]
    _panel_label(ax, "a")
    cats = ["Development", "Held-out", "Ablation"]
    vals = [100, 100, 69]
    colors = [C["primary"], C["neutral"], C["secondary"]]
    x = np.arange(len(cats))
    bars = ax.bar(x, vals, color=colors, width=0.58, edgecolor="white", linewidth=1.2, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{c}\n(n={n})" for c, n in zip(cats, [16, 10, 16])])
    ax.set_ylim(0, 118)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Curated vignettes (single patient)")
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color=C["grid"], zorder=0)
    ax.set_axisbelow(True)
    _annotate_bars(ax, bars, vals, 118)

    ax = axes[1]
    _panel_label(ax, "b")
    cats = ["ADO", "Condition-blind", "Flat checkbox"]
    vals = [ado_pct, blind_pct, cb_pct]
    colors = [C["primary"], C["secondary"], C["muted"]]
    bars = ax.bar(np.arange(3), vals, color=colors, width=0.58, edgecolor="white", linewidth=1.2, zorder=3)
    ax.set_xticks(range(3))
    ax.set_xticklabels(cats)
    ax.set_ylim(0, 118)
    ax.set_ylabel("Agreement with reference oracle (%)")
    ax.set_title("Cohort stress test (520 cells)")
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color=C["grid"], zorder=0)
    ax.set_axisbelow(True)
    _annotate_bars(ax, bars, vals, 118)

    _save(fig, "eval_two_layer.png")
    CAPTIONS["eval_two_layer.png"] = (
        "**Two-layer validation.** (a) Curated vignettes on one encoded patient: "
        "16/16 development and 10/10 held-out accuracy (spec test); condition-blind "
        "ablation drops to 69% (11/16), showing activation logic is essential. "
        "(b) Cohort stress test across 20 template-inspired profiles and 12 clinical "
        f"scenarios (520 query cells): ADO agrees with an independent simplified oracle "
        f"on ~{ado_pct}% of decisions—far below vignette scores, reflecting messy real-world "
        "encoding and granularity gaps, not a deployment-ready error rate."
    )


def fig_eval_overview():
    cohort = _load_cohort()
    cohort_pct = round(cohort.get("ado_decision_accuracy", 0.47) * 100)

    fig, ax = plt.subplots(figsize=(8, 4), constrained_layout=True)
    labels = ["Vignette\ndev", "Ablation", "Cohort", "POLST\nfields"]
    values = [100, 69, cohort_pct, 97]
    colors = [C["primary"], C["secondary"], C["neutral"], C["tertiary"]]
    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=colors, width=0.55, edgecolor="white", linewidth=1.2, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 118)
    ax.set_ylabel("Agreement / accuracy (%)")
    ax.set_title("Headline evaluation metrics")
    ax.axhline(50, color=C["grid"], linestyle="--", linewidth=0.8, zorder=0)
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color=C["grid"], zorder=0)
    ax.set_axisbelow(True)
    _annotate_bars(ax, bars, values, 118)
    _save(fig, "eval_overview.png")
    CAPTIONS["eval_overview.png"] = (
        "**Summary metrics** across evaluation tracks: perfect vignette development accuracy "
        f"contrasts with {cohort_pct}% cohort agreement; 69% under condition-blind ablation; "
        "97% field agreement mapping 12 directive profiles to hospital code status and POLST "
        "(35/36 fields)."
    )


def fig_cohort_messy():
    cohort = _load_cohort()
    by = cohort.get("by_messy_level", {})
    order = ["clean", "typical", "minimal", "contradictory", "incomplete_encoding"]
    levels = [k for k in order if k in by] or list(by.keys())
    ado = [by[l]["ado_decision_pct"] for l in levels]
    blind = [by[l]["blind_pct"] for l in levels]

    fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True)
    x = np.arange(len(levels))
    w = 0.34
    ax.bar(x - w / 2, ado, w, label="ADO (full reasoner)", color=C["primary"],
           edgecolor="white", linewidth=1.2, zorder=3)
    ax.bar(x + w / 2, blind, w, label="Condition-blind", color=C["secondary"],
           edgecolor="white", linewidth=1.2, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels([_format_messy_label(l) for l in levels])
    ax.set_ylabel("Decision agreement (%)")
    ax.set_ylim(0, 78)
    ax.set_title("Cohort accuracy by directive data-quality tag")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2)
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color=C["grid"], zorder=0)
    ax.set_axisbelow(True)
    _save(fig, "cohort_messy_breakdown.png")
    CAPTIONS["cohort_messy_breakdown.png"] = (
        "**Cohort performance stratified by messiness.** Profiles tagged clean (well-structured "
        "encoding) score highest; minimal, contradictory, and incomplete-encoding profiles "
        "show lower agreement with the reference oracle—highlighting sensitivity to chart "
        "abstraction quality and template ambiguity."
    )


def fig_cohort_baselines():
    cohort = _load_cohort()
    n = cohort.get("n_cells", 520)
    overconf = cohort.get("checkbox_overconfident_cells", 421)
    ado = round(cohort.get("ado_decision_accuracy", 0.47) * 100)
    cb = round(cohort.get("checkbox_accuracy", 0.19) * 100)
    pct_over = round(overconf / n * 100)

    fig, axes = plt.subplots(2, 1, figsize=(8, 6.2), gridspec_kw={"height_ratios": [1.2, 1]},
                             constrained_layout=True)

    ax = axes[0]
    _panel_label(ax, "a")
    labels = ["ADO", "Checkbox\n(full code default)", "Checkbox\n(blank if silent)"]
    vals = [ado, cb, round(cohort.get("checkbox_blank_accuracy", 0.86) * 100)]
    colors = [C["primary"], C["muted"], C["neutral"]]
    bars = ax.bar(np.arange(3), vals, color=colors, width=0.5, edgecolor="white", linewidth=1.2, zorder=3)
    ax.set_xticks(range(3))
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Agreement with oracle (%)")
    ax.set_title("Baseline comparison (520 cells)")
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color=C["grid"], zorder=0)
    ax.set_axisbelow(True)
    _annotate_bars(ax, bars, vals, 105)

    ax = axes[1]
    _panel_label(ax, "b")
    ax.barh([0], [pct_over], color=C["secondary"], height=0.45, edgecolor="white", zorder=3)
    ax.set_yticks([0])
    ax.set_yticklabels(["Checkbox overconfident"])
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of cohort cells (%)")
    ax.set_title("Nuanced gold collapsed to flat yes/no")
    ax.text(pct_over + 1.5, 0, f"{overconf}/{n} cells ({pct_over}%)",
            va="center", fontsize=10, fontweight="600", color=C["dark"])
    ax.xaxis.grid(True, linestyle="-", linewidth=0.6, color=C["grid"], zorder=0)
    ax.set_axisbelow(True)

    _save(fig, "cohort_baseline_comparison.png")
    CAPTIONS["cohort_baseline_comparison.png"] = (
        f"**(a)** Agreement with the simplified reference oracle: ADO ({ado}%) versus flat "
        f"checkbox heuristics. **(b)** In {overconf} of {n} cells ({pct_over}%), the reference "
        "expects partial, vague, or no-coverage answers but a checkbox forces a definitive "
        "yes/no—illustrating ADO's value in preserving epistemic honesty."
    )


def fig_eval_dashboard():
    cohort = _load_cohort()
    cohort_pct = round(cohort.get("ado_decision_accuracy", 0.47) * 100)

    fig = plt.figure(figsize=(12, 7.5))
    gs = fig.add_gridspec(2, 3, hspace=0.42, wspace=0.35, left=0.07, right=0.98, top=0.94, bottom=0.08)

    def mini_bar(ax, labels, vals, colors, ylabel, title, ylim_top, fmt_pct=True):
        x = np.arange(len(labels))
        bars = ax.bar(x, vals, color=colors, width=0.55, edgecolor="white", linewidth=1, zorder=3)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylim(0, ylim_top)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_title(title, fontsize=10, pad=8)
        ax.yaxis.grid(True, linestyle="-", linewidth=0.5, color=C["grid"], zorder=0)
        ax.set_axisbelow(True)
        for bar, v in zip(bars, vals):
            label = f"{v:.0f}%" if fmt_pct else str(v)
            h = bar.get_height()
            yoff = ylim_top * 0.04
            ax.text(bar.get_x() + bar.get_width() / 2, h + yoff, label,
                    ha="center", va="bottom", fontsize=8, fontweight="600")

    mini_bar(fig.add_subplot(gs[0, 0]), ["Dev", "Hold"], [100, 100],
             [C["primary"], C["neutral"]], "%", "Vignettes", 115)
    mini_bar(fig.add_subplot(gs[0, 1]), ["Full", "Blind"], [100, 69],
             [C["primary"], C["secondary"]], "%", "Ablation", 115)
    mini_bar(fig.add_subplot(gs[0, 2]), ["Cohort"], [cohort_pct],
             [C["neutral"]], "%", "Stress test", 115)

    ax = fig.add_subplot(gs[1, 0])
    labels = ["Full", "Vague", "Part.", "Who", "OWL", "OOS"]
    counts = [14, 3, 3, 3, 1, 6]
    colors = [C["primary"], C["neutral"], C["tertiary"], C["secondary"], C["accent"], C["muted"]]
    x = np.arange(len(labels))
    ax.bar(x, counts, color=colors, width=0.65, edgecolor="white", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Clauses", fontsize=9)
    ax.set_title("Coverage (n=30)", fontsize=10, pad=8)
    ax.yaxis.grid(True, linestyle="-", linewidth=0.5, color=C["grid"], zorder=0)
    ax.set_axisbelow(True)
    for i, c in enumerate(counts):
        ax.text(i, c + 0.35, str(c), ha="center", fontsize=8, fontweight="600")

    ax = fig.add_subplot(gs[1, 1])
    bars = ax.bar([0, 1, 2], [0.94, 1.0, 0.97], color=C["primary"], width=0.5, edgecolor="white", zorder=3)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["P", "R", "F1"], fontsize=9)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Score", fontsize=9)
    ax.set_title("Extraction (n=12)", fontsize=10, pad=8)
    _annotate_bars_frac(ax, bars, [0.94, 1.0, 0.97], 1.12)

    ax = fig.add_subplot(gs[1, 2])
    fields = ["Code", "A", "B", "All"]
    correct = [12, 12, 11, 11]
    x = np.arange(4)
    bars = ax.bar(x, [c / 12 * 100 for c in correct], color=C["primary"], width=0.55, edgecolor="white", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(fields, fontsize=9)
    ax.set_ylim(0, 115)
    ax.set_ylabel("%", fontsize=9)
    ax.set_title("POLST mapping (n=12)", fontsize=10, pad=8)
    ax.yaxis.grid(True, linestyle="-", linewidth=0.5, color=C["grid"], zorder=0)
    ax.set_axisbelow(True)
    for bar, c in zip(bars, correct):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
                f"{c}/12", ha="center", fontsize=8, fontweight="600")

    _save(fig, "eval_dashboard.png")
    CAPTIONS["eval_dashboard.png"] = (
        "**Evaluation dashboard** (developmental validation, Spring 2026): vignette splits, "
        f"ablation, cohort stress ({cohort_pct}%), inventory coverage (47% fully representable), "
        "LLM extraction F1 0.97, and POLST/code-status field agreement (35/36)."
    )


def fig_study_design():
    fig, ax = plt.subplots(figsize=(10, 5.2), constrained_layout=True)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    strands = [
        (1.2, 4.6, "Vignettes", "16 dev + 10 held-out"),
        (5.0, 4.6, "Ablation", "69% if blind"),
        (8.2, 4.6, "Cohort", "520 cells"),
        (1.2, 1.6, "Extraction", "n=12, F1 0.97"),
        (5.0, 1.6, "Code / POLST", "35/36 fields"),
        (8.2, 1.6, "Coverage", "47% full"),
    ]
    for x, y, title, sub in strands:
        face = C["fill_a"] if title == "Cohort" else "#F4F6F8"
        rect = mpatches.FancyBboxPatch(
            (x - 1.05, y - 0.72), 2.1, 1.35,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor=face, edgecolor=C["primary"], linewidth=1.2,
        )
        ax.add_patch(rect)
        ax.text(x, y + 0.22, title, ha="center", fontweight="700", fontsize=11, color=C["primary"])
        ax.text(x, y - 0.28, sub, ha="center", fontsize=9, color=C["muted"])

    ax.text(5.0, 3.05, "Developmental validation (not a clinical trial)",
            ha="center", fontsize=10, fontstyle="italic", color=C["secondary"])

    _save(fig, "study_design_strands.png")
    CAPTIONS["study_design_strands.png"] = (
        "**Evaluation design:** six complementary strands—curated vignettes, condition-blind "
        "ablation, large cohort simulation, LLM extraction on real template language, "
        "POLST-semantics mapping, and systematic inventory coverage analysis."
    )


def fig_track3_fields():
    fields = ["Code status", "POLST A", "POLST B", "Exact profile"]
    correct = [12, 12, 11, 11]
    n = 12

    fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
    x = np.arange(len(fields))
    heights = [c / n * 100 for c in correct]
    bars = ax.bar(x, heights, color=C["primary"], width=0.52, edgecolor="white", linewidth=1.2, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(fields)
    ax.set_ylim(0, 115)
    ax.set_ylabel(f"Agreement (of {n} profiles, %)")
    ax.set_title("Directive profiles mapped to bedside orders")
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color=C["grid"], zorder=0)
    ax.set_axisbelow(True)
    for bar, c in zip(bars, correct):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
                f"{c}/{n}", ha="center", fontsize=9, fontweight="600")
    _save(fig, "track3_field_agreement.png")
    CAPTIONS["track3_field_agreement.png"] = (
        "**Track 3:** Agreement between ADO-derived hospital code status and POLST sections "
        "versus gold labels from published POLST semantics (12 inventory-grounded profiles). "
        "One principled divergence on profile P5 (POLST B not specified vs default full treatment)."
    )


def fig_confusion_matrix():
    short = ["Full", "DNR", "DNI", "DNR/DNI", "DNE", "DNR/DNI+DNE"]
    matrix = np.array([
        [4, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 2, 0, 0],
        [0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 2],
    ])

    fig, ax = plt.subplots(figsize=(7.8, 6.2), constrained_layout=True)
    cmap = mpl.colors.LinearSegmentedColormap.from_list("ado_blues", ["#FFFFFF", C["primary"]])
    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=4, aspect="equal")
    ax.set_xticks(range(6))
    ax.set_yticks(range(6))
    ax.set_xticklabels(short, fontsize=9, rotation=35, ha="right")
    ax.set_yticklabels(short, fontsize=9)
    ax.set_xlabel("ADO derived code status", labelpad=10)
    ax.set_ylabel("Gold (POLST semantics)", labelpad=10)
    ax.set_title("Code-status confusion matrix")
    for i in range(6):
        for j in range(6):
            if matrix[i, j] > 0:
                ax.text(j, i, int(matrix[i, j]), ha="center", va="center",
                        fontsize=11, fontweight="600",
                        color="white" if matrix[i, j] >= 2 else C["primary"])
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, shrink=0.85)
    cbar.set_label("Profile count", fontsize=9)
    cbar.ax.tick_params(labelsize=8)
    _save(fig, "code_status_confusion.png")
    CAPTIONS["code_status_confusion.png"] = (
        "**Code-status confusion matrix** (n=12 profiles): perfect diagonal agreement—no "
        "profile-level misclassification across six observed code-status categories."
    )


def fig_ablation():
    fig, ax = plt.subplots(figsize=(6.5, 4.5), constrained_layout=True)
    labels = ["Full reasoner", "Condition-blind"]
    acc = [100, 69]
    x = np.arange(2)
    bars = ax.bar(x, acc, color=[C["primary"], C["secondary"]], width=0.48,
                  edgecolor="white", linewidth=1.2, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 118)
    ax.set_ylabel("Vignette accuracy (%)")
    ax.set_title("Effect of ignoring activation conditions")
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color=C["grid"], zorder=0)
    ax.set_axisbelow(True)
    _annotate_bars(ax, bars, acc, 118)
    _save(fig, "ablation_conditions.png")
    CAPTIONS["ablation_conditions.png"] = (
        "**Ablation:** Re-scoring the same 16 development vignettes while treating every matched "
        "preference as unconditionally applicable drops accuracy from 100% to 69% (11/16)—"
        "failures align with partial, vague, and conditional cases."
    )


def fig_vignette_outputs():
    types = ["Clear", "Partial", "No coverage", "Vague"]
    counts = [9, 4, 2, 1]
    colors = [C["primary"], C["neutral"], C["tertiary"], C["accent"]]

    fig, ax = plt.subplots(figsize=(6.5, 4.5), constrained_layout=True)
    wedges, _, autotexts = ax.pie(
        counts, colors=colors, startangle=90, autopct="%1.0f%%",
        pctdistance=0.72, wedgeprops=dict(edgecolor="white", linewidth=1.5, width=0.55),
        textprops={"fontsize": 9, "fontweight": "600", "color": C["dark"]},
    )
    ax.legend(wedges, [f"{t} (n={c})" for t, c in zip(types, counts)],
              loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=9)
    ax.set_title("Expected match-type distribution (16 vignettes)")
    _save(fig, "vignette_match_types.png")
    CAPTIONS["vignette_match_types.png"] = (
        "**Vignette suite composition:** Most gold labels expect clear or partial matches; "
        "the suite deliberately includes no-coverage and vague cases to test honest non-answers."
    )


def fig_conditional_flip():
    fig, ax = plt.subplots(figsize=(8, 3.8), constrained_layout=True)
    scenarios = ["Condition met", "Condition not met"]
    codes = ["DNR", "Full code"]
    y = np.arange(2)
    bars = ax.barh(y, [1, 1], color=[C["secondary"], C["primary"]], height=0.5,
                   edgecolor="white", linewidth=1.2, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([
        "NYHA IV, no reversible cause",
        "NYHA III, reversible cause present",
    ], fontsize=9)
    ax.set_xlim(0, 1.35)
    ax.set_xticks([])
    ax.set_title('Same directive: "No CPR if NYHA IV and no reversible cause"')
    for bar, code in zip(bars, codes):
        ax.text(0.5, bar.get_y() + bar.get_height() / 2, code,
                ha="center", va="center", fontsize=13, fontweight="700", color="white")
    _save(fig, "conditional_p9_p10.png")
    CAPTIONS["conditional_p9_p10.png"] = (
        "**Conditional value-add (profiles P9 vs P10):** Identical preference text yields "
        "DNR when activation conditions are met versus full code when they are not—logic "
        "a flat POLST checkbox cannot represent."
    )


def fig_vignette_splits():
    fig, ax = plt.subplots(figsize=(6, 4.5), constrained_layout=True)
    labels = ["Development", "Held-out"]
    vals = [100, 100]
    x = np.arange(2)
    bars = ax.bar(x, vals, color=[C["primary"], C["neutral"]], width=0.45,
                  edgecolor="white", linewidth=1.2, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{l}\n(n={n})" for l, n in zip(labels, [16, 10])])
    ax.set_ylim(0, 118)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Vignette splits (Jane Doe ontology)")
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color=C["grid"], zorder=0)
    ax.set_axisbelow(True)
    _annotate_bars(ax, bars, vals, 118)
    _save(fig, "vignette_splits.png")
    CAPTIONS["vignette_splits.png"] = (
        "**Vignette splits:** 100% decision and match-type accuracy on both development (n=16) "
        "and held-out (n=10) sets using the same encoded patient—developmental spec test, not "
        "multi-patient generalization."
    )


def fig_coverage():
    labels = ["Fully\nrepresentable", "Vague", "Partial\nloss", "Who\ndecides", "OWL\ngap", "Out of\nscope"]
    counts = [14, 3, 3, 3, 1, 6]
    colors = [C["primary"], C["neutral"], C["tertiary"], C["secondary"], C["accent"], C["muted"]]

    fig, ax = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
    x = np.arange(len(labels))
    bars = ax.bar(x, counts, color=colors, width=0.62, edgecolor="white", linewidth=1.2, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Clauses (of 30 sampled)")
    ax.set_title("Advance directive inventory coverage")
    ax.set_ylim(0, max(counts) + 2.5)
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color=C["grid"], zorder=0)
    ax.set_axisbelow(True)
    for bar, c in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.25,
                str(c), ha="center", fontsize=9, fontweight="600")
    _save(fig, "coverage_inventory.png")
    CAPTIONS["coverage_inventory.png"] = (
        "**Coverage analysis** of 30 stratified clauses from a 50-template inventory: 14 (47%) "
        "fully representable in the HF-focused ontology; six out of scope (e.g., nutrition, "
        "antibiotics); gaps include surrogate-override and time-limited trials."
    )


def fig_extraction_metrics():
    fig, ax = plt.subplots(figsize=(6.5, 4.5), constrained_layout=True)
    metrics = ["Precision", "Recall", "F1"]
    vals = [0.94, 1.00, 0.97]
    x = np.arange(3)
    bars = ax.bar(x, vals, color=C["primary"], width=0.5, edgecolor="white", linewidth=1.2, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Score")
    ax.set_title("LLM preference extraction (n=12 clauses)")
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color=C["grid"], zorder=0)
    ax.set_axisbelow(True)
    _annotate_bars_frac(ax, bars, vals, 1.15)
    _save(fig, "extraction_f1.png")
    CAPTIONS["extraction_f1.png"] = (
        "**Track 2 extraction** on 12 verbatim clauses from real template families: F1 0.97 with "
        "zero hallucinated preferences on out-of-scope artificial nutrition and antibiotics "
        "statements (closed-world discipline)."
    )


def write_captions_md():
    lines = [
        "# Figure captions for ADO presentation",
        "",
        "Copy each caption below the corresponding figure on your slide, or into the speaker notes.",
        "Figures are in `docs/presentation_figures/` at **300 DPI**.",
        "",
        "---",
        "",
    ]
    order = [
        "eval_two_layer.png",
        "eval_overview.png",
        "study_design_strands.png",
        "ablation_conditions.png",
        "conditional_p9_p10.png",
        "cohort_messy_breakdown.png",
        "cohort_baseline_comparison.png",
        "eval_dashboard.png",
        "vignette_splits.png",
        "vignette_match_types.png",
        "coverage_inventory.png",
        "extraction_f1.png",
        "track3_field_agreement.png",
        "code_status_confusion.png",
    ]
    for i, name in enumerate(order, 1):
        cap = CAPTIONS.get(name, "")
        title = name.replace("_", " ").replace(".png", "").title()
        lines.append(f"## Figure {i}. `{name}`")
        lines.append("")
        lines.append(cap)
        lines.append("")
        lines.append("---")
        lines.append("")

  # Short slide captions (one line)
    lines.append("## One-line slide captions (bullets)")
    lines.append("")
    for name in order:
        cap = CAPTIONS.get(name, "")
        short = cap.split(".")[0].replace("**", "") + "." if cap else ""
        lines.append(f"- **{name}:** {short}")
        lines.append("")

    CAPTIONS_MD.write_text("\n".join(lines), encoding="utf-8")
    (OUT / "figure_captions.json").write_text(json.dumps(CAPTIONS, indent=2), encoding="utf-8")


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
    write_captions_md()
    print(f"Wrote {len(list(OUT.glob('*.png')))} figures + {CAPTIONS_MD.name} at {DPI} DPI")


if __name__ == "__main__":
    main()
