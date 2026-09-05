# Failures & Non-Compliances Log

## #001 — Methodological Defect: Monthly Chunking and Boundary Truncation Vulnerability
- **Date:** 2026-09-04
- **Severity:** Architectural Flaw
- **Description:** Preliminary approach in s1 relied on month-by-month chunking that did not protect against timezone/DST boundary clipping and MTU interval losses at monthly seams.
- **Resolution:** Formal ABORT by human operator decision. Instance abandoned and superseded by entsoe-scarcity-s2 on vintage architecture.

## #002 — Packaging Policy Non-Compliance: Raw Source Artifacts Committed to Public Repository
- **Date:** 2026-09-05 (Identified during Gate review of s2)
- **Severity:** Repository Packaging Policy Violation
- **Observed:** 7 raw binary .feather files (~6.06 MB) were tracked under `instances/entsoe-scarcity-s1/inputs/` (and additional legacy feather files exist across historical note/instance directories in Open-Market-Notes).
- **Expected:** Manifest-and-hash-only public repository packaging.
- **Disposition:** Removed from `instances/entsoe-scarcity-s1/inputs/` in current branch; historical Git commits remain in Git history pending broader repo-wide licensing and cleanup review.
- **Affected Scientific Claims:** None (s1 carries verdict = null; already Abandoned).
