# PARAMS — Exploratory Instance entsoe-eclipse-exp-20260812 Proposal

> **Document Status:** Draft — SPREMNO ZA GEJT (Pre-Registration Proposal)
> **Version:** v1.0.0
> **Specification Standard:** INSTRUMENT_SPEC v0.3.0 · M1 v0.7.4 · C v1.4.1 · S1 v0.3.1 · INSTANCE_ISOLATION v0.1.0
> **Instance Identifier:** `entsoe-eclipse-exp-20260812`
> **Selection Mode:** `exploratory`

---

## 1. Pre-Registration Proposal Configuration

```json
{
  "instance_id": "entsoe-eclipse-exp-20260812",
  "selection_mode": "exploratory",
  "event_name": "Western European Total Solar Eclipse Probe (2026-08-12)",
  "instrument_id": "M1_SCARCITY_PERSISTENCE",
  "instrument_version": "v0.7.4",
  "classifier_id": "C_CLASSIFIER_SCARCITY_PERSISTENCE",
  "classifier_version": "v1.4.1",
  "q_ref": 0.90,
  "k_multiplier": 1.50,
  "s_thresh_formula": "S_thresh is selected conservatively as 20.0% (exactly >= 2 out of 10 MTUs) over 10.0% (1 out of 10 MTUs) to require >= 30 min of extreme scarcity persistence.",
  "s_thresh_pct": 20.0,
  "s_thresh_discrete_intervals": ">= 2 out of 10 MTUs (15-min MTU resolution)",
  "timestamp_convention": "Interval Start Time in UTC (ENTSO-E Item #27 standard)",
  "slicing_rule": "Half-open interval filtering [start, end) on UTC timestamp index",
  "quantile_method": "linear",
  "baseline_type": "Fixed 12-month calendar reference (2025-08-01T00:00:00Z to 2026-07-31T23:59:59Z)",
  "baseline_N_months": 12,
  "baseline_utc_bounds": {
    "start": "2025-08-01T00:00:00Z",
    "end": "2026-07-31T23:59:59Z"
  },
  "event_utc_window": {
    "date": "2026-08-12",
    "start": "2026-08-12T17:00:00Z",
    "end": "2026-08-12T19:30:00Z",
    "duration_minutes": 150,
    "nominal_15min_mtus": 10
  },
  "control_utc_windows": [
    {"date": "2026-08-05", "start": "2026-08-05T17:00:00Z", "end": "2026-08-05T19:30:00Z"},
    {"date": "2026-08-06", "start": "2026-08-06T17:00:00Z", "end": "2026-08-06T19:30:00Z"},
    {"date": "2026-08-07", "start": "2026-08-07T17:00:00Z", "end": "2026-08-07T19:30:00Z"},
    {"date": "2026-08-08", "start": "2026-08-08T17:00:00Z", "end": "2026-08-08T19:30:00Z"},
    {"date": "2026-08-09", "start": "2026-08-09T17:00:00Z", "end": "2026-08-09T19:30:00Z"},
    {"date": "2026-08-10", "start": "2026-08-10T17:00:00Z", "end": "2026-08-10T19:30:00Z"},
    {"date": "2026-08-11", "start": "2026-08-11T17:00:00Z", "end": "2026-08-11T19:30:00Z"}
  ],
  "comparison_zones": ["ES", "PT", "FR", "DE_LU", "NL"],
  "companion_zones": [],
  "series_bindings": {
    "ES": {"imbalance_col": "imbalance_price_eur_mwh", "interval_sec": 900.0, "nominal_mtus": 10, "binding_status": "PROVISIONAL_PRE_FETCH"},
    "PT": {"imbalance_col": "imbalance_price_eur_mwh", "interval_sec": 900.0, "nominal_mtus": 10, "binding_status": "PROVISIONAL_PRE_FETCH"},
    "FR": {"imbalance_col": "imbalance_price_eur_mwh", "interval_sec": 900.0, "nominal_mtus": 10, "binding_status": "PROVISIONAL_PRE_FETCH"},
    "DE_LU": {"imbalance_col": "imbalance_price_eur_mwh", "interval_sec": 900.0, "nominal_mtus": 10, "binding_status": "PROVISIONAL_PRE_FETCH"},
    "NL": {"imbalance_col": "imbalance_price_eur_mwh", "interval_sec": 900.0, "nominal_mtus": 10, "binding_status": "PROVISIONAL_PRE_FETCH"}
  },
  "primary_signal": "Imbalance Settlement Price (Uncontaminated telemetry)",
  "secondary_disclosed_signal": "Day-Ahead Clearing Price (Pre-exposed prior to specification freeze)",
  "completeness_floor_pct": 80.0,
  "completeness_rationale": "Allows 1 missing 15-min MTU out of 10 (8/10 = 80.0%), evaluated under M1 v0.7.4 exposure bounds [E_lower, E_upper].",
  "max_control_crossings_allowed": 2,
  "comparability_discipline_disclosure": "Target zones differ in settlement mechanics (single-pricing in DE_LU/NL vs dual/single rules in ES/FR). Imbalance persistence values are measured against zone-local 12-month rolling P90 baselines (R_z), which natively absorb zone-specific pricing structures, but cross-zone persistence values reflect distinct market settlement designs.",
  "per_zone_elevation_rule": "A zone z is ELEVATED_BY_EVENT iff M1_event(z) == ELEVATED AND N_control_crossings(z) <= 2 out of 7 control days.",
  "falsification_rule": "The hypothesis that the solar eclipse produced measurable extreme scarcity elevation is FALSE if zero comparison zones return ELEVATED_BY_EVENT."
}
```

*VolMax Studio Lab · Exploratory Solar Eclipse Probe Specification*
