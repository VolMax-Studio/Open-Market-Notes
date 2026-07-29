# VolMax Open Market Notes — Recurrence Specification
**Version:** v1.0.3  
**Status:** Draft for Ratification  
**Date:** 2026-07-30  
**Repository:** `VolMax-Studio/Open-Market-Notes`  

---

## 1. Executive Summary

This document defines the formal operational, procedural, and cryptographic governance protocol for executing **recurrent baseline refreshes** across the VolMax Open Market Notes repository (#001–#005+).

The recurrence pipeline ensures that market observation baselines remain dynamically updated over a rolling 13-month calendar window while strictly maintaining:
1. **Audit Immutability:** Core analytical logic (`reproduce.py`), parameter definitions (`PARAMS.md`), and historical baseline registries (`notes_registry.json`) are immutable.
2. **Provenance Traceability:** Every recurrent execution appends a Quad-Hash record to `history/measurement_log.json`.
3. **Human-in-the-Loop Ratification:** Automated executions submit Pull Requests; machine code **NEVER** writes directly to `main`.

---

## 2. Mandatory Core Mandates

### Mandate 1 — 13-Month Rolling Calendar Window Alignment
- Every recurrent measurement MUST evaluate exactly 13 full calendar months ending on the last fully completed calendar day of the preceding month.
- Parcial calendar months are strictly prohibited.

### Mandate 2 — PR-Only Branch & Commit Isolation
- Recurrent automation workflows MUST execute on isolated branches named `recurrent-measurement/omn-00X-${{ github.run_id }}`.
- Machine workflows are strictly forbidden from committing directly to `main`.
- Automated PRs MUST target `main` and require explicit human review and merge ratification.

### Mandate 3 — PARAMS Immutability & Hash Verification
- Before running analytical calculations, the runner MUST verify `PARAMS.md` against the authoritative `params_sha256` stored in `notes_registry.json`.
- If `PARAMS.md` has been modified or the hash differs, execution MUST terminate immediately (`sys.exit(1)`).

### Mandate 4 — Quad-Hash Provenance Stack
Every recurrent measurement execution MUST record a 4-layer cryptographic provenance stack:
1. **`results_sha256`**: SHA-256 hash of the output `results.json`.
2. **`input_manifest_sha256`**: SHA-256 hash of `data_manifest.json`.
3. **`params_sha256`**: SHA-256 hash of `PARAMS.md`.
4. **`pipeline_commit_sha`**: Full 40-character Git commit SHA of the execution pipeline HEAD.

### Mandate 5 — Versioning Taxonomy
- **`v1.0.0`**: Initial published baseline (linked to original Zenodo DOI).
- **`v1.x.0`**: Recurrent 13-month rolling measurement refresh (recorded in `history/measurement_log.json`).
- **`v2.0.0`**: Major structural or parameter methodology change (requires new Zenodo DOI minting).

### Mandate 6 — History Log Ledger
All recurrent measurement refreshes write to `history/measurement_log.json`:
```json
[
  {
    "version": "v1.1.0",
    "measurement_window": "2025-07-01 to 2026-07-31",
    "results_sha256": "...",
    "input_manifest_sha256": "...",
    "params_sha256": "...",
    "pipeline_commit_sha": "...",
    "executed_at": "2026-08-01T04:00:00Z"
  }
]
```

### Mandate 7 — Note Readiness & Parameterization
- **Note #001 (NEM Duration Baseline)** is the sole date-parameterized pilot note.
- **Notes #002–#005** require date parameterization PRs before automated recurrence dispatch can be enabled (`parameterized: False`).

### Mandate 8 — Telemetry Completeness & Boundary Verification
- The pipeline MUST verify the presence and non-zero size of all 13 monthly telemetry files. If telemetry is missing or incomplete, the workflow MUST terminate immediately (`sys.exit(1)`).

---

## 3. Workflow Architecture

```
[GitHub Cron / Dispatch]
        │
        ▼
[Check Out main Clean]
        │
        ▼
[Execute In-Job Synthetic CI Guard] ──(FAIL)──► [ABORT Workflow]
        │ (PASS)
        ▼
[Verify PARAMS.md Hash vs Frozen Registry] ──(FAIL)──► [ABORT Workflow]
        │ (PASS)
        ▼
[Download & Verify 13-Month Telemetry] ──(FAIL)──► [ABORT Workflow]
        │ (PASS)
        ▼
[Execute Analysis Pipeline (cwd=note_dir)]
        │
        ▼
[Append Entry to history/measurement_log.json]
        │
        ▼
[Open Pull Request for Human Ratification]
```

---

## 4. Operational Checklist & Ratification Protocol

1. **Frozen Registry:** `notes_registry.json` is immutable for published $v1.0.0$ baselines and DOIs.
2. **Dynamic Lineage:** All recurrent runs append to `history/measurement_log.json`.
3. **PR Payload:** PRs contain only `results.json`, `data_manifest.json`, `history/measurement_log.json`, and generated plots (`results/*.png`).
4. **Human Control:** The human maintainer reviews the PR diff and merges to ratify the new measurement into `main`.
