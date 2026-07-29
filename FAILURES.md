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
