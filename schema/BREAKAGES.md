# Where the model breaks: three published plans

v0.2 pilot, revised after review. Three open-access research plans were encoded by
hand against the schema, run, then re-encoded against schema v0.2 and run again.
The first reading mixed two different things: gaps in the model, and artefacts of
how the plans were encoded. This version separates them.

## Revision: model gaps and encoding artefacts

| Finding | First reading | After review | Status |
|---|---|---|---|
| i-MaCHeL, R1 | model gap: objectives rejected | model gap: the plan is written as an aim, as funders ask | fixed by `form` (change 2) |
| i-MaCHeL, falsifier | not noticed | artefact: a falsifier was written that the protocol does not state; its hypothesis ("strong potential to be effective") is not testable as written | encoding removed; results omitted. Gap 4 open |
| i-MaCHeL, criterion | model gap | model gap: no plan states one | fixed by `"none"` (change 3) |
| Forest, R5 | model gap: outputs rejected | artefact: `results` is optional, and the map's outputs were put there by choice. The missing slot for outputs is real, but it did not cause the failure | encoding removed; results omitted. Gap 4 open |
| Forest, answer_type | model gap | model gap: an evidence map is not one of the six types | open (change 5) |
| Bibliotherapy, PASS | "manufactured" | model gap: the completion criterion was required, so one was supplied | fixed by `"none"`; now passes without invention |
| Bibliotherapy, second question | model gap | model gap: one question slot | fixed by plural questions (change 1) |
| Bibliotherapy, funder | model gap | model gap: Wellcome is not in the enum | open (change 7) |
| Standpoint `none` | not noticed | a declaration we made, not the plan's | open (change 8) |
| `meta.expect` | model gap | fixture machinery inside the plan | open (change 9) |

Two of the three first-round failures were therefore encoding choices: R5 on the
forest map, and the supplied falsifier on the trial. The model gaps that remain
are real, but they were not what made the run red.

## The three plans, after v0.2

| File | Plan | Type | Result |
|---|---|---|---|
| `published/imachel.json` | i-MaCHeL, preschool healthy-lifestyle trial | cluster RCT protocol | **PASS** |
| `published/forest-anticipation.json` | Anticipatory forest use behaviours under policy introduction | systematic map protocol | **PASS** |
| `published/bibliotherapy.json` | School-based creative bibliotherapy and mental health | systematic review + realist synthesis protocol | **PASS** |

```bash
cd schema
python3 validate.py published/imachel.json published/forest-anticipation.json published/bibliotherapy.json
```

Exit code 0. The 14 fixtures migrated to the new shape and still run green
(`python3 validate.py`).

## What changed in the encodings

- `questions` is plural: i-MaCHeL's two secondary objectives and bibliotherapy's
  mechanism question now have a home instead of being dropped.
- Every question declares its `form`. i-MaCHeL is an objective and says so; the
  other two are interrogative. Nothing was rewritten to please R1.
- `completion_criterion` is `"none"` in all three: no plan states one, and none
  was invented.
- `results` is omitted in all three, because no protocol states findings. The
  trial's hypothesis is left out: encoding it would require a falsifier the
  document does not have.
- No field is now supplied by the encoder beyond `meta` (ours by design) and
  paraphrases of sentences that exist in the documents.

## Plan by plan

### i-MaCHeL — passes

Objective declared as such, with a tertium taken from the primary comparison; two
secondary objectives encoded. Still missing: the hypothesis cannot be represented
without inventing its falsifier (gap 4); the outcomes are measures, not results
(gap 4); the funding statement was not captured, so `funder` is omitted.

### Anticipatory forest use — passes

Interrogative question, criterion `"none"`, sources that read naturally as
sources. Still missing: the evidence-map question is forced into `descriptive`
(gap 5); the map, dataset and atlas have no slot anywhere (gap 4); they are
recorded here rather than squeezed into `results`.

### Creative bibliotherapy — passes

Both questions encoded; the mechanisms question carries no answer type because
none of the six fits (gap 5). Criterion `"none"`. Still missing: the Wellcome
Trust cannot be named in `funder` (gap 7); the undeclared standpoint is recorded
as `"none"` by us (gap 8).

## Still open (changes 4–11)

| # | Breakage | Where | Seen in | Change |
|---|---|---|---|---|
| 4 | Results conflate findings and outputs | S6, S7, R5 | forest, i-MaCHeL | add `kind: outcome` (with `measure`) and `kind: output`; R5 only for claims |
| 5 | Answer types too narrow | S3 `answer_type` | forest, bibliotherapy | add `synthesis`, `mechanistic`, `feasibility`, `validation`, `other` |
| 6 | `sources` has one semantics | S5 | i-MaCHeL vs forest | typed sources: `{kind: data \| literature \| participants \| corpus, description}` |
| 7 | Funder list is closed | S2 | bibliotherapy | free string, or `other` plus `scheme` |
| 8 | Standpoint is binary | S2, R8 | all three | `declared \| none \| undeclared` |
| 9 | Fixture machinery sits inside the plan | S2 `meta.expect` | all three | move `expect` to a fixture envelope |
| 10 | Registration, ethics, timeline have no home | S1 `additionalProperties` | all three | declare them out of scope, or allow `extensions` |
| 11 | Absent limits look like no limits | S5 | i-MaCHeL | allow `"none"` as an explicit value |

Changes 1–3 are in: plural questions, declared form, explicit completion
criterion. They touched S3, R1, R2, the 14 fixtures, the template, the skill and
the README.

## What held

- `warrant.gap_statement` and dated evidence: the one slot that worked in all
  three without invention.
- `scope`: population, setting and period were always present.
- `method.procedure`: long, but always there, and always in order.
- `validity_conditions` and `limits` where the plan states them: R7 produced no
  false positives.
- R4 (dated evidence) produced no false positives.
- R1 now checks the text against the declared form instead of assuming one, and
  produced no false positives on the three plans.
- The structural layer accepted all three encodings without a single S finding.

## Next

Change 4 first: it is the only remaining place where a real plan has to leave
something out (the map's outputs, the trial's hypothesis). Then 5–7 in one pass,
then 8–11. The v0.3 mappings (Horizon, DFG, SNSF) should follow, not precede, the
result-kinds change, or they will encode the old shape three more times.

## Sources encoded

- Rashid AF, Wafa SW, Abd Talib R, Abu Bakar NM. An interactive Malaysian
  Childhood Healthy Lifestyle (i-MaCHeL) intervention programme to change
  weight-related behaviour in preschool child-parent dyads: study protocol of a
  cluster randomised controlled trial. *PLOS ONE*. 2022;17(10):e0276843.
  doi:10.1371/journal.pone.0276843
- Evidence of anticipatory forest use behaviours under policy introduction: a
  systematic map protocol. *Environmental Evidence*. 2023.
  doi:10.1186/s13750-023-00307-0
- The impact of school-based creative bibliotherapy interventions on child and
  adolescent mental health: a systematic review and realist synthesis protocol.
  *Systematic Reviews*. 2024;13:86. doi:10.1186/s13643-024-02482-8

All three are open access; the encodings paraphrase them and reproduce no
substantial portion. They remain the property of their publishers.
