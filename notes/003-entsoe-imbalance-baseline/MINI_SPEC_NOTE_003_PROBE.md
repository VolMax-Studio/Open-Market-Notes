# VolMax Open Market Note #003 Probe: Pre-Registration Mini-Spec
> **Scope:** July 2026 Recurrence & European Imbalance Scarcity Probe  
> **Version:** 1.7.0-draft (Remediated Pre-Registration Draft)  
> **Status:** Draft Submitted to Human Gate on `feature/omn-003-preregistration-draft` (Pre-Execution Freeze)  
> **Repository:** `VolMax-Studio/Open-Market-Notes`  
> **PARAMS Freeze Commitment:** `a2c0b3a` (*Baseline cryptographically fixed, committed alongside reproducible figures*)  
> **PARAMS Cryptographic SHA-256:** `acc7111a0119f835540689fcffbe7f3333cef9d2b580bc81e8174c2add2c9e58`  
> **Pipeline Analysis Script (`run_imbalance_analysis.py`) Blob SHA-256 (`6fa1cb7`):** `7e6be06d5b7e7a46223c83998eb4ad35cdb4a16be5245932abce3c827aa5b484`  
> **Ingestion Script (`download_entsoe_data.py`) Draft SHA-256:** `7b78d1f10a27e480f3e5013a10442df4cdf5b131462b21d0fccce6b61607d64b`  
> **Baseline Results SHA-256 (`notes_registry.json`):** `b1c713379887043cc429a43d12722939ec70c4ff93f351512970a302478131f9`

---

## Layer 1 / Measured: Verified Code-Enforced Protocol & Baseline Measurements

### 1. Ingestion Safety & Baseline Overwrite Protection (Remediated — B2, B3, B7)
- **Feather Contract & Overwrite Guard:** Telemetry files in `proc_dir` maintain standard naming `imbalance_{ZONE}.feather`. To prevent accidental overwriting of published baseline files, `download_entsoe_data.py` raises `ValueError` if `imbalance_{ZONE}.feather` already exists, unless `--allow-overwrite` is explicitly passed or an isolated `--out-dir` is specified.
- **Manifest Provenance Integrity:** `update_manifest()` validates and updates provenance entries within the `"files"` JSON array structure in `data_manifest.json`.

### 2. Measured Target Bidding Zones & Regime Mapping Persistence (Remediated — B4, B7, B8)
- **NL** Netherlands (`10YNL----------L`) — *Frozen DUAL_PRICING*
- **BE** Belgium (`10YBE----------X`) — *Frozen SINGLE_PRICING*
- **FR** France (`10YFR-RTE------C`) — *Frozen DUAL_PRICING*
- **DK_1** Denmark West (`10YDK-1--------W`) — *Frozen SINGLE_PRICING*
- **DK_2** Denmark East (`10YDK-2--------T`) — *Frozen SINGLE_PRICING*
- **AT** Austria (`10YAT-APG------L`) — *Frozen SINGLE_PRICING*  
*Persistence:* Regime mapping parameters (`frozen_regime`, `m1_shortage_col`, `m2_surplus_col`) are persisted into `data_manifest.json` under each zone's file entry.

### 3. Security & Zero Secret Leakage Pipeline (Remediated — B1, B5)
- **Token Source:** Passed strictly via environment variable `ENTSOE_API_KEY`.
- **Token Rotation Verification:** Active key prefix checked against historical compromised key prefix (`RESULT: NO MATCH` verified).
- **Redaction Order:** `sanitize_token_url()` scrubs `securityToken=[^&]+` parameters on `response.url` and `request.url` *prior* to string concatenation.

### 4. Verified Mandate 8 Telemetry Completeness & Timestamp Gap Measurements (Remediated — B2, B3, B6)
- **Timestamp Parsing:** Timestamps are parsed using `pd.to_datetime(df.index, utc=True)` to prevent object index misinterpretation.
- **Measured Gap Calibration:** Measured timestamp gaps across baseline cache:
  - `BE`, `NL`, `AT`, `FR`: Maximum gap = `00:30:00` (30 minutes).
  - `DK_1`, `DK_2`: Maximum gap = `01:30:00` (90 minutes / 1.5 hours).
- **Code Enforcement:** `check_mandate8_completeness()` enforces a row count floor of $\lceil 2,976 \times 0.98 \rceil = \mathbf{2,917\text{ intervals}}$ ($98.0\%$ ceiling for 31 days) and a maximum timestamp gap threshold of $\le 90\text{ minutes}$.

---

## Layer 2 / Inference / Hypothesis: Cross-Market Comparison Protocol (C1–C5)

### C1. Normalised Scarcity Metric (Currency-Free)
For each market $m$ and zone $z$, let $Q_{90}(z)$ be the 90th percentile of imbalance price over that zone's own uncontaminated baseline (1 Aug 2025 – 30 Jun 2026, 11 months). Define:
$$S(z) = \text{share of settlement TIME in probe month with price} \ge Q_{90}(z)$$
Expressed as share of time (not raw interval counts). No FX conversion is performed anywhere. Absolute EUR thresholds (M1/M2) remain descriptive within EU zones only and carry NO cross-market weight.

### C2. Matched Comparator Pair & Vintage Bias Declaration
July 2026 vs July 2025, same zone, same metric, both computed by the same script. GB is recomputed on the matched July/July pair after Elexon HTTP retry logic is landed.  
*Vintage Bias:* July 2025 data was acquired in July 2026 (recorded at `acquired_at_utc: 2026-07-19T12:00:00Z` in manifest); July 2026 data will be acquired in August 2026. Potential TSO price revisions between acquisition dates are declared as a known data-vintage bias.

### C3. Elevation Threshold (Frozen Before Data)
Zone $z$ is "elevated" iff $S(z) \ge S_{\text{thresh}}$ (e.g., $15.0\%$, 1.5x baseline decile).

### C4. Decision Rule — Three Outcomes
- **`REGIONAL`**: GB elevated AND $\ge N_{\text{high}}$ of 6 EU zones elevated.
- **`GB-SPECIFIC`**: GB elevated AND $\le N_{\text{low}}$ of 6 EU zones elevated.
- **`INCONCLUSIVE`**: Every other configuration, including GB not elevated. *INCONCLUSIVE is a first-class outcome and is reported as the finding when it occurs.*

### C5. Independence Caveat (Load-Bearing)
The 6 EU zones are NOT independent samples (DK_1/DK_2 share a national system, NL/BE/FR are interconnector-coupled). The count in C4 is a descriptive tally, not a statistical test ($n = 1$ time window).

---

## Layer 3 / Decision (Human-Owned): Gate Status & Open Threshold Choices

- **Current Status:** `DRAFT SUBMITTED FOR RATIFICATION` on `feature/omn-003-preregistration-draft`.
- **Human Choice 1 (Elevation Threshold $S_{\text{thresh}}$ in C3):** [15.0% | 12.5% | 20.0%]
- **Human Choice 2 (INCONCLUSIVE Band Limits $N_{\text{high}} / N_{\text{low}}$ in C4):** [4-of-6 / 1-of-6 | 5-of-6 / 2-of-6]
