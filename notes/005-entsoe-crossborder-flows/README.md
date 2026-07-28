# Open Market Note #005 — ENTSO-E Cross-Border Transmission Telemetry Baseline

> **Document Status:** Under Review (Methodology Metric Pivot Required — Rule A Exclusion Triggered)  
> **Evaluation Period:** June 1, 2025 – June 30, 2026 (13 Months)  
> **Primary Data Source:** ENTSO-E Transparency Platform (DocumentType `A11` Cross-Border Physical Flow, 181,917 sub-hourly records)  
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

## Executive Summary & P10 Gate Finding

Per **Rule A (`D-003 Denominator Hierarchy`)**, any capacity denominator ($C_{\text{ref}}$) MUST be ingested directly from measured ENTSO-E Total Transfer Capacity (NTC/ATC) telemetry. Fallbacks to hardcoded nameplate estimates or commercial allocation results (`A09` Already Allocated Capacity) are strictly prohibited because:
1. Hardcoded static capacities ($5,200\text{ MW}, 4,800\text{ MW}$) distort utilization metrics depending on arbitrary user inputs.
2. Commercial allocation results (`A09`) measure net auction clearing quantities rather than total physical transfer capacity, leading to artificial directional capacity zeros and corrupted utilization ratios.

Because ENTSO-E does not disclose directional Total NTC ($A61/A26$) under CC BY 4.0 for Central Western European flow-based bidding zone borders, **all evaluated corridors are classified as TIER 3 (EXCLUDED FOR METRIC M1)** per Rule A.

---

## 1. Metric M1 Exclusion Table (Rule A Compliance)

| Corridor | Measured Physical Flow ($A11$) | Total NTC Telemetry ($A61$) | Metric M1 Status | Reason for Exclusion |
| :--- | :---: | :---: | :---: | :--- |
| **AT ↔ DE** | Ingested (100% Real) | Missing in API | **EXCLUDED (Rule A)** | Total NTC telemetry unannounced under CC BY 4.0 |
| **NL ↔ DE** | Ingested (100% Real) | Missing in API | **EXCLUDED (Rule A)** | Total NTC telemetry unannounced under CC BY 4.0 |
| **FR ↔ BE** | Ingested (100% Real) | Missing in API | **EXCLUDED (Rule A)** | Total NTC telemetry unannounced under CC BY 4.0 |
| **BE ↔ NL** | Ingested (100% Real) | Missing in API | **EXCLUDED (Rule A)** | Total NTC telemetry unannounced under CC BY 4.0 |
| **DK1 ↔ DE** | Ingested (100% Real) | Missing in API | **EXCLUDED (Rule A)** | Total NTC telemetry unannounced under CC BY 4.0 |

---

## 2. P10 Forensic Audit Log (Pattern #9 Discovery)

```
[AUDIT FINDING - P10 GATE PATTERN #9]
Issue: Hardcoded or mismatched capacity denominator carried over from mock/synthetic runner.
Impact: Utilization ratio U_t = |P_flow| / C_ref is hyper-sensitive to C_ref. 
Action: Enforce Rule A. Classify M1 as Excluded until dynamic Total NTC API integration is established.
Status: Document Status set to Under Review.
```

---

## 3. Decision Impact Matrix (Dependency Graph)

| Decision ID | Target Area | Decision Source | Affected Downstream Artifacts |
| :---: | :--- | :--- | :--- |
| [`D-001`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-001--threshold-choice-for-high-utilization-metric-m_1) | High Utilization Threshold ($\ge 90\%$) | `Active` | Metric M1 definition |
| [`D-002`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-002--spatial-corridor-scope) | Spatial Scope (4 Corridors evaluated) | `Active` | Query loop, data_manifest.json |
| [`D-003`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-003--denominator-hierarchy-rule) | Capacity Denominator Hierarchy | `Active` | **Rule A Exclusion Enforcement** |

---

## 4. Next Steps for Note #005
1. Pivot Note #005 primary metric from $M_1$ (Utilization Ratio) to an absolute physical flow metric (e.g., **$M_2$ Net Physical Flow Volatility & Peak Inter-Bidding Zone Transfers**), which relies 100% on the ingested 181,917 real $A11$ physical flow records without requiring an unannounced capacity denominator.

---
*VolMax Studio Lab · Open Market Note #005 (v1.0.0 — Under Review per Rule A Exclusion)*
