# L10 Publication Lag Verification Pre-Registration Protocol
**Target Series:** `entsoe-scarcity-s1` | **Baseline Snapshot Date:** `2026-08-09` (`cfec9e2`) | **Fresh Snapshot Date:** `2026-08-15` | **Protocol Version:** `v1.0.0`

---

## 1. Purpose & Pre-Registration Scope

This document establishes the pre-registered empirical criteria for verifying whether publication lag **$L = 10$ calendar days** is sufficient to guarantee raw imbalance price telemetry stability across ENTSO-E bidding zones (`AT`, `BE`, `DK_1`, `DK_2`, `FR`, `NL`) and companion zone `GB`.

This specification is frozen in Git prior to executing the live fresh data fetch call on 2026-08-15.

---

## 2. Execution & Isolation Boundaries

1. **Isolation Directory:** Fresh telemetry is downloaded exclusively into an isolated test directory (`instances/entsoe-scarcity-s1/test_fresh_fetch/`). The committed baseline feather files in `instances/entsoe-scarcity-s1/inputs/` are preserved without modification.
2. **Right-Boundary Window Lock:** The fresh fetch query requests the exact same temporal boundary as the 2026-08-09 baseline snapshot.
3. **Overlapping Interval Scope:** Evaluation is performed strictly over pre-existing overlapping 15-minute intervals starting from `2025-05-31 22:00:00 UTC` up to **`2026-07-31 21:45:00 UTC`** (the rightmost boundary of the baseline snapshot).

---

## 3. Normative Evaluation Conditions

### 3.1 Primary Condition — Raw Telemetry Stability ($L = 10$ Sufficiency)
Publication lag $L = 10$ calendar days is empirically **SUFFICIENT** for a zone if and only if zero raw imbalance price values differ across all overlapping 15-minute intervals between the 2026-08-09 baseline and 2026-08-15 fresh snapshot under numerical tolerance $|p_{15.08} - p_{09.08}| \le 10^{-4}\text{ EUR/MWh}$.

If any raw price value differs ($|p_{15.08} - p_{09.08}| > 10^{-4}\text{ EUR/MWh}$), publication lag $L = 10$ is empirically **INSUFFICIENT** (settlement drift present).

### 3.2 Secondary Condition — Aggregate Metric $M_1$ Impact
If raw price revisions occur, the evaluator calculates:
1. Total count and percentage of revised intervals ($N_{\text{revised}}$).
2. Maximum absolute price drift ($\max |p_{15.08} - p_{09.08}|$).
3. Delta impact on aggregate $M_1$ (%) and window classification (`REGIONAL` / `ISOLATED` / `NULL`).

---

## 4. Per-Zone & Per-Column Evaluation Rules

Evaluation is executed and reported **per bidding zone and per column**:

### 4.1 Binding Columns by Zone
* **ENTSO-E Voting Zones (`AT`, `BE`, `DK_1`, `DK_2`, `FR`, `NL`):**
  - Primary binding column: `Short` (shortage imbalance price).
  - Secondary column: `Long` (surplus imbalance price).
  - *Duplicate Column Rule:* For single-pricing zones (`AT`, `BE`, `DK_1`, `DK_2`) where `Long == Short` across 100% of baseline rows, column `Long` is evaluated and reported as `DUPLICATE_SERIES (Long == Short)` to avoid double-counting stable series.
* **Companion Zone (`GB`):**
  - Primary column: `systemSellPrice`.
  - Secondary column: `systemBuyPrice`.

### 4.2 IEEE 754 NaN & Numerical Equality Rules
For every interval timestamp $t$ and price pair $(p_1, p_2)$ where $p_1 = p_{09.08}(t)$ and $p_2 = p_{15.08}(t)$:
1. **Both NaN (`pd.isna(p_1) and pd.isna(p_2)`):** Evaluates to **`STABLE`** (no change in missing value status).
2. **One NaN (`pd.isna(p_1) != pd.isna(p_2)`):** Evaluates to **`COVERAGE_CHANGE`** (data interval added or removed).
3. **Both Numeric:**
   - If $|p_2 - p_1| > 10^{-4}\text{ EUR/MWh}$ $\implies$ **`PRICE_REVISION`**.
   - If $|p_2 - p_1| \le 10^{-4}\text{ EUR/MWh}$ $\implies$ **`STABLE`**.

---

## 5. Allowed Verdict Vocabulary (Non-Exclusive Outcome Flags)

Per-column evaluation outcomes are classified using the following non-exclusive flags:
* **`STABLE`:** 0 price diffs ($|p_2 - p_1| \le 10^{-4}$) and 0 coverage changes.
* **`PRICE_REVISION`:** $\ge 1$ interval with $|p_2 - p_1| > 10^{-4}\text{ EUR/MWh}$.
* **`COVERAGE_CHANGE`:** $\ge 1$ interval added or removed within overlapping timestamps.
* **`PRICE_REVISION + COVERAGE_CHANGE`:** Both price drift and interval coverage changes present.
* **`DUPLICATE_SERIES`:** Secondary column is byte-identical to primary column (`Long == Short`).

---

## 6. Mandate 9 Zero Secret Leakage Control

All automated fetching and comparison scripts MUST strictly enforce Mandate 9. No ENTSO-E API tokens or request credentials shall be printed or logged in standard output.
