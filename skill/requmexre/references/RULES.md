# Rules

Two layers, because two kinds of failure. A document can be well-formed and
still say nothing: a question that is a statement in disguise, a completion
criterion that repeats the question, a falsifier that repeats the claim. The
first kind is structural and lives in `requmexre.schema.json`; the second needs
the words themselves and lives in `validate.py`.

Rule codes are stable: a finding always names one. Rationale, the fixture
envelope, the overlap tests and the steps for adding a rule are in the
repository's `schema/NOTES.md`, outside this bundle.

## Layer 1 — structural, S1–S10

Encoded in `requmexre.schema.json` (JSON Schema draft 2020-12). Every subschema
carries a `$comment` beginning with its rule code; `validate.py` reads those
annotations, so the schema stays the single source of truth for the structural
layer.

| Code | Rule | Where |
|---|---|---|
| S1 | The document is a closed object with `meta`, `questions`, `method` and `warrant` required; `results` is required unless `meta.funder` is `dfg` or `snsf`; `standpoint` optional; no other keys. | root |
| S2 | `meta` is a closed object with `standpoint` required. `standpoint` is `declared`, `none` or `undeclared`; optional `funder` (`fwo`, `prin`, `vub`, `horizon`, `dfg`, `snsf`, `other` or `none`), `scheme` (required when `funder` is `other`, forbidden otherwise), `title`, `version`, `date`, `id`. | `$defs/meta` |
| S3 | `questions` holds one `primary` question and optional `secondary` questions. Every question requires `text` and `form` (interrogative or objective); the primary also requires `answer_type`, `scope` and `completion_criterion`, which is a string or the word `none`. `answer_type` is one of `descriptive`, `exploratory`, `comparative`, `causal`, `evaluative`, `methodological`, `synthesis`, `mechanistic`, `feasibility`, `validation`, `other`. | `$defs/questions`, `$defs/question`, `$defs/primaryQuestion` |
| S4 | A comparative question requires `tertium_comparationis` and carries neither `criteria` nor `operationalisation`. An evaluative question requires `criteria` and `operationalisation` and carries no `tertium_comparationis`. A question of any other type carries none of the three. Applies to every question that declares an answer type. | `$defs/question/allOf` |
| S5 | `method` requires `approach`, a non-empty `sources` list and `procedure`. Each source is an object with `kind` (`data`, `literature`, `participants`, `corpus`) and `description`. `validity_conditions` is an optional list of non-blank strings; `limits` is an optional list of non-blank strings or the word `none`; `risks` is an optional non-empty list of objects with `risk` and `mitigation`, both non-blank strings; absent means not declared. | `$defs/method`, `$defs/source`, `$defs/risks`, `$defs/risk` |
| S6 | `results` is required unless `meta.funder` is exactly `dfg` or `snsf`; the exemption covers only those two forms, not a document with no funder or another funder. When present, `results` is a non-empty list of objects with `claim` and `kind` (hypothesis, expected_finding, outcome, output); no other required keys. | root, `$defs/results`, `$defs/result` |
| S7 | A `hypothesis` or an `expected_finding` requires `falsifier` and `evidence_needed`. An `outcome` requires `measure` and carries no falsifier. An `output` carries neither a measure nor a falsifier: it is produced, not tested. | `$defs/result/allOf` |
| S8 | `warrant` requires `gap_statement` and a non-empty `evidence` list. | `$defs/warrant` |
| S9 | `standpoint`, when present, requires `normative_premises` and `criteria`. Both are lists; whether they may be empty is a matter for R8, not the schema. | `$defs/standpoint` |
| S10 | Every string holds at least one non-blank character. | `$defs/text`, used everywhere |

## Layer 2 — semantic, R1–R8

Implemented in `validate.py` and run only when the structural layer is clean,
since every check below reads fields the schema guarantees.

| Code | Rule | Fires when |
|---|---|---|
| R1 | Each question matches its declared form. | the form is `interrogative` and the text neither ends with `?` nor opens with an interrogative word (what, how, why, whether, which, who, when, where, to/under/in/for what, does, do, did, is, are, was, were, can, could, should, would, will, may, might); or the form is `objective` and the text reads as a question. |
| R2 | Each completion criterion does not restate its own question. | the criterion and its question share 70 per cent or more of the criterion's content words. `none` is skipped. |
| R3 | The gap statement does not restate the primary question. | the gap statement and the primary question share 70 per cent or more of the gap statement's content words. |
| R4 | Warrant evidence is dated or identifiable. | an entry in `warrant.evidence` carries no year (19xx/20xx) and no identifier (DOI, `10.xxxx/`, arXiv, ISBN, PMID, URL). |
| R5 | Results make a claim about the world, or measure something. | `results` is present and every entry has `kind` `output`. Outputs alone answer no question. |
| R6 | A falsifier differs from the claim it tests. | a result's `falsifier` shares 70 per cent or more of its content words with the claim. |
| R7 | Limits are not validity conditions. | a limit shares 70 per cent or more of its content words with a validity condition, or the two lists repeat an entry. `none` is skipped. |
| R8 | The standpoint is declared, explicitly none, or undeclared, and the body agrees. | `meta.standpoint` is `none` or `undeclared` and a `standpoint` object is present; or it is `declared` and the object is missing, or either list is empty. |

## What neither layer checks

- Truth, plausibility or originality of the document.
- Whether a citation exists, or says what the document says it says. The
  separate `verify_citations.py` resolves an identifier and compares title,
  year and author; it cannot read a paywalled full text or decide whether the
  source supports a specific claim.
- Whether the evidence listed under a claim is the evidence that claim needs.
- Fit between a claim and its falsifier beyond lexical difference.
- Funder compliance: section order, page and character limits, eligibility.
- Registration numbers, ethics approvals and calendar time (dates, durations,
  milestones): out of scope, not represented; the model carries the procedure's
  logical order only, and no `extensions` field is provided.
- Language quality beyond the form and overlap tests above.
