# Parametric Changelog — Open Market Note #004 (GB BESS Duration Baseline)

*(Governance Note: All entries marked `Pending Ratification (Pre-Merge)` transition to `Ratified` upon PR merge to `main`).*

### Entry #000 — Pre-Publication Baseline Freeze & Ground-Truth Verification
- **Date:** 2026-07-25  
- **Producing Commit:** `792b4d9`  
- **Scope:** `run_analysis.py`, `download_elexon_data.py`, `PARAMS.md`, `results.json`  
- **Change:** Frozen 13-month baseline telemetry for Great Britain System Prices (`2025-06-01` to `2026-06-30`, 18,960 settlement periods). Single Imbalance Pricing regime verified across 100% of intervals.  
- **Authoritative Baseline Hash:** `385ddfd9ed88357d6edf1dc39161468dbaa94115339671d4a39cec90446f873e`  
- **Status:** Published Baseline Reference (Zenodo DOI: 10.5281/zenodo.21693262)

---

### Entry #001 — `reproduce_sha256` Registry Transition & Pipeline Parameterization
- **Date:** 2026-08-06  
- **Scope:** `run_analysis.py`, `download_elexon_data.py`, `notes_registry.json`, `data_manifest.json`  
- **Previous Script Hash (`v1.0.0` baseline script @ commit `792b4d9`):** `c168f0ceab8320002b784ce71ee458ec3f05c3589ea3cc653cddb71923ff2180`  
- **Current Script Hash (Mandate 3 enforced):** `f3642ff2829e5a3eadf97832aba6042a47176f66d2f85efe30b3a323cbf6b0ae`  
- **Changes Applied:**  
  1. Parameterized CLI arguments (`--start-date`, `--end-date`, `--data-dir`, `--out-dir`).  
  2. Implemented **Market Timezone Calendar Day Filtering** (`Europe/London` `start_date 00:00:00` to `end_date 23:59:59`), eliminating boundary daylight saving truncations.  
  3. Added frozen ground-truth telemetry directory (`data/baseline/gb_system_prices_202506_202606.feather`) to protect single-file layout from being overwritten by recurrent rolling window executions (NB113).  
  4. Enforced strict date window matching (`("2025-06-01", "2026-06-30")`) before allowing baseline fallback in `run_analysis.py`; non-baseline windows without explicit `--data-dir` fail-closed (NB117).  
  5. Updated `download_elexon_data.py` (committed in `0c3f9c5`) to write dynamic CSV cache filenames (`gb_system_prices_YYYYMM_YYYYMM.csv`) and register both CSV and Feather files in `data_manifest.json` (NB111, NB112, NB119).  
  6. Empirical baseline telemetry re-acquisition from Elexon API produced **100% byte-identical System Price data**, confirming Elexon settlement stability.  
- **Empirical Reproduction Verification:**  
  ```bash
  python notes/004-gb-duration-baseline/run_analysis.py \
    --start-date 2025-06-01 --end-date 2026-06-30 --out-dir /tmp/repro_004b
  sha256sum /tmp/repro_004b/results.json
  385ddfd9ed88357d6edf1dc39161468dbaa94115339671d4a39cec90446f873e  /tmp/repro_004b/results.json
  ```
  Baseline output hash (`results_sha256`) is **100% byte-identical** to published $v1.0.0$ Zenodo record (`385ddfd9...`) over complete 13-month telemetry.  
- **Classification:** Non-breaking maintenance patch ($v1.x.0$).  
- **Status:** Pending Ratification (Pre-Merge)

---

### Entry #002 — BSC Settlement Reconciliation Lifecycle & Ingestion Provenance Alignment
- **Date:** 2026-08-06  
- **Scope:** `data_manifest.json`, `README.md`, `PARAMETRIC_CHANGELOG.md`  
- **Governance Finding:** Elexon System Prices undergo multi-stage BSC settlement reconciliations (Interim, SF, R1, R2, R3 over ~14 months). In accordance with Mandate 3, frozen baseline parameters (`PARAMS.md` sha256 `6efc418b...`) remain immutable. Retrospective findings regarding Elexon settlement run revision mechanics (`priceDerivationCode` P/R) are recorded here and in `README.md` rather than retroactively altering frozen parameter definitions.  
- **Status:** Pending Ratification (Pre-Merge)

---

### Entry #003 — Recurrence Measurement v1.1.0 Executed via Mandate 7 (GitHub Hosted-Runner Unavailability & HTTP Retry Patch)
- **Date:** 2026-08-06  
- **Scope:** `download_elexon_data.py`, `results.json`, `data_manifest.json`, `history/measurement_log.json`  
- **Governance Audit Findings:**  
  1. **GitHub Runner Outage:** Two consecutive workflow dispatches for Note #004 failed to acquire an automated runner (`Internal server error`, `The job was not acquired by Runner of type hosted even after multiple attempts`).  
  2. **Mandate 7 Manual Recurrence:** Per Mandate 7 (manual recurrence authorized when automated infrastructure is unavailable), the measurement was executed locally. Mandate 3 (`PARAMS.md` sha256 `6efc418b...` and script sha256 `f3642ff2...`) and Mandate 8 (`19,008` settlement periods verified) both passed cleanly. `pipeline_commit_sha` references the branch HEAD at execution time (`c92d9ad9...`).  
  3. **Mandate 8 Abort & HTTP Retry Patch:** Initial local run aborted under Mandate 8 (`18,864 rows < 19,008 threshold`) due to three historical days (`2025-07-02`, `2025-09-21`, `2025-11-18`) lost to transient Elexon B1780 API HTTP timeouts. Added 3-attempt HTTP retry logic with 0.5s backoff to `download_elexon_data.py`, enabling 100% complete telemetry retrieval on second attempt.  
  4. **Empirical Measurement (`v1.1.0`):** Rolling window `2025-07-01` to `2026-07-31` produced `results_sha256: 9cd0c9117e580732776db0251f9a0edf68c669591805c1ab7a3fffc602eaded7`.  
- **Status:** Pending Ratification (Pre-Merge)
