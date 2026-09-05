# Failures & Non-Compliances Log

## #001 — Methodological Defect: Monthly Chunking and Boundary Truncation Vulnerability
- **Date:** 2026-09-04
- **Severity:** Architectural Flaw
- **Description:** Preliminary approach in s1 relied on month-by-month chunking that did not protect against timezone/DST boundary clipping and MTU interval losses at monthly seams.
- **Resolution:** Formal ABORT by human operator decision. Instance abandoned and superseded by entsoe-scarcity-s2 on vintage architecture.
