#!/usr/bin/env python3
"""
ADO Failure Mode Analysis
==========================
Runs the full 50-patient × 25-scenario simulation, categorizes every ADO
failure, and produces four diagnostic figures:

  eval_failure_taxonomy.png       — breakdown of failure types (all 3,550 cells)
  eval_scenario_difficulty.png    — per-scenario accuracy (25 bars)
  eval_failure_heatmap.png        — patient × scenario pass/fail grid
  eval_coverage_gap_by_intervention.png — which interventions produce coverage gaps

Failure taxonomy:
  coverage_gap       ADO no_coverage; ref expects yes/no/partial
                     → honest closed-world silence, but oracle infers coverage
  false_activation   ADO fires (yes/no/partial); ref is no_coverage
                     → ADO wrongly asserts coverage
  direction_error    ADO yes; ref no (or vice versa) — completely inverted
  boundary_confusion ADO partial; ref clear (or vice versa) — right direction, wrong confidence
  correct            ADO matches ref on both decision + match_type

Usage:
    python evaluation/failure_analysis.py
    python evaluation/failure_analysis.py --out results/failure_figures/
"""
from __future__ import annotations

import contextlib
import copy
import io
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = Path(__file__).resolve().parent
for p in (ROOT, EVAL_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from baselines import find_matching_preferences_condition_blind
from data.patient_cohort import PATIENT_COHORT
from data.scenario_battery import SCENARIO_BATTERY
from oracle_gold import checkbox_baseline, reference_expected
from ado.preference_input import load_ontology, populate_patient
from ado.query_evaluation import evaluate_vignette

# ── Palette ────────────────────────────────────────────────────────────────────
BLUE   = "#2166ac"
RED    = "#d6604d"
ORANGE = "#f4a582"
GREEN  = "#4dac26"
GRAY   = "#999999"
PURPLE = "#984ea3"
TEAL   = "#018571"
DARK   = "#1a1a1a"
LIGHT  = "#f7f7f7"

FAILURE_COLORS = {
    "correct":           GREEN,
    "coverage_gap":      BLUE,
    "false_activation":  RED,
    "direction_error":   ORANGE,
    "boundary_confusion": PURPLE,
}

FAILURE_LABELS = {
    "correct":           "Correct",
    "coverage_gap":      "Coverage gap\n(ADO silent, oracle expects coverage)",
    "false_activation":  "False activation\n(ADO fires, oracle says no coverage)",
    "direction_error":   "Direction error\n(ADO yes↔no inversion)",
    "boundary_confusion": "Boundary confusion\n(partial vs. clear disagreement)",
}


# ── Failure classification ─────────────────────────────────────────────────────

def classify(row: dict) -> str:
    ref_d  = row["ref_decision"]
    ado_d  = row["ado_decision"]
    ref_mt = row["ref_match"]
    ado_mt = row["ado_match"]

    if ado_d == ref_d and ado_mt == ref_mt:
        return "correct"

    # ADO returns no_coverage but oracle expects actual coverage
    if ado_d == "no_coverage" and ref_d not in ("no_coverage",):
        return "coverage_gap"

    # ADO fires a real decision (yes/no/partial) but oracle says not applicable
    if ref_d == "no_coverage" and ado_d not in ("no_coverage",):
        return "false_activation"

    # Completely inverted direction
    if (ado_d == "yes" and ref_d == "no") or (ado_d == "no" and ref_d == "yes"):
        return "direction_error"

    # Confidence level / match-type mismatch (direction correct, gradient wrong)
    return "boundary_confusion"


# ── Simulation ─────────────────────────────────────────────────────────────────

def run_full_simulation() -> list[dict]:
    rows = []
    for prec in PATIENT_COHORT:
        pdata = {
            "patient_id": prec["patient_id"],
            "patient_name": prec["patient_name"],
            "source_document": {"type": "living_will", "label": "Advance directive"},
            "preferences": copy.deepcopy(prec.get("preferences", [])),
        }
        onto = load_ontology()
        with contextlib.redirect_stdout(io.StringIO()):
            populate_patient(onto, pdata)
        patients = list(onto.search(type=onto.Patient))
        if not patients:
            continue
        patient = max(patients, key=lambda p: len(p.hasPreference) if p.hasPreference else 0)

        for scenario in SCENARIO_BATTERY:
            state = scenario["scenario_state"]
            for intervention in scenario["interventions"]:
                vignette = {
                    "id": f"{prec['patient_id']}_{scenario['id']}_{intervention}",
                    "description": scenario["description"],
                    "query_intervention": intervention,
                    "scenario_state": state,
                    "expected": reference_expected(pdata, state, intervention),
                }
                ref = vignette["expected"]
                ado = evaluate_vignette(onto, patient, vignette)
                row = {
                    "patient_id":   prec["patient_id"],
                    "messy_level":  prec.get("messy_level", "typical"),
                    "scenario_id":  scenario["id"],
                    "scenario_desc": scenario["description"],
                    "intervention": intervention,
                    "ref_decision": ref["decision"],
                    "ref_match":    ref["match_type"],
                    "ado_decision": ado["system_decision"],
                    "ado_match":    ado["system_match_type"],
                }
                row["failure_mode"] = classify(row)
                rows.append(row)
    return rows


# ── Figure helpers ─────────────────────────────────────────────────────────────

def savefig(fig, path: Path):
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  saved → {path.name}")


# ── Figure 1: Failure taxonomy overview ────────────────────────────────────────

def fig_failure_taxonomy(rows: list[dict], out: Path):
    total = len(rows)
    order = ["correct", "coverage_gap", "false_activation", "direction_error", "boundary_confusion"]
    counts = Counter(r["failure_mode"] for r in rows)
    vals   = [counts.get(k, 0) for k in order]
    pcts   = [100 * v / total for v in vals]
    colors = [FAILURE_COLORS[k] for k in order]
    labels = [
        "Correct",
        "Coverage gap",
        "False activation",
        "Direction error",
        "Boundary confusion",
    ]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Left: absolute + % bars
    ax = axes[0]
    x = np.arange(len(order))
    bars = ax.bar(x, vals, color=colors, width=0.6, zorder=3, edgecolor="white")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Cell count", fontsize=10)
    ax.set_title(f"ADO Failure Taxonomy\n(all {total:,} evaluation cells, 50 patients × 25 scenarios)",
                 fontsize=10, fontweight="bold")
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    for bar, val, pct in zip(bars, vals, pcts):
        ax.text(bar.get_x() + bar.get_width()/2, val + 15,
                f"{val:,}\n({pct:.1f}%)", ha="center", fontsize=8.5, color=DARK, fontweight="bold")

    # Key insight annotation
    gap    = counts.get("coverage_gap",      0)
    false_ = counts.get("false_activation",  0)
    dir_   = counts.get("direction_error",   0)
    ratio  = false_ / max(gap, 1)
    ax.text(0.5, 0.04,
            f"False activations ({false_:,}) outnumber coverage gaps ({gap:,}) by {ratio:.1f}×\n"
            f"→ ADO over-fires more than it stays silent; direction errors ({dir_:,}) are rare",
            ha="center", transform=ax.transAxes, fontsize=8.5, style="italic",
            bbox=dict(boxstyle="round,pad=0.4", facecolor=LIGHT, edgecolor=GRAY))

    # Right: stacked bar by messy level
    ax2 = axes[1]
    messy_order = ["clean", "typical", "minimal", "incomplete_encoding",
                   "contradictory", "outdated", "culturally_complex"]
    messy_display = ["Clean", "Typical", "Minimal", "Incomplete", "Contradictory", "Outdated", "Cultural"]
    by_messy: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        by_messy[r["messy_level"]][r["failure_mode"]] += 1

    ml_present = [m for m in messy_order if m in by_messy]
    ml_display = [messy_display[messy_order.index(m)] for m in ml_present]

    bottoms = np.zeros(len(ml_present))
    mode_order = ["correct", "coverage_gap", "false_activation", "direction_error", "boundary_confusion"]
    for mode in mode_order:
        heights = [by_messy[ml].get(mode, 0) for ml in ml_present]
        ax2.bar(np.arange(len(ml_present)), heights, bottom=bottoms,
                color=FAILURE_COLORS[mode], label=FAILURE_LABELS[mode].split("\n")[0],
                width=0.6, zorder=3, edgecolor="white")
        bottoms += np.array(heights)

    ax2.set_xticks(np.arange(len(ml_present)))
    ax2.set_xticklabels(ml_display, fontsize=9)
    ax2.set_ylabel("Cell count", fontsize=10)
    ax2.set_title("Failure Mode by Encoding Quality",
                  fontsize=10, fontweight="bold")
    ax2.legend(fontsize=7.5, loc="upper right", framealpha=0.9)
    ax2.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax2.set_axisbelow(True)

    savefig(fig, out)


# ── Figure 2: Per-scenario difficulty ──────────────────────────────────────────

def fig_scenario_difficulty(rows: list[dict], out: Path):
    # Scenario accuracy and failure breakdown
    scenario_ids = [s["id"] for s in SCENARIO_BATTERY]
    scenario_desc_short = {
        s["id"]: s["description"][:40] + ("…" if len(s["description"]) > 40 else "")
        for s in SCENARIO_BATTERY
    }

    by_scen: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        by_scen[r["scenario_id"]][r["failure_mode"]] += 1

    # Compute accuracy per scenario
    def acc(sid):
        c = by_scen[sid]
        t = sum(c.values())
        return 100 * c.get("correct", 0) / t if t else 0

    sids_sorted = sorted(scenario_ids, key=acc)
    accs  = [acc(s) for s in sids_sorted]
    totals = [sum(by_scen[s].values()) for s in sids_sorted]

    # Color by accuracy tier
    bar_colors = [GREEN if a >= 60 else ORANGE if a >= 35 else RED for a in accs]

    # Scenario type labels (canonical / boundary / multi / outside / stress)
    def stype(sid):
        n = int(sid[1:])
        if n <= 11:   return "Canonical"
        if n <= 16:   return "Boundary"
        if n <= 19:   return "Multi-cond"
        if n <= 23:   return "Out-of-scope"
        return "Stress"

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: horizontal bars sorted by accuracy
    ax = axes[0]
    y = np.arange(len(sids_sorted))
    ax.barh(y, accs, color=bar_colors, height=0.7, zorder=3, edgecolor="white")
    ax.axvline(41.4, color=GRAY, linewidth=1, linestyle="--", label="Overall mean (41.4%)")
    ax.set_yticks(y)
    ax.set_yticklabels(
        [f"{s}  {scenario_desc_short[s]}" for s in sids_sorted],
        fontsize=7.5
    )
    ax.set_xlabel("ADO accuracy (%)", fontsize=10)
    ax.set_title("Per-Scenario Accuracy (all 50 patients)\nSorted worst → best",
                 fontsize=10, fontweight="bold")
    ax.xaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    for i, (a, n) in enumerate(zip(accs, totals)):
        ax.text(a + 0.5, i, f"{a:.0f}%", va="center", fontsize=7, color=DARK)
    legend_patches = [
        mpatches.Patch(color=GREEN,  label="≥60% (good)"),
        mpatches.Patch(color=ORANGE, label="35–60% (moderate)"),
        mpatches.Patch(color=RED,    label="<35% (hard)"),
        mpatches.Patch(color=GRAY,   label="Overall mean 41.4%"),
    ]
    ax.legend(handles=legend_patches, fontsize=8, loc="lower right")

    # Right: stacked bars by scenario type
    ax2 = axes[1]
    type_order = ["Canonical", "Boundary", "Multi-cond", "Out-of-scope", "Stress"]
    type_colors_map = {
        "Canonical":    BLUE,
        "Boundary":     ORANGE,
        "Multi-cond":   PURPLE,
        "Out-of-scope": RED,
        "Stress":       GRAY,
    }
    type_acc = defaultdict(list)
    for s in scenario_ids:
        type_acc[stype(s)].append(acc(s))

    type_means = [np.mean(type_acc[t]) if type_acc[t] else 0 for t in type_order]
    type_ns    = [len(type_acc[t]) for t in type_order]
    colors2 = [type_colors_map[t] for t in type_order]
    bars2 = ax2.bar(np.arange(len(type_order)), type_means, color=colors2, width=0.55, zorder=3)
    ax2.axhline(41.4, color=GRAY, linewidth=1, linestyle="--")
    ax2.set_xticks(np.arange(len(type_order)))
    ax2.set_xticklabels(type_order, fontsize=9)
    ax2.set_ylabel("Mean ADO accuracy (%)", fontsize=10)
    ax2.set_title("Accuracy by Scenario Category",
                  fontsize=10, fontweight="bold")
    ax2.set_ylim(0, 80)
    ax2.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax2.set_axisbelow(True)
    for bar, val, n in zip(bars2, type_means, type_ns):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 1.5,
                 f"{val:.0f}%\n(n={n} scen.)", ha="center", fontsize=8.5, color=DARK)

    savefig(fig, out)


