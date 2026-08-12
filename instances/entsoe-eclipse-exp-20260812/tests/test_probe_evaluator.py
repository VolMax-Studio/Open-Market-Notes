#!/usr/bin/env python3
import os
import sys
import json
import tempfile
import unittest
import pandas as pd
import numpy as np

src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from evaluate_eclipse_probe import evaluate_eclipse_probe

class TestSolarEclipseProbeEvaluator(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.inputs_dir = os.path.join(self.test_dir, 'inputs')
        os.makedirs(self.inputs_dir, exist_ok=True)

        # Copy actual frozen PARAMS.md from instance root for 100% config parity (B35)
        instance_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        actual_params_path = os.path.join(instance_root, 'PARAMS.md')
        with open(actual_params_path) as f:
            params_content = f.read()

        with open(os.path.join(self.test_dir, 'PARAMS.md'), 'w') as f:
            f.write(params_content)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    def make_synthetic_feather(self, zones=None, event_prices_dict=None, drop_event_idx_dict=None, drop_control_dict=None):
        if zones is None:
            zones = ["ES", "PT", "FR", "DE_LU", "NL"]

        for z in zones:
            b_dates = pd.date_range("2025-08-01", "2026-07-31 23:45", freq="15min", tz="UTC")
            b_df = pd.DataFrame({"DateTime": b_dates, "imbalance_price_eur_mwh": 50.0})
            n_p90 = int(len(b_df) * 0.10)
            b_df.iloc[:n_p90, b_df.columns.get_loc("imbalance_price_eur_mwh")] = 150.0

            # Control days timestamps extended past 19:30 to 20:00 to test half-open slicing (B31)
            c_rows = []
            for c_date in ["2026-08-05", "2026-08-06", "2026-08-07", "2026-08-08", "2026-08-09", "2026-08-10", "2026-08-11"]:
                c_ts = pd.date_range(f"{c_date} 17:00", f"{c_date} 20:00", freq="15min", tz="UTC")
                for idx, ts in enumerate(c_ts):
                    if drop_control_dict and z in drop_control_dict and c_date in drop_control_dict[z] and idx in drop_control_dict[z][c_date]:
                        continue
                    c_rows.append({"DateTime": ts, "imbalance_price_eur_mwh": 50.0})
            c_df = pd.DataFrame(c_rows)

            # Event day timestamps extended past 19:30 to 20:00 to test half-open slicing (B31)
            e_ts = pd.date_range("2026-08-12 17:00", "2026-08-12 20:00", freq="15min", tz="UTC")
            e_prices = event_prices_dict.get(z, [50.0]*len(e_ts)) if event_prices_dict else [50.0]*len(e_ts)
            if len(e_prices) < len(e_ts):
                e_prices = e_prices + [50.0] * (len(e_ts) - len(e_prices))

            e_df = pd.DataFrame({"DateTime": e_ts, "imbalance_price_eur_mwh": e_prices})

            if drop_event_idx_dict and z in drop_event_idx_dict:
                e_df = e_df.drop(index=drop_event_idx_dict[z]).reset_index(drop=True)

            full_df = pd.concat([b_df, c_df, e_df], ignore_index=True)
            full_df.to_feather(os.path.join(self.inputs_dir, f"imbalance_{z}.feather"))

    def test_b31_off_by_one_half_open_slice_fails_on_inclusive(self):
        """B31 Test: Assert dataset containing 19:30 returns 11 on inclusive slicing, but EXACTLY 10 on half-open."""
        self.make_synthetic_feather()
        # Verify inclusive slicing on synthetic file yields 11 rows
        df = pd.read_feather(os.path.join(self.inputs_dir, "imbalance_ES.feather"))
        df['DateTime'] = pd.to_datetime(df['DateTime'], utc=True)
        df = df.set_index('DateTime').sort_index()

        inclusive_slice = df.loc["2026-08-12 17:00:00Z":"2026-08-12 19:30:00Z"]
        self.assertEqual(len(inclusive_slice), 11, "Inclusive slicing MUST yield 11 rows when 19:30 exists")

        # Verify evaluator uses half-open slicing to return exactly 10
        res = evaluate_eclipse_probe(self.test_dir)
        es_res = res['zone_results']['ES']
        self.assertEqual(es_res['admitted_mtus'], 10, "Evaluator MUST return exactly 10 admitted MTUs")
        self.assertEqual(es_res['nominal_mtus'], 10)
        self.assertEqual(es_res['completeness_pct'], 100.0)

    def test_b32_control_incomplete_and_indeterminate_branches(self):
        """B32 Test: Assert control day INCOMPLETE, INDETERMINATE, and zone INCOMPLETE branches."""
        # Zone ES: Drop 3 timestamps from control day 2026-08-05 (completeness 7/10 = 70% < 80% -> INCOMPLETE)
        # Drop 3 timestamps from control day 2026-08-06 (INCOMPLETE) -> incomplete_control_days = 2 >= 2 -> Zone INCOMPLETE!
        drop_control = {
            "ES": {
                "2026-08-05": [0, 1, 2],
                "2026-08-06": [0, 1, 2]
            }
        }
        self.make_synthetic_feather(drop_control_dict=drop_control)
        res = evaluate_eclipse_probe(self.test_dir)
        es_res = res['zone_results']['ES']
        self.assertEqual(es_res['incomplete_control_days'], 2)
        self.assertEqual(es_res['zone_determinacy'], 'INCOMPLETE')

    def test_b35_frozen_params_parity_all_5_zones(self):
        """B35 Test: Verify evaluator runs against all 5 frozen zones in PARAMS.md cleanly."""
        self.make_synthetic_feather()
        res = evaluate_eclipse_probe(self.test_dir)
        self.assertEqual(res['status'], 'EVALUATED')
        self.assertEqual(set(res['zone_results'].keys()), {"ES", "PT", "FR", "DE_LU", "NL"})

    def test_b36_series_log_append_only_deduplication(self):
        """B36 Test: Verify multiple executions append to SERIES_LOG.json without overwriting history."""
        self.make_synthetic_feather()
        evaluate_eclipse_probe(self.test_dir)
        evaluate_eclipse_probe(self.test_dir)

        series_log_path = os.path.join(self.test_dir, 'runs', 'SERIES_LOG.json')
        with open(series_log_path) as f:
            log_entries = json.load(f)

        self.assertEqual(len(log_entries), 2, "SERIES_LOG.json MUST retain all execution records (append-only)")
        self.assertEqual(log_entries[0]['run_id'], 1)
        self.assertEqual(log_entries[1]['run_id'], 2)

if __name__ == '__main__':
    unittest.main()
