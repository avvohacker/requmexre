"""The Pages build refuses a schema whose $id is outside the site URL.

A schema published at a path other than its $id is unusable, so build.py exits
after writing the page when the two disagree. This test runs the real script on
a temporary copy of its build inputs, with the $id moved to another host.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "site" / "build.py"
INPUTS = [
    "README.md",
    "SOURCES.md",
    "schema/RULES.md",
    "schema/requmexre.schema.json",
]


def copy_inputs(tmp_path):
    """Lay out a repository root the build can read, and return its schema path."""
    (tmp_path / "site").mkdir()
    shutil.copy2(BUILD, tmp_path / "site" / "build.py")
    for name in INPUTS:
        source = ROOT / name
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    shutil.copytree(ROOT / "schema" / "archive", tmp_path / "schema" / "archive")
    return tmp_path / "schema" / "requmexre.schema.json"


def run_build(root):
    return subprocess.run(
        [sys.executable, str(root / "site" / "build.py")],
        capture_output=True,
        text=True,
        cwd=root,
    )


def test_build_exits_when_the_schema_id_is_outside_the_site(tmp_path):
    schema_path = copy_inputs(tmp_path)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["$id"] = "https://example.org/schema/1.0/requmexre.schema.json"
    schema_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")

    result = run_build(tmp_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "does not start with" in result.stderr
    assert "https://example.org/schema/1.0/requmexre.schema.json" in result.stderr


def test_build_publishes_the_current_and_archived_schemas(tmp_path):
    copy_inputs(tmp_path)

    result = run_build(tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    cases = [
        (
            "schema/1.2/requmexre.schema.json",
            "https://avvohacker.github.io/requmexre/schema/1.2/requmexre.schema.json",
        ),
        (
            "schema/1.1/requmexre.schema.json",
            "https://avvohacker.github.io/requmexre/schema/1.1/requmexre.schema.json",
        ),
        (
            "schema/1.0/requmexre.schema.json",
            "https://avvohacker.github.io/requmexre/schema/1.0/requmexre.schema.json",
        ),
    ]
    for relative, expected in cases:
        path = tmp_path / "site" / "_out" / relative
        assert path.is_file(), relative
        assert json.loads(path.read_text(encoding="utf-8"))["$id"] == expected
