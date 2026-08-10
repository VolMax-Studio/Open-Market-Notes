# PARAMS — Instance nem-scarcity-s1 Parameters (Unfrozen Proposal)

> **Document Status:** Draft — SPREMNO ZA GEJT (not ratified)
> **Version:** v1.0.0
> **Specification Standard:** INSTRUMENT_SPEC v0.3.0 · M1 v0.7.3 · C v1.4.0 · S1 v0.3.1 · INSTANCE_ISOLATION v0.1.0
> **Instance Identifier:** `nem-scarcity-s1`
> **Selection Mode:** `S1_scheduled`

---

## 1. Parameter Proposal Configuration

```json
{
  "instance_id": "nem-scarcity-s1",
  "selection_mode": "S1_scheduled",
  "instrument_id": "M1_SCARCITY_PERSISTENCE",
  "classifier_id": "C_CLASSIFIER_SCARCITY_PERSISTENCE",
  "q_ref": 0.90,
  "k_multiplier": 1.50,
  "n_low": 1,
  "n_high": "TO BE FROZEN (Option 1: 4 for unanimity, Option 2: 3 for majority)",
  "N": 12,
  "L_publication_lag_days": "PROVISIONAL (AEMO lag 7-18 days)",
  "run_day": 21,
  "operating_start": "2026-06",
  "window_timezone": "UTC",
  "market_timezone": "Australia/Brisbane (Fixed AEST UTC+10:00, no DST)",
  "completeness_floor_pct": 98.0,
  "quantile_method": "linear",
  "timestamp_tz": "UTC",
  "comparison_zones": "TO BE FROZEN (Option A: [NSW1, QLD1, SA1, VIC1], Option B: [NSW1, QLD1, SA1, VIC1, TAS1])",
  "companion_zones": "TO BE FROZEN (Option A: [TAS1], Option B: [])",
  "series_bindings": {
    "NSW1": {"baseline_col": "RRP", "probe_col": "RRP", "interval_duration_sec": 300.0},
    "QLD1": {"baseline_col": "RRP", "probe_col": "RRP", "interval_duration_sec": 300.0},
    "SA1": {"baseline_col": "RRP", "probe_col": "RRP", "interval_duration_sec": 300.0},
    "VIC1": {"baseline_col": "RRP", "probe_col": "RRP", "interval_duration_sec": 300.0},
    "TAS1": {"baseline_col": "RRP", "probe_col": "RRP", "interval_duration_sec": 300.0}
  }
}
```

*VolMax Studio Lab · AEMO NEM Market Scheduled Series Instance*