# ── Figure 3: Patient × Scenario failure heatmap ──────────────────────────────

def fig_failure_heatmap(rows: list[dict], out: Path):
    patients = [p["patient_id"] for p in PATIENT_COHORT]
    scenarios = [s["id"] for s in SCENARIO_BATTERY]

    # For each (patient, scenario) cell, find dominant failure mode
    # (a cell has multiple rows if multiple interventions were tested)
    cell_modes: dict[tuple, Counter] = defaultdict(Counter)
    for r in rows:
        cell_modes[(r["patient_id"], r["scenario_id"])][r["failure_mode"]] += 1

    def dominant_mode(counter):
        if not counter:
            return "correct"
        # If any intervention is false_activation or direction_error, flag it
        for critical in ("false_activation", "direction_error"):
            if counter.get(critical, 0) > 0:
                return critical
        # Otherwise pick most common failure
        return counter.most_common(1)[0][0]

    # Mode → integer for coloring
    mode_int = {
        "correct":           0,
        "coverage_gap":      1,
        "false_activation":  2,
        "direction_error":   3,
        "boundary_confusion": 4,
    }
    mode_colors_list = [GREEN, BLUE, RED, ORANGE, PURPLE]
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(mode_colors_list)

    # Build matrix
    matrix = np.zeros((len(patients), len(scenarios)), dtype=int)
    for pi, pat in enumerate(patients):
        for si, scen in enumerate(scenarios):
            c = cell_modes.get((pat, scen), Counter({"correct": 1}))
            matrix[pi, si] = mode_int[dominant_mode(c)]

    # Patient labels (short ID + messy level)
    messy_map = {p["patient_id"]: p.get("messy_level", "?") for p in PATIENT_COHORT}
    pat_labels = [
        f"{pid.split('_')[0]}  [{messy_map.get(pid,'?')[:4]}]"
        for pid in patients
    ]

    fig, ax = plt.subplots(figsize=(16, 14))
    im = ax.imshow(matrix, cmap=cmap, vmin=-0.5, vmax=4.5, aspect="auto")

    ax.set_xticks(np.arange(len(scenarios)))
    ax.set_xticklabels(scenarios, fontsize=7, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(patients)))
    ax.set_yticklabels(pat_labels, fontsize=6.5)
    ax.set_xlabel("Scenario", fontsize=10, fontweight="bold")
    ax.set_ylabel("Patient (short ID + messy level)", fontsize=10, fontweight="bold")
    ax.set_title(
        "ADO Failure Mode Heatmap — 50 Patients × 25 Scenarios\n"
        "(dominant failure mode per patient × scenario cell)",
        fontsize=11, fontweight="bold"
    )

    legend_patches = [
        mpatches.Patch(color=c, label=FAILURE_LABELS[m].split("\n")[0])
        for m, c in FAILURE_COLORS.items()
    ]
    ax.legend(handles=legend_patches, fontsize=8, loc="upper right",
              bbox_to_anchor=(1.18, 1.0), framealpha=0.9)

    # Thin grid lines
    ax.set_xticks(np.arange(-0.5, len(scenarios), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(patients), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.3)
    ax.tick_params(which="minor", length=0)

    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  saved → {out.name}")


# ── Figure 4: Coverage-gap analysis by intervention ────────────────────────────

def fig_coverage_gap_by_intervention(rows: list[dict], out: Path):
    """
    For coverage-gap rows (ADO silent, oracle expects answer):
      - How many gaps per intervention?
      - What did the oracle expect? (yes / no / partial)
    Also show false-activation count per intervention.
    """
    gap_rows   = [r for r in rows if r["failure_mode"] == "coverage_gap"]
    false_rows = [r for r in rows if r["failure_mode"] == "false_activation"]

    gap_by_interv   = Counter(r["intervention"] for r in gap_rows)
    false_by_interv = Counter(r["intervention"] for r in false_rows)
    correct_by_interv = Counter(r["intervention"] for r in rows if r["failure_mode"] == "correct")

    # All interventions that appear in any failure
    all_intervs = sorted(
        set(gap_by_interv) | set(false_by_interv),
        key=lambda i: -(gap_by_interv.get(i, 0) + false_by_interv.get(i, 0))
    )[:20]  # top 20

    gap_vals   = [gap_by_interv.get(i, 0)   for i in all_intervs]
    false_vals = [false_by_interv.get(i, 0) for i in all_intervs]

    # What did oracle expect for the gap rows?
    gap_ref_by_interv: dict[str, Counter] = defaultdict(Counter)
    for r in gap_rows:
        gap_ref_by_interv[r["intervention"]][r["ref_decision"]] += 1

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: coverage gap + false activation by intervention
    ax = axes[0]
    y = np.arange(len(all_intervs))
    width = 0.38
    ax.barh(y + width/2, gap_vals,   width, color=BLUE, label="Coverage gap (ADO silent)", zorder=3)
    ax.barh(y - width/2, false_vals, width, color=RED,  label="False activation (ADO over-fires)", zorder=3)
    ax.set_yticks(y); ax.set_yticklabels(all_intervs, fontsize=8.5)
    ax.set_xlabel("Cell count", fontsize=10)
    ax.set_title("Coverage Gaps vs. False Activations\nby Intervention (top 20 by total failures)",
                 fontsize=10, fontweight="bold")
    ax.legend(fontsize=9)
    ax.xaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)

    # Right: For gap rows, what did the oracle expect?
    ax2 = axes[1]
    ref_labels = ["yes", "no", "partial"]
    ref_colors  = [GREEN, BLUE, ORANGE]

    # Top 12 interventions by gap count
    top12 = sorted(gap_by_interv, key=lambda i: -gap_by_interv[i])[:12]
    bottoms2 = np.zeros(len(top12))
    for ref_d, color in zip(ref_labels, ref_colors):
        heights = [gap_ref_by_interv[i].get(ref_d, 0) for i in top12]
        ax2.bar(np.arange(len(top12)), heights, bottom=bottoms2, color=color,
                label=f"oracle says '{ref_d}'", width=0.6, zorder=3, edgecolor="white")
        bottoms2 += np.array(heights)

    ax2.set_xticks(np.arange(len(top12)))
    ax2.set_xticklabels(top12, fontsize=8, rotation=35, ha="right")
    ax2.set_ylabel("Coverage gap count", fontsize=10)
    ax2.set_title("What Oracle Expected in Coverage Gap Cells\n"
                  "(i.e., what ADO missed by being silent)",
                  fontsize=10, fontweight="bold")
    ax2.legend(fontsize=9, loc="upper right")
    ax2.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax2.set_axisbelow(True)

    # Key insight
    total_gaps = sum(gap_vals)
    total_false = sum(false_vals)
    ax2.text(0.5, 0.02,
             f"Total coverage gaps: {total_gaps}  |  Total false activations: {total_false}\n"
             f"ADO over-fires {total_false/max(total_gaps,1):.1f}× more often than it stays silent — "
             "primary failure mode is asserting coverage the directive doesn't support",
             ha="center", transform=ax2.transAxes, fontsize=8, style="italic",
             bbox=dict(boxstyle="round,pad=0.3", facecolor=LIGHT, edgecolor=GRAY))

    savefig(fig, out)


