# DECISIONS — Instance entsoe-eclipse-exp-20260812 Append-Only Decision Log

> **Instance ID:** `entsoe-eclipse-exp-20260812`
> **Selection Mode:** `exploratory`
> **Governance Protocol:** Instance Isolation Protocol (v0.1.0) & P10 Verification Protocol

---

## Decision 001 — Proposal Instantiation for Solar Eclipse Probe (2026-08-12)

- **Context:** Western European Total Solar Eclipse on 2026-08-12 (~17:15 to 19:30 UTC).
- **Decision:** Proposed exploratory probe instance `instances/entsoe-eclipse-exp-20260812/` under M1 v0.7.3 / C v1.4.1.

---

## Decision 002 — Remediation of Gate Round 1 Blockers (2026-08-12)

- **Context:** P10 Gate Audit Round 1 identified discretization mismatches and diurnal peak artifacts.
- **Decision:** Shifted status to `Draft — SPREMNO ZA GEJT`, defined per-zone elevation rules, and incorporated diurnal 7-day control windows.

---

## Decision 003 — Remediation of Gate Round 2 Blockers B9–B19 (2026-08-12)

- **Context:** P10 Gate Audit Round 2 identified force-push violations (B9), commit hash fixed-point loops (B10), un-implemented M1 v0.7.4 exposure bounds (B11–B13), control day asymmetry (B14), zone-resolution bindings (B15), price column bindings and comparability disclosures (B16), truncated identity blocks (B17), L0 license terms (B18), and output artifact generation (B19).
- **Decision:**
  1. Halted force-pushes; logged Entry #026 in `FAILURES.md`.
  2. Set `spec_commit` to `null` in registry to rely on pure `params_sha256` and post-commit git tag `freeze/entsoe-eclipse-exp-20260812`.
  3. Implemented full M1 v0.7.4 exposure bounds $[E_{\text{lower}}, E_{\text{upper}}]$ for both event and control windows symmetrically.
  4. Bound target price column (`imbalance_price_eur_mwh`) per zone in `PARAMS.md` and added Comparability Discipline Disclosure.
  5. Pinned verbatim ENTSO-E Item #27 redistribution terms and restored author identity block.
  6. Added output file writing (`runs/2026-08-12/result.json`, `completeness.json`, `SERIES_LOG.json`).

*VolMax Studio Lab · Append-Only Decision Record*
