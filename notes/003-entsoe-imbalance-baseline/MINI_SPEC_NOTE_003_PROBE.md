# VolMax Open Market Note #003 Probe: Pre-Registration Mini-Spec
> **Scope:** July 2026 Recurrence & European Imbalance Scarcity Probe  
> **Version:** 1.9.0-draft (Fully Reconstructed & Verified Pre-Registration Spec)  
> **Status:** Draft Submitted to Human Gate on `feature/omn-003-preregistration-draft` (Pre-Execution Freeze)  
> **Repository:** `VolMax-Studio/Open-Market-Notes`  
> **PARAMS Freeze Commitment (`a2c0b3a`):** `feat(note-003): publish final ENTSO-E baseline note with PARAMS v3.1.0 and reproducible figures`  
> **PARAMS Cryptographic SHA-256:** `acc7111a0119f835540689fcffbe7f3333cef9d2b580bc81e8174c2add2c9e58`  
> **Main Branch HEAD (`6fa1cb7`):** `Merge pull request #51 from VolMax-Studio/recurrent-measurement/omn-004-31221838425`  
> **Pipeline Analysis Script (`run_imbalance_analysis.py`) SHA-256:** `93bc17f58b64326db78fc3fa4d10031a146fa42af74ddfb40f4942db2677281b`  
> **Ingestion Script (`download_entsoe_data.py`) Draft SHA-256:** `c6eb203ab3daf4c6f4844aeb4b2c248d2466eaa373bff5afd56bcba80aa7eabe`  
> **Baseline Results SHA-256 (`notes_registry.json`):** `b1c713379887043cc429a43d12722939ec70c4ff93f351512970a302478131f9`

---

## Layer 1 / Measured: Reconstructed Baseline & Pre-Registered Protocol

### 1. Pre-Registered Metrics & Threshold Definitions (Restored & Verified)
- **Metric M1: Scarcity Duration & Shortage Pricing**
  - Evaluated on Shortage Column (`Short` for Dual Pricing zones, or Single Imbalance Price column).
  - **Threshold A (Moderate Scarcity):** Imbalance Price $\ge €100.00/\text{MWh}$.
  - **Threshold B (Extreme Scarcity):** Imbalance Price $\ge €250.00/\text{MWh}$.
  - **Continuity Rule:** Imbalance scarcity events are contiguous 15-minute settlement intervals where price remains at or above threshold. A timestamp gap $>15\text{ minutes}$ terminates an ongoing event block.
- **Metric M2: Grid Surplus Absorption & BESS Charging Windows**
  - Evaluated on Surplus Column (`Long` for Dual Pricing zones, or Single Imbalance Price column).
  - **Cheap Surplus Threshold:** Imbalance Price $\le €25.00/\text{MWh}$.
  - **Zero/Negative Surplus Threshold:** Imbalance Price $\le €0.00/\text{MWh}$.
  - **BESS Opportunity Windows:**
    - **4-Hour BESS Window:** Minimum $4.75\text{ hours}$ ($\ge 19$ settlement intervals at $85\%$ round-trip efficiency).
    - **8-Hour BESS Window:** Minimum $9.50\text{ hours}$ ($\ge 38$ settlement intervals at $85\%$ round-trip efficiency).

### 2. Temporal Windows & Baseline Isolation
- **Baseline Window (Zenodo v1.0.0):** 1 June 2025 – 30 June 2026 (13 Calendar Months / 395 Days).
- **Uncontaminated Baseline Window ($Q_{90}$ Base):** 1 August 2025 – 30 June 2026 (11 Calendar Months / 334 Days).
- **Probe Window:** 1 July 2026 – 31 July 2026 (31 Days / 2,976 expected 15-min settlement intervals per zone).
- **Matched Pair Window:** July 2026 vs July 2025 (same zone, same script, same metric).

