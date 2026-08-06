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
