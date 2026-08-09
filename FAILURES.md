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
