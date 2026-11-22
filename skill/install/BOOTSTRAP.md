# requmexre

A self-extracting skill package for a document whose argument is a research
question, a methodology and expected results, with a warrant and a standpoint.
FWO, PRIN, VUB, Horizon, DFG and SNSF have section tables; any other document
that uses the three headings — including one with no `meta.funder` — renders
through the generic profile.

## First step

Run, from the skill directory:

    python3 scripts/requmexre.py unpack

The first run downloads the checksum-pinned bundle from the project repository,
verifies its SHA-256 and writes SKILL.md, references/, assets/mappings.json,
assets/template.json and scripts/validate.py, render.py and verify_citations.py.
The visible schema is already at assets/requmexre.schema.json. Later runs use
the local files and need no network.

## Running the tools without unpacking

The bundle can run each tool directly; it unpacks a temporary copy when the
skill directory is read-only:

    python3 scripts/requmexre.py validate plan.json
    python3 scripts/requmexre.py verify plan.json
    python3 scripts/requmexre.py render plan.json

`verify` accepts `--json`, `--offline` and `--strict`; `render` accepts
`--heading-question`, `--heading-method` and `--heading-results` for a generic
document in another language.

## What it is not

Budgets, CVs, ethics annexes and calendar time are outside the model. The
validator checks form, not truth; the citation checker verifies source metadata,
not whether a source supports a claim, and never reads a paywalled full text.
