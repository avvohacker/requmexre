#!/usr/bin/env python3
"""requmexre — two-layer validator.

Layer 1, structural (S1–S10): evaluates requmexre.schema.json. The schema is the
source of truth; this file implements only the JSON Schema keywords that schema
uses, and refuses any keyword it does not implement, so the two cannot drift
silently. No third-party dependency.

Layer 2, semantic (R1–R8): reads the document's own words. It runs only when the
structural layer is clean.

Usage
    python3 validate.py                             # every fixture + skill template
    python3 validate.py cases/prin.json             # one file
    python3 validate.py ../skill/requmexre/assets/template.json

Exit status is 0 when every file behaves as declared in meta.expect, 1 when one
does not, 2 when there is nothing to check.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCHEMA_PATH = HERE / "requmexre.schema.json"
CASES_DIR = HERE / "cases"
TEMPLATE_PATH = ROOT / "skill" / "requmexre" / "assets" / "template.json"

RULE_IDS = [*(f"S{i}" for i in range(1, 11)), *(f"R{i}" for i in range(1, 9))]

SEMANTIC_RULES = {
    "R1": "each question matches its declared form",
    "R2": "each completion criterion does not restate its question",
    "R3": "the gap statement does not restate the question",
    "R4": "each piece of warrant evidence is dated or identifiable",
    "R5": "results make a claim about the world, or measure something, not only outputs",
    "R6": "each falsifier differs from the claim it tests",
    "R7": "limits are not validity conditions",
    "R8": "the standpoint is declared or explicitly none, and the body agrees",
}

PARAPHRASE = 0.70


# --------------------------------------------------------------------------
# Findings
# --------------------------------------------------------------------------


class Violation:
    __slots__ = ("rule", "path", "message")

    def __init__(self, rule: str, path: str, message: str) -> None:
        self.rule = rule or "?"
        self.path = path or "$"
        self.message = message

    def __str__(self) -> str:
        return f"{self.rule}  {self.path}: {self.message}"


def _rule_of(comment):
    match = re.match(r"\s*(S(?:10|[1-9])|R[1-8])\b", comment or "")
    return match.group(1) if match else None


# --------------------------------------------------------------------------
# Layer 1 — structural: a small evaluator for the schema's keyword set
# --------------------------------------------------------------------------

KEYWORDS = {
    "$schema", "$id", "title", "description", "$comment", "$defs", "$ref",
    "type", "enum", "const", "required", "properties", "additionalProperties",
    "items", "minItems", "maxItems", "minLength", "pattern", "allOf",
    "if", "then", "else",
}
SCHEMA_MAPS = {"properties", "$defs"}
SCHEMA_VALUES = {"items", "additionalProperties", "if", "then", "else"}


def audit_keywords(schema, where="$"):
    """Refuse a schema keyword this evaluator does not implement."""
    if isinstance(schema, bool):
        return
    if not isinstance(schema, dict):
        raise SystemExit(f"schema error at {where}: expected an object or a boolean")
    for keyword, value in schema.items():
        if keyword in SCHEMA_MAPS:
            for name, subschema in value.items():
                audit_keywords(subschema, f"{where}.{keyword}.{name}")
        elif keyword in SCHEMA_VALUES:
            if isinstance(value, dict):
                audit_keywords(value, f"{where}.{keyword}")
        elif keyword == "allOf":
            for index, subschema in enumerate(value):
                audit_keywords(subschema, f"{where}.allOf[{index}]")
        elif keyword not in KEYWORDS:
            raise SystemExit(
                f"schema error: keyword {keyword!r} at {where} is not evaluated by validate.py; "
                "add it to the evaluator or remove it from the schema"
            )


def _kind(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    return type(value).__name__


def _type_ok(value, name):
    if name == "object":
        return isinstance(value, dict)
    if name == "array":
        return isinstance(value, list)
    if name == "string":
        return isinstance(value, str)
    if name == "boolean":
        return isinstance(value, bool)
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if name == "null":
        return value is None
    raise SystemExit(f"schema error: unknown type {name!r}")


def _resolve(ref, root):
    if not isinstance(ref, str) or not ref.startswith("#/"):
        raise SystemExit(f"schema error: only local references are supported, got {ref!r}")
    node = root
    for part in ref[2:].split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        try:
            node = node[key]
        except (KeyError, TypeError):
            raise SystemExit(f"schema error: unresolved reference {ref!r}")
    return node


def evaluate(instance, schema, path="$", rule=None, root=None):
    """Return the findings for instance against schema."""
    if root is None:
        root = schema
    if schema is True:
        return []
    if schema is False:
        return [Violation(rule, path, "no value is permitted here")]
    if not isinstance(schema, dict):
        raise SystemExit(f"schema error at {path}: expected an object or a boolean")

    rule = _rule_of(schema.get("$comment")) or rule
    findings = []

    if "$ref" in schema:
        findings += evaluate(instance, _resolve(schema["$ref"], root), path, rule, root)

    if "type" in schema and not _type_ok(instance, schema["type"]):
        findings.append(Violation(rule, path, f"expected {schema['type']}, found {_kind(instance)}"))
        return findings

    if "const" in schema and instance != schema["const"]:
        findings.append(Violation(rule, path, f"expected {schema['const']!r}"))
    if "enum" in schema and instance not in schema["enum"]:
        allowed = ", ".join(repr(item) for item in schema["enum"])
        findings.append(Violation(rule, path, f"expected one of {allowed}"))

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            findings.append(
                Violation(rule, path, f"shorter than {schema['minLength']} characters")
            )
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            findings.append(
                Violation(rule, path, f"does not match the pattern {schema['pattern']!r}")
            )

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            findings.append(
                Violation(rule, path, f"has {len(instance)} item(s); at least {schema['minItems']} needed")
            )
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            findings.append(
                Violation(rule, path, f"has {len(instance)} items; at most {schema['maxItems']} allowed")
            )
        if "items" in schema:
            for index, item in enumerate(instance):
                findings += evaluate(item, schema["items"], f"{path}[{index}]", rule, root)

    if isinstance(instance, dict):
        for name in schema.get("required", []):
            if name not in instance:
                findings.append(Violation(rule, path, f"missing required field {name!r}"))
        properties = schema.get("properties", {})
        extra = schema.get("additionalProperties", True)
        for name, value in instance.items():
            child = f"{path}.{name}"
            if name in properties:
                findings += evaluate(value, properties[name], child, rule, root)
            elif extra is False:
                findings.append(Violation(rule, path, f"unexpected field {name!r}"))
            elif isinstance(extra, dict):
                findings += evaluate(value, extra, child, rule, root)

    for subschema in schema.get("allOf", []):
        findings += evaluate(instance, subschema, path, rule, root)

    if "if" in schema:
        if not evaluate(instance, schema["if"], path, rule, root):
            if "then" in schema:
                findings += evaluate(instance, schema["then"], path, rule, root)
        elif "else" in schema:
            findings += evaluate(instance, schema["else"], path, rule, root)

    return findings


# --------------------------------------------------------------------------
# Layer 2 — semantic: R1–R8
# --------------------------------------------------------------------------

STOPWORDS = set(
    """a an the and or but if then than that this these those of to in on at by for
    with from into over under as is are was were be been being do does did done have
    has had not no nor so such it its their they we you he she them our your his her
    who whom whose which what when where why how whether there here also more most
    less least other another any all each both some only very can could should would
    may might must will shall about after before between among during through within
    without upon against per via""".split()
)

INTERROGATIVE = re.compile(
    r"^(?:what|how|why|whether|which|who|whom|whose|when|where|to what|under what|"
    r"in what|for what|does|do|did|is|are|was|were|can|could|should|would|will|"
    r"may|might)\b",
    re.IGNORECASE,
)

DATED = re.compile(r"\b(?:19|20)\d{2}\b")
IDENTIFIER = re.compile(
    r"(?:doi\.org|doi:|\b10\.\d{4,9}/|arxiv[:/ ]|isbn|https?://|pmid|handle\.net)",
    re.IGNORECASE,
)


def content_words(text):
    words = re.findall(r"[0-9a-zà-öø-ÿ]+", str(text).lower())
    return [word for word in words if len(word) > 2 and word not in STOPWORDS]


def overlap(first, second):
    """Shared content words over the smaller set: catches one text swallowing the other."""
    left, right = set(content_words(first)), set(content_words(second))
    if not left or not right:
        return 0.0
    return len(left & right) / min(len(left), len(right))


def _normalise(text):
    return re.sub(r"\W+", " ", str(text).lower()).strip()


def check_semantics(doc):
    findings = []
    questions = doc.get("questions", {}) or {}
    primary = questions.get("primary", {}) or {}
    secondary = questions.get("secondary") or []
    method = doc.get("method", {})
    meta = doc.get("meta", {})

    numbered = [("$.questions.primary", primary)]
    numbered += [
        (f"$.questions.secondary[{index}]", item)
        for index, item in enumerate(secondary)
    ]

    # R1 — each question matches its declared form
    for path, question in numbered:
        text = str(question.get("text", "")).strip()
        form = question.get("form")
        reads_as_question = text.endswith("?") or bool(INTERROGATIVE.match(text))
        if form == "interrogative" and not reads_as_question:
            findings.append(
                Violation(
                    "R1",
                    f"{path}.text",
                    "declared interrogative but not written as a question: end with '?' "
                    "or open with an interrogative word",
                )
            )
        elif form == "objective" and reads_as_question:
            findings.append(
                Violation(
                    "R1",
                    f"{path}.text",
                    "declared objective but written as a question",
                )
            )

    # R2 — each completion criterion is not its own question again
    for path, question in numbered:
        criterion = question.get("completion_criterion")
        if not criterion or str(criterion).strip().lower() == "none":
            continue
        ratio = overlap(criterion, question.get("text", ""))
        if ratio >= PARAPHRASE:
            findings.append(
                Violation(
                    "R2",
                    f"{path}.completion_criterion",
                    f"reuses {round(ratio * 100)} per cent of its question's content words; "
                    "state what would count as an answer instead",
                )
            )

    # R3 — the gap statement is not the primary question again
    gap = doc.get("warrant", {}).get("gap_statement", "")
    ratio = overlap(gap, primary.get("text", ""))
    if ratio >= PARAPHRASE:
        findings.append(
            Violation(
                "R3",
                "$.warrant.gap_statement",
                f"reuses {round(ratio * 100)} per cent of the question's content words; "
                "state what is missing from the literature instead",
            )
        )

    # R4 — evidence is dated or identifiable
    for index, entry in enumerate(doc.get("warrant", {}).get("evidence", [])):
        if not (DATED.search(entry) or IDENTIFIER.search(entry)):
            findings.append(
                Violation(
                    "R4",
                    f"$.warrant.evidence[{index}]",
                    f"no year and no identifier, so the source cannot be found: {entry!r}",
                )
            )

    # R5 — results are not only outputs
    results = doc.get("results") or []
    kinds = [item.get("kind") for item in results if isinstance(item, dict)]
    if results and kinds and all(kind == "output" for kind in kinds):
        findings.append(
            Violation(
                "R5",
                "$.results",
                "only outputs: at least one result must be a claim (hypothesis or expected finding) or an outcome",
            )
        )

    # R6 — a falsifier says something the claim does not
    for index, item in enumerate(results):
        if not isinstance(item, dict) or "falsifier" not in item:
            continue
        ratio = overlap(item.get("falsifier", ""), item.get("claim", ""))
        if ratio >= PARAPHRASE:
            findings.append(
                Violation(
                    "R6",
                    f"$.results[{index}].falsifier",
                    f"reuses {round(ratio * 100)} per cent of the claim's content words; "
                    "state what would show the claim false",
                )
            )

    # R7 — limits and validity conditions are different things
    conditions = method.get("validity_conditions") or []
    limits = method.get("limits") or []
    for index, limit in enumerate(limits):
        for other, condition in enumerate(conditions):
            if _normalise(limit) == _normalise(condition) or overlap(limit, condition) >= PARAPHRASE:
                findings.append(
                    Violation(
                        "R7",
                        f"$.method.limits[{index}]",
                        f"restates method.validity_conditions[{other}]; "
                        "a condition under which the finding holds is not a limit",
                    )
                )
                break

    # R8 — the declared standpoint and the body agree
    standpoint = doc.get("standpoint")
    declared = meta.get("standpoint")
    if declared == "none":
        if standpoint is not None:
            findings.append(
                Violation(
                    "R8",
                    "$.standpoint",
                    "present while meta.standpoint is 'none'; remove it or declare the standpoint",
                )
            )
    elif declared == "declared":
        if standpoint is None:
            findings.append(
                Violation(
                    "R8",
                    "$.standpoint",
                    "missing while meta.standpoint is 'declared'",
                )
            )
        else:
            for field in ("normative_premises", "criteria"):
                if not standpoint.get(field):
                    findings.append(
                        Violation(
                            "R8",
                            f"$.standpoint.{field}",
                            "empty; a declared standpoint needs at least one entry",
                        )
                    )

    return findings


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------


def declared_expectation(doc):
    meta = doc.get("meta") if isinstance(doc, dict) else None
    return meta.get("expect") if isinstance(meta, dict) else None


def display(path):
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def default_targets():
    targets = sorted(CASES_DIR.rglob("*.json"))
    if TEMPLATE_PATH.exists():
        targets.append(TEMPLATE_PATH)
    return targets


def check_file(path, schema):
    path = Path(path)
    if not path.exists():
        return False, None, [], "file not found"
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        return False, None, [], f"not readable as JSON: {error}"

    expect = declared_expectation(doc)
    findings = evaluate(doc, schema, root=schema)
    if not findings:
        findings = check_semantics(doc)

    codes = sorted({finding.rule for finding in findings})
    if expect is None:
        return False, None, findings, "meta.expect missing"
    if expect == "valid":
        ok = not findings
    elif expect in RULE_IDS:
        ok = expect in codes
    else:
        ok = False
        findings.append(
            Violation("?", "$.meta.expect", f"{expect!r} is not 'valid' or a rule code")
        )
        codes = sorted({finding.rule for finding in findings})

    note = "0 findings" if not findings else ", ".join(codes)
    return ok, expect, findings, note


def main(argv):
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"cannot read {SCHEMA_PATH}: {error}", file=sys.stderr)
        return 2
    audit_keywords(schema)

    targets = [Path(argument) for argument in argv] or default_targets()
    if not targets:
        print("no files to check", file=sys.stderr)
        return 2

    width = max(len(display(target)) for target in targets)
    failures = 0
    print("requmexre v0.3 — structural S1–S10, semantic R1–R8\n")

    for target in targets:
        ok, expect, findings, note = check_file(target, schema)
        if not ok:
            failures += 1
        label = "PASS" if ok else "FAIL"
        expected = expect if expect else "—"
        print(f"{label}  {display(target):<{width}}  expected {expected:<6}  {note}")
        for finding in findings:
            print(f"      {finding}")

    print()
    total = len(targets)
    if failures:
        print(f"{total - failures} of {total} files behave as declared; {failures} do not.")
        return 1
    print(f"{total} of {total} files behave as declared.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
