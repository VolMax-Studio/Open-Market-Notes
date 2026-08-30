# PRE-REGISTRATION — <Title of Study / Probe>
Status: FROZEN / PRE-DATA
Frozen: see git log for this file (freeze point is the commit introducing this document before data acquisition)

## 0. Licence (L0)

Source: <Data Source Name>
Terms URL: <URL>
Licence: <e.g. CC BY 4.0 / Open Data>
Accessed: <YYYY-MM-DD>
Attribution string to carry: "<Exact attribution string required by terms>"
Compatible with Note public repository: <yes/no>

## 1. Source mapping

Target Item / Concept: <e.g. Imbalance Prices / Flow Data>
  → Source Dataset: `<dataset_name>`
  → Target Field(s): `<field_name>`

Endpoint: <URL>

Record schema (read from live sample before freezing):
    <list of fields>

Resolution (measured before freezing):
    <e.g. PT15M / PT60M>

## 2. Interval identity

Key: (<field1>, <field2>)
- Timezone convention: <e.g. strict UTC>
- Boundary convention: <e.g. interval-beginning>

## 3. Target set

<Exact finite list or bounded count of intervals/lookups under test>
Out-of-scope items: <explicit list of exclusions>

## 4. Decision rule — per lookup, before any data is retrieved

| Condition | Verdict |
| :--- | :--- |
| <Condition 1> | **CONFIRMED** |
| <Condition 2> | **NOT_CONFIRMED** |
| <Condition 3> | **NULL_VALUED** |
| <Condition 4> | **UNRESOLVED** |

Aggregate reported as counts out of N. No single verdict is issued for the set without per-lookup breakdown.

## 5. Frozen non-goals

<Explicit list of what is NOT tested: causality, economics, price validity, etc.>

## 6. Termination

The check ends when all N lookups carry a verdict, or when the identity in §2 is shown to be inapplicable.
No criterion is modified after data retrieval.
