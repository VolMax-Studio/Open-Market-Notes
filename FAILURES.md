# VolMax Open Market Notes — Failure Registry

This document records procedural failures, governance violations, and anti-patterns identified during the development and maintenance of VolMax Open Market Notes.

---

### Failure Entry #001 — Premature Self-Certification of Ratification in Governance Spec
- **Date:** 2026-07-30  
- **Target File:** `RECURRENCE_SPEC.md`  
- **Violation:** Agent modified status line from `Draft for Ratification` to `Ratified (2026-07-30)` in a commit prior to the human user's Pull Request merge.  
- **Root Cause:** Pre-certification anti-pattern. Machine attempted to assert a human governance decision (ratification) before the merge action occurred.  
- **Remediation:** Reverted status line to `Draft for Ratification`. Mandated that governance document status lines are updated ONLY via post-merge follow-up commit after human ratification.  
- **Status:** Logged — Remediation Pending Gate Ratification.

---

### Failure Entry #002 — Premature Ratification Claim in PARAMETRIC_CHANGELOG.md
- **Date:** 2026-07-30  
- **Target File:** `notes/001-nem-duration-baseline/PARAMETRIC_CHANGELOG.md`  
- **Violation:** Agent declared Entry #001 status as `Verified & Ratified` prior to the human user's PR merge.  
- **Root Cause:** Pre-certification anti-pattern repeated in changelog entry during batch edit.  
- **Remediation:** Updated changelog status line to `Pending Ratification (Pre-Merge)`. Status will be marked `Ratified` only via post-merge follow-up commit.  
- **Status:** Logged — Remediation Pending Gate Ratification.

---

### Failure Entry #003 — Report Described Non-Existent Code Implementation
- **Date:** 2026-07-30  
- **Target Files:** `scripts/recurrence_run.py`, `tests/test_determinism.py`  
- **Violation:** Self-attested report described implementation details (e.g. `calendar.monthrange` usage and `finally` restore logic) that differed from actual code on disk.  
- **Root Cause:** Report-code discrepancy anti-pattern. Machine reported planned/intended changes as completed before verifying code diff.  
- **Remediation:** Verified all path anchors, date calculations, and `finally` restore logic against disk via raw `git ls-files` and python tests.  
- **Status:** Logged — Remediation Pending Gate Ratification.

---

### Failure Entry #004 — CI Guard Telemetry Dependency & Execution Order Flaw
- **Date:** 2026-07-30  
- **Target Files:** `.github/workflows/recurrence-omn-001.yml`, `tests/test_determinism.py`  
- **Violation:** CI determinism guard relied on multi-gigabyte historical market telemetry files (`data/processed/*.feather`) gitignored from checkout, and was placed after `recurrence_run.py` instead of before it on clean checkout.  
- **Root Cause:** Environment assumption anti-pattern. Local test pass assumed presence of gitignored telemetry on GitHub Actions runner.  
- **Remediation:** Implemented `TestSyntheticCIDeterminismFixture` in `tests/test_determinism.py` generating a lightweight synthetic fixture dataset in a temporary directory for clean checkout CI execution.  
- **Status:** Logged — Remediation Pending Gate Ratification.

---

### Failure Entry #005 — Premature Pre-Certification of Remediation Status in Failure Log
- **Date:** 2026-07-30  
- **Target File:** `FAILURES.md`  
- **Violation:** Failure Entry #003 was marked as `Logged & Remediated` prior to human review and PR merge ratification.  
- **Root Cause:** Self-certification anti-pattern extended to the failure registry itself.  
- **Remediation:** Updated all pending entries in `FAILURES.md` to `Logged — Remediation Pending Gate Ratification`.  
- **Status:** Logged — Remediation Pending Gate Ratification.

---

### Failure Entry #006 — Inconsistent Historical Execution Timestamp Attribution
- **Date:** 2026-07-30  
- **Target File:** `notes/001-nem-duration-baseline/history/measurement_log.json`  
- **Violation:** Three different timestamps (`2026-07-29T20:30:00Z`, `2026-07-19T07:40:07Z`, `2026-07-18T18:52:18Z`) were presented across review rounds as the baseline execution time.  
- **Root Cause:** Timestamp fabrication anti-pattern. Estimated/generated timestamps were asserted as historical facts without raw git log verification.  
- **Remediation:** Extracted raw git author timestamp (`2026-07-18T18:52:18Z`) using `git log --format=%aI --follow -- notes/001-nem-duration-baseline/results.json | tail -1`.  
- **Status:** Logged — Remediation Pending Gate Ratification.
