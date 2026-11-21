#!/usr/bin/env python3
"""requmexre — render a plan into the sections of a funder.

The six section tables are data, not code: mappings.json maps each funder's
sections to fields of the plan. This file turns that mapping into Markdown. It
copies the plan's prose and never rewrites it, never translates it (PRIN's
section names and connectives are Italian; the plan's own wording is kept) and
never renders a falsifier, `evidence_needed` or an output as an expected result.

A plan must name one of the six funders. `none`, an absent funder and `other`
have no table: the first two are funder-agnostic, the third is rendered by hand
from the call's own form.

Usage
    python3 render.py plan.json                 # the draft, to stdout
    python3 render.py plan.json --out draft.md  # the draft, to a file
    python3 render.py --version

The renderer refuses a plan the validator rejects (exit 1), exits 2 on bad usage
or on a funder with no table, and warns on stderr when a field present in the
plan has no section in that funder's table.

    python3 render.py cases/prin.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import validate

HERE = Path(__file__).resolve().parent
# The renderer ships twice: canonical in schema/ and bundled in
# skill/requmexre/scripts/ for an installed skill. The fallback lets the same
# bytes find the mapping data in either layout.
MAPPINGS_PATH = HERE / "mappings.json"
if not MAPPINGS_PATH.exists():
    MAPPINGS_PATH = HERE.parent / "assets" / "mappings.json"

VERSION = "1.0"

MODEL_FIELDS = (
    "warrant",
    "questions.primary",
    "questions.secondary",
    "method",
    "method.procedure",
    "results",
    "standpoint",
)

PHRASES = {
    "en": {
        "scope": "Scope",
        "criterion": "What would count as an answer",
        "comparison": "The comparison is made on",
        "criteria": "Criteria",
        "operationalisation": "Operationalisation",
        "secondary": "Secondary questions and objectives",
        "sources": "Sources",
        "validity": "Validity conditions",
        "limits": "Limits",
        "limits_none": "The plan declares no limits.",
        "limits_absent": "The plan does not state limits.",
        "premises": "Normative premises",
        "standpoint_none": "The plan declares no normative standpoint.",
        "standpoint_undeclared": "The plan does not declare a standpoint.",
        "no_results": "The plan states no results.",
        "outputs": "The procedure delivers",
        "measure": "Measured as",
        "kinds": {
            "hypothesis": "Hypothesis",
            "expected_finding": "Expected finding",
            "outcome": "Outcome",
        },
        "source_kinds": {
            "data": "data",
            "literature": "literature",
            "participants": "participants",
            "corpus": "corpus",
        },
    },
    "it": {
        "scope": "Ambito",
        "criterion": "Costituirebbe una risposta",
        "comparison": "Il confronto avviene su",
        "criteria": "Criteri",
        "operationalisation": "Operazionalizzazione",
        "secondary": "Obiettivi e domande secondarie",
        "sources": "Fonti",
        "validity": "Condizioni di validità",
        "limits": "Limiti",
        "limits_none": "Il piano dichiara l'assenza di limiti.",
        "limits_absent": "Il piano non indica limiti.",
        "premises": "Premesse normative",
        "standpoint_none": "Il piano dichiara l'assenza di una prospettiva normativa.",
        "standpoint_undeclared": "Il piano non dichiara una prospettiva normativa.",
        "no_results": "Il piano non indica risultati.",
        "outputs": "La procedura produce",
        "measure": "Misurato come",
        "kinds": {
            "hypothesis": "Ipotesi",
            "expected_finding": "Risultato atteso",
            "outcome": "Esito",
        },
        "source_kinds": {
            "data": "dati",
            "literature": "letteratura",
            "participants": "partecipanti",
            "corpus": "corpus",
        },
    },
}


class RenderError(Exception):
    """A plan or a mapping that cannot be rendered."""


# --------------------------------------------------------------------------
# Mapping data
# --------------------------------------------------------------------------


def load_mappings(path=None):
    path = Path(path) if path is not None else MAPPINGS_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RenderError(f"cannot read {path}: {error}")

    funders = data.get("funders")
    if not isinstance(funders, list) or not funders:
        raise RenderError(f"{path} has no funders")

    seen = set()
    for funder in funders:
        funder_id = funder.get("id")
        if not funder_id or funder_id in seen:
            raise RenderError(f"{path}: missing or duplicate funder id {funder_id!r}")
        seen.add(funder_id)
        if funder.get("language") not in PHRASES:
            raise RenderError(f"{path}: {funder_id} has no known language")
        delivered = 0
        for section in funder.get("sections") or []:
            if not section.get("name"):
                raise RenderError(f"{path}: {funder_id} has a section without a name")
            for field in section.get("fields") or []:
                if field not in MODEL_FIELDS:
                    raise RenderError(
                        f"{path}: {funder_id} maps unknown field {field!r}"
                    )
            if section.get("delivers"):
                delivered += 1
        if delivered > 1:
            raise RenderError(f"{path}: {funder_id} delivers outputs in more than one section")
        for field in funder.get("absent") or {}:
            if field not in MODEL_FIELDS:
                raise RenderError(f"{path}: {funder_id} declares unknown field {field!r}")
    return data


def funder_of(data, funder_id):
    for funder in data["funders"]:
        if funder["id"] == funder_id:
            return funder
    raise RenderError(
        f"{funder_id!r} has no section table; the six mapped funders are "
        + ", ".join(entry["id"] for entry in data["funders"])
    )


# --------------------------------------------------------------------------
# Sentence assembly
# --------------------------------------------------------------------------


def _end(text):
    text = str(text).strip()
    if not text:
        return ""
    return text if text.endswith((".", "?", "!")) else text + "."


def _labelled(label, value):
    return _end(f"{label}: {value}")


def _listed(label, items):
    items = [str(item).strip() for item in items if str(item).strip()]
    return _end(f"{label}: " + "; ".join(items)) if items else ""


def _cited(text, evidence):
    text = str(text).strip()
    evidence = [entry for entry in evidence or [] if entry]
    if not evidence:
        return _end(text)
    citation = "(" + "; ".join(evidence) + ")"
    if text.endswith("."):
        return f"{text[:-1]} {citation}."
    return f"{text} {citation}."


def _question(primary, phrases):
    parts = [_end(primary.get("text", ""))]
    if primary.get("tertium_comparationis"):
        parts.append(_labelled(phrases["comparison"], primary["tertium_comparationis"]))
    if primary.get("criteria"):
        parts.append(_listed(phrases["criteria"], primary["criteria"]))
    if primary.get("operationalisation"):
        parts.append(
            _labelled(phrases["operationalisation"], primary["operationalisation"])
        )
    if primary.get("scope"):
        parts.append(_labelled(phrases["scope"], primary["scope"]))
    criterion = primary.get("completion_criterion")
    if criterion and str(criterion).strip().lower() != "none":
        parts.append(_labelled(phrases["criterion"], criterion))
    return " ".join(part for part in parts if part)


def _secondary(secondary, phrases):
    texts = [str(item.get("text", "")).strip() for item in secondary or []]
    texts = [text for text in texts if text]
    if not texts:
        return ""
    return _listed(phrases["secondary"], texts)


def _warrant(warrant, phrases):
    return _cited(warrant.get("gap_statement", ""), warrant.get("evidence"))


def _standpoint(plan, phrases):
    declaration = (plan.get("meta") or {}).get("standpoint")
    body = plan.get("standpoint")
    if declaration == "none":
        return phrases["standpoint_none"]
    if declaration == "undeclared" or body is None:
        return phrases["standpoint_undeclared"]
    parts = [
        _listed(phrases["premises"], body.get("normative_premises") or []),
        _listed(phrases["criteria"], body.get("criteria") or []),
    ]
    return " ".join(part for part in parts if part)


def _sources(sources, phrases):
    items = []
    for source in sources or []:
        kind = phrases["source_kinds"].get(source.get("kind"), source.get("kind", ""))
        description = str(source.get("description", "")).strip()
        if description:
            items.append(f"{description} ({kind})")
    return _listed(phrases["sources"], items)


def _method(method, phrases):
    first = [_end(method.get("approach", ""))]
    sources = _sources(method.get("sources"), phrases)
    if sources:
        first.append(sources)
    paragraphs = [" ".join(part for part in first if part)]

    if method.get("procedure"):
        paragraphs.append(_end(method["procedure"]))

    last = []
    if method.get("validity_conditions"):
        last.append(_listed(phrases["validity"], method["validity_conditions"]))
    limits = method.get("limits")
    if limits == "none":
        last.append(phrases["limits_none"])
    elif limits:
        last.append(_listed(phrases["limits"], limits))
    else:
        last.append(phrases["limits_absent"])
    paragraphs.append(" ".join(part for part in last if part))
    return [paragraph for paragraph in paragraphs if paragraph]


def _results(results, phrases):
    paragraphs = []
    for result in results or []:
        kind = result.get("kind")
        if kind == "output":
            continue
        label = phrases["kinds"].get(kind)
        if label is None:
            continue
        text = _labelled(label, result.get("claim", ""))
        if kind == "outcome" and result.get("measure"):
            text = f"{text} {_labelled(phrases['measure'], result['measure'])}"
        paragraphs.append(text)
    return paragraphs


def _outputs(results, phrases):
    claims = [
        str(result.get("claim", "")).strip().rstrip(".")
        for result in results or []
        if result.get("kind") == "output" and result.get("claim")
    ]
    if not claims:
        return ""
    return _end(f"{phrases['outputs']}: " + "; ".join(claims))


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def _funder_id(plan):
    meta = plan.get("meta") or {}
    funder_id = meta.get("funder")
    if not funder_id or funder_id == "none":
        raise RenderError(
            "no funder: set meta.funder to fwo, prin, vub, horizon, dfg or snsf "
            "before rendering; a funder-agnostic plan has no section table"
        )
    if funder_id == "other":
        scheme = meta.get("scheme")
        named = f" ({scheme})" if scheme else ""
        raise RenderError(
            f"funder 'other'{named} has no section table: render by hand from "
            "the call's own form"
        )
    return funder_id


def _section_body(section, plan, phrases):
    blocks = []
    fields = section.get("fields") or []
    results_here = False

    for field in fields:
        if field == "warrant":
            blocks.append(_warrant(plan["warrant"], phrases))
        elif field == "standpoint":
            blocks.append(_standpoint(plan, phrases))
        elif field == "questions.primary":
            blocks.append(_question(plan["questions"]["primary"], phrases))
        elif field == "questions.secondary":
            blocks.append(_secondary(plan["questions"].get("secondary"), phrases))
        elif field == "method":
            blocks.extend(_method(plan["method"], phrases))
        elif field == "method.procedure":
            blocks.append(_end(plan["method"].get("procedure", "")))
        elif field == "results":
            results_here = True
            if plan.get("results"):
                blocks.extend(_results(plan["results"], phrases))
            else:
                blocks.append(phrases["no_results"])
            if section.get("delivers"):
                blocks.append(_outputs(plan.get("results"), phrases))
            blocks = [block for block in blocks if block]

    if section.get("delivers") and not results_here:
        blocks.append(_outputs(plan.get("results"), phrases))

    if not fields:
        blocks.append(f"*{section.get('outside_model', '')}*")

    return [block for block in blocks if block]


def render_plan(plan, mappings=None):
    """Return the Markdown draft for a plan that names one of the six funders."""
    data = mappings if mappings is not None else load_mappings()
    funder_id = _funder_id(plan)
    funder = funder_of(data, funder_id)
    phrases = PHRASES[funder["language"]]

    for name in ("questions", "method", "warrant"):
        if name not in plan:
            raise RenderError(f"plan has no {name!r}; validate it before rendering")

    parts = []
    title = (plan.get("meta") or {}).get("title")
    if title:
        parts.append(f"# {title}")

    for section in funder["sections"]:
        body = _section_body(section, plan, phrases)
        parts.append("\n\n".join([f"## {section['name']}", *body]))

    return "\n\n".join(parts) + "\n"


def coverage_gaps(plan, mappings=None):
    """Fields present in the plan that this funder's table does not place."""
    data = mappings if mappings is not None else load_mappings()
    funder = funder_of(data, _funder_id(plan))
    mapped = {field for section in funder["sections"] for field in section.get("fields") or []}
    absent = funder.get("absent") or {}

    gaps = []
    if plan.get("results") and "results" not in mapped:
        gaps.append(("results", absent.get("results")))
    if plan.get("standpoint") is not None and "standpoint" not in mapped:
        gaps.append(("standpoint", absent.get("standpoint")))
    return gaps


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------


