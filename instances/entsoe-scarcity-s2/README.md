# ENTSO-E Scarcity Vintage-Stability Audit

**P10 instance:** `entsoe-scarcity-s2`  
**Repository:** `VolMax-Studio/Open-Market-Notes`  
**Audit class:** Internal self-reproduction / vintage-stability audit  
**Claimant:** VolMax Studio  
**Current scientific verdict:** None  
**Current execution state:** Interpretation invalid in `run-003-confirmatory` (frozen parser specification defect); raw acquisition vintage valid  

---

## Overview

This project tests whether a previously published VolMax July 2026 six-zone European scarcity classification can be reconstructed from a single frozen ENTSO-E Transparency Platform acquisition vintage without silent interval repair.

The audit is intentionally narrower than the original market narrative.

It does not claim independent verification of ENTSO-E, a general European scarcity regime, market causality, BESS economics, or the Great Britain leg of the earlier comparison.

It tests two things:

- **Target S — Structural integrity:** Does the preserved public source yield the exact preregistered 15-minute interval population, with zero unexplained missing, duplicate, or unexpected timestamps?
- **Target R — Reproduction:** If Target S passes, does the frozen vintage reproduce the previously published six-zone scarcity classification under the exact historical estimator?

---

## Why this repository exists

The project was created after an earlier approach (`entsoe-scarcity-s1`) was abandoned because monthly chunking and boundary handling could silently alter the observed population.

`s2` replaces that approach with a stricter architecture:
- preregister before confirmatory execution;
- freeze the request contract and executable harness;
- preserve raw public responses byte-for-byte;
- hash all evidentiary artifacts;
- require exact MTU counts rather than percentage completeness;
- prohibit interpolation, silent deduplication, adaptive chunking, and post-hoc request changes;
- stop on unresolved evidence instead of repairing it during the run.

---

## Audit workflow

```mermaid
flowchart LR
    A["Published VolMax Note #003 result"]
    B["Draft preregistration"]
    C["Claude read-only pre-execution Gate"]
    D["Operator acceptance"]
    E["Frozen PREREG_SHA"]
    F["Ananke official acquisition"]
    G["Raw bytes + SHA-256 evidence"]
    H["Target S: exact MTU structure"]
    I["Target R: classification reproduction"]
    J["Claude post-execution Gate"]
    K["Operator ratification"]
    L["FAILURES.md"]
    M["New prereg version"]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K

    F -. "unexpected source or execution condition" .-> L
    H -. "structural failure" .-> L
    J -. "gate finding" .-> L
    L --> M
    M --> C
```

The failure path is deliberate. A halted run is preserved as evidence and cannot be silently rewritten into a successful run.

---

## Frozen measurement design

### Zones

| Zone | ENTSO-E area identifier |
| :--- | :--- |
| **AT** | `10YAT-APG------L` |
| **BE** | `10YBE----------2` |
| **DK-1** | `10YDK-1--------W` |
| **DK-2** | `10YDK-2--------M` |
| **FR** | `10YFR-RTE------C` |
| **NL** | `10YNL----------L` |

### Source
- ENTSO-E Transparency Platform Web API
- `documentType=A85` — imbalance prices
- `A16` realised-process semantics validated from the returned document
- Price category: `<imbalance_Price.category>A04</imbalance_Price.category>` (Shortage / deficit imbalance price)
- raw public response preserved before interpretation

### Windows

| Window | UTC request period | Expected PT15M intervals / zone |
| :--- | :--- | :--- |
| **Baseline** | `202507312200` $\rightarrow$ `202606302200` | 32,064 |
| **July 2026 target** | `202606302200` $\rightarrow$ `202607312200` | 2,976 |

Exactly 12 requests are preregistered (6 zones $\times$ 2 windows).  
No monthly chunking and no adaptive date-window retry are permitted inside an official run.

---

## Structural gate — Target S

For every zone and window, the expected UTC grid is constructed independently of the source payload.

A structurally admissible population requires:
```text
missing timestamps    = 0
duplicate timestamps  = 0
unexpected timestamps = 0
resolution            = PT15M
document identity     = A85
process semantics     = A16
```

A percentage such as “99.9% complete” is not a substitute for this invariant.  
No interpolation, forward fill, backward fill, silent deduplication, boundary clipping, or synthetic MTU creation is allowed.

---

## Reproduction estimator — Target R

Only structurally admissible zones may enter Target R.

The historical threshold estimator is frozen as:
```python
R_z = float(
    pd.Series(B_z).quantile(
        0.90,
        interpolation="linear"
    )
)
```

July occupancy is then:
$$M_z = \frac{\text{count}(\text{price} \ge R_z)}{2,976}$$

Classification:
$$\text{ELEVATED} \iff M_z \ge 0.15 \quad (15.0\%)$$
$$\text{NOT\_ELEVATED} \iff M_z < 0.15$$

The previously published values are comparison outputs only. They are never used as estimator inputs.

---

## Run history

