"""The mapping data must agree with the tables it was ported from.

`schema/mappings.json` drives `schema/render.py`; `references/mappings.md` is the
same six tables for a reader. This suite keeps them one source in two forms: a
section added to one without the other fails here. It also checks the property
the data exists for — every field of the model has a home, or a declared reason
why a funder has no place for it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import render

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "schema" / "mappings.json"
DOC = ROOT / "skill" / "requmexre" / "references" / "mappings.md"
SCHEMA = ROOT / "schema" / "requmexre.schema.json"

SIX = ["fwo", "prin", "vub", "horizon", "dfg", "snsf"]
MODEL_FIELDS = set(render.MODEL_FIELDS)


@pytest.fixture(scope="module")
def mapping():
    return json.loads(DATA.read_text(encoding="utf-8"))


def funders(mapping):
    return {funder["id"]: funder for funder in mapping["funders"]}


def mapped_fields(funder):
    fields = {field for section in funder["sections"] for field in section["fields"]}
    # `method` renders its procedure too; a separate work-plan section refines
    # the same field rather than adding one.
    if "method" in fields:
        fields.add("method.procedure")
    return fields


def test_the_six_funders_match_the_schema_enum(mapping):
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    enum = schema["$defs"]["meta"]["properties"]["funder"]["enum"]
    assert [entry["id"] for entry in mapping["funders"]] == SIX
    assert set(SIX) <= set(enum)


def test_sections_have_known_fields_and_unique_names(mapping):
    for funder in mapping["funders"]:
        names = [section["name"] for section in funder["sections"]]
        assert len(names) == len(set(names)), funder["id"]
        for section in funder["sections"]:
            assert set(section["fields"]) <= MODEL_FIELDS, (funder["id"], section["name"])


def test_every_model_field_has_a_home_or_a_declared_absence(mapping):
    for funder in mapping["funders"]:
        mapped = mapped_fields(funder)
        absent = funder.get("absent", {})
        missing = MODEL_FIELDS - mapped - set(absent)
        assert not missing, f"{funder['id']} leaves {sorted(missing)} unplaced"
        for field, reason in absent.items():
            assert field not in mapped, f"{funder['id']} maps and drops {field}"
            assert reason.strip(), f"{funder['id']} gives no reason for {field}"


def test_outputs_are_delivered_in_exactly_one_section(mapping):
    for funder in mapping["funders"]:
        delivering = [
            section["name"] for section in funder["sections"] if section.get("delivers")
        ]
        assert len(delivering) == 1, f"{funder['id']}: {delivering}"


def test_a_section_without_fields_says_why(mapping):
    for funder in mapping["funders"]:
        for section in funder["sections"]:
            if not section["fields"]:
                assert section.get("outside_model", "").strip(), (
                    funder["id"],
                    section["name"],
                )


def test_each_funder_uses_a_language_the_renderer_has(mapping):
    for funder in mapping["funders"]:
        assert funder["language"] in render.PHRASES
    assert funders(mapping)["prin"]["language"] == "en"


def markdown_rows(text):
    """Return the (section, fields) rows of the six '| Section | Fields |' tables."""
    rows = []
    in_table = False
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("| Section |"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                in_table = False
                continue
            if set(line) <= set("|-: "):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) < 2:
                continue
            rows.append((cells[0], re.findall(r"`([^`]+)`", cells[1])))
    return rows


def test_markdown_tables_match_the_data(mapping):
    expected = [
        (section["name"], section["fields"])
        for funder in mapping["funders"]
        for section in funder["sections"]
    ]
    assert markdown_rows(DOC.read_text(encoding="utf-8")) == expected
