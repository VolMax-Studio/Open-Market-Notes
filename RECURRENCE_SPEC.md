# VolMax Open Market Notes — Recurrence Specification v1.0.2

> **Class of Work:** VolMax Governance Specification & Automation Standard  
> **Status:** Draft for Ratification (v1.0.2 Gate Remediation)  
> **Version:** 1.0.2  
> **Target Scope:** All VolMax Open Market Notes (#001–#010+)  
> **Enforcement Level:** Mandatory for all automated `workflow_dispatch` and scheduled `cron` executions  

---

## 1. Executive Summary

This specification governs the automated and semi-automated recalculation ("recurrence") of empirical market measurement baselines across all VolMax Open Market Notes.

The core objective of the VolMax Observatory is to transform point-in-time descriptive analytical notes into **living, reproducible market instruments**. Recurrence builds a continuous **Measurement History** ($v1.0.0 \rightarrow v1.1.0 \rightarrow v2.0.0$), allowing the market to observe how scarcity duration, BESS charging availability, and cross-border flow dynamics evolve over time under identical analytical parameters.

---

## 2. Core Operational Mandates

### Mandate 1: Rolling Measurement Window Rule
- Recurrent measurement runs calculate market metrics over **13 full calendar months, ending on the last fully completed calendar month prior to execution** (e.g., execution on 15 August 2026 calculates the window `1 July 2025 – 31 July 2026`).
- The rolling window MUST retain full telemetry resolution (15-minute / 30-minute / 5-minute) across the entire 13-month span to guarantee seasonal comparability across full annual cycles.

### Mandate 2: Human-in-the-Loop PR Enforcement (Zero Direct Commit to Main)
- Automated GitHub Action workflows **MUST NEVER commit directly to `main`**.
- Every workflow run generates an isolated git branch (`recurrent-measurement/omn-00X-YYYYMMDD`) and opens a Pull Request against `main`.
- The Pull Request MUST contain:
  1. Updated `notes_registry.json` (with fresh `results_sha256`).
  2. Updated `results.json` and metric figures.
  3. Updated `data_manifest.json` with fresh input file SHA-256 hashes.
  4. Appended measurement record entry in `history/measurement_log.json`.
  5. A mechanical PR diff summary highlighting metric changes relative to the previous ratified baseline.
- Human review and manual PR merge constitute the formal ratification of every new measurement point.

### Mandate 3: Strict Parameter & Metric Immutability
- Governance documents reference single sources of truth and MUST NOT duplicate analytical parameters.
- Workflows MUST preserve all scarcity and charging price thresholds **exactly as recorded in each note's frozen `PARAMS.md`**.
- Workflows are **STRICTLY FORBIDDEN** from modifying:
  - Metric formulas, mathematical definitions, or bridging rules.
  - Price thresholds recorded in `PARAMS.md`.
  - Fixed parameter ledgers or methodology documentation.

### Mandate 4: Quad-Hash Provenance Stack Preservation
Every recurrent execution MUST construct and verify the 4-layer provenance chain:
1. **Input Telemetry Hash:** SHA-256 manifest of raw telemetry files recorded in `data_manifest.json`.
2. **Frozen Pipeline Hash:** Commit SHA of the execution codebase on `main`.
3. **Parametric Ledger Hash:** SHA-256 hash of `PARAMS.md`.
4. **Results Output Hash:** SHA-256 hash of `results.json` recorded in `notes_registry.json` as `results_sha256`.

### Mandate 5: Versioning Taxonomy
- **`v1.0.0`**: Initial Baseline Release (Minted Zenodo DOI #1).
- **`v1.x.0`**: Periodic Recurrent Measurement Refresh (Monthly / Quarterly rolling update ratified via PR merge).
- **`v2.0.0`**: Annual Milestone Measurement Release (Triggers minting of new Zenodo DOI #2).

### Mandate 6: Measurement History Persistence Architecture
To prevent past measurement points from being lost when `results.json` is updated, every note directory MUST maintain a persistent `history/measurement_log.json` ledger.
Each workflow run appends an immutable JSON record using the timestamp of execution (`executed_at`):
```json
{
  "version": "v1.1.0",
  "measurement_window": "YYYY-MM-01 to YYYY-MM-31",
  "results_sha256": "<sha256-hash-of-results-json>",
  "input_manifest_sha256": "<sha256-hash-of-data-manifest>",
  "executed_at": "YYYY-MM-DDTHH:MM:SSZ"
}
```
*Note: Ratification is established solely by the human merge commit in git history, which records the author's identity and timestamp.*

### Mandate 7: Execution Modes (Automated vs. Manual Recurrence)
Notes operate under one of two legal execution modes depending on upstream provider infrastructure:
- **`Automated Recurrence`** (e.g., #001 NEM, #003/#004 ENTSO-E/Elexon): Executed via GitHub Actions `workflow_dispatch` / `cron`.
- **`Manual Recurrence`** (e.g., #002 ERCOT via GridStatus WAF): Executed manually on authorized local environments when runner IPs are blocked by Web Application Firewalls (WAF), submitting results via identical Pull Request workflows.

### Mandate 8: Telemetry Failure & Data Boundary Rule
- If primary data acquisition fails, times out, or returns incomplete date coverage for the target 13-month window, **the workflow MUST abort immediately with an exit code error**.
- The workflow **MUST NOT open a Pull Request** for incomplete or partial telemetry windows.

### Mandate 9: Zero Secret Leakage Policy
- API credentials (ENTSO-E Security Tokens, GridStatus API Keys, GitHub Access Tokens) supplied via GitHub Secrets MUST NEVER be printed, echoed, or dumped into standard logs or stdout/stderr under any circumstances.

---

## 3. Workflow Execution Architecture

```
[ Scheduled Cron / Manual Dispatch ]
                 │
                 ▼
[ Runner Environment (Automated or Manual Recurrence) ]
                 │
                 ├── 1. Verify telemetry availability for target 13-month window
                 │      └─> [ABORT if incomplete / API failure]
                 ├── 2. Checkout main frozen codebase
                 ├── 3. Download telemetry & hash inputs into data_manifest.json
                 ├── 4. Execute frozen pipeline (run_analysis.py)
                 ├── 5. Generate fresh results.json & plots
                 └── 6. Append entry to history/measurement_log.json (executed_at)
                 │
                 ▼
[ Open Branch & Pull Request (recurrent-measurement/omn-XXX) ]
                 │
                 ▼
[ Human Review & Ratification (Click Merge) ]
                 │
                 ▼
[ Automated GitHub Pages Re-Render (Observatory Dashboard) ]
```

---

## 4. Verification Checklist for Recurrence PR Approval

Before merging a recurrent measurement PR into `main`, the following automated checks MUST pass:

- `[ ]` The `results_sha256` entry in `notes_registry.json` within the PR must exactly match the SHA-256 hash of the freshly produced `results.json` file in that same PR.
- `[ ]` `data_manifest.json` updated with valid SHA-256 input hashes for the entire 13-month window.
- `[ ]` `history/measurement_log.json` correctly appended with the new measurement record using `executed_at`.
- `[ ]` Zero modified lines in `PARAMS.md` or core calculation logic.

---

*VolMax Studio Lab · Recurrence Specification v1.0.2 (Governance & Automation Standard)*
