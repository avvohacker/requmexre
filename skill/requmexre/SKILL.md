---
name: requmexre
description: Build, validate, check and render a document typed as research question, methodology and expected results, with warrant and standpoint. Use when drafting, reviewing or reformatting a grant proposal, a doctoral plan, or any other document that uses those three headings; FWO, PRIN, VUB, Horizon, DFG and SNSF have section tables, and every other document uses the generic three-section profile.
---

# requmexre

A requmexre document has three slots and two guards. The slots are the research
question, the methodology and the expected results; the guards are the warrant
(why the question is still open) and the standpoint (the normative premises the
document works from). This skill writes those five fields as JSON, validates the
file against the schema, checks the sources cited in the warrant, then renders
the document into the sections a funder asks for or into the generic
three-section profile.

## When to use it

- Drafting a research document, a doctoral research plan, a proposal section or
  any other document that has to state a question, a method and results.
- Reviewing a draft: the validator names the empty slots and the circular ones —
  a question that is a statement, a criterion that repeats the question, a
  falsifier that repeats the claim. The review path is
  [below](#reviewing-a-draft).
- Reformatting a document written for one funder into the sections of another,
  or into the generic Research Question / Methodology / Expected Results shape.

Not for: budgets, CVs, ethics annexes, letters of support, or the parts of a
proposal that are not the document itself.

## The five fields

| Field | Required |
|---|---|
| `questions` | `primary` with `text`, `form`, `answer_type`, `scope`, `completion_criterion`; optional `secondary` |
| `method` | `approach`, `sources`, `procedure`; optional `validity_conditions`, `limits`, `risks` |
| `results` | required unless `meta.funder` is `dfg` or `snsf`; `claim` + `kind`, with `falsifier` and `evidence_needed` for claims, `measure` for outcomes |
| `warrant` | `gap_statement`, `evidence` |
| `standpoint` | optional; `normative_premises`, `criteria`, declared in `meta.standpoint` |

Structural rules S1–S10 and semantic rules R1–R8 are in
[`references/RULES.md`](references/RULES.md). Read them before the first run: the
validator will refuse a plan that breaks them, and the rules are what the five
fields mean.

## Procedure

Run the phases in order. Each has an exit condition; do not carry a weak field
forward to be fixed later.

### 1. Detect

Establish what is being asked and for whom.

- Which funder and which call? FWO, PRIN, VUB, Horizon, DFG and SNSF have
  section tables in [`references/mappings.md`](references/mappings.md). A funder
  outside the six is `meta.funder: "other"` with `meta.scheme` naming it; a
  document with no funder may leave `meta.funder` absent. Both use the generic
  profile, which is the default.
- Record the funder in `meta.funder` when it is known: `fwo`, `prin`, `vub`,
  `horizon`, `dfg`, `snsf`, `other` with `meta.scheme`, or `none` for a document
  explicitly without a funder. A document you will render into a named funder's
  sections must name that funder; absence, `none` and `other` use the generic
  three-section profile.
- Is there a draft to convert, or is the document new? If there is a draft,
  extract candidate sentences for each field before writing anything.
- What length does the call allow, in its own units (pages or characters, per
  section)? Take it from the form or the author; if neither is at hand, say it is
  unknown and do not guess.
- Is a standpoint declared? If the document argues from normative premises —
  equity, sustainability, safety — the answer is `declared`; if it says it has
  none, `none`; if it says nothing, `undeclared`. Do not leave the standpoint
  unanswered: `meta.standpoint` is required, and `undeclared` records silence
  rather than inventing a position.

Exit: the funder recorded in `meta.funder`, or `none`, or an explicit note that
the document has no funder and uses the generic profile; a source draft (or
none), `meta.standpoint`, and the length limit or a note that it is unknown.

### 2. Questions

Write `questions.primary.text`, then decide its `form`: `interrogative` if the
sentence is a question, `objective` if it is written as an aim ("This study
evaluates..."). Do not convert one into the other: funders ask for objectives as
often as for questions, and R1 checks the text against the form declared.

- `answer_type` names the kind of answer: `descriptive`, `exploratory`,
  `comparative`, `causal`, `evaluative`, `methodological`, `synthesis`,
  `mechanistic`, `feasibility`, `validation` or `other`. Comparative requires the
  `tertium_comparationis`, the dimension on which the cases are compared.
  Evaluative requires `criteria` and the `operationalisation` that turns each into
  something measurable. Every other type carries neither. Use `synthesis` for a
  map, review or meta-analysis, `mechanistic` for how or why something works, and
  `other` only when none of the named types fits.
- `scope` bounds the answer: population, setting, period, corpus.
- `completion_criterion` says what would count as an answer — an estimate with an
  uncertainty, a typology that covers the variation, a comparison that holds. If
  the plan states none, write `"none"`; do not invent one. When present, it must
  not restate the question (R2).
- `questions.secondary` holds the secondary questions and objectives: `text` and
  `form` are enough, the rest is optional.

Exit: a question that a reader could answer with evidence, and could recognise
as answered.

### 3. Method

- `approach`: the design in one sentence — experiment, difference-in-differences,
  ethnography, corpus study, proof.
- `sources`: what the evidence comes from, as `{kind, description}`. `kind` is
  `data` (datasets, records, measurements), `literature` (databases, citation
  chasing, grey literature), `participants` (people, sites or organisations
  recruited) or `corpus` (documents or texts analysed). The description says what
  exactly is used, concretely enough to find it.
- `procedure`: the steps, in the order they happen, with the sample and the analysis named. Order only: no dates, durations, work packages or roles.
- `validity_conditions`: what has to hold for the finding to stand — matching,
  instrument stability, response rate, coding independence.
- `limits`: what the design does not cover. A limit is not a condition (R7) and
  not an apology. When the plan states no limits, write `"none"`; absence means
  the field was not addressed.
- `risks`: what could go wrong and the mitigation. A risk is not a limit, and a
  mitigation is not an apology. Each entry has `risk` and `mitigation`. If the
  plan states no risks, omit the field; do not invent one.

Exit: a method a competent stranger could execute, and a list of the ways it
could fail.

### 4. Results

Required unless `meta.funder` is `dfg` or `snsf`, whose forms have no results
section. For those two, omit the block; do not invent one.

- `kind` is `hypothesis`, `expected_finding`, `outcome` or `output`.
- A hypothesis or an expected finding needs a `falsifier`: the observation that
  would show it false, stated as an observation, not as its negation (R6). It also
  needs `evidence_needed`: the data that would settle it.
- An outcome is a quantity the study will estimate: it needs a `measure` and
  carries no falsifier (S7).
- An output is produced, not tested: no falsifier and no measure (S7).
- At least one result must be a claim or an outcome; a list of outputs answers
  nothing (R5).

Exit: every claim has an observation that could defeat it.

### 5. Guards

- `warrant.gap_statement`: what is missing, contradictory or untested in the
  literature — not a summary of the field, and not the question again (R3).
- `warrant.evidence`: at least one dated or identifiable source (R4). Write each
  entry as the citation itself — who produced it, what it is, when, plus a DOI,
  URL, ISBN or PMID when it has one — not as a note about a source.
- `standpoint`: if declared, normative premises and the criteria that follow from
  them; if `none` or `undeclared`, the object is absent (R8). `none` says the
  plan explicitly has no standpoint; `undeclared` says it does not address one.

Exit: the document says why the question is worth asking now, and from where it
speaks.

### 6. Citations

Run `python3 scripts/verify_citations.py plan.json` on the validated file. It
extracts a DOI, PMID, arXiv ID, ISBN or URL from every `warrant.evidence` entry,
resolves the record, and compares the citation's title, year and author with it.
It also reports open-access status and, when an abstract is available, a lexical
overlap with the gap statement.

- `FAIL` — the source was not found, or its title or year disagrees with the
  citation. Correct the citation or the claim before rendering.
- `WARN` — no identifier, an unreachable service, a restricted URL or a
  paywalled full text. This is not a pass: add an identifier where possible and
  record the entry as unverified.
- Read the abstract before treating a source as support. The checker verifies
  the source's metadata, not the claim; it never reads a paywalled full text.

Exit: every citation resolved, or the unresolved ones named with their reason.

## Reviewing a draft

A review runs the same five fields read backwards. Do not rewrite the draft into
the skill's voice and do not fill a field the draft does not have: a review
reports what is missing, and the author supplies it. Load
[`references/review.md`](references/review.md) only for a review; it owns the
procedure, report template, status words, five checks and form defects.

Exit: a review report, a copy that passes validation where the draft supplies
enough to pass, and the named content only the author can provide. A draft that
lacks a required field ends as blocked on that field, not as a passing plan.

## Validation gate

Write the document to `plan.json` with `"meta": {"standpoint": ...}`. Run the
validator from the skill directory with the file's path: it travels with the
skill, so no checkout of the repository is needed.

```bash
python3 scripts/validate.py /path/to/plan.json          # PASS/FAIL per file
python3 scripts/validate.py --json /path/to/plan.json   # same verdict, as JSON
```

`--json` carries `tool`, `version`, `scope` (`fixtures` or `files`), `ok`,
`total`, `passed`, `failed` and one entry per file with `path`, `ok`, `expected`,
`findings` (`rule`, `path`, `message`) and `note`.

Then fix every finding and run again. Do not render a document that does not
exit 0. The validator checks form, not truth: a clean file can still be a bad
document, and you remain responsible for the content. Run the citation check
after the validator; it is a separate gate and its `FAIL` blocks rendering.

## Rendering

Map fields onto the selected profile — never paste JSON into a proposal, and
never rename a section a funder owns. The tables, the section names and the
caveats for each funder, plus the generic profile, are in
[`references/mappings.md`](references/mappings.md); its rendering rules are the
single source for the profile gate, falsifiers, the work plan, citations and the
sections outside the document, and are not repeated here.

[`scripts/render.py`](scripts/render.py) applies the table: `python3
scripts/render.py plan.json` writes the draft to stdout, `--out draft.md` to a
file. A document with no `meta.funder` renders through the generic profile by
default; `none` and `other` do the same (Research Question, Methodology,
Expected Results), and `other` carries a warning that those headings are the
model's, not the form's. It warns on stderr when a field present in the document has no section
in the selected table. For a generic document whose three headings are
translated or named differently, pass `--heading-question`, `--heading-method`
and `--heading-results`; the JSON fields stay the same, and the override applies
to the generic profile only. The draft copies the document's wording; it is a
draft to edit, not a finished proposal.

Length is an input, not a guess. Cut the draft to the page or character limit
the call sets, in the units the call uses. If the limit is not available, ask
for the form or the figure and leave the draft marked as unchecked against the
call. Cut in this order: examples and long enumerations from the state of the
art; definitions restated in the method; secondary objectives the question does
not need; method detail a competent stranger would not need to reproduce the
design. Never cut the question, the completion criterion, the claim of an
expected result, or the gap statement. Never pad: a short draft under the limit
stays short.

[`references/fwo-example.md`](references/fwo-example.md) shows the result: a
claim without its falsifier, its test in the method, and the evidence cited
verbatim.

## Files

The template at `assets/template.json` is a valid document, not a form with
blanks: copy it, replace the content, keep the shape. The validator, renderer,
citation checker, schema, template, rules and section tables travel in
`scripts/`, `assets/` and `references/`, byte-identical to the repository's
`schema/` copies; CI fails if they drift, and nothing else in the repository is
needed to validate, check or render a document. Read `references/RULES.md`
before the first validation, `mappings.md` before rendering, and `review.md`
only for a review; do not load every reference at the start. Scripts and assets
are for execution, not wholesale reading.

## Limits

- Six funders have section tables: FWO, PRIN, VUB, Horizon, DFG and SNSF. The
  schema is v1.2. Any other document that uses Research Question, Methodology
  and Expected Results — including one with no `meta.funder` — renders through
  the generic profile; a form that renames or merges those sections needs its
  own table.
- A funder outside the six may use `funder: "other"` and `scheme` to name it; an
  absent field, `none`, and `other` get the generic headings, not a named
  funder's own. Check them against the call.
- The citation checker resolves metadata from OpenAlex, Crossref, PubMed, arXiv,
  Open Library or the URL. It cannot read a paywalled full text or decide
  whether a source supports a specific claim; it reports that limit rather than
  guessing. `REQMEXRE_CONTACT_EMAIL` and `NCBI_API_KEY` are optional; no key is
  required.
- Fixtures and the template are synthetic: structure from the funder documents,
  content illustrative.
- Registration, ethics and calendar time — dates, durations, work packages,
  milestones — are outside the document: see the rendering rules in
  `references/mappings.md`. Page and character limits are not modelled either;
  the length rule above says how to cut.
