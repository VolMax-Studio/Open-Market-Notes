# VolMax Open Market Note #003: Operational Parameters & Data Rules

> **Version:** 3.1.0  
> **Status:** Frozen Baseline Specification  
> **Target Dataset:** ENTSO-E Transparency Platform Imbalance Prices (17.1.g / 17.2.f)  
> **Analysis Period:** 1 June 2025 – 30 June 2026 (13 Months / 395 Days)

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
