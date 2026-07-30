# Parametric Changelog — Open Market Note #001 (NEM Duration Baseline)

### Entry #000 — Pre-Publication BESS Denominator Alignment & Fleet Subsample Calibration
- **Date:** 2026-07-19  
- **Producing Commit:** `29012c8d27376c729dd73fe31fb84a0c8cb0bbf3`  
- **Scope:** `reproduce.py`, `PARAMS.md`, `results.json`  
- **Change:** Verified nameplate energy capacities against official AEMO National Electricity Market Registration and Exemption List (15 May 2026). Corrected 6 BESS energy denominators (BHB1: 50.0 MWh, WALGRV1: 75.0 MWh, ULPBESS1: 298.0 MWh, HBESS1: 150.0 MWh, WDBESS1: 540.0 MWh, BLYTHB1: 477.0 MWh) and aligned fleet subsample to 16 accepted operational units (excluding mid-window commissioning units TARBESS1 and TEMPB1).  
- **Output Hash Transition:** Output hash transitioned from pre-calibration draft `7d24f0a6...` (at freeze commit `6df5bcc`) to authoritative baseline output hash `c192e7ee...` (at producing commit `29012c8`).  
- **Status:** Published Baseline Reference

---

### Entry #001 — Date Window Parameterization for Recurrence Spec v1.0.2 Compatibility
- **Date:** 2026-07-30  
- **Scope:** `download_aemo_data.py`, `reproduce.py`  
- **Change:** Added `--start-date` (`YYYY-MM-DD`) and `--end-date` (`YYYY-MM-DD`) command-line arguments. Full parameterization of `pd.date_range`, `month_days`, and plot titles without hardcoded date literals.  
- **Default Preservation:** When invoked without arguments, default execution preserves the frozen baseline window (`2025-06-01` to `2026-06-30`) byte-identically.  
- **Recurrence Compatibility:** Enables automated Recurrence Spec workflows to specify a dynamic 13-month rolling window without altering underlying metric definitions, price thresholds, or `PARAMS.md`.  
- **Status:** Pending Ratification (Pre-Merge)

---

### Entry #002 — `reproduce_sha256` Registry Transition: Path Anchoring & Upper-Bound Date Filtering
- **Date:** 2026-07-30  
- **Scope:** `reproduce.py`, `notes_registry.json`  
- **Previous Hash (`v1.0.0` baseline script @ producing commit `29012c8`):** `acfb4c6f48fe68daee6d7c945b7ff48c8f07ad627dbf8e4cb2721ad902a5209c`  
- **Current Hash (Mandate 3 enforced):** `f6f6c2617bcfc0e09bf3cf8625542352b63ee74209eee3e9605607198b53fc81` (commit `668677a`)  
- **Changes Applied:**  
  1. Input path anchored to `os.path.abspath(os.path.join(script_dir, "data", "processed"))` instead of CWD-relative `../../data/processed`.  
  2. Added `--out-dir` CLI argument for isolated output directory (enabling non-destructive synthetic CI guard).  
  3. Added upper-bound date filtering (`SETTLEMENTDATE <= end_date+1d 04:00:00`) — previously only lower bound was enforced.  
  4. Added `--data-dir` absolute path resolution via `os.path.abspath()`.  
- **Empirical Reproduction Verification:**  
  ```
  python reproduce.py --start-date 2025-06-01 --end-date 2026-06-30 \
    --data-dir ./data/processed --out-dir /tmp/repro_check
  sha256sum /tmp/repro_check/results.json
  c192e7ee97ac413a07db6a1357f0dbcf49c1164cdbe0a5a4c0f5e9b113b614ed
  ```
  Baseline output hash (`results_sha256`) byte-identical to published $v1.0.0$ Zenodo record (`c192e7ee...`) over complete 13-month telemetry. Upper-bound date filtering guarantees boundary safety for future rolling window executions.  
- **Classification:** Non-breaking maintenance patch ($v1.x.0$). No new Zenodo DOI required per Mandate 5.  
- **Status:** Pending Ratification (Pre-Merge)
