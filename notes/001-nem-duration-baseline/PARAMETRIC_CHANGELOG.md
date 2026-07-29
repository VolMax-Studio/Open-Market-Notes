# Parametric Changelog — Open Market Note #001 (NEM Duration Baseline)

### Entry #001 — Date Window Parameterization for Recurrence Spec v1.0.2 Compatibility
- **Date:** 2026-07-30  
- **Scope:** `download_aemo_data.py`, `reproduce.py`  
- **Change:** Added `--start-date` (`YYYY-MM-DD`) and `--end-date` (`YYYY-MM-DD`) command-line arguments. Full parameterization of `pd.date_range`, `month_days`, and plot titles without hardcoded date literals.  
- **Default Preservation:** When invoked without arguments, default execution preserves the frozen baseline window (`2025-06-01` to `2026-06-30`) byte-identically.  
- **Recurrence Compatibility:** Enables automated Recurrence Spec workflows to specify a dynamic 13-month rolling window without altering underlying metric definitions, price thresholds, or `PARAMS.md`.  
- **Status:** Pending Ratification (Pre-Merge)
