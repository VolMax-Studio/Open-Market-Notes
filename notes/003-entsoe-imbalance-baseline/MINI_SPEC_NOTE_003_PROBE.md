# VolMax Open Market Note #003 Probe: Pre-Registration Mini-Spec
> **Scope:** July 2026 Recurrence & European Imbalance Scarcity Probe  
> **Version:** 4.0.0-frozen (Strict Gap-Terminated & Pre-Registered Decision Spec)  
> **Status:** Ratified Pre-Registration Frozen Spec  
> **Repository:** `VolMax-Studio/Open-Market-Notes`  
> **PARAMS Freeze Commitment (`a2c0b3a`):** `feat(note-003): publish final ENTSO-E baseline note with PARAMS v3.1.0 and reproducible figures`  
> **PARAMS Cryptographic SHA-256:** `acc7111a0119f835540689fcffbe7f3333cef9d2b580bc81e8174c2add2c9e58`  
> **Main Branch HEAD (`70b79d0`):** `Merge pull request #54 from VolMax-Studio/docs/recurrence-spec-v1-1-0`  
> **Published Baseline Analysis Script (`run_imbalance_analysis.py`) Blob:** `7e6be06d5b7e7a46223c83998eb4ad35cdb4a16be5245932abce3c827aa5b484`  
> **Remediated Analysis Script (`run_imbalance_analysis.py`) SHA-256:** `2957e2c5905c40228cb74012c791164b0a0b34c6cf22ea578490f1d0b095874e`  
> **Ingestion Script (`download_entsoe_data.py`) SHA-256:** `265d1e722c1f444e1b4041ea1518dd83fc61db5f29efc6f62ac5ff4fecd3b887` (Calibrated 23:45:00 timestamp alignment for exact 15m MTU boundary)  
> **Baseline Provenance Manifest (`data_manifest.json` / `baseline_data_manifest.json`) SHA-256:** `147eef422d0b96d02b3bc5acc630722dbd3a7a8b592ba07c952f147492702346`  
> **Probe Provenance Manifest (`probe_jul2026/data_manifest.json` / `probe_data_manifest.json`) SHA-256:** `613d2d9b17fe4cbda62bf60db6a0aa78122c97607acba4ed48f88ddfa8af2c0f`  
> **Published Baseline Results SHA-256 (`notes_registry.json`):** `b1c713379887043cc429a43d12722939ec70c4ff93f351512970a302478131f9`  
> **Remediated Gap-Terminated Baseline Results SHA-256 (`notes/003-entsoe-imbalance-baseline/results.json`):** `a10c0aae107b52147e98bb269c44a3fac6d9656c7b70af5b398352545a03635c`

---

## Layer 1 / Measured: Baseline & Pre-Registered Metric Alignment

