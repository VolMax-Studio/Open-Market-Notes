# PARAMS — Open Market Note #005 (ENTSO-E High Utilization Duration Baseline)

> **Document Status:** Frozen for L0 Release  
> **Version:** `v1.3.0`  
> **Date Frozen:** `2026-07-28T19:40:00+02:00`  
> **Licensing Anchor:** ENTSO-E Transparency Platform Terms of Use Item #27 (CC BY 4.0 Verbatim)  
> **Protocol Stack:**  
> - `market-note-baseline v1.4.0`  
> - `p10-gate v1.1.0`  
> - `p10-client-audit v1.0.0`

---

## 1. Scope Classification, Scope Exit & Empirical Limitations

```text
Type:
Descriptive Market Measurement

Out of Scope (Intentionally Unanswered Questions):
- Operator performance evaluation
- Market design quality assessment
- Investment recommendations
- Dispatch optimization modeling
- Causal attribution of physical bottlenecks

Known Empirical Limitations (Data & Physical System Bounds):
- Missing or unannounced ATC values trigger corridor exclusion (Rule A / D-003).
- ENTSO-E API server maintenance or transmission outages propagate into dataset gaps.
- Mixed sampling resolutions (15m vs 60m) are normalized per Rule B (D-005), but sub-hourly dynamics are smoothed u 60m zones.
- TSO settlement publication delays may cause minor historical revisions in raw ENTSO-E payloads.
```

---

## 2. Decision Impact Matrix (Dependency Graph)

| Decision ID | Target Area | Affected Downstream Artifacts |
| :---: | :--- | :--- |
| `D-001` | High Utilization Threshold ($\ge 90\%$) | M1 computation, summary.json, figures, README |
| `D-002` | Spatial Scope (5 Corridors) | API query loop, data_manifest.json, summary.json |
| `D-003` | Capacity Denominator Hierarchy | Data parser, exclusion filter, summary.json |
| `D-004` | Directional Neutrality ($|P_{\text{flow}}|$) | Flow sign logic, figures, README |
| `D-005` | Sub-Hourly Normalization | Time-weighting calculator, event duration sum |

---

## 3. Core Metric Definition

### Primary Metric: M1 — High Utilization Duration ($\ge 90\%$ Capacity)
* **Decision Source:** [`D-001`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-001--threshold-choice-for-high-utilization-metric-m_1)
- **Definition:** The cumulative duration (hours per year) during which net physical power flow ($P_{\text{flow}}$) across a cross-border interconnection equals or exceeds $90\%$ of the reported reference capacity ($C_{\text{ref}}$).
- **Mathematical Expression:**
  $$\text{Utilization Ratio } (U_t) = \frac{|P_{\text{flow}, t}|}{C_{\text{ref}, t}}$$
  $$\text{High Utilization Condition } \iff U_t \ge 0.90$$

---

## 4. Mandatory Metric Rules (Hierarchy, Normalization, Direction)

### Rule A — Capacity Denominator Hierarchy
* **Decision Source:** [`D-003`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-003--denominator-hierarchy-rule)
To eliminate ambiguity, reference capacity $C_{\text{ref}}$ MUST strictly follow this 3-tier hierarchy:
1. **Tier 1:** Use reported Available Transfer Capacity ($ATC$) / Net Transfer Capacity ($NTC$) for period $t$, if available.
2. **Tier 2:** If $ATC$/$NTC$ is unannounced, use reported Permanent Transmission Physical Limit ($P_{\text{max}}$).
3. **Tier 3:** If neither $ATC$/$NTC$ nor $P_{\text{max}}$ is available, **EXCLUDE the corridor** from M1 computation (falling back to unverified guesses is prohibited).

### Rule B — Sub-Hourly Normalization Rule
* **Decision Source:** [`D-005`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-005--sub-hourly-normalization-rule)
Sub-hourly sampling intervals contribute proportionally to cumulative duration:
- Each 15-minute interval where $U_t \ge 0.90$ contributes exactly **0.25 hours**.
- Each 30-minute interval where $U_t \ge 0.90$ contributes exactly **0.50 hours**.
- Each 60-minute interval where $U_t \ge 0.90$ contributes exactly **1.00 hour**.
- **Contiguous Event Definition:** An event is defined as a contiguous sequence of intervals satisfying $U_t \ge 0.90$. Total event duration equals the sum of sub-hourly interval contributions.

### Rule C — Directional Neutrality
* **Decision Source:** [`D-004`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-004--directional-neutrality)
- **Absolute Value Usage:** The formula uses $|P_{\text{flow}, t}|$. Direction is intentionally ignored because M1 measures physical infrastructure capacity utilization, not commercial trade direction or import/export bias.

---

## 5. Evaluated Interconnection Corridors
* **Decision Source:** [`D-002`](file:///home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/005-entsoe-crossborder-flows/DECISIONS.md#d-002--spatial-corridor-scope)

The 13-month baseline (June 1, 2025 – June 30, 2026) evaluates five key ENTSO-E cross-border corridors:
1. `NL ↔ DE` (Netherlands — Germany)
2. `BE ↔ NL` (Belgium — Netherlands)
3. `AT ↔ DE` (Austria — Germany)
4. `DK1 ↔ DE` (Denmark 1 — Germany)
5. `FR ↔ BE` (France — Belgium)

---

## 6. Primary Data Source & Provenance

- **API Endpoint:** ENTSO-E Transparency Platform — Cross-Border Physical Flow (`12.1.D` / DocumentType `A11`).
- **Data Resolution:** 15-minute, 30-minute, or 60-minute resolution, normalized per Rule B.
- **License Anchor:** CC BY 4.0 (ENTSO-E ToU Item #27). Raw XML files frozen in `data/` with SHA-256 hashes logged in `data_manifest.json`.

---

## 7. Parametric Changelog

| Version | Date | Change Description | Empirical Justification |
| :---: | :---: | :--- | :--- |
| `v1.3.0` | 2026-07-28 | Added Decision Impact Matrix dependency graph and updated Protocol Stack to v1.4.0. | Provided immediate visibility into downstream computational artifacts affected by decision changes. |
| `v1.2.0` | 2026-07-28 | Added Known Empirical Limitations section and mapped Rule B to Decision D-005. | Explicitly separated empirical data limits from methodological scope exits; ensured 100% 1-to-1 decision mapping. |
| `v1.1.0` | 2026-07-28 | Added strict 3-tier Capacity Hierarchy, Sub-hourly Normalization rule, Directional Neutrality clause, and Decision Source links. | Resolved denominator ambiguity (ATC vs Pmax) and linked parameters directly to Decision Ledger prior to data ingestion. |
| `v1.0.0` | 2026-07-28 | Initial protocol freeze. Defined M1 High Utilization Duration ($\ge 90\%$) with strict contiguous blocks. | Frozen prior to data download per P10 L0 rules. |

---
*VolMax Studio Lab · Open Market Note #005 Baseline Standard*
