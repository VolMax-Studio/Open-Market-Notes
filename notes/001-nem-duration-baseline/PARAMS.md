# VolMax Note #1: NEM Duration Baseline — Frozen Parameters
**Class of Work:** VolMax Descriptive Analytical Note (Not a P10 Audit)
**Status:** Frozen (Committed prior to running calculations)
**Frozen Timestamp:** 2026-07-18T19:49:00+02:00

---

## 1. Scope & Datasets
- **Analysis Period:** 1 June 2025 – 30 June 2026 (13 months).
- **Regions:** NSW1, QLD1, SA1, VIC1 (Mainland NEM).
- **Data Source:** Primary AEMO 5-minute dispatch interval data (NEMWEB DISPATCHPRICE).
- **BESS Fleet Subsample:** 16 BESS units from the active NEM dispatch audit repository.

---

## 2. Parameter Definitions

### Metric 1 (M1): Scarcity Pricing Duration
- **High-Price Threshold:** 5-minute Regional Reference Price (RRP) $\ge \$300/\text{MWh}$.
- **Event Definition:** A continuous sequence of 5-minute dispatch intervals meeting the price threshold.
- **Separation Rule:** Events separated by $<30\text{ minutes}$ (less than 6 intervals) of prices below $\$300/\text{MWh}$ are counted as separate events (no merging/smoothing).
- **Metrics Collected:** Histogram of event durations, median, mean, P90, and the maximum single event duration (with date) per region.

### Metric 2 (M2): Charging Window Availability
- **Cheap Energy Threshold:** 5-minute RRP $\le \$50/\text{MWh}$.
- **Accumulation Rule:** Cumulative hours within a single trading day (04:00 to 04:00 AEST). Continuous blocks are *not* required (inverters can segment charging).
- **Target Thresholds:**
  - **8-Hour BESS:** Requires $\ge 9.4\text{ hours}$ cumulative cheap pricing (8 hours discharge $\div$ 0.85 Round-Trip Efficiency $\approx$ 9.4 hours charging).
  - **4-Hour BESS:** Requires $\ge 4.7\text{ hours}$ cumulative cheap pricing (4 hours discharge $\div$ 0.85 Round-Trip Efficiency $\approx$ 4.7 hours charging).
- **Primary Metric:** Percentage of days in the analysis period meeting the cumulative window requirements per region.

### Metric 3 (M3): Fleet Cycling Feedback Loop
- **Data Source:** Equivalent Full Cycles (EFC) per month per asset from the existing NEM dispatch audit dataset.
- **Stratification Groups:**
  - Short-to-Medium Duration: $\le 2\text{ hours}$ registered capacity duration.
  - Long Duration: $\ge 4\text{ hours}$ registered capacity duration.
- **Analysis:** Compare monthly EFC trends between the two groups.
- **Constraint:** Descriptive monthly plot only. No OLS trends or forecasting will be calculated, as 13 months is insufficient to separate seasonality from structural fleet changes.
