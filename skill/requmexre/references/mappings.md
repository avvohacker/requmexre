# Section mappings

How the five fields become the sections of a document: the six funder tables
below, then the generic profile for any other document that uses Research
Question, Methodology and Expected Results. Section names and numbers are taken
from the documents cited in [`SOURCES.md`](../../../SOURCES.md); where a form does
not number its headings, the numbers here are editorial. Page and character
limits are set by the call and are not reproduced here; `SKILL.md` gives the cut
order.

The tables read in both directions: fields → sections when writing, sections →
fields when reviewing. For a review, [`review.md`](review.md) gives the report
template, the status words, the outside-model rule and the complete list of form
defects.

The six funder tables and the generic profile are data in
[`../assets/mappings.json`](../assets/mappings.json), which
[`../scripts/render.py`](../scripts/render.py) reads; the test suite fails when
the Markdown and the data disagree. The renderer copies the document's prose and
does not translate it. A section the table gives no field is emitted as a
placeholder for the author, not filled.

Impact is not one of the five fields. Where a form asks for it, the section is
written from the call; `results` and `standpoint` can inform it, but neither is an
impact narrative.

## FWO — application form (PhD fellowship, fundamental research)

The document is the application form cited in `SOURCES.md`; the table below
covers the project outline embedded in it. The outline's headings are unnumbered;
the numbers below are for reference.

| Section | Fields | What to write |
|---|---|---|
| 1. Rationale and positioning | `warrant`, `standpoint` | The gap, with its dated evidence, and the position from which the question is asked. If `meta.standpoint` is `none`, say so in one sentence. If it is `undeclared`, do not claim none: flag the silence and ask for a declaration where the form requires positioning. |
| 2. Scientific research objectives | `questions.primary`, `questions.secondary`, `results` | The question or objective as written, then the secondary objectives, then what would count as an answer, then the expected outcomes. FWO has no separate results section, so expected outcomes belong here. Render each claim as an expected result; never its falsifier. See [`fwo-example.md`](fwo-example.md). |
| 3. Research methodology and work plan | `method` | Approach, sources, procedure, then validity conditions, limits and risks. The work plan is the procedure split into its steps and put in the order it gives, each step saying what it draws on and what it produces (see the sequence rule under Rendering rules). See [`fwo-example.md`](fwo-example.md). |

FWO asks for hypotheses and expected outcomes inside the objectives. Do not open
a results section of your own; the form's order is part of the assessment.

An `output` is not an expected result: render it in section 3, once, at the end
of the work plan, as what the procedure delivers (see the output rule under
Rendering rules).

## PRIN — scientific proposal

The form's SECTION C has one scientific proposal; its detailed description is
divided into blocks a., b. and c. The form gives the letters with long criteria,
not short headings; the headings below are short descriptions.

| Section | Fields | What to write |
|---|---|---|
| a. Objectives, state of the art, methodology and risks | `warrant`, `questions.primary`, `questions.secondary`, `method` | The gap with its dated evidence, then the objective or question as written with scope and criteria, then approach, sources, procedure, validity conditions, limits and risks. |
| b. Pathways to results and expected impacts | `results` | Expected findings as findings, outcomes as outcomes, outputs as outputs. The impact pathway, beneficiaries and measures are not modelled: write them from the call. `standpoint` is not an impact field and is not rendered here. |
| c. Organization, work plan and resources | — | Organization, operational work plan, team roles, timeframes, resources, budget and management are not modelled; draft this block from the call. |

The form's impact pathways and measures to maximise impact are not model fields;
draft them from the call. `standpoint` is not a PRIN section: if it is declared,
use its criteria only where the call asks for them; it is not the impact
narrative.

PRIN's form is in English. Render into English; the JSON keeps its own language,
and `meta.funder` is `prin`. The Italian evaluation guidelines are used for the
content criteria, not for the section names.

## VUB — doctoral research plan

The template's sections are Abstract; Rationale and positioning with regard to
the state-of-the-art; Scientific research goals; Research methodology and work
plan; PhD advisory committee; Publication strategy; Ethics; Doctoral training
programme. The table covers the three model sections; the rest is written by
hand.