### 1. Parametric Changelog & Continuity Rule Audit
- **Published Zenodo v1.0.0 Baseline (`notes_registry.json`):** Computed via row-adjacency continuity (`b1c713379887043cc429a43d12722939ec70c4ff93f351512970a302478131f9`).
- **Remediated Strict Gap-Terminated Baseline (`a10c0aae...`):** Enforces strict timestamp continuity rule ($\Delta t > 15\text{ min}$ terminates an active block). Documented in `PARAMETRIC_CHANGELOG.md` Entry #002.
- **Verbatim Empirical Audit Findings (59 Total Gaps Across 6 Zones):**
  - Across 19,219 total M1 moderate scarcity events ($\ge €100/\text{MWh}$ across 13 calendar months, 6 zones), 19,212 events ($99.964\%$) contained ZERO internal timestamp gaps.
  - Enforcing strict timestamp gap termination splits exactly **7 bridged events** (8 total gap breaches).
  - **Telemetry Gap & Scarcity Breach Breakdown:**
    - **Dataset Totals:** Across all 6 bidding zones in the 13-month baseline, there are **59 total telemetry gaps** ($\Delta t > 15\text{ min}$): 55 gaps in Denmark (27 in DK_1, 28 in DK_2, episodic with 24 of 27 DK_1 gaps and 22 of 28 DK_2 gaps occurring on 10 August 2025) and 4 gaps in non-Danish zones (1 gap each in AT, BE, FR, NL).
    - **Missing 22:00 UTC MTU Gap (6 gaps total: 5 scarcity breaches, 1 non-scarcity gap):** All 6 zones (AT, BE, DK_1, DK_2, FR, NL) possess an identical 30-minute timestamp gap at `2026-05-31 21:45 UTC` $\rightarrow$ `22:15 UTC` (missing 22:00 UTC Market Time Unit), accounting for 6 total gaps. Cause not established; single-call window acquisition in `download_entsoe_data.py` excludes monthly stitching in analysis code. In FR, price drops to €96.3/MWh after the gap (1 non-scarcity gap); in AT, BE, DK_1, DK_2, and NL, prices remain $\ge €100/\text{MWh}$ across the gap, generating 5 gap breaches across 5 zones.
    - **Danish Telemetry Gap Scarcity Breaches (3 breaches across 2 zones):** Out of 55 total Danish gaps, exactly 3 fall within $\ge €100/\text{MWh}$ scarcity events: 1 breach in DK_1 (`2025-08-10 18:45 UTC` $\rightarrow$ `19:15 UTC`) and 2 separate breaches in DK_2 (`2025-08-10 18:45 UTC` $\rightarrow$ `19:15 UTC` and `19:45 UTC` $\rightarrow$ `20:15 UTC`). In DK_2, both 10 August 2025 gaps occurred within a single ongoing extended scarcity event (Bridged Event #1), while the 31 May 2026 gap occurred in a separate event 10 months later (Bridged Event #2), totaling 3 gap breaches across 2 bridged events in DK_2.
    - **DK_2 Extreme Price Boundary Note (10 Aug 2025):** Imbalance shortage prices in DK_2 reached €803.80/MWh at 16:30 UTC (`curr_p` following the 16:00 $\rightarrow$ 16:30 30m gap) and €4,689.50/MWh at 16:45 UTC (`prev_p` preceding the 16:45 $\rightarrow$ 17:30 45m gap). These prices sit directly on gap boundaries of the 10 August 2025 telemetry gap cluster in Denmark. Prices adjacent to telemetry gaps carry potential boundary artifacts and should be interpreted with operational caution.
    - **Diagnostic vs Analyzer Definition:** The diagnostic script evaluates static price thresholds (`prev_p >= 100 and curr_p >= 100`) across timestamp gaps $\Delta t > 15\text{ min}$, whereas `run_imbalance_analysis.py` (`compute_m1`) evaluates active event block state transitions during timeline iteration. In this 13-month baseline, both methods yield identical counts (8 gap breaches across 7 bridged events).
    - **Scarcity vs Non-Scarcity Totals:** Exactly **8 gaps** fall inside active scarcity events ($\ge €100/\text{MWh}$) across 7 bridged events. The remaining **51 gaps** fall outside scarcity events, distributed as: 25 in DK_1 (27 total - 2 scarcity breaches), 25 in DK_2 (28 total - 3 scarcity breaches), 1 in FR (1 total - 0 scarcity breaches), and 0 in AT, BE, NL (1 total - 1 scarcity breach each).
  - **Metric Impact:** €250 extreme scarcity metrics and daily BESS M2 metrics are 100% unaffected. €100 mean durations shifted by $-0.1\text{ min}$ in BE (76.0m $\rightarrow$ 75.9m) and NL (67.4m $\rightarrow$ 67.3m). Maximum event duration in BE remained exactly 1,545 minutes ($25.75\text{ hours}$).
  - Both `gap_breaches_count` and `bridged_events_count` are recorded explicitly in `results.json` per zone.

### 2. Pre-Registered Metrics & Threshold Definitions
- **Metric M1: Scarcity Duration & Shortage Pricing**
  - Evaluated on Shortage Column (`Short` for Dual Pricing zones, or Single Imbalance Price column).
  - **Threshold A (Moderate Scarcity):** Imbalance Price $\ge €100.00/\text{MWh}$.
  - **Threshold B (Extreme Scarcity):** Imbalance Price $\ge €250.00/\text{MWh}$.
  - **Strict Timestamp Continuity Rule (`Δt > 15 min` Termination):** Imbalance scarcity events are contiguous 15-minute settlement intervals where price remains at or above threshold. A timestamp gap $\Delta t > 15\text{ minutes}$ across adjacent rows terminates the active event block and starts a new event if pricing remains elevated.
- **Metric M2: Grid Surplus Absorption & Daily BESS Opportunity Windows**
  - Evaluated on Surplus Column (`Long` for Dual Pricing zones, or Single Imbalance Price column).
  - **Cheap Surplus Threshold:** Imbalance Price $\le €25.00/\text{MWh}$.
  - **Zero/Negative Surplus Threshold:** Imbalance Price $\le €0.00/\text{MWh}$.
  - **Daily Aggregation & BESS Opportunity Windows (Per Calendar Day):**
    - **4-Hour BESS Window:** Minimum $\ge 4.80\text{ hours}$ per calendar day of surplus pricing. (Note: 85% round-trip efficiency serves as the post-hoc engineering rationale for this daily window and does not alter the frozen 4.8h threshold).
    - **8-Hour BESS Window:** Minimum $\ge 9.50\text{ hours}$ per calendar day of surplus pricing.

### 3. Manifest-Bound Pricing Regime Assignment (Single Source of Truth — Zero Fallbacks)
- **Single Source of Truth:** `run_imbalance_analysis.py` reads `frozen_regime`, `m1_shortage_col`, and `m2_surplus_col` directly from `data_manifest.json`.
- **Parametrized Timeframe Window Tag:** `run_imbalance_analysis.py` accepts `--window-tag` (default `202506_202606`) via `argparse` to match zone manifest entries dynamically per timeframe.
- **Zero Fallback Abort Policy:** If a zone's manifest entry or column metadata is missing, `run_imbalance_analysis.py` raises an immediate `ValueError` abort. Zero silent defaults are permitted.
- **Dual Pricing Zones (NL, FR):** `Short` (shortage) and `Long` (surplus) columns are distinct (`max_diff` = €4,081.59/MWh in NL; €632.20/MWh in FR). M1 is evaluated strictly on `Short` and M2 strictly on `Long` as registered in manifest.
- **Single Pricing Zones (AT, BE, DK_1, DK_2):** `Short` and `Long` columns are empirically verified to be **100% byte-for-byte identical** (`max_diff = 0.000000`, `all_match (<1e-4) = True`). Evaluating M1 or M2 on either column yields mathematically identical values. Manifest binding prevents silent column switching.

### 4. Temporal Windows & Baseline Isolation
- **Baseline Window (Zenodo v1.0.0):** 1 June 2025 – 30 June 2026 (13 Calendar Months / 395 Days).
- **Uncontaminated Baseline Window ($Q_{90}$ Base):** 1 August 2025 – 30 June 2026 (11 Calendar Months / 334 Days).
- **Probe Window:** 1 July 2026 – 31 July 2026 (31 Days / 2,976 expected 15-min settlement intervals per zone).
- **Matched Pair Window:** July 2026 vs July 2025 (same zone, same script, same metric).

### 5. Licensing Boundary Guard & Source Platform
- **Permitted Data Source:** ENTSO-E Primary Transparency Platform (REST API DocumentType `A85`, Imbalance Prices).
- **Forbidden Data Source:** DocumentType `A44` (Day-Ahead Prices) or unverified third-party aggregators.
- **Provenance Manifest Anchor:** `data_manifest.json` contains verbatim entry: `"acquired_at_utc": "2026-07-19T12:00:00Z"`.

### 6. Code-Enforced Mandate 8 & Data Completeness Guard
- **Row Floor:** $\lceil 2,976 \times 0.98 \rceil = \mathbf{2,917\text{ intervals}}$ ($98.0\%$ math ceiling for 31 days).  
  *Operational Extension Note:* The $98\%$ telemetry floor is a Note #003 pre-registration extension pending formal ratification in `RECURRENCE_SPEC`.
- **Timestamp Gap Threshold:** $\le 90\text{ minutes}$.  
  *Post-Hoc Empirical Calibration Note:* Threshold of 90 minutes was calibrated to DK_1/DK_2 historical baseline telemetry gap structure.

### 7. Step 0 Determinism & Output Isolation Protocol
- **Argparse Output Isolation:** Executing `python3 run_imbalance_analysis.py --out-dir probe_jul2026` writes probe analytical outputs to the version-controlled `probe_jul2026/` directory without modifying root baseline files.
- **Probe Telemetry & Baseline Acquisition Requirement:** Probe processed telemetry files (`probe_jul2026/processed/*.feather`, ~324 KB total) are committed directly to the repository to guarantee probe evaluation reproducibility. Full local end-to-end baseline re-evaluation requires running `download_entsoe_data.py` to acquire baseline telemetry (`data/processed/imbalance_{zone}.feather`), which is validated against SHA-256 hashes in `data_manifest.json`.
- **ENTSO-E Data Licensing & Attribution:** Data sourced from ENTSO-E Transparency Platform under Creative Commons Attribution 4.0 International (CC BY 4.0) License.
- **Baseline Integrity Execution:** Executing `python3 run_imbalance_analysis.py --out-dir probe_jul2026` over baseline `.feather` files produced SHA-256 `a10c0aae107b52147e98bb269c44a3fac6d9656c7b70af5b398352545a03635c` under strict timestamp gap termination, matching tracked `notes/003-entsoe-imbalance-baseline/results.json`.

### 8. Verified Target Bidding Zones & Regime Mapping Persistence
- **NL** Netherlands (`10YNL----------L`) — *Frozen DUAL_PRICING*
- **BE** Belgium (`10YBE----------X`) — *Frozen SINGLE_PRICING*
- **FR** France (`10YFR-RTE------C`) — *Frozen DUAL_PRICING*
- **DK_1** Denmark West (`10YDK-1--------W`) — *Frozen SINGLE_PRICING*
- **DK_2** Denmark East (`10YDK-2--------T`) — *Frozen SINGLE_PRICING*
- **AT** Austria (`10YAT-APG------L`) — *Frozen SINGLE_PRICING*  
*Persistence:* Regime mapping parameters (`frozen_regime`, `m1_shortage_col`, `m2_surplus_col`) are persisted into `data_manifest.json` under each zone's file entry.

### 9. Security & Zero Secret Leakage Pipeline (Mandate 9)
- **Token Source:** Environment variable `ENTSOE_API_KEY`.
- **Token Rotation Verification:** Active key prefix vs historical compromised prefix (`RESULT: NO MATCH`).
- **Redaction Order:** `sanitize_token_url()` scrubs `securityToken=[^&]+` parameters on `response.url` and `request.url` *prior* to string formatting.

---

## Layer 2 / Inference / Hypothesis: Cross-Market Comparison Protocol (C1–C5)

### C1. Normalised Scarcity Metric (Currency-Free)
For each market $m$ and zone $z$, let $Q_{90}(z)$ be the 90th percentile of imbalance price over that zone's own uncontaminated baseline (1 Aug 2025 – 30 Jun 2026, 11 months). Define:
$$S(z) = \text{share of settlement TIME in probe month with price} \ge Q_{90}(z)$$
Expressed as share of time (not raw interval counts). No FX conversion is performed anywhere. Absolute EUR thresholds (M1/M2) remain descriptive within EU zones only and carry NO cross-market weight.

### C2. Matched Comparator Pair, Vintage Bias Declaration & GB Sequential Benchmark Audit
July 2026 vs July 2025, same zone, same metric, both computed by the same script.
- **Vintage Bias:** July 2025 data was acquired in July 2026 (recorded at `"acquired_at_utc": "2026-07-19T12:00:00Z"` in manifest); July 2026 data was acquired in August 2026. Potential TSO price revisions between acquisition dates are declared as a known data-vintage bias.
- **Sequential GB Benchmark Audit Record (Measured 2026-08-08 prior to EU probe acquisition):**
  - **GB Uncontaminated Baseline $Q_{90}$ (1 Aug 2025 – 30 Jun 2026):** £131.54 / MWh.
  - **GB Column Verification:** Column `systemSellPrice` is empirically verified to match `systemBuyPrice` (Single Pricing regime P305, `all_match = True`, `max_diff = 0.0000 GBP/MWh`). Evaluated on `systemSellPrice`.
  - **July 2026 GB Scarcity Metric ($S(\text{GB})_{\text{Jul26}}$):** 454.0 hours $\ge £100/\text{MWh}$; share $\ge Q_{90}$ = **28.83%** (429 of 1,488 30-min settlement periods). Since $28.83\% \ge 15.0\%$ ($S_{\text{thresh}}$), GB is empirically **ELEVATED** (Condition 1 of C4 satisfied).
  - **July 2025 GB Comparator Metric ($S(\text{GB})_{\text{Jul25}}$):** 220.0 hours $\ge £100/\text{MWh}$; share $\ge Q_{90}$ = **0.81%** (12 of 1,488 30-min settlement periods).
  - **Audit Lineage Declaration:** GB $S(z)$ metrics were measured and logged on 2026-08-08 prior to ENTSO-E EU probe data acquisition.

### C3. Elevation Threshold (Pre-Registered & Frozen Before Data)
Zone $z$ is "elevated" iff $S(z) \ge \mathbf{15.0\%}$ (1.5x baseline decile).  
*Ratification Record:* Ratified by **Ivan Nestorov** on **2026-08-08** prior to probe data acquisition.

### C4. Decision Rule — Three Outcomes (Pre-Registered & Frozen Before Data)
- **`REGIONAL`**: GB elevated AND $\ge \mathbf{4\text{ of }6}$ EU zones elevated ($N_{\text{high}} = 4$).
- **`GB-SPECIFIC`**: GB elevated AND $\le \mathbf{1\text{ of }6}$ EU zones elevated ($N_{\text{low}} = 1$).
- **`INCONCLUSIVE`**: Every other configuration, including GB not elevated ($N = 2$ or $N = 3$). *INCONCLUSIVE is a first-class outcome and is reported as the finding when it occurs.*  
*Ratification Record:* Ratified by **Ivan Nestorov** on **2026-08-08** prior to probe data acquisition.

### C5. Independence Caveat (Load-Bearing)
The 6 EU zones are NOT independent samples (DK_1/DK_2 share a national system, NL/BE/FR are interconnector-coupled). The count in C4 is a descriptive tally, not a statistical test ($n = 1$ time window).

---

## Layer 3 / Decision (Human-Owned): Gate Status & Frozen Decision Parameters

- **Pre-Registration Decision Ratification:** Ratified by **Ivan Nestorov** on **2026-08-08** (Prior to July 2026 Probe Data Acquisition).
- **Elevation Threshold $S_{\text{thresh}}$ (C3):** `15.0%`
- **INCONCLUSIVE Band Limits ($N_{\text{high}} / N_{\text{low}}$) (C4):** `4 of 6 / 1 of 6`
- **Repository Commit Status:** `FROZEN PRE-REGISTRATION SPEC` on `main`.
