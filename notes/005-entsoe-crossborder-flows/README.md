# Open Market Note #005 — ENTSO-E Cross-Border High Utilization Duration Baseline

> **Document Status:** Complete (100% Empirical Telemetry & Measured NTC Capacities Verified)  
> **Evaluation Period:** June 1, 2025 – June 30, 2026 (13 Months)  
> **Primary Data Sources:**  
> - ENTSO-E Physical Flows: DocumentType `A11` (181,917 sub-hourly records)  
> - ENTSO-E Transfer Capacities: DocumentType `A09` (Final Transfer Capacity / NTC)  
> **Licensing Anchor:** CC BY 4.0 Verbatim (ENTSO-E Terms of Use Item #27)  
> **Protocol Stack:**  
> - `market-note-baseline v1.4.0`  
> - `p10-gate v1.1.0`  
> - `p10-client-audit v1.0.0`  
> **Tri-Hash Provenance Stack:**  
> - `methodology_sha256`: `1231d1586e6869d07ade21e28f611042471d640d581317980c9feb3e3c76e512`  
> - `pipeline_sha256`: `c02fffcc99683f5545e2bcb67ed9706808edb157bda4902bd4be71a8be96f35a`  
> - `data_sha256`: `e79c901af6e18d541f7a64599b0c30e6434aefe0438c49e279a940f8cc519e8b`

---

## Executive Summary

This Open Market Note establishes a 13-month descriptive baseline for cross-border transmission utilization across 4 evaluated Central-Western European (CWE) bidding zone interconnections (`NL ↔ DE`, `BE ↔ NL`, `AT ↔ DE`, `FR ↔ BE`). Both the net physical flow numerators ($A11$) and the dynamic transfer capacity denominators ($A09\text{ NTC}$) are ingested directly from ENTSO-E Transparency Platform telemetry.

### Key Empirical Findings:
1. **Dynamic Capacity vs Static Nameplate Masking:** Evaluating utilization against real measured hour-by-hour Net Transfer Capacities ($A09\text{ NTC}$) reveals that major CWE interconnections operate near physical capacity ($\ge 90\%$) for **5,600 to 5,800 hours per year** (~60% of total time).
2. **Austria–Germany (`AT ↔ DE`) Baseline:** Under static historical assumptions, `AT ↔ DE` appeared un-congested. When evaluated against actual reported dynamic NTC (averaging $1,648.9\text{ MW}$), the corridor spends **5,856.50 hours** at $\ge 90\%$ capacity.
3. **Corridor Exclusion (Rule A):** `DK1 ↔ DE` was excluded from calculation per Rule A due to missing API transfer capacity disclosures.

---

## 1. Metric M1 Summary Table (Measured Flows & Measured A09 NTC Capacities)

| Corridor | Mean Measured NTC ($C_{\text{ref}}$ MW) | High Utilization ($M_1$ Hours) | % of Period | Total Events | Max Event (Hours) | Mean Event (Hours) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **AT ↔ DE** | 1,648.9 | **5,856.50** | 61.62% | 3,310 | 37.75 | 1.77 |
| **NL ↔ DE** | 1,725.2 | **5,707.75** | 60.05% | 5,036 | 42.00 | 1.13 |
| **FR ↔ BE** | 2,346.4 | **5,629.25** | 59.23% | 4,551 | 68.00 | 1.24 |
| **BE ↔ NL** | 1,321.7 | **918.00** | 9.66% | 1,677 | 21.00 | 0.55 |
| **DK1 ↔ DE** | N/A | *Excluded (Rule A)* | N/A | N/A | N/A | N/A |

---

## 2. Decision Impact Matrix (Dependency Graph)

| Decision ID | Target Area | Decision Source | Affected Downstream Artifacts |
| :---: | :--- | :--- | :--- |
| [`D-001`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-001--threshold-choice-for-high-utilization-metric-m_1) | High Utilization Threshold ($\ge 90\%$) | `Active` | M1 computation, summary.json, README |
| [`D-002`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-002--spatial-corridor-scope) | Spatial Scope (4 Corridors evaluated) | `Active` | Query loop, data_manifest.json, summary.json |
| [`D-003`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-003--denominator-hierarchy-rule) | Capacity Denominator Hierarchy | `Active` | Measured A09 NTC integration |
| [`D-004`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-004--directional-neutrality) | Directional Neutrality ($|P_{\text{flow}}|$) | `Active` | Net flow logic, README |
| [`D-005`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-005--sub-hourly-normalization-rule) | Sub-Hourly Normalization | `Active` | Time-weighting calculator (15m=0.25h) |

---

## 3. Scope Exit vs Known Empirical Limitations

### Out of Scope (Methodological Scope Exit)
- **Operator Performance:** This baseline does NOT evaluate or rank transmission system operators (TSOs).
- **Market Design Quality:** No recommendations regarding bidding zone split or flow-based market coupling design.
- **Dispatch Optimization:** Does not model hypothetical redispatch or battery energy storage system (BESS) arbitrage revenues.

### Known Empirical Limitations (Data & Physical Bounds)
- **Dynamic Capacity Variations:** Capacities fluctuate based on seasonal thermal ratings and N-1 security limits as published in ENTSO-E $A09$ payloads.
- **Corridor Exclusion:** `DK1 ↔ DE` excluded per Rule A due to unannounced API capacity disclosures.

---

## 4. Reproducibility & Provenance

To execute deterministic regeneration of all outputs:

```bash
python3 run_pipeline.py
```

- **Raw Payload Manifest:** [`data/data_manifest.json`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/data/data_manifest.json)
- **Input Manifest:** [`data/input_manifest.json`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/data/input_manifest.json)
- **JSON Summary:** [`summary.json`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/summary.json)
- **Pre-Registration Ledger:** [`DECISIONS.md`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md)
- **Frozen Parameters:** [`PARAMS.md`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/PARAMS.md)

---
*VolMax Studio Lab · Open Market Note #005 (v1.0.0 — Verified Empirical Release)*