### `run-001-confirmatory`
- **Disposition:** `Exploratory (Protocol Non-Compliance)`
- The run preserved useful raw observations, but it cannot carry a confirmatory result because the execution harness was authored after the governing preregistration freeze.
- It also exposed a wrong Belgian area identifier (`10YBE----------X`) and an overly broad HALT classifier.
- The run is preserved; it is not repaired retroactively.

### `run-002-confirmatory`
- **Disposition:** `Halted outside taxonomy` (Specification boundary failure)
- **Governing preregistration:** `98929035eb86a6f65a83fc4538a732e98f13912a`
- **Evidence commit:** `1a53d688b1f41bf56ca01062b0c3ffb9cf1ba895`
- Acquisition: 12/12 HTTP 200 OK.
- Interpretation: Halted due to PKZip container format unhandled by frozen v2 parser.

### `run-003-confirmatory`
- **Disposition:** `Acquisition valid — interpretation invalid (frozen parser specification defect)`
- **Governing preregistration:** `d9dfbbada85100243ba0150835d824c1c68629cd`
- **Evidence commit:** `9a68ed467f56cf8f1155986fc0d17676c66cf1d2`
- **Acquisition result:**
  - 12 / 12 requests returned HTTP 200.
  - The complete 12-response acquisition batch exists as a frozen public vintage.
  - Raw payload hashes match the recorded run metadata.
- **Interpretation result:**
  - Multi-Period iteration defect (`ts.find('.//ns:Period')` read only the first `<Period>` per `<TimeSeries>`).
  - Missing category filter: parsed both `A04` (Shortage) and `A05` (Surplus) series without distinguishing `<imbalance_Price.category>`, producing duplicate timestamps.
  - Target S outputs from `run-003` are artifacts of the parser and are **not scientifically interpretable**.

---

## Current boundary: B-21 / B-23 / B-24

The v4 preregistration defines:
- Iteration over all `<Period>` children within each `<TimeSeries>`;
- Extraction of timestamp from each `<Period>`'s own `timeInterval/start`;
- Selection of shortage price series strictly via `<imbalance_Price.category>A04</imbalance_Price.category>`;
- Execution of `run-004-confirmatory` as an offline interpretation run over the preserved `run-003` raw vintage.

---

## Evidence layout

Each official run is expected to preserve:
```text
evidence/runs/<RUN_ID>/
├── command.sh
├── stdout.log
├── stderr.log
├── exit_code.txt
├── env.txt
├── git_commit.txt
├── inputs.sha256
├── outputs.sha256
├── run_metadata.json
└── raw/
```

Derived listings and document inventories are added only after structurally valid parsing.  
Raw artifacts and literal logs outrank narrative summaries.

---

## Governance

| Role | Responsibility |
| :--- | :--- |
| **Ivan** | Human Operator; sole final ratifier |
| **Sol** | Research Lead; claim decomposition, preregistration, methods, interpretation |
| **Claude** | Read-only adversarial Gate |
| **Ananke** | Ops Custodian; Git, hashes, execution, evidence packaging |

A model does not self-ratify.  
Human merge / explicit acceptance is the governance boundary for ratification.

---

## Controlled P10 verdicts

The project uses only the following scientific verdict vocabulary:
- `Verified`
- `Verified with Limitations`
- `Not Verified`
- `Not Demonstrated`
- `Unfalsifiable-as-Stated`
- `Deferred`

Execution states such as `HALT`, `Exploratory (not pre-registered)`, `SPREMNO ZA GEJT`, and `Ratified` are not scientific verdicts.  
At the current stage, this instance has no scientific verdict.

---

## Reproducibility principle

This repository distinguishes:
- source acquisition
- artifact preservation
- structural admissibility
- numerical reproduction
- scientific interpretation
- ratification

A successful network request is not a successful audit.  
A deterministic computation is not scientific truth.  
A failed run is not erased when a later run succeeds.

---

## Status

- **Latest completed run:** `run-004-confirmatory`
- **Acquisition:** `VERIFIED (reused pinned 12/12 HTTP 200 raw vintage from run-003)`
- **Interpretation:** `DETERMINISTIC / VALID (zero duplicates across all 12 series)`
- **Target S:** `S-FAIL across all 6 zones (true source missing MTUs present, 0 duplicates, 0 unexpected)`
- **Target R:** `NOT EVALUATED (blocked by Target S structural gate failure)`
- **Scientific verdict:** `NONE (pending post-execution Gate & Operator ratification)`
- **Next protocol step:** `Post-Execution Gate for run-004-confirmatory`

---

## License / data note

The audit is built around public ENTSO-E Transparency Platform evidence.  
Repository policy is to prefer manifests, hashes, and provenance records over unnecessary redistribution of source data. Legacy raw-data packaging issues are tracked separately in `FAILURES.md` and do not alter the evidentiary status of this instance.

---

## Citation

If this audit is later archived or released with a DOI, the canonical citation and exact release commit should be added here only after the DOI $\rightarrow$ release $\rightarrow$ commit binding is explicitly recorded.
