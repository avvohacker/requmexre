# requmexre

A machine-readable model of a research plan written as **research question → methodology → expected results**: a JSON Schema, a two-layer validator and section mappings for three funders.

The name is the three slots: **RE**search **QU**estion + **ME**thodology + e**X**pected **RE**sults.

**Version:** v0.3 · **Licence:** all rights reserved · **Sources:** [SOURCES.md](SOURCES.md)

## What the funders ask

| Template | Question / objective | Method | Results | Document |
|---|---|---|---|---|
| FWO — project outline | 2. Scientific research objectives | 3. Research methodology and work plan | inside 2: expected outcomes | [form](https://www.fwo.be/media/qi1jlhea/application-form-for-a-phd-fellowship-fundamental-research.pdf) |
| VUB — research plan | Research objectives/questions | Methodology and work plan | Hypothesis, to be confirmed later | [regulations](https://www.vub.be/sites/default/files/2025-02/2025_Reglementen_Centraal_Doctoraatsreglement_EN.pdf) |
| Horizon Europe — Part B | 1.1 Objectives and ambition | 1.2 Methodology | 2. Impact | [form](https://ec.europa.eu/info/funding-tenders/opportunities/docs/2021-2027/horizon/temp-form/af/af_he-ria-ia_en.pdf) |
| DFG — project description | 2.2 Objectives | 2.3 Work programme incl. methods | **no section** | [template](https://www.dfg.de/resource/blob/168328/54-012-en.pdf) |
| SNSF — research plan | 3. Detailed research plan | inside 3 | **no section** | [requirements](https://www.snf.ch/en/257qx6wxjo72ODHy/page/funding/documents-downloads/regulations-requirements-for-the-research-plan) |
| PRIN — progetto di ricerca | Obiettivi | Metodologia e piano di lavoro | Risultati attesi e impatto | [guidelines](https://www.mur.gov.it/sites/default/files/2026-05/D.D.%202298%20All.%203%20Linee%20Guida%20di%20valutazione.pdf) |

Question and method appear in all six. Results appear in four — FWO (inside the objectives), VUB (as a hypothesis), Horizon, PRIN — and have no section in DFG and SNSF. The schema therefore treats results as optional.

## The model

Five fields: three slots plus two guards.

```json
{
  "questions": { "primary": { "text": "...", "form": "interrogative",
                              "answer_type": "comparative",
                              "scope": "...", "completion_criterion": "..." },
                 "secondary": [ { "text": "...", "form": "objective" } ] },
  "method":    { "approach": "...", "sources": ["..."], "procedure": "...",
                 "validity_conditions": ["..."], "limits": ["..."] },
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
- `method.validity_conditions` and `method.limits`: when the finding holds, and what it does not cover.
- `results[].falsifier`: required for `hypothesis` and `expected_finding`; an `outcome` carries a `measure` instead, and an `output` carries neither.
- `warrant`: why the question is still open, with at least one dated or identifiable source.
- `standpoint`: the normative premises, declared or explicitly set to `"none"` in `meta`.

Conditional rules: a comparative question needs a `tertium_comparationis`; an evaluative question needs criteria and their operationalisation.

Full rules: [schema/RULES.md](schema/RULES.md). Structural S1–S10 in JSON Schema; semantic R1–R8 in the validator.

## Files

```
README.md · SOURCES.md · LICENSE.md
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

Exit code 0 when every file behaves as declared (`meta.expect`). The skill runs five phases — detect, question, method, results, guards — writes `plan.json`, validates it, and renders it into FWO, PRIN or VUB sections.

## Limits

- Fixtures are synthetic: structure taken from the documents above, content illustrative.
- The validator checks form, not truth, not the existence of citations, not the fit between a claim and its evidence.
- The three slots are an administrative form, not a theory of method. The schema formalises the document, not the research.

## Roadmap

| Version | Content |
|---|---|
| v0.2 | Plural questions, declared form, explicit completion criterion; three published plans in `schema/published` |
| v0.3 | Outcomes with a measure, and outputs, in `results`; pilot re-run in [schema/BREAKAGES.md](schema/BREAKAGES.md) |
| v0.4 | Mappings for Horizon, DFG and SNSF in the skill |
| v1.0 | Stable schema and citation |

## Cite

> *requmexre*, v0.3, 2026.
