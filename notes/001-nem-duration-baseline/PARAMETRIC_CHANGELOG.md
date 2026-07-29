# Parametric Changelog — Open Market Note #001 (NEM Duration Baseline)

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
- **Previous Hash (`v1.0.0` baseline script):** `7accfd96e6f9c03c4bea9e76435b9afa87f969862d9f8ec2cf07d028d5d3d279` (commit `6df5bcc`)  
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
  0ddbc333b298b298868966cfb1b49cb09867b7af179e4b9dc809cc65ed512260
  ```
  Baseline output hash (`results_sha256`) byte-identical to published $v1.0.0$ Zenodo record. Upper-bound filter had zero effect on baseline data (all telemetry files fall within window).  
- **Classification:** Non-breaking maintenance patch ($v1.x.0$). No new Zenodo DOI required per Mandate 5.  
- **Status:** Pending Ratification (Pre-Merge)
