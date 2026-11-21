"""The Question component's answer-type vocabulary is pinned here.

The funder forms ask for objectives or questions; they do not prescribe an
answer type. `answer_type` is the model's vocabulary, and only comparative and
evaluative questions impose a structural obligation. These tests accept all
eleven values and reject the two cross-type combinations that S4 forbids.
"""

from __future__ import annotations

import copy

import pytest

TYPES = [
    "descriptive",
    "exploratory",
    "comparative",
    "causal",
    "evaluative",
    "methodological",
    "synthesis",
    "mechanistic",
    "feasibility",
    "validation",
    "other",
]
OTHER = [kind for kind in TYPES if kind not in ("comparative", "evaluative")]


def codes(findings):
    return {finding.rule for finding in findings}


def structurally_invalid(v, schema, doc):
    return "S4" in codes(v.evaluate(doc, schema, root=schema))


def question(kind, **overrides):
    q = {
        "text": "How does remote work change overtime in small firms?",
        "form": "interrogative",
        "answer_type": kind,
        "scope": "Small firms in Belgium, 2027 to 2029.",
        "completion_criterion": (
            "The question is answered when overtime hours are estimated before "
            "and after adoption."
        ),
    }
    if kind == "comparative":
        q["tertium_comparationis"] = "overtime hours per employee"
    elif kind == "evaluative":
        q["criteria"] = ["the change in overtime hours"]
        q["operationalisation"] = (
            "Overtime hours per employee, estimated before and after adoption."
        )
    q.update(overrides)
    return q


def plan_with(plan, kind, **overrides):
    doc = copy.deepcopy(plan)
    doc["questions"]["primary"] = question(kind, **overrides)
    return doc


@pytest.mark.parametrize("kind", TYPES)
def test_every_answer_type_is_accepted(v, schema, plan, kind):
    doc = plan_with(plan, kind)

    assert v.evaluate(doc, schema, root=schema) == []
    assert v.check_semantics(doc) == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("criteria", ["the change in overtime hours"]),
        ("operationalisation", "Overtime hours per employee."),
    ],
)
def test_a_comparative_question_cannot_carry_evaluative_fields(
    v, schema, plan, field, value
):
    doc = plan_with(plan, "comparative", **{field: value})

    assert structurally_invalid(v, schema, doc)


def test_an_evaluative_question_cannot_carry_a_tertium(v, schema, plan):
    doc = plan_with(
        plan, "evaluative", tertium_comparationis="overtime hours per employee"
    )

    assert structurally_invalid(v, schema, doc)


def test_other_types_cannot_carry_any_conditional_field(v, schema, plan):
    values = {
        "tertium_comparationis": "overtime hours per employee",
        "criteria": ["the change in overtime hours"],
        "operationalisation": "Overtime hours per employee.",
    }
    for kind in OTHER:
        for field, value in values.items():
            doc = plan_with(plan, kind, **{field: value})
            assert structurally_invalid(v, schema, doc), (kind, field)


def test_both_forms_are_accepted_when_the_text_matches(v, schema, plan):
    doc = plan_with(plan, "descriptive")
    doc["questions"]["primary"].update(
        text="This study estimates how remote work changes overtime in small firms.",
        form="objective",
    )

    assert v.evaluate(doc, schema, root=schema) == []
    assert v.check_semantics(doc) == []


def test_a_secondary_question_follows_the_same_conditionals(v, schema, plan):
    doc = copy.deepcopy(plan)
    doc["questions"]["secondary"] = [
        question("evaluative"),
        question("comparative"),
    ]

    assert v.evaluate(doc, schema, root=schema) == []
    assert v.check_semantics(doc) == []

    invalid = copy.deepcopy(doc)
    invalid["questions"]["secondary"][0]["tertium_comparationis"] = "overtime hours"
    assert structurally_invalid(v, schema, invalid)


def test_the_vocabulary_is_the_documented_eleven(schema):
    enum = schema["$defs"]["question"]["properties"]["answer_type"]["enum"]

    assert enum == TYPES
