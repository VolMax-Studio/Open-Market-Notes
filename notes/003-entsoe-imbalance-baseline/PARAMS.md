# VolMax Note #3: ENTSO-E Imbalance Duration Baseline — Frozen Parameters
**Class of Work:** VolMax Descriptive Analytical Note (Not a P10 Audit)
**Status:** Frozen
**Frozen Timestamp:** 2026-07-24T22:15:00+02:00

---

## 1. Scope & Datasets
- **Analysis Period:** 1 June 2025 – 30 June 2026 (13 months).
- **Bidding Zones:** DE-LU (Germany/Luxembourg), FR (France), BE (Belgium), NL (Netherlands).
- **Data Source:** Primary ENTSO-E Transparency Platform (Imbalance prices [17.1.g / 17.2.f]). Selected because it represents the actual financial settlement interval for BESS imbalance arbitrage in European markets. Verified as available for free re-use (CC-BY 4.0).
- **BESS Fleet Subsample:** N/A for baseline pricing duration.

---

## 2. Parameter Definitions

### Metric 1 (M1): Scarcity Pricing Duration
- **Threshold A (Volatility):** 15-minute Imbalance Price $\ge €100/\text{MWh}$.
- **Threshold B (Extreme Scarcity):** 15-minute Imbalance Price $\ge €250/\text{MWh}$.
- **Event Definition:** A continuous sequence of 15-minute intervals meeting the price threshold.
- **Separation Rule:** Events separated by $<30\text{ minutes}$ (less than 2 intervals of 15 minutes) of prices below the threshold are counted as separate events.
- **Metrics Collected:** Histogram of event durations, median, mean, P90, and the maximum single event duration (with date) per Bidding Zone.

### Metric 2 (M2): Charging Window Availability
- **Cheap Energy Threshold:** 15-minute Imbalance Price $\le €25/\text{MWh}$.
- **Accumulation Rule:** Cumulative hours within a single calendar day. Continuous blocks are *not* required.
- **Target Thresholds:**
  - **8-Hour BESS:** Requires $\ge 9.4\text{ hours}$ cumulative cheap pricing (8 hours discharge $\div$ 0.85 Round-Trip Efficiency $\approx$ 9.4 hours charging).
  - **4-Hour BESS:** Requires $\ge 4.7\text{ hours}$ cumulative cheap pricing (4 hours discharge $\div$ 0.85 Round-Trip Efficiency $\approx$ 4.7 hours charging).
- **Primary Metric:** Percentage of days in the analysis period meeting the cumulative window requirements per Zone.

### Metric 3 (M3): Fleet Cycling Feedback Loop
M3 (fleet cycling) deferred (requires matched operational asset telemetry not covered in this baseline note).

---

## 3. Market References & Citations
- **ENTSO-E Transparency Platform:** Regulation (EU) No 543/2013, Article 17.1.g and 17.2.f.
- **Imbalance Pricing:** Represents the settlement price for energy imbalances in the respective bidding zones. Verified as free for re-use without restrictions under CC-BY 4.0 on 2026-07-24.
