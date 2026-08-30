# Instance: <Instance Name>

**Target Subject:** <Note / Issue Reference>  
**Objective:** <Single-sentence operational question under test>

---

## Structure

```
instances/<instance-name>/
├── PREREGISTRATION.md              # Frozen pre-registration specification
├── README.md                       # Instance overview and protocol
├── results.json                    # Machine-readable aggregate verdicts
├── src/
│   └── run_audit.py                # Deterministic acquisition & decision runner
└── data/
    └── <lookup_results>.csv        # Full per-lookup audit table
```

---

## 1. Legal and Mandatory Attribution (L0)

* **Source:** <Source Name>
* **License:** <License Type>
* **Mandatory Attribution:** *"<Attribution>"*
* **Endpoint:** `<URL>`

---

## 2. Methodology & Invariants

* **Target Set:** <Count / description of target lookups>
* **Decision Rules:** <Summary table of frozen decision rules>

---

## 3. Results

```json
{
  "instance": "<instance-name>",
  "target_date": "<date>",
  "total_lookups": 0,
  "counts": {
    "CONFIRMED": 0,
    "NOT_CONFIRMED": 0,
    "NULL_VALUED": 0,
    "UNRESOLVED": 0
  },
  "verdict_ratio": "0/0"
}
```

### Formal Verdict Statement
> *<Exact bounded verdict statement adhering to frozen decision rules and non-goals>*
