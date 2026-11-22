# Version notes

## v1.2 — 22 November 2026

requmexre v1.2 makes `results` required by default. The only exemptions are
plans whose `meta.funder` is exactly `dfg` or `snsf`, the two forms with no
results section. A plan without `meta.funder` is not exempt.

### Schema and validator

- The `$id` moves to `https://avvohacker.github.io/requmexre/schema/1.2/requmexre.schema.json`; the Pages build publishes the file at that path.
- S1 and S6 make `results` required unless `meta.funder` is `dfg` or `snsf`. A missing `results` is an S6 finding; an empty list is still a non-empty-list failure.
- S2–S5, S7–S10 and R1–R8 are unchanged. R5 still runs whenever results are present.
- The 1.1 schema remains published at its original `$id`, from `schema/archive/1.1/`; the 1.0 schema remains published from `schema/archive/1.0/`.

### Migration

- Add a `results` list to every plan whose `meta.funder` is not `dfg` or `snsf`; a plan without a funder needs one too.
- A DFG or SNSF plan may omit `results`; if it carries one, the non-empty and R5 rules still apply. Do not add an empty list or invent a results section.
- The exemption is based on the funder value alone, not on a section table or a missing `meta.funder`.

### Fixtures and checks

- New positive fixtures `dfg-no-results.json` and `snsf-no-results.json` pin the exemption; `negative/s6-missing-results.json` pins the default requirement.
- The renderer still reports results carried by DFG or SNSF as a coverage gap, because those forms have no section for them.
- Checks: 32/32 fixtures, 249 tests, and a Pages build that writes `/schema/1.0/`, `/schema/1.1/` and `/schema/1.2/`.

### Citation

- `CITATION.cff` at `version: "1.2.0"`, author `avvohacker`, licence all rights
  reserved, no DOI. v1.2 is not tagged and has no GitHub release.

Earlier versions are in git history; the 1.0 and 1.1 schemas remain in
`schema/archive/`.
