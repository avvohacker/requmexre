"""CLI tests for schema/validate.py.

The validator is the only interface most users see, so its exit status and its
per-file verdicts are pinned here: 0 when every file behaves as declared, 1 when
one does not, and a FAIL line naming the file and its findings.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "schema" / "validate.py"
CASES = ROOT / "schema" / "cases"
TEMPLATE = ROOT / "skill" / "requmexre" / "assets" / "template.json"


def run(*arguments):
    return subprocess.run(
        [sys.executable, str(CLI), *map(str, arguments)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def write(tmp_path, name, document):
    path = tmp_path / name
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_default_run_checks_the_fixtures_and_the_template():
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "requmexre v1.0" in result.stdout
    assert "files behave as declared" in result.stdout
    assert "skill/requmexre/assets/template.json" in result.stdout


def test_single_valid_file_passes():
    result = run(CASES / "fwo.json")
    assert result.returncode == 0
    assert "PASS" in result.stdout
    assert "expected valid" in result.stdout
    assert "0 findings" in result.stdout


def test_negative_fixture_passes_when_it_reports_its_rule():
    result = run(CASES / "negative" / "r1-statement-as-question.json")
    assert result.returncode == 0
    assert "PASS" in result.stdout
    assert "expected R1" in result.stdout


def test_mismatched_expectation_fails(tmp_path, plan):
    path = write(tmp_path, "mismatch.json", {"expect": "R4", "plan": plan})
    result = run(path)
    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "0 of 1 files behave as declared; 1 do not" in result.stdout


def test_missing_file_exits_one(tmp_path):
    result = run(tmp_path / "absent.json")
    assert result.returncode == 1
    assert "file not found" in result.stdout


def test_unreadable_json_exits_one(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    result = run(path)
    assert result.returncode == 1
    assert "not readable as JSON" in result.stdout


def test_unknown_expectation_exits_one(tmp_path, plan):
    path = write(tmp_path, "unknown.json", {"expect": "R9", "plan": plan})
    result = run(path)
    assert result.returncode == 1
    assert "is not 'valid' or a rule code" in result.stdout


def test_several_files_are_reported_one_per_line():
    result = run(CASES / "fwo.json", CASES / "vub.json", TEMPLATE)
    assert result.returncode == 0
    assert result.stdout.count("PASS") == 3
    assert "3 of 3 files behave as declared" in result.stdout
