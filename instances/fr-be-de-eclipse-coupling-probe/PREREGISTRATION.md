# PRE-REGISTRATION — FR/BE/DE Day-Ahead Eclipse Coupling & Peak Price Probe
Status: FROZEN / PRE-DATA
Frozen: see git log for this file (freeze point is the commit introducing this document before data acquisition)

## 0. Licence (L0)

Source: ENTSO-E Transparency Platform (Day-Ahead Prices)
Terms URL: https://transparency.entsoe.eu/content/static_content/Static%20content/terms%20and%20conditions/terms%20and%20conditions.html
Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)
Accessed: 2026-08-30
Attribution string to carry: "Source: ENTSO-E Transparency Platform (transparency.entsoe.eu), under CC BY 4.0 license"
Compatible with Note public repository: yes

## 1. Source mapping & Target Zones

Target Item / Concept: Day-Ahead Market (SDAC) Prices during the August 2026 Solar Eclipse and Gravelines Nuclear Outage Window
  → Source Dataset: Day-Ahead Prices (`query_day_ahead_prices`, DocumentType A44)
  → Target Field: `price` (Price in EUR/MWh)

Target Bidding Zones:
1. France (`FR`, EIC: `10YFR-RTE------C`)
2. Belgium (`BE`, EIC: `10YBE----------2`)
3. Germany-Luxembourg (`DE_LU`, EIC: `10Y1001A1001A82H`)

Endpoint: `https://web-api.tp.entsoe.eu/api`

Record schema:
- `timestamp`: UTC interval start timestamp (ISO 8601)
- `price`: Numeric value in EUR/MWh

Resolution:
- PT15M (15-minute intervals, 96 intervals per delivery day, post-SDAC 15-minute go-live in October 2025).

## 2. Interval identity

Key: (`timestamp_utc`, `bidding_zone`)
- Timezone convention: Strict UTC query and interval boundary matching (converted to CEST Europe/Paris / Europe/Brussels / Europe/Berlin for market delivery hour alignment).
- Boundary convention: Interval-beginning timestamp (left-closed).

Candidate Test Dates (Evaluating Dual Claims):
- **Date A (Solar Eclipse Actual Day):** `2026-08-12` (Wednesday) — UTC delivery range `2026-08-11 22:00:00+00:00` to `2026-08-12 22:00:00+00:00` (96 MTUs).
- **Date B (Literal Text Claim Day):** `2026-08-13` (Thursday) — UTC delivery range `2026-08-12 22:00:00+00:00` to `2026-08-13 22:00:00+00:00` (96 MTUs).

Resolution & Aggregation Convention:
- All queries pull 15-minute resolution data (PT15M).
- Hourly Equivalent Price $P_{\text{hourly}}(h)$ is computed as the strict arithmetic mean of the four 15-minute MTUs within delivery hour $h$:
  $$P_{\text{hourly}}(h) = \frac{1}{4} \sum_{i=1}^4 P_{15m}(h, i)$$

Target Sub-Windows:
1. **Evening Window (Peak Stress & Coupling Window):** 18:00 to 22:00 CEST (16:00 to 20:00 UTC) = 16 consecutive 15-minute MTUs per date per zone.
2. **Delivery Hour 20:00 CEST (18:00 to 19:00 UTC):** 4 MTUs (`20:00`, `20:15`, `20:30`, `20:45` CEST).

## 3. Target set

Exact bounded list of lookups under test:
- **Total MTU Intervals:** 96 MTUs/day $\times$ 2 dates $\times$ 3 zones = **576 price lookups**.
- **Coupling Evaluations:** 16 evening MTUs/day $\times$ 2 dates = **32 tri-zone coupling evaluations**.

Out-of-scope items:
- Intraday (continuous or auctions) prices and volumes.
- Physical cross-border grid flow measurements and line capacity ratings.
- Dates outside 2026-08-12 and 2026-08-13.

## 4. Decision rules — per lookup and per hypothesis

### Hypothesis 1: Exact Price Coupling Across FR, BE, and DE_LU in Evening Window
- For each evening MTU $t \in [18:00, 22:00\text{ CEST})$:
  $$\Delta P_{\max}(t) = \max(|P_{FR}(t) - P_{BE}(t)|, |P_{FR}(t) - P_{DE\_LU}(t)|, |P_{BE}(t) - P_{DE\_LU}(t)|)$$

| Condition | Verdict |
| :--- | :--- |
| $\Delta P_{\max}(t) \le 0.01\text{ EUR/MWh}$ | **COUPLED_EXACT** |
| $\Delta P_{\max}(t) > 0.01\text{ EUR/MWh}$ | **DIVERGED** |

### Hypothesis 2: French Hourly Peak Price = 338.86 EUR/MWh at Delivery Hour 20:00 CEST

| Condition | Verdict |
| :--- | :--- |
| $|P_{\text{hourly, FR}}(20:00\text{ CEST}) - 338.86| \le 0.01\text{ EUR/MWh}$ | **PEAK_CONFIRMED** |
| $|P_{\text{hourly, FR}}(20:00\text{ CEST}) - 338.86| > 0.01\text{ EUR/MWh}$ | **PEAK_NOT_CONFIRMED** |

### Hypothesis 3: 15-Minute Peak Price Exceeds 400.00 EUR/MWh

| Condition | Verdict |
| :--- | :--- |
| $\max_{t \in \text{Day}} P_{15m, FR}(t) > 400.00\text{ EUR/MWh}$ | **SPIKE_CONFIRMED** |
| $\max_{t \in \text{Day}} P_{15m, FR}(t) \le 400.00\text{ EUR/MWh}$ | **SPIKE_NOT_CONFIRMED** |

## 5. Frozen non-goals

1. No meteorological modeling or estimation of solar irradiance loss during the eclipse.
2. No causal attribution of price formation to individual generation units (e.g. Gravelines nuclear reactors), river temperatures, or cooling water constraints.
3. No physical transmission congestion modeling (only pure price equality/divergence is measured; physical causality is out of scope).
4. No assessment of private OTC or continuous intraday market spreads.

## 6. Termination

The probe terminates when all 576 lookups across both dates (2026-08-12 and 2026-08-13) and all 3 zones are retrieved and evaluated against the decision rules in §4.
No metric or decision threshold may be altered after data retrieval.
