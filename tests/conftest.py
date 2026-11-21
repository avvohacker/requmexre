"""Shared fixtures for the requmexre test suite.

validate.py lives in schema/ and is run as a script, not installed as a package.
Putting that directory on sys.path lets the tests call the same functions the
CLI calls, so a rule is tested where it is implemented.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "schema"))

import validate  # noqa: E402


@pytest.fixture(scope="session")
def v():
    return validate


@pytest.fixture(scope="session")
def schema(v):
    return json.loads(v.SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def plan():
    """A plan with no findings; each test mutates a deep copy of it."""
    return {
        "meta": {
            "standpoint": "none",
            "funder": "none",
            "title": "Remote work and overtime in small firms",
            "version": "0.1",
            "date": "2026-11-20",
        },
        "questions": {
            "primary": {
                "text": "How does the frequency of remote work change overtime hours in small firms?",
                "form": "interrogative",
                "answer_type": "descriptive",
                "scope": "Small firms in Belgium with 10 to 49 employees, 2027 to 2029.",
                "completion_criterion": (
                    "The question is answered once overtime hours per employee are "
                    "estimated before and after adoption and compared with non-adopting firms."
                ),
            }
        },
        "method": {
            "approach": "Difference-in-differences on payroll records.",
            "sources": [
                {
                    "kind": "data",
                    "description": "Payroll records, 2025-2029, social secretariats",
                }
            ],
            "procedure": (
                "Match adopting and non-adopting firms on sector and size; estimate "
                "overtime hours per employee; test for pre-trends."
            ),
            "validity_conditions": [
                "Firms are observed for two years on either side of adoption"
            ],
            "limits": ["The design does not cover firms with fewer than 10 employees"],
        },
        "results": [
            {
                "claim": (
                    "Overtime hours per employee fall after adoption and fall further "
                    "where the week is shortened without a pay cut."
                ),
                "kind": "expected_finding",
                "falsifier": (
                    "Overtime hours stay within one standard error of their pre-adoption "
                    "level in adopting firms and in the matched comparison."
                ),
                "evidence_needed": "Payroll records for adopting and matched non-adopting firms.",
            }
        ],
        "warrant": {
            "gap_statement": (
                "Payroll records and remote-work surveys are held by different agencies, "
                "so the association has not been estimated for Belgium."
            ),
            "evidence": ["City of Ghent payroll records, 2025"],
        },
    }
