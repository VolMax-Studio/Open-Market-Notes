# VolMax Open Market Notes
> **Independent measurements of public electricity markets.**

---

## The Philosophy of Open Market Notes

In energy analytics, projections are cheap and easy to bend. Most market outlooks and duration models start with the charts, then define the metrics that fit the desired narrative. 

**VolMax Open Market Notes** reverse this sequence. We pre-register and freeze our parameter definitions in Git *before* running any calculations. By timestamping our methodologies publicly, we guarantee that the resulting baselines are entirely free from post-hoc parameter tuning (p-hacking).

We do not predict the future; we build the empirical, version-controlled foundations that make predictions checkable.

---

## 🏛️ VolMax Observatory Registry

| Note ID | Note Title | Market Scope | Results Hash (`results_sha256`) | Immutable Zenodo DOI |
| :--- | :--- | :--- | :--- | :---: |
| `OMN-001` | [Open Market Note #001 — NEM Duration Baseline](https://github.com/VolMax-Studio/Open-Market-Notes/tree/main/notes/001-nem-duration-baseline) | Mainland Australia NEM (NSW1, QLD1, SA1, VIC1) | `c192e7ee97ac...` | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21693239.svg)](https://doi.org/10.5281/zenodo.21693239) |
| `OMN-002` | [Open Market Note #002 — ERCOT Duration Baseline](https://github.com/VolMax-Studio/Open-Market-Notes/tree/main/notes/002-ercot-duration-baseline) | ERCOT (West, North, South, Houston) | `90e3543b5550...` | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21693245.svg)](https://doi.org/10.5281/zenodo.21693245) |
| `OMN-003` | [Open Market Note #003 — ENTSO-E Imbalance Price Duration Baseline](https://github.com/VolMax-Studio/Open-Market-Notes/tree/main/notes/003-entsoe-imbalance-baseline) | ENTSO-E Imbalance (NL, BE, FR, DK1, DK2, AT) | `b1c713379887...` | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21693254.svg)](https://doi.org/10.5281/zenodo.21693254) |
| `OMN-004` | [Open Market Note #004 — GB BESS Duration Baseline (Elexon BMRS)](https://github.com/VolMax-Studio/Open-Market-Notes/tree/main/notes/004-gb-duration-baseline) | Great Britain (Elexon BMRS NGET Area) | `385ddfd9ed88...` | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21693262.svg)](https://doi.org/10.5281/zenodo.21693262) |
| `OMN-005` | [Open Market Note #005 — ENTSO-E Cross-Border Physical Flow Dynamics Baseline](https://github.com/VolMax-Studio/Open-Market-Notes/tree/main/notes/005-entsoe-crossborder-flows) | ENTSO-E CWE Interconnections (AT-DE, BE-NL, FR-BE, NL-DE) | `60314bd2764e...` | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21693276.svg)](https://doi.org/10.5281/zenodo.21693276) |

---

## Product Hierarchy

VolMax operates three distinct layers of public infrastructure:

| Layer | Purpose | Key Attributes | Examples |
| :--- | :--- | :--- | :--- |
| **1. Open Market Notes** | Descriptive, reproducible baselines of public markets. | Frozen parameters, primary data, no asset verdicts. | `001-nem-duration-baseline`, `005-entsoe-crossborder-flows` |
| **2. Verification Audits** | Claim-centric verification under P10 protocol. | Claim statement, Failure Registry, formal verdict. | `Bat Cave`, `Anole`, `Pillswood` |
| **3. Verification Protocols** | Open-source methodology and standard specifications. | Theoretical rules, mathematical bounds, reproducibility docs. | `P10 Protocol`, `SOH-aware Inverter Derating` |

---

## Directory Structure

Each Open Market Note resides in its own directory under `notes/` and adheres to a strict structural schema:

```
notes/[id]-[slug]/
├── PARAMS.md         # Frozen parameters (committed before analysis starts)
├── DECISIONS.md      # Append-only pre-registration decision ledger
├── README.md         # Method, dataset provenance, and execution guide
├── run_pipeline.py   # Executable script (regenerates results from primary data)
└── summary.json      # Output dictionary of verified metrics
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
   * *Status:* Complete & Verified (Timestamp: `2026-07-18T20:52:00+02:00`).

2. **[Note #002: ERCOT Duration Baseline](./notes/002-ercot-duration-baseline)**
   * *Scope:* ERCOT Hubs (West, North, South, Houston) from 1 Jun 2025 – 30 Jun 2026.
   * *Focus:* Scarcity pricing duration ($100/MWh & $250/MWh thresholds) and charging window availability (8h BESS at 0.85 RTE).
   * *Status:* Complete & Verified (Timestamp: `2026-07-19T13:48:00+02:00`).

3. **[Note #003: ENTSO-E Imbalance Price Duration Baseline](./notes/003-entsoe-imbalance-baseline)**
   * *Scope:* European 15-minute imbalance telemetry across 6 bidding zones (`NL`, `BE`, `FR`, `DK1`, `DK2`, `AT`) from 1 Jun 2025 – 30 Jun 2026.
   * *Focus:* System shortage scarcity ($\ge €100/€250$) vs renewable surplus absorption ($\le €0/€25$), TSO settlement incentive windows.
   * *Status:* Complete & Verified (Timestamp: `2026-07-25T14:15:00+02:00`).

4. **[Note #004: GB BESS Duration Baseline (Elexon BMRS)](./notes/004-gb-duration-baseline)**
   * *Scope:* Great Britain (NGET Grid Area) 30-minute settlement periods from 1 Jun 2025 – 30 Jun 2026 (18,960 settlement periods).
   * *Focus:* Elexon System Prices, pure active scarcity runs vs macro event window spans (£100/£200/£300/MWh).
   * *Status:* Complete & Verified (Timestamp: `2026-07-25T20:00:00+02:00`).

5. **[Note #005: ENTSO-E Cross-Border Physical Flow Dynamics Baseline](./notes/005-entsoe-crossborder-flows)**
   * *Scope:* Central-Western European (CWE) bidding zone interconnections (`AT ↔ DE`, `BE ↔ NL`, `FR ↔ BE`, `NL ↔ DE`) from 1 Jun 2025 – 30 Jun 2026 (181,917 sub-hourly records).
   * *Focus:* Intra-corridor physical flow dynamics ($|P_{\text{flow}}|$ MW), flow volatility, peak load factors, Rule A exclusion audit & Rule D intra-corridor self-distribution compliance.
   * *Status:* Complete & Verified (Timestamp: `2026-07-28T23:00:00+02:00`).

---
*Developed by VolMax Studio Lab | [volmax-studio.rs](https://www.volmax-studio.rs) | Because trust should be verifiable.*
