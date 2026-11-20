# Section mappings

How the five fields become the sections of an FWO, PRIN or VUB plan. Section
names and numbers are taken from the documents cited in
[`SOURCES.md`](../../SOURCES.md); page and character limits are set by the call
and are not reproduced here — read the current form before rendering.

## FWO — project outline (PhD fellowship, fundamental research)

| Section | Fields | What to write |
|---|---|---|
| 1. Rationale and positioning | `warrant`, `standpoint` | The gap, with its dated evidence, and the position from which the question is asked. If `meta.standpoint` is `none`, say so in one sentence rather than leaving the section silent about it. |
| 2. Scientific research objectives | `questions.primary`, `questions.secondary`, `results` | The question or objective as written, then the secondary objectives, then what would count as an answer, then the expected outcomes. FWO has no separate results section, so expected outcomes belong here — as claims with their falsifiers in hand, rendered as outcomes. |
| 3. Research methodology and work plan | `method` | Approach, sources, procedure, then validity conditions and limits. The work plan is the procedure with its sequence made explicit. |

FWO asks for hypotheses and expected results inside the objectives. Do not open a
results section of your own; the form's numbering is part of the assessment.

## PRIN — progetto di ricerca

| Section | Fields | What to write |
|---|---|---|
| Contesto e stato dell'arte | `warrant` | The state of the art organised around the gap, not a literature review in chronological order. Each claim about the state of the art carries its source. |
| Obiettivi | `questions.primary`, `questions.secondary` | The question or objective as written, its scope, and — for evaluative questions — the criteria and how they are operationalised. |
| Metodologia e piano di lavoro | `method` | Approach, sources, procedure, validity conditions, limits. The work plan states who does what and when; the procedure supplies the order. |
| Risultati attesi e impatto | `results`, `standpoint` | Expected findings as outcomes, deliverables as deliverables, and the impact argued from the declared criteria. Impact without criteria is a wish. |

PRIN is in Italian. Render into Italian; the JSON keeps its own language, and
`meta.funder` is `prin`.

## VUB — doctoral research plan

| Section | Fields | What to write |
|---|---|---|
| Research objectives/questions | `questions.primary`, `questions.secondary` | The question or objective as written, its scope and what would count as an answer. |
| Methodology and work plan | `method` | Approach, sources, procedure, validity conditions, limits. |
| Hypothesis, to be confirmed later | `results` | The hypothesis as a hypothesis. The regulations say it is "to be confirmed or not at a later stage": do not write it as a finding, and keep the falsifier out of the section — it belongs in `plan.json`. |

VUB asks for a hypothesis rather than results. If `results` is absent, say what
would be tested and leave the section short; do not invent findings to fill it.

## Rendering rules

- Prose only. No JSON, no field names, no rule codes in the rendered text.
- Keep the declared `form`: an objective stays an objective in the proposal, an
  interrogative stays a question. Do not rewrite one as the other.
- Section order and numbering follow the funder, not the schema.
- The falsifier and `evidence_needed` are design aids: they stay in `plan.json`.
  A proposal states the claim and the method that would test it.
- `standpoint` is rendered where the funder asks for rationale, impact or
  positioning. If it is `none`, one sentence of declaration is enough; silence
  reads as an undeclared premise.
- Word and page limits are not in this file because they change with the call.
  Check the form, then cut — preferably from the state of the art, never from the
  falsifiers.

## What is not mapped

Horizon Europe (Part B), DFG (project description 54.012) and SNSF (research
plan) appear in the README table and in `SOURCES.md`, but the skill does not
render them yet. Their sections are known — objectives, methodology, impact
for Horizon; objectives, work programme, no results section for DFG; a single
detailed research plan for SNSF — and mapping them is roadmap v0.3.

## Gaps the mapping exposes

- FWO and VUB have no results section: the schema's optional `results` is what
  makes one plan serve both.
- VUB calls results a hypothesis to be confirmed; DFG and SNSF do not ask for
  them at all. A model that required results would exclude three of the six
  templates.
- PRIN alone asks for impact, which is why `standpoint` carries criteria rather
  than a free-text justification.
