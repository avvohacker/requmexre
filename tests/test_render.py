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
    ("horizon", "schema/cases/horizon.json", None),
    ("dfg", "schema/cases/dfg.json", None),
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


def test_a_document_without_a_funder_uses_the_generic_profile():
    plan = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    plan["meta"].pop("funder")

    draft = render.render_plan(plan)

    assert "## Research Question" in draft
    assert "## Methodology" in draft
    assert "## Expected Results" in draft
    assert render.coverage_gaps(plan) == []


def test_none_renders_the_generic_profile():
    plan = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    draft = render.render_plan(plan)

    assert draft.index("## Research Question") < draft.index("## Methodology")
    assert draft.index("## Methodology") < draft.index("## Expected Results")
    assert "Local green-space inventories and health surveys" in draft
    assert plan["method"]["procedure"] in draft
    assert plan["results"][0]["claim"] in draft
    assert render.coverage_gaps(plan) == []


def test_other_renders_the_generic_profile():
    plan = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    plan["meta"].update(funder="other", scheme="ERC Starting Grant")

    draft = render.render_plan(plan)

    assert "## Research Question" in draft
    assert "## Methodology" in draft
    assert "## Expected Results" in draft


def test_heading_overrides_rename_the_generic_sections():
    plan = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    draft = render.render_plan(
        plan,
        headings={
            "question": "Domanda di ricerca",
            "method": "Metodologia",
            "results": "Risultati attesi",
        },
    )

    assert "## Domanda di ricerca" in draft
    assert "## Metodologia" in draft
    assert "## Risultati attesi" in draft
    assert "## Research Question" not in draft


def test_heading_overrides_are_refused_for_a_mapped_funder():
    plan = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    plan["meta"]["funder"] = "fwo"

    with pytest.raises(render.RenderError, match="generic profile only"):
        render.render_plan(plan, headings={"question": "Domanda di ricerca"})


def test_cli_renders_a_document_without_a_funder(tmp_path):
    plan = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    plan["meta"].pop("funder")
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(RENDER), str(path)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert "## Research Question" in result.stdout
    assert "## Methodology" in result.stdout
    assert "## Expected Results" in result.stdout
    assert result.stderr == ""


def test_cli_passes_heading_overrides(tmp_path):
    plan = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(RENDER),
            str(path),
            "--heading-question",
            "Domanda di ricerca",
            "--heading-method",
            "Metodologia",
            "--heading-results",
            "Risultati attesi",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert "## Domanda di ricerca" in result.stdout
    assert "## Risultati attesi" in result.stdout


def test_cli_warns_when_other_uses_the_generic_profile(tmp_path):
    plan = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    plan["meta"].update(funder="other", scheme="ERC Starting Grant")
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(RENDER), str(path)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert "## Research Question" in result.stdout
    assert "warning: generic profile for ERC Starting Grant" in result.stderr


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
    plan = load_case("schema/cases/dfg.json", None)

    gaps = dict(render.coverage_gaps(plan))

    assert "results" in gaps
    assert "no results section" in gaps["results"]


def test_cli_warns_on_a_dfg_plan_that_carries_results():
    result = subprocess.run(
        [sys.executable, str(RENDER), str(ROOT / "schema" / "cases" / "dfg.json")],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == golden("dfg")
    assert "warning: results has no section for dfg" in result.stderr
    assert "DFG has no results section" in result.stderr


@pytest.mark.parametrize(
    "funder,source,section",
    [
        ("dfg", "schema/cases/dfg-no-results.json", "## 2.3 Work programme"),
        ("snsf", "schema/cases/snsf-no-results.json", "## 3. Detailed research plan"),
    ],
    ids=["dfg", "snsf"],
)
def test_no_results_exemption_renders_without_a_results_block(funder, source, section):
    plan = json.loads((ROOT / source).read_text(encoding="utf-8"))
    assert plan["meta"]["funder"] == funder

    draft = render.render_plan(plan)

    assert section in draft
    assert "The document states no results." not in draft
    assert render.coverage_gaps(plan) == []

    result = subprocess.run(
        [sys.executable, str(RENDER), str(ROOT / source)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == draft
    assert result.stderr == ""
