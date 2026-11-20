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
| S1 | The document is a closed object with `meta`, `question`, `method` and `warrant` required; `results` and `standpoint` optional; no other keys. | root |
| S2 | `meta` is a closed object with `expect` and `standpoint` required. `standpoint` is `declared` or `none`; `expect` is `valid`, `S1`–`S10` or `R1`–`R8`; optional `funder`, `title`, `version`, `date`, `id`. | `$defs/meta` |
| S3 | `question` requires `text`, `answer_type`, `scope`, `completion_criterion`; `answer_type` is one of descriptive, exploratory, comparative, causal, evaluative, methodological; no other keys beyond the conditional ones. | `$defs/question` |
| S4 | A comparative question requires `tertium_comparationis`. An evaluative question requires `criteria` and `operationalisation`. A question of any other type carries none of the three. | `$defs/question/allOf` |
| S5 | `method` requires `approach`, a non-empty `sources` list and `procedure`; `validity_conditions` and `limits` are optional lists of non-blank strings. | `$defs/method` |
| S6 | `results`, when present, is a non-empty list of objects with `claim` and `kind` (hypothesis, expected_finding, deliverable); no other required keys. | `$defs/results`, `$defs/result` |
| S7 | A `hypothesis` or an `expected_finding` requires `falsifier` and `evidence_needed`. A `deliverable` carries no `falsifier`: it is produced, not falsified. | `$defs/result/allOf` |
| S8 | `warrant` requires `gap_statement` and a non-empty `evidence` list. | `$defs/warrant` |
| S9 | `standpoint`, when present, requires `normative_premises` and `criteria`. Both are lists; whether they may be empty is a matter for R8, not the schema. | `$defs/standpoint` |
| S10 | Every string holds at least one non-blank character. | `$defs/text`, used everywhere |

`results` is optional because two of the six templates in the README have no
results section (DFG, SNSF). `standpoint` is optional because a plan may declare
that it has none; `meta.standpoint` makes that declaration explicit rather than
silent.

## Layer 2 — semantic, R1–R8

Implemented in `schema/validate.py` and run only when the structural layer is
clean, since every check below reads fields the schema guarantees.

| Code | Rule | Fires when |
|---|---|---|
| R1 | The question is interrogative. | `question.text` neither ends with `?` nor opens with an interrogative word (what, how, why, whether, which, who, when, where, to/under/in/for what, does, do, did, is, are, was, were, can, could, should, would, will, may, might). |
| R2 | The completion criterion does not restate the question. | the criterion and the question share 70 per cent or more of the criterion's content words. |
| R3 | The gap statement does not restate the question. | the gap statement and the question share 70 per cent or more of the gap statement's content words. |
| R4 | Warrant evidence is dated or identifiable. | an entry in `warrant.evidence` carries no year (19xx/20xx) and no identifier (DOI, `10.xxxx/`, arXiv, ISBN, PMID, URL). |
| R5 | Results make a claim about the world. | `results` is present and every entry has `kind` `deliverable`. Deliverables alone answer no question. |
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
- Language quality beyond the interrogative and overlap tests above.

## Extending

A structural rule: add the constraint to the schema, put its code in the
subschema's `$comment`, then add a negative fixture with `meta.expect` set to the
new code. `validate.py` refuses any schema keyword it does not implement, so a
new keyword must be added to its evaluator before the schema will run.

A semantic rule: add a function in the semantic layer, register its code in
`SEMANTIC_RULES`, add a negative fixture, and run the validator. Keep R codes for
checks that need the text; anything a JSON Schema can express belongs in S.
