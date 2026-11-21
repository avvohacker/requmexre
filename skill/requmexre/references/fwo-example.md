# A minimal FWO render

One plan, three sections, to show the shape of the prose the mapping produces.
The plan below is invented and short, with the same five fields as
`assets/template.json`; the sections are those of the FWO project outline. Section names and numbering are
the funder's; word and page limits belong to the call, so read the form before
cutting.

## The plan, in brief

- Question: does a four-day week reduce overtime hours in small firms?
- Method: difference-in-differences on payroll records, 2025–2029.
- Expected finding: overtime falls after adoption, more where pay is unchanged.
- Output: a cleaned firm-level panel of overtime hours, with its build code.
- Gap: payroll records and working-time surveys are held by different agencies.
- Standpoint: none.

The finding's falsifier — "overtime stays within one standard error of its
pre-adoption level" — is not in the render. It stays in `plan.json`, where it
tests the claim; section 3 says which comparison would produce the evidence.

## 1. Rationale and positioning

Payroll records and surveys of working time are held by different agencies, so
the effect of a four-day week on overtime in small firms has not been estimated
for Belgium (Social secretariats, payroll records, 2025; Flemish working-time
survey, 2023). The plan declares no normative standpoint: it estimates an effect
and does not argue from premises about how work ought to be organised.

## 2. Scientific research objectives

The study asks whether a four-day week reduces overtime hours in small firms.
Its scope is firms with 10 to 49 employees in Belgium, 2026 to 2029. The
question is answered when overtime hours per employee are estimated before and
after adoption, compared with non-adopting firms, and the uncertainty of the
estimate is reported.

Expected result: overtime hours per employee fall after adoption, and fall
further in firms that shorten the week without cutting pay.

## 3. Research methodology and work plan

The design is a difference-in-differences comparison of adopting and
non-adopting firms, matched on sector and size, using payroll records from the
social secretariats (2025–2029). The work runs in four steps: match firms;
estimate overtime hours per employee before and after adoption; test for
pre-trends; compare the estimate with the matched firms. The finding holds if
firms are observed for two years on either side of adoption. The design does
not cover firms with fewer than 10 employees, and payroll records measure paid
overtime, not hours worked informally.

At the end of the work plan the procedure delivers a cleaned firm-level panel of
overtime hours and the code that builds it.
