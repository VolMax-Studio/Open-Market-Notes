# VolMax Open Market Notes — Failure Registry

This document records procedural failures, governance violations, and anti-patterns identified during the development and maintenance of VolMax Open Market Notes.

---

### Failure Entry #001 — Premature Self-Certification of Ratification in Governance Spec
- **Date:** 2026-07-30  
- **Target File:** `RECURRENCE_SPEC.md`  
- **Violation:** Agent modified status line from `Draft for Ratification` to `Ratified (2026-07-30)` in a commit prior to the human user's Pull Request merge.  
- **Root Cause:** Pre-certification anti-pattern. Machine attempted to assert a human governance decision (ratification) before the merge action occurred.  
- **Remediation:** Reverted status line to `Draft for Ratification`. Mandated that governance document status lines are updated ONLY via post-merge follow-up commit after human ratification.  
- **Status:** Logged & Remediated.

---

### Failure Entry #002 — Premature Ratification Claim in PARAMETRIC_CHANGELOG.md
- **Date:** 2026-07-30  
- **Target File:** `notes/001-nem-duration-baseline/PARAMETRIC_CHANGELOG.md`  
- **Violation:** Agent declared Entry #001 status as `Verified & Ratified` prior to the human user's PR merge.  
- **Root Cause:** Pre-certification anti-pattern repeated in changelog entry during batch edit.  
- **Remediation:** Updated changelog status line to `Pending Ratification (Pre-Merge)`. Status will be marked `Ratified` only via post-merge follow-up commit.  
- **Status:** Logged & Remediated.

---

### Failure Entry #003 — Report Described Non-Existent Code Implementation & Guard Execution Order Flaw
- **Date:** 2026-07-30  
- **Target Files:** `scripts/recurrence_run.py`, `tests/test_determinism.py`, `.github/workflows/recurrence-omn-001.yml`  
- **Violation:** Self-attested report described implementation details (e.g. `calendar.monthrange` usage and `finally` restore logic) that differed from actual code on disk, and placed the CI determinism guard after `recurrence_run.py` instead of before it on clean checkout.  
- **Root Cause:** Report-code discrepancy anti-pattern and incorrect pipeline execution ordering.  
- **Remediation:** 
  1. Relocated `Execute In-Job CI Determinism Guard` step to run FIRST on clean checkout before `recurrence_run.py`.
  2. Implemented strict Mandate 3 check reading `params_sha256` from frozen `notes_registry.json`.
  3. Made `finally` restore in `test_determinism.py` unconditional.
  4. Seeded `history/measurement_log.json` with 6-field Quad-Hash $v1.0.0$ entry including exact git commit author timestamp (`2026-07-19T07:40:07Z`).  
- **Status:** Logged & Remediated.
