# PROVENANCE — Instance nem-scarcity-s1

> **Instance ID:** `nem-scarcity-s1`
> **Selection Mode:** `S1_scheduled` (Australian NEM Market Scheduled Series Instance)
> **Governance Protocol:** Instance Isolation Protocol (v0.1.0) & S₁ (v0.3.1)

---

## 1. Primary Inputs & Manifest Checksums (Protocol §4)

Telemetry files in `inputs/` are copied from the OMN-001 archive, converted to regional series with UTC timestamp alignment, and recorded in `MANIFEST.json`. Manifest records are append-only.

| Input File | Region | Covered Period (UTC) | Rows | SHA-256 Checksum | License / Attribution |
|---|---|---|---|---|---|
| `inputs/nem_NSW1.feather` | `NSW1` | 2025-05-31T14:05:00Z to 2026-06-30T14:00:00Z | 113,760 | `91dc944aeb637508cf311d4d03964d3753cfc9085ecaf238c8ae38724e6cf1e4` | CC BY 4.0 AEMO |
| `inputs/nem_QLD1.feather` | `QLD1` | 2025-05-31T14:05:00Z to 2026-06-30T14:00:00Z | 113,760 | `f1d1a21dac8ca8a05c754d92419bc9ef7f9c2d1b820a406085a8d9bf16c31fa6` | CC BY 4.0 AEMO |
| `inputs/nem_SA1.feather` | `SA1` | 2025-05-31T14:05:00Z to 2026-06-30T14:00:00Z | 113,760 | `bd0aeae228eddf7fa9d02c7df76fcaa7576fcabac10e30ebf0f9b31d8ce4a713` | CC BY 4.0 AEMO |
| `inputs/nem_VIC1.feather` | `VIC1` | 2025-05-31T14:05:00Z to 2026-06-30T14:00:00Z | 113,760 | `0e4dbff71f5256e2eb9df5728a0715dfcbfb40fe6be9ecacfa1548eebf81498b` | CC BY 4.0 AEMO |
| `inputs/nem_TAS1.feather` | `TAS1` | 2025-05-31T14:05:00Z to 2026-06-30T14:00:00Z | 113,760 | `42260ad9d4b3df3634fa6164d1f274092b77c5c2d334544d673bc8caeb08dd44` | CC BY 4.0 AEMO |

---

## 2. Isolation Guarantees
- Absolute zero relative paths (`../`) escaping `instances/nem-scarcity-s1/` in execution code.
- `MANIFEST.json` maintained as append-only.
- All evaluation runs execute strictly against `inputs/` inside this instance.
- Immutable source note OMN-001 (`notes/001-nem-duration-baseline/`) remains byte-unchanged and untouched.

*VolMax Studio Lab · Instance Isolation Protocol*
