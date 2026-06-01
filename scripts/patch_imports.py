#!/usr/bin/env python3
"""Apply import/path updates after repo reorganization."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATH_BLOCK = """
import sys
from pathlib import Path as _Path
_ADO_ROOT = _Path(__file__).resolve().parents[1]
_ADO_EVAL = _Path(__file__).resolve().parent
for _p in (_ADO_ROOT, _ADO_EVAL):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
""".strip() + "\n\n"

SUBS = [
    ("populated_ontologies/", "data/populated/"),
    ("populated_ontologies", "data/populated"),
    ("gold_annotations/", "data/gold/"),
    ("gold_annotations", "data/gold"),
    ("from eval_baselines", "from baselines"),
    ("from eval_data.patient_cohort", "from data.patient_cohort"),
    ("from eval_data.scenario_battery", "from data.scenario_battery"),
    ("from query_evaluation", "from ado.query_evaluation"),
    ("from preference_input", "from ado.preference_input"),
    ("from code_status", "from ado.code_status"),
    ("from holdout_vignettes", "from ado.holdout_vignettes"),
    ("from oracle_gold", "from oracle_gold"),
    ("from gemini_extraction", "from ado.gemini_extraction"),
    ("from llm_direct_reasoning", "from ado.llm_direct_reasoning"),
    ("import preference_input", "from ado import preference_input"),
    ("import llm_extraction", "from ado import llm_extraction"),
    ("docs/cohort_simulation_results.json", "docs/evaluation/cohort_simulation_results.json"),
    ("docs/evaluation_results_summary.md", "docs/evaluation/evaluation_results_summary.md"),
    ('"vignette_eval.py"', '"evaluation/vignette_eval.py"'),
    ('"realistic_simulation.py"', '"evaluation/realistic_simulation.py"'),
    ('"track3_evaluation.py"', '"evaluation/track3_evaluation.py"'),
    ('"coverage_analysis.py"', '"evaluation/coverage_analysis.py"'),
    ('"eval_inter_annotator.py"', '"evaluation/eval_inter_annotator.py"'),
]


def apply_subs(text: str) -> str:
    for a, b in SUBS:
        text = text.replace(a, b)
    return text


def insert_path_block(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out, i = [], 0
    if lines and lines[0].startswith("#!"):
        out.append(lines[0])
        i = 1
    if i < len(lines) and '"""' in lines[i]:
        out.append(lines[i])
        i += 1
        while i < len(lines) and not lines[i].strip().endswith('"""'):
            out.append(lines[i])
            i += 1
        if i < len(lines):
            out.append(lines[i])
            i += 1
    while i < len(lines) and lines[i].strip().startswith("from __future__"):
        out.append(lines[i])
        i += 1
    out.append(PATH_BLOCK)
    out.extend(lines[i:])
    return "".join(out)


def patch_eval(path: Path) -> None:
    t = apply_subs(path.read_text(encoding="utf-8"))
    if "_ADO_ROOT" not in t:
        t = insert_path_block(t)
    if path.name == "evaluation_suite.py":
        t = t.replace("ROOT = Path(__file__).parent", "ROOT = Path(__file__).resolve().parents[1]")
        t = t.replace(
            'OUT = ROOT / "docs/evaluation/evaluation_results_summary.md"',
            'OUT = ROOT / "docs" / "evaluation" / "evaluation_results_summary.md"',
        )
    if path.name == "eval_inter_annotator.py":
        t = t.replace("ROOT = Path(__file__).parent", "ROOT = Path(__file__).resolve().parents[1]")
    if path.name == "ablation_evaluation.py":
        t = t.replace("ROOT = Path(__file__).parent", "ROOT = Path(__file__).resolve().parents[1]")
    path.write_text(t, encoding="utf-8")


def patch_ado() -> None:
    pref = ROOT / "ado/preference_input.py"
    t = apply_subs(pref.read_text(encoding="utf-8"))
    old = (
        'OWL_FILE = Path(__file__).parent / "advanced_directives.owl"\n'
        'OUTPUT_DIR = Path(__file__).parent / "populated_ontologies"'
    )
    if old in t:
        t = t.replace(old, "from ado.paths import OWL_FILE, POPULATED_DIR as OUTPUT_DIR")
    pref.write_text(t, encoding="utf-8")
    for name in ("query_evaluation.py", "code_status.py"):
        p = ROOT / "ado" / name
        p.write_text(apply_subs(p.read_text(encoding="utf-8")), encoding="utf-8")


def main() -> None:
    for py in (ROOT / "evaluation").glob("*.py"):
        if py.name != "__init__.py":
            patch_eval(py)
    patch_ado()
    print("Done.")


if __name__ == "__main__":
    main()
