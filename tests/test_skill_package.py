"""An installed skill must validate a plan without the repository.

The skill is distributed as skill/requmexre/: an agent may copy that folder
somewhere else and have nothing else. These tests copy it to a temporary
directory, write a plan there and run the bundled validator, so a stale copy or
a path that only resolves inside the checkout fails here, not in a session.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "requmexre"
TEMPLATE = SKILL / "assets" / "template.json"

BUNDLED = [
    (ROOT / "schema" / "validate.py", SKILL / "scripts" / "validate.py"),
    (ROOT / "schema" / "render.py", SKILL / "scripts" / "render.py"),
    (ROOT / "schema" / "requmexre.schema.json", SKILL / "assets" / "requmexre.schema.json"),
    (ROOT / "schema" / "mappings.json", SKILL / "assets" / "mappings.json"),
    (ROOT / "schema" / "RULES.md", SKILL / "references" / "RULES.md"),
]


@pytest.mark.parametrize(
    "canonical, bundled",
    BUNDLED,
    ids=[str(canonical.relative_to(ROOT)) for canonical, _ in BUNDLED],
)
def test_bundled_copy_matches_the_repository(canonical, bundled):
    assert bundled.is_file(), f"missing bundled copy {bundled.relative_to(ROOT)}"
    assert bundled.read_bytes() == canonical.read_bytes()


def install(tmp_path):
    target = tmp_path / "requmexre"
    shutil.copytree(SKILL, target)
    return target


def write_plan(skill, name, mutate=None):
    plan = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    if mutate is not None:
        mutate(plan)
    path = skill / name
    path.write_text(json.dumps(plan), encoding="utf-8")
    return path


def run(skill, *arguments):
    return subprocess.run(
        [sys.executable, str(skill / "scripts" / "validate.py"), *map(str, arguments)],
        capture_output=True,
        text=True,
        cwd=skill,
    )


def test_installed_skill_validates_a_plan_without_the_repository(tmp_path):
    skill = install(tmp_path)
    write_plan(skill, "plan.json")

    result = run(skill, "plan.json")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout
    assert "0 findings" in result.stdout


def test_installed_skill_reports_a_broken_plan(tmp_path):
    skill = install(tmp_path)
    write_plan(
        skill,
        "plan.json",
        lambda plan: plan["questions"]["primary"].update(
            text="This plan measures green space and walking."
        ),
    )

    result = run(skill, "--json", "plan.json")

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["scope"] == "files"
    assert report["files"][0]["ok"] is False
    assert any(
        finding["rule"] == "R1" for finding in report["files"][0]["findings"]
    )


def test_installed_skill_refuses_a_bare_run(tmp_path):
    skill = install(tmp_path)

    result = run(skill)

    assert result.returncode == 2
    assert "no plan given" in result.stderr


def test_installed_skill_can_run_its_bundled_fixtures(tmp_path):
    skill = install(tmp_path)

    result = run(skill, "--fixtures")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 of 1 files behave as declared" in result.stdout


def test_installed_skill_renders_without_the_repository(tmp_path):
    skill = install(tmp_path)
    plan = json.loads(write_plan(skill, "plan.json").read_text(encoding="utf-8"))
    plan["meta"]["funder"] = "fwo"
    (skill / "plan.json").write_text(json.dumps(plan), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(skill / "scripts" / "render.py"), "plan.json"],
        capture_output=True,
        text=True,
        cwd=skill,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "## 1. Rationale and positioning" in result.stdout
    assert "## 3. Research methodology and work plan" in result.stdout
