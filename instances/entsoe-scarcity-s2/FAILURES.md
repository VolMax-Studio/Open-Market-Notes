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

---

## [FAILURES #005] run-003-confirmatory Parser Specification Defect (Multi-Period Iteration & Price Category Filtering)

- **Run ID:** `run-003-confirmatory`
- **Execution Date:** 2026-09-05
- **Nominal Freeze Commit:** `d9dfbbada85100243ba0150835d824c1c68629cd`
- **Evidence Commit:** `9a68ed467f56cf8f1155986fc0d17676c66cf1d2`
- **Disposition:** `Acquisition valid — interpretation invalid (frozen parser specification defect)`
- **Preserved Evidence:** Preserved under `evidence/runs/run-003-confirmatory/` (12 raw HTTP 200 PKZip payloads totaling ~3.5MB, `command.sh`, `env.txt`, `git_commit.txt`, `inputs.sha256`, `outputs.sha256`, `run_metadata.json`, `derived_results.json`, `expected_grids.json`, `missing_listings.json`, `duplicate_listings.json`, `document_inventory.json`, `stdout.log`, `stderr.log`).

### Findings Recorded:
1. **B-21 (Multi-Period Iteration within TimeSeries):** In IEC 62325 XML Balancing Market Documents, a single `<TimeSeries>` contains multiple `<Period>` child elements across temporal segments (e.g. across seasonal/DST boundaries). The frozen parser used `ts.find('.//ns:Period')` which read only the first `<Period>` element and ignored all subsequent `<Period>` elements, generating large artificial missing MTU counts (e.g. 23,307 missing intervals in AT baseline).
2. **B-23 (Price Direction Selection via `<imbalance_Price.category>`):** In DocumentType A85 XML documents, `flowDirection.direction` does not exist on `<TimeSeries>`. Price direction is specified at the `<Point>` level by `<imbalance_Price.category>`: `A04` for Shortage / Deficit price and `A05` for Surplus / Excess price. The parser parsed both `A04` and `A05` series without category filtering, resulting in duplicate counts matching unique observed counts.
3. **B-24 (`Short` Column Mapping Terminology):** `L0.md` previously described shortage column mapping as "Short" (inherited from `entsoe-py` dataframe semantics), which does not correspond to XML elements. The exact XML selector is `<imbalance_Price.category>A04</imbalance_Price.category>`.

4. **B-25 (Unconditional Category Filtering):** `<imbalance_Price.category>` filter must be unconditional (`if category != 'A04': continue`), preventing any point lacking category or bearing a non-A04 category from silently entering the shortage population.
5. **B-26 (Source Vintage Hash Verification Invariant):** Offline interpretation runs (`--source-raw-dir`) must verify before extraction that every loaded payload matches the pinned SHA-256 hash in the source run's `run_metadata.json` (or `outputs.sha256`), triggering `EXECUTION_STATE_INVALID` on any missing metadata or mismatch.

### Confirmed Surviving Findings from run-003:
- Complete 12/12 HTTP 200 acquisition batch successfully executed and preserved.
- PKZip container extraction and document identity invariants (`documentType=A85`, `processType=A16`, `resolution=PT15M`) verified across all 12 responses.
- Preserved raw response vintage is valid, byte-frozen, and reusable for offline interpretation in `run-004`.

### Remediation for run-004:
- Update `L0.md` v4 and `PREREGISTRATION.md` v4 to specify multi-period iteration across all `<Period>` children, unconditional category filtering for `<imbalance_Price.category>A04</imbalance_Price.category>`, and strict source vintage hash verification.
- Configure `run-004` as an offline interpretation run over the preserved `run-003` raw vintage (`evidence/runs/run-003-confirmatory/raw/`), eliminating source revision noise and isolating all differences strictly to the parser specification fix.
- Update `README.md` status: `Target S: NOT INTERPRETABLE`, `Target R: NOT EVALUATED`.
