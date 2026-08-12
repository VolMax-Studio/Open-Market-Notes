# Exploratory Series Specification — entsoe-scarcity-exp-b6

> **Document Status:** Draft — SPREMNO ZA GEJT (Exploratory 6M Baseline Instance)
> **Series Identifier:** `entsoe-scarcity-exp-b6`
> **Version:** v1.0.0
> **Author:** Nestorov, Ivan / VolMax Studio Lab / ORCID 0009-0006-7940-9539
> **Selection mode:** `exploratory` — S₁ (v0.3.1 §3.4 exploratory baseline test)
> **Measurement:** M₁ — `M1_SCARCITY_PERSISTENCE.md` (v0.7.3)
> **Classifier:** C — `C_CLASSIFIER_SCARCITY_PERSISTENCE.md` (v1.4.0)
> **Isolation Protocol:** `INSTANCE_ISOLATION_PROTOCOL.md` (v0.1.0)

---

## 1. Series Scope & Purpose

This exploratory instance evaluates European imbalance scarcity persistence under a shorter $N = 6$ calendar month rolling baseline window across 8 consecutive historical months (`2025-12` through `2026-07`).

Its primary objective is empirical diagnostic exploration: testing label contrast (`NULL` vs `ISOLATED` vs `REGIONAL`) across different seasonal regimes (winter, spring, summer peaker periods).

- **Primary Comparison Set ($\mathcal{M}$):** `AT`, `BE`, `DK_1`, `DK_2`, `FR`, `NL` (6 ENTSO-E bidding zones).
- **Descriptive Companion Market:** `GB` (Great Britain Elexon BMRS system prices, non-voting).
- **Baseline Window ($B$):** Rolling $N = 6$ calendar months ending immediately prior to observation window $W$.
- **Observation Windows ($W$):** 8 calendar months in UTC (`2025-12` to `2026-07`).

---

## 2. Frozen Instance Parameters

Parameters are frozen in `instances/entsoe-scarcity-exp-b6/PARAMS.md`:
- $q_{\text{ref}} = 0.90$, $k_{\text{mult}} = 1.50 \implies S_{\text{thresh}} = 0.150$ (15.0% threshold)
- $N_{\text{low}} = 1$, $N_{\text{high}} = 4$
- $N = 6$ calendar months rolling baseline
- Telemetry completeness floor: $98.0\%$
- `window_timezone`: `UTC`

---

## 3. Provenance & Execution Structure

Every run $W$ is executed deterministically by `instances/entsoe-scarcity-exp-b6/src/run_window.py --window YYYY-MM`.
Run outputs are saved under `instances/entsoe-scarcity-exp-b6/runs/YYYY-MM/`:
- `result.json`: Canonical deterministic measurement dictionary and classification label.
- `completeness.json`: Per-zone telemetry completeness account under $M_1$ §4.

All window evaluations are recorded sequentially in `instances/entsoe-scarcity-exp-b6/runs/SERIES_LOG.json`.

*VolMax Studio Lab · Exploratory Series Specification*
