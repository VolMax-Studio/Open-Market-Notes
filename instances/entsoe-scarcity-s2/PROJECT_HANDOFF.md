# Project Handoff

## Identity

Project: entsoe-scarcity-s2
Repository: VolMax-Studio/Open-Market-Notes
Branch: instances/entsoe-scarcity-s2
Current commit: Pending draft v3 commit
Preregistration commit: Pending Gate pass and Operator freeze (PREREG_SHA_v3)
Latest run ID: run-002-confirmatory (Halted outside taxonomy on PKZip container format)
Next run ID: run-003-confirmatory (NOT YET AUTHORIZED)
Deadline: 2026-09-12

## Phase

Specification Draft v3 (PRE-EXECUTION GATE DRAFT) — Execution State: NOT AUTHORIZED

Portfolio status: ACTIVE / DEADLINE PRIORITY

Architecture:
Pinned-vintage ENTSO-E Transparency Platform / IEC 62325 raw-document architecture with PKZip transport container extraction.

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
- Raw HTTP response bodies from run-002 captured under `evidence/runs/run-002-confirmatory/raw/`.

Hashes / commit SHA:
- Preserved run-002 evidence in `evidence/runs/run-002-confirmatory/` (Evidence commit: `1a53d688b1f41bf56ca01062b0c3ffb9cf1ba895`).

## Current results

- run-001-confirmatory: Permanently classified as `Exploratory (Protocol Non-Compliance)` per FAILURES #003.
- run-002-confirmatory: Permanently classified as `Halted outside taxonomy` per FAILURES #004 (Clean 12/12 HTTP 200 acquisition; interpretation halted on PKZip container format).
- run-003-confirmatory: Not yet authorized. Awaiting pre-execution Gate review of Draft v3 specification.

## Gate status

Gate model/person: Claude
Gate outcome: PENDING PRE-EXECUTION GATE REVIEW (Draft v3)
Blocking findings:
None pending review.

## Next single action

Submit Draft v3 commit to Claude for pre-execution Gate review.
