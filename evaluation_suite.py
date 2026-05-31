#!/usr/bin/env python3
"""Run all evaluation tracks and write docs/evaluation_results_summary.md."""

import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs" / "evaluation_results_summary.md"


def capture(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return e.output or str(e)


def main():
    subprocess.run([sys.executable, "eval_inter_annotator.py", "--export-template"], cwd=ROOT, check=False)

    parts = [
        f"# ADO Evaluation Results Summary\n\nGenerated: {date.today().isoformat()}\n\n",
        "## Track 1 — Vignettes (development + held-out)\n\n```\n",
        capture([sys.executable, "vignette_eval.py", "--suite", "all"]),
        "```\n\n## Track 1 — Ablation (condition-blind, development only)\n\n```\n",
        capture([sys.executable, "vignette_eval.py", "--suite", "dev", "--baseline", "condition-blind"]),
        "```\n\n## Track 3 — Code status / POLST\n\n```\n",
        capture([sys.executable, "track3_evaluation.py"]),
        "```\n\n## Coverage (30 inventory clauses)\n\n```\n",
        capture([sys.executable, "coverage_analysis.py"]),
        "```\n\n## Inter-annotator agreement (extraction)\n\n```\n",
        capture([sys.executable, "eval_inter_annotator.py"]),
        "```\n",
    ]
    OUT.write_text("".join(parts))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
