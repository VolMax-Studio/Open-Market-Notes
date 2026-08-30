# Instance: Energinet Cross-Source Verification Probe

**Target Subject:** Note #003 (`003-entsoe-imbalance-baseline`) synchronous missing interval event on 2025-08-10.  
**Objective:** Empirically verify whether the 44 missing 15-minute intervals (across price areas DK1 and DK2, total 88 lookups) exist on the Danish national transmission system operator portal (Energi Data Service).

---

## Structure

```
instances/energinet-cross-source-probe/
├── PREREGISTRATION.md              # Frozen pre-registration specification
├── README.md                       # Instance overview and protocol
├── results.json                    # Machine-readable aggregate verdicts
├── src/
│   └── run_audit.py                # Deterministic acquisition & decision runner
└── data/
    └── energinet_lookup_results.csv # Full per-lookup audit table (88 rows)
```

---

## 1. Legal and Attribution (L0)

* **Source:** Energinet Energi Data Service (EDS)
* **Dataset:** `ImbalancePrice` (Dataset ID: 160)
* **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Mandatory Attribution:** *"Source: Energinet (www.energidataservice.dk)"*
* **Endpoint:** `https://api.energidataservice.dk/dataset/ImbalancePrice`

---

## 2. Methodology & Decision Rules

Each of the 44 synchronous missing timestamps on 2025-08-10 is queried across both price areas `(TimeUTC, PriceArea)`:

| Energinet `ImbalancePrice` Condition | Verdict |
| :--- | :--- |
| Row present AND `ImbalancePriceEUR` is not null | **CONFIRMED** |
| No row present for that `(TimeUTC, PriceArea)` | **NOT_CONFIRMED** |
| Row present AND `ImbalancePriceEUR` is null | **NULL_VALUED** |
| Request failure / schema change | **UNRESOLVED** |

---

## 3. Results

Executed on 2026-08-30 against the live Energi Data Service API:

```json
{
  "instance": "energinet-cross-source-probe",
  "target_date": "2025-08-10",
  "total_lookups": 88,
  "counts": {
    "CONFIRMED": 88,
    "NOT_CONFIRMED": 0,
    "NULL_VALUED": 0,
    "UNRESOLVED": 0
  },
  "verdict_ratio": "88/88 CONFIRMED"
}
```

### Key Finding
All 88 lookups returned valid, non-null settlement prices from Energinet (`88 / 88 CONFIRMED`). The data dropout on 2025-08-10 was localized to the ENTSO-E Transparency Platform ingestion/aggregation layer; the Danish national balancing settlement repository remained complete.
