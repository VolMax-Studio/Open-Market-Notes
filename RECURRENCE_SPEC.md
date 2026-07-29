# VolMax Open Market Notes — Recurrence Specification v1.0.0

> **Class of Work:** VolMax Governance Specification & Automation Standard  
> **Status:** Draft for Ratification  
> **Version:** 1.0.0  
> **Target Scope:** All VolMax Open Market Notes (#001–#010+)  
> **Enforcement Level:** Mandatory for all automated `workflow_dispatch` and scheduled `cron` executions  

---

## 1. Executive Summary

This specification governs the automated, periodic recalculation ("recurrence") of empirical market measurement baselines across all VolMax Open Market Notes.

The core objective of the VolMax Observatory is to transform point-in-time descriptive analytical notes into **living, reproducible market instruments**. Recurrence builds a continuous **Measurement History** ($v1.0 \rightarrow v1.1 \rightarrow v2.0$), allowing the market to observe how scarcity duration, BESS charging availability, and cross-border flow dynamics evolve over time under identical analytical parameters.

---

## 2. Core Operational Mandates

### Mandate 1: Rolling Measurement Window Rule
- Automated runs calculate market metrics over a **13-Month Rolling Window** ending on the last completed calendar day prior to execution (e.g., `1 July 2025 – 31 July 2026`).
- The rolling window MUST retain full 15-minute / 30-minute / 5-minute telemetry resolution across the entire 13-month span to guarantee seasonal comparability across full annual cycles.

### Mandate 2: Human-in-the-Loop PR Enforcement (Zero Direct Commit to Main)
- Automated GitHub Action workflows **MUST NEVER commit directly to `main`**.
- Every workflow run generates an isolated git branch (`recurrent-measurement/omn-00X-YYYYMMDD`) and opens a Pull Request against `main`.
- The Pull Request MUST contain:
  1. Updated `results.json` and metric figures.
  2. Updated `data_manifest.json` with fresh input file SHA-256 hashes.
  3. A mechanical PR diff summary highlighting changes in key metrics relative to the previous ratified baseline.
- Human review and manual PR merge constitute the formal ratification of every new measurement point.

### Mandate 3: Parameter & Metric Immutability
- Automated workflows are **STRICTLY FORBIDDEN** from modifying:
  - Metric formulas, mathematical definitions, or bridging rules.
  - Scarcity price thresholds ($\ge \$100/\text{MWh}$, $\ge \$300/\text{MWh}$, $\ge €100/\text{MWh}$).
  - Charging price thresholds ($\le \$25/\text{MWh}$, $\le €0/\text{MWh}$).
  - Fixed parameter definitions recorded in `PARAMS.md`.
- Workflow scripts may ONLY update the date window parameters strictly as authorized by this specification.

### Mandate 4: Quad-Hash Provenance Stack Preservation
Every recurrent execution MUST construct and verify the 4-layer provenance chain:
1. **Input Telemetry Hash:** SHA-256 manifest of raw telemetry files recorded in `data_manifest.json`.
2. **Frozen Pipeline Hash:** Commit SHA of the execution codebase.
3. **Parametric Ledger Hash:** Hash of `PARAMS.md`.
4. **Results Output Hash:** SHA-256 hash of `results.json` recorded in `notes_registry.json` as `results_sha256`.

### Mandate 5: Versioning Taxonomy
- **`v1.0.0`**: Initial Baseline Release (Minted Zenodo DOI).
- **`v1.x.0`**: Periodic Recurrent Measurement Refresh (Monthly / Quarterly rolling update via PR).
- **`v2.0.0`**: Annual Milestone Measurement Release (Minted Zenodo DOI #2).

### Mandate 6: Zero Secret Leakage Policy
- API credentials (ENTSO-E Security Tokens, GridStatus API Keys, GitHub Access Tokens) supplied via GitHub Secrets MUST NEVER be printed, echoed, or dumped into standard logs or stdout/stderr under any circumstances.

---

## 3. Workflow Execution Architecture

```
[ Scheduled Cron / Manual Dispatch ]
                 │
                 ▼
[ GitHub Action Runner (Isolated Environment) ]
                 │
                 ├── 1. Checkout main frozen codebase
                 ├── 2. Download telemetry for rolling window
                 ├── 3. Hash inputs into data_manifest.json
                 ├── 4. Execute frozen pipeline (run_analysis.py)
                 ├── 5. Generate fresh results.json & plots
                 └── 6. Compare metrics against current main
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

- `[ ]` `results.json` produced cleanly with matching `results_sha256`.
- `[ ]` `data_manifest.json` updated with valid SHA-256 input hashes.
- `[ ]` Zero modified lines in `PARAMS.md` or core calculation logic.
- `[ ]` All generated plot figures match defined aspect ratios and formatting standards.
- `[ ]` All tests in `pytest` suite pass without warnings.

---

*VolMax Studio Lab · Recurrence Specification v1.0.0 (Governance & Automation Standard)*
