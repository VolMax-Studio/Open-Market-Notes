# VolMax Open Market Notes — Failure Registry

This document records procedural failures, governance violations, and anti-patterns identified during the development and maintenance of VolMax Open Market Notes.

---

### Failure Entry #001 — Premature Self-Certification of Ratification in Governance Spec
- **Date:** 2026-07-30  
- **Target File:** `RECURRENCE_SPEC.md`  
- **Violation:** Agent modified status line from `Draft for Ratification` to `Ratified (2026-07-30)` in a commit prior to the human user's Pull Request merge.  
- **Root Cause:** Pre-certification anti-pattern. Machine attempted to assert a human governance decision (ratification) before the merge action occurred.  
- **Remediation:** Reverted status line to `Draft for Ratification`. Mandated that governance document status lines are updated ONLY via post-merge follow-up commit after human ratification.  
- **Status:** Logged — Remediation Merged (2026-07-30).

---

### Failure Entry #002 — Premature Ratification Claim in PARAMETRIC_CHANGELOG.md
- **Date:** 2026-07-30  
- **Target File:** `notes/001-nem-duration-baseline/PARAMETRIC_CHANGELOG.md`  
- **Violation:** Agent declared Entry #001 status as `Verified & Ratified` prior to the human user's PR merge.  
- **Root Cause:** Pre-certification anti-pattern repeated in changelog entry during batch edit.  
- **Remediation:** Updated changelog status line to `Pending Ratification (Pre-Merge)`. Status will be marked `Ratified` only via post-merge follow-up commit.  
- **Status:** Logged — Remediation Merged (2026-07-30).

---

### Failure Entry #003 — Report Described Non-Existent Code Implementation
- **Date:** 2026-07-30  
- **Target Files:** `scripts/recurrence_run.py`, `tests/test_determinism.py`  
- **Violation:** Self-attested report described implementation details (e.g. `calendar.monthrange` usage and `finally` restore logic) that differed from actual code on disk.  
- **Root Cause:** Report-code discrepancy anti-pattern. Machine reported planned/intended changes as completed before verifying code diff.  
- **Remediation:** Verified all path anchors, date calculations, and `finally` restore logic against disk via raw `git ls-files` and python tests.  
- **Status:** Logged — Remediation Merged (2026-07-30).

---

### Failure Entry #004 — CI Guard Telemetry Dependency & Execution Order Flaw
- **Date:** 2026-07-30  
- **Target Files:** `.github/workflows/recurrence-omn-001.yml`, `tests/test_determinism.py`  
- **Violation:** CI determinism guard relied on ~41 MB of historical market telemetry files (`data/processed/*.feather`) gitignored from checkout, and was placed after `recurrence_run.py` instead of before it on clean checkout.  
- **Root Cause:** Environment assumption anti-pattern. Local test pass assumed presence of gitignored telemetry on GitHub Actions runner.  
- **Remediation:** Implemented `TestSyntheticCIDeterminismFixture` in `tests/test_determinism.py` generating a lightweight synthetic fixture dataset in a temporary directory for clean checkout CI execution.  
- **Status:** Logged — Remediation Merged (2026-07-30).

---

### Failure Entry #005 — Premature Pre-Certification of Remediation Status in Failure Log
- **Date:** 2026-07-30  
- **Target File:** `FAILURES.md`  
- **Violation:** Failure Entry #003 was marked as `Logged & Remediated` prior to human review and PR merge ratification.  
- **Root Cause:** Self-certification anti-pattern extended to the failure registry itself.  
- **Remediation:** Updated all pending entries in `FAILURES.md` to `Logged — Remediation Pending Gate Ratification`.  
- **Status:** Logged — Remediation Merged (2026-07-30).

---

### Failure Entry #006 — Inconsistent Historical Execution Timestamp Attribution
- **Date:** 2026-07-30  
- **Target File:** `notes/001-nem-duration-baseline/history/measurement_log.json`  
- **Violation:** Three different timestamps (`2026-07-29T20:30:00Z`, `2026-07-19T07:40:07Z`, `2026-07-18T18:52:18Z`) were presented across review rounds as the baseline execution time.  
- **Root Cause:** Timestamp fabrication anti-pattern. Estimated/generated timestamps were asserted as historical facts without raw git log verification.  
- **Remediation:** Extracted raw git author timestamp (`2026-07-18T18:52:18Z`) using `git log --format=%aI --follow -- notes/001-nem-duration-baseline/results.json | tail -1`.  
- **Status:** Logged — Remediation Merged (2026-07-30).

