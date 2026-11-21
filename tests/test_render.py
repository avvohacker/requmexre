"""The renderer must reproduce its golden drafts, funder by funder.

Each golden file is the whole output for one plan: section names, order, and the
prose the mapping produces. A change in wording, in field placement or in the
output rule shows up as a diff here before it reaches a reader.
"""

from __future__ import annotations

import copy
import difflib
import json
import subprocess
import sys
from pathlib import Path

import pytest

import render

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / "schema" / "render.py"
GOLDEN = ROOT / "tests" / "golden" / "render"
TEMPLATE = ROOT / "skill" / "requmexre" / "assets" / "template.json"

CASES = [
    ("fwo", "schema/cases/fwo.json", None),
    ("prin", "schema/cases/prin.json", None),
    ("vub", "schema/cases/vub.json", None),
    ("horizon", "schema/cases/fwo.json", "horizon"),
    ("dfg", "schema/cases/fwo.json", "dfg"),
    ("snsf", "schema/cases/fwo.json", "snsf"),
]


def load_case(source, funder):
    plan = json.loads((ROOT / source).read_text(encoding="utf-8"))
    if funder is not None:
        plan = copy.deepcopy(plan)
        plan["meta"]["funder"] = funder
    return plan


def golden(name):
    return (GOLDEN / f"{name}.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("name,source,funder", CASES, ids=[case[0] for case in CASES])
def test_render_matches_the_golden_draft(name, source, funder):
    actual = render.render_plan(load_case(source, funder))
    expected = golden(name)
    if actual != expected:
        diff = "".join(
            difflib.unified_diff(
                expected.splitlines(keepends=True),
                actual.splitlines(keepends=True),
                fromfile=f"golden/{name}.md",
                tofile="rendered",
            )
        )
        pytest.fail(f"the draft changed:\n{diff}")


def test_cli_writes_the_same_draft_as_the_library():
    result = subprocess.run(
        [sys.executable, str(RENDER), str(ROOT / "schema" / "cases" / "fwo.json")],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == golden("fwo")
    assert result.stderr == ""


def test_a_plan_without_a_funder_is_refused():
    plan = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    with pytest.raises(render.RenderError, match="no funder"):
        render.render_plan(plan)


def test_other_is_refused_because_it_has_no_table():
    plan = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    plan["meta"].update(funder="other", scheme="ERC Starting Grant")

    with pytest.raises(render.RenderError, match="has no section table"):
        render.render_plan(plan)


def test_the_cli_refuses_a_plan_the_validator_rejects(tmp_path):
    plan = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    plan["meta"]["funder"] = "fwo"
    plan["questions"]["primary"].update(
        text="The study measures walking among older adults."
    )
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(RENDER), str(path)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert result.returncode == 1
    assert "R1" in result.stderr
    assert result.stdout == ""


def test_dfg_reports_results_as_a_coverage_gap():
    plan = load_case("schema/cases/fwo.json", "dfg")

    gaps = dict(render.coverage_gaps(plan))

    assert "results" in gaps
    assert "no results section" in gaps["results"]
