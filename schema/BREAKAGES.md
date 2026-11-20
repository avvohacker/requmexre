# Where the model breaks: three published plans

v0.2 pilot. Three open-access research plans were encoded by hand against
`schema/requmexre.schema.json` and run through `validate.py`. The encodings are
paraphrases, not reproductions, and `meta` is ours, not the plans'. Where a
required field had no counterpart in the document, it was supplied; those places
are marked **[supplied]** and are the most useful part of the result.

## The three plans

| File | Plan | Type | Published | Result |
|---|---|---|---|---|
| `published/imachel.json` | i-MaCHeL, preschool healthy-lifestyle trial | cluster RCT protocol | PLOS ONE, 2022 | **FAIL, R1** |
| `published/forest-anticipation.json` | Anticipatory forest use behaviours under policy introduction | systematic map protocol | Environmental Evidence, 2023 | **FAIL, R5** |
| `published/bibliotherapy.json` | School-based creative bibliotherapy and mental health | systematic review + realist synthesis protocol | Systematic Reviews, 2024 | PASS, after one supplied field |

## Reproduce

```bash
cd schema
python3 validate.py published/imachel.json published/forest-anticipation.json published/bibliotherapy.json
```

Exit code 1 is the pilot result, not a regression. The default run
(`python3 validate.py`) still covers only `cases/`, so CI stays green: these are
applications of the model, not fixtures.

## i-MaCHeL — FAIL R1

Rashid et al., PLOS ONE 2022, doi:10.1371/journal.pone.0276843.

**What the plan contains.** A single-blind two-group cluster RCT, 460 child-parent
dyads in 12 preschools, 3-month intervention, outcomes at 3 and 9 months. The
document has a background, a long gap statement, aims, objectives, design,
eligibility, sample size, randomisation, intervention, outcomes, statistical
methods and a significance section.

**What broke.**

- The question is written as an aim: "The general aim of this study is to
  evaluate the efficacy of..." R1 fires because the model accepts only an
  interrogative. Every protocol in this sample does the same thing; funders ask
  for objectives, not questions.
- The plan has one primary and two secondary objectives. `question` is a single
  object, so the secondary objectives have nowhere to go. They were left out.
- No sentence states what would count as an answer. The completion criterion was
  **[supplied]** from the outcome and the analysis plan.
- The results slot has no counterpart: the protocol reports outcomes and an
  analysis, not findings. The abstract's hypothesis ("strong potential to be
  effective") is too vague to falsify, so the falsifier was **[supplied]** from
  the primary outcome. R6 passes only because a new sentence was written.
- `method.sources` was filled with participants and instruments. In the document
  those are the study population and the measurements, not sources.
- There is no limitations section; `limits` was left absent. Single-blinding and
  the two-district setting are facts of the design, not declared limits.
- The funding statement was not captured in the read, so `funder` is omitted
  rather than guessed.

**What held.** The warrant and its evidence mapped cleanly (Malaysia, high-income
trials, classroom plus web); `method.procedure` carried the trial in order;
`validity_conditions` were present in substance (independent randomisation,
intention-to-treat, cluster adjustment) even if never collected in one place.

## Anticipatory forest use — FAIL R5

Environmental Evidence 2023, doi:10.1186/s13750-023-00307-0.

**What the plan contains.** A systematic map with a PIO frame, a tested search
string, four databases, two dissertation platforms, Google Scholar, 67 websites,
citation chasing, kappa-checked screening, narrative synthesis, an EviAtlas map
and an online dataset.

**What broke.**

- The question is interrogative and fits the schema word for word. It is also the
  only plan here whose `method.sources` reads naturally as sources.
- `answer_type` had to be forced to `descriptive`: the question is about the state
  of the evidence, not about forests. None of the six types covers an evidence
  map.
- The completion criterion was **[supplied]**; the plan says what it will search
  and code, not what would count as an answer.
- Its outputs are a map, a dataset and an atlas. Encoded as two `deliverable`
  results, R5 fires: "only deliverables". A systematic map at protocol stage has
  no findings, and the only slot for its outputs is the one that demands a claim
  about the world.
- `limits` and `validity_conditions` are present, distinct and specific
  (English-only, no design exclusion, benchmark coverage, double screening); R7
  did not fire.
- SNSF fits the `funder` enum, the only plan here that does.

**What held.** Question, scope, warrant, evidence, procedure and limits all mapped
without distortion. This is the closest of the three to the model.