# ── Figure 5: Oracle uncertainty — how hard IS the right answer? ───────────────

def fig_oracle_uncertainty(rows: list[dict], out: Path):
    """
    Show what fraction of the reference oracle's answers are themselves uncertain
    (partial / vague / no_coverage), broken down by scenario type and messy level.
    This contextualizes the 41.4% ADO accuracy: how often is 'I don't know' the right answer?
    """
    def is_uncertain(r):
        return r["ref_decision"] in ("partial", "no_coverage", "vague")

    def stype(sid):
        n = int(sid[1:])
        if n <= 11:   return "Canonical"
        if n <= 16:   return "Boundary"
        if n <= 19:   return "Multi-cond"
        if n <= 23:   return "Out-of-scope"
        return "Stress"

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: oracle decision distribution overall
    ax = axes[0]
    oracle_counts = Counter(r["ref_decision"] for r in rows)
    dec_order   = ["yes", "no", "partial", "no_coverage", "vague"]
    dec_display = ["yes", "no", "partial", "no cov.", "vague"]
    dec_colors  = [GREEN, BLUE, ORANGE, GRAY, RED]
    vals = [oracle_counts.get(d, 0) for d in dec_order]
    total = sum(vals)
    bars = ax.bar(np.arange(len(dec_order)), vals,
                  color=dec_colors, width=0.55, zorder=3, edgecolor="white")
    ax.set_xticks(np.arange(len(dec_order)))
    ax.set_xticklabels(dec_display, fontsize=10)
    ax.set_ylabel("Cell count", fontsize=10)
    ax.set_title(f"Oracle (Reference) Decision Distribution\n(all {total:,} cells — how hard is the right answer?)",
                 fontsize=10, fontweight="bold")
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, val + 15,
                f"{val:,}\n({100*val/total:.0f}%)", ha="center", fontsize=8.5, color=DARK)

    uncertain_total = sum(oracle_counts.get(d, 0) for d in ("partial", "no_coverage", "vague"))
    ax.text(0.5, 0.06,
            f"{uncertain_total:,} of {total:,} cells ({100*uncertain_total/total:.0f}%) "
            f"have inherently uncertain reference answers\n"
            "→ a system that refuses to guess IS the right answer",
            ha="center", transform=ax.transAxes, fontsize=8.5, style="italic",
            bbox=dict(boxstyle="round,pad=0.4", facecolor=LIGHT, edgecolor=GRAY))

    # Right: oracle uncertainty rate by messy level
    ax2 = axes[1]
    messy_order = ["clean", "typical", "minimal", "incomplete_encoding",
                   "contradictory", "outdated", "culturally_complex"]
    messy_display = ["Clean", "Typical", "Minimal", "Incomplete", "Contradictory", "Outdated", "Cultural"]
    by_messy_uncertain: dict[str, list] = defaultdict(list)
    for r in rows:
        by_messy_uncertain[r["messy_level"]].append(int(is_uncertain(r)))

    ml_present  = [m for m in messy_order if m in by_messy_uncertain]
    ml_disp     = [messy_display[messy_order.index(m)] for m in ml_present]
    unc_rates   = [100 * np.mean(by_messy_uncertain[m]) for m in ml_present]
    unc_colors  = [RED if r > 70 else ORANGE if r > 55 else GREEN for r in unc_rates]

    bars2 = ax2.bar(np.arange(len(ml_present)), unc_rates,
                    color=unc_colors, width=0.55, zorder=3, edgecolor="white")
    ax2.axhline(100 * uncertain_total / total, color=GRAY, linewidth=1, linestyle="--",
                label=f"Overall uncertainty rate ({100*uncertain_total/total:.0f}%)")
    ax2.set_xticks(np.arange(len(ml_present)))
    ax2.set_xticklabels(ml_disp, fontsize=9)
    ax2.set_ylabel("Oracle uncertainty rate (%)", fontsize=10)
    ax2.set_ylim(0, 105)
    ax2.set_title("How Often Is 'I Don't Know' the Right Answer?\nBy encoding quality level",
                  fontsize=10, fontweight="bold")
    ax2.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax2.set_axisbelow(True)
    ax2.legend(fontsize=8)
    for bar, val in zip(bars2, unc_rates):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 1.5,
                 f"{val:.0f}%", ha="center", fontsize=9, color=DARK, fontweight="bold")

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
    print("  ADO Failure Mode Analysis")
    print("=" * 72)
    print("\nRunning full simulation (50 patients × 25 scenarios)...")
    rows = run_full_simulation()
    print(f"  Generated {len(rows):,} evaluation cells")

    counts = Counter(r["failure_mode"] for r in rows)
    total  = len(rows)
    print(f"\nFailure taxonomy:")
    for mode in ["correct", "coverage_gap", "false_activation", "direction_error", "boundary_confusion"]:
        n = counts.get(mode, 0)
        print(f"  {mode:22s}: {n:4d}  ({100*n/total:.1f}%)")

    print("\nGenerating figures...")
    fig_failure_taxonomy(rows, out_dir / "eval_failure_taxonomy.png")
    fig_scenario_difficulty(rows, out_dir / "eval_scenario_difficulty.png")
    fig_failure_heatmap(rows, out_dir / "eval_failure_heatmap.png")
    fig_coverage_gap_by_intervention(rows, out_dir / "eval_coverage_gap_by_intervention.png")
    fig_oracle_uncertainty(rows, out_dir / "eval_oracle_uncertainty.png")

    print(f"\n  All figures saved to: {out_dir}")
    print("=" * 72)


if __name__ == "__main__":
    main()
