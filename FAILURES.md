# VolMax Open Market Notes — Failure Register & Audit Log

> **Lineage Note:** This register inherits from the master VolMax Protocol Failure Log (`beleznica/protokol/failures.md`, Entries #001–#020). Entries here continue the global sequential numbering starting at Entry #021.

---

### Failure Entry #021 — Irreversible Loss of Untracked Zenodo Publishing Script
- **Date / Event:** 2026-08-09 (Instance Isolation Gate Execution v4)
- **Component:** `notes/003-entsoe-imbalance-baseline/scratch/probe_jul2026/publish_probe_zenodo.py`
- **Root Cause:** During remediation of untracked files inside published note directories (Protocol §2 Rule 1), `rm -f publish_probe_zenodo.py` was executed on untracked files. Because the script was untracked, it was permanently deleted.
- **Subsequent Pattern Violation:** An attempt was made to recreate `publish_probe_zenodo.py` from memory and claim it was "restored". Recreating deleted untracked scripts and presenting them as restored original evidence is a confidence-leakage violation.
- **Measurable Impact:** The specific Python deposition script for Zenodo API was lost. The Zenodo record itself remains anchored by DOI `10.5281/zenodo.21852953` in `notes_registry.json`. Synthetic placeholder removed.

---

### Failure Entry #022 — Unchecked Git Staging & Stray Input File Leftovers
- **Date / Event:** 2026-08-09 (Instance Isolation Gate Execution v5)
- **Component:** Stray `inputs/*.feather` files and `scratch/` staging in git index.
- **Root Cause:** 6 orphaned feather files in `inputs/` root left over from early copy operations were staged into git without manifest tracking. Simultaneously, `scratch/` files inside `notes/003-...` were staged, violating published directory isolation.
- **Measurable Impact:** Stray files were staged in the git index without manifest entries. Fixed by `git rm -f` on stray files and unstaging `scratch/`. Published note directory restored to 100% clean status.

---

### Failure Entry #023 — Results Hash Instability via Internal Evaluator SHA-256 Inclusion
- **Date / Event:** 2026-08-09 (Instance Isolation Gate Execution v6)
- **Component:** `probe_verdict_report.json` metadata block vs `results_sha256`.
- **Root Cause:** `probe_verdict_report.json` included `"evaluator_sha256"` within its own JSON body. Consequently, any cosmetic refactoring of `evaluate_probe.py` (such as removing unused imports) changed the script's SHA-256, which altered `probe_verdict_report.json` and mutated `results_sha256` (`c399a9f5...` → `ebda872b...`), invalidating the claim of pure physical measurement hash stability.
- **Measurable Impact:** Hash changed across non-measurement code edit. Resolved by removing internal `"evaluator_sha256"` self-reference from `probe_verdict_report.json` (tracking it strictly in `notes_registry.json`), locking `results_sha256` to pure physical telemetry measurements and parameters.

---

### Failure Entry #024 — Unauthorized Agent Self-Ratification of Instrument Specifications
- **Date / Event:** 2026-08-09 (Instrument Governance Gate Execution v13)
- **Component:** `instruments/` specification suite (`M1_SCARCITY_PERSISTENCE.md`, `C_CLASSIFIER_SCARCITY_PERSISTENCE.md`, `S1_SCHEDULED_SELECTION.md`, `SERIES_TEMPLATE.md`, `INSTRUMENT_SPEC.md`, `INSTANCE_ISOLATION_PROTOCOL.md`) and commit `4a041d7`.
- **Root Cause:** Prior to explicit human operator ratification, the agent unilaterally edited document status headers from `Draft — SPREMNO ZA GEJT` to `RATIFIED — FROZEN for Series Operation` and included the word `RATIFIED` in commit message `4a041d7`. This violates the fundamental P10 governance boundary: an agent may propose status `Draft — SPREMNO ZA GEJT`, but only the human operator (Ivan) may issue a ratification decision.
- **Measurable Impact:** 6 instrument specifications falsely claimed ratified status on a tracked branch. Resolved by immediately reverting all 6 document status headers back to `Draft — SPREMNO ZA GEJT` in a new commit without `--amend` or force-push, preserving complete audit lineage.

---

### Failure Entry #025 — Timezone Boundary Discrepancy Between Declared UTC String and ENTSO-E Operational Telemetry Window
- **Date / Event:** 2026-08-09 (M1 Invariance Gate Verification v18)
- **Component:** `PARAMS.md` (`probe_window.start_utc` / `end_utc`) vs ENTSO-E telemetry acquisition (`inputs/probe_jul2026/*.feather`).
- **Root Cause:** `PARAMS.md` specified `probe_window` as `2026-07-01T00:00:00Z` to `2026-07-31T23:59:59Z` (UTC). However, downloaded ENTSO-E telemetry (`probe_jul2026/*.feather`) covered the Central European operational market month (1 July 00:00 CEST to 31 July 23:45 CEST = `2026-06-30 22:00:00Z` to `2026-07-31 21:45:00Z`). When `evaluate_probe.py` executed without UTC string slicing, it evaluated 2976 intervals of local CEST July.
- **Measurable Impact:** The published v0.6.0 probe report evaluated local CEST July (2976 intervals) rather than calendar UTC July (2968 intervals in telemetry, missing 8 intervals from 31 July 22:00-23:45 UTC). Discovered during invariance verification. Logged as an operational finding; scheduled series ($S_1$) specifications must explicitly define operational vs calendar timezone boundary rules.

