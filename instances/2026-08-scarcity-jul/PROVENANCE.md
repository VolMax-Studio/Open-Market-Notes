# PROVENANCE — Instance 2026-08-scarcity-jul

> **Instance ID:** `2026-08-scarcity-jul`
> **Derived From:** OMN-003 Baseline & Probe Telemetry
> **Governance Protocol:** Instance Isolation Protocol (v0.1.0)

---

## 1. Inherited Artefacts & Value-Copy Record (Protocol §4)

| Input File | Source Repo Path | Source Commit | SHA-256 Checksum | License / Attribution |
|---|---|---|---|---|
| `inputs/baseline/imbalance_AT.feather` | `notes/003-entsoe-imbalance-baseline/data/processed/imbalance_AT.feather` | `10c1e58fa6a3af529d8d1e65f8133d5f7cab4f63` | `bbf726205c0c663e79240c81f69ec030b2ab66829a2c9a296f54d79797baf571` | CC BY 4.0 ENTSO-E (Item #27) |
| `inputs/baseline/imbalance_BE.feather` | `notes/003-entsoe-imbalance-baseline/data/processed/imbalance_BE.feather` | `10c1e58fa6a3af529d8d1e65f8133d5f7cab4f63` | `82b4a532fa1d5ee92efc4d216f466b0dfd669ef0528fb46ab7448e895ec76722` | CC BY 4.0 ENTSO-E (Item #27) |
| `inputs/baseline/imbalance_DK_1.feather` | `notes/003-entsoe-imbalance-baseline/data/processed/imbalance_DK_1.feather` | `10c1e58fa6a3af529d8d1e65f8133d5f7cab4f63` | `4329fb2ef71399478f7aa95bd28b7eec9b1c73ad7d8e87ef87f25aa26ee57a72` | CC BY 4.0 ENTSO-E (Item #27) |
| `inputs/baseline/imbalance_DK_2.feather` | `notes/003-entsoe-imbalance-baseline/data/processed/imbalance_DK_2.feather` | `10c1e58fa6a3af529d8d1e65f8133d5f7cab4f63` | `5e98bb4b8b6f38ef7a1eb1d713c7a36f97ef78fa6ee15c15629c42ae3a6933bb` | CC BY 4.0 ENTSO-E (Item #27) |
| `inputs/baseline/imbalance_FR.feather` | `notes/003-entsoe-imbalance-baseline/data/processed/imbalance_FR.feather` | `10c1e58fa6a3af529d8d1e65f8133d5f7cab4f63` | `d720b666a7b7a14ad6b840e6c6b7ef9dfbcf2d6bd7a1ef24a1b028448831ecad` | CC BY 4.0 ENTSO-E (Item #27) |
| `inputs/baseline/imbalance_NL.feather` | `notes/003-entsoe-imbalance-baseline/data/processed/imbalance_NL.feather` | `10c1e58fa6a3af529d8d1e65f8133d5f7cab4f63` | `2e086111edeb762cf1b4fecff532d56a7bc3cfd10cb233d67b2dcb588ac5b6d1` | CC BY 4.0 ENTSO-E (Item #27) |
| `inputs/probe_jul2026/imbalance_AT.feather` | `notes/003-entsoe-imbalance-baseline/probe_jul2026/processed/imbalance_AT.feather` | `10c1e58fa6a3af529d8d1e65f8133d5f7cab4f63` | `b5327299ee853d6ebefcd4275c9772bf2eb8d5e165aaeb0953ef27c44dfbc9cf` | CC BY 4.0 ENTSO-E (Item #27) |
| `inputs/probe_jul2026/imbalance_BE.feather` | `notes/003-entsoe-imbalance-baseline/probe_jul2026/processed/imbalance_BE.feather` | `10c1e58fa6a3af529d8d1e65f8133d5f7cab4f63` | `7973c68ceebaf7894aee9edbc6a362f6236b283dfa3fa71fefd83dc47fdbbde3` | CC BY 4.0 ENTSO-E (Item #27) |
| `inputs/probe_jul2026/imbalance_DK_1.feather` | `notes/003-entsoe-imbalance-baseline/probe_jul2026/processed/imbalance_DK_1.feather` | `10c1e58fa6a3af529d8d1e65f8133d5f7cab4f63` | `d2c88219416550b06b978bfdce1eb0e1eb84efceeb591d37aed09f7a9dd97b5e` | CC BY 4.0 ENTSO-E (Item #27) |
| `inputs/probe_jul2026/imbalance_DK_2.feather` | `notes/003-entsoe-imbalance-baseline/probe_jul2026/processed/imbalance_DK_2.feather` | `10c1e58fa6a3af529d8d1e65f8133d5f7cab4f63` | `c87aa9ad74e92eb13cf7bebbfe005fcfa7f69eeaafeebffbbbc23ab26f95a639` | CC BY 4.0 ENTSO-E (Item #27) |
| `inputs/probe_jul2026/imbalance_FR.feather` | `notes/003-entsoe-imbalance-baseline/probe_jul2026/processed/imbalance_FR.feather` | `10c1e58fa6a3af529d8d1e65f8133d5f7cab4f63` | `6ae285be23c10a12e2f3d61bca11c03cf8bb95bcfed9d5c3fcefaed22ca72d42` | CC BY 4.0 ENTSO-E (Item #27) |
| `inputs/probe_jul2026/imbalance_NL.feather` | `notes/003-entsoe-imbalance-baseline/probe_jul2026/processed/imbalance_NL.feather` | `10c1e58fa6a3af529d8d1e65f8133d5f7cab4f63` | `3aa8cfbc1fcf0b0ef85408ebc3080ffbc56c56fbcfd40eeb2eaf2dbbcfa326f5` | CC BY 4.0 ENTSO-E (Item #27) |
| `inputs/gb_system_prices.feather` | `notes/004-gb-duration-baseline/data/processed/gb_system_prices.feather` | `792b4d91e3eec1438992adbeabf20e408ecbbcc4` | `ed54c86bb0fbbe5aebffae40bc756c9a35eecfa8f5c90b6ecbc4d46b7edafcae` | Elexon BMRS Open Data |

---

## 2. Isolation Guarantees
- Absolute zero relative paths (`../`) escaping `instances/2026-08-scarcity-jul/` in source code.
- No write actions against published `notes/003-entsoe-imbalance-baseline/` directory (`git status notes/003-...` 100% clean).
- Parent registry entry OMN-003 and OMN-003-PROBE hashes left 100% byte-unchanged.

*VolMax Studio Lab · Instance Isolation Protocol*
