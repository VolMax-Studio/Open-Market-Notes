# Project Handoff

## Identity

Project: entsoe-scarcity-s2
Repository: VolMax-Studio/Open-Market-Notes
Branch: instances/entsoe-scarcity-s2
Current commit: Pending freeze commit (PREREG_SHA_v2)
Preregistration commit: Pending freeze commit (PREREG_SHA_v2)
Latest run ID: run-001-confirmatory (Exploratory / Protocol Non-Compliance)
Next run ID: run-002-confirmatory (AUTHORIZED)
Deadline: 2026-09-12

## Phase

Preregistered v2 (FROZEN) — Execution State: AUTHORIZED FOR run-002-confirmatory

Portfolio status: ACTIVE / DEADLINE PRIORITY

Architecture:
Pinned-vintage ENTSO-E Transparency Platform / IEC 62325 raw-document architecture.

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
- ENTSO-E Transparency Platform API (`https://web-api.tp.entsoe.eu/api`, DocumentType A85 / processType A16 / IEC 62325 XML).
- Raw HTTP response bodies from run-001 captured under `evidence/runs/run-001-confirmatory/raw/`.

Hashes / commit SHA:
- Preserved run-001 evidence in `evidence/runs/run-001-confirmatory/`.

## Current results

- run-001-confirmatory: Permanently classified as `Exploratory (Protocol Non-Compliance)` per FAILURES #003 due to post-freeze harness authorship and incorrect area identifier for Belgium (`10YBE----------X` vs `10YBE----------2`).
- run-002-confirmatory: AUTHORIZED following Claude Gate PASS at draft `ac33cdc` and Operator acceptance.

## Gate status

Gate model/person: Claude
Gate outcome: GATE_PASS (at draft `ac33cdc`)
Blocking findings:
None. Operator accepted specification.

## Next single action

Ananke executes official run-002-confirmatory under PREREG_SHA_v2.
