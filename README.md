# requmexre

A machine-readable model of a research plan written as **research question → methodology → expected results**: a JSON Schema, a two-layer validator and section mappings for six funders.

The name is the three slots: **RE**search **QU**estion + **ME**thodology + e**X**pected **RE**sults.

**Version:** v0.4 (schema) · **Mappings:** v0.5 draft · **Licence:** all rights reserved · **Sources:** [SOURCES.md](SOURCES.md)

## What the funders ask

| Template | Question / objective | Method | Results | Document |
|---|---|---|---|---|
| FWO — project outline | 2. Scientific research objectives | 3. Research methodology and work plan | inside 2: expected outcomes | [form](https://www.fwo.be/media/qi1jlhea/application-form-for-a-phd-fellowship-fundamental-research.pdf) |
| VUB — research plan | Research objectives/questions | Methodology and work plan | Hypothesis, to be confirmed later | [regulations](https://www.vub.be/sites/default/files/2025-02/2025_Reglementen_Centraal_Doctoraatsreglement_EN.pdf) |
| Horizon Europe — Part B | 1.1 Objectives and ambition | 1.2 Methodology; 3.1 Work plan and resources | 2. Impact | [form](https://ec.europa.eu/info/funding-tenders/opportunities/docs/2021-2027/horizon/temp-form/af/af_he-ria-ia_en.pdf) |
| DFG — project description | 2.2 Objectives | 2.3 Work programme incl. methods | **no section** | [template](https://www.dfg.de/resource/blob/168328/54-012-en.pdf) |
| SNSF — research plan | 3. Detailed research plan | inside 3 | **no section** | [requirements](https://www.snf.ch/en/257qx6wxjo72ODHy/page/funding/documents-downloads/regulations-requirements-for-the-research-plan) |
| PRIN — progetto di ricerca | Obiettivi | Metodologia e piano di lavoro | Risultati attesi e impatto | [guidelines](https://www.mur.gov.it/sites/default/files/2026-05/D.D.%202298%20All.%203%20Linee%20Guida%20di%20valutazione.pdf) |

Question and method appear in all six. Results appear in four — FWO (inside the objectives), VUB (as a hypothesis), Horizon, PRIN — and have no section in DFG and SNSF. The schema therefore treats results as optional.

Structural notes:

- Horizon Part B also has 2.2 measures to maximise impact (dissemination, exploitation and communication), an optional 2.3 Summary, 3.1 Work plan and resources, and 3.2 Capacity of participants and consortium as a whole. 3.1 renders the procedure's sequence; resources and 3.2 are not modelled.
- DFG section 1 is the state of the art and preliminary work; 2.1 is the anticipated total duration, not the state of the art.
- The SNSF plan has five sections: 1 current state of research, 2 current state of your own research, 3 detailed research plan, 4 schedule and milestones, 5 relevance and impact.

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
                 "limits": ["..."] },
  "results":   [ { "claim": "...", "kind": "hypothesis",
                   "falsifier": "...", "evidence_needed": "..." },
                 { "claim": "...", "kind": "outcome", "measure": "..." },
                 { "claim": "...", "kind": "output" } ],
  "warrant":   { "gap_statement": "...", "evidence": ["..."] },
  "standpoint":{ "normative_premises": ["..."], "criteria": ["..."] }
}
```

- `questions.primary.completion_criterion`: what would count as an answer; `"none"` when the plan states none.
- `questions.primary.form`: whether the text is written as an `interrogative` or an `objective`; R1 checks the text against it.
- `method.sources[].kind`: `data`, `literature`, `participants` or `corpus`; the `description` says what exactly is used.
- `method.validity_conditions` and `method.limits`: when the finding holds, and what it does not cover; `limits` is `"none"` when the plan states none.
- `results[].falsifier`: required for `hypothesis` and `expected_finding`; an `outcome` carries a `measure` instead, and an `output` carries neither.
- `warrant`: why the question is still open, with at least one dated or identifiable source.
- `standpoint`: the normative premises and criteria; `meta.standpoint` says `declared`, `none` or `undeclared`.

Conditional rules: a comparative question needs a `tertium_comparationis`; an evaluative question needs criteria and their operationalisation.

Full rules: [schema/RULES.md](schema/RULES.md). Structural S1–S10 in JSON Schema; semantic R1–R8 in the validator.

## Files

```
README.md · SOURCES.md · LICENSE.md · AGENTS.md
schema/requmexre.schema.json   JSON Schema draft 2020-12
schema/RULES.md                S1–S10, R1–R8
schema/validate.py             two-layer validator
schema/cases/                  fwo, prin, vub, negative (fixtures)
schema/published/               three published plans, encoded
schema/BREAKAGES.md            where the model breaks on those plans
skill/requmexre/               SKILL.md, references/mappings.md, assets/template.json
site/build.py                  Pages build: README, RULES, SOURCES → one page
.github/workflows/             validate.yml, pages.yml
```

## Use

```bash
cd schema
python3 validate.py                                      # all fixtures
python3 validate.py cases/prin.json                      # one file
python3 validate.py ../skill/requmexre/assets/template.json
python3 validate.py published/*.json                     # the published plans
```

Exit code 0 when every pure plan is valid and every negative envelope reports its expected rule. Negative fixtures wrap the plan as `{ "expect": ..., "plan": ... }`; positive plans, the template and the published plans are pure. The skill runs five phases — detect, question, method, results, guards — writes `plan.json`, validates it, and renders it into the six funder sections.

## Limits

- Fixtures are synthetic: structure taken from the documents above, content illustrative.
- The validator checks form, not truth, not the existence of citations, not the fit between a claim and its evidence.
- The three slots are an administrative form, not a theory of method. The schema formalises the document, not the research.
- Registration numbers, ethics approvals and timelines are out of scope: they belong to the funder's submission forms, not to the plan. There is no `extensions` field.

## Roadmap

| Version | Content |
|---|---|
| v0.2 | Plural questions, declared form, explicit completion criterion; three published plans in `schema/published` |
| v0.3 | Outcomes with a measure, and outputs, in `results`; answer types widened; pilot re-run in [schema/BREAKAGES.md](schema/BREAKAGES.md) |
| v0.4 | Typed sources: `data`, `literature`, `participants`, `corpus` in `method.sources` |
| v0.5 | Mappings for Horizon, DFG and SNSF in the skill (draft) |
| v1.0 | Stable schema and citation |

## Cite

> *requmexre*, v0.4, 2026.
