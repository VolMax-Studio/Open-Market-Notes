# L10 Publication Lag Verification Execution Outcome Report

* **Pre-Registration Protocol Commit:** `3057a72` (`instances/entsoe-scarcity-s1/L10_LAG_VERIFICATION_PREREGISTRATION.md`)
* **Evaluator Hardening Commit:** `a1d1ee7`
* **Live Ingestion & Report Commit:** `f07cea3` (`instances/entsoe-scarcity-s1/test_fresh_fetch/l10_report.json`)
* **Gate Verdict (Claude):** `SURVIVES-REVIEW` (2026-08-15)
* **Human Operator Ratification Status:** `PENDING`

---

## 1. Measured Empirical Findings

1. **Primary Verdict:** `overall_l10_sufficient`: `false`. Publication lag $L = 10$ calendar days is **EMPIRICALLY INSUFFICIENT / BREACHED**.
2. **Revisions in France (RTE):** Between 2026-08-09 and 2026-08-15, RTE revised 633 imbalance price intervals in July 2026 (21.33% of the July window) with price drifts up to 506.41 EUR/MWh.
3. **Long-Tail Settlement Revisions (Structural Finding):** Price revisions were detected retroactively up to 12 months in the past (14 revised intervals in August 2025). This proves that publication lag $L$ cannot be managed as a fixed daily parameter ($L=10$ or $L=30$), but represents a fundamental property of settlement reconciliation runs (M+1, M+6, M+12).
4. **Zone Stability:** `AT`, `BE`, `DK_1`, `DK_2`, `NL` exhibited 0 price revisions (`STABLE`).
5. **Companion Zone Limitation:** `GB` imbalance series (`gb_system_prices.feather` sourced via Elexon) was un-evaluated in this ENTSO-E API run and remains unverified.
