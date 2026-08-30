# PRE-REGISTRATION — Energinet Cross-Source Check for Note #003 Residual Gaps
Status: FROZEN / PRE-DATA
Frozen: see git log for this file (freeze point is the commit introducing this document before data acquisition)

## 0. Licence (L0)

Source: Energi Data Service, Energinet
Terms URL: https://www.energidataservice.dk/terms-and-conditions
Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)
Accessed: 2026-08-30
Attribution string to carry: "Source: Energinet (www.energidataservice.dk)"
Compatible with Note #003 public repository: yes

## 1. Source mapping

ENTSO-E TP item #27 (imbalance prices, Art. 17.1.g / 17.2.f)
  → Energi Data Service dataset `ImbalancePrice`
  → field `ImbalancePriceEUR`

Endpoint: https://api.energidataservice.dk/dataset/ImbalancePrice

Record schema, read from records[0].keys() before freezing:

    TimeUTC, TimeDK, PriceArea, SatisfiedDemand, ImbalancePriceEUR,
    ImbalancePriceDKK, SpotPriceEUR, DominatingDirection, aFRRUpMW,
    aFRRVWAUpEUR, aFRRVWAUpDKK, aFRRDownMW, aFRRVWADownEUR, aFRRVWADownDKK,
    mFRRMarginalPriceUpEUR, mFRRMarginalPriceUpDKK,
    mFRRMarginalPriceDownEUR, mFRRMarginalPriceDownDKK

Resolution, measured before freezing: consecutive TimeUTC deltas for a single
PriceArea are 00:15:00. Matches Note #003 MTU resolution.

This mapping is asserted on field naming and resolution only. It is NOT a
claim that the two sources compute the same quantity by the same method.

## 2. Interval identity

Key: (TimeUTC, PriceArea)

- `TimeUTC` is a naive string in the API response and is interpreted as UTC.
- `PriceArea` values "DK1" and "DK2" map to Note #003 zones DK_1 and DK_2.
- Interval convention: interval-beginning, as in Note #003.

## 3. Target set

Defined and committed in `target_set.json` (SHA-256: `df9b1353154164b95501f4b919becbb1f682aa4514181848098437ac4dafe634`).

Total Lookups: **11**
- Derived directly from `imbalance_DK_1.feather` (SHA-256: `fea6acbd0174ace9f6c76db26fa21217204b10ca76a9bf282ceae5d1c4d174e1`) and `imbalance_DK_2.feather` (SHA-256: `8082f184e09624502c83088c78489b5d0947b09e611eda06e65ac712dae762c0`).
- Excludes the 44 synchronous timestamps of 2025-08-10 (audited in `energinet-cross-source-probe`).
- Excludes `2026-05-31T22:00:00` (proven `entsoe-py` `@year_limited` boundary drop at year junction, Entry #003 / PR #539).
- Excludes `2026-06-30T22:00:00` (right edge boundary instant of the 13-month observation window).

The target set consists of:
- `2025-07-07T17:45:00` (DK1, DK2)
- `2025-07-07T19:15:00` (DK1, DK2)
- `2025-07-08T08:45:00` (DK1, DK2)
- `2025-07-11T09:45:00` (DK2 only)
- `2026-04-30T15:15:00` (DK1, DK2)
- `2026-04-30T15:30:00` (DK1, DK2)

## 4. Decision rule — per lookup, before any data is retrieved

| Energinet `ImbalancePrice`                          | Verdict           |
|-----------------------------------------------------|-------------------|
| row present AND `ImbalancePriceEUR` is not null      | CONFIRMED         |
| no row for that (TimeUTC, PriceArea)                 | NOT_CONFIRMED     |
| row present AND `ImbalancePriceEUR` is null          | NULL_VALUED       |
| request failure, schema change, or key inapplicable  | UNRESOLVED        |

Numerical agreement with the ENTSO-E value is NOT part of any verdict.
CONFIRMED asserts only that the interval exists on the national source while
absent from ENTSO-E TP. It does not locate where the loss occurred.

Aggregate reported as counts out of 11, per category. No single verdict is
issued for the set without per-lookup breakdown.

## 5. Frozen non-goals

- Not tested: correctness of either price; reason for any value difference; quality of either source; cause of the outage; economic significance.
- Settlement finality: Preliminary vs. final settlement status in Energinet EDS is NOT tested and does not affect the existence verdict.
- Event aggregation: Consecutive timestamps (`2026-04-30 15:15` and `15:30`) are evaluated as 2 distinct lookups per protocol rules, without collapsing them into a single event.

## 6. Termination

The check ends when all 11 lookups carry a verdict, or when the identity in
§2 is shown to be inapplicable. No criterion is modified after data retrieval.
No additional queries are added because the data is already fetched.
