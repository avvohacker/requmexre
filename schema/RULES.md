# Rules

Two layers, because two kinds of failure. A plan can be well-formed and still say
nothing: a question that is a statement in disguise, a completion criterion that
repeats the question, a falsifier that repeats the claim. The first kind is
structural and lives in `requmexre.schema.json`; the second needs the words
themselves and lives in `validate.py`.

Rule codes are stable. A finding always names one, so a fixture can declare which
rule it is meant to break.

## Layer 1 — structural, S1–S10

Encoded in `schema/requmexre.schema.json` (JSON Schema draft 2020-12). Every
subschema carries a `$comment` beginning with its rule code; `validate.py` reads
those annotations, so the schema stays the single source of truth for the
structural layer.

| Code | Rule | Where |
|---|---|---|
| S1 | The document is a closed object with `meta`, `questions`, `method` and `warrant` required; `results` and `standpoint` optional; no other keys. | root |
| S2 | `meta` is a closed object with `expect` and `standpoint` required. `standpoint` is `declared` or `none`; `expect` is `valid`, `S1`–`S10` or `R1`–`R8`; optional `funder` (`fwo`, `prin`, `vub`, `horizon`, `dfg`, `snsf`, `other` or `none`), `scheme` (required when `funder` is `other`, forbidden otherwise), `title`, `version`, `date`, `id`. | `$defs/meta` |
| S3 | `questions` holds one `primary` question and optional `secondary` questions. Every question requires `text` and `form` (interrogative or objective); the primary also requires `answer_type`, `scope` and `completion_criterion`, which is a string or the word `none`. `answer_type` is one of `descriptive`, `exploratory`, `comparative`, `causal`, `evaluative`, `methodological`, `synthesis`, `mechanistic`, `feasibility`, `validation`, `other`. | `$defs/questions`, `$defs/question`, `$defs/primaryQuestion` |
| S4 | A comparative question requires `tertium_comparationis`. An evaluative question requires `criteria` and `operationalisation`. A question of any other type carries none of the three. Applies to every question that declares an answer type. | `$defs/question/allOf` |
| S5 | `method` requires `approach`, a non-empty `sources` list and `procedure`. Each source is an object with `kind` (`data`, `literature`, `participants`, `corpus`) and `description`. `validity_conditions` and `limits` are optional lists of non-blank strings. | `$defs/method`, `$defs/source` |
| S6 | `results`, when present, is a non-empty list of objects with `claim` and `kind` (hypothesis, expected_finding, outcome, output); no other required keys. | `$defs/results`, `$defs/result` |
| S7 | A `hypothesis` or an `expected_finding` requires `falsifier` and `evidence_needed`. An `outcome` requires `measure` and carries no falsifier. An `output` carries neither a measure nor a falsifier: it is produced, not tested. | `$defs/result/allOf` |
| S8 | `warrant` requires `gap_statement` and a non-empty `evidence` list. | `$defs/warrant` |
| S9 | `standpoint`, when present, requires `normative_premises` and `criteria`. Both are lists; whether they may be empty is a matter for R8, not the schema. | `$defs/standpoint` |
| S10 | Every string holds at least one non-blank character. | `$defs/text`, used everywhere |

`results` is optional because two of the six templates in the README have no
results section (DFG, SNSF). `standpoint` is optional because a plan may declare
that it has none; `meta.standpoint` makes that declaration explicit rather than
silent.

A result is one of four kinds. A `hypothesis` or an `expected_finding` is a claim
about the world: it carries a `falsifier` and the `evidence_needed`. An `outcome`
is a quantity the study will estimate, and carries its `measure`. An `output` is
a map, dataset, instrument or other artefact that is produced, and carries
neither. R5 requires at least one claim or outcome, so a list of outputs alone
still fails.

### Why a form and why "none"

Published plans state objectives at least as often as questions. Requiring an
interrogative would fail them for a wording the funder asked for, so every
question declares its `form` and R1 checks the text against that declaration.
Secondary objectives are often short: they need only `text` and `form`, while the
primary question also carries the answer type, the scope and the criterion.

