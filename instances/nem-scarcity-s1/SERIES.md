# Scheduled Series Specification — nem-scarcity-s1

> **Document Status:** Draft — SPREMNO ZA GEJT (not ratified)
> **Series Identifier:** `nem-scarcity-s1`
> **Version:** v1.0.0
> **Author:** Nestorov, Ivan / VolMax Studio Lab / ORCID 0009-0006-7940-9539
> **Selection mode:** `S1_scheduled` — S₁ (v0.3.1 scheduled series)
> **Measurement:** M₁ — `M1_SCARCITY_PERSISTENCE.md` (v0.7.3)
> **Classifier:** C — `C_CLASSIFIER_SCARCITY_PERSISTENCE.md` (v1.4.0)
> **Isolation Protocol:** `INSTANCE_ISOLATION_PROTOCOL.md` (v0.1.0)
> **Derived From:** OMN-001 (`notes/001-nem-duration-baseline/`, DOI 10.5281/zenodo.21693239)

---

## 1. Series Scope & Purpose

This scheduled series evaluates Australian AEMO NEM regional imbalance scarcity persistence under a 12-month rolling baseline window ($N = 12$).

### Relationship to OMN-001
- **OMN-001** measured scarcity duration above an **absolute price threshold** (300 AUD/MWh).
- **This series (`nem-scarcity-s1`)** measures scarcity persistence above a **market-local tail quantile** ($R_z = P_{90}$).
- These are separate physical quantities. This series does not reproduce, extend, or supersede OMN-001; it is an independent measurement over the same market infrastructure.

- **Primary Comparison Set ($\mathcal{M}$):** `NSW1`, `QLD1`, `SA1`, `VIC1` (4 AEMO mainland bidding regions).
- **Descriptive Companion Market:** `TAS1` (Tasmania island region, non-voting comparator).
- **Baseline Window ($B$):** Rolling $N = 12$ calendar months ending immediately prior to observation window $W$.
- **Operating Start Window ($W_{\text{start}}$):** `2026-06` (12 months post telemetry start `2025-06-01T00:00:00Z`).

---

## 2. Parameter Configuration Proposal

Parameters are proposed in `instances/nem-scarcity-s1/PARAMS.md`:
- $q_{\text{ref}} = 0.90$, $k_{\text{mult}} = 1.50 \implies S_{\text{thresh}} = 0.150$ (15.0% threshold)
- $N_{\text{low}} = 1$, $N_{\text{high}} = 4$ (Pending Ivan's decision on reachability constraint)
- $N = 12$ calendar months rolling baseline
- Telemetry resolution: 300.0 seconds (5-minute dispatch interval)
- Telemetry completeness floor: $98.0\%$
- `window_timezone`: `UTC`

---

## 3. Provenance & Execution Structure

Every run $W$ is executed deterministically by `instances/nem-scarcity-s1/src/run_window.py --window YYYY-MM`.
Run outputs are saved under `instances/nem-scarcity-s1/runs/YYYY-MM/`:
- `result.json`: Canonical deterministic measurement dictionary and classification label.
- `completeness.json`: Per-region telemetry completeness account under $M_1$ §4.

All window evaluations are recorded sequentially in `instances/nem-scarcity-s1/runs/SERIES_LOG.json`.

*VolMax Studio Lab · AEMO NEM Series Specification*
