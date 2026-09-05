# Project Handoff

## Identity

Project: entsoe-scarcity-s2
Repository: VolMax-Studio/Open-Market-Notes
Branch: instances/entsoe-scarcity-s2
Current commit: Pending freeze v4 commit
Preregistration commit: Pending freeze v4 commit (PREREG_SHA_v4)
Latest run ID: run-003-confirmatory (Acquisition valid — interpretation invalid)
Next run ID: run-004-confirmatory (AUTHORIZED — Offline interpretation over run-003 raw vintage)
Deadline: 2026-09-12

## Phase

Specification Freeze v4 (PREREG_SHA_v4) — Execution State: AUTHORIZED

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
- Preserved raw HTTP response bodies from run-003 captured under `evidence/runs/run-003-confirmatory/raw/` (Evidence commit: `9a68ed467f56cf8f1155986fc0d17676c66cf1d2`).

## Current results

- run-001-confirmatory: Permanently classified as `Exploratory (Protocol Non-Compliance)` per FAILURES #003.
- run-002-confirmatory: Permanently classified as `Halted outside taxonomy` per FAILURES #004.
- run-003-confirmatory: Permanently classified as `Acquisition valid — interpretation invalid` per FAILURES #005 (Complete 12/12 HTTP 200 raw vintage preserved).
- run-004-confirmatory: AUTHORIZED for execution over preserved run-003 raw vintage.

## Gate status

Gate model/person: Claude
Gate outcome: GATE_PASS (Draft v4 @ 9a6cb25)
Blocking findings:
None.

## Next single action

Execute run-004-confirmatory under Ananke supervision.
