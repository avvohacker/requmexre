# Version notes

## Post-v1.0 correction — 21 November 2026

S4 already required a comparative question to carry no `criteria` or
`operationalisation` and an evaluative question to carry no
`tertium_comparationis`; the schema did not enforce either prohibition.
Commit `f5034db` adds the two missing `properties: false` constraints. No
field, rule or `$id` changed: a plan that followed `schema/RULES.md` is
unaffected, and a plan that mixed the fields is now rejected as S4 always
said. The two negative fixtures and the question matrix pin the correction.
Checks: 28/28 fixtures, 222 tests.

## v1.0 — 20 November 2026

requmexre v1.0 freezes the v0.5 model: no field, rule, fixture or mapping
changed. The diff of `schema/requmexre.schema.json`, `schema/RULES.md` and
`schema/validate.py` against v0.5 (`e2ef265`) is empty apart from the version
strings.

v1.0 is the tree on `main`: it has no tag and no GitHub release.

### Schema and validator

- The `$id` moves to `https://avvohacker.github.io/requmexre/schema/1.0/requmexre.schema.json`; the Pages build publishes the file at that path.
- S1–S10 and R1–R8 are unchanged; the validator banner reads v1.0.
- Compatibility is unchanged from v0.5: same fields, same rules, same fixtures.

### Citation

- `CITATION.cff` at `version: "1.0.0"`, author `avvohacker`, licence all rights
  reserved, no DOI.

### Checks

- `python3 validate.py`: 24/24 fixtures.
- `python3 validate.py published/*.json`: 3/3 pilot encodings.
- Draft 2020-12 schema check: ok.
- `cffconvert --validate`: ok.
- `site/build.py`: ok.

## v0.5 — 20 November 2026

requmexre v0.5 closes changes 1–11 and ships the Horizon, DFG and SNSF
mappings. The schema and its `$id` move to v0.5.

v0.5 is the tree on `main`: it has no `v0.5` tag and no GitHub release. These
notes record the version, not a published release.

### Schema and validator

- `meta.funder: "other"` requires `meta.scheme`.
- `meta.standpoint` is required and is `declared`, `none` or `undeclared`.
- `method.limits` is a list or the string `"none"`; R7 skips the declaration.
- Registration, ethics and timelines are out of scope; there is no `extensions`
  field.
- Negative fixtures use the `{ "expect": ..., "plan": ... }` envelope. Positive
  plans, the template and the three pilot encodings remain pure plans.
- S1–S10 and R1–R8 keep their numbering; the new S1 negative checks the closed
  root.

### Mappings

- Six funders: FWO, PRIN, VUB, Horizon, DFG and SNSF.
- Section titles and numbering follow the official forms: Horizon V5.1, DFG
  54.012 09/26 and the SNSF requirements for the research plan.
- DFG and SNSF have no results section; the mapping does not invent one.

### Checks

- `python3 validate.py`: 24/24 fixtures.
- `python3 validate.py published/*.json`: 3/3 pilot encodings.
- Draft 2020-12 schema check: ok.
- `site/build.py`: ok.
- CI: validate #23 and pages #17 completed successfully on 178f18d.

### Compatibility

- The schema `$id` moves from `/schema/0.4/` to `/schema/0.5/`.
- A plan with `funder: "other"` must add `scheme`.
- A plan that states no limits should say `limits: "none"`; absence still means
  the field was not addressed.
- `meta.standpoint` remains required; a declared standpoint needs its criteria.

### Not in this release

- Preliminary and own research, Horizon dissemination/exploitation/communication
  and capacity, DFG duration, diversity, data handling, publications and funding,
  SNSF milestones, ethics and budget, and standalone results sections are not
  modelled.
- The validator checks form, not truth or citations.
- The v1.0 stable schema and citation remain on the roadmap.
