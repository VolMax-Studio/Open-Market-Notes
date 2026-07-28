# DECISIONS — Open Market Note #005 (ENTSO-E High Utilization Duration Baseline)

> **Document Type:** Append-Only Pre-Registration Decision Ledger  
> **Status:** Locked for L0 Data Download  
> **Protocol Stack:**  
> - `market-note-baseline v1.4.0`  
> - `p10-gate v1.1.0`  
> - `p10-client-audit v1.0.0`

---

## Decision Impact Matrix (Dependency Graph)

| Decision ID | Target Area | Affected Downstream Artifacts |
| :---: | :--- | :--- |
| `D-001` | High Utilization Threshold ($\ge 90\%$) | M1 computation, summary.json, figures, README |
| `D-002` | Spatial Scope (5 Corridors) | API query loop, data_manifest.json, summary.json |
| `D-003` | Capacity Denominator Hierarchy | Data parser, exclusion filter, summary.json |
| `D-004` | Directional Neutrality ($|P_{\text{flow}}|$) | Flow sign logic, figures, README |
| `D-005` | Sub-Hourly Normalization | Time-weighting calculator, event duration sum |

---

## Decision Log

### D-001 — Threshold Choice for High Utilization Metric ($M_1$)
- **Status:** `Active`
- **Question:** What percentage threshold defines the High Utilization state across cross-border interconnections?
- **Alternatives Considered:** $80\%$, $85\%$, $90\%$, $95\%$.
- **Choice Made:** $\ge 90\%$ of reported transfer capacity ($C_{\text{ref}}$).
- **A-Priori Justification:** $90\%$ was selected as the operational threshold for this baseline to isolate sustained high-utilisation periods while reducing inclusion of routine operating variability.
- **Evidence Required:**
  - [x] ENTSO-E Physical Flow API field (`quantity` / `A11`)
  - [x] ENTSO-E Transfer Capacity field (`ATC`/`NTC` or $P_{\text{max}}$)
  - [x] Pre-registered mathematical threshold condition ($U_t \ge 0.90$)

---

### D-002 — Spatial Corridor Scope
- **Status:** `Active`
- **Question:** Which ENTSO-E bidding zone corridors should be included in the 13-month baseline?
- **Alternatives Considered:** All 30+ European borders vs 5 key Central-Western European (CWE) corridors.
- **Choice Made:** 5 key interconnections (`NL ↔ DE`, `BE ↔ NL`, `AT ↔ DE`, `DK1 ↔ DE`, `FR ↔ BE`).
- **A-Priori Justification:** These five corridors represent high-volume renewable export/import seams (solar/wind shifts between Germany, Benelux, Austria, and Scandinavia) with clean, high-resolution ENTSO-E telemetry.
- **Evidence Required:**
  - [x] ENTSO-E EIC domain codes for 6 bidding zones
  - [x] Operational API availability for bi-directional flows
  - [x] Overlapping 13-month history window

---

### D-003 — Denominator Hierarchy Rule
- **Status:** `Active`
- **Question:** How to handle discrepancies between Net Transfer Capacity ($NTC$/$ATC$) and physical nameplate rating ($P_{\text{max}}$)?
- **Alternatives Considered:** Arbitrary fallback or mixing $NTC$ and $P_{\text{max}}$.
- **Choice Made:** Strict 3-tier hierarchy (Tier 1: $ATC$/$NTC$; Tier 2: Permanent $P_{\text{max}}$; Tier 3: Exclude corridor).
- **A-Priori Justification:** Prevents distortion of the utilization metric by eliminating non-verifiable or unannounced transmission limits.
- **Evidence Required:**
  - [x] ENTSO-E Parameter manual for DocumentType `A11` vs `A65`
  - [x] Exclusion rule trigger in data parser (`Tier 3 -> Exclude`)

---

### D-004 — Directional Neutrality
- **Status:** `Active`
- **Question:** Should M1 separate import vs export trade directions?
- **Alternatives Considered:** Separate M1 into directional metrics vs single absolute value metric $|P_{\text{flow}}|$.
- **Choice Made:** Absolute value $|P_{\text{flow}}|$ (Directional Neutrality).
- **A-Priori Justification:** M1 measures physical infrastructure capacity utilization. Commercial trade direction or market arbitrage direction belongs to separate market-coupling notes.
- **Evidence Required:**
  - [x] Absolute value operator $|P_{\text{flow}, t}|$ in pipeline core logic

---

### D-005 — Sub-Hourly Normalization Rule
- **Status:** `Active`
- **Question:** How are sub-hourly (15-min / 30-min) telemetry intervals aggregated into hourly duration?
- **Alternatives Considered:** Binary hourly threshold vs linear time-weighted interval sum.
- **Choice Made:** Linear time-weighting (15-min interval $= 0.25\text{ h}$, 30-min interval $= 0.50\text{ h}$, 60-min interval $= 1.00\text{ h}$).
- **A-Priori Justification:** Preserves exact physical duration without artificial hour-rounding or discretization artifacts.
- **Evidence Required:**
  - [x] Timestamp delta calculator in aggregation pipeline

---
*VolMax Studio Lab · Open Market Note #005 Decision Ledger*
