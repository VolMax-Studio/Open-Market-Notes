# PARAMS — Instance entsoe-scarcity-exp-b6 Frozen Parameters

> **Document Status:** Draft — SPREMNO ZA GEJT (Exploratory 6M Baseline Instance)
> **Version:** v1.0.0
> **Specification Standard:** INSTRUMENT_SPEC v0.3.0 · M1 v0.7.3 · C v1.4.0 · S1 v0.3.1 · INSTANCE_ISOLATION v0.1.0
> **Instance Identifier:** `entsoe-scarcity-exp-b6`
> **Selection Mode:** `exploratory`

---

## 1. Frozen Parameter Configuration

```json
{
  "instance_id": "entsoe-scarcity-exp-b6",
  "selection_mode": "exploratory",
  "instrument_id": "M1_SCARCITY_PERSISTENCE",
  "classifier_id": "C_SCARCITY_PERSISTENCE",
  "q_ref": 0.90,
  "k_multiplier": 1.50,
  "n_low": 1,
  "n_high": 4,
  "N": 6,
  "run_day": 12,
  "operating_start": "2025-12",
  "window_timezone": "UTC",
  "completeness_floor_pct": 98.0,
  "quantile_method": "linear",
  "timestamp_tz": "UTC",
  "comparison_zones": ["AT", "BE", "DK_1", "DK_2", "FR", "NL"],
  "companion_zones": ["GB"],
  "series_bindings": {
    "AT": {"baseline_col": "Short", "probe_col": "Short", "interval_duration_sec": 900.0},
    "BE": {"baseline_col": "Short", "probe_col": "Short", "interval_duration_sec": 900.0},
    "DK_1": {"baseline_col": "Short", "probe_col": "Short", "interval_duration_sec": 900.0},
    "DK_2": {"baseline_col": "Short", "probe_col": "Short", "interval_duration_sec": 900.0},
    "FR": {"baseline_col": "Short", "probe_col": "Short", "interval_duration_sec": 900.0},
    "NL": {"baseline_col": "Short", "probe_col": "Short", "interval_duration_sec": 900.0},
    "GB": {"baseline_col": "systemSellPrice", "probe_col": "systemSellPrice", "interval_duration_sec": 1800.0}
  }
}
```

*VolMax Studio Lab · Exploratory 6M Baseline Instance*
