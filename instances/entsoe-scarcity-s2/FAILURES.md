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
- Formalize structured halt taxonomy (`HTTP_ERROR`, `REQUEST_CONTRACT_UNSUPPORTED`, `API_REPORTS_NO_MATCHING_DATA`, `API_REASON_OTHER`, `SOURCE_IDENTITY_INVALID`, `EXECUTION_STATE_INVALID`).

---

## [FAILURES #004] run-002-confirmatory Specification Boundary Failure (PKZip Container & Multi-Member Extraction)

- **Run ID:** `run-002-confirmatory`
- **Execution Date:** 2026-09-05
- **Nominal Freeze Commit:** `98929035eb86a6f65a83fc4538a732e98f13912a`
- **Evidence Commit:** `1a53d688b1f41bf56ca01062b0c3ffb9cf1ba895`
- **Disposition:** `Halted outside frozen taxonomy (Clean 12/12 acquisition, interpretation halted on undescribed PKZip container format)`
- **Preserved Evidence:** Preserved under `evidence/runs/run-002-confirmatory/` (12 raw HTTP 200 PKZip payloads totaling ~3.5MB, `command.sh`, `env.txt`, `git_commit.txt`, `inputs.sha256`, `outputs.sha256`, `run_metadata.json`, `stdout.log`, `stderr.log`).

### Findings Recorded:
1. **B-19 (Payload is PKZip Container, not Plain XML):** All 12 successful HTTP 200 responses were delivered by ENTSO-E as PKZip compressed archives (magic bytes `50 4b 03 04`). AT and BE baseline each contain 2 XML members in the archive; the remaining 10 contain 1 XML member. The frozen v2 specification and parser expected direct uncompressed XML bytes, causing `xml.etree.ElementTree.ParseError`. Multi-member archive ordering and extraction must be explicitly specified and implemented.
2. **B-20 (Halt was Outside Pre-registered Taxonomy):** The parse exception escaped unhandled, resulting in `exit_code = 1` recorded by shell with `halt_class = None` in metadata. Halt taxonomy must include `PAYLOAD_FORMAT_UNEXPECTED` (or explicit container validation).

### Confirmed Surviving Findings from run-002:
- ENTSO-E accepted the full preregistered 334-day baseline request for all six zones (12/12 HTTP 200).
- All six corrected area identifiers produced valid HTTP 200 responses.
- Raw payload hashes match recorded run metadata down to the byte.
- Execution harness was frozen before run; dynamic commit check passed cleanly.

### Remediation for run-003:
- In `L0.md` v3 and `PREREGISTRATION.md` v3, formalize §3 PKZip container detection, member sorting, multi-member XML extraction, and deterministic MTU merging.
- Add `PAYLOAD_FORMAT_UNEXPECTED` to the frozen halt taxonomy in §10 and `runner.py`.
- Update `runner.py` to transparently extract PKZip payloads using `zipfile.ZipFile`, parse all contained `Balancing_MarketDocument` XMLs, and evaluate Target S & Target R.
