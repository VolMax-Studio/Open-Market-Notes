# Scheduled Series Specification — entsoe-scarcity-s1

> **Document Status:** RATIFIED — FROZEN for Series Operation
> **Series Identifier:** `entsoe-scarcity-s1`
> **Version:** v1.0.0
> **Author:** Nestorov, Ivan / VolMax Studio Lab / ORCID 0009-0006-7940-9539
> **Selection mode:** S₁ (Scheduled) — `S1_SCHEDULED_SELECTION.md` (v0.3.1)
> **Measurement:** M₁ — `M1_SCARCITY_PERSISTENCE.md` (v0.7.3)
> **Classifier:** C — `C_CLASSIFIER_SCARCITY_PERSISTENCE.md` (v1.4.0)
> **Isolation Protocol:** `INSTANCE_ISOLATION_PROTOCOL.md` (v0.1.0)

---

## 1. Series Scope & Definition

This document instantiates the scheduled series `entsoe-scarcity-s1` under selection rule $S_1$ (Scheduled Cadence Operation). 

The series measures scarcity price duration exposure across Central-Western European electricity imbalance markets on a strict, unskipped monthly calendar cadence.

- **Primary Comparison Set ($\mathcal{M}$):** `AT`, `BE`, `DK_1`, `DK_2`, `FR`, `NL` (6 ENTSO-E bidding zones).
- **Descriptive Companion Market:** `GB` (Great Britain Elexon BMRS system prices, non-voting).
- **Baseline Window ($B$):** Rolling $N = 12$ calendar months ending immediately prior to observation window $W$.
- **Observation Window ($W$):** Full calendar month in UTC (`YYYY-MM-01T00:00:00Z` to `YYYY-MM-<last>T23:59:59Z`).
- **Cadence & Execution:** Scheduled monthly run executed on `run_day` = 12 of each month following publication lag $L = 10$ calendar days.

---

## 2. Frozen Instance Parameters

Parameters are frozen in `instances/entsoe-scarcity-s1/PARAMS.md`:
- $q_{\text{ref}} = 0.90$, $k_{\text{mult}} = 1.50 \implies S_{\text{thresh}} = 0.150$ (15.0% threshold)
- $N_{\text{low}} = 1$, $N_{\text{high}} = 4$
- Telemetry completeness floor: $98.0\%$
- `window_timezone`: `UTC`

---

## 3. Provenance & Execution Structure

Every run $W$ is executed deterministically by `instances/entsoe-scarcity-s1/src/run_window.py --window YYYY-MM`.
Run outputs are saved under `instances/entsoe-scarcity-s1/runs/YYYY-MM/`:
- `result.json`: Canonical deterministic measurement dictionary and classification label.
- `completeness.json`: Per-zone telemetry completeness account under $M_1$ §4.

All window evaluations are recorded sequentially in `instances/entsoe-scarcity-s1/runs/SERIES_LOG.json`.

*VolMax Studio Lab · Scheduled Series Specification*