### 3. Licensing Boundary Guard & Source Platform
- **Permitted Data Source:** ENTSO-E Primary Transparency Platform (REST API DocumentType `A85`, Imbalance Prices).
- **Forbidden Data Source:** DocumentType `A44` (Day-Ahead Prices) or unverified third-party aggregators.
- **Provenance Manifest Anchor:** `data_manifest.json` contains verbatim entry: `"acquired_at_utc": "2026-07-19T12:00:00Z"`.

### 4. Code-Enforced Mandate 8 & Data Completeness Guard
- **Row Floor:** $\lceil 2,976 \times 0.98 \rceil = \mathbf{2,917\text{ intervals}}$ ($98.0\%$ math ceiling for 31 days).  
  *Operational Extension Note:* The $98\%$ telemetry floor is a Note #003 pre-registration extension pending formal ratification in RECURRENCE_SPEC v1.1.0.
- **Timestamp Gap Threshold:** $\le 90\text{ minutes}$.  
  *Post-Hoc Empirical Calibration Note:* Threshold of 90 minutes was calibrated to DK_1/DK_2 historical baseline telemetry gap structure.

### 5. Step 0 Determinism & Baseline Feather Integrity Verification (Blocker 4 & 5 Verification)
- **Baseline Integrity Execution:** Running `run_imbalance_analysis.py` against baseline `.feather` files produced SHA-256 `b1c713379887043cc429a43d12722939ec70c4ff93f351512970a302478131f9` (100% byte-perfect match with `notes_registry.json`).
- **Step 0 Protocol:**
  1. Isolated output directory: `--out-dir scratch/step0_probe`.
  2. Verify zero modification to `./data/processed/imbalance_{ZONE}.feather` baseline files.
  3. Validate output hash against pre-registered baseline result hash (`b1c71337...`).

### 6. Verified Target Bidding Zones & Regime Mapping Persistence
- **NL** Netherlands (`10YNL----------L`) — *Frozen DUAL_PRICING*
- **BE** Belgium (`10YBE----------X`) — *Frozen SINGLE_PRICING*
- **FR** France (`10YFR-RTE------C`) — *Frozen DUAL_PRICING*
- **DK_1** Denmark West (`10YDK-1--------W`) — *Frozen SINGLE_PRICING*
- **DK_2** Denmark East (`10YDK-2--------T`) — *Frozen SINGLE_PRICING*
- **AT** Austria (`10YAT-APG------L`) — *Frozen SINGLE_PRICING*  
*Persistence:* Regime mapping parameters (`frozen_regime`, `m1_shortage_col`, `m2_surplus_col`) are persisted into `data_manifest.json` under each zone's file entry.

### 7. Security & Zero Secret Leakage Pipeline (Mandate 9)
- **Token Source:** Environment variable `ENTSOE_API_KEY`.
- **Token Rotation Verification:** Active key prefix vs historical compromised prefix (`RESULT: NO MATCH`).
- **Redaction Order:** `sanitize_token_url()` scrubs `securityToken=[^&]+` parameters on `response.url` and `request.url` *prior* to string formatting.

---

## Layer 2 / Inference / Hypothesis: Cross-Market Comparison Protocol (C1–C5)

### C1. Normalised Scarcity Metric (Currency-Free)
For each market $m$ and zone $z$, let $Q_{90}(z)$ be the 90th percentile of imbalance price over that zone's own uncontaminated baseline (1 Aug 2025 – 30 Jun 2026, 11 months). Define:
$$S(z) = \text{share of settlement TIME in probe month with price} \ge Q_{90}(z)$$
Expressed as share of time (not raw interval counts). No FX conversion is performed anywhere. Absolute EUR thresholds (M1/M2) remain descriptive within EU zones only and carry NO cross-market weight.

### C2. Matched Comparator Pair & Vintage Bias Declaration
July 2026 vs July 2025, same zone, same metric, both computed by the same script. GB is recomputed on the matched July/July pair after Elexon HTTP retry logic is landed.  
*Vintage Bias:* July 2025 data was acquired in July 2026 (recorded at `"acquired_at_utc": "2026-07-19T12:00:00Z"` in manifest); July 2026 data will be acquired in August 2026. Potential TSO price revisions between acquisition dates are declared as a known data-vintage bias.

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
