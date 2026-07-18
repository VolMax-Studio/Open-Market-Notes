# VolMax Note #2: ERCOT Duration Baseline — Frozen Parameters
**Class of Work:** VolMax Descriptive Analytical Note (Not a P10 Audit)
**Status:** Frozen (Committed prior to running calculations)
**Frozen Timestamp:** 2026-07-18T20:10:00+02:00

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
- **Data Source:** Monthly Equivalent Full Cycles (EFC) from the ERCOT BESS audit datasets.
- **Stratification Groups:**
  - Short-to-Medium Duration: $\le 2\text{ hours}$ registered capacity duration (e.g., Bat Cave 1h, Anole 2h).
  - Long Duration: $\ge 4\text{ hours}$ registered capacity duration (if any operational assets exist in the database for the period).
- **Analysis:** Compare monthly EFC trends between groups. If no long-duration assets are operational, the baseline will record only the short-to-medium duration baseline to serve as the pre-transition reference.
