# Reviewing a draft — procedure, report, statuses and form defects

The companion to the review path in `SKILL.md`. Rule codes and their meaning
are in `RULES.md`; the section tables are in `mappings.md`.

## Procedure

A review runs the same five fields read backwards. Do not rewrite the draft into
the skill's voice and do not fill a field the draft does not have: a review
reports what is missing, and the author supplies it.

1. **Locate.** Which funder and call, which sections the draft has, whether it
   is prose or a `plan.json`, and the length limit. Record `meta.funder` when the
   draft or the call supplies one; a draft written for FWO is `fwo` even if the
   field is absent. If neither supplies it, record the funder as unknown: review
   by field, leave the Section column empty, and do not assign a funder to make a
   table fit. If the limit is unavailable, say so: the review can end without it,
   marked as not cut to the call.
2. **Extract — prose only.** Take candidate sentences for each field and quote
   them. Where a field has no sentence, leave it empty and mark it. If the draft
   is already a `plan.json`, skip this step and step 3: quote the fields as they
   stand and do not retype them. A rendered proposal carries no `falsifier` and
   no `evidence_needed` for its claims: the render leaves them in the plan on
   purpose. Mark both missing and ask the author for the plan or for the two
   statements; do not reconstruct them from the prose.
3. **Type — prose only.** Give each extracted question its `form` from the
   sentence as written — `interrogative` or `objective` — never by rewriting it.
4. **Copy and validate.** Copy the draft to `plan.review.json` and leave the
   author's file untouched; never edit the original. Validate the copy with
   `scripts/validate.py`. Every finding names a rule and a path; map it back to
   the draft's sentence and to the section the table assigns it.
5. **Report.** Use the template and the status words below: one row per field or
   result, with the quoted text, the status, the rule if one fired and the
   section affected. Below it, the five checks with their outcome — pass, fail
   with the sentence that fails, not applicable, not verifiable with the reason,
   or a coverage gap with its field path. Read `mappings.md` in both directions
   for coverage.
6. **Propose, then fix.** Return the report first. On the copy only, and with
   the author's agreement, repair the form defects listed below: mechanical
   fixes such as an unambiguous `form`, an extraneous key or a duplicated limit.
   Content defects — a criterion, a citation, a falsifier, a declaration — go
   back to the author with the question that would settle them.

Exit: a review report, a copy that passes validation where the draft supplies
enough to pass, and the named content only the author can provide. A draft that
lacks a required field ends as blocked on that field, not as a passing plan.

## Report template

### Fields

| Field | The draft says | Status | Rule | Section |
|---|---|---|---|---|
| `meta.funder` | the value, or absent; the call if it is known | mapped / other / unknown | `S2` | the funder's sections, or — |
| `questions.primary` | quoted | present / weak / missing | `R1`, `S3` | the section the table assigns |
| `questions.primary.completion_criterion` | quoted, or `none` | present / weak / declared none | `R2`, `S3` | as above |
| `method` | quoted or summarised per subfield, limits excepted | present / weak / missing | `S5` | |
| `method.limits` | list, or `none` | present / weak / declared none | `R7`, `S5` | |
| `results` | one row per result | present / weak / missing / not required | `R5`, `R6`, `S6`, `S7` | |
| `warrant.gap_statement` | quoted | present / weak / missing | `R3`, `S8` | |
| `warrant.evidence` | each string, verbatim | present / weak / missing | `R4`, `S8` | |
| `standpoint` | quoted, or absent | present / weak / declared none / undeclared | `R8`, `S9` | |

The funder row has plan-level statuses: **mapped** (one of the six), **other**
(with a `scheme`, no table) and **unknown** (neither the plan nor the call names
one). For `other` and unknown, leave the Section column empty, review by field
and say the sections were not mapped. Never assign a funder to make a table fit:
an unknown funder is a question for the author, not a default.

### Status words

- **present** — the field has content and no rule fired against it.
- **weak** — content is there but a named check below fails; say which one and
  quote the sentence that fails.
- **missing** — no content at all. For a required field this blocks the review;
  do not fill it. `results` is required unless `meta.funder` is `dfg` or
  `snsf`; for those two forms report **not required** instead of missing.
- **declared none** — an explicit `"none"` in `completion_criterion` or
  `limits`, or `meta.standpoint: none`. It is a declaration, not a defect; `R2`,
  `R7` and `R8` accept it. Report it as declared, never as missing and never as
  present. For the standpoint, `none` is a declaration of no normative
  standpoint; `undeclared` is the silence that says nothing.
- **undeclared** — `meta.standpoint` is `undeclared` and there is no standpoint
  object. It records silence, not neutrality: do not render an impact argument
  as if criteria existed, and do not call the plan neutral.
- **outside model** — a section of the call with no field behind it
  (preliminary work, own research, impact pathways and measures, ethics, budget,
  timetable). Report it; do not invent a field.

A **coverage gap** is not a status of a field: it belongs to check 5, with the
field path.

### The five checks

A check that cannot be run is reported as **not verifiable** with the reason,
never as a pass.

1. **Claim and evidence.** For each hypothesis or expected finding, point to the
   `evidence_needed` entry and the procedure step that produces it. For each
   outcome, point to its `measure` and the step that computes it. If either
   cannot be named, the check fails. For an `output` the check is **not
   applicable**: an output is not a claim and carries no `measure`.
2. **Criterion reachable.** Name the quantity, comparison or typology the
   completion criterion requires, and the step that produces it. With
   `"none"`, record `declared none`: not checkable, not a defect.
3. **Falsifier observable.** The falsifier must name an observation the
   procedure can produce: point to the source and the step. If it names
   something the design cannot observe, the check fails. No falsifier and no
   hypothesis or expected finding means the check is not applicable.
4. **Gap dated and specific.** Every evidence entry carries a year or an
   identifier (`R4`). The gap names what is missing and which studies leave it
   open; "little is known" without an object fails.
5. **Section coverage.** Read `mappings.md` in both directions. Sections →
   fields: list the sections with a field behind them and those without; the
   second list is `outside model`. Fields → sections: for every field present in
   the plan, and for each result kind separately, name the section that receives
   it. A field that a funder's table does not name is a **coverage gap**: report
   its path, say the renderer must place it or leave it out, and never open a
   section the funder does not have. A funder outside the six has no table at
   all: its fields are unsectioned by design, rendered by hand, and are not a
   coverage gap in a table that does not exist.

## Form defects

Every rule is a defect of form; the defect each code names is in `RULES.md`.
What differs is who can supply the fix: a review may repair mechanical defects
on its copy, with the author's agreement; content defects go back to the author
with the question that would settle them.

| Rule | Who fixes it |
|---|---|
| S1 | Missing block: author. Unknown key: review, with agreement |
| S2 | Declaration: author. Misplaced `scheme`: mechanical |
| S3 | Author |
| S4 | Missing: author. Extraneous: review, with agreement |
| S5 | Missing content: author. Wrong `kind`: author decides the material |
| S6 | Author, or remove the optional block with agreement |
| S7 | Author decides; reclassification is mechanical |
| S8 | Author |
| S9 | Author |
| S10 | Optional: review deletes. Required: author |
| R1 | Unambiguous form: review. Otherwise author |
| R2 | Author: the criterion is content |
| R3 | Author |
| R4 | Author: only the author has the source |
| R5 | Author |
| R6 | Author |
| R7 | Duplicate: review moves or deletes it, with agreement. Otherwise author |
| R8 | Author: declaration or removal is a decision |