def plan_findings(plan):
    schema = json.loads(validate.SCHEMA_PATH.read_text(encoding="utf-8"))
    findings = validate.evaluate(plan, schema, root=schema)
    if not findings:
        findings = validate.check_semantics(plan)
    return findings


def build_parser():
    parser = argparse.ArgumentParser(
        prog="render.py",
        description="Render a requmexre plan into the sections of one of six funders.",
        epilog=(
            "Exit status: 0 rendered; 1 the validator rejects the plan; "
            "2 no plan, bad usage, or a funder with no table."
        ),
    )
    parser.add_argument("file", nargs="?", metavar="PLAN", help="a validated plan.json")
    parser.add_argument("--out", metavar="PATH", help="write the draft to PATH")
    parser.add_argument(
        "--mappings", metavar="PATH", help="read the section tables from PATH"
    )
    parser.add_argument("--version", action="version", version=f"requmexre render v{VERSION}")
    return parser


def refuse(message, as_json=False):
    print(message, file=sys.stderr)
    return 2


def main(argv):
    args = build_parser().parse_args(argv)
    if not args.file:
        return refuse("no plan given. Pass a plan.json to render.")
    try:
        plan = json.loads(Path(args.file).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return refuse(f"cannot read {args.file}: {error}")

    findings = plan_findings(plan)
    if findings:
        print(f"{args.file} does not validate; fix it before rendering:", file=sys.stderr)
        for finding in findings:
            print(f"  {finding}", file=sys.stderr)
        return 1

    try:
        data = load_mappings(args.mappings)
        text = render_plan(plan, data)
        gaps = coverage_gaps(plan, data)
    except RenderError as error:
        return refuse(str(error))

    for field, reason in gaps:
        suffix = f": {reason}" if reason else ""
        print(
            f"warning: {field} has no section for {plan['meta']['funder']}{suffix}",
            file=sys.stderr,
        )

    if args.out:
        target = Path(args.out)
        target.write_text(text, encoding="utf-8")
        print(f"wrote {target}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
