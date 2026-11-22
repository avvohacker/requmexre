# A minimal FWO render

One document, three sections, to show the shape of the prose the mapping produces.
The document below is invented and short, with the same five fields as
`assets/template.json`; the sections are those of the FWO application form. Section names and numbering are
the funder's. No page or character limit is assumed here: the example is as
short as the argument allows, and a real draft is cut to the call's own limit.

## The document, in brief

- Funder: `fwo` — this is what makes the table below the right one.
- Question: does a four-day week reduce overtime hours in small firms?
- Expected finding: overtime falls after adoption, more where pay is unchanged.
- Output: a cleaned firm-level panel of overtime hours, with its build code.
- Evidence: `Social secretariats, payroll records, 2025`; `Flemish working-time
  survey, 2023`.

The finding's falsifier — "overtime stays within one standard error of its
pre-adoption level" — is not in the render. It stays in `plan.json`, where it
tests the claim; section 3 says which comparison would produce the evidence. The
two evidence strings appear verbatim in the parenthesis of section 1, and no
separate reference list is opened because the FWO form has none.

## 1. Rationale and positioning

Payroll records and surveys of working time are held by different agencies, so
the effect of a four-day week on overtime in small firms has not been estimated
for Belgium (Social secretariats, payroll records, 2025; Flemish working-time
survey, 2023). The document declares no normative standpoint: it estimates an effect
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
