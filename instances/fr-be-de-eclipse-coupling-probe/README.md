# Instance: FR/BE/DE Day-Ahead Eclipse Coupling & Peak Price Probe

**Instance ID:** `instances/fr-be-de-eclipse-coupling-probe`  
**Status:** SPREMNO ZA GEJT  
**Pre-registration Freeze Commit:** `e8d267c`  
**Data Retrieval Date:** 2026-08-30  
**Attribution:** "Source: ENTSO-E Transparency Platform (transparency.entsoe.eu), under CC BY 4.0 license"

---

## 1. Summary of Measurements

This instance evaluates public market claims regarding European Day-Ahead electricity market (SDAC) prices during the 12–13 August 2026 window across France (`FR`), Belgium (`BE`), and Germany-Luxembourg (`DE_LU`).

### Evaluated Hypotheses & Measured Outcomes

| Hypothesis Under Test | Pre-Registered Metric & Scope | Date A: 2026-08-12 (Wednesday - Eclipse) | Date B: 2026-08-13 (Thursday - Text Claim) | Outcome by Frozen Rule |
| :--- | :--- | :--- | :--- | :--- |
| **French Hourly Peak = 338.86 EUR/MWh** | Arithmetic mean of 4 MTUs at delivery hour 20:00 CEST ($|P - 338.86| \le 0.01$) | 289.18 EUR/MWh (diff = 49.68 EUR/MWh) | **338.8625 EUR/MWh** (diff = 0.0025 EUR/MWh) | **PEAK_CONFIRMED on Date B**<br>PEAK_NOT_CONFIRMED on Date A |
| **15-Minute Peak > 400.00 EUR/MWh** | Max 15m MTU price on delivery day | **461.17 EUR/MWh** at 19:45 CEST | **487.38 EUR/MWh** at 19:45 CEST | **SPIKE_CONFIRMED on both dates** |
| **Tri-Zone Price Coupling Equality** | $\max(\Delta P) \le 0.01\text{ EUR/MWh}$ in evening window (18:00–22:00 CEST, 16 MTUs) | **10 / 16 MTUs COUPLED_EXACT**<br>6 / 16 MTUs DIVERGED (max gap = 42.77 EUR/MWh) | **12 / 16 MTUs COUPLED_EXACT**<br>4 / 16 MTUs DIVERGED (max gap = 50.77 EUR/MWh) | **DIVERGED during peak intervals** |

---

## 2. Empirical Findings (L1 Measurements)

1. **Date Alignment and Price Accuracy:**
   - The viral post stated: *"338,86 EUR/MWh — tyle wyniosła cena godzinowa day-ahead (ENTSO-E) we Francji dla dostawy o 20:00 w środę 13 sierpnia"*.
   - In calendar year 2026, **Wednesday was 12 August** (the day of the solar eclipse) and **Thursday was 13 August**.
   - The literal price of **338.86 EUR/MWh** occurred on **Thursday 13 August 2026** ($P_{\text{hourly}} = (414.96 + 371.94 + 300.14 + 268.41) / 4 = 338.8625\text{ EUR/MWh}$).
   - On Wednesday 12 August, the 20:00 CEST hourly price was **289.18 EUR/MWh**, while the daily maximum hourly price reached **300.00 EUR/MWh** at 19:00 CEST (matching the post's claim of rising *"do 300 EUR/MWh dla dostawy 12 sierpnia"*).
   - Thus, the price levels cited in the post accurately match ENTSO-E Day-Ahead auction clearing data, but were attributed to a calendar date/day combination that does not exist.

2. **15-Minute Peak Succeeded the Eclipse Window:**
   - The highest 15-minute price across both days occurred on **Thursday 13 August at 19:45 CEST (487.38 EUR/MWh)**, which exceeded the peak on the day of the solar eclipse (**461.17 EUR/MWh on Wednesday 12 August at 19:45 CEST**) in the exact same minute of the day.

3. **Evening Market Coupling Divergence:**
   - On 12 August, tri-zone prices diverged in 6 of 16 evening MTUs, reaching a maximum price spread of **42.77 EUR/MWh** at 20:15 CEST (`FR`: 272.05, `BE`: 297.17, `DE_LU`: 314.82).
   - On 13 August, tri-zone prices diverged in 4 of 16 evening MTUs, reaching a maximum price spread of **50.77 EUR/MWh** at 19:30 CEST (`FR`/`BE`: 327.17 vs `DE_LU`: 276.40).
   - While prices were identical ($\le 0.01\text{ EUR/MWh}$) for the majority of intervals, prices diverged during the peak ramp intervals.

---

## 3. Data Manifest & Raw Response Checksums

| Target Window | Zone | Records | SHA-256 Checksum of Raw API Response |
| :--- | :---: | :---: | :--- |
| `Date_A_2026-08-12` | `FR` | 96 | `34d7b76b6ed872539aa9bbedcf65ccf352c11f283e911759d6f952ba586addce` |
| `Date_A_2026-08-12` | `BE` | 96 | `3872c3b24a6ee9d6afb59550c32b00882968480ef89e91a8e1d578f6f01f6c9e` |
| `Date_A_2026-08-12` | `DE_LU` | 96 | `d22d0887ac1d6ef779b6d50e061ffc622ae48b81296c98c74fd85dff7d9a0f57` |
| `Date_B_2026-08-13` | `FR` | 96 | `a5676c9a665b68d296d033c85364211bf7a645d81c5ea3a464cb60871be6f9bb` |
| `Date_B_2026-08-13` | `BE` | 96 | `2b0aae784318623df46ecdc6cf7b30334eb7bf5199d95aebdf5c8cef6e60a662` |
| `Date_B_2026-08-13` | `DE_LU` | 96 | `7fa632423d091a5dd8384dea8234c57f33906f9657f5d6eb8c39eb858dc71a74` |

---

## 4. Deterministic Recreation Verification

```bash
mv instances/fr-be-de-eclipse-coupling-probe/results.json instances/fr-be-de-eclipse-coupling-probe/results.json.bak
python3 instances/fr-be-de-eclipse-coupling-probe/src/run_audit.py
sha256sum instances/fr-be-de-eclipse-coupling-probe/results.json instances/fr-be-de-eclipse-coupling-probe/results.json.bak
diff -u instances/fr-be-de-eclipse-coupling-probe/results.json instances/fr-be-de-eclipse-coupling-probe/results.json.bak
```
