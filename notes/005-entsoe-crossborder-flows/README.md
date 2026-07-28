# Open Market Note #005 — ENTSO-E Cross-Border High Utilization Duration Baseline

> **Document Status:** Complete (Empirical Findings Verified)  
> **Evaluation Period:** June 1, 2025 – June 30, 2026 (13 Months)  
> **Primary Data Source:** ENTSO-E Transparency Platform (DocumentType `A11` Cross-Border Physical Flow)  
> **Licensing Anchor:** CC BY 4.0 Verbatim (ENTSO-E Terms of Use Item #27)  
> **Protocol Stack:**  
> - `market-note-baseline v1.4.0`  
> - `p10-gate v1.1.0`  
> - `p10-client-audit v1.0.0`  
> **Tri-Hash Provenance Stack:**  
> - `methodology_sha256`: `1231d1586e6869d07ade21e28f611042471d640d581317980c9feb3e3c76e512`  
> - `pipeline_sha256`: `4709426580b01b315b1337028c97a3bacc8a1edb4e66a5fdde5f1c32aab6be23`  
> - `data_sha256`: `cbbfebcda91af51f316575040d8f28ccfed7f1c50e750c674037e8b01f02c638`

---

## Executive Summary

This Open Market Note establishes a 13-month descriptive baseline for cross-border transmission utilization across 4 evaluated Central-Western European (CWE) bidding zone interconnections (`NL ↔ DE`, `BE ↔ NL`, `AT ↔ DE`, `FR ↔ BE`). Using 181,917 sub-hourly physical flow telemetry records normalized under **Rule B** (15-min $= 0.25\text{ h}$), the baseline measures **Primary Metric M1 — High Utilization Duration**, defined as the cumulative hours per year where net physical flow equals or exceeds $90\%$ of reported transfer capacity ($C_{\text{ref}}$).

### Key Empirical Findings:
1. **Asymmetric Structural Bottlenecks:** `FR ↔ BE` (France–Belgium) experiences severe physical utilization, spending **1,756.00 hours** (18.52% of the period) at $\ge 90\%$ capacity, with continuous congestion events lasting up to **46.00 hours**.
2. **Low-Congestion Interconnections:** In contrast, `AT ↔ DE` (Austria–Germany) registered **0.00 hours** at $\ge 90\%$ capacity, while `NL ↔ DE` registered **64.75 hours** and `BE ↔ NL` registered **1.00 hour**.
3. **Corridor Exclusion (Rule A):** `DK1 ↔ DE` was excluded from M1 calculation per Rule A due to missing API transfer capacity disclosures.

---

## 1. Metric M1 Summary Table (Empirical ENTSO-E Telemetry)

| Corridor | Capacity ($C_{\text{ref}}$ MW) | High Utilization ($M_1$ Hours) | % of Year | Total Events | Max Event (Hours) | Mean Event (Hours) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **FR ↔ BE** | 3,200 | **1,756.00** | 18.52% | 551 | 46.00 | 3.19 |
| **NL ↔ DE** | 5,200 | **64.75** | 0.68% | 72 | 7.00 | 0.90 |
| **BE ↔ NL** | 3,400 | **1.00** | 0.01% | 133 | 1.00 | 0.01 |
| **AT ↔ DE** | 4,800 | **0.00** | 0.00% | 0 | 0.00 | 0.00 |
| **DK1 ↔ DE** | 2,500 | *Excluded (Rule A)* | N/A | N/A | N/A | N/A |

---

## 2. Decision Impact Matrix (Dependency Graph)

| Decision ID | Target Area | Decision Source | Affected Downstream Artifacts |
| :---: | :--- | :--- | :--- |
| [`D-001`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-001--threshold-choice-for-high-utilization-metric-m_1) | High Utilization Threshold ($\ge 90\%$) | `Active` | M1 computation, summary.json, README |
| [`D-002`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-002--spatial-corridor-scope) | Spatial Scope (4 Corridors evaluated) | `Active` | Query loop, data_manifest.json, summary.json |
| [`D-003`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-003--denominator-hierarchy-rule) | Capacity Denominator Hierarchy | `Active` | Parser exclusion filter (DK1 excluded), summary.json |
| [`D-004`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-004--directional-neutrality) | Directional Neutrality ($|P_{\text{flow}}|$) | `Active` | Net flow logic, README |
| [`D-005`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-005--sub-hourly-normalization-rule) | Sub-Hourly Normalization | `Active` | Time-weighting calculator (15m=0.25h) |

---

## 3. Scope Exit vs Known Empirical Limitations

### Out of Scope (Methodological Scope Exit)
- **Operator Performance:** This baseline does NOT evaluate or rank transmission system operators (TSOs).
- **Market Design Quality:** No recommendations regarding bidding zone split or flow-based market coupling design.
- **Dispatch Optimization:** Does not model hypothetical redispatch or battery energy storage system (BESS) arbitrage revenues.

### Known Empirical Limitations (Data & Physical Bounds)
- **Capacity Exclusion (Rule A):** `DK1 ↔ DE` excluded due to missing API transfer capacity disclosures.
- **Resolution Mixing:** Sub-hourly intervals (15m/60m) normalized per Rule B.

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
*VolMax Studio Lab · Open Market Note #005 (v1.0.0 — Empirical ENTSO-E Release)*
