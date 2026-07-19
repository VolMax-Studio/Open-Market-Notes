# VolMax Open Market Notes
> **Independent measurements of public electricity markets.**

---

## The Philosophy of Open Market Notes

In energy analytics, projections are cheap and easy to bend. Most market outlooks and duration models start with the charts, then define the metrics that fit the desired narrative. 

**VolMax Open Market Notes** reverse this sequence. We pre-register and freeze our parameter definitions in Git *before* running any calculations. By timestamping our methodologies publicly, we guarantee that the resulting baselines are entirely free from post-hoc parameter tuning (p-hacking).

We do not predict the future; we build the empirical, version-controlled foundations that make predictions checkable.

---

## Product Hierarchy

VolMax operates three distinct layers of public infrastructure:

| Layer | Purpose | Key Attributes | Examples |
| :--- | :--- | :--- | :--- |
| **1. Open Market Notes** | Descriptive, reproducible baselines of public markets. | Frozen parameters, primary data, no asset verdicts. | `001-nem-duration-baseline`, `002-ercot-duration-baseline` |
| **2. Verification Audits** | Claim-centric verification under P10 protocol. | Claim statement, Failure Registry, formal verdict. | `Bat Cave`, `Anole`, `Pillswood` |
| **3. Verification Protocols** | Open-source methodology and standard specifications. | Theoretical rules, mathematical bounds, reproducibility docs. | `P10 Protocol`, `SOH-aware Inverter Derating` |

---

## Directory Structure

Each Open Market Note resides in its own directory under `notes/` and adheres to a strict structural schema:

```
notes/[id]-[slug]/
├── PARAMS.md         # Frozen parameters (committed before analysis starts)
├── README.md         # Method, dataset provenance, and execution guide
├── reproduce.py      # Executable script (regenerates results from primary data)
└── results.json      # Output dictionary of verified metrics
```

---

## The Parametric Changelog (Notes Integrity)

Unlike Verification Audits, Open Market Notes do not carry a formal **Failure Registry** because they do not pronounce a PASS/FAIL/DEFERRED verdict on specific assets.

Instead, they maintain a **Parametric Changelog** in this repository. If a frozen parameter proves uninformative or physically inappropriate after analysis (e.g., a scarcity price threshold that captures zero events due to changing grid dynamics):
1. The original result is published under the frozen parameters.
2. The mismatch is documented openly.
3. A new set of parameters is frozen and committed under a new version, preserving the lineage.
4. **No parameters are ever modified or retroactively tuned in silence.**

---

## Active Notes Index

1. **[Note #001: NEM Duration Baseline](./notes/001-nem-duration-baseline)**
   * *Scope:* Mainland Australia NEM (NSW1, QLD1, SA1, VIC1) from 1 Jun 2025 – 30 Jun 2026.
   * *Focus:* Scarcity price duration ($300/MWh threshold) and charging window availability (8h BESS at 0.85 RTE).
   * *Status:* Completed (Timestamp: `2026-07-18T20:52:00+02:00`).
   * *Note:* Contains full empirical statistics, execution script, and visualizations.

2. **[Note #002: ERCOT Duration Baseline](./notes/002-ercot-duration-baseline)**
   * *Scope:* ERCOT Hubs (West, North, South, Houston) from 1 Jun 2025 – 30 Jun 2026.
   * *Focus:* Scarcity pricing duration ($100/MWh & $250/MWh thresholds) and charging window availability (8h BESS at 0.85 RTE).
   * *Status:* Completed (Timestamp: `2026-07-19T13:48:00+02:00`).

3. **Note #003: European Negative Price Baseline**
   * *Scope:* European bidding zones (e.g., DE-LU, FR, ES, IT-North, NL, BE, DK1, DK2) from 1 Jun 2025 – 30 Jun 2026.
   * *Focus:* Cumulative negative price hours, extreme pricing intervals (< -€50/MWh), and charging window suitability.
   * *Status:* Scoping (ENTSO-E API discovery phase).


---
*Developed by VolMax Studio Lab | [volmax-studio.rs](https://www.volmax-studio.rs) | Because trust should be verifiable.*
