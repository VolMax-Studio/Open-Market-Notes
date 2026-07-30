# VolMax Open Market Notes — Recurrence Specification
**Version:** v1.0.7  
**Status:** Draft for Ratification  
**Date:** 2026-07-30  
**Repository:** `VolMax-Studio/Open-Market-Notes`  

---

## 1. Executive Summary & Immutability Scope

This document defines the formal operational, procedural, and cryptographic governance protocol for executing **recurrent baseline refreshes** across the VolMax Open Market Notes repository (#001–#005+).

The recurrence pipeline ensures that market observation baselines remain dynamically updated over a rolling 13-month calendar window while strictly maintaining:
1. **Audit Immutability:** Core analytical logic (`reproduce.py`), parameter definitions (`PARAMS.md`), and historical baseline registries (`notes_registry.json`) are immutable. Both `PARAMS.md` and `reproduce.py` immutability are cryptographically enforced via non-bypassable SHA-256 verification (`params_sha256` and `reproduce_sha256`) against the frozen registry reference.
2. **Provenance Traceability:** Every recurrent execution appends a 4-layer Quad-Hash provenance record to `history/measurement_log.json`.
3. **Human-in-the-Loop Ratification:** Automated executions submit Pull Requests; machine code **NEVER** writes directly to `main`.

---

## 2. Revision History & Governance Changelog

- **v1.0.7 (2026-07-30):** Ratified Option 3 alignment of `notes_registry.json` and `results.json` to the canonical 13-month published Zenodo baseline hash (`c192e7ee...`) after restoring complete 13-month telemetry; formalized DOI Revision & `superseded_doi` Erratum Policy in Mandate 5; upgraded Mandate 8 to enforce dual-prefix monthly telemetry completeness (`price_` AND `scada_` files for all 13 months); logged Failure Entries #011 and #012; explicitly supersedes and corrects the erroneous v1.0.6 changelog claim regarding `0ddbc333...` baseline output verification.
- **v1.0.6 (2026-07-30):** Enforced non-bypassable `reproduce_sha256` check across all notes; established Registry Code Hash Revision Policy for minor maintenance patches ($v1.x.0$); pin-locked dependency versions in `requirements.txt`; enriched synthetic CI fixture with scarcity price spikes; dynamic spec version resolution.
- **v1.0.5 (2026-07-30):** Enforced Mandate 3 dual cryptographic check (`params_sha256` + `reproduce_sha256`); mandated isolated output directory (`--out-dir`) for synthetic CI guard; enforced upper and lower boundary date filtering; unified input path anchoring via `requirements.txt` and `--data-dir`; expanded Mandate 7 manual recurrence taxonomy.
- **v1.0.4 (2026-07-30):** Restored Mandate 7 (Execution Modes: Automated vs Manual) and Mandate 9 (Zero Secret Leakage Control); corrected Mandate 1 calendar window phrasing; added synthetic CI guard architecture specification; enforced strict git commit SHA resolution.
- **v1.0.3 (2026-07-30):** Aligned specification with frozen registry baseline ($v1.0.0$); updated history log schema to 4-layer Quad-Hash stack (`results_sha256`, `input_manifest_sha256`, `params_sha256`, `pipeline_commit_sha`).
- **v1.0.2 (2026-07-30):** Restored versioning taxonomy ($v1.0.0$ / $v1.x.0$ / $v2.0.0$) and `executed_at` ratification rules.
- **v1.0.1 (2026-07-30):** Clarified 13-month rolling window calculation rules.
- **v1.0.0 (2026-07-29):** Initial baseline recurrence specification.

---

## 3. Mandatory Core Mandates

### Mandate 1 — 13-Month Rolling Calendar Window Alignment
- Every recurrent measurement MUST evaluate exactly 13 full calendar months ending on the last day of the last fully completed calendar month prior to execution.
- Telemetry data MUST be filtered with strict lower AND upper boundary timestamps (`SETTLEMENTDATE >= start_date 04:05:00` AND `SETTLEMENTDATE <= end_date+1d 04:00:00`). Partial calendar months are strictly prohibited.

### Mandate 2 — PR-Only Branch & Commit Isolation
- Recurrent automation workflows MUST execute on isolated branches named `recurrent-measurement/omn-00X-${{ github.run_id }}`.
- Machine workflows are strictly forbidden from committing directly to `main`.
- Automated PRs MUST target `main` and require explicit human review and merge ratification.

### Mandate 3 — PARAMS & Code Immutability Verification & Registry Revision Policy
- Before running analytical calculations, the runner MUST verify BOTH `PARAMS.md` (`params_sha256`) and the analytical script (`reproduce_sha256`) against the authoritative reference in `notes_registry.json`.
- If either hash is missing or differs from the registry reference, execution MUST terminate immediately (`sys.exit(1)`).
- **Registry Code Hash Revision Policy:** `results_sha256`, `params_sha256`, and DOI metadata are frozen for published $v1.0.0$ baselines. If a non-breaking maintenance patch ($v1.x.0$) is applied to `reproduce.py` (e.g. CLI path anchoring), `reproduce_sha256` in `notes_registry.json` is updated via a governance amendment PR accompanied by empirical verification that the published baseline output hash (`results_sha256`) reproduces byte-identically.

### Mandate 4 — Quad-Hash Provenance Stack
Every recurrent measurement execution MUST record a 4-layer cryptographic provenance stack:
1. **`results_sha256`**: SHA-256 hash of output `results.json`.
2. **`input_manifest_sha256`**: SHA-256 hash of `data_manifest.json`.
3. **`params_sha256`**: SHA-256 hash of `PARAMS.md`.
4. **`pipeline_commit_sha`**: Full 40-character Git commit SHA of the execution pipeline HEAD.
*(Note: `reproduce_sha256` is verified in Mandate 3 and recorded in history logs for complete code lineage).*

### Mandate 5 — Versioning & DOI Semantics
- **`v1.0.0`**: Initial published baseline (linked to original Zenodo DOI).
- **`v1.x.0`**: Recurrent 13-month rolling measurement refresh (recorded in `history/measurement_log.json`). Recurrent runs update history lineage and DO NOT mint new Zenodo DOIs.
- **`v2.0.0`**: Major structural or parameter methodology change (requires new Zenodo DOI minting).
- **DOI Revision & Erratum Policy:** Updating the `doi` field in `notes_registry.json` is strictly prohibited except via a formal, ratified erratum PR accompanied by a new Zenodo version release. If a DOI is updated, the previous published DOI MUST be preserved in the `superseded_doi` field of `notes_registry.json` for complete historical reference.

### Mandate 6 — History Log Ledger
All recurrent measurement refreshes write to `history/measurement_log.json`. Core schema required fields are:
```json
[
  {
    "version": "v1.1.0",
    "measurement_window": "2025-07-01 to 2026-07-31",
    "results_sha256": "...",
    "input_manifest_sha256": "...",
    "params_sha256": "...",
    "reproduce_sha256": "...",
    "pipeline_commit_sha": "...",
    "executed_at": "2026-08-01T04:00:00Z"
  }
]
```
*(Note: `input_manifest_sha256` refers to the SHA-256 hash of the note-level canonical manifest file `notes/00X-.../data_manifest.json`).*  
*(Optional additive fields: `packaging_commit_sha` may record the packaging commit SHA when distinct from the producing commit; `manifest_provenance` may record manifest reconstruction notes).*

### Mandate 7 — Execution Modes (Automated vs Manual Recurrence)
- **Automated Recurrence (`parameterized: True`)**: Fully parameterized pipelines (e.g. Note #001) dispatched automatically via GitHub Actions schedule or manual workflow_dispatch.
- **Manual Recurrence (`parameterized: False` OR IP/WAF Restrictions)**: Non-parameterized pipelines (e.g. Notes #003–#005) OR pipelines subject to cloud runner IP blocks (e.g. Note #002 ERCOT grid telemetry WAF) executed manually in controlled local environments using parametric changelog protocol until resolved.

### Mandate 8 — Telemetry Completeness & Boundary Verification
- The pipeline MUST verify the presence and non-zero size of ALL 13 monthly telemetry files across ALL required dataset types (`price_YYYYMM.feather` AND `scada_YYYYMM.feather`) in the explicitly passed data directory. If any telemetry file is missing or empty, the workflow MUST terminate immediately (`sys.exit(1)`).

### Mandate 9 — Zero Secret Leakage Control
- Automated workflows and scripts MUST NOT dump environment variables or print secrets. Log output must remain strictly limited to provenance hashes and execution status.

### Mandate 10 — Local Pre-Dispatch Reproduction & Synthetic Guard Isolation
- The In-Job Synthetic CI Guard verifies code execution determinism on clean checkouts by writing exclusively to an isolated temporary output directory (`--out-dir temp_out_dir`), guaranteeing zero modification of committed repository artifacts.
- Byte-level reproduction of the published baseline ($v1.0.0$) is a mandatory local pre-dispatch verification step executed prior to opening pull requests.

---

## 4. Workflow Architecture & CI Guard

```
[GitHub Cron / Dispatch]
        │
        ▼
[Check Out main Clean]
        │
        ▼
[Execute In-Job Synthetic CI Guard (Isolated Temp Out)] ──(FAIL)──► [ABORT Workflow]
        │ (PASS)
        ▼
[Verify PARAMS.md & reproduce.py Hashes vs Frozen Registry] ──(FAIL)──► [ABORT Workflow]
        │ (PASS)
        ▼
[Download & Verify 13-Month Telemetry] ──(FAIL)──► [ABORT Workflow]
        │ (PASS)
        ▼
[Execute Analysis Pipeline (cwd=note_dir, --data-dir proc_dir)]
        │
        ▼
[Append Entry to history/measurement_log.json]
        │
        ▼
[Open Pull Request for Human Ratification]
```

---

## 5. Operational Checklist & Ratification Protocol

1. **Frozen Registry:** `notes_registry.json` is immutable for published $v1.0.0$ baselines, DOIs, and baseline pipeline hashes.
2. **Dynamic Lineage:** All recurrent runs append to `history/measurement_log.json`.
3. **PR Payload:** PRs contain only `results.json`, `data_manifest.json`, `history/measurement_log.json`, and generated plots (`results/*.png`).
4. **Human Control:** The human maintainer reviews the PR diff and merges to ratify the new measurement into `main`.