No published plan read for this pilot states what would count as an answer. The
criterion stays required so that the absence is recorded rather than hidden: a
plan writes `"none"`, and R2 skips it. The alternative — leaving the field
optional — makes "no criterion" and "not stated" indistinguishable.

## Layer 2 — semantic, R1–R8

Implemented in `schema/validate.py` and run only when the structural layer is
clean, since every check below reads fields the schema guarantees.

| Code | Rule | Fires when |
|---|---|---|
| R1 | Each question matches its declared form. | the form is `interrogative` and the text neither ends with `?` nor opens with an interrogative word (what, how, why, whether, which, who, when, where, to/under/in/for what, does, do, did, is, are, was, were, can, could, should, would, will, may, might); or the form is `objective` and the text reads as a question. |
| R2 | Each completion criterion does not restate its own question. | the criterion and its question share 70 per cent or more of the criterion's content words. `none` is skipped. |
| R3 | The gap statement does not restate the primary question. | the gap statement and the primary question share 70 per cent or more of the gap statement's content words. |
| R4 | Warrant evidence is dated or identifiable. | an entry in `warrant.evidence` carries no year (19xx/20xx) and no identifier (DOI, `10.xxxx/`, arXiv, ISBN, PMID, URL). |
| R5 | Results make a claim about the world, or measure something. | `results` is present and every entry has `kind` `output`. Outputs alone answer no question. |
| R6 | A falsifier differs from the claim it tests. | a result's `falsifier` shares 70 per cent or more of its content words with the claim. |
| R7 | Limits are not validity conditions. | a limit shares 70 per cent or more of its content words with a validity condition, or the two lists repeat an entry. |
| R8 | The standpoint is declared or explicitly none, and the body agrees. | `meta.standpoint` is `none` and a `standpoint` object is present; or it is `declared` and the object is missing, or either list is empty. |

### How the overlap tests work

R2, R3, R6 and R7 compare word sets, not meanings. `content_words` lowercases,
splits on non-alphanumerics, drops tokens of two characters or fewer and drops a
fixed English stopword list. Overlap is

```
|A ∩ B| / min(|A|, |B|)
```

not Jaccard: the failure being caught is one text swallowing the other, which a
union-based measure understates. At 0.70 a criterion such as "the question is
answered once it is clear how a four-day week affects overtime in small firms"
against the question "How does a four-day week affect overtime in small firms?"
scores 0.86 and fires; a criterion that introduces its own observable — an
estimate, a measure, a comparison — stays well below.

The tests are lexical. A paraphrase that shares no vocabulary passes R2, R3 and
R6. That is a known limit, and the reason these are called form checks.

## Declaring the expectation

`meta.expect` says how the file is meant to behave, so that fixtures are
self-describing and `python3 validate.py` can return a meaningful exit code:

- `"valid"` — the file must produce no finding.
- `"S3"`, `"R7"` — the named rule must fire. Other findings are reported but do
  not change the verdict; a negative fixture should still be written to break one
  rule cleanly.

The validator exits 0 when every file behaves as declared, 1 when one does not,
2 when there is nothing to check.

## What neither layer checks

- Truth, plausibility or originality of the plan.
- Whether a citation exists, or says what the plan says it says.
- Whether the evidence listed under a claim is the evidence that claim needs.
- Fit between a claim and its falsifier beyond lexical difference.
- Funder compliance: section order, page and character limits, eligibility.
- Language quality beyond the form and overlap tests above.

## Extending

A structural rule: add the constraint to the schema, put its code in the
subschema's `$comment`, then add a negative fixture with `meta.expect` set to the
new code. `validate.py` refuses any schema keyword it does not implement, so a
new keyword must be added to its evaluator before the schema will run.

A semantic rule: add a function in the semantic layer, register its code in
`SEMANTIC_RULES`, add a negative fixture, and run the validator. Keep R codes for
checks that need the text; anything a JSON Schema can express belongs in S.
