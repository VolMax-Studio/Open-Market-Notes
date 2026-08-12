# DECISIONS — Instance entsoe-eclipse-exp-20260812 Append-Only Decision Log

> **Instance ID:** `entsoe-eclipse-exp-20260812`
> **Selection Mode:** `exploratory`
> **Governance Protocol:** Instance Isolation Protocol (v0.1.0) & P10 Verification Protocol

---

## Decision 001 — Proposal Instantiation for Solar Eclipse Probe (2026-08-12)

- **Context:** Western European Total Solar Eclipse on 2026-08-12 (~17:15 to 19:30 UTC).
- **Decision:** Proposed exploratory probe instance `instances/entsoe-eclipse-exp-20260812/` under M1 v0.7.3 / C v1.4.1. Initial draft created for pre-registration review.

---

## Decision 002 — Remediation of Gate Round 1 Blockers B1–B8 (2026-08-12)

- **Context:** P10 Gate Audit Round 1 identified discretization mismatches, diurnal peak artifacts, and self-ratification status headers.
- **Decision:**
  1. Shifted status headers strictly to `Draft — SPREMNO ZA GEJT`.
  2. Aligned discrete threshold to $\ge 2$ out of 10 MTUs ($20.0\%$).
  3. Defined per-zone elevation rules and 7-day diurnal control baseline window.

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

---

## Decision 004 — First-Principles Remediation & Synthetic Test Suite (Gate Round 3 B20–B29, 2026-08-12)

- **Context:** P10 Gate Audit Round 3 identified off-by-one slice inclusivity (B20), unstated timestamp convention (B21), binary NULL verdict swallowing INDETERMINATE/INCOMPLETE (B22), control day exposure asymmetry (B23), un-opened L0 source licensing (B24), provisional bindings (B25), silent price column fallbacks (B26), Decision log overwriting (B27), SERIES_LOG overwriting (B28), and non-deterministic result timestamps (B29).
- **Decision:**
  1. Implemented synthetic test suite `tests/test_probe_evaluator.py` enforcing unit testing before telemetry fetch.
  2. Applied half-open interval slicing `[start, end)` to guarantee exact 10 nominal MTUs for 150-minute windows.
  3. Pre-registered ENTSO-E UTC Interval Start Time convention.
  4. Expanded global verdict to a strict 4-state enum (`ELEVATED_BY_EVENT`, `INDETERMINATE`, `INCOMPLETE`, `NULL`).
  5. Enforced symmetric M1 v0.7.4 exposure bounds for control days and strict `KeyError` on missing columns.
  6. Set L0 status to `[BLOCKED — source not opened]` per Check 4.
  7. Converted `SERIES_LOG.json` to append-only mode and removed volatile timestamps from `result.json` byte payload to guarantee 100% hash reproducibility.

*VolMax Studio Lab · Append-Only Decision Record*
