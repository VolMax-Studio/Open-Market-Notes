#!/usr/bin/env python3
import os
import sys
import json
import glob
import shutil
import hashlib
import tempfile
import unittest
import subprocess
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(BASE_DIR, "notes_registry.json")
NOTE_DIR = os.path.join(BASE_DIR, "notes", "001-nem-duration-baseline")
RESULTS_JSON = os.path.join(NOTE_DIR, "results.json")
BACKUP_JSON = os.path.join(NOTE_DIR, "results.json.bak")
LOCAL_PROC_DIR = os.path.join(BASE_DIR, "notes", "001-nem-duration-baseline", "data", "processed")

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def get_frozen_registry_sha256(note_num="001"):
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)
    for entry in registry:
        if entry["note_number"] == note_num:
            return entry["results_sha256"]
    return None

def create_synthetic_telemetry_fixture(temp_proc_dir, start_date="2025-06-01", end_date="2026-06-30"):
    """Generates synthetic feather telemetry fixture for clean checkout CI execution, exercising scarcity spikes."""
    os.makedirs(temp_proc_dir, exist_ok=True)
    months = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    duids = ['HPR1', 'VBB1', 'WANDB1', 'WDBESS1', 'TIB1', 'HBESS1', 'RANGEB1', 'CHBESS1', 
             'BLYTHB1', 'BHB1', 'BBATTERY1', 'ULPBESS1', 'WALGRV1', 'RESS1', 'RIVNB2', 'CAPBES1']
    regions = ['NSW1', 'QLD1', 'SA1', 'VIC1']
    
    for m in months:
        ym_str = m.strftime('%Y%m')
        dates = pd.date_range(start=m, periods=288, freq='5min') # 1 day sample per month
        price_records = []
        for i, r in enumerate(regions):
            np.random.seed(42 + i + m.month)
            rrps = np.random.uniform(10, 100, len(dates))
            # Inject scarcity price spikes (>= 300.0) to fully exercise Metric 1 event detection
            rrps[10:14] = 500.0
            rrps[50:52] = 12000.0
            for d, rrp in zip(dates, rrps):
                price_records.append({'SETTLEMENTDATE': d, 'REGIONID': r, 'RRP': rrp})
        price_df = pd.DataFrame(price_records)
        price_df.to_feather(os.path.join(temp_proc_dir, f"price_{ym_str}.feather"))
        
        # Synthetic SCADA DataFrame
        scada_records = []
        for duid in duids:
            np.random.seed(42 + hash(duid) % 100)
            vals = np.random.uniform(-50, 50, len(dates))
            for d, val in zip(dates, vals):
                scada_records.append({'SETTLEMENTDATE': d, 'DUID': duid, 'SCADAVALUE': val})
        scada_df = pd.DataFrame(scada_records)
        scada_df.to_feather(os.path.join(temp_proc_dir, f"scada_{ym_str}.feather"))

class TestSyntheticCIDeterminismFixture(unittest.TestCase):
    """Guarantees CI Determinism Guard passes 100% reliably on clean checkout without modifying repository working tree."""
    def test_synthetic_reproduction_determinism(self):
        with tempfile.TemporaryDirectory() as temp_proc_dir, tempfile.TemporaryDirectory() as temp_out_dir:
            create_synthetic_telemetry_fixture(temp_proc_dir)
            reproduce_script = os.path.join(NOTE_DIR, "reproduce.py")
            temp_results_json = os.path.join(temp_out_dir, "results.json")
            
            # Run 1
            cmd1 = [sys.executable, reproduce_script, "--start-date", "2025-06-01", "--end-date", "2026-06-30", "--data-dir", temp_proc_dir, "--out-dir", temp_out_dir]
            res1 = subprocess.run(cmd1, cwd=BASE_DIR, capture_output=True, text=True)
            self.assertEqual(res1.returncode, 0, f"Synthetic Run 1 failed:\n{res1.stderr}")
            
            with open(temp_results_json, "r") as f:
                res_data = json.load(f)
            # Assert Metric 1 event detection was executed
            nsw_events = res_data["Metric_1_Scarcity_Pricing_Duration"]["NSW1"]["Total_Events"]
            self.assertGreater(nsw_events, 0, "Synthetic fixture failed to exercise Metric 1 event detection!")
            
            hash1 = compute_sha256(temp_results_json)
            
            # Delete temp output and Run 2
            os.remove(temp_results_json)
            res2 = subprocess.run(cmd1, cwd=BASE_DIR, capture_output=True, text=True)
            self.assertEqual(res2.returncode, 0, f"Synthetic Run 2 failed:\n{res2.stderr}")
            hash2 = compute_sha256(temp_results_json)
            
            self.assertEqual(hash1, hash2, "Synthetic fixture output is non-deterministic!")
            print(f"\n[SYNTHETIC CI DETERMINISM GUARD PASSED] Verified byte-identity on scarcity-spiked synthetic fixture (isolated temp_out_dir): {hash1}")

