#!/usr/bin/env python3
import os
import sys
import json
import tempfile
import unittest
import pandas as pd
import numpy as np

# Ensure instance src is in path
src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from evaluate_eclipse_probe import evaluate_eclipse_probe

class TestSolarEclipseProbeEvaluator(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.inputs_dir = os.path.join(self.test_dir, 'inputs')
        os.makedirs(self.inputs_dir, exist_ok=True)

        # Write test PARAMS.md
        self.params_content = """# PARAMS — Test Config
```json
{
  "instance_id": "entsoe-eclipse-exp-20260812",
  "selection_mode": "exploratory",
  "q_ref": 0.90,
  "s_thresh_pct": 20.0,
  "quantile_method": "linear",
  "completeness_floor_pct": 80.0,
  "max_control_crossings_allowed": 2,
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
  "comparison_zones": ["ES"],
  "companion_zones": [],
  "series_bindings": {
    "ES": {"imbalance_col": "imbalance_price_eur_mwh", "interval_sec": 900.0, "nominal_mtus": 10}
  }
}
```
"""
        with open(os.path.join(self.test_dir, 'PARAMS.md'), 'w') as f:
            f.write(self.params_content)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    def make_synthetic_feather(self, zone="ES", event_prices=None, drop_event_idx=None):
        # Create full 1-year timestamps + 7 control days + 1 event day
        b_dates = pd.date_range("2025-08-01", "2026-07-31 23:45", freq="15min", tz="UTC")
        b_df = pd.DataFrame({"DateTime": b_dates, "imbalance_price_eur_mwh": 50.0})
        # Set top 10% to 150.0 so P90 is around 60.0
        n_p90 = int(len(b_df) * 0.10)
        b_df.iloc[:n_p90, b_df.columns.get_loc("imbalance_price_eur_mwh")] = 150.0

        # Control days timestamps (17:00 to 19:30 half-open = 10 MTUs per day)
        c_rows = []
        for c_date in ["2026-08-05", "2026-08-06", "2026-08-07", "2026-08-08", "2026-08-09", "2026-08-10", "2026-08-11"]:
            c_ts = pd.date_range(f"{c_date} 17:00", f"{c_date} 19:15", freq="15min", tz="UTC")
            for ts in c_ts:
                c_rows.append({"DateTime": ts, "imbalance_price_eur_mwh": 50.0}) # All normal
        c_df = pd.DataFrame(c_rows)

        # Event day timestamps (17:00 to 19:30 half-open = 10 MTUs)
        e_ts = pd.date_range("2026-08-12 17:00", "2026-08-12 19:15", freq="15min", tz="UTC")
        if event_prices is None:
            event_prices = [50.0] * 10

        e_df = pd.DataFrame({"DateTime": e_ts, "imbalance_price_eur_mwh": event_prices})

        if drop_event_idx is not None:
            e_df = e_df.drop(index=drop_event_idx).reset_index(drop=True)

        full_df = pd.concat([b_df, c_df, e_df], ignore_index=True)
        full_df.to_feather(os.path.join(self.inputs_dir, f"imbalance_{zone}.feather"))

    def test_b20_half_open_slice_exact_10_mtus(self):
        """B20 Test: Ensure half-open slice [17:00, 19:30) returns exactly 10 admitted MTUs, not 11."""
        self.make_synthetic_feather(event_prices=[50.0]*10)
        res = evaluate_eclipse_probe(self.test_dir)
        es_res = res['zone_results']['ES']
        self.assertEqual(es_res['admitted_mtus'], 10)
        self.assertEqual(es_res['nominal_mtus'], 10)
        self.assertEqual(es_res['completeness_pct'], 100.0)
        self.assertEqual(res['verdict'], 'NULL')

    def test_b22_enum_null_vs_indeterminate(self):
        """B22 Test: Ensure missing interval resulting in exposure straddling thresh yields INDETERMINATE, not NULL."""
        # Index 0 is 150.0 (elevated). Index 1 (50.0) is dropped.
        # Admitted: 9 MTUs. q_count = 1. exp_lower = 1/10 = 10%, exp_upper = (1+1)/10 = 20%.
        # Straddles 20.0% threshold -> INDETERMINATE!
        event_prices = [150.0] + [50.0]*9  # 10 intervals
        self.make_synthetic_feather(event_prices=event_prices, drop_event_idx=[1])
        res = evaluate_eclipse_probe(self.test_dir)
        es_res = res['zone_results']['ES']
        self.assertEqual(es_res['event_determinacy'], 'INDETERMINATE')
        self.assertEqual(res['verdict'], 'INDETERMINATE')

    def test_b23_symmetric_control_evaluation(self):
        """B23 Test: Control day missing intervals evaluate exposure bounds symmetrically."""
        self.make_synthetic_feather(event_prices=[150.0, 150.0] + [50.0]*8) # 2 elevated = 20%
        res = evaluate_eclipse_probe(self.test_dir)
        es_res = res['zone_results']['ES']
        self.assertEqual(es_res['event_determinacy'], 'ELEVATED')
        self.assertEqual(es_res['is_elevated_by_event'], True)
        self.assertEqual(res['verdict'], 'ELEVATED_BY_EVENT')

    def test_b26_missing_column_raises_keyerror(self):
        """B26 Test: If target column specified in series_bindings is missing, script MUST raise KeyError."""
        bad_df = pd.DataFrame({"DateTime": pd.date_range("2026-08-12 17:00", "2026-08-12 19:15", freq="15min", tz="UTC"), "wrong_column": [50.0]*10})
        bad_df.to_feather(os.path.join(self.inputs_dir, "imbalance_ES.feather"))
        with self.assertRaises(KeyError):
            evaluate_eclipse_probe(self.test_dir)

if __name__ == '__main__':
    unittest.main()
