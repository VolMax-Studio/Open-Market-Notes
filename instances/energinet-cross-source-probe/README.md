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

## 1. Legal and Mandatory Attribution (L0)

* **Source:** Energinet Energi Data Service (EDS)
* **Dataset:** `ImbalancePrice` (Dataset ID: 160)
* **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Mandatory Attribution:** *"Source: Energinet (www.energidataservice.dk)"*
* **Endpoint:** `https://api.energidataservice.dk/dataset/ImbalancePrice`

---

## 2. Methodology & Invariants

* **Target Set Derivation:** The set of 44 missing timestamps was identified from `imbalance_DK_1.feather` across the nominal grid `2025-08-10 00:00:00` to `2025-08-10 23:45:00` UTC; applicability to DK_2 is inherited from the 100% synchronous dropout proof established in Entry #004 (`set(missing_DK1) == set(missing_DK2)`).
* **API Formatting Note:** Initial trial query using seconds notation (`yyyy-MM-ddTHH:mm:ss`) returned HTTP 400 as EDS strictly expects `yyyy-MM-ddTHH:mm`; production execution called `start=2025-08-10T00:00&end=2025-08-11T00:00`.
* **Decision Rules:** Each of the 44 synchronous missing timestamps is evaluated across both price areas `(TimeUTC, PriceArea)`:

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

### Formal Verdict Statement
> *Svih 44 intervala odsutnih na ENTSO-E TP-u 10.08.2025 prisutni su u Energinet `ImbalancePrice` sa nenultim vrednostima, u obe cenovne zone. 88/88 CONFIRMED. Gde je gubitak nastao ovim testom nije utvrđeno.*