class TestReinforcedDeterminism(unittest.TestCase):
    def test_rename_recreate_byte_identity(self):
        # Canonical telemetry directory
        data_dir = LOCAL_PROC_DIR
        price_files = glob.glob(os.path.join(data_dir, "price_*.feather"))
        scada_files = glob.glob(os.path.join(data_dir, "scada_*.feather"))
        has_full_telemetry = len(price_files) == 13 and len(scada_files) == 13
        
        if not has_full_telemetry:
            self.skipTest(f"Skipping full telemetry determinism test — complete 13-month telemetry (13 price + 13 scada files) not present in {data_dir} (found {len(price_files)} price, {len(scada_files)} scada). Handled by TestSyntheticCIDeterminismFixture.")

        self.assertTrue(os.path.exists(RESULTS_JSON), f"Source results.json missing at {RESULTS_JSON}")
        frozen_registry_sha256 = get_frozen_registry_sha256("001")
        
        # 1. COPY original file to backup location (non-destructive)
        shutil.copy2(RESULTS_JSON, BACKUP_JSON)
        # Delete original to force true recreation by reproduce.py
        os.remove(RESULTS_JSON)
        self.assertFalse(os.path.exists(RESULTS_JSON), "results.json was not successfully deleted for recreation test!")

        try:
            # 2. RUN pipeline with explicit baseline dates and explicit --data-dir from root CWD
            reproduce_script = os.path.join(NOTE_DIR, "reproduce.py")
            cmd = [sys.executable, reproduce_script, "--start-date", "2025-06-01", "--end-date", "2026-06-30", "--data-dir", data_dir]
            
            # Execute with root CWD to verify path anchor independence
            res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Pipeline execution failed:\n{res.stderr}")
            
            # 3. VERIFY RECREATION
            self.assertTrue(os.path.exists(RESULTS_JSON), "Pipeline failed to RECREATE results.json!")
            
            # 4. VERIFY BYTE-IDENTITY (SHA-256 Match)
            recreated_sha256 = compute_sha256(RESULTS_JSON)
            backup_sha256 = compute_sha256(BACKUP_JSON)
            
            self.assertEqual(recreated_sha256, backup_sha256, "Recreated results.json does not match backup hash!")
            self.assertEqual(recreated_sha256, frozen_registry_sha256, f"Hash mismatch with frozen registry! Expected {frozen_registry_sha256}, got {recreated_sha256}")
            print(f"\n[REINFORCED DETERMINISM TEST PASSED] Recreated results_sha256: {recreated_sha256}")
            
        finally:
            # Unconditional restore in finally block to ensure working tree is NEVER left corrupt
            if os.path.exists(BACKUP_JSON):
                if os.path.exists(RESULTS_JSON) and compute_sha256(RESULTS_JSON) != compute_sha256(BACKUP_JSON):
                    shutil.copy2(RESULTS_JSON, RESULTS_JSON + ".failed")
                shutil.copy2(BACKUP_JSON, RESULTS_JSON)
                os.remove(BACKUP_JSON)

if __name__ == '__main__':
    unittest.main()
