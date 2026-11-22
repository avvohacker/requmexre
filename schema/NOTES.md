# Notes for maintainers

Rationale, test mechanics and extension steps behind `RULES.md`. None of this is
needed to write or validate a plan; it is here so that a rule is changed for a
reason rather than by accident.

## Why results is required and standpoint is optional

`results` is required by default because it is one of the three slots the model
exists to state. The only exemptions are plans whose `meta.funder` is exactly
`dfg` or `snsf`: those two forms have no results section, and requiring a block
there would make a faithful plan invent one. A plan without `meta.funder` is not
exempt; neither is a plan for another funder. `standpoint` remains optional
because a plan may declare that it has none or may not address it;
`meta.standpoint` distinguishes `none` from `undeclared` rather than leaving
both silent.

A result is one of four kinds. A `hypothesis` or an `expected_finding` is a claim
about the world: it carries a `falsifier` and the `evidence_needed`. An `outcome`
is a quantity the study will estimate, and carries its `measure`. An `output` is
a map, dataset, instrument or other artefact that is produced, and carries
neither. R5 requires at least one claim or outcome, so a list of outputs alone
still fails.

## Why a form and why "none"

Published research plans state objectives at least as often as questions. Requiring an
interrogative would fail them for a wording the funder asked for, so every
question declares its `form` and R1 checks the text against that declaration.
Secondary objectives are often short: they need only `text` and `form`, while the
primary question also carries the answer type, the scope and the criterion.

No research plan read for this pilot states what would count as an answer. The
criterion stays required so that the absence is recorded rather than hidden: a
plan writes `"none"`, and R2 skips it. The alternative — leaving the field
optional — makes "no criterion" and "not stated" indistinguishable.

## Why the answer types are a vocabulary, not a gate

The funder documents ask for objectives or questions, not for an answer type:
the VUB research plan lists `Research objectives/questions`; FWO asks for the
scientific objectives and, where applicable, the research hypotheses and
expected outcomes; Horizon asks whether the objectives are measurable and
verifiable; PRIN asks for measurable objectives and any key scientific
hypotheses or research questions; DFG and SNSF name the objectives without
prescribing a classification. The eleven `answer_type` values are therefore the
model's vocabulary, not a funder requirement. Only `comparative` and
`evaluative` impose a structural obligation, and each forbids the other's
fields; the remaining values are labels. The test matrix in
`tests/test_questions.py` pins all eleven, so the vocabulary cannot drift
silently.

## Why risks are not limits

FWO asks for potential scientific risks and contingency plans, Horizon for the
challenges in the method and how they will be overcome, PRIN for risks and
mitigation, and SNSF for risks and alternatives. `limits` answers a different
question: what the design does not cover. A risk is something that could go
wrong; its mitigation is the response. v1.1 adds an optional `method.risks`
list of `{risk, mitigation}` so that the two are not conflated. The field is
optional: a plan that states no risks is valid, and no risk is invented. The
1.0 schema remains published from `schema/archive/1.0/` at its original `$id`.

## How the overlap tests work

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

A pure plan is expected to be valid: it must produce no finding. A negative
fixture wraps the plan in an envelope that says which rule it is meant to break,
so that fixtures are self-describing and `python3 validate.py` can return a
meaningful exit code:

- `"valid"` — the plan must produce no finding.
- `"S3"`, `"R7"` — the named rule must fire. Other findings are reported but do
  not change the verdict; a negative fixture should still be written to break one
  rule cleanly.

The envelope is `{ "expect": "R7", "plan": { ... } }`. Positive fixtures, the
template and the pilot encodings are pure plans, with no `expect`.

The validator exits 0 when every plan is valid and every negative envelope
reports its expected rule, 1 when one does not, 2 when there is nothing to
check.

## Extending

A structural rule: add the constraint to the schema, put its code in the
subschema's `$comment`, then add a negative fixture whose envelope `expect` is
the new code. `validate.py` refuses any schema keyword it does not implement, so
a new keyword must be added to its evaluator before the schema will run.

A semantic rule: add the check to `check_semantics`, add its code to `RULE_IDS`
and to the `_rule_of` pattern when it is a new code, add a negative fixture, and
run the validator. Keep R codes for checks that need the text; anything a JSON
Schema can express belongs in S.
