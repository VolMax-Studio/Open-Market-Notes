---
# Parameter Ledger Metadata & Licensing Anchors
license:
  source_repo: "https://github.com/VolMax-Studio/P10-Verification-Method"
  source_repo_commit: "9eac8561c231c5eceea3a8e8b6662e1673e9e1e2"
  source_register: "L-04, L-08"
  clause: "ENTSO-E ToU Article 2.5"
  list_version: "18/10/2023"
  list_sha256: "b21717e8a5a41b9b8544db730d11c2a717abc9b07f89704437a89332b708ff9a"
  data_item: 27
  regulation_article: "17.1.g / 17.2.f"
time_contract:
  timezone: "UTC"
  timestamp_convention: "interval_beginning"
  sampling_step_seconds: 900
  sampling_step_minutes: 15
  window_bounds: "[start, end)"
  window_start_utc: "2025-06-01T00:00:00Z"
  window_end_utc: "2026-07-01T00:00:00Z"
  total_days: 395
  intervals_per_day: 96
  nominal_intervals: 37920  # verification check: derived from (window_end_utc - window_start_utc).days * 96
quality_contract:
  min_completeness_ratio: 0.98
  max_telemetry_gap_minutes: 90 # [POST-HOC EMPIRICAL CALIBRATION] Calibrated to maximum observed historical gap in DK_1/DK_2 (10 Aug 2025). No external normative/regulatory source established.
---

# VolMax Open Market Note #003: Operational Parameters & Data Rules

