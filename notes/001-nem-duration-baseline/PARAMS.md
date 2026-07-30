# VolMax Note #1: NEM Duration Baseline — Frozen Parameters
**Class of Work:** VolMax Descriptive Analytical Note (Not a P10 Audit)
**Status:** Frozen (Committed prior to running calculations)
**Frozen Timestamp:** 2026-07-18T19:49:00+02:00

---

## 1. Scope & Datasets
- **Analysis Period:** 1 June 2025 – 30 June 2026 (13 months).
- **Regions:** NSW1, QLD1, SA1, VIC1 (Mainland NEM).
- **Data Source:** Primary AEMO 5-minute dispatch interval data (NEMWEB DISPATCHPRICE).
- **BESS Fleet Subsample:** 16 accepted BESS units from the active NEM dispatch audit repository.

### BESS Energy Capacity Denominator Table & Source Attribution
*Nameplate energy capacities (MWh) verified against the official AEMO National Electricity Market Registration and Exemption List (published 15 May 2026):*

| DUID | Asset Name | Registered Energy Capacity (MWh) | Registered Power Capacity (MW) | Subsample Status |
|:---|:---|:---:|:---:|:---:|
| **HPR1** | Hornsdale Power Reserve | 193.5 | 150.0 | Accepted Established |
| **VBB1** | Victorian Big Battery | 450.0 | 300.0 | Accepted Established |
| **WANDB1** | Wandoan South BESS | 150.0 | 100.0 | Accepted Established |
| **WDBESS1** | Western Downs BESS | 540.0 | 270.0 | Accepted Established |
| **TIB1** | Torrens Island BESS | 250.0 | 250.0 | Accepted Established |
| **HBESS1** | Hazelwood BESS | 150.0 | 150.0 | Accepted Established |
| **RANGEB1** | Rangebank BESS | 260.0 | 200.0 | Accepted Established |
| **CHBESS1** | Chinchilla BESS | 200.0 | 100.0 | Accepted Established |
| **BLYTHB1** | Blyth BESS | 477.0 | 200.0 | Accepted Established |
| **BHB1** | Broken Hill BESS | 50.0 | 50.0 | Accepted Established |
| **BBATTERY1** | Bouldercombe BESS | 100.0 | 50.0 | Accepted Established |
| **ULPBESS1** | Ulinda Park BESS | 298.0 | 149.0 | Accepted Commissioning |
| **WALGRV1** | Wallgrove Grid Battery | 75.0 | 50.0 | Accepted Established |
| **RESS1** | Riverina BESS 1 | 120.0 | 60.0 | Accepted Established |
| **RIVNB2** | Riverina BESS 2 | 130.0 | 65.0 | Accepted Established |
| **CAPBES1** | Capital BESS | 200.0 | 100.0 | Accepted Established |

### Uniform Fleet Inclusion & Exclusion Criteria
1. **Registered Power Threshold:** Utility-scale grid-connected BESS assets with registered power capacity $\ge 50\text{ MW}$.
2. **Established Operational Status:** Assets with commercial registration prior to the analysis start date (`2025-06-01`).
3. **Mid-Window Initial Commissioning Exclusion:** Assets entering registration or initial testing mid-window without complete prior operational history (e.g. `TARBESS1`, `TEMPB1`) are excluded from the baseline cohort to prevent denominator/throughput skew.
4. **Commissioning Nuance Handling:** Units registered prior to the window but undergoing commercial ramp-up in Month 1 (e.g. `ULPBESS1` at 0.74 EFC in June 2025) are retained in the 16-unit aggregate metric for conservative lower-bound estimation, but excluded from established per-unit median comparisons in analytical observations.

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
