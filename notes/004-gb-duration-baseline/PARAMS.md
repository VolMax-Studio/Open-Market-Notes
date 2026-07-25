# VolMax Note #4: GB (Elexon BMRS) Duration Baseline — Frozen Parameters
**Class of Work:** VolMax Descriptive Analytical Note (Not a P10 Audit)
**Status:** Frozen
**Frozen Timestamp:** 2026-07-25T20:00:00+02:00

---

## 1. Scope & Datasets
- **Analysis Period:** 1 June 2025 00:00:00 BST – 30 June 2026 23:59:59 BST (13 months, localized in `Europe/London` market timezone to eliminate UTC daylight saving boundary shift artifacts).
- **Market / Bidding Zone:** Great Britain (GB / NGET Grid Area).
- **Resolution:** 30-minute Settlement Periods (48 settlement periods per calendar day).
- **Data Source:** Primary Elexon Insights Solution REST API (System Prices Endpoint: `https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices/{settlementDate}`). Formally listed as Open Data under the Elexon Open Data License / Open Government License v3.0 (free commercial and non-commercial re-use).
- **Data Provenance Rule:** All raw data files must be accompanied by explicit provenance metadata in `data_manifest.json` (including exact REST API query URL, UTC acquisition timestamp, sha256 hash, and byte count).
- **BESS Fleet Subsample:** N/A for baseline pricing duration.

---

## 2. Parameter Definitions

### Schema & Procedural Regime Classification Rules
- **Settlement Price Mapping:** Great Britain operates under Single Imbalance Pricing (System Buy Price = System Sell Price = $P_{sys}$).
- **Procedural Regime Verification:** The ingestion pipeline verifies pairwise integer equality ($systemSellPrice == systemBuyPrice$) across 100% of settlement periods over the 13-month analysis period.
- **Metric Mapping:**
  - **Metric 1 (Scarcity / Discharge):** Evaluated directly against the 30-minute System Price $P_{sys}$.
  - **Metric 2 (Cheap Energy / Charge):** Evaluated directly against the 30-minute System Price $P_{sys}$.
- **Co-Measurement Clarification:** M1 and M2 are co-measured on the same underlying price time series ($P_{sys}$). While a single 30-minute settlement period cannot meet both thresholds simultaneously ($£100 > £25$), M1 continuous event separation ($<60\text{ minutes}$) and M2 daily cumulative window tracking ($\le £25/\text{MWh}$) operate on the same daily time series independently.

### Metric 1 (M1): Scarcity Pricing Duration
- **Threshold A (Volatility):** 30-minute System Price $\ge £100/\text{MWh}$.
- **Threshold B (Extreme Scarcity):** 30-minute System Price $\ge £250/\text{MWh}$.
- **Event Definition:** A continuous sequence of 30-minute settlement periods meeting the price threshold.
- **Separation Rule:** Events separated by $<60\text{ minutes}$ (less than 2 settlement periods of 30 minutes) of prices below the threshold are counted as separate events.
- **Metrics Collected:** Histogram of event durations, median, mean, P90, and the maximum single event duration (with date) for the GB market.

### Metric 2 (M2): Charging Window Availability
- **Cheap Energy Threshold:** 30-minute System Price $\le £25/\text{MWh}$.
- **Accumulation Rule:** Cumulative hours within a single calendar day (00:00 to 00:00 local market time, `Europe/London`). Continuous blocks are *not* required.
- **Target Thresholds (Conservative Ceiling Rounding):**
  - **8-Hour BESS:** Requires $\ge 9.5\text{ hours}$ cumulative cheap pricing ($8\text{ hours} \div 0.85\text{ Round-Trip Efficiency} = 9.412\text{ hours}$, rounded conservatively up to $9.5\text{ hours}$).
  - **4-Hour BESS:** Requires $\ge 4.8\text{ hours}$ cumulative cheap pricing ($4\text{ hours} \div 0.85\text{ Round-Trip Efficiency} = 4.706\text{ hours}$, rounded conservatively up to $4.8\text{ hours}$).
  - **2-Hour BESS:** Requires $\ge 2.4\text{ hours}$ cumulative cheap pricing ($2\text{ hours} \div 0.85\text{ Round-Trip Efficiency} = 2.353\text{ hours}$, rounded conservatively up to $2.4\text{ hours}$).
- **Primary Metric:** Percentage of days in the analysis period meeting the cumulative window requirements.

### Metric 3 (M3): Fleet Cycling Feedback Loop
M3 (fleet cycling) deferred (requires matched operational asset telemetry not covered in this baseline note).

---

## 3. Market References & Citations
- **Elexon Insights Platform:** Balancing and Settlement Code (BSC), Section T (Settlement Governance).
- **System Pricing Data:** Elexon Open Data Portal (`https://data.elexon.co.uk/bmrs/api/v1/`).