> **Version:** 3.2.0  
> **Status:** Frozen Baseline Specification  
> **Target Dataset:** ENTSO-E Transparency Platform Imbalance Prices (17.1.g / 17.2.f)  
> **Licensing Anchor:** CC BY 4.0 (ENTSO-E ToU Article 2.5 / Open Data Item #27 [Article 17.1.g / 17.2.f])  
> **Analysis Period:** 1 June 2025 00:00:00Z – 30 June 2026 23:45:00Z (13 Months / 395 Days / 37,920 MTUs)

---

## 1. Parametric Changelog (v3.0.0 -> v3.1.0)

> [!IMPORTANT]
> **Refinement of Metric 1 (M1) Scarcity Event Definition:**
> - **v3.0.0 (Gap Bridging Heuristic - Superceded):** Defined events by bridging gaps of $<30\text{ minutes}$ (1 interval drop below threshold). Empirical audit proved this bridging loop introduced recursive fragmentation artifacts, inflating event counts up to 18,500+ and collapsing discrete percentiles to $P_{50} = P_{90} = 15.0\text{ min}$.
> - **v3.1.0 (Strict Contiguous Blocks - Active Baseline):** Replaced heuristic bridging with **Strict Contiguous Block Evaluation**. An M1 event is defined strictly as an uninterrupted sequence of 15-minute intervals where the imbalance price remains $\ge €100/\text{MWh}$ (or $\ge €250/\text{MWh}$).
> - **Impact:** Eliminates artificial fragment artifacts and reveals the true physical continuous plateau durations of grid shortage pricing across Europe.

---

## 2. Ingestion & Provenance Rules

1. **Target Bidding Zones (6 Verified Zones):**
   - `NL` (Netherlands / `10YNL----------L`)
   - `BE` (Belgium / `10YBE----------X`)
   - `FR` (France / `10YFR-RTE------C`)
   - `DK_1` (Denmark West / `10YDK-1--------W`)
   - `DK_2` (Denmark East / `10YDK-2--------T`)
   - `AT` (Austria / `10YAT-APG------L`)
   *Boundary Exclusion:* `DE-LU` (Germany) is excluded because German TSOs publish imbalance settlement prices via `regelleistung.net` rather than DocumentType `A85` on the ENTSO-E REST API.

2. **Provenance & Auditing:**
   - All extracted raw XML payloads and Feather datasets must be hashed (SHA-256) and cataloged in `data_manifest.json`.

3. **Time Contract & Interval Invariants:**
   - **Timezone Domain:** Strict **`UTC`** (`timestamp_tz: UTC`).
   - **Timestamp Convention:** **`interval_beginning`** (each 15-minute MTU is indexed by its starting timestamp: `00:00:00` through `23:45:00`).
   - **Baseline Ingestion Bounds:**
     - $\text{Start MTU} = \text{2025-06-01 00:00:00Z}$
     - $\text{End MTU} = \text{2026-06-30 23:45:00Z}$ (covering the half-open temporal span $[\text{2025-06-01T00:00:00Z}, \text{2026-07-01T00:00:00Z})$).
   - **Nominal Interval Invariant Formula:**
     $$\text{Total Days} = 395 \text{ calendar days}$$
     $$\text{MTUs per Day} = 24 \text{ hours} \times 4 \text{ MTUs/hour} = 96 \text{ MTUs/day}$$
     $$\text{Nominal Intervals} = N_{\text{days}} \times 96 = 395 \times 96 = \mathbf{37,920 \text{ MTUs}}$$
   - **Zero DST Discontinuity:** In strict UTC, every calendar day comprises exactly $96$ MTUs, ensuring mathematical invariance across daylight saving transitions (October 2025 and March 2026).

---

## 3. Procedural Column Mapping Rules

Per ENTSO-E Electricity Balancing Guideline (EBGL) specifications:
- **Dual-Pricing Regimes (`NL`, `FR`):**
  - **M1 (System Shortage Scarcity):** Evaluated strictly on the `Short` column ($P_{\text{imb}}^{-}$).
  - **M2 (Grid Surplus Absorption):** Evaluated strictly on the `Long` column ($P_{\text{imb}}^{+}$).
- **Single-Pricing Regimes (`BE`, `DK_1`, `DK_2`, `AT`):**
  - Both M1 and M2 are evaluated on the unified $P_{\text{imb}}$ series ($P_{\text{imb}}^{+} == P_{\text{imb}}^{-}$). Raw XML audit confirms TSOs publish equal prices in categories `A04` and `A05`.

---

## 4. Parameter Freeze Matrix

| Parameter ID | Parameter Description | Frozen Value / Metric | Epistemological / Physical Rationale |
| :--- | :--- | :--- | :--- |
| **`M1_THRESH_A`** | Moderate Shortage Threshold | **$\ge €100/\text{MWh}$** | Reflects TSO scarcity activation trigger rate. |
| **`M1_THRESH_B`** | Extreme Shortage Threshold | **$\ge €250/\text{MWh}$** | Reflects severe system deficit peaker activation. |
| **`M1_EVAL_TYPE`** | Event Duration Definition | **Strict Contiguous Block (v3.1.0)** | Evaluates continuous uninterrupted price plateaus. |
| **`M2_THRESH_CHEAP`**| Grid Surplus Absorption Rate | **$\le €25/\text{MWh}$** | Economic signal for BESS demand absorption. |
| **`M2_THRESH_ZERO`** | Zero/Negative Rate | **$\le €0/\text{MWh}$** | Financial penalty/reward for over-frequency mitigation. |
| **`M2_4H_WINDOW`** | 4h BESS Absorption Target | **$\ge 4.8\text{ Hours}$** | $4.0\text{h} \div 0.85\text{ RTE} = 4.706\text{h}$ (conservative round-up). |
| **`M2_8H_WINDOW`** | 8h BESS Absorption Target | **$\ge 9.5\text{ Hours}$** | $8.0\text{h} \div 0.85\text{ RTE} = 9.412\text{h}$ (conservative round-up). |

---

## 5. Cross-Zonal Incomparability Rule

Direct quantitative comparison of raw price levels or event metrics between zones operating under different settlement rules (e.g. Dual-Pricing in FR/NL vs Single-Pricing in BE/DK/AT) is prohibited without regime-neutral normalization.

---
*Specification Locked | VolMax Studio Engineering Team | 2026-07-27*
