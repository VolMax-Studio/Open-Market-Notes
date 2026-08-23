# PROVENANCE — Instance nem-scarcity-s1

> **Instance ID:** `nem-scarcity-s1`
> **Selection Mode:** `S1_scheduled` (Australian NEM Market Scheduled Series Instance)
> **Governance Protocol:** Instance Isolation Protocol (v0.1.0) & S₁ (v0.3.1)

---

## 1. Primary Inputs & Manifest Checksums (Protocol §4)

Telemetry files in `inputs/` are derived from the OMN-001 archive, complemented with July 1st 2026 AEST AEMO NEMWEB daily reports to ensure 100.0000% UTC month completeness for June 2026 (`2026-06`), converted to regional series with UTC timestamp alignment, and recorded in `MANIFEST.json`. Manifest records are append-only.

| Input File | Region | Covered Period (UTC) | Rows | SHA-256 Checksum | License / Attribution |
|---|---|---|---|---|---|
| `inputs/nem_NSW1.feather` | `NSW1` | 2025-05-31T14:05:00Z to 2026-07-31T14:00:00Z | 122,688 | `2704a936ec12e4b57aa7f70b926bb6ed7a4f783c0b044e3bdea3de3be762e9e0` | CC BY 4.0 AEMO |
| `inputs/nem_QLD1.feather` | `QLD1` | 2025-05-31T14:05:00Z to 2026-07-31T14:00:00Z | 122,688 | `cfb046acafd964ac0b7be68caab8da1c28b285cae0a483c7402ad3a275a96b4d` | CC BY 4.0 AEMO |
| `inputs/nem_SA1.feather` | `SA1` | 2025-05-31T14:05:00Z to 2026-07-31T14:00:00Z | 122,688 | `07d7de7f2fc7910c68482bf0083e418640e2f56c4d7c7fdba2024e108f51cd5b` | CC BY 4.0 AEMO |
| `inputs/nem_VIC1.feather` | `VIC1` | 2025-05-31T14:05:00Z to 2026-07-31T14:00:00Z | 122,688 | `3696c86ee9b20966bbe19815c81a44b4f69322dddd0aac8ce75c23e40688e6fe` | CC BY 4.0 AEMO |
| `inputs/nem_TAS1.feather` | `TAS1` | 2025-05-31T14:05:00Z to 2026-07-31T14:00:00Z | 122,688 | `d6d0fb0408a80ab60222e8a9ae4f9f3185dea005b2bdcc20e9b8e3561741793f` | CC BY 4.0 AEMO |

---

## 2. Isolation Guarantees
- Absolute zero relative paths (`../`) escaping `instances/nem-scarcity-s1/` in execution code.
- `MANIFEST.json` maintained as append-only.
- All evaluation runs execute strictly against `inputs/` inside this instance.
- Immutable source note OMN-001 (`notes/001-nem-duration-baseline/`) remains byte-unchanged and untouched.

*VolMax Studio Lab · Instance Isolation Protocol*
