# Instance: <Instance Name>

**Target Subject:** <Note / Claim / Issue Reference>  
**Objective:** <Single-sentence operational question under test>

---

## Structure

```
instances/<instance-name>/
├── PREREGISTRATION.md              # Frozen pre-registration specification
├── README.md                       # Instance overview, protocol, and verdict ledger
├── requirements.txt                # Pinned dependencies for third-party execution
├── results.json                    # Machine-readable aggregate verdicts
├── src/
│   ├── run_audit.py                # In-instance acquisition & evaluation runner
│   └── reproduce.py                # Single entry-point reproduction runner with hash check
├── figures/                        # Generated figures (strictly from audit CSV)
│   └── .gitkeep
└── data/
    └── <lookup_results>.csv        # Full per-lookup audit table
```

---

## 1. Legal and Mandatory Attribution (L0)

* **Source:** <Source Name / Operator>
* **Dataset:** <Dataset Name & ID>
* **License:** <Clean Open License, e.g. CC BY 4.0>
* **Mandatory Attribution:** *"<Verbatim Attribution String>"*
* **Endpoint:** `<URL>`

---

## 2. Methodology & Invariants

* **Target Set Derivation:** <Explicit rule and input provenance for target timestamps/lookups>
* **Decision Rules:** Each lookup is evaluated across the closed partition:

| Condition | Verdict |
| :--- | :--- |
| <Observable Match Condition> | **CONFIRMED** |
| <Observable Mismatch Condition> | **NOT_CONFIRMED** |
| <Data Present but Null / Degenerate> | **NULL_VALUED** |
| <Request Failure / Schema Mismatch> | **UNRESOLVED** |

---

## 3. Results

```json
{
  "instance": "<instance-name>",
  "target_set": {
    "total_lookups": 0,
    "counts": {
      "CONFIRMED": 0,
      "NOT_CONFIRMED": 0,
      "NULL_VALUED": 0,
      "UNRESOLVED": 0
    },
    "verdict_ratio": "0/0 CONFIRMED"
  }
}
```

### Formal Verdict Statement
> *<Single sentence delivering the exact bounded verdict, stating explicitly what was proven and naming what this test does NOT isolate or determine>.*

---

## 4. Deterministic Reproduction & Execution Trace

To independently reproduce all findings and verify byte-identical hash matching:

```bash
pip install -r requirements.txt
export API_TOKEN="<your-token>"
python3 src/reproduce.py
```

### Checksums & Byte-for-Byte Invariants
* `results.json`: `<sha256sum>`
* `data/<lookup_results>.csv`: `<sha256sum>`

---
*VolMax Studio Verification Doctrine — Zero Self-Certification.*
