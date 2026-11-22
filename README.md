# requmexre

A machine-readable model of a document written as **research question → methodology → expected results**: a JSON Schema, a two-layer validator, a citation checker, section mappings for six funders and a generic profile for any other document that uses those three headings.

The name is the three slots: **RE**search **QU**estion + **ME**thodology + e**X**pected **RE**sults.

**Version:** v1.2 · **Licence:** all rights reserved · **Sources:** [SOURCES.md](SOURCES.md)

## What the funders ask

| Template | Question / objective | Method | Results | Document |
|---|---|---|---|---|
| FWO — application form | 2. Scientific research objectives | 3. Research methodology and work plan | inside 2: expected outcomes | [form](https://www.fwo.be/media/qi1jlhea/application-form-for-a-phd-fellowship-fundamental-research.pdf) |
| VUB — research plan | Scientific research goals | Research methodology and work plan | inside goals: hypotheses and partial results | [template](https://www.vub.be/sites/default/files/2025-04/2025_Benodigde_documenten_Template_Research_Plan_PhD_EN.docx) |
| Horizon Europe — Part B | 1.1 Objectives and ambition | 1.2 Methodology; 3.1 Work plan and resources | 2. Impact | [form](https://ec.europa.eu/info/funding-tenders/opportunities/docs/2021-2027/horizon/temp-form/af/af_he-ria-ia_en.pdf) |
| DFG — project description | 2.2 Objectives | 2.3 Work programme incl. proposed research methods | **no section** | [template](https://www.dfg.de/resource/blob/168328/54-012-en.pdf) |
| SNSF — research plan | 3. Detailed research plan | inside 3 | **no section** | [requirements](https://www.snf.ch/en/257qx6wxjo72ODHy/page/funding/documents-downloads/regulations-requirements-for-the-research-plan) |
| PRIN — scientific proposal | a. Objectives | a. Methodology and risks | b. Results and expected impacts | [form](http://prin.mur.gov.it/Attachments/getAttachment?key=oLjLA8JnI6imQjuJ7hMr4A==) |

Question and method appear in all six. Results appear in four — FWO (inside the objectives), VUB (inside Scientific research goals, as hypotheses and partial results), Horizon, PRIN (block b) — and have no section in DFG and SNSF. The schema therefore requires `results` by default, but exempts a document whose `meta.funder` is exactly `dfg` or `snsf`; a document with no funder is not exempt. When results are present, R5 still requires a claim or an outcome, never outputs alone.

The six are pre-mapped, not the model's boundary. A document with no `meta.funder`, `meta.funder: none`, or `other` with a `scheme` renders through the generic profile — **Research Question**, **Methodology**, **Expected Results** — with the warrant and standpoint inside the question and outputs closing the method. A form whose headings rename or merge those three needs its own table; the generic profile does not pretend to be that form.

Structural notes:

- Horizon Part B also has 2.2 Measures to maximise impact - Dissemination, exploitation and communication, an optional 2.3 Summary, 3.1 Work plan and resources, and 3.2 Capacity of participants and consortium as a whole. 2.1 renders results; the impact pathway, target groups, barriers and measures are not modelled, and `standpoint` is not an impact field. 3.1 renders the procedure's sequence; resources and 3.2 are not modelled.
- DFG section 1 is Starting Point (State of the art and preliminary work); 2.1 is “Anticipated total duration of the project”, not the state of the art.
- The SNSF plan has five sections: 1 current state of research in the field, 2 current state of your own research, 3 detailed research plan, 4 schedule and milestones, 5 relevance and impact. Section 5 is outside the model; results and `standpoint` are not substitutes for it.
- PRIN's SECTION C has blocks a., b. and c. Block b renders results; its impact pathways and measures to maximise impact are not modelled, and `standpoint` is not an impact field. Block c (organization, operational work plan, team, timeframes, resources and budget) is not modelled; draft it from the call.
- Impact is not one of the five fields. The six-funder matrix in [SOURCES.md](SOURCES.md) separates results, outcomes and impacts; where a form asks for impact, it is written from the call.

## The model

Five fields: three slots plus two guards.

```json
{
  "questions": { "primary": { "text": "...", "form": "interrogative",
                              "answer_type": "comparative",
                              "scope": "...", "completion_criterion": "..." },
                 "secondary": [ { "text": "...", "form": "objective" } ] },
  "method":    { "approach": "...",
                 "sources": [ { "kind": "literature", "description": "..." } ],
                 "procedure": "...", "validity_conditions": ["..."],
                 "limits": ["..."],
                 "risks": [ { "risk": "...", "mitigation": "..." } ] },
  "results":   [ { "claim": "...", "kind": "hypothesis",
                   "falsifier": "...", "evidence_needed": "..." },
                 { "claim": "...", "kind": "outcome", "measure": "..." },
                 { "claim": "...", "kind": "output" } ],
  "warrant":   { "gap_statement": "...", "evidence": ["..."] },
  "standpoint":{ "normative_premises": ["..."], "criteria": ["..."] }
}
```

- `questions.primary.completion_criterion`: what would count as an answer; `"none"` when the document states none.
- `questions.primary.form`: whether the text is written as an `interrogative` or an `objective`; R1 checks the text against it.
- `method.sources[].kind`: `data`, `literature`, `participants` or `corpus`; the `description` says what exactly is used.
- `method.validity_conditions` and `method.limits`: when the finding holds, and what it does not cover; `limits` is `"none"` when the document states none.
- `method.risks`: optional; each entry states what could go wrong and its mitigation. A risk is not a limit; a mitigation is not an apology.
- `results[].falsifier`: required for `hypothesis` and `expected_finding`; an `outcome` carries a `measure` instead, and an `output` carries neither.
- `warrant`: why the question is still open, with at least one dated or identifiable source.
- `standpoint`: the normative premises and criteria; `meta.standpoint` says `declared`, `none` or `undeclared`.

Conditional rules: a comparative question needs a `tertium_comparationis` and carries no evaluative fields; an evaluative question needs criteria and their operationalisation and carries no tertium.

Full rules: [schema/RULES.md](schema/RULES.md). Structural S1–S10 in JSON Schema; semantic R1–R8 in the validator. The schema `$id` is `https://avvohacker.github.io/requmexre/schema/1.2/requmexre.schema.json`, and the Pages build publishes the file at that path. The frozen 1.1 schema remains published at its original `/schema/1.1/` path from `schema/archive/1.1/`; the 1.0 schema remains at `/schema/1.0/` from `schema/archive/1.0/`.

## Files

```
README.md · VERSION_NOTES.md · CITATION.cff · SOURCES.md · LICENSE.md · AGENTS.md
schema/requmexre.schema.json   JSON Schema draft 2020-12
schema/RULES.md                S1–S10, R1–R8
schema/validate.py             two-layer validator
schema/verify_citations.py     checks cited sources against their records
schema/render.py               renders a document into a funder's sections or the generic profile
schema/mappings.json           six funder tables and the generic profile, machine-readable
schema/archive/1.1/           the frozen 1.1 schema, still published at its $id
schema/archive/1.0/           the frozen 1.0 schema, still published at its $id
schema/cases/                  fwo, prin, vub, dfg, horizon, negative (fixtures)
schema/published/              three pilot encodings (convenience sample)
tests/                         pytest suite: rules, fixtures, CLI, render goldens
schema/NOTES.md                maintainer notes: rationale, fixtures, extending
skill/requmexre/SKILL.md       the skill: five fields, six phases
skill/requmexre/references/    mappings, RULES, FWO example, review report
skill/requmexre/scripts/       bundled validator, renderer and citation checker, identical to schema/
skill/requmexre/assets/        template and schema, identical to schema/
skill/install/                 bootstrap loader, bundle builder and checksum-pinned bundle
site/build.py                  Pages build: README, RULES, SOURCES → one page
.github/workflows/             validate.yml, pages.yml
```

The three files in `schema/published/` are a convenience sample of open-access
protocols, chosen to stress the model — an aim-form objective, a secondary
mechanistic question, outputs and an outcome, a funder outside the enum. They
are not a representative corpus, and no user selected them; the protocols belong
to their publishers, the encodings to this project.

## Use

```bash
cd schema
python3 validate.py --fixtures                           # built-in corpus, not your document
python3 validate.py cases/prin.json                      # one file
python3 validate.py ../skill/requmexre/assets/template.json
python3 validate.py published/*.json                     # the pilot encodings
python3 validate.py --help                               # usage and exit codes
python3 validate.py --version                            # requmexre v1.2
python3 validate.py --json cases/prin.json               # one machine-readable report
python3 render.py cases/prin.json                        # draft in PRIN's sections
python3 render.py cases/fwo.json --out draft.md          # to a file
python3 render.py ../skill/requmexre/assets/template.json # generic profile (funder none or absent)
python3 render.py plan.json --heading-question "Domanda di ricerca" \
  --heading-method "Metodologia" --heading-results "Risultati attesi"
python3 verify_citations.py cases/prin.json              # source metadata check
python3 verify_citations.py --offline plan.json          # extract identifiers only
```

The account skill is installed as the visible schema plus `scripts/requmexre.py`. Its first run downloads `skill/install/requmexre.bundle` from `main`, verifies the SHA-256 and unpacks the rest into the skill directory; later runs use the local copy.

The pytest suite runs from the repository root: `python3 -m pytest -q`. The citation checker uses OpenAlex, Crossref, PubMed, arXiv, Open Library and the URL itself; no API key is required, and `--offline` extracts identifiers without a request. `REQMEXRE_CONTACT_EMAIL` and `NCBI_API_KEY` are optional.

The renderer exits 0 on a draft, 1 when the validator rejects the document, and 2 on bad usage or an unknown profile.

Exit code 0 when every pure plan is valid and every negative envelope reports its expected rule, 1 when one does not, 2 on bad usage. A run with neither a file nor `--fixtures` exits 2, so the built-in corpus can never be mistaken for a check of your plan. `--json` writes one object with `tool`, `version`, `scope` (`fixtures` or `files`), `ok`, `total`, `passed`, `failed` and a `files` list, each entry carrying `path`, `ok`, `expected`, `findings` (`rule`, `path`, `message`) and `note`. Negative fixtures wrap the plan as `{ "expect": ..., "plan": ... }`; positive plans, the template and the pilot encodings are pure. The skill runs six phases — detect, question, method, results, guards, citations — writes `plan.json`, validates it, checks its cited sources, and renders it into a funder's sections or the generic three-section profile.

## Limits

- Fixtures are synthetic: structure taken from the documents above, content illustrative.
- The validator checks form, not truth. `verify_citations.py` checks that a cited source exists and that its title, year and author agree with the citation; it cannot read a paywalled full text or decide whether the source supports a specific claim. The gap-to-abstract overlap is a signal, not a verdict.
- Six funders are pre-mapped; a document outside them, or with no `meta.funder`, that uses the three headings renders through the generic profile. A form that renames or merges those sections needs its own table.
- The three slots are an administrative form, not a theory of method. The schema formalises the document, not the research.
- Registration numbers, ethics approvals and calendar timelines are out of scope: they belong to the funder's submission forms, not to the plan, and the procedure's order is not a timetable. There is no `extensions` field.

## Roadmap

v1.2 is the current tree on `main`: it is not tagged and has no GitHub release.
Earlier versions are frozen in `schema/archive/` and in git history;
[`VERSION_NOTES.md`](VERSION_NOTES.md) records the current release.

## Cite

> *requmexre*, v1.2, 2026.

The machine-readable record is [CITATION.cff](CITATION.cff). There is no DOI:
v1.2 is not tagged and not released, so the citation resolves through the
repository and the Pages site.
