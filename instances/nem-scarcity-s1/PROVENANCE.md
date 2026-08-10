# PROVENANCE — Instance nem-scarcity-s1

> **Instance ID:** `nem-scarcity-s1`
> **Selection Mode:** `S1_scheduled` (Australian NEM Market Scheduled Series Instance)
> **Governance Protocol:** Instance Isolation Protocol (v0.1.0) & S₁ (v0.3.1)

---

## 1. Primary Inputs & Manifest Checksums (Protocol §4)

Telemetry files in `inputs/` are derived from the OMN-001 archive, complemented with July 1st 2026 AEST AEMO NEMWEB daily reports to ensure 100.0000% UTC month completeness for June 2026 (`2026-06`), converted to regional series with UTC timestamp alignment, and recorded in `MANIFEST.json`. Manifest records are append-only.

| Input File | Region | Covered Period (UTC) | Rows | SHA-256 Checksum | License / Attribution |
|---|---|---|---|---|---|
| `inputs/nem_NSW1.feather` | `NSW1` | 2025-05-31T14:05:00Z to 2026-07-01T00:00:00Z | 113,880 | `4105b7169181ebac1e0f0fbfaee9d2bc181e1fe352b2f6efadac3dbe0bc3141f` | CC BY 4.0 AEMO |
| `inputs/nem_QLD1.feather` | `QLD1` | 2025-05-31T14:05:00Z to 2026-07-01T00:00:00Z | 113,880 | `cd609adedacacfb5cdb9aa4b7f7396b27072ceecab07707e7bca9c1b3f9ff705` | CC BY 4.0 AEMO |
| `inputs/nem_SA1.feather` | `SA1` | 2025-05-31T14:05:00Z to 2026-07-01T00:00:00Z | 113,880 | `6d27829c4d6adfc40742f1cf105d15a2ec2ef1e06fa5ddb698bb2c222ff47e0a` | CC BY 4.0 AEMO |
| `inputs/nem_VIC1.feather` | `VIC1` | 2025-05-31T14:05:00Z to 2026-07-01T00:00:00Z | 113,880 | `e21d0d11d2f31b52a5edb0e6cfa8f5c35eb659c0edbc31d683fb082103f6fba5` | CC BY 4.0 AEMO |
| `inputs/nem_TAS1.feather` | `TAS1` | 2025-05-31T14:05:00Z to 2026-07-01T00:00:00Z | 113,880 | `cc30c1effc80036ee7bfeb08bce1121d5a7d32c8fe5a03426e6d1ebcf9979313` | CC BY 4.0 AEMO |

---

## 2. Isolation Guarantees
- Absolute zero relative paths (`../`) escaping `instances/nem-scarcity-s1/` in execution code.
- `MANIFEST.json` maintained as append-only.
- All evaluation runs execute strictly against `inputs/` inside this instance.
- Immutable source note OMN-001 (`notes/001-nem-duration-baseline/`) remains byte-unchanged and untouched.

*VolMax Studio Lab · Instance Isolation Protocol*
