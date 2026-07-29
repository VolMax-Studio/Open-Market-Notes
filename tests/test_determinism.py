#!/usr/bin/env python3
import os
import sys
import json
import shutil
import hashlib
import unittest
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(BASE_DIR, "notes_registry.json")
NOTE_DIR = os.path.join(BASE_DIR, "notes", "001-nem-duration-baseline")
RESULTS_JSON = os.path.join(NOTE_DIR, "results.json")
BACKUP_JSON = os.path.join(NOTE_DIR, "results.json.bak")

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def get_registry_sha256(note_num="001"):
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)
    for entry in registry:
        if entry["note_number"] == note_num:
            return entry["results_sha256"]
    return None

class TestReinforcedDeterminism(unittest.TestCase):
    def test_rename_recreate_byte_identity(self):
        self.assertTrue(os.path.exists(RESULTS_JSON), f"Source results.json missing at {RESULTS_JSON}")
        expected_registry_sha256 = get_registry_sha256("001")
        
        # 1. RENAME original file to force true recreation
        shutil.move(RESULTS_JSON, BACKUP_JSON)
        self.assertFalse(os.path.exists(RESULTS_JSON), "results.json was not successfully moved!")

        try:
            # 2. RUN pipeline with explicit baseline dates from root CWD
            reproduce_script = os.path.join(NOTE_DIR, "reproduce.py")
            cmd = [sys.executable, reproduce_script, "--start-date", "2025-06-01", "--end-date", "2026-06-30"]
            
            # Execute with root CWD to verify anchor independence (Blocker 1)
            res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Pipeline execution failed:\n{res.stderr}")
            
            # 3. VERIFY RECREATION
            self.assertTrue(os.path.exists(RESULTS_JSON), "Pipeline failed to RECREATE results.json!")
            
            # 4. VERIFY BYTE-IDENTITY (SHA-256 Match)
            recreated_sha256 = compute_sha256(RESULTS_JSON)
            backup_sha256 = compute_sha256(BACKUP_JSON)
            
            self.assertEqual(recreated_sha256, backup_sha256, "Recreated results.json does not match backup hash!")
            self.assertEqual(recreated_sha256, expected_registry_sha256, f"Hash mismatch with registry! Expected {expected_registry_sha256}, got {recreated_sha256}")
            print(f"\n[REINFORCED DETERMINISM TEST PASSED] Recreated results_sha256: {recreated_sha256}")
            
        finally:
            # Clean up backup and ensure results.json exists
            if os.path.exists(BACKUP_JSON):
                if not os.path.exists(RESULTS_JSON):
                    shutil.move(BACKUP_JSON, RESULTS_JSON)
                else:
                    os.remove(BACKUP_JSON)

if __name__ == '__main__':
    unittest.main()