| Section | Fields | What to write |
|---|---|---|
| Rationale and positioning with regard to the state-of-the-art | `warrant` | The gap with its dated evidence, and the scientific position of the project. |
| Scientific research goals | `questions.primary`, `questions.secondary`, `results` | The question or objective as written, its scope and what would count as an answer, then the hypothesis and the (partial) results. |
| Research methodology and work plan | `method` | Approach, sources, procedure, validity conditions, limits, risks. Outputs close the work plan. |

VUB asks for objectives and/or hypotheses and the (partial) results inside
Scientific research goals. Do not open a separate results or hypothesis section.
`standpoint` is not a VUB section: if `meta.standpoint` is `declared`, it is not
rendered here; keep it as a model guard and write positioning by hand only where
the call asks for it. The template also has an Abstract (including "Anticipated
Results and Impact"), an advisory committee, a publication strategy, ethics and
doctoral training; none of them is modelled.

## Horizon Europe — Part B (RIA/IA)

| Section | Fields | What to write |
|---|---|---|
| 1.1 Objectives and ambition | `warrant`, `questions.primary`, `questions.secondary` | The gap with its dated evidence, then the question or objective as written with its scope and criterion. Ambition is the advance beyond the state of the art, not a promise. |
| 1.2 Methodology | `method` | Approach, sources, procedure, validity conditions, limits, risks. |
| 2.1 Project's pathways towards impact | `results` | Results as the evidence base for the impact narrative. The pathway, target groups, barriers, outcomes and impacts are not modelled: write them from the call. `standpoint` is not an impact field. |
| 3.1 Work plan and resources | `method.procedure` | The procedure's steps in order, as the work plan. Resources and work-package numbering are not modelled; see the sequence rule under Rendering rules. Outputs close 3.1. |

`standpoint` is not a Horizon section: if it is declared, use its criteria only
where the call asks for them; it is not the impact pathway or the measures.

Horizon also has 2.2 Measures to maximise impact - Dissemination, exploitation
and communication, an optional 2.3 Summary, and 3.2 Capacity of participants and
consortium as a whole. Preliminary work and the applicant's own research are not
model fields: do not invent them.

## DFG — project description 54.012

| Section | Fields | What to write |
|---|---|---|
| 1 Starting Point — State of the art and preliminary work | `warrant` | The gap and its dated evidence. Preliminary work and the applicant's own research are not modelled; do not invent them. |
| 2.2 Objectives | `questions.primary`, `questions.secondary`, `standpoint` | The question or objective as written, its scope, and its criterion. DFG has no results section: if `results` is present, do not open one; use the claims only inside 2.2 or 2.3 where they serve the objectives or work programme. |
| 2.3 Work programme incl. proposed research methods | `method` | Approach, sources, procedure, validity conditions, limits, risks. Outputs close the work programme. |

DFG 2.1 Anticipated total duration of the project, 2.4 Handling of research data, 2.5 Relevance of sex, gender and/or diversity in the research project, 3 Project- and subject-related list of publications, 4 Supplementary information on the research context and 5 Requested modules/funds are not modelled.
There is no dedicated standpoint section: if `meta.standpoint` is `declared`, it
belongs in 2.2 as part of the objectives; if it is `none` or `undeclared`, do
not invent one.

## SNSF — research plan

| Section | Fields | What to write |
|---|---|---|
| 1. Current state of research in the field | `warrant` | The gap and its dated evidence. |
| 2. Current state of your own research | — | Own research is not a model field; do not invent it. |
| 3. Detailed research plan | `questions.primary`, `questions.secondary`, `method` | Question or objective, approach, sources, procedure, risks. The form also asks for investigations, data collection and team roles; the first two are in the method, the team is not modelled. Outputs close the detailed research plan. |
| 4. Schedule and milestones | `method.procedure` (partial) | The procedure's sequence; milestones and resources are not modelled. |
| 5. Relevance and impact | — | Relevance and impact is outside the model: scientific relevance; expected impacts for the discipline and academic learning as a whole (research and education/teaching); publication forms. Expected results and `standpoint` are not substitutes. |

SNSF has no results section: do not render one. Section 2 reports results obtained so far, not expected results. The budget is submitted through the SNSF portal and is not modelled; animal-welfare requirements, where applicable, are not a separate section. `standpoint` is not the relevance and impact section: if it is declared, use its criteria only where the call asks for them; it is not an impact narrative.

## Generic — any document with Research Question, Methodology, Expected Results

`meta.funder: none` — a document with no funder — and `meta.funder: other` with
`meta.scheme` — a funder outside the six — render through the generic profile.
It is not a seventh funder and does not claim to be a funder's form: it uses the
three headings by their model names. Check them against the call, and rename
them by hand where the form differs. The gap and the standpoint sit inside
Research Question; outputs close Methodology, so an output is never presented as
an expected result.

| Section | Fields | What to write |
|---|---|---|
| Research Question | `questions.primary`, `questions.secondary`, `warrant`, `standpoint` | The question or objective as written, its scope and completion criterion, then the secondary questions, the gap with its dated evidence, and the standpoint where one is declared. |
| Methodology | `method` | Approach, sources, procedure, validity conditions, limits and risks. Outputs close the section. |
| Expected Results | `results` | Expected findings as findings, outcomes as outcomes, and outputs only as what the procedure delivers. Never render a falsifier or `evidence_needed`. |

Where the document uses the same three sections under other names — a
translation, or a house style — pass `--heading-question`, `--heading-method`
and `--heading-results` to the renderer; the JSON field names stay the same.
The override applies to the generic profile only. A form that merges or adds
sections still needs a table: add it to `assets/mappings.json` and to this file
rather than renaming the generic headings. The generic profile is a fallback,
not a substitute for the funder's form.

## Rendering rules

- **Profile gate.** `meta.funder` selects the table: a named funder uses its own,
  `none` and `other` (with `meta.scheme`) use the generic profile. An absent
  field is refused, not treated as `none`: the author must say whether the
  document has no funder or which funder it is. Set the field to the call's
  funder and revalidate before rendering. The validator does not check this — a
  document without a funder is valid — so the check is the renderer's.
- Prose only. No JSON, no field names, no rule codes in the rendered text.
- Keep the declared `form`: an objective stays an objective in the proposal, an
  interrogative stays a question. Do not rewrite one as the other.
- Section order and numbering follow the profile, not the schema.
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
- An `output` is a deliverable, not a finding. Render it once, as what the
  procedure delivers, in the section the table assigns: at the end of the method
  or work plan, or in PRIN's results section, as outputs. Never open a results
  section for it elsewhere. Where an outcome and an output share an artefact —
  an outcome measured as counts presented in heatmaps, an output that is the
  heatmap — the
  section that receives the outcome says what the map will show, and the work
  plan lists the artefact once. Do not restate the artefact as an expected
  result. Where the procedure names the artefacts it produces, drop the names,
  not the step that produces them: "synthesise narratively with a flow diagram
  and a dataset" becomes "synthesise narratively". A step that produces the
  output stays: "build context-mechanism-outcome configurations in a realist
  synthesis" is method, and the refined programme theory is the output.
- `standpoint` is rendered where the funder asks for rationale or positioning.
  It is never rendered as an impact section and never substitutes for a pathway,
  beneficiary or measure. If it is `none`, one sentence of declaration is
  enough. If it is `undeclared`, do not claim the plan has none: flag the
  silence to the author and, where the form requires positioning, ask for a
  declaration rather than inventing one.
- `limits: "none"` is a declaration that the plan states no limits: do not
  invent a limitation. If `limits` is absent, say the plan does not state limits
  rather than claiming there are none.
- `risks` is rendered with its mitigation in the method section, after the
  limits: each entry says what could go wrong and how it is addressed. Never
  render a risk as a limit, and never invent a mitigation.
- **Outside the document.** Registration, ethics and calendar time sit outside
  `plan.json`: render them from the call's forms, not from requmexre, and do not
  invent an `extensions` field. The procedure's order is not a calendar; see
  Rendering rules.
- Word and page limits change with the call: cut to the limit the author
  supplies, in the call's own units, and say so when none was available.
  `SKILL.md` gives the cut order and the no-padding rule.
