# Project Handoff

## Identity

Project: entsoe-scarcity-s2
Repository: VolMax-Studio/Open-Market-Notes
Branch: instances/entsoe-scarcity-s2
Current commit: Pending evidence commit for run-004
Preregistration commit: 88c7959e3dae0eb8cb5ad49640424d368e625eea (PREREG_SHA_v4)
Latest run ID: run-004-confirmatory (Target S evaluated: 6/6 zones S-FAIL on missing intervals; 0 duplicates; Target R blocked)
Next run ID: Pending post-execution Gate review
Deadline: 2026-09-12

## Phase

Post-Execution Evidence Review (run-004-confirmatory) — Execution State: SPREMNO ZA GEJT

Portfolio status: ACTIVE / DEADLINE PRIORITY

Architecture:
Pinned-vintage ENTSO-E Transparency Platform / IEC 62325 raw-document architecture with PKZip transport container extraction, multi-period iteration, unconditional A04 shortage price category filtering, and source vintage integrity verification.

Audit Class:
Internal self-reproduction and vintage-stability audit of published VolMax Open Market Note #003 findings.  
Claimant: VolMax Studio.

This is a new instance. It is not a repaired continuation of entsoe-scarcity-s1.

## Exact claim under test

Claimant: VolMax Studio (historical published finding in Open Market Note #003 / July 2026 probe)
Claim: At a single pinned post-freeze ENTSO-E Transparency Platform acquisition batch, the July-2026 six-zone European scarcity classification published by VolMax can be reconstructed from the raw A85 imbalance-price documents without silent interval repair, while satisfying an exact MTU population invariant.
Source: Historical VolMax Note #003 probe and ENTSO-E Transparency Platform API.
Source location: ENTSO-E REST API DocumentType A85 (Area EICs: AT, BE, DK-1, DK-2, FR, NL).

## Evidence boundary

Public artifacts:
- ENTSO-E Transparency Platform API (`https://web-api.tp.entsoe.eu/api`, DocumentType A85 / processType A16 / IEC 62325 XML / PKZip container).
- Preserved raw HTTP response bodies from run-003 reused in run-004 under `evidence/runs/run-004-confirmatory/raw/` with verified bit-for-bit SHA-256 integrity.

## Current results

- run-001-confirmatory: Permanently classified as `Exploratory (Protocol Non-Compliance)` per FAILURES #003.
- run-002-confirmatory: Permanently classified as `Halted outside taxonomy` per FAILURES #004.
- run-003-confirmatory: Permanently classified as `Acquisition valid — interpretation invalid` per FAILURES #005 (Complete 12/12 HTTP 200 raw vintage preserved).
- run-004-confirmatory: Executed offline against run-003 vintage. Target S evaluated for all 6 zones: 6/6 S-FAIL due to true source missing intervals (0 duplicates, 0 unexpected). Target R blocked by Target S failure.

## Gate status

Gate model/person: Claude
Gate outcome: PENDING POST-EXECUTION GATE REVIEW (run-004-confirmatory)
Blocking findings:
None.

## Next single action

Submit run-004-confirmatory evidence package to Claude for Post-Execution Gate review.
