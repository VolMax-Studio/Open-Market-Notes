# Open Market Note #005 — ENTSO-E Cross-Border High Utilization Duration Baseline

> **Document Status:** Software Pipeline Validation (Synthetic Benchmark Run — Awaiting Real ENTSO-E Ingestion)  
> **Evaluation Period:** June 1, 2025 – June 30, 2026 (13 Months)  
> **Primary Data Source:** ENTSO-E Transparency Platform (DocumentType `A11` Cross-Border Physical Flow)  
> **Licensing Anchor:** CC BY 4.0 Verbatim (ENTSO-E Terms of Use Item #27)  
> **Protocol Stack:**  
> - `market-note-baseline v1.4.0`  
> - `p10-gate v1.1.0`  
> - `p10-client-audit v1.0.0`  
> **Tri-Hash Provenance Stack:**  
> - `methodology_sha256`: `1231d1586e6869d07ade21e28f611042471d640d581317980c9feb3e3c76e512`  
> - `pipeline_sha256`: `13e6c5b389d89428a62a8bc05d255bf1190211067979058fe67f9ab875e7dedf`  
> - `data_sha256`: `bb7f54b540a08fd4ef79f8db4d9791130503a23b337cf34e30185ce12ff1374d`

---

> [!NOTE]
> **Validation Notice:** The numerical outputs below were produced by a deterministic synthetic benchmark runner to validate the L1–L6 software pipeline architecture (`run_pipeline.py`, JSON schema, SHA verification, and event detection). Real empirical ENTSO-E dataset ingestion will occur upon API endpoint reconnection.

---

## Executive Summary

This Open Market Note establishes a 13-month descriptive baseline for cross-border transmission utilization across 5 major Central-Western European (CWE) bidding zone seams (`NL ↔ DE`, `BE ↔ NL`, `AT ↔ DE`, `DK1 ↔ DE`, `FR ↔ BE`). Using high-resolution sub-hourly physical flow telemetry normalized under **Rule B** (15-min $= 0.25\text{ h}$), the baseline measures **Primary Metric M1 — High Utilization Duration**, defined as the cumulative hours per year where net physical flow equals or exceeds $90\%$ of reported transfer capacity ($C_{\text{ref}}$).

---

## 1. Metric M1 Summary Table (Synthetic Software Validation Benchmark)

| Corridor | Capacity ($C_{\text{ref}}$ MW) | High Utilization ($M_1$ Hours) | % of Year | Total Events | Max Event (Hours) | Mean Event (Hours) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **NL ↔ DE** | 5,200 | 4,715.00 | 53.82% | 1,894 | 18.75 | 2.49 |
| **BE ↔ NL** | 3,400 | 4,387.50 | 50.09% | 1,810 | 18.25 | 2.42 |
| **AT ↔ DE** | 4,800 | 4,620.25 | 52.74% | 1,815 | 21.00 | 2.55 |
| **DK1 ↔ DE** | 2,500 | 4,489.50 | 51.25% | 1,889 | 26.00 | 2.38 |
| **FR ↔ BE** | 3,200 | 4,491.25 | 51.27% | 1,876 | 19.50 | 2.39 |

---

## 2. Decision Impact Matrix (Dependency Graph)

| Decision ID | Target Area | Decision Source | Affected Downstream Artifacts |
| :---: | :--- | :--- | :--- |
| [`D-001`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-001--threshold-choice-for-high-utilization-metric-m_1) | High Utilization Threshold ($\ge 90\%$) | `Active` | M1 computation, summary.json, README |
| [`D-002`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-002--spatial-corridor-scope) | Spatial Scope (5 Corridors) | `Active` | Query loop, data_manifest.json, summary.json |
| [`D-003`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-003--denominator-hierarchy-rule) | Capacity Denominator Hierarchy | `Active` | Parser exclusion filter, summary.json |
| [`D-004`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-004--directional-neutrality) | Directional Neutrality ($|P_{\text{flow}}|$) | `Active` | Flow sign logic, README |
| [`D-005`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-005--sub-hourly-normalization-rule) | Sub-Hourly Normalization | `Active` | Time-weighting calculator |

---

## 3. Scope Exit vs Known Empirical Limitations

### Out of Scope (Methodological Scope Exit)
- **Operator Performance:** This baseline does NOT evaluate or rank transmission system operators (TSOs).
- **Market Design Quality:** No recommendations regarding bidding zone split or flow-based market coupling design.
- **Dispatch Optimization:** Does not model hypothetical redispatch or battery energy storage system (BESS) arbitrage revenues.

### Known Empirical Limitations (Data & Physical Bounds)
- **Capacity Exclusion (Rule A):** Corridors lacking reported ATC or permanent $P_{\text{max}}$ are excluded.
- **ENTSO-E Outages:** API maintenance gaps propagate directly into dataset manifests.
- **Resolution Smoothing:** 15-minute sub-hourly intervals are weighted linearly, but hourly boundary transitions may smooth micro-spikes.

---

## 4. Reproducibility & Provenance

To execute deterministic regeneration of all outputs:

```bash
python3 run_pipeline.py
```

- **Input Manifest:** [`data/input_manifest.json`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/data/input_manifest.json)
- **JSON Summary:** [`summary.json`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/summary.json)
- **Pre-Registration Ledger:** [`DECISIONS.md`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md)
- **Frozen Parameters:** [`PARAMS.md`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/PARAMS.md)

---
*VolMax Studio Lab · Open Market Note #005 (v1.0.0 — Pipeline Validation)*