## Creative bibliotherapy — PASS, with one supplied field

Systematic Reviews 2024, doi:10.1186/s13643-024-02482-8.

**What the plan contains.** Two questions (impacts; mechanisms and contexts), six
databases, citation searching, dual screening, Cochrane risk-of-bias tools,
descriptive synthesis, intervention components analysis and a restricted realist
synthesis.

**What broke, despite the PASS.**

- Two questions, one slot. The impacts question was encoded; the mechanisms and
  contexts question disappeared.
- `answer_type` was forced to `causal` for an evidence-synthesis question. The
  second question is neither causal nor descriptive: it is mechanistic.
- No completion criterion; **[supplied]**. The PASS is manufactured by that
  supplied sentence.
- The plan's "findings will assess..." is an output, not a finding, and was left
  out of `results`.
- The funder is the Wellcome Trust (221457/Z/20/Z). The enum holds fwo, prin,
  vub, horizon, dfg, snsf, none. `none` would have been false, so `funder` is
  omitted.
- The review works from a premise it does not declare (schools should promote
  mental health). `meta.standpoint: "none"` is our declaration, not the plan's:
  the model has no way to record "not declared".
- The plan says it draws on "two rather different paradigms"; the model has one
  `approach` string, so the tension is flattened into a sentence.

**What held.** Limits, validity conditions, sources, procedure and warrant all
mapped. R7, R4 and R2/R3 did not fire on faithful paraphrases.

## The breakages, ranked

| # | Breakage | Where | Seen in | Change for v0.2 |
|---|---|---|---|---|
| 1 | One question only | S3 | all three | `questions: {primary, secondary[]}`, or a list with `role` |
| 2 | R1 rejects objectives | R1 | i-MaCHeL | `question.form: interrogative \| objective`; R1 checks the declared form |
| 3 | Answer types too narrow | S3 `answer_type` | forest, bibliotherapy | add `synthesis`, `mechanistic`, `feasibility`, `validation`, `other` |
| 4 | Completion criterion has no counterpart | S3, R2 | all three | make it optional, or allow `"none"`, and keep R2 when present |
| 5 | Results conflate findings and outputs | S6, S7, R5 | forest, i-MaCHeL | add `kind: outcome` (with `measure`) and `kind: output`; R5 only for claims |
| 6 | `sources` has one semantics | S5 | i-MaCHeL vs forest | typed sources: `{kind: data \| literature \| participants \| corpus, description}` |
| 7 | Funder list is closed | S2 | bibliotherapy | free string, or `other` plus `scheme` |
| 8 | Standpoint is binary | S2, R8 | all three | `declared \| none \| undeclared` |
| 9 | Fixture machinery sits inside the plan | S2 `meta.expect` | all three | move `expect` to a fixture envelope; plans should not declare how to be judged |
| 10 | Registration, ethics, timeline have no home | S1 `additionalProperties` | all three | declare them out of scope, or allow an `extensions` object |
| 11 | Absent limits look like no limits | S5 | i-MaCHeL | allow `"none"` as an explicit value |

## What held

- `warrant.gap_statement` and dated evidence: the one slot that worked in all
  three without invention.
- `scope`: population, setting and period were always present.
- `method.procedure`: long, but always there, and always in order.
- `validity_conditions` and `limits` where the plan states them: R7 produced no
  false positives.
- R4 (dated evidence) produced no false positives.
- The structural layer accepted all three encodings without a single S finding:
  the shape is robust even where the semantics are not.

## Suggested order of work

1. **Questions plural and form.** Biggest gain: every funder form asks for
   objectives, and most plans have primary and secondary questions. Touches S3,
   R1 and all fixtures.
2. **Completion criterion.** Either optional or explicitly `"none"`. Right now
   the model demands a sentence no plan contains, then silently rewards the
   encoder who writes one.
3. **Result kinds.** `outcome` and `output` alongside `hypothesis`,
   `expected_finding`, `deliverable`; R5 then means "no claim and no outcome",
   not "no hypothesis".
4. **The rest** (typed sources, funder string, `undeclared`, `expect` out of the
   plan) in one pass, since each is small but changes the schema and fixtures.

Doing 1–3 first keeps the migration contained: the 14 fixtures stay valid, the
skill's mappings gain a row, and `BREAKAGES.md` becomes the regression test for
the next round. The roadmap's v0.3 mappings (Horizon, DFG, SNSF) should follow
the schema change, not precede it, or they will encode the old shape three more
times.

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
