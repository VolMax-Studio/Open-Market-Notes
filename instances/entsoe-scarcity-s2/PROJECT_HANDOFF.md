# Project Handoff

## Identity

Project: entsoe-scarcity-s2
Repository: VolMax-Studio/Open-Market-Notes
Branch: instances/entsoe-scarcity-s2
Current commit: [track via git rev-parse HEAD]
Preregistration commit: null
Latest run ID: null
Deadline: 2026-09-12

## Phase

Candidate (SPREMNO ZA CLAUDE PRE-EXECUTION GATE)

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
Published number/text:
FR: approx 31.8%, NL: approx 23.3%, BE: approx 18.8%, AT: approx 18.4%, DK-1: approx 17.5% (Elevated >= 15%), DK-2: approx 11.3% (Not Elevated < 15%). Published qualitative result: 5 of 6 zones elevated.

## Evidence boundary

Public artifacts:
- ENTSO-E Transparency Platform API (`https://web-api.tp.entsoe.eu/api`, DocumentType A85 / processType A16 / IEC 62325 XML).
- Raw HTTP response bodies captured at T_vintage within the official 12-request acquisition batch.
- Pinned EIC codes (ControlArea_Domain): 10YAT-APG------L (AT), 10YBE----------X (BE), 10YDK-1--------W (DK_1), 10YDK-2--------T (DK_2), 10YFR-RTE------C (FR), 10YNL----------L (NL).

Hashes / DOI / commit SHA:
Raw response hashes captured at execution post-freeze under PREREG_SHA.

Missing artifacts:
Enumerate explicitly during acquisition; zero silent imputation.

Evidence owner:
ENTSO-E (source publisher) / TSOs (originating telemetry).

Independence class:
Self-reproduction audit (claimant = VolMax Studio). Evaluated against external primary public API.

What the evidence can resolve:
Whether the frozen raw public acquisition batch captured at T_vintage yields the preregistered exact interval population (Target S) and reproduces the published July 2026 six-zone scarcity classification (Target R).

What it cannot resolve:
Internal TSO telemetry accuracy, private market dynamics, British market comparison (GB excluded), or post-vintage ENTSO-E database revisions.

## Frozen rules

Population definition:
PT15M resolution. Baseline: 32,064 expected intervals per zone (2025-08-01 00:00 to 2026-07-01 00:00 local, converted to UTC: 202507312200 to 202606302200). July 2026 Target: 2,976 expected intervals per zone (2026-07-01 00:00 to 2026-08-01 00:00 local, converted to UTC: 202606302200 to 202607312200).

Request Contract:
Exactly 12 requests (6 zones $\times$ 2 windows). No monthly chunking, zero slicing.

Estimator:
Baseline 90th percentile computed strictly via `pandas.Series(B_z).quantile(0.90, interpolation='linear')`. Occupancy M_z = count(price >= R_z) / 2976. Elevated iff M_z >= 0.15.

Thresholds:
Target S: missing = 0, duplicates = 0, unexpected = 0.
Target R: FR, NL, BE, AT, DK-1 = ELEVATED; DK-2 = NOT_ELEVATED.

Halting conditions:
See PREREGISTRATION.md §14.

Determinism requirement:
Exact deterministic mapping from preserved raw XML response to derived interval grid.

Scope exclusions:
See PREREGISTRATION.md §15.

## What has already been seen

Data inspected before freeze:
Prior s1 / Note 003 work exposed the team to the general defect family involving monthly boundaries, MTU handling, chunking, timezone and DST behaviour.

Outputs already known:
The published July-2026 six-zone occupancy values and 5/6 elevated classification are known. This audit is an explicit vintage-stability / reproduction audit, not naive discovery.

Exploratory runs:
None for s2. Any pre-freeze run is classified as Exploratory (not pre-registered).

## Current results

Measured: none
Derived: none
Scope findings: none for s2
Protocol failures: none for s2 at initialization

## Gate status

Gate model/person: Claude
Conflict check: No known model-provider conflict from the current target description.
Gate outcome: SPREMNO ZA CLAUDE PRE-EXECUTION GATE
Blocking findings:
None pending; draft ready for gate review.

## Failures

List IDs from FAILURES.md:
None at initialization.

## Next single action

Submit PREREGISTRATION.md draft to Claude for pre-execution Gate review.
