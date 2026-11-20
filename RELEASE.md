# Release notes

## v0.5 — 20 November 2026

requmexre v0.5 closes changes 1–11 and ships the Horizon, DFG and SNSF
mappings. The schema and its `$id` move to v0.5.

### Schema and validator

- `meta.funder: "other"` requires `meta.scheme`.
- `meta.standpoint` is required and is `declared`, `none` or `undeclared`.
- `method.limits` is a list or the string `"none"`; R7 skips the declaration.
- Registration, ethics and timelines are out of scope; there is no `extensions`
  field.
- Negative fixtures use the `{ "expect": ..., "plan": ... }` envelope. Positive
  plans, the template and the three published plans remain pure plans.
- S1–S10 and R1–R8 keep their numbering; the new S1 negative checks the closed
  root.

### Mappings

- Six funders: FWO, PRIN, VUB, Horizon, DFG and SNSF.
- Section titles and numbering follow the official forms: Horizon V5.1, DFG
  54.012 09/26 and the SNSF requirements for the research plan.
- DFG and SNSF have no results section; the mapping does not invent one.

### Checks

- `python3 validate.py`: 24/24 fixtures.
- `python3 validate.py published/*.json`: 3/3 published plans.
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
