# PARAMS — Exploratory Instance entsoe-eclipse-exp-20260812

> **Document Status:** RATIFIED & PRE-REGISTERED
> **Version:** v1.0.0
> **Specification Standard:** INSTRUMENT_SPEC v0.3.0 · M1 v0.7.3 · C v1.4.1 · S1 v0.3.1 · INSTANCE_ISOLATION v0.1.0
> **Instance Identifier:** `entsoe-eclipse-exp-20260812`
> **Selection Mode:** `exploratory`

---

## 1. Pre-Registered Parameter Configuration

```json
{
  "instance_id": "entsoe-eclipse-exp-20260812",
  "selection_mode": "exploratory",
  "event_name": "Western European Total Solar Eclipse Probe (2026-08-12)",
  "instrument_id": "M1_SCARCITY_PERSISTENCE",
  "classifier_id": "C_CLASSIFIER_SCARCITY_PERSISTENCE",
  "q_ref": 0.90,
  "k_multiplier": 1.50,
  "s_thresh_pct": 15.0,
  "baseline_N_months": 12,
  "baseline_utc_bounds": {
    "start": "2025-08-01T00:00:00Z",
    "end": "2026-07-31T23:59:59Z"
  },
  "event_utc_window": {
    "date": "2026-08-12",
    "start": "2026-08-12T17:15:00Z",
    "end": "2026-08-12T19:30:00Z",
    "duration_minutes": 135
  },
  "control_utc_windows": [
    {"date": "2026-08-05", "start": "2026-08-05T17:15:00Z", "end": "2026-08-05T19:30:00Z"},
    {"date": "2026-08-06", "start": "2026-08-06T17:15:00Z", "end": "2026-08-06T19:30:00Z"},
    {"date": "2026-08-07", "start": "2026-08-07T17:15:00Z", "end": "2026-08-07T19:30:00Z"},
    {"date": "2026-08-08", "start": "2026-08-08T17:15:00Z", "end": "2026-08-08T19:30:00Z"},
    {"date": "2026-08-09", "start": "2026-08-09T17:15:00Z", "end": "2026-08-09T19:30:00Z"},
    {"date": "2026-08-10", "start": "2026-08-10T17:15:00Z", "end": "2026-08-10T19:30:00Z"},
    {"date": "2026-08-11", "start": "2026-08-11T17:15:00Z", "end": "2026-08-11T19:30:00Z"}
  ],
  "comparison_zones": ["ES", "PT", "FR", "DE_LU", "NL"],
  "companion_zones": [],
  "primary_signal": "Imbalance Settlement Price (Uncontaminated telemetry)",
  "secondary_disclosed_signal": "Day-Ahead Clearing Price (Pre-exposed prior to specification freeze)",
  "completeness_floor_pct": 98.0,
  "falsification_rule": "The claim that the solar eclipse produced measurable extreme scarcity elevation is false if no zone crosses S_thresh = 15.0% during the event window (17:15-19:30 UTC), OR if the zone crossed S_thresh in >= 4 of the 7 control days."
}
```

*VolMax Studio Lab · Exploratory Solar Eclipse Probe Specification*
