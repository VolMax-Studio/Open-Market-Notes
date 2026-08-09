# PROVENANCE — Instance entsoe-scarcity-exp-b6

> **Instance ID:** `entsoe-scarcity-exp-b6`
> **Selection Mode:** `exploratory` (6-Month Rolling Baseline Exploratory Instance)
> **Governance Protocol:** Instance Isolation Protocol (v0.1.0) & S₁ (v0.3.1 §3.4)

---

## 1. Primary Inputs & Manifest Checksums (Protocol §4)

Telemetry files in `inputs/` are copied from `entsoe-scarcity-s1`. Manifest records are append-only.

| Input File | Covered Period (UTC) | Rows | SHA-256 Checksum | License / Attribution |
|---|---|---|---|---|
| `inputs/imbalance_AT.feather` | 2025-05-31T22:00:00Z to 2026-07-31T21:45:00Z | 40,895 | `1e2b15e5e0aacbbd1560f698a9c2300ed8cdb8e5a41147b28f870f8177e7930f` | CC BY 4.0 ENTSO-E |
| `inputs/imbalance_BE.feather` | 2025-05-31T22:00:00Z to 2026-07-31T21:45:00Z | 40,895 | `7079b220e858b63dc3bae8c6a3d4e458a3961948e45fb854750f0a559f6271f0` | CC BY 4.0 ENTSO-E |
| `inputs/imbalance_DK_1.feather` | 2025-05-31T22:00:00Z to 2026-07-31T21:45:00Z | 40,846 | `18c8d1b440934a6983f8bddcba73117d4c497ab34bada3aec7f73f5baec979cd` | CC BY 4.0 ENTSO-E |
| `inputs/imbalance_DK_2.feather` | 2025-05-31T22:00:00Z to 2026-07-31T21:45:00Z | 40,845 | `b24e31281700f6ddb4c973573c8ac05a1e6bbd2fda16afea9b3f661547e664c8` | CC BY 4.0 ENTSO-E |
| `inputs/imbalance_FR.feather` | 2025-05-31T22:00:00Z to 2026-07-31T21:45:00Z | 40,895 | `9a5be474e2b45dda8e3afe4f89d472af28ec6d253f8cbb94397e4f778c16782f` | CC BY 4.0 ENTSO-E |
| `inputs/imbalance_NL.feather` | 2025-05-31T22:00:00Z to 2026-07-31T21:45:00Z | 40,895 | `a13d6481251a566d053d46846139712c1723c6ac438fa88b7ae7cebbda71a0bf` | CC BY 4.0 ENTSO-E |
| `inputs/gb_system_prices.feather` | 2025-05-31T23:00:00Z to 2026-07-31T22:30:00Z | 20,448 | `973f114775366b89683edb75e307d7906b3632375ceba5ae8f4cdfd32b96c2ab` | Elexon BMRS Open Data |

---

## 2. Isolation Guarantees
- Absolute zero relative paths (`../`) escaping `instances/entsoe-scarcity-exp-b6/` in execution code.
- `MANIFEST.json` maintained as append-only.
- All evaluation runs execute strictly against `inputs/` inside this instance.

*VolMax Studio Lab · Instance Isolation Protocol*
