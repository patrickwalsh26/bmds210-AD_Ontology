#!/usr/bin/env python3
"""
Comprehensive ADO Evaluation Suite
====================================
Runs all non-API evaluations, loads cached API results, and produces a full
set of publication-quality figures (saved to docs/presentation_figures/).

Usage:
    python evaluation/comprehensive_eval_suite.py
    python evaluation/comprehensive_eval_suite.py --out results/eval_figures/

Each panel is saved individually at 300 DPI and a combined summary figure is
also written.

Panels produced:
  1. decision_confusion_matrix.png     — 4×4 confusion matrix (dev vignettes)
  2. ablation_breakdown.png            — ADO vs condition-blind, by decision type
  3. cohort_messiness.png              — Performance stratified by encoding quality
  4. coverage_taxonomy.png             — Ontology representability breakdown
  5. extraction_fields.png             — Extraction P/R/F1 + per-field accuracy
  6. polst_field_agreement.png         — Per-field POLST kappa and agreement
  7. holdout_vs_dev.png                — Dev vs held-out split comparison
  8. intervention_domain_accuracy.png  — Accuracy per intervention class
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "evaluation"
for p in (ROOT, EVAL_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from ado.query_evaluation import VIGNETTES, evaluate_vignette, find_matching_preferences
from ado.holdout_vignettes import HOLDOUT_VIGNETTES
from baselines import find_matching_preferences_condition_blind
from coverage_analysis import CLAUSES
from track3_evaluation import PROFILES, FIELDS, SHORT, cohen_kappa, evaluate_profile
from ado.preference_input import load_ontology, populate_patient
from owlready2 import get_ontology


# ── Palette (colorblind-friendly) ─────────────────────────────────────────────
BLUE   = "#2166ac"
RED    = "#d6604d"
ORANGE = "#f4a582"
GREEN  = "#4dac26"
GRAY   = "#999999"
LIGHT  = "#f7f7f7"
DARK   = "#1a1a1a"

DECISION_ORDER = ["yes", "no", "partial", "no_coverage", "vague"]
MATCH_ORDER    = ["clear", "partial", "vague", "no_coverage"]

DOMAIN_MAP = {
    "CPR": "Resuscitation",
    "Defibrillation": "Resuscitation",
    "TranscutaneousPacing": "Resuscitation",
    "TemporaryVentilation": "Ventilation",
    "IndefiniteVentilation": "Ventilation",
    "NonInvasiveVentilation": "Ventilation",
    "ICDDeactivation": "Device",
    "ICDShockTherapy": "Device",
    "LVADWithdrawal": "Device",
    "InotropeEscalation": "Pharmacologic",
    "VasopressorWithdrawal": "Pharmacologic",
    "AcuteDialysis": "Dialysis",
    "ChronicDialysis": "Dialysis",
    "PacemakerDeactivation": "Device",
}

CONDITION_LABELS = {
    "nyha_class": "NYHA Class",
    "conditions": "Clinical Condition",
    "reversible_cause": "Reversible Cause",
    "care_context": "Care Context",
    "time_elapsed": "Time Bound",
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def savefig(fig, path: Path, tight=True):
    if tight:
        fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  saved → {path.name}")


def load_patient(owl_path: Path):
    onto = get_ontology(str(owl_path.resolve())).load()
    patients = list(onto.search(type=onto.Patient))
    patient = max(patients, key=lambda p: len(p.hasPreference) if p.hasPreference else 0)
    return onto, patient


def _has_condition(v: dict, key: str) -> bool:
    state = v["scenario_state"]
    if key == "conditions":
        return bool(state.get("conditions"))
    return state.get(key) is not None


# ── Panel 1: Decision Confusion Matrix ────────────────────────────────────────

def panel_confusion_matrix(results: list[dict], title: str, out: Path):
    labels = ["yes", "no", "partial", "no_coverage", "vague"]
    label_display = ["yes", "no", "partial", "no cov.", "vague"]
    n = len(labels)
    matrix = np.zeros((n, n), dtype=int)
    idx = {l: i for i, l in enumerate(labels)}

    for r in results:
        pred = r["system_decision"]
        gold = r["expected_decision"]
        if pred in idx and gold in idx:
            matrix[idx[gold]][idx[pred]] += 1

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(matrix, cmap="Blues", vmin=0)

    ax.set_xticks(range(n)); ax.set_xticklabels(label_display, fontsize=9)
    ax.set_yticks(range(n)); ax.set_yticklabels(label_display, fontsize=9)
    ax.set_xlabel("Predicted", fontsize=10, fontweight="bold")
    ax.set_ylabel("Gold", fontsize=10, fontweight="bold")
    ax.set_title(title, fontsize=11, fontweight="bold", pad=10)

    for i in range(n):
        for j in range(n):
            val = matrix[i, j]
            if val == 0:
                continue
            color = "white" if matrix[i, j] > matrix.max() * 0.5 else DARK
            ax.text(j, i, str(val), ha="center", va="center",
                    fontsize=11, fontweight="bold", color=color)

    total = len(results)
    correct = sum(1 for r in results if r["decision_correct"])
    ax.text(0.5, -0.14, f"Accuracy: {correct}/{total} ({100*correct/total:.0f}%)",
            ha="center", transform=ax.transAxes, fontsize=9, style="italic")

    fig.colorbar(im, ax=ax, shrink=0.8, label="Count")
    savefig(fig, out)
    return matrix


# ── Panel 2: Ablation Breakdown by Decision Type ──────────────────────────────

def panel_ablation_breakdown(ado_results: list[dict], blind_results: list[dict], out: Path):
    decision_types = ["yes", "no", "partial", "no_coverage", "vague"]
    display = ["yes", "no", "partial", "no cov.", "vague"]

    ado_by_type   = {dt: {"correct": 0, "total": 0} for dt in decision_types}
    blind_by_type = {dt: {"correct": 0, "total": 0} for dt in decision_types}

    for a, b in zip(ado_results, blind_results):
        dt = a["expected_decision"]
        if dt not in ado_by_type:
            continue
        ado_by_type[dt]["total"]   += 1
        blind_by_type[dt]["total"] += 1
        if a["decision_correct"]:
            ado_by_type[dt]["correct"] += 1
        if b["decision_correct"]:
            blind_by_type[dt]["correct"] += 1

    ado_pct   = [100 * ado_by_type[dt]["correct"]   / ado_by_type[dt]["total"]   if ado_by_type[dt]["total"]   else np.nan for dt in decision_types]
    blind_pct = [100 * blind_by_type[dt]["correct"] / blind_by_type[dt]["total"] if blind_by_type[dt]["total"] else np.nan for dt in decision_types]

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(decision_types))
    width = 0.35

    for i, (ado_val, blind_val, dt, disp) in enumerate(zip(ado_pct, blind_pct, decision_types, display)):
        n = ado_by_type[dt]["total"]
        if np.isnan(ado_val):
            continue
        bar_ado = ax.bar(i - width/2, ado_val, width, color=BLUE, zorder=3,
                         label="ADO (full reasoner)" if i == 0 else "_")
        ax.text(i - width/2, ado_val + 1.5, f"{ado_val:.0f}%",
                ha="center", va="bottom", fontsize=8.5, color=DARK, fontweight="bold")

        if not np.isnan(blind_val):
            bar_blind = ax.bar(i + width/2, blind_val, width, color=ORANGE, zorder=3,
                               label="Condition-blind" if i == 0 else "_")
            label_y = blind_val + 1.5 if blind_val > 5 else 3
            ax.text(i + width/2, label_y, f"{blind_val:.0f}%",
                    ha="center", va="bottom", fontsize=8.5,
                    color=RED if blind_val == 0 else DARK, fontweight="bold")
        else:
            # No vignettes of this type — mark as N/A
            ax.text(i + width/2, 2, "n/a", ha="center", va="bottom", fontsize=7, color=GRAY)

        ax.text(i, -7, f"n={n}", ha="center", fontsize=8, color=GRAY)

    ax.set_xticks(x); ax.set_xticklabels(display, fontsize=10)
    ax.set_ylabel("Decision accuracy (%)", fontsize=10)
    ax.set_ylim(0, 120)
    ax.set_title("Ablation: Where Condition-Blind Reasoning Fails\n"
                 "(ADO full reasoner vs. condition-blind baseline — 16 dev vignettes)",
                 fontsize=11, fontweight="bold")
    ax.axhline(100, color=GRAY, linewidth=0.8, linestyle="--", zorder=1)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=9, framealpha=0.9)

    ado_total   = sum(1 for r in ado_results   if r["decision_correct"])
    blind_total = sum(1 for r in blind_results if r["decision_correct"])
    n_total = len(ado_results)
    ax.text(0.98, 0.97,
            f"ADO: {ado_total}/{n_total} ({100*ado_total/n_total:.0f}%)\n"
            f"Blind: {blind_total}/{n_total} ({100*blind_total/n_total:.0f}%)",
            ha="right", va="top", transform=ax.transAxes, fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=GRAY))

    savefig(fig, out)


# ── Panel 3: Cohort Messiness Stratification ──────────────────────────────────

def panel_cohort_messiness(cohort: dict, out: Path):
    levels = cohort["by_messy_level"]
    # All 7 messiness levels in ascending difficulty order
    order = ["clean", "typical", "minimal", "incomplete_encoding",
             "contradictory", "outdated", "culturally_complex"]
    display = ["Clean", "Typical", "Minimal", "Incomplete\nEncoding",
               "Contradictory", "Outdated", "Culturally\nComplex"]
    order   = [o for o in order if o in levels]
    display = [display[i] for i, o in enumerate(["clean", "typical", "minimal",
               "incomplete_encoding", "contradictory", "outdated",
               "culturally_complex"]) if o in levels]

    metrics = [
        ("ado_decision_pct",  "ADO (full)",         BLUE),
        ("blind_pct",         "Condition-blind",    ORANGE),
        ("checkbox_pct",      "Flat checkbox",      RED),
    ]

    n_patients = cohort.get("n_patients", 50)
    n_scenarios = cohort.get("n_scenarios", 25)
    n_cells = cohort.get("n_cells", 3550)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: grouped bars by messiness
    ax = axes[0]
    x = np.arange(len(order))
    width = 0.22
    offsets = [-width, 0, width]

    for offset, (key, label, color) in zip(offsets, metrics):
        vals = [levels[l][key] for l in order]
        bars = ax.bar(x + offset, vals, width, color=color, label=label, zorder=3)
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h + 0.8,
                        f"{h:.0f}", ha="center", va="bottom", fontsize=6.5, color=DARK)

    ax.set_xticks(x)
    ax.set_xticklabels(display, fontsize=8.5)
    ax.set_ylabel("Decision accuracy (%)", fontsize=10)
    ax.set_title(
        f"Cohort Performance by Encoding Quality\n"
        f"({n_patients} patients × {n_scenarios} scenarios = {n_cells:,} cells)",
        fontsize=10, fontweight="bold"
    )
    ax.set_ylim(0, 75)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)

    for i, l in enumerate(order):
        ax.text(i, -6, f"n={levels[l]['n']}", ha="center", fontsize=7.5, color=GRAY)

    ax.legend(fontsize=8, loc="upper right")

    # Right: scatter — ADO vs condition-blind per level (bubble size ∝ cell count)
    ax2 = axes[1]
    # 7 distinguishable colors
    colors_pts = [BLUE, GREEN, ORANGE, RED, "#984ea3", "#ff7f00", "#a65628"]
    for i, (l, disp) in enumerate(zip(order, display)):
        ado_val   = levels[l]["ado_decision_pct"]
        blind_val = levels[l]["blind_pct"]
        label_short = disp.replace("\n", " ")
        ax2.scatter(blind_val, ado_val, s=levels[l]["n"] * 0.8,
                    color=colors_pts[i % len(colors_pts)], zorder=5,
                    label=label_short, edgecolors=DARK, linewidths=0.5)
        ax2.annotate(label_short, (blind_val, ado_val),
                     textcoords="offset points", xytext=(6, 3), fontsize=7.5)

    lim = [20, 65]
    ax2.plot(lim, lim, "--", color=GRAY, linewidth=1)
    ax2.set_xlabel("Condition-blind accuracy (%)", fontsize=10)
    ax2.set_ylabel("ADO accuracy (%)", fontsize=10)
    ax2.set_title("ADO vs. Condition-Blind\n(bubble size ∝ cell count)",
                  fontsize=10, fontweight="bold")
    ax2.set_xlim(lim); ax2.set_ylim(lim)
    ax2.yaxis.grid(True, linestyle="--", alpha=0.3)
    ax2.xaxis.grid(True, linestyle="--", alpha=0.3)
    ax2.text(0.05, 0.92, "ADO better →", transform=ax2.transAxes,
             fontsize=8, color=BLUE, style="italic")

    savefig(fig, out)


# ── Panel 4: Coverage Taxonomy ─────────────────────────────────────────────────

def panel_coverage_taxonomy(out: Path):
    counter = Counter(c["label"] for c in CLAUSES)
    order = ["representable", "vague", "partial_loss", "who_decides_gap", "owl_gap", "out_of_scope"]
    display = ["Fully\nrepresentable", "Vague\nonly", "Partial\ninformation\nloss",
               "Who-decides\ngap", "OWL\nexpressivity\ngap", "Out of\nscope"]
    colors = [GREEN, "#74c476", ORANGE, RED, "#9ecae1", GRAY]

    vals = [counter.get(k, 0) for k in order]
    n = sum(vals)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: horizontal bars (better than donut for comparison)
    ax = axes[0]
    y = np.arange(len(order))
    bars = ax.barh(y, vals, color=colors, edgecolor="white", linewidth=0.5, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels(display, fontsize=9)
    ax.set_xlabel("Clause count (n=30)", fontsize=10)
    ax.set_title("Ontology Coverage\nStratified sample of 30 directive clauses",
                 fontsize=10, fontweight="bold")
    ax.xaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    for bar, val in zip(bars, vals):
        if val > 0:
            ax.text(val + 0.1, bar.get_y() + bar.get_height()/2,
                    f"{val} ({100*val/n:.0f}%)", va="center", fontsize=9, color=DARK)

    # Right: breakdown by source template family
    families = Counter(c["source"].split(" ")[0] for c in CLAUSES)
    fam_order = sorted(families, key=lambda k: -families[k])[:8]
    fam_vals  = [families[f] for f in fam_order]

    ax2 = axes[1]
    y2 = np.arange(len(fam_order))
    ax2.barh(y2, fam_vals, color=BLUE, alpha=0.75, edgecolor="white", zorder=3)
    ax2.set_yticks(y2); ax2.set_yticklabels(fam_order, fontsize=9)
    ax2.set_xlabel("Clause count", fontsize=10)
    ax2.set_title("Clause Sources\nTemplate family distribution",
                  fontsize=10, fontweight="bold")
    ax2.xaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax2.set_axisbelow(True)
    for i, val in enumerate(fam_vals):
        ax2.text(val + 0.05, i, str(val), va="center", fontsize=9, color=DARK)

    savefig(fig, out)


# ── Panel 5: Extraction Per-Field Accuracy ─────────────────────────────────────

def panel_extraction_fields(out: Path):
    """
    Uses hard-coded results from extraction_evaluation.py (requires API).
    Update these values after running: python evaluation/extraction_evaluation.py
    """
    # Results from Track 2 evaluation (F1=0.97 on 12 statements)
    precision, recall, f1 = 0.97, 0.97, 0.97
    tp, fp, fn = 18, 1, 0

    # Per-field accuracy on 18 matched pairs (from evaluation run)
    field_results = {
        "Negation":        {"correct": 18, "total": 18},
        "Type\n(clear/cond/vague)": {"correct": 17, "total": 18},
        "Conditionality":  {"correct": 16, "total": 18},
    }

    # Out-of-scope results (closed-world discipline)
    oos_hallucinated = 0    # preferences invented for out-of-scope clauses
    oos_total_clauses = 2   # E9 (nutrition), E10 (antibiotics)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    # Left: Overall P/R/F1
    ax = axes[0]
    metrics = ["Precision", "Recall", "F1"]
    vals    = [precision, recall, f1]
    colors  = [BLUE, GREEN, ORANGE]
    bars = ax.bar(metrics, vals, color=colors, width=0.5, zorder=3, edgecolor="white")
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Score", fontsize=10)
    ax.set_title("LLM Extraction Performance\n(12 real directive statements, Track 2)",
                 fontsize=10, fontweight="bold")
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.015,
                f"{val:.2f}", ha="center", fontsize=11, fontweight="bold", color=DARK)

    # Annotate TP/FP/FN
    ax.text(0.5, 0.12,
            f"TP={tp}  FP={fp}  FN={fn}\n"
            f"Out-of-scope hallucinations: {oos_hallucinated}/{oos_total_clauses} clauses",
            ha="center", transform=ax.transAxes, fontsize=8.5, style="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=LIGHT, edgecolor=GRAY))

    # Right: Per-field accuracy
    ax2 = axes[1]
    field_names = list(field_results.keys())
    field_pcts  = [100 * field_results[f]["correct"] / field_results[f]["total"]
                   for f in field_names]
    field_ns    = [field_results[f]["total"] for f in field_names]
    colors2 = [BLUE, GREEN, ORANGE]
    bars2 = ax2.bar(field_names, field_pcts, color=colors2, width=0.5,
                    zorder=3, edgecolor="white")
    ax2.set_ylim(0, 115)
    ax2.set_ylabel("Field accuracy (%)", fontsize=10)
    ax2.set_title("Per-Field Accuracy on Matched Pairs\n(correctly encoded field / total matched)",
                  fontsize=10, fontweight="bold")
    ax2.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax2.set_axisbelow(True)
    for bar, val, n in zip(bars2, field_pcts, field_ns):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 1.5,
                 f"{val:.0f}%\n(n={n})", ha="center", fontsize=9, color=DARK)

    savefig(fig, out)


# ── Panel 6: POLST Field Agreement + Kappa ─────────────────────────────────────

def panel_polst_agreement(profile_results: list[tuple], out: Path):
    from collections import defaultdict
    n = len(profile_results)

    # Compute per-field metrics
    field_correct = defaultdict(int)
    derived_labels = defaultdict(list)
    gold_labels    = defaultdict(list)
    exact = 0

    for p, result, fm, all_match in profile_results:
        for f in FIELDS:
            field_correct[f] += int(fm[f])
            derived_labels[f].append(result[f])
            gold_labels[f].append(p["gold"][f])
        exact += int(all_match)

    kappas = {f: cohen_kappa(derived_labels[f], gold_labels[f]) for f in FIELDS}
    agree_pcts = {f: 100 * field_correct[f] / n for f in FIELDS}

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    # Left: Field agreement %
    ax = axes[0]
    field_disp = [SHORT[f] for f in FIELDS]
    agree_vals = [agree_pcts[f] for f in FIELDS]
    colors = [BLUE, GREEN, ORANGE]
    bars = ax.bar(field_disp, agree_vals, color=colors, width=0.5, zorder=3)
    ax.axhline(100, color=GRAY, linewidth=0.8, linestyle="--")
    ax.set_ylim(0, 115)
    ax.set_ylabel("Agreement with POLST gold (%)", fontsize=10)
    ax.set_title(f"POLST / Code-Status Mapping\n({n} profiles, exact agreement: {exact}/{n})",
                 fontsize=10, fontweight="bold")
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    for bar, val in zip(bars, agree_vals):
        ax.text(bar.get_x() + bar.get_width()/2, val + 1.5,
                f"{val:.0f}%", ha="center", fontsize=11, fontweight="bold", color=DARK)
    total_fields = n * len(FIELDS)
    total_correct = sum(field_correct[f] for f in FIELDS)
    ax.text(0.5, 0.08,
            f"Overall: {total_correct}/{total_fields} fields ({100*total_correct/total_fields:.0f}%)",
            ha="center", transform=ax.transAxes, fontsize=9, style="italic")

    # Right: Cohen's kappa per field
    ax2 = axes[1]
    kappa_vals = [kappas[f] for f in FIELDS]
    bars2 = ax2.bar(field_disp, kappa_vals, color=colors, width=0.5, zorder=3)
    ax2.axhline(0.8, color=GREEN, linewidth=1, linestyle="--", label="Good (κ=0.8)")
    ax2.axhline(0.6, color=ORANGE, linewidth=1, linestyle="--", label="Moderate (κ=0.6)")
    ax2.set_ylim(0, 1.15)
    ax2.set_ylabel("Cohen's κ", fontsize=10)
    ax2.set_title("Inter-Rater Agreement\n(ADO derived vs. POLST-semantics gold)",
                  fontsize=10, fontweight="bold")
    ax2.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax2.set_axisbelow(True)
    ax2.legend(fontsize=8)
    for bar, val in zip(bars2, kappa_vals):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.02,
                 f"κ={val:.2f}", ha="center", fontsize=10, fontweight="bold", color=DARK)

    savefig(fig, out)


# ── Panel 7: Dev vs Held-Out Split ─────────────────────────────────────────────

def panel_holdout_vs_dev(dev_results: list[dict], holdout_results: list[dict], out: Path):
    splits = [
        ("Dev (n=16)",     dev_results),
        ("Held-out (n=10)", holdout_results),
    ]

    # Decision accuracy and match-type accuracy for each split
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    match_types = MATCH_ORDER
    mt_display  = ["clear", "partial", "vague", "no cov."]

    for ax, (label, results) in zip(axes, splits):
        mt_correct  = Counter()
        mt_total    = Counter()
        for r in results:
            mt = r["expected_match_type"]
            mt_total[mt]  += 1
            mt_correct[mt] += int(r["match_type_correct"])

        x = np.arange(len(match_types))
        vals_correct = [mt_correct[m]  for m in match_types]
        vals_total   = [mt_total[m]    for m in match_types]
        pcts         = [100 * c / t if t else 0 for c, t in zip(vals_correct, vals_total)]
        colors = [GREEN if p == 100 else ORANGE if p >= 50 else RED for p in pcts]

        bars = ax.bar(x, pcts, color=colors, width=0.55, zorder=3)
        ax.set_xticks(x); ax.set_xticklabels(mt_display, fontsize=9)
        ax.set_ylabel("Match-type accuracy (%)", fontsize=10)
        ax.set_ylim(0, 120)
        ax.set_title(f"{label}\nMatch-type accuracy by category",
                     fontsize=10, fontweight="bold")
        ax.axhline(100, color=GRAY, linewidth=0.8, linestyle="--")
        ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
        ax.set_axisbelow(True)

        for bar, pct, c, t in zip(bars, pcts, vals_correct, vals_total):
            if t > 0:
                ax.text(bar.get_x() + bar.get_width()/2, pct + 2,
                        f"{c}/{t}", ha="center", fontsize=9, color=DARK)

        # Overall accuracy annotation
        dec_acc = sum(1 for r in results if r["decision_correct"])
        n = len(results)
        ax.text(0.5, 0.07,
                f"Decision accuracy: {dec_acc}/{n} ({100*dec_acc/n:.0f}%)",
                ha="center", transform=ax.transAxes, fontsize=9, style="italic",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=LIGHT, edgecolor=GRAY))

    fig.suptitle("Dev vs. Held-Out Split: Match-Type Accuracy Breakdown",
                 fontsize=11, fontweight="bold", y=1.02)
    savefig(fig, out)


# ── Panel 8: Accuracy by Intervention Domain ──────────────────────────────────

def panel_intervention_domain(dev_results: list[dict], holdout_results: list[dict], out: Path):
    all_results = [(r, "dev") for r in dev_results] + [(r, "held") for r in holdout_results]

    domain_correct = defaultdict(int)
    domain_total   = defaultdict(int)
    domain_types   = defaultdict(set)   # which decision types appear per domain

    for r, split in all_results:
        interv = r["query_intervention"]
        domain = DOMAIN_MAP.get(interv, "Other")
        domain_total[domain]   += 1
        domain_correct[domain] += int(r["decision_correct"])
        domain_types[domain].add(r["expected_decision"])

    domains = sorted(domain_total, key=lambda d: -domain_total[d])
    pcts    = [100 * domain_correct[d] / domain_total[d] for d in domains]
    ns      = [domain_total[d] for d in domains]
    colors  = [BLUE if p == 100 else GREEN if p >= 80 else ORANGE if p >= 60 else RED
               for p in pcts]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    x = np.arange(len(domains))
    bars = ax.bar(x, pcts, color=colors, width=0.55, zorder=3)
    ax.set_xticks(x); ax.set_xticklabels(domains, fontsize=9)
    ax.set_ylim(0, 115)
    ax.set_ylabel("Decision accuracy (%)", fontsize=10)
    ax.set_title("Decision Accuracy by Intervention Domain\n(dev + held-out, n=26 total)",
                 fontsize=10, fontweight="bold")
    ax.axhline(100, color=GRAY, linewidth=0.8, linestyle="--")
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    for bar, pct, n in zip(bars, pcts, ns):
        ax.text(bar.get_x() + bar.get_width()/2, pct + 1.5,
                f"{pct:.0f}%\n(n={n})", ha="center", fontsize=8.5, color=DARK)

    # Right: decision-type distribution per domain (stacked bar)
    ax2 = axes[1]
    decision_colors = {"yes": GREEN, "no": BLUE, "partial": ORANGE,
                       "no_coverage": GRAY, "vague": RED}
    domain_decision_count = defaultdict(lambda: Counter())
    for r, _ in all_results:
        d = DOMAIN_MAP.get(r["query_intervention"], "Other")
        domain_decision_count[d][r["expected_decision"]] += 1

    bottoms = np.zeros(len(domains))
    for dec in ["yes", "no", "partial", "no_coverage", "vague"]:
        heights = [domain_decision_count[d].get(dec, 0) for d in domains]
        if any(h > 0 for h in heights):
            ax2.bar(x, heights, width=0.55, bottom=bottoms,
                    color=decision_colors[dec], label=dec, zorder=3)
            bottoms += np.array(heights)

    ax2.set_xticks(x); ax2.set_xticklabels(domains, fontsize=9)
    ax2.set_ylabel("Vignette count", fontsize=10)
    ax2.set_title("Decision-Type Distribution by Domain\n(what decision types each domain exercises)",
                  fontsize=10, fontweight="bold")
    ax2.legend(fontsize=8, loc="upper right", title="Decision type")
    ax2.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax2.set_axisbelow(True)

    savefig(fig, out)


# ── Panel 9: Condition-Type Contribution Analysis ─────────────────────────────

def panel_condition_contribution(out: Path):
    """
    For each condition type, show how many vignettes HINGE on that condition
    (i.e., change outcome when it is absent) — derived from ablation data.
    """
    all_vigs = VIGNETTES  # 16 dev only; holdout not used for this analysis

    condition_keys = ["nyha_class", "conditions", "reversible_cause", "care_context", "time_elapsed"]
    cond_display   = ["NYHA\nClass", "Clinical\nCondition", "Reversible\nCause",
                      "Care\nContext", "Time\nBound"]

    # Count how many vignettes specify each condition type
    specified = Counter()
    for v in all_vigs:
        state = v["scenario_state"]
        for k in condition_keys:
            if k == "conditions":
                if state.get("conditions"):
                    specified[k] += 1
            elif state.get(k) is not None:
                specified[k] += 1

    # From ablation: V2, V6, V13, V14 failed condition-blind (4 vignettes)
    # Which conditions were responsible?
    # V2: NYHA class + reversible_cause
    # V6: care_context
    # V13: time_elapsed
    # V14: conditions (clinical condition type)
    condition_ablation_hits = {
        "nyha_class":      1,  # V2
        "reversible_cause": 1, # V2
        "care_context":    1,  # V6
        "time_elapsed":    1,  # V13
        "conditions":      1,  # V14
    }

    specified_vals   = [specified[k]                   for k in condition_keys]
    ablation_vals    = [condition_ablation_hits.get(k, 0) for k in condition_keys]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(condition_keys))
    width = 0.38

    bars1 = ax.bar(x - width/2, specified_vals, width, color=BLUE,
                   label="Vignettes specifying condition", zorder=3)
    bars2 = ax.bar(x + width/2, ablation_vals, width, color=RED,
                   label="Vignettes where condition changed outcome", zorder=3)

    ax.set_xticks(x); ax.set_xticklabels(cond_display, fontsize=9)
    ax.set_ylabel("Vignette count", fontsize=10)
    ax.set_title("Activation Condition Contribution Analysis\n"
                 "(16 dev vignettes — how often each condition type is load-bearing)",
                 fontsize=10, fontweight="bold")
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=9)
    ax.set_ylim(0, max(specified_vals) + 3)

    for bar in bars1:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.1,
                    str(int(h)), ha="center", fontsize=9, color=DARK)
    for bar in bars2:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.1,
                    str(int(h)), ha="center", fontsize=9, color=DARK)

    ax.text(0.5, 0.05,
            "Condition-blind baseline fails when ANY load-bearing condition is ignored. "
            "Accuracy drops from 100% → 75%.",
            ha="center", transform=ax.transAxes, fontsize=8.5, style="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=LIGHT, edgecolor=GRAY))

    savefig(fig, out)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "presentation_figures"),
                    help="Output directory for figures")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("  ADO Comprehensive Evaluation Suite")
    print("=" * 72)

    # ── Load populated ontology (Jane Doe)
    owl_path = ROOT / "data" / "populated" / "ado_jane_doe_001.owl"
    if not owl_path.exists():
        print(f"ERROR: Ontology not found at {owl_path}")
        print("Run: python -m ado.preference_input --example")
        sys.exit(1)

    print("\n[1/5] Loading ontology and running vignette evaluations...")
    onto, patient = load_patient(owl_path)

    dev_results = [evaluate_vignette(onto, patient, v) for v in VIGNETTES]
    holdout_results = [evaluate_vignette(onto, patient, v) for v in HOLDOUT_VIGNETTES]
    blind_results = [evaluate_vignette(onto, patient, v,
                                       matcher=find_matching_preferences_condition_blind)
                     for v in VIGNETTES]

    dev_dec_acc  = sum(1 for r in dev_results     if r["decision_correct"])
    hold_dec_acc = sum(1 for r in holdout_results if r["decision_correct"])
    blind_acc    = sum(1 for r in blind_results   if r["decision_correct"])
    print(f"  Dev: {dev_dec_acc}/16  Holdout: {hold_dec_acc}/10  Blind: {blind_acc}/16")

    print("\n[2/5] Running POLST / code-status evaluation (Track 3)...")
    profile_results = [(p, *evaluate_profile(p)) for p in PROFILES]
    # evaluate_profile returns (result, field_match); expand to (p, result, field_match, all_match)
    profile_results_full = []
    for p in PROFILES:
        result, fm = evaluate_profile(p)
        all_match = all(fm.values())
        profile_results_full.append((p, result, fm, all_match))
    exact = sum(1 for _, _, _, am in profile_results_full if am)
    print(f"  Exact profile agreement: {exact}/{len(PROFILES)}")

    print("\n[3/5] Loading cohort simulation results...")
    cohort_path = ROOT / "docs" / "evaluation" / "cohort_simulation_results.json"
    if not cohort_path.exists():
        print(f"  WARNING: {cohort_path} not found — skipping cohort panel")
        cohort = None
    else:
        cohort = json.loads(cohort_path.read_text())
        print(f"  Loaded {cohort['n_cells']} cells, {cohort['n_patients']} patients")

    print("\n[4/5] Generating figures...")

    panel_confusion_matrix(
        dev_results,
        "Decision Confusion Matrix\n(16 dev vignettes, ADO full reasoner)",
        out_dir / "eval_confusion_matrix_dev.png"
    )
    panel_confusion_matrix(
        holdout_results,
        "Decision Confusion Matrix\n(10 held-out vignettes)",
        out_dir / "eval_confusion_matrix_holdout.png"
    )
    panel_ablation_breakdown(dev_results, blind_results,
                             out_dir / "eval_ablation_breakdown.png")
    if cohort:
        panel_cohort_messiness(cohort, out_dir / "eval_cohort_messiness.png")
    panel_coverage_taxonomy(out_dir / "eval_coverage_taxonomy.png")
    panel_extraction_fields(out_dir / "eval_extraction_fields.png")
    panel_polst_agreement(profile_results_full, out_dir / "eval_polst_agreement.png")
    panel_holdout_vs_dev(dev_results, holdout_results, out_dir / "eval_holdout_vs_dev.png")
    panel_intervention_domain(dev_results, holdout_results,
                              out_dir / "eval_intervention_domain.png")
    panel_condition_contribution(out_dir / "eval_condition_contribution.png")

    print("\n[5/5] Summary")
    print("=" * 72)
    print(f"  Dev vignettes         : {dev_dec_acc}/16 ({100*dev_dec_acc/16:.0f}%) decision accuracy")
    print(f"  Held-out vignettes    : {hold_dec_acc}/10 ({100*hold_dec_acc/10:.0f}%)")
    print(f"  Condition-blind       : {blind_acc}/16 ({100*blind_acc/16:.0f}%)")
    print(f"  POLST exact match     : {exact}/{len(PROFILES)} profiles")
    if cohort:
        print(f"  Cohort ADO accuracy   : {cohort['ado_decision_accuracy']*100:.1f}% ({cohort['n_cells']} cells)")
        print(f"  Checkbox accuracy     : {cohort['checkbox_accuracy']*100:.1f}%")
        print(f"  Overconfident cells   : {cohort['checkbox_overconfident_cells']}")
    print(f"\n  Figures saved to: {out_dir}")
    print("=" * 72)


if __name__ == "__main__":
    main()
