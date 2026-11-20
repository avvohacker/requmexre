# Section mappings

How the five fields become the sections of an FWO, PRIN, VUB, Horizon, DFG or
SNSF plan. The six tables are the v0.5 mappings; the schema is v0.5. Section
names and numbers are taken from
the documents cited in
[`SOURCES.md`](../../../SOURCES.md); page and character limits are set by the call
and are not reproduced here — read the current form before rendering.

## FWO — project outline (PhD fellowship, fundamental research)

| Section | Fields | What to write |
|---|---|---|
| 1. Rationale and positioning | `warrant`, `standpoint` | The gap, with its dated evidence, and the position from which the question is asked. If `meta.standpoint` is `none`, say so in one sentence. If it is `undeclared`, do not claim none: flag the silence and ask for a declaration where the form requires positioning. |
| 2. Scientific research objectives | `questions.primary`, `questions.secondary`, `results` | The question or objective as written, then the secondary objectives, then what would count as an answer, then the expected outcomes. FWO has no separate results section, so expected outcomes belong here — as claims with their falsifiers in hand, rendered as expected results. |
| 3. Research methodology and work plan | `method` | Approach, sources, procedure, then validity conditions and limits. The work plan is the procedure with its sequence made explicit. |

FWO asks for hypotheses and expected results inside the objectives. Do not open a
results section of your own; the form's numbering is part of the assessment.

## PRIN — progetto di ricerca

| Section | Fields | What to write |
|---|---|---|
| Contesto e stato dell'arte | `warrant` | The state of the art organised around the gap, not a literature review in chronological order. Each claim about the state of the art carries its source. |
| Obiettivi | `questions.primary`, `questions.secondary` | The question or objective as written, its scope, and — for evaluative questions — the criteria and how they are operationalised. |
| Metodologia e piano di lavoro | `method` | Approach, sources, procedure, validity conditions, limits. The work plan states who does what and when; the procedure supplies the order. |
| Risultati attesi e impatto | `results`, `standpoint` | Expected findings as findings, outcomes as outcomes, outputs as outputs, and the impact argued from the declared criteria. Impact without criteria is a wish. |

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

## Horizon Europe — Part B (RIA/IA)

| Section | Fields | What to write |
|---|---|---|
| 1.1 Objectives and ambition | `warrant`, `questions.primary`, `questions.secondary` | The gap with its dated evidence, then the question or objective as written with its scope and criterion. Ambition is the advance beyond the state of the art, not a promise. |
| 1.2 Methodology | `method` | Approach, sources, procedure, validity conditions, limits. |
| 2.1 Project's pathways towards impact | `results`, `standpoint` | Impact argued from expected findings and outcomes and from the declared criteria. If `meta.standpoint` is `none` or `undeclared`, do not invent a standpoint. |
| 3.1 Work plan and resources | `method.procedure` | The procedure's sequence as work packages. Resources are not modelled. |

Horizon also has 2.2 Measures to maximise impact - Dissemination, exploitation
and communication, an optional 2.3 Summary, and 3.2 Capacity of participants and
consortium as a whole. Preliminary work and the applicant's own research are not
model fields: do not invent them.

## DFG — project description 54.012

| Section | Fields | What to write |
|---|---|---|
| 1 Starting Point — State of the art and preliminary work | `warrant` | The gap and its dated evidence. Preliminary work and the applicant's own research are not modelled; do not invent them. |
| 2.2 Objectives | `questions.primary`, `questions.secondary` | The question or objective as written, its scope, and its criterion. DFG has no results section: if `results` is present, do not open one; use the claims only inside 2.2 or 2.3 where they serve the objectives or work programme. |
| 2.3 Work programme incl. proposed research methods | `method` | Approach, sources, procedure, validity conditions, limits. |

DFG 2.1 Anticipated total duration of the project, 2.4 Handling of research data, 2.5 Relevance of sex, gender and/or diversity in the research project, 3 Project- and subject-related list of publications, 4 Supplementary information on the research context and 5 Requested modules/funds are not modelled.
There is no dedicated standpoint section: if `meta.standpoint` is `declared`, it
belongs in 2.2 as part of the objectives; if it is `none` or `undeclared`, do
not invent one.

## SNSF — research plan

| Section | Fields | What to write |
|---|---|---|
| 1. Current state of research in the field | `warrant` | The gap and its dated evidence. |
| 2. Current state of your own research | — | Own research is not a model field; do not invent it. |
| 3. Detailed research plan | `questions`, `method` | Question or objective, approach, sources and procedure. The form also asks for investigations, data collection and team roles; the first two are in the method, the team is not modelled. |
| 4. Schedule and milestones | `method.procedure` (partial) | The procedure's sequence; milestones and resources are not modelled. |
| 5. Relevance and impact | `standpoint` | Impact from the plan's expected findings or outcomes, if present, and from the declared criteria. SNSF has no results section; do not open one. If `meta.standpoint` is `none` or `undeclared`, do not invent one. |

SNSF has no results section: do not render one. It also asks for ethics and budget; neither is modelled.

## Rendering rules

- Prose only. No JSON, no field names, no rule codes in the rendered text.
- Keep the declared `form`: an objective stays an objective in the proposal, an
  interrogative stays a question. Do not rewrite one as the other.
- Section order and numbering follow the funder, not the schema.
- The falsifier and `evidence_needed` are design aids: they stay in `plan.json`.
  A proposal states the claim and the method that would test it.
- `standpoint` is rendered where the funder asks for rationale, impact or
  positioning. If it is `none`, one sentence of declaration is enough. If it is
  `undeclared`, do not claim the plan has none: flag the silence to the author
  and, where the form requires positioning, ask for a declaration rather than
  inventing one.
- `limits: "none"` is a declaration that the plan states no limits: do not
  invent a limitation. If `limits` is absent, say the plan does not state limits
  rather than claiming there are none.
- Registration, ethics and timeline sit outside `plan.json`: render them from the
  call's forms, not from requmexre, and do not invent an `extensions` field.
- Word and page limits are not in this file because they change with the call.
  Check the form, then cut — preferably from the state of the art, never from the
  falsifiers.

## What is not modelled

The six funders are mapped. The model does not carry:

- preliminary work and the applicant's own research (Horizon, DFG section 1,
  SNSF section 2);
- Horizon 2.2 Measures to maximise impact - Dissemination, exploitation and
  communication, optional 2.3 Summary, 3.2 Capacity of participants and
  consortium as a whole, and the resources of 3.1;
- DFG 2.1 Anticipated total duration of the project, 2.4 Handling of research
  data, 2.5 Relevance of sex, gender and/or diversity in the research project,
  3 Project- and subject-related list of publications, 4 Supplementary
  information on the research context, 5 Requested modules/funds, and a standalone
  results section;
- SNSF results (no section; do not render one), 4 milestones (only the
  procedure's sequence is mapped), ethics and budget.

A funder outside the six known values is `funder: "other"` with `scheme`; it
has no table and is handled by hand.

## Gaps the mapping exposes

- FWO and VUB have no results section: the schema's optional `results` is what
  makes one plan serve both.
- VUB calls results a hypothesis to be confirmed; DFG and SNSF give them no
  separate section. A model that required results would exclude three of the six
  templates.
- PRIN, Horizon and SNSF ask for impact, which is why `standpoint` carries
  criteria rather than a free-text justification.
