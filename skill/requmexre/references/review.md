# Reviewing a draft — report, statuses and form defects

The companion to the review path in `SKILL.md`. Rule codes and their meaning
are in `RULES.md`; the section tables are in `mappings.md`.

## Report template

### Fields

| Field | The draft says | Status | Rule | Section |
|---|---|---|---|---|
| `meta.funder` | the value, or absent; the call if it is known | mapped / other / unknown | `S2` | the funder's sections, or — |
| `questions.primary` | quoted | present / weak / missing | `R1`, `S3` | the section the table assigns |
| `questions.primary.completion_criterion` | quoted, or `none` | present / weak / declared none | `R2`, `S3` | as above |
| `method` | quoted or summarised per subfield, limits excepted | present / weak / missing | `S5` | |
| `method.limits` | list, or `none` | present / weak / declared none | `R7`, `S5` | |
| `results` | one row per result | present / weak / missing | `R5`, `R6`, `S6`, `S7` | |
| `warrant.gap_statement` | quoted | present / weak / missing | `R3`, `S8` | |
| `warrant.evidence` | each string, verbatim | present / weak / missing | `R4`, `S8` | |
| `standpoint` | quoted, or absent | present / weak / declared none / undeclared | `R8`, `S9` | |

The funder row has plan-level statuses: **mapped** (one of the six), **other**
(with a `scheme`) and **unknown** (neither the plan nor the call names one).

There are three cases. `funder: other` with a `scheme` has no table but a named
scheme. A plan with no funder at all, and no call to supply one, is recorded as
**funder unknown**. In both cases leave the Section column empty, review by
field, and say the sections were not mapped. Never assign a funder to make a
table fit: an unknown funder is a question for the author, not a default.

### Status words

- **present** — the field has content and no rule fired against it.
- **weak** — content is there but a named check below fails; say which one and
  quote the sentence that fails.
- **missing** — no content at all. For a required field this blocks the review;
  do not fill it.
- **declared none** — an explicit `"none"` in `completion_criterion` or
  `limits`, or `meta.standpoint: none`. It is a declaration, not a defect; `R2`,
  `R7` and `R8` accept it. Report it as declared, never as missing and never as
  present. For the standpoint, `none` is a declaration of no normative
  standpoint; `undeclared` is the silence that says nothing.
- **undeclared** — `meta.standpoint` is `undeclared` and there is no standpoint
  object. It records silence, not neutrality: do not render an impact argument
  as if criteria existed, and do not call the plan neutral.
- **outside model** — a section of the call with no field behind it
  (preliminary work, own research, ethics, budget, timetable). Report it; do not
  invent a field.

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
5. **Section coverage.** Read `mappings.md` in reverse. List the sections with a
   field behind them and those without. The second list is `outside model`.

## Form defects

Every rule is a defect of form. What differs is who can supply the fix: a review
may repair mechanical defects on its copy, with the author's agreement; content
defects go back to the author with the question that would settle them.

| Rule | Defect | Who fixes it |
|---|---|---|
| S1 | Closed root; a required block missing, or an unknown key present | Missing block: author. Unknown key: review, with agreement |
| S2 | `meta` closed; `standpoint` missing or outside its three values; `scheme` present without `funder: other`, or missing with it | The declaration is the author's; a misplaced `scheme` is mechanical |
| S3 | A question missing `text` or `form`; the primary missing `answer_type`, `scope` or `completion_criterion` | Author |
| S4 | Comparative without `tertium`; evaluative without `criteria` or `operationalisation`; any other type carrying one of them | Missing: author. Extraneous: review, with agreement |
| S5 | `method` missing `approach`, `sources` or `procedure`; a source with the wrong `kind`; `limits` a string other than `none` | Missing content: author. Wrong `kind`: author decides the material |
| S6 | `results` empty; a result missing `claim` or `kind` | Author, or remove the optional block with agreement |
| S7 | Hypothesis or expected finding without `falsifier` or `evidence_needed`; outcome without `measure` or with a falsifier; output with either | Author decides whether to reclassify or supply; reclassification is mechanical |
| S8 | `warrant` missing `gap_statement`, or `evidence` empty | Author |
| S9 | `standpoint` missing `normative_premises` or `criteria` | Author |
| S10 | A string blank or only whitespace | Review deletes it if optional; author if required |
| R1 | The text does not match the declared `form` | Review may flip `form` when the text is unambiguous; otherwise author |
| R2 | The completion criterion restates its question | Author: the criterion is content |
| R3 | The gap statement restates the question | Author |
| R4 | An evidence entry has no year and no identifier | Author: only the author has the source |
| R5 | Every result is an `output` | Author |
| R6 | The falsifier restates the claim | Author |
| R7 | A limit restates a validity condition | Review moves or deletes a duplicate, with agreement; otherwise author |
| R8 | `meta.standpoint` and the standpoint body disagree | Author: declaration or removal is a decision |
