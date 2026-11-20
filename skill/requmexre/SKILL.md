---
name: requmexre
description: Build, validate and render a research plan typed as research question, methodology and expected results, with warrant and standpoint. Use when drafting, reviewing or reformatting a grant proposal or a doctoral research plan for FWO, PRIN or VUB.
---

# requmexre

A research plan is a document with three slots and two guards. The slots are the
research question, the methodology and the expected results; the guards are the
warrant (why the question is still open) and the standpoint (the normative
premises the plan works from). This skill writes those five fields as JSON,
validates the file against the schema, then renders it into the sections a funder
asks for.

## When to use it

- Drafting a research plan, a doctoral research plan or a proposal section that
  has to state a question, a method and results.
- Reviewing a draft: the validator names the empty slots and the circular ones —
  a question that is a statement, a criterion that repeats the question, a
  falsifier that repeats the claim.
- Reformatting a plan written for one funder into the sections of another.

Not for: budgets, CVs, ethics annexes, letters of support, or the parts of a
proposal that are not the plan.

## The five fields

| Field | Holds | Required |
|---|---|---|
| `question` | `text`, `answer_type`, `scope`, `completion_criterion`; `tertium_comparationis` for comparative, `criteria` and `operationalisation` for evaluative | yes |
| `method` | `approach`, `sources`, `procedure`; `validity_conditions`, `limits` | yes |
| `results` | list of `claim` + `kind`; `falsifier` and `evidence_needed` for hypotheses and expected findings | no |
| `warrant` | `gap_statement`, `evidence` | yes |
| `standpoint` | `normative_premises`, `criteria`; declared, or `meta.standpoint` set to `none` | no |

Structural rules S1–S10 and semantic rules R1–R8 are in
[`schema/RULES.md`](../../schema/RULES.md). Read them before the first run: the
validator will refuse a plan that breaks them, and the rules are what the five
fields mean.

## Procedure

Run the phases in order. Each has an exit condition; do not carry a weak field
forward to be fixed later.

### 1. Detect

Establish what is being asked and for whom.

- Which funder and which call? FWO, PRIN and VUB are mapped in
  [`references/mappings.md`](references/mappings.md); Horizon, DFG and SNSF are
  not mapped in v0.1 and should be handled by hand.
- Is there a draft to convert, or is the plan new? If there is a draft, extract
  candidate sentences for each field before writing anything.
- Is a standpoint declared? If the plan argues from normative premises — equity,
  sustainability, safety — the answer is `declared`; if it claims none, `none`.
  Do not leave the question unanswered: `meta.standpoint` is required.

Exit: a funder (or `none`), a source draft (or none), and `meta.standpoint`.

### 2. Question

Write `question.text` as a question, not as an objective. "This project studies
X" is an objective; "How does X vary with Y in Z?" is a question.

- `answer_type` decides what else is required. Comparative: name the
  `tertium_comparationis`, the dimension on which the cases are compared.
  Evaluative: name `criteria` and write the `operationalisation` that turns each
  into something measurable.
- `scope` bounds the answer: population, setting, period, corpus.
- `completion_criterion` says what would count as an answer — an estimate with an
  uncertainty, a typology that covers the variation, a comparison that holds.
  It must not restate the question (R2).

Exit: a question that a reader could answer with evidence, and could recognise
as answered.

### 3. Method

- `approach`: the design in one sentence — experiment, difference-in-differences,
  ethnography, corpus study, proof.
- `sources`: what the evidence comes from, each entry concrete enough to find
  (archive, dataset, corpus, series of interviews).
- `procedure`: the steps, in the order they happen, with the sample and the
  analysis named.
- `validity_conditions`: what has to hold for the finding to stand — matching,
  instrument stability, response rate, coding independence.
- `limits`: what the design does not cover. A limit is not a condition (R7) and
  not an apology.

Exit: a method a competent stranger could execute, and a list of the ways it
could fail.

### 4. Results

Only if the funder asks for results, or if the plan needs them to be checkable.

- `kind` is `hypothesis`, `expected_finding` or `deliverable`.
- A hypothesis or an expected finding needs a `falsifier`: the observation that
  would show it false, stated as an observation, not as its negation (R6). It also
  needs `evidence_needed`: the data that would settle it.
- A deliverable is produced, not falsified: no falsifier (S7).
- At least one result must be a claim about the world; a list of deliverables
  answers nothing (R5).

Exit: every claim has an observation that could defeat it.

### 5. Guards

- `warrant.gap_statement`: what is missing, contradictory or untested in the
  literature — not a summary of the field, and not the question again (R3).
- `warrant.evidence`: at least one dated or identifiable source (R4).
- `standpoint`: if declared, normative premises and the criteria that follow from
  them; if none, the object is absent and `meta.standpoint` is `none` (R8).

Exit: the plan says why the question is worth asking now, and from where it
speaks.

## Validation gate

Write the plan to `plan.json` with `"meta": {"expect": "valid", "standpoint": ...}`
and run:

```bash
cd schema
python3 validate.py ../plan.json
```

Then fix every finding and run again. Do not render a plan that does not exit 0.
The validator checks form, not truth: a clean file can still be a bad plan, and
you remain responsible for the content.

## Rendering

Map fields onto the funder's sections — never paste JSON into a proposal, and
never rename a section. The tables, the section names and the caveats for each
funder are in [`references/mappings.md`](references/mappings.md).

Falsifiers and `evidence_needed` stay in `plan.json`: they are there to test the
plan, not to be submitted. What goes into the proposal is the claim, the method
that would produce the evidence, and the gap that makes it worth producing.

## Files

```
SKILL.md                     this file
references/mappings.md       FWO, PRIN and VUB section mappings
assets/template.json         a complete valid plan to copy and adapt
```

The template is a valid plan, not a form with blanks: copy it, replace the
content, keep the shape.

## Limits

- Three funders are mapped; Horizon, DFG and SNSF are not (roadmap v0.3).
- The validator checks form, not truth, not citations, not fit between a claim
  and its evidence.
- Fixtures and the template are synthetic: structure from the funder documents,
  content illustrative.
