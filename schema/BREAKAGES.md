# Where the model breaks: three published plans

v0.4 pilot. Three open-access research plans were encoded by hand against the
schema, run, and re-encoded three times: once after review separated model gaps
from encoding artefacts (v0.2), once after result kinds were added (v0.3), and
once after answer types were widened and sources typed (v0.3 second pass, v0.4).
This version records those revisions and what is still open.

## Revision history

| Version | Change | Effect on the pilot |
|---|---|---|
| v0.1 | first encoding | 1 of 3 passed; R1 on the trial, R5 on the map |
| v0.2 | plural questions, declared form, explicit completion criterion (changes 1–3) | 3 of 3 passed, with results omitted where the plans have none |
| v0.3 | `outcome` with `measure`, `output`, S7 and R5 updated (change 4) | 3 of 3 pass with the results included |
| v0.3, second pass | five more answer types (change 5) | 3 of 3 pass; forest is `synthesis`, bibliotherapy secondary is `mechanistic` |
| v0.4 | typed sources, each with `kind` and `description` (change 6) | 3 of 3 pass; every source classified |
| v0.5 | other + scheme, standpoint, fixture envelope, scope, limits `"none"` (changes 7–11) | 3 of 3 pass; six-funder mappings shipped |

## Model gaps and encoding artefacts

| Finding | First reading | After review | Status |
|---|---|---|---|
| i-MaCHeL, R1 | model gap: objectives rejected | model gap: the plan is written as an aim, as funders ask | fixed by `form` |
| i-MaCHeL, falsifier | not noticed | artefact: a falsifier was written that the protocol does not state | resolved by change 4: the hypothesis is kept, the falsifier is the null result the design tests, and it is flagged as derived |
| i-MaCHeL, criterion | model gap | model gap: no plan states one | fixed by `"none"` |
| i-MaCHeL, limits | not noticed | model gap: absent limits and no limits were indistinguishable | fixed by change 11 (v0.5): `limits: "none"` |
| Forest, R5 | model gap: outputs rejected | artefact: `results` is optional, and the map's outputs were put there by choice. The missing slot for outputs was real | fixed by change 4: outputs have a kind, and the map also reports an outcome |
| Forest, answer_type | model gap | model gap: an evidence map is not one of the six types | fixed by change 5: the map declares `synthesis` |
| Sources, one semantics | not noticed | model gap: a database and a set of measurements were both plain strings | fixed by change 6: each source declares `data`, `literature`, `participants` or `corpus` |
| Bibliotherapy, PASS | "manufactured" | model gap: the completion criterion was required, so one was supplied | fixed by `"none"` |
| Bibliotherapy, second question | model gap | model gap: one question slot | fixed by plural questions |
| Bibliotherapy, funder | model gap | model gap: Wellcome is not in the enum | fixed by change 7 (v0.5): `other` + `scheme` |
| Standpoint `none` | not noticed | a declaration we made, not the plan's | fixed by change 8 (v0.5): `declared \| none \| undeclared` |
| `meta.expect` | model gap | fixture machinery inside the plan | fixed by change 9 (v0.5): negative fixture envelope |
| Registration, ethics, timeline | not noticed | model gap: no home in the plan | fixed by change 10 (v0.5): declared out of scope, no extensions |

Two of the first-round failures were encoding choices, not model gaps. The model
gaps were real, but change 4 shows that some of them were also representational:
the map's outputs and the trial's hypothesis only needed kinds that the schema did
not have.

## The three plans, after v0.5

| File | Plan | Type | Result |
|---|---|---|---|
| `published/imachel.json` | i-MaCHeL, preschool healthy-lifestyle trial | cluster RCT protocol | **PASS** |
| `published/forest-anticipation.json` | Anticipatory forest use behaviours under policy introduction | systematic map protocol | **PASS** |
| `published/bibliotherapy.json` | School-based creative bibliotherapy and mental health | systematic review + realist synthesis protocol | **PASS** |

```bash
cd schema
python3 validate.py published/imachel.json published/forest-anticipation.json published/bibliotherapy.json
```

Exit code 0. The 15 files — 14 fixtures and the template — were migrated to the
new result kinds and still run green (`python3 validate.py`). This is a migration
count, not a list of files to fix: the other two fixtures are negative cases and
intentionally have no `results`.

## What changed in the encodings

- `results` is present in all three plans. none of it is supplied text: each claim
  paraphrases a sentence in the document, and each kind is one the document
  supports.
- The trial keeps its hypothesis, with the null result of its primary analysis as
  the falsifier, and adds two outcomes with their measures.
- The systematic map reports one outcome (the distribution of studies by policy,
  behaviour, income level and biome) and two outputs (the map/dataset and the
  evidence atlas).
- The review reports one outcome (range and strength of evidence by outcome) and
  one output (the refined programme theory).
- Each source now declares its kind: the trial's dyads are `participants` and its
  measurements `data`; both reviews draw `literature`.
- `deliverable` is now `output`. The two were synonyms; keeping both would have
  given the same artefact two names.
- No field is supplied by the encoder beyond `meta` (ours by design), the
  paraphrases, and the trial's falsifier, which states the null its analysis
  tests.

## Plan by plan

### i-MaCHeL — passes

Objective declared as such, with a tertium taken from the primary comparison; two
secondary objectives encoded. Sources: `participants` (the dyads) and `data` (the
measurements and records). Results: one hypothesis and two outcomes, with the
outcome measures the protocol names. Still missing: the funding statement was not
captured, so `funder` is omitted; `answer_type: comparative` fits this plan. The
protocol states no limits, so `limits` is `"none"` (change 11).

### Anticipatory forest use — passes

Interrogative question, criterion `"none"`, sources typed as `literature`,
outputs that are outputs. The evidence-map question declares `synthesis`
(change 5).

### Creative bibliotherapy — passes

Both questions encoded; the mechanisms question declares `mechanistic` (change
5), and the sources are `literature`. Results: one outcome and one output. The
funder is `other` with `scheme: "Wellcome Trust"` (change 7), and the standpoint
is `undeclared` (change 8).

## Still open

Nothing from the pilot remains open. Changes 1–11, the six-funder mappings and
the v0.5 release are closed.

Changes 1–6 touched S3, S5, S6, S7, R1, R2, R5, all fixtures, the template, the
published plans, the skill, the README and the site.

## What held

- `warrant.gap_statement` and dated evidence: the one slot that worked in all
  three without invention.
- `scope`: population, setting and period were always present.
- `method.procedure`: long, but always there, and always in order.
- `validity_conditions` and `limits` where the plan states them, including
  i-MaCHeL's explicit `"none"`: R7 produced no false positives.
- R4 (dated evidence), R5 (outputs only) and R6 (falsifier) produced no false
  positives on the three plans.
- R1 checks the text against the declared form and produced no false positives.
- The structural layer accepted all three encodings without a single S finding.
- `sources`: every plan named its material; typing it required one decision per
  entry, and no entry was ambiguous.

## Next

The v0.5 release closes changes 1–11 and the six-funder mappings. The v1.0
stable schema and citation remain.

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