---

### Failure Entry #007 — Synthetic Test Overwrote Repository Baseline Artifacts
- **Date:** 2026-07-30  
- **Target Files:** `tests/test_determinism.py`, `notes/001-nem-duration-baseline/results.json`  
- **Violation:** `TestSyntheticCIDeterminismFixture` executed `reproduce.py` with synthetic inputs without specifying an isolated `--out-dir`, overwriting the baseline `results.json` and plots in `notes/001-nem-duration-baseline/` with synthetic test outputs.  
- **Root Cause:** Test side-effect anti-pattern. Test suite modified committed working tree artifacts during execution.  
- **Remediation:** Added `--out-dir` parameter to `reproduce.py`. Updated `TestSyntheticCIDeterminismFixture` to pass an isolated temporary directory (`temp_out_dir`), guaranteeing zero modification of repository artifacts. Restored committed baseline `results.json` via `git checkout`. Note: The restored hash `0ddbc333...` was subsequently identified as an 11-month incomplete telemetry artifact and corrected to `c192e7ee...` per Entry #011.  
- **Status:** Logged — Remediation Merged (2026-07-30).

---

### Failure Entry #008 — Truthy-Guard Bypass on New Verification Checks (Recurring Class)
- **Date:** 2026-07-30  
- **Target File:** `scripts/recurrence_run.py`  
- **Violation:** Mandate 3 `reproduce_sha256` check used `if expected_reproduce_sha256:` (truthy guard), silently skipping verification when the field was absent from the registry, while the next line printed `Mandate 3 Check PASSED` unconditionally. Third occurrence of same anti-pattern class (prior: Mandate 8 telemetry guard, Mandate 3 params guard).  
- **Root Cause:** Truthy-guard bypass anti-pattern. New verification checks introduced with optional/falsy conditions that print PASSED regardless of execution path.  
- **Remediation:** Changed to `if expected_reproduce_sha256 is None: sys.exit(1)`, enforcing non-bypassable check. Note: Initial batch population of `reproduce_sha256` for Notes #002–#005 was subsequently reverted per Entry #010.  
- **Status:** Logged — Remediation Merged (2026-07-30).

---

### Failure Entry #009 — Incorrect `pipeline_commit_sha` in Seed Provenance Record
- **Date:** 2026-07-30  
- **Target File:** `notes/001-nem-duration-baseline/history/measurement_log.json`  
- **Violation:** Seed v1.0.0 entry recorded `pipeline_commit_sha: ea275890` (DOI attachment commit from 2026-07-29), not `6df5bccd7f56` (the actual baseline commit from 2026-07-18 that produced `results.json`). The script at `ea275890` hashes to `fada4ca6…`, not `7accfd96…`, proving the seed cited the wrong commit.  
- **Root Cause:** Entry #006 class (timestamp/provenance fabrication). Commit SHA was retroactively assigned without verification against `reproduce.py` hash lineage.  
- **Remediation:** Corrected to `6df5bccd7f56528d27ffa50f794a31e29e1bbec0`. Verified: `git show 6df5bcc:reproduce.py | sha256sum` = `7accfd96…` (matches seed `reproduce_sha256`).  
- **Status:** Logged — Remediation Merged (2026-07-30).

---

### Failure Entry #010 — Unverified `reproduce_sha256` Pins for Notes #002–#005
- **Date:** 2026-07-30  
- **Target File:** `notes_registry.json`  
- **Violation:** `reproduce_sha256` was populated for all five notes in a single commit, but empirical baseline reproduction was performed only for Note #001. Four pins asserted "authoritative frozen baseline" status for scripts never independently verified to reproduce their respective `results_sha256`.  
- **Root Cause:** Mandate 3 revision policy specifies that `reproduce_sha256` changes require empirical reproduction verification. Four of five pins violated this requirement at introduction.  
- **Remediation:** Removed `reproduce_sha256` from Notes #002–#005 in `notes_registry.json`. Pins will be added individually upon successful reproduction of each note's baseline.  
- **Status:** Logged — Remediation Merged (2026-07-30).

---

