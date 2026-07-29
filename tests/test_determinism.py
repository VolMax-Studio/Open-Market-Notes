#!/usr/bin/env python3
import os
import sys
import json
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
PROC_DIR = os.path.join(NOTE_DIR, "data", "processed")

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
    """Generates synthetic feather telemetry fixture for clean checkout CI execution."""
    os.makedirs(temp_proc_dir, exist_ok=True)
    months = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    duids = ['HPR1', 'VBB1', 'WANDB1', 'WDBESS1', 'TIB1', 'HBESS1', 'RANGEB1', 'CHBESS1', 
             'BLYTHB1', 'BHB1', 'BBATTERY1', 'ULPBESS1', 'WALGRV1', 'RESS1', 'RIVNB2', 'CAPBES1']
    regions = ['NSW1', 'QLD1', 'SA1', 'VIC1']
    
    for m in months:
        ym_str = m.strftime('%Y%m')
        
        # Synthetic Price DataFrame
        dates = pd.date_range(start=m, periods=288, freq='5min') # 1 day sample per month for speed
        price_records = []
        for r in regions:
            np.random.seed(42)
            rrps = np.random.uniform(10, 100, len(dates))
            for d, rrp in zip(dates, rrps):
                price_records.append({'SETTLEMENTDATE': d, 'REGIONID': r, 'RRP': rrp})
        price_df = pd.DataFrame(price_records)
        price_df.to_feather(os.path.join(temp_proc_dir, f"price_{ym_str}.feather"))
        
        # Synthetic SCADA DataFrame
        scada_records = []
        for duid in duids:
            np.random.seed(42)
            vals = np.random.uniform(-50, 50, len(dates))
            for d, val in zip(dates, vals):
                scada_records.append({'SETTLEMENTDATE': d, 'DUID': duid, 'SCADAVALUE': val})
        scada_df = pd.DataFrame(scada_records)
        scada_df.to_feather(os.path.join(temp_proc_dir, f"scada_{ym_str}.feather"))

class TestSyntheticCIDeterminismFixture(unittest.TestCase):
    """Guarantees CI Determinism Guard passes 100% reliably on clean checkout without telemetry dependency."""
    def test_synthetic_reproduction_determinism(self):
        with tempfile.TemporaryDirectory() as temp_proc_dir:
            create_synthetic_telemetry_fixture(temp_proc_dir)
            reproduce_script = os.path.join(NOTE_DIR, "reproduce.py")
            
            # Run 1
            cmd1 = [sys.executable, reproduce_script, "--start-date", "2025-06-01", "--end-date", "2026-06-30", "--data-dir", temp_proc_dir]
            res1 = subprocess.run(cmd1, cwd=BASE_DIR, capture_output=True, text=True)
            self.assertEqual(res1.returncode, 0, f"Synthetic Run 1 failed:\n{res1.stderr}")
            hash1 = compute_sha256(RESULTS_JSON)
            
            # Delete output and Run 2
            os.remove(RESULTS_JSON)
            res2 = subprocess.run(cmd1, cwd=BASE_DIR, capture_output=True, text=True)
            self.assertEqual(res2.returncode, 0, f"Synthetic Run 2 failed:\n{res2.stderr}")
            hash2 = compute_sha256(RESULTS_JSON)
            
            self.assertEqual(hash1, hash2, "Synthetic fixture output is non-deterministic!")
            print(f"\n[SYNTHETIC CI DETERMINISM GUARD PASSED] Verified byte-identity on synthetic fixture: {hash1}")

class TestReinforcedDeterminism(unittest.TestCase):
    def test_rename_recreate_byte_identity(self):
        # Skip local telemetry test if data/processed is missing (e.g. clean CI runner checkout)
        has_telemetry = os.path.exists(PROC_DIR) and len(os.listdir(PROC_DIR)) > 0
        if not has_telemetry:
            self.skipTest("Skipping full telemetry determinism test — telemetry directory missing (handled by TestSyntheticCIDeterminismFixture).")

        self.assertTrue(os.path.exists(RESULTS_JSON), f"Source results.json missing at {RESULTS_JSON}")
        frozen_registry_sha256 = get_frozen_registry_sha256("001")
        
        # 1. COPY original file to backup location (non-destructive)
        shutil.copy2(RESULTS_JSON, BACKUP_JSON)
        # Delete original to force true recreation by reproduce.py
        os.remove(RESULTS_JSON)
        self.assertFalse(os.path.exists(RESULTS_JSON), "results.json was not successfully deleted for recreation test!")

        try:
            # 2. RUN pipeline with explicit baseline dates from root CWD
            reproduce_script = os.path.join(NOTE_DIR, "reproduce.py")
            cmd = [sys.executable, reproduce_script, "--start-date", "2025-06-01", "--end-date", "2026-06-30"]
            
            # Execute with root CWD to verify path anchor independence (Blocker 1)
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
