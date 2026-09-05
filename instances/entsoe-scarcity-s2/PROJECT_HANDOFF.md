# Project Handoff

## Identity

Project: entsoe-scarcity-s2
Repository: VolMax-Studio/Open-Market-Notes
Branch: instances/entsoe-scarcity-s2
Current commit: 1f6f52d9c6029d105e8a4b80499c7c0553c7525b
Preregistration commit: 1f6f52d9c6029d105e8a4b80499c7c0553c7525b
Latest run ID: run-001-confirmatory
Deadline: 2026-09-12

## Phase

Preregistered (FROZEN) — Execution State: HALT

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
- Raw HTTP response bodies captured under `evidence/runs/run-001-confirmatory/raw/`.

Hashes / DOI / commit SHA:
See `evidence/runs/run-001-confirmatory/outputs.sha256`.

## Current results

Measured: none (halted on request 3/12)
Derived: none
Scope findings:
- Request 1 (AT baseline 334d): HTTP 200 OK (567,572 bytes)
- Request 2 (AT target 31d): HTTP 200 OK (55,981 bytes)
- Request 3 (BE baseline 334d): HTTP 200 Acknowledgement_MarketDocument Reason 999: "No matching data found for Data item IMBALANCE_PRICES_R3 [17.1.G] (10YBE----------X) and interval 2025-07-31T22:00:00Z/2026-06-30T22:00:00Z."
Protocol outcome: HALT: request contract unsupported

## Gate status

Gate model/person: Claude
Gate outcome: PENDING POST-EXECUTION GATE
Blocking findings:
Official run halted per preregistered HALT rule (§14).

## Next single action

Submit run-001-confirmatory evidence packet to Claude for post-execution Gate review.
