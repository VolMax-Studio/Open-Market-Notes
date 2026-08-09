# PARAMS — Instance 2026-08-scarcity-jul Frozen Parameters

> **Document Status:** Draft — SPREMNO ZA GEJT (not ratified)
> **Version:** v1.1.0
> **Specification Standard:** INSTRUMENT_SPEC v0.3.0 · M1 v0.6.0 · C v1.2.0 · INSTANCE_ISOLATION v0.1.0
> **Instance Identifier:** `2026-08-scarcity-jul`

---

## 1. Frozen Parameter Configuration

```json
{
  "instance_id": "2026-08-scarcity-jul",
  "derived_from": "OMN-003",
  "instrument_id": "M1_SCARCITY_PERSISTENCE",
  "classifier_id": "C_SCARCITY_PERSISTENCE",
  "q_ref": 0.90,
  "k_multiplier": 1.50,
  "n_low": 1,
  "n_high": 4,
  "completeness_floor_pct": 98.0,
  "max_allowed_gap_seconds": 900.0,
  "quantile_method": "linear",
  "timestamp_tz": "UTC",
  "window_timezone": "UTC",
  "baseline_window": {
    "start_utc": "2025-08-01T00:00:00Z",
    "end_utc": "2026-06-30T23:59:59Z",
    "nominal_intervals_15m": 32064
  },
  "probe_window": {
    "start_utc": "2026-07-01T00:00:00Z",
    "end_utc": "2026-07-31T23:59:59Z",
    "nominal_intervals_15m": 2976
  },
  "comparison_zones": ["AT", "BE", "DK_1", "DK_2", "FR", "NL"],
  "companion_zones": ["GB"],
  "series_bindings": {
    "AT": {"baseline_col": "Short", "probe_col": "Short"},
    "BE": {"baseline_col": "Short", "probe_col": "Short"},
    "DK_1": {"baseline_col": "Short", "probe_col": "Short"},
    "DK_2": {"baseline_col": "Short", "probe_col": "Short"},
    "FR": {"baseline_col": "Short", "probe_col": "Short"},
    "NL": {"baseline_col": "Short", "probe_col": "Short"},
    "GB": {"baseline_col": "systemSellPrice", "probe_col": "systemSellPrice", "max_allowed_gap_seconds": 1800.0}
  }
}
```

*VolMax Studio Lab · Instance Isolation Protocol*
