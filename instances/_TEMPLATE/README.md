# Instance: <Instance Name>

> [!IMPORTANT]
> **5-Point Verification Standard Compliance (P10 Protocol)**

---

## 1. Central Claim
*<State the singular, falsifiable assertion. What does this artifact prove or measure?>*

## 2. What Would Falsify It
*<Define the exact quantitative or physical threshold that invalidates this claim.>*

## 3. Limitations & Boundaries
*<Document all structural, numerical, hardware, and physical assumptions (e.g., resolution floors, unobserved intervals, market rule boundaries)>.*

## 4. Operational Status
*Specify exact status: `CLOSED`, `COMPLETE & VERIFIED (PENDING RATIFICATION)`, or `PRE-REGISTERED`.*

## 5. Provenance & Anchor
* **Public Source / API / DOI:** <Link or DOI citation>
* **Verification Method:** Verified live in browser / HTTP response check (not agent-only self-certification).
* **Verification Timestamp:** YYYY-MM-DD
* **Data License:** Clean open license (e.g., CC BY 4.0, OGL v3.0, MIT).

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
│   └── reproduce.py                # Single entry-point reproduction runner with hash assertions
├── figures/                        # Generated figures (strictly from audit CSV)
│   └── .gitkeep
└── data/
    └── <lookup_results>.csv        # Full per-lookup audit table
```

---

## 6. Methodology & Invariants

* **Target Set Derivation:** <Explicit rule and input provenance for target timestamps/lookups>
* **Decision Rules:** Each lookup is evaluated across the closed partition:

| Condition | Verdict |
| :--- | :--- |
| <Observable Match Condition> | **CONFIRMED** |
| <Observable Mismatch Condition> | **NOT_CONFIRMED** |
| <Data Present but Null / Degenerate> | **NULL_VALUED** |
| <Request Failure / Schema Mismatch> | **UNRESOLVED** |

---

## 7. Results

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

## 8. Deterministic Reproduction & Execution Trace

To independently reproduce all findings and verify byte-identical hash matching:

```bash
pip install -r requirements.txt
export API_TOKEN="your-api-token-here"
python3 src/reproduce.py
```

### Checksums & Byte-for-Byte Invariants
* `results.json`: `<sha256sum>`
* `data/<lookup_results>.csv`: `<sha256sum>`

---
*VolMax Studio Verification Doctrine — Zero Self-Certification.*
