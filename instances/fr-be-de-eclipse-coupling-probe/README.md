# Instance: FR/BE/DE Day-Ahead Eclipse Coupling & Peak Price Probe

**Instance ID:** `instances/fr-be-de-eclipse-coupling-probe`  
**Status:** SPREMNO ZA GEJT  
**Pre-registration Freeze Commit:** `e8d267c`  
**Data Retrieval Date:** 2026-08-30  
**Attribution:** "Source: ENTSO-E Transparency Platform (transparency.entsoe.eu), under CC BY 4.0 license"

---

## 1. Summary of Measurements

This instance evaluates public market claims regarding European Day-Ahead electricity market (SDAC) prices during the 12–13 August 2026 window across France (`FR`), Belgium (`BE`), and Germany-Luxembourg (`DE_LU`).

### Target Set and Evaluated Hypotheses

* **Input Data Points:** 576 retrieved 15-minute price records (96 MTUs $\times$ 2 dates $\times$ 3 zones).
* **Evaluated Lookups:** 32 tri-zone evening MTU coupling evaluations (16 MTUs $\times$ 2 dates).
* **Aggregate Outcome:** 22 / 32 COUPLED_EXACT, 10 / 32 DIVERGED.

| Hypothesis Under Test | Pre-Registered Metric & Scope | Date A: 2026-08-12 (Wednesday - Eclipse) | Date B: 2026-08-13 (Thursday - Text Claim) | Outcome by Frozen Rule |
| :--- | :--- | :--- | :--- | :--- |
| **French Hourly Peak = 338.86 EUR/MWh** | Arithmetic mean of 4 MTUs at delivery hour 20:00 CEST ($|P - 338.86| \le 0.01$) | 289.18 EUR/MWh (diff = 49.68 EUR/MWh) | **338.8625 EUR/MWh** (diff = 0.0025 EUR/MWh) | PEAK_NOT_CONFIRMED on Date A; **PEAK_CONFIRMED on Date B** |
| **15-Minute Peak > 400.00 EUR/MWh** | Max 15m MTU price on delivery day | **461.17 EUR/MWh** at 19:45 CEST | **487.38 EUR/MWh** at 19:45 CEST | **SPIKE_CONFIRMED on both dates** |
| **Tri-Zone Price Coupling Equality** | $\max(\Delta P) \le 0.01\text{ EUR/MWh}$ in evening window (18:00–22:00 CEST, 16 MTUs) | **10 / 16 MTUs COUPLED_EXACT**; 6 / 16 MTUs DIVERGED (max gap = 42.77 EUR/MWh) | **12 / 16 MTUs COUPLED_EXACT**; 4 / 16 MTUs DIVERGED (max gap = 50.77 EUR/MWh) | Na oba datuma najviši 15-minutni MTU bio je COUPLED_EXACT; svi izmereni razlazi pali su na intervale niže od dnevnog vrha. |

---

## 2. Empirical Findings (L1 Measurements)

