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


def test_fixtures_run_checks_the_fixtures_and_the_template():
    result = run("--fixtures")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "requmexre v1.1" in result.stdout
    assert "not your plan" in result.stdout
    assert "files behave as declared" in result.stdout
    assert "No plan of yours was checked" in result.stdout
    assert "skill/requmexre/assets/template.json" in result.stdout


def test_no_arguments_refuses_to_run_the_corpus():
    result = run()
    assert result.returncode == 2
    assert result.stdout == ""
    assert "no plan given" in result.stderr
    assert "--fixtures" in result.stderr


def test_no_arguments_with_json_returns_an_error_object():
    result = run("--json")
    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["ok"] is False
    assert "no plan given" in report["error"]


def test_fixtures_refuses_file_arguments():
    result = run("--fixtures", CASES / "fwo.json")
    assert result.returncode == 2
    assert "--fixtures takes no file arguments" in result.stderr


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


# --------------------------------------------------------------------------
# Flags: --help, --version, --json
# --------------------------------------------------------------------------


def test_version_exits_zero():
    result = run("--version")
    assert result.returncode == 0
    assert result.stdout.strip() == "requmexre v1.1"
    assert result.stderr == ""


def test_help_exits_zero_and_documents_the_flags():
    result = run("--help")
    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert "--json" in result.stdout
    assert "--version" in result.stdout
    assert "Exit status" in result.stdout


def test_unknown_option_exits_two():
    result = run("--nope")
    assert result.returncode == 2
    assert "unrecognized arguments" in result.stderr


def test_json_report_is_parseable_and_complete():
    result = run("--json", "--fixtures")
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["tool"] == "requmexre"
    assert report["version"] == "1.1"
    assert report["scope"] == "fixtures"
    assert report["ok"] is True
    assert report["failed"] == 0
    assert report["passed"] == report["total"] == len(report["files"])
    assert report["total"] >= 24
    for entry in report["files"]:
        assert {"path", "ok", "expected", "findings", "note"} <= set(entry)


def test_json_report_carries_the_rule_and_path_of_a_finding():
    result = run("--json", CASES / "negative" / "r1-statement-as-question.json")
    assert result.returncode == 0
    entry = json.loads(result.stdout)["files"][0]
    assert entry["expected"] == "R1"
    assert any(
        finding["rule"] == "R1" and finding["path"].startswith("$.questions")
        for finding in entry["findings"]
    )


def test_json_report_on_a_mismatch_exits_one(tmp_path, plan):
    path = write(tmp_path, "mismatch.json", {"expect": "R4", "plan": plan})
    result = run("--json", path)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["ok"] is False
    assert report["failed"] == 1
    assert report["files"][0]["expected"] == "R4"
    assert report["files"][0]["findings"] == []


def test_json_report_on_a_missing_file_exits_one(tmp_path):
    result = run("--json", tmp_path / "absent.json")
    assert result.returncode == 1
    entry = json.loads(result.stdout)["files"][0]
    assert entry["ok"] is False
    assert entry["expected"] is None
    assert entry["note"] == "file not found"


def test_json_report_on_unreadable_json_exits_one(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    result = run("--json", path)
    assert result.returncode == 1
    entry = json.loads(result.stdout)["files"][0]
    assert entry["note"].startswith("not readable as JSON")


def test_json_flag_does_not_print_the_banner():
    result = run("--json", CASES / "fwo.json")
    assert "requmexre v1.1 — structural" not in result.stdout


def test_json_scope_is_files_for_explicit_targets():
    result = run("--json", CASES / "fwo.json")
    assert json.loads(result.stdout)["scope"] == "files"
