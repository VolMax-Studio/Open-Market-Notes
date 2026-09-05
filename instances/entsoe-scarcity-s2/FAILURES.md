# Failures & Non-Compliances Log — entsoe-scarcity-s2

## [FAILURES #003] run-001-confirmatory Protocol Non-Compliances and Halt Taxonomy Resolution

- **Run ID:** `run-001-confirmatory`
- **Execution Date:** 2026-09-05
- **Nominal Freeze Commit:** `1f6f52d9c6029d105e8a4b80499c7c0553c7525b`
- **Disposition:** `Exploratory (Protocol Non-Compliance)`
- **Preserved Evidence:** Preserved under `evidence/runs/run-001-confirmatory/` (including `raw/AT_baseline_raw.xml`, `raw/AT_target_raw.xml`, `raw/BE_baseline_raw.xml`, `run_metadata.json`, `inputs.sha256`, `outputs.sha256`, and execution logs).

### Findings Recorded:
1. **B-10 (Halt Cause Misclassification):** The execution halted on request 3/12 (Belgium baseline) with ENTSO-E Acknowledgement `Reason 999: "No matching data found for Data item IMBALANCE_PRICES_R3 [17.1.G] (10YBE----------X) and interval 2025-07-31T22:00:00Z/2026-06-30T22:00:00Z."`. The runner classified this as `HALT: request contract unsupported`. However, Request 1 (Austria baseline over the full 334-day window) succeeded completely (HTTP 200, 567,572 bytes), proving the API accepts 334-day queries. The halt cause was an incorrect area identifier (`10YBE----------X` which is Elia TSO Party EIC, instead of `10YBE----------2` which is the Area EIC), not an API query duration limit. Halt taxonomy must distinguish `SOURCE_DATA_ABSENT` from `REQUEST_CONTRACT_UNSUPPORTED`.
2. **B-11 (Dynamic Commit Verification):** `git_commit.txt` was recorded statically rather than dynamically queried from `git rev-parse HEAD`.
3. **B-12 (Contemporaneous Logging):** stdout was captured from task output rather than piped directly during execution (`command > stdout.log 2> stderr.log`).
4. **B-13 (Mutable Governance Files in inputs.sha256):** `STATUS.md` and `PROJECT_HANDOFF.md` were hashed into `inputs.sha256` and subsequently modified post-run. `inputs.sha256` must be strictly restricted to immutable spec and code inputs.
5. **B-14 (Secret Safety):** Zero credential leakage was verified; API token was read strictly from external credentials file and never printed.
6. **B-15 (Freeze Order Defect):** `runner.py` was authored and modified after the pre-execution commit `1f6f52d`. Consequently, `run-001` cannot serve as a confirmatory run and is permanently classified as `Exploratory (Protocol Non-Compliance)`.

### Remediation for run-002:
- Author and freeze `runner.py`, `requirements.txt`, `L0.md` v2, and `PREREGISTRATION.md` v2 in the pre-execution commit before any network execution.
- Update EICs: Belgium (`BE`) = `10YBE----------2`, Denmark East (`DK-2`) = `10YDK-2--------M`.
- Implement dynamic git verification (`git rev-parse HEAD` and `git status --porcelain`) inside `runner.py`.
- Formalize structured halt taxonomy (`HTTP_ERROR`, `REQUEST_CONTRACT_UNSUPPORTED`, `SOURCE_DATA_ABSENT`, `API_REASON_OTHER`, `SOURCE_IDENTITY_INVALID`, `EXECUTION_STATE_INVALID`).
