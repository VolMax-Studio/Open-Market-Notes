# VolMax Note #2: ERCOT Duration Baseline — Frozen Parameters
**Class of Work:** VolMax Descriptive Analytical Note (Not a P10 Audit)
**Status:** Frozen
**Frozen Timestamp:** 2026-07-19T10:10:00+02:00

---

## 1. Scope & Datasets
- **Analysis Period:** 1 June 2025 – 30 June 2026 (13 months).
- **Hubs (Pricing Nodes):** 
  - `HB_WEST` (West Hub - high wind penetration)
  - `HB_NORTH` (North Hub - high industrial/load center)
  - `HB_SOUTH` (South Hub)
  - `HB_HOUSTON` (Houston Hub - high coastal load)
- **Data Source:** Primary ERCOT 15-minute Real-Time Settlement Point Prices (SPP) for the specified Hubs. 15-minute SPP is selected because it represents the actual financial settlement interval for BESS energy arbitrage in the ERCOT market.
- **BESS Fleet Subsample:** All operational BESS assets from the active ERCOT audit files (including esVolta Anole and Bat Cave).

---

## 2. Parameter Definitions

### Metric 1 (M1): Scarcity Pricing Duration
Due to the different market design of ERCOT compared to the NEM, we define two levels of price spikes to capture volatility and extreme scarcity:
- **Threshold A (Volatility):** 15-minute SPP $\ge \$100/\text{MWh}$.
- **Threshold B (Extreme Scarcity):** 15-minute SPP $\ge \$250/\text{MWh}$ (indicates peaking conditions or ORDC price adder activation).
- **Event Definition:** A continuous sequence of 15-minute intervals meeting the price threshold.
- **Separation Rule:** Events separated by $<30\text{ minutes}$ (less than 2 intervals of 15 minutes) of prices below the threshold are counted as separate events.
- **Metrics Collected:** Histogram of event durations, median, mean, P90, and the maximum single event duration (with date) per Hub.

### Metric 2 (M2): Charging Window Availability
ERCOT's West Hub frequently sees low, zero, or negative pricing due to wind curtailment, while load hubs experience different profiles.
- **Cheap Energy Threshold:** 15-minute SPP $\le \$25/\text{MWh}$ (reflects economically viable charging price boundaries).
- **Accumulation Rule:** Cumulative hours within a single calendar day (00:00 to 00:00 Central Time). Continuous blocks are *not* required.
- **Target Thresholds:**
  - **8-Hour BESS:** Requires $\ge 9.4\text{ hours}$ cumulative cheap pricing (8 hours discharge $\div$ 0.85 Round-Trip Efficiency $\approx$ 9.4 hours charging).
  - **4-Hour BESS:** Requires $\ge 4.7\text{ hours}$ cumulative cheap pricing (4 hours discharge $\div$ 0.85 Round-Trip Efficiency $\approx$ 4.7 hours charging).
- **Primary Metric:** Percentage of days in the analysis period meeting the cumulative window requirements per Hub.

### Metric 3 (M3): Fleet Cycling Feedback Loop
M3 (fleet cycling) deferred — current ERCOT holdings (60 days, 2 units) cannot support a 13-month fleet analysis; will be added when a longer holding exists.

---

## 3. Market References & Citations
- **Settlement Point Price (SPP) Calculations:** ERCOT Nodal Protocols Section 2, Definitions and Acronyms, and Section 6.6, Settlement Calculations for the Real-Time Energy Operations.
- **15-Minute Settlement Intervals:** Real-Time Settlement Interval is 15 minutes as defined in ERCOT Nodal Protocols Section 2, Definitions and Acronyms.
- **Price Volatility Thresholds:** The $100/\text{MWh}$ and $250/\text{MWh}$ thresholds are selected as benchmarks for operational price volatility. $100/\text{MWh}$ represents the typical threshold for gas/peaker economic dispatch activation, and $250/\text{MWh}$ represents peaking or extreme scarcity conditions (e.g. activation of ORDC price adders under ERCOT Nodal Protocols Section 6.5.7.3, Security Constrained Economic Dispatch).
- **Cheap Charging Energy Threshold:** The $25/\text{MWh}$ threshold represents low-cost wind and solar charging opportunities, which are frequently driven by negative or near-zero pricing regimes in the West Hub (HB_WEST) (governed by Energy Offer Curves under ERCOT Nodal Protocols Section 4.4.9, Energy Offers and Bids).

---

## 4. Implementation Deviation Report (2026-07-19)
- **Data Access Path:** The primary ERCOT MIS direct download (Path 1) returned HTTP 403 Forbidden due to WAF geoblocking of the local residential IP, and the configured proxy was inactive.
- **Realized Path:** Executed Path 2 (GridStatus API fallback). Consequently, the note is classified as **Evidence Class B** (Third-Party API Ingestion), matching the Bat Cave audit protocol.
- **Redistribution Decision:** To comply with GridStatus Terms of Use, the raw 15-minute SPP dataset is not committed to the public repository. Instead, it is hosted in a private repository for independent GHA execution, with public verification restricted to SHA-256 hashes inside `data_manifest.json`.




