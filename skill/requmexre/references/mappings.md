# Section mappings

How the five fields become the sections of an FWO, PRIN, VUB, Horizon, DFG or
SNSF plan. The six tables date from v0.5; the schema is v1.0 and neither changed
at the freeze. Section names and numbers are taken from the documents cited in
[`SOURCES.md`](../../../SOURCES.md); page and character limits are set by the
call and are not reproduced here; `SKILL.md` gives the cut order.

The tables read in both directions: fields → sections when writing, sections →
fields when reviewing. For a review, [`review.md`](review.md) gives the report
template, the status words, the outside-model rule and the complete list of form
defects.

## FWO — application form (PhD fellowship, fundamental research)

The document is the application form cited in `SOURCES.md`; this corpus has no
separate "project outline", and the table below covers sections 1–3 of the form.

| Section | Fields | What to write |
|---|---|---|
| 1. Rationale and positioning | `warrant`, `standpoint` | The gap, with its dated evidence, and the position from which the question is asked. If `meta.standpoint` is `none`, say so in one sentence. If it is `undeclared`, do not claim none: flag the silence and ask for a declaration where the form requires positioning. |
| 2. Scientific research objectives | `questions.primary`, `questions.secondary`, `results` | The question or objective as written, then the secondary objectives, then what would count as an answer, then the expected outcomes. FWO has no separate results section, so expected outcomes belong here. Render each claim as an expected result; never its falsifier. See [`fwo-example.md`](fwo-example.md). |
| 3. Research methodology and work plan | `method` | Approach, sources, procedure, then validity conditions and limits. The work plan is the procedure split into its steps and put in the order it gives, each step saying what it draws on and what it produces (see the sequence rule under Rendering rules). See [`fwo-example.md`](fwo-example.md). |

FWO asks for hypotheses and expected results inside the objectives. Do not open a
results section of your own; the form's numbering is part of the assessment.

An `output` is not an expected result: a dataset, instrument or piece of code is
produced, not inferred, and section 2 asks what the study expects to find. Render
outputs in section 3, once, at the end of the work plan, as what the procedure
delivers — not as an outcome and not as a finding.

## PRIN — progetto di ricerca

| Section | Fields | What to write |
|---|---|---|
| Contesto e stato dell'arte | `warrant` | The state of the art organised around the gap, not a literature review in chronological order. Each claim about the state of the art carries its source. |
| Obiettivi | `questions.primary`, `questions.secondary` | The question or objective as written, its scope, and — for evaluative questions — the criteria and how they are operationalised. |
| Metodologia e piano di lavoro | `method` | Approach, sources, procedure, validity conditions, limits. The procedure supplies the order; who does what and when come from the call, not from `plan.json`. |
| Risultati attesi e impatto | `results`, `standpoint` | Expected findings as findings, outcomes as outcomes, outputs as outputs, and the impact argued from the declared criteria. Impact without criteria is a wish. |

PRIN is in Italian. Render into Italian; the JSON keeps its own language, and
`meta.funder` is `prin`.

## VUB — doctoral research plan

| Section | Fields | What to write |
|---|---|---|
| Research objectives/questions | `questions.primary`, `questions.secondary` | The question or objective as written, its scope and what would count as an answer. |
| Methodology and work plan | `method` | Approach, sources, procedure, validity conditions, limits. |
| Hypothesis, to be confirmed later | `results` | The hypothesis as a hypothesis. The regulations say it is "to be confirmed or not at a later stage": do not write it as a finding. |

VUB asks for a hypothesis rather than results. If `results` is absent, say what
would be tested and leave the section short; do not invent findings to fill it.

## Horizon Europe — Part B (RIA/IA)

| Section | Fields | What to write |
|---|---|---|
| 1.1 Objectives and ambition | `warrant`, `questions.primary`, `questions.secondary` | The gap with its dated evidence, then the question or objective as written with its scope and criterion. Ambition is the advance beyond the state of the art, not a promise. |
| 1.2 Methodology | `method` | Approach, sources, procedure, validity conditions, limits. |
| 2.1 Project's pathways towards impact | `results`, `standpoint` | Impact argued from expected findings and outcomes and from the declared criteria. If `meta.standpoint` is `none` or `undeclared`, do not invent a standpoint. |
| 3.1 Work plan and resources | `method.procedure` | The procedure's steps in order, as the work plan. Resources and work-package numbering are not modelled; see the sequence rule under Rendering rules. |

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

- **Funder gate.** A table applies only to a plan whose `meta.funder` names that funder (`other`
  with `meta.scheme` is matched by hand). `none`, or an absent field, means the
  plan is funder-agnostic: no table applies. Set the field to the call's funder
  and revalidate before rendering. The validator does not check this — a plan
  without a funder is valid — so the check is the renderer's.
- Prose only. No JSON, no field names, no rule codes in the rendered text.
- Keep the declared `form`: an objective stays an objective in the proposal, an
  interrogative stays a question. Do not rewrite one as the other.
- Section order and numbering follow the funder, not the schema.
- The falsifier and `evidence_needed` are design aids: they stay in `plan.json`,
  and a falsifier is never rendered, not even as "this would be falsified if…".
  A proposal states the claim and the method that would test it.
- Evidence strings are citations. Render each one verbatim, in parentheses, at
  the sentence it supports, separated by semicolons; do not abbreviate, reorder
  or number them. Open a reference list only when the call has one, and then
  reuse the same strings unchanged, in order of first appearance.
- The work plan renders the procedure's steps in the order `method.procedure`
  already gives them. Do not add steps, dates, durations, work packages,
  milestones or roles: the model holds the logical order, not a timetable. A
  timetable the call requires is filled from the form, not from the plan.
- `standpoint` is rendered where the funder asks for rationale, impact or
  positioning. If it is `none`, one sentence of declaration is enough. If it is
  `undeclared`, do not claim the plan has none: flag the silence to the author
  and, where the form requires positioning, ask for a declaration rather than
  inventing one.
- `limits: "none"` is a declaration that the plan states no limits: do not
  invent a limitation. If `limits` is absent, say the plan does not state limits
  rather than claiming there are none.
- **Outside the plan.** Registration, ethics and calendar time sit outside `plan.json`: render them
  from the call's forms, not from requmexre, and do not invent an `extensions`
  field. The procedure's order is not a calendar; see Rendering rules.
- Word and page limits change with the call: cut to the limit the author
  supplies, in the call's own units, and say so when none was available.
  `SKILL.md` gives the cut order and the no-padding rule.

## What is not modelled

The six funders are mapped. The model does not carry:

- calendar time: dates, durations, work packages, milestones and roles; only the
  procedure's logical order is in the model;
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
