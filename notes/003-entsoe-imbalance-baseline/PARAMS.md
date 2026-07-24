# VolMax Note #3: ENTSO-E Imbalance Duration Baseline — Frozen Parameters
**Class of Work:** VolMax Descriptive Analytical Note (Not a P10 Audit)
**Status:** Frozen
**Frozen Timestamp:** 2026-07-24T22:25:00+02:00

---

## 1. Scope & Datasets
- **Analysis Period:** 1 June 2025 00:00:00 CEST – 30 June 2026 23:59:59 CEST (13 months, localized in `Europe/Brussels` market timezone to eliminate UTC daylight saving shift boundary artifacts).
- **Bidding Zones:** DE-LU (Germany/Luxembourg), FR (France), BE (Belgium), NL (Netherlands).
- **Data Source:** Primary ENTSO-E Transparency Platform (Imbalance prices [17.1.g / 17.2.f]). Selected because it represents the actual financial settlement interval for BESS imbalance arbitrage in European markets. Formally listed on the CC BY 4.0 free re-use list (item #27, "Imbalance prices"), version 18 October 2023, accessed 2026-07-24.
- **Evidence Anchors:**
  - Page 1 License: `PORTFOLIO/VolMax_Lineage_Credit_Sandbox/evidence/ENTSOE_FreeReuse_Page1_License_2026-07-24.png`
  - Page 4 Row 27 Listing: `PORTFOLIO/VolMax_Lineage_Credit_Sandbox/evidence/ENTSOE_FreeReuse_Page4_Row27_ImbalancePrices_2026-07-24.png`
- **Data Provenance Rule:** All raw data files must be accompanied by explicit provenance metadata in `data_manifest.json` (including exact API query endpoint / source URL, UTC acquisition timestamp, sha256 hash, and byte count). Unanchored or silent cache fallbacks without verified provenance metadata are prohibited.
- **BESS Fleet Subsample:** N/A for baseline pricing duration.

---

## 2. Parameter Definitions

### Schema & Procedural Regime Detection Rules
- **Procedural Regime Classification:** The imbalance settlement regime for each bidding zone is determined empirically during data ingestion by evaluating the pairwise relation between `+ Imbalance Price` ($P_{imb}^+$) and `- Imbalance Price` ($P_{imb}^-$) across all 15-minute intervals over the full 13-month analysis period:
  - **Single-Pricing Regime:** If $P_{imb}^+ == P_{imb}^-$ for 100% of valid settlement intervals $\rightarrow$ Zone is empirically classified as **Single-Pricing**. Both M1 (Scarcity $\ge €100/\text{MWh}$ / $\ge €250/\text{MWh}$) and M2 (Cheap Energy $\le €25/\text{MWh}$) evaluate directly on the single unified price time-series $P_{imb}$.
  - **Dual-Pricing Regime:** If $P_{imb}^+ \neq P_{imb}^-$ for any valid interval $\rightarrow$ Zone is empirically classified as **Dual-Pricing**. Column mapping is assigned dynamically based on full-period distribution metrics: M1 (discharge / scarcity value) maps to the deficit settlement distribution (higher positive price spikes), and M2 (charge / cheap energy cost) maps to the surplus settlement distribution.
- **Reporting Rule:** The final regime classification, total valid intervals, pairwise equality percentage, and distribution metrics for each zone are reported as empirical pipeline measurements in Note #003, not pre-assigned in parameter declarations.
- **Co-Measurement Clarification:** In single-pricing regimes, M1 and M2 are co-measured on the same underlying price time series ($P_{imb}$). While a single 15-minute interval cannot meet both thresholds simultaneously ($€100 > €25$), M1 continuous event separation ($<30\text{ minutes}$) and M2 daily cumulative window tracking ($\le €25/\text{MWh}$) operate on the same daily time series independently.



### Metric 1 (M1): Scarcity Pricing Duration
- **Threshold A (Volatility):** 15-minute Imbalance Price $\ge €100/\text{MWh}$.
- **Threshold B (Extreme Scarcity):** 15-minute Imbalance Price $\ge €250/\text{MWh}$.
- **Event Definition:** A continuous sequence of 15-minute intervals meeting the price threshold.
- **Separation Rule:** Events separated by $<30\text{ minutes}$ (less than 2 intervals of 15 minutes) of prices below the threshold are counted as separate events.
- **Metrics Collected:** Histogram of event durations, median, mean, P90, and the maximum single event duration (with date) per Bidding Zone.

### Metric 2 (M2): Charging Window Availability
- **Cheap Energy Threshold:** 15-minute Imbalance Price $\le €25/\text{MWh}$.
- **Accumulation Rule:** Cumulative hours within a single calendar day (00:00 to 00:00 local market time, `Europe/Brussels`). Continuous blocks are *not* required.
- **Target Thresholds (Conservative Ceiling Rounding):**
  - **8-Hour BESS:** Requires $\ge 9.5\text{ hours}$ cumulative cheap pricing ($8\text{ hours} \div 0.85\text{ Round-Trip Efficiency} = 9.412\text{ hours}$, rounded conservatively up to $9.5\text{ hours}$).
  - **4-Hour BESS:** Requires $\ge 4.8\text{ hours}$ cumulative cheap pricing ($4\text{ hours} \div 0.85\text{ Round-Trip Efficiency} = 4.706\text{ hours}$, rounded conservatively up to $4.8\text{ hours}$).
- **Primary Metric:** Percentage of days in the analysis period meeting the cumulative window requirements per Zone.

### Metric 3 (M3): Fleet Cycling Feedback Loop
M3 (fleet cycling) deferred (requires matched operational asset telemetry not covered in this baseline note).

---

## 3. Market References & Citations
- **ENTSO-E Transparency Platform:** Regulation (EU) No 543/2013, Article 17.1.g and 17.2.f.
- **Imbalance Pricing:** Represents the settlement price for energy imbalances in the respective bidding zones. Listed on the ENTSO-E "List of Data available for free re-use" under CC-BY 4.0 (Item #27, document modified 18 Oct 2023, captured 2026-07-24).


