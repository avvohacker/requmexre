"""Rule-level tests for the two layers.

S1–S10 are exercised through the schema evaluator, R1–R8 through check_semantics.
The fixtures in schema/cases/ are also checked end to end, but the crafted
documents below pin each rule's trigger and the edges that must stay quiet.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import validate

ROOT = Path(__file__).resolve().parents[1]
CASES = sorted((ROOT / "schema" / "cases").rglob("*.json"))
TEMPLATE = ROOT / "skill" / "requmexre" / "assets" / "template.json"


def codes(findings):
    return {finding.rule for finding in findings}


def structural(v, schema, plan):
    return v.evaluate(plan, schema, root=schema)


def semantic(v, plan):
    return v.check_semantics(plan)


def label(path):
    return str(path.relative_to(ROOT))


# --------------------------------------------------------------------------
# The fixtures and the template, end to end
# --------------------------------------------------------------------------


@pytest.mark.parametrize("path", CASES + [TEMPLATE], ids=label)
def test_every_fixture_behaves_as_declared(v, schema, path):
    ok, expect, findings, note = v.check_file(path, schema)
    assert ok, f"{label(path)}: expected {expect}, got {note}: {[str(f) for f in findings]}"


@pytest.mark.parametrize(
    "path", [p for p in CASES if p.parent.name == "negative"], ids=label
)
def test_negative_fixture_reports_its_rule(v, schema, path):
    doc = json.loads(path.read_text(encoding="utf-8"))
    ok, expect, findings, _ = v.check_file(path, schema)
    assert ok
    assert expect in v.RULE_IDS, f"{label(path)}: {expect!r} is not a rule code"
    assert expect in codes(findings), f"{label(path)}: {expect} not among {sorted(codes(findings))}"


@pytest.mark.parametrize(
    "path", [p for p in CASES if p.parent.name != "negative"], ids=label
)
def test_positive_fixture_has_no_findings(v, schema, path):
    plan = json.loads(path.read_text(encoding="utf-8"))
    assert structural(v, schema, plan) == []
    assert semantic(v, plan) == []


def test_skill_template_has_no_findings(v, schema):
    plan = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    assert structural(v, schema, plan) == []
    assert semantic(v, plan) == []


@pytest.mark.parametrize("path", CASES, ids=label)
def test_every_fixture_is_readable_json(path):
    assert isinstance(json.loads(path.read_text(encoding="utf-8")), dict)


def test_schema_uses_only_keywords_the_evaluator_implements(schema):
    validate.audit_keywords(schema)


def test_base_document_is_clean(v, schema, plan):
    assert structural(v, schema, plan) == []
    assert semantic(v, plan) == []


# --------------------------------------------------------------------------
# Layer 1 — S1–S10
# --------------------------------------------------------------------------

STRUCTURAL_CASES = [
    (lambda p: p.pop("warrant"), "S1"),
    (lambda p: p.update(registration={"doi": "10.1000/xyz"}), "S1"),
    (lambda p: p.pop("meta"), "S1"),
    (lambda p: p["meta"].update(funder="other"), "S2"),
    (lambda p: p["meta"].update(funder="fwo", scheme="FWO"), "S2"),
    (lambda p: p["meta"].update(standpoint="maybe"), "S2"),
    (lambda p: p["meta"].update(version="1"), "S2"),
    (lambda p: p["meta"].update(date="20-11-2026"), "S2"),
    (lambda p: p["questions"]["primary"].pop("scope"), "S3"),
    (lambda p: p["questions"]["primary"].pop("answer_type"), "S3"),
    (lambda p: p["questions"]["primary"].update(answer_type="comparative"), "S4"),
    (lambda p: p["questions"]["primary"].update(answer_type="evaluative"), "S4"),
    (lambda p: p["questions"]["primary"].update(criteria=["fit"]), "S4"),
    (lambda p: p["method"].update(sources=[]), "S5"),
    (lambda p: p["method"]["sources"][0].update(kind="interview"), "S5"),
    (lambda p: p["method"].update(limits="many"), "S5"),
    (lambda p: p["method"].update(validity_conditions="observed twice"), "S5"),
    (lambda p: p["method"].update(risks=[]), "S5"),
    (lambda p: p["method"].update(risks=[{"risk": "Attrition"}]), "S5"),
    (lambda p: p["method"].update(risks=[{"risk": " ", "mitigation": "Oversample"}]), "S10"),
    (
        lambda p: p["method"].update(
            risks=[{"risk": "Attrition", "mitigation": "Oversample", "owner": "PI"}]
        ),
        "S5",
    ),
    (lambda p: p.update(results=[]), "S6"),
    (lambda p: p["results"][0].pop("kind"), "S6"),
    (lambda p: p["results"][0].pop("falsifier"), "S7"),
    (lambda p: p["results"][0].update(kind="outcome"), "S7"),
    (lambda p: p["results"][0].update(kind="output"), "S7"),
    (lambda p: p["warrant"].update(evidence=[]), "S8"),
    (lambda p: p["warrant"].pop("gap_statement"), "S8"),
    (lambda p: p.update(standpoint={"normative_premises": ["fairness"]}), "S9"),
    (lambda p: p["questions"]["primary"].update(text="   "), "S10"),
    (lambda p: p["warrant"]["evidence"].__setitem__(0, ""), "S10"),
]


@pytest.mark.parametrize("mutate, rule", STRUCTURAL_CASES)
def test_structural_rule_fires(v, schema, plan, mutate, rule):
    doc = copy.deepcopy(plan)
    mutate(doc)
    findings = structural(v, schema, doc)
    assert rule in codes(findings), f"{rule} missing from {[str(f) for f in findings]}"


def test_secondary_question_needs_only_text_and_form(v, schema, plan):
    plan["questions"]["secondary"] = [
        {"text": "Which sectors adopt first?", "form": "interrogative"}
    ]
    assert structural(v, schema, plan) == []
    assert semantic(v, plan) == []


def test_secondary_question_cannot_be_empty(v, schema, plan):
    plan["questions"]["secondary"] = []
    assert "S3" in codes(structural(v, schema, plan))


def test_method_risks_are_optional_and_accepted(v, schema, plan):
    plan["method"]["risks"] = [
        {
            "risk": "Attrition above 15 per cent per wave.",
            "mitigation": "Oversample and follow movers.",
        }
    ]
    assert structural(v, schema, plan) == []
    assert semantic(v, plan) == []


def test_results_are_required_when_no_funder_is_named(v, schema, plan):
    plan.pop("results")
    plan["meta"].pop("funder")
    assert "S6" in codes(structural(v, schema, plan))


def test_results_are_required_for_a_funder_with_a_results_section(v, schema, plan):
    plan.pop("results")
    plan["meta"]["funder"] = "fwo"
    assert "S6" in codes(structural(v, schema, plan))


def test_results_are_required_for_an_unknown_funder(v, schema, plan):
    plan.pop("results")
    plan["meta"].update(funder="other", scheme="ERC Starting Grant")
    assert "S6" in codes(structural(v, schema, plan))


def test_dfg_without_results_is_valid(v, schema, plan):
    plan.pop("results")
    plan["meta"]["funder"] = "dfg"
    assert structural(v, schema, plan) == []
    assert semantic(v, plan) == []


def test_snsf_without_results_is_valid(v, schema, plan):
    plan.pop("results")
    plan["meta"]["funder"] = "snsf"
    assert structural(v, schema, plan) == []
    assert semantic(v, plan) == []


def test_dfg_exemption_does_not_allow_an_empty_results_list(v, schema, plan):
    plan["meta"]["funder"] = "dfg"
    plan["results"] = []
    assert "S6" in codes(structural(v, schema, plan))


# --------------------------------------------------------------------------
# Layer 2 — R1–R8
# --------------------------------------------------------------------------

SEMANTIC_CASES = [
    (
        lambda p: p["questions"]["primary"].update(
            text="This project measures overtime in small firms."
        ),
        "R1",
    ),
    (lambda p: p["questions"]["primary"].update(form="objective"), "R1"),
    (
        lambda p: p["questions"]["primary"].update(
            completion_criterion=p["questions"]["primary"]["text"]
        ),
        "R2",
    ),
    (
        lambda p: p["warrant"].update(
            gap_statement=p["questions"]["primary"]["text"]
        ),
        "R3",
    ),
    (
        lambda p: p["warrant"].update(
            evidence=["Payroll records from the social secretariats"]
        ),
        "R4",
    ),
    (lambda p: p.update(results=[{"claim": "A dataset.", "kind": "output"}]), "R5"),
    (
        lambda p: p["results"][0].update(
            falsifier=p["results"][0]["claim"]
        ),
        "R6",
    ),
    (
        lambda p: p["method"].update(limits=list(p["method"]["validity_conditions"])),
        "R7",
    ),
    (lambda p: p["meta"].update(standpoint="declared"), "R8"),
    (
        lambda p: (
            p["meta"].update(standpoint="none"),
            p.update(
                standpoint={"normative_premises": ["fairness"], "criteria": ["fit"]}
            ),
        ),
        "R8",
    ),
    (
        lambda p: (
            p["meta"].update(standpoint="declared"),
            p.update(standpoint={"normative_premises": ["fairness"], "criteria": []}),
        ),
        "R8",
    ),
]


@pytest.mark.parametrize("mutate, rule", SEMANTIC_CASES)
def test_semantic_rule_fires(v, plan, mutate, rule):
    doc = copy.deepcopy(plan)
    mutate(doc)
    findings = semantic(v, doc)
    assert rule in codes(findings), f"{rule} missing from {[str(f) for f in findings]}"


def test_criterion_word_none_is_skipped(v, plan):
    plan["questions"]["primary"]["completion_criterion"] = "none"
    assert semantic(v, plan) == []


def test_limits_word_none_is_skipped(v, plan):
    plan["method"]["limits"] = "none"
    assert semantic(v, plan) == []


def test_evidence_with_doi_only_is_identifiable(v, plan):
    plan["warrant"]["evidence"] = ["10.1000/xyz123"]
    assert semantic(v, plan) == []


def test_evidence_with_url_only_is_identifiable(v, plan):
    plan["warrant"]["evidence"] = ["https://example.org/report"]
    assert semantic(v, plan) == []


def test_output_beside_an_outcome_is_allowed(v, plan):
    plan["results"].append({"claim": "A dataset of payroll records.", "kind": "output"})
    assert semantic(v, plan) == []


def test_interrogative_word_is_enough_without_a_question_mark(v, plan):
    plan["questions"]["primary"]["text"] = "Does remote work change overtime hours?"
    assert "R1" not in codes(semantic(v, plan))
    plan["questions"]["primary"]["text"] = "Does remote work change overtime hours"
    assert "R1" not in codes(semantic(v, plan))


def test_paraphrase_threshold_is_seventy_per_cent(v, plan):
    question = "alpha beta gamma delta epsilon zeta eta theta iota kappa"
    plan["questions"]["primary"]["text"] = question
    plan["questions"]["primary"]["form"] = "objective"
    plan["questions"]["primary"]["completion_criterion"] = (
        "alpha beta gamma delta epsilon zeta eta quark gluon boson lepton"
    )
    assert "R2" in codes(semantic(v, plan))
    plan["questions"]["primary"]["completion_criterion"] = (
        "alpha beta gamma delta epsilon zeta quark gluon boson lepton"
    )
    assert "R2" not in codes(semantic(v, plan))


def test_overlap_is_one_for_the_same_text(v):
    assert v.overlap("overtime hours fall", "overtime hours fall") == 1.0


def test_overlap_ignores_stopwords_and_short_tokens(v):
    assert v.overlap("the of and", "overtime") == 0.0
    assert v.overlap("a b c", "overtime") == 0.0


def test_every_rule_code_has_a_trigger_here():
    covered = {rule for _, rule in STRUCTURAL_CASES}
    covered |= {rule for _, rule in SEMANTIC_CASES}
    assert covered == set(validate.RULE_IDS)
