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

        # Load frozen PARAMS.md from instance root for 100% config parity
        instance_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        actual_params_path = os.path.join(instance_root, 'PARAMS.md')
        with open(actual_params_path) as f:
            self.raw_params_content = f.read()

        with open(os.path.join(self.test_dir, 'PARAMS.md'), 'w') as f:
            f.write(self.raw_params_content)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    def set_ratified_params(self):
        """Helper to resolve provisional bindings for synthetic telemetry execution tests."""
        params_obj = json.loads(self.raw_params_content[self.raw_params_content.find('{'):self.raw_params_content.rfind('}')+1])
        params_obj['timestamp_convention'] = 'INTERVAL_START_UTC'
        for z in params_obj['series_bindings']:
            params_obj['series_bindings'][z]['binding_status'] = 'RATIFIED'
        
        new_content = f"# PARAMS — Test Config\n```json\n{json.dumps(params_obj, indent=2)}\n```"
        with open(os.path.join(self.test_dir, 'PARAMS.md'), 'w') as f:
            f.write(new_content)

    def make_synthetic_feather(self, zones=None, event_prices_dict=None, drop_event_idx_dict=None, drop_control_dict=None, elevated_control_days_dict=None):
        if zones is None:
            zones = ["ES", "PT", "FR", "DE_LU", "NL"]

        for z in zones:
            b_dates = pd.date_range("2025-08-01", "2026-07-31 23:45", freq="15min", tz="UTC")
            b_df = pd.DataFrame({"DateTime": b_dates, "imbalance_price_eur_mwh": 50.0})
            n_p90 = int(len(b_df) * 0.10)
            b_df.iloc[:n_p90, b_df.columns.get_loc("imbalance_price_eur_mwh")] = 150.0

            c_rows = []
            control_dates = ["2026-08-05", "2026-08-06", "2026-08-07", "2026-08-08", "2026-08-09", "2026-08-10", "2026-08-11"]
            for c_date in control_dates:
                c_ts = pd.date_range(f"{c_date} 17:00", f"{c_date} 20:00", freq="15min", tz="UTC")
                is_elevated_day = elevated_control_days_dict and z in elevated_control_days_dict and c_date in elevated_control_days_dict[z]
                
                for idx, ts in enumerate(c_ts):
                    if drop_control_dict and z in drop_control_dict and c_date in drop_control_dict[z] and idx in drop_control_dict[z][c_date]:
                        continue
                    
                    price = 150.0 if (is_elevated_day and idx < 2) else 50.0
                    c_rows.append({"DateTime": ts, "imbalance_price_eur_mwh": price})
            c_df = pd.DataFrame(c_rows)

            e_ts = pd.date_range("2026-08-12 17:00", "2026-08-12 20:00", freq="15min", tz="UTC")
            e_prices = event_prices_dict.get(z, [50.0]*len(e_ts)) if event_prices_dict else [50.0]*len(e_ts)
            if len(e_prices) < len(e_ts):
                e_prices = e_prices + [50.0] * (len(e_ts) - len(e_prices))

            e_df = pd.DataFrame({"DateTime": e_ts, "imbalance_price_eur_mwh": e_prices})

            if drop_event_idx_dict and z in drop_event_idx_dict:
                e_df = e_df.drop(index=drop_event_idx_dict[z]).reset_index(drop=True)

            full_df = pd.concat([b_df, c_df, e_df], ignore_index=True)
            full_df.to_feather(os.path.join(self.inputs_dir, f"imbalance_{z}.feather"))

    def test_b39_mutant_1_kill_elevated_by_event_positive_path(self):
        """B39 Mutant #1 Kill: Assert positive elevation path produces ELEVATED_BY_EVENT (Fails if is_elevated_by_event=False)."""
        self.set_ratified_params()
        # Event has 2 elevated intervals (2/10 = 20.0% >= S_thresh) -> ELEVATED
        event_prices = {"ES": [150.0, 150.0] + [50.0]*11}
        self.make_synthetic_feather(event_prices_dict=event_prices)
        res = evaluate_eclipse_probe(self.test_dir)
        es_res = res['zone_results']['ES']
        self.assertTrue(es_res['is_elevated_by_event'], "Positive path MUST yield is_elevated_by_event = True")
        self.assertEqual(es_res['zone_determinacy'], 'ELEVATED_BY_EVENT')
        self.assertEqual(res['verdict'], 'ELEVATED_BY_EVENT')

    def test_b39_mutant_2_kill_exposure_bounds_swap(self):
        """B39 Mutant #2 Kill: Assert missing interval resulting in exp_lower < 20% <= exp_upper yields INDETERMINATE, not ELEVATED."""
        self.set_ratified_params()
        # Event: 1 missing interval out of 10 (index 1 dropped), index 0 is 150.0.
        # exp_lower = 1/10 = 10% < 20%; exp_upper = (1+1)/10 = 20% >= 20%.
        event_prices = {"ES": [150.0] + [50.0]*11}
        drop_event = {"ES": [1]}
        self.make_synthetic_feather(event_prices_dict=event_prices, drop_event_idx_dict=drop_event)
        res = evaluate_eclipse_probe(self.test_dir)
        es_res = res['zone_results']['ES']
        self.assertEqual(es_res['event_determinacy'], 'INDETERMINATE', "Straddled exposure MUST yield INDETERMINATE, not ELEVATED")
        self.assertEqual(res['verdict'], 'INDETERMINATE')

    def test_b39_mutant_3_kill_control_indeterminate_counting(self):
        """B39 Mutant #3 Kill: Assert control INDETERMINATE counts as crossing (Fails if control INDETERMINATE ignored)."""
        self.set_ratified_params()
        # Event window is ELEVATED (2/10 = 20%):
        event_prices = {"ES": [150.0, 150.0] + [50.0]*11}
        # 1 control day is fully ELEVATED (2026-08-05)
        elevated_control = {"ES": ["2026-08-05"]}
        # 2 control days have 1 missing interval and 1 elevated value -> INDETERMINATE (2026-08-06, 2026-08-07)
        drop_control = {
            "ES": {
                "2026-08-06": [1],
                "2026-08-07": [1]
            }
        }
        # Event day 2026-08-06 and 2026-08-07 have index 0 elevated (150.0)
        # We need 2026-08-06 and 2026-08-07 to have index 0 = 150.0 in make_synthetic_feather:
        # Pass custom prices for control days via elevated_control_days_dict for 05, 06, 07
        elevated_control_all = {"ES": ["2026-08-05", "2026-08-06", "2026-08-07"]}
        self.make_synthetic_feather(event_prices_dict=event_prices, drop_control_dict=drop_control, elevated_control_days_dict=elevated_control_all)
        res = evaluate_eclipse_probe(self.test_dir)
        es_res = res['zone_results']['ES']
        # Total crossings = 1 (ELEVATED) + 2 (INDETERMINATE) = 3 > 2 (max_control_crossings_allowed)
        self.assertEqual(es_res['control_crossings'], 3, "Control INDETERMINATE MUST count as crossing")
        self.assertFalse(es_res['is_elevated_by_event'], "Crossings > 2 MUST prevent ELEVATED_BY_EVENT")

    def test_b40_mutant_kill_unfetched_zone_yields_data_pending(self):
        """B40 Mutant Kill: Assert un-fetched zone returns DATA_PENDING, NOT global NULL."""
        self.set_ratified_params()
        # Only create feather files for 4 zones, leave NL un-created
        self.make_synthetic_feather(zones=["ES", "PT", "FR", "DE_LU"])
        res = evaluate_eclipse_probe(self.test_dir)
        self.assertEqual(res['verdict'], 'DATA_PENDING', "Un-fetched zone MUST force global DATA_PENDING, NOT NULL")

    def test_b26_missing_column_raises_keyerror(self):
        """B26 Test: Missing specified column MUST raise KeyError."""
        self.set_ratified_params()
        bad_df = pd.DataFrame({"DateTime": pd.date_range("2026-08-12 17:00", "2026-08-12 19:15", freq="15min", tz="UTC"), "wrong_col": [50.0]*10})
        bad_df.to_feather(os.path.join(self.inputs_dir, "imbalance_ES.feather"))
        with self.assertRaises(KeyError):
            evaluate_eclipse_probe(self.test_dir)

    def test_f1_provisional_execution_gate_raises_valueerror(self):
        """F1 Test: Execution with telemetry when bindings are PROVISIONAL MUST raise ValueError."""
        # PARAMS.md is in PROVISIONAL state by default from setUp
        self.make_synthetic_feather()
        with self.assertRaises(ValueError):
            evaluate_eclipse_probe(self.test_dir)

    def test_b31_off_by_one_half_open_slice(self):
        """B31 Test: Half-open slicing yields exact 10 MTUs when dataset extends to 20:00."""
        self.set_ratified_params()
        self.make_synthetic_feather()
        df = pd.read_feather(os.path.join(self.inputs_dir, "imbalance_ES.feather"))
        df['DateTime'] = pd.to_datetime(df['DateTime'], utc=True)
        df = df.set_index('DateTime').sort_index()

        inclusive_slice = df.loc["2026-08-12 17:00:00Z":"2026-08-12 19:30:00Z"]
        self.assertEqual(len(inclusive_slice), 11, "Inclusive slicing MUST yield 11 rows")

        res = evaluate_eclipse_probe(self.test_dir)
        es_res = res['zone_results']['ES']
        self.assertEqual(es_res['admitted_mtus'], 10, "Half-open evaluator MUST return exactly 10 admitted MTUs")

    def test_b36_series_log_append_only(self):
        """B36 Test: Evaluator executions append to SERIES_LOG.json without overwriting."""
        self.set_ratified_params()
        self.make_synthetic_feather()
        evaluate_eclipse_probe(self.test_dir)
        evaluate_eclipse_probe(self.test_dir)

        series_log_path = os.path.join(self.test_dir, 'runs', 'SERIES_LOG.json')
        with open(series_log_path) as f:
            log_entries = json.load(f)

        self.assertEqual(len(log_entries), 2, "SERIES_LOG.json MUST retain all execution records")

if __name__ == '__main__':
    unittest.main()