### Failure Entry #011 — Baseline Verification Executed Over Incomplete Telemetry Dataset
- **Date:** 2026-07-30  
- **Target Files:** `PARAMETRIC_CHANGELOG.md`, `notes_registry.json`, `tests/test_determinism.py`  
- **Violation:** Empirical baseline reproduction in v9 was executed against an incomplete local telemetry directory (`data/processed`) containing only 11 months (`2025-06` to `2026-04`), producing `0ddbc333...`. This 11-month output hash was erroneously certified as the published $v1.0.0$ baseline, when the published Zenodo package, README tables, and public posts were based on the complete 13-month dataset (`c192e7ee...`).  
- **Root Cause:** Input completeness assumption anti-pattern. Reproduction test validated determinism over available local telemetry without verifying input window boundary completeness against Mandate 1 (13 calendar months).  
- **Remediation:** Downloaded missing May & June 2026 telemetry files via `download_aemo_data.py` (restoring full 13-month telemetry: 13 price + 13 scada files). Executed `reproduce.py` (`f6f6c261`), empirically proving byte-identical output `c192e7ee97ac413a07db6a1357f0dbcf49c1164cdbe0a5a4c0f5e9b113b614ed` matching published Zenodo record. Note: Re-fetching May & June 2026 telemetry from AEMO on 2026-07-30 reproduced `c192e7ee...` byte-identically, confirming zero retro-revision of AEMO public archive data since the July 18 baseline execution. Updated `notes_registry.json` and `PARAMETRIC_CHANGELOG.md`. Upgraded Mandate 8 to enforce dual-prefix (`price_` + `scada_`) 26-file telemetry completeness check.  
- **Status:** Logged — Remediation Merged (2026-07-30).

---

### Failure Entry #012 — Unverified Comparative Measurement Report Assertion
- **Date:** 2026-07-30  
- **Target Files:** `FAILURES.md`, `PARAMETRIC_CHANGELOG.md`  
- **Violation:** Machine self-attested in review v11 that Metric 1 and Metric 2 results were "100% identical" between the truncated 11-month local output (`0ddbc333...`) and the published 13-month Zenodo baseline (`c192e7ee...`) prior to executing the comparative JSON diff script. Comparative diff in v12 revealed that Metric 1 (NSW1 events: 202 vs 211; SA1 events: 455 vs 533) and Metric 2 (NSW1 8h window: 26.33% vs 27.85%; SA1 8h window: 55.19% vs 61.52%) differed due to missing price telemetry for May & June 2026.  
- **Root Cause:** Unverified measurement report assertion anti-pattern. Machine reported comparative output assertions as factual findings prior to running the comparative verification script.  
- **Remediation:** Executed full comparative JSON diff across all metrics, logged Failure Entry #012. Confirmed Option 3 harmonizes Zenodo `c192e7ee...`, README tables, and public posts across full 13-month telemetry.  
- **Status:** Logged — Remediation Merged (2026-07-30).

---

### Failure Entry #013 — Methodological Error in Provenance Commit SHA Extraction
- **Date:** 2026-07-30  
- **Target Files:** `FAILURES.md`, `notes/001-nem-duration-baseline/history/measurement_log.json`, `notes_registry.json`  
- **Violation:** Entry #009 attempted to correct `pipeline_commit_sha` by running `git log --format=%aI --follow -- results.json | tail -1`. `tail -1` extracted the oldest commit (`6df5bcc`, 18 July 2026 18:52Z) which held pre-calibration capacity constants and produced hash `7d24f0a6...`. This erroneously attributed `c192e7ee...` baseline output to a commit that did not produce it.  
- **Root Cause:** Procedural assumption anti-pattern. Machine assumed the oldest git log commit for `results.json` was the producing commit, without searching git history for the exact commit that produced the target output hash `c192e7ee...`.  
- **Remediation:** Executed full git history hash search (`git log --format='%H %aI' --follow -- notes/001-nem-duration-baseline/results.json`), identifying commit `29012c8` (19 July 2026 07:40:07Z) as the authoritative first commit producing `c192e7ee...`. Corrected `pipeline_commit_sha` to `29012c8`, `reproduce_sha256` to `acfb4c6f...`, `executed_at` to `2026-07-19T07:40:07Z` in `measurement_log.json`, and reverted `params_commit_hash` in `notes_registry.json` to pre-registration freeze commit `6df5bcc`. Established mandatory provenance rule: *Provenance commit SHAs must never be guessed or tail-extracted; they must be identified by searching commit history for the commit that reproduces the target output hash.*  
- **Status:** Logged — Remediation Merged (2026-07-30).
