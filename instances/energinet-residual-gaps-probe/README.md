# Instance: Energinet Residual Gaps Probe

**Target Subject:** Note #003 (`003-entsoe-imbalance-baseline`) residual missing intervals outside the 2025-08-10 event.  
**Objective:** Empirically verify whether the 11 residual missing 15-minute intervals across DK1 and DK2 (July 2025 and April 2026) exist on the Danish national transmission system operator portal (Energi Data Service).

---

## Structure

```
instances/energinet-residual-gaps-probe/
├── PREREGISTRATION.md              # Frozen pre-registration specification
├── target_set.json                 # Machine-readable target set specification
├── README.md                       # Instance overview and protocol
├── results.json                    # Machine-readable aggregate verdicts
├── data_manifest.json              # Raw EDS response hashes and attribution
├── src/
│   └── run_audit.py                # Deterministic acquisition & decision runner
└── data/
    └── energinet_lookup_results.csv # Complete per-lookup audit table (11 rows)
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

* **Target Set Derivation:** Defined and locked in `target_set.json` (SHA-256: `df9b1353154164b95501f4b919becbb1f682aa4514181848098437ac4dafe634`).
  * Derived from `imbalance_DK_1.feather` and `imbalance_DK_2.feather`.
  * Excludes the 44 synchronous timestamps of 2025-08-10 (audited in `energinet-cross-source-probe`).
  * Excludes `2026-05-31T22:00:00` (proven `entsoe-py` `@year_limited` boundary drop at year junction, Entry #003 / PR #539).
  * Excludes `2026-06-30T22:00:00` (right edge boundary instant of the 13-month observation window).
* **Decision Rules:** Evaluated per lookup against the frozen 4-state table:

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
  "instance": "energinet-residual-gaps-probe",
  "target_set_sha256": "df9b1353154164b95501f4b919becbb1f682aa4514181848098437ac4dafe634",
  "total_lookups": 11,
  "counts": {
    "CONFIRMED": 11,
    "NOT_CONFIRMED": 0,
    "NULL_VALUED": 0,
    "UNRESOLVED": 0
  },
  "verdict_ratio": "11/11 CONFIRMED"
}
```

### Complete Verdict Table
| TimeUTC | PriceArea | Zone | ImbalancePriceEUR | Verdict |
| :--- | :--- | :--- | :---: | :--- |
| 2025-07-07T17:45:00 | DK1 | DK_1 | 30.82 | **CONFIRMED** |
| 2025-07-07T17:45:00 | DK2 | DK_2 | 27.79 | **CONFIRMED** |
| 2025-07-07T19:15:00 | DK1 | DK_1 | 17.77 | **CONFIRMED** |
| 2025-07-07T19:15:00 | DK2 | DK_2 | 17.77 | **CONFIRMED** |
| 2025-07-08T08:45:00 | DK1 | DK_1 | -7.32 | **CONFIRMED** |
| 2025-07-08T08:45:00 | DK2 | DK_2 | 81.76 | **CONFIRMED** |
| 2025-07-11T09:45:00 | DK2 | DK_2 | -6.60 | **CONFIRMED** |
| 2026-04-30T15:15:00 | DK1 | DK_1 | 61.42 | **CONFIRMED** |
| 2026-04-30T15:15:00 | DK2 | DK_2 | 46.80 | **CONFIRMED** |
| 2026-04-30T15:30:00 | DK1 | DK_1 | 136.00 | **CONFIRMED** |
| 2026-04-30T15:30:00 | DK2 | DK_2 | 7.83 | **CONFIRMED** |

### Formal Verdict Statement
> *Svih 11 preostalih intervala odsutnih na ENTSO-E TP-u izvan događaja 10.08.2025 prisutni su u Energinet `ImbalancePrice` sa nenultim vrednostima. 11/11 CONFIRMED. Gde je gubitak nastao ovim testom nije utvrđeno.*

---

## 4. Deterministic Reproduction & Execution Trace

### Literal Execution Output (`python3 src/run_audit.py`)
```text
=== 1. LOADING FROZEN TARGET SET ===
Total lookups to evaluate: 11

=== 2. FETCHING ENERGINET EDS ImbalancePrice FOR TARGET WINDOWS ===
Window 2025-07-07T00:00 -> 2025-07-12T00:00: returned 960 records
Window 2026-04-30T00:00 -> 2026-05-01T00:00: returned 192 records
Data manifest written to: .../instances/energinet-residual-gaps-probe/data_manifest.json

=== 3. EVALUATING 11 LOOKUPS AGAINST FROZEN DECISION RULE ===
Lookup results table saved to: .../instances/energinet-residual-gaps-probe/data/energinet_lookup_results.csv

=== AGGREGATE SUMMARY ===
CONFIRMED      : 11 / 11
NOT_CONFIRMED  :  0 / 11
NULL_VALUED    :  0 / 11
UNRESOLVED     :  0 / 11
```

### Checksums & Invariants
* `target_set.json`: `df9b1353154164b95501f4b919becbb1f682aa4514181848098437ac4dafe634`
* `results.json`: `6038318b763ecad9fe5d0a6c6ec2ee46c646ef6766487e411b7dfb899bf99201`
* `data/energinet_lookup_results.csv`: `12fc0cb5d0bf93cba41e2feee17e1ec93e7f4c54e0c4516ff8363ae168a2ee31`