1. **Date Alignment and Price Accuracy for Tested Claims:**
   - The viral post stated: *"338,86 EUR/MWh — tyle wyniosła cena godzinowa day-ahead (ENTSO-E) we Francji dla dostawy o 20:00 w środę 13 sierpnia"*.
   - In calendar year 2026, **Wednesday was 12 August** (the day of the solar eclipse) and **Thursday was 13 August**.
   - The literal price of **338.86 EUR/MWh** occurred on **Thursday 13 August 2026** ($P_{\text{hourly}} = (414.96 + 371.94 + 300.14 + 268.41) / 4 = 338.8625\text{ EUR/MWh}$).
   - On Wednesday 12 August, the 20:00 CEST hourly price was **289.18 EUR/MWh**, while the daily maximum hourly price reached **300.00 EUR/MWh** at 19:00 CEST (matching the post's claim of rising *"do 300 EUR/MWh dla dostawy 12 sierpnia"*).
   - Thus, the tested price levels cited in the post (338.86 EUR/MWh and >400 EUR/MWh 15m spike) accurately match ENTSO-E Day-Ahead auction clearing data, but were attributed to a calendar date/day combination that does not exist.

2. **15-Minute Peak Timing:**
   - The highest 15-minute price across both days occurred on **Thursday 13 August at 19:45 CEST (487.38 EUR/MWh)**, which exceeded the peak on the day of the solar eclipse (**461.17 EUR/MWh on Wednesday 12 August at 19:45 CEST**) in the exact same minute of the day.

3. **Evening Market Coupling Divergence:**
   - On 12 August, tri-zone prices diverged in 6 of 16 evening MTUs, reaching a maximum price spread of **42.77 EUR/MWh** at 20:15 CEST (`FR`: 272.05, `BE`: 297.17, `DE_LU`: 314.82).
   - On 13 August, tri-zone prices diverged in 4 of 16 evening MTUs, reaching a maximum price spread of **50.77 EUR/MWh** at 19:30 CEST (`FR`/`BE`: 327.17 vs `DE_LU`: 276.40).
   - Na oba datuma najviši 15-minutni MTU bio je COUPLED_EXACT; svi izmereni razlazi pali su na intervale niže od dnevnog vrha.

---

## 3. Data Governance & Artifact Tracking Decisions

- **Derived Audit Table:** `data/coupling_lookups.csv` is an evaluated, derived 32-row tabular dataset under CC BY 4.0 (attribution: "Source: ENTSO-E Transparency Platform (transparency.entsoe.eu), under CC BY 4.0 license"). Because it is a structured audit evaluation artifact rather than raw bulky XML/telemetry payloads, it is tracked directly in git.
- **Exploratory Network Calibration:** During runner resilience calibration for transient ENTSO-E 503/ReadTimeout responses, isolated requests were tested to establish request timeout bounds (fixed at 45s with explicit connection closure). All definitive telemetry is parsed and emitted strictly through `src/run_audit.py`.

---

## 4. Data Manifest & Raw Response Checksums

| Target Window | Zone | Records | SHA-256 Checksum of Raw API Response |
| :--- | :---: | :---: | :--- |
| `Date_A_2026-08-12` | `FR` | 96 | `514a06c93ff848356d4375f8d0796fb1120dddc1a0b920e6d37c56fee3dbbb52` |
| `Date_A_2026-08-12` | `BE` | 96 | `c327e22e73bcb389a652a91e850e68d1f33f8593ab5bdca33afffd56dd6bcb15` |
| `Date_A_2026-08-12` | `DE_LU` | 96 | `79ac02e5d7661693735c5fe22bbbe054a92eb65e991a27228e5d924ebe8bfa67` |
| `Date_B_2026-08-13` | `FR` | 96 | `a7c93d856abacf08a004f657ebda8b98a4dd1f19e7f642611bae7aea0a53e820` |
| `Date_B_2026-08-13` | `BE` | 96 | `3f97550d47098cb5f65bbfca405f6725a5def1479feb8f673e3ee21b9e8c039a` |
| `Date_B_2026-08-13` | `DE_LU` | 96 | `dfaa09939de084af4bb369ab0044a5fbb09e122634f847d05cf3e89c10e6f0c4` |

---

## 5. Deterministic Recreation Verification

```bash
mv instances/fr-be-de-eclipse-coupling-probe/results.json instances/fr-be-de-eclipse-coupling-probe/results.json.bak
python3 instances/fr-be-de-eclipse-coupling-probe/src/run_audit.py
sha256sum instances/fr-be-de-eclipse-coupling-probe/results.json instances/fr-be-de-eclipse-coupling-probe/results.json.bak
diff -u instances/fr-be-de-eclipse-coupling-probe/results.json instances/fr-be-de-eclipse-coupling-probe/results.json.bak; echo "exit=$?"
```
