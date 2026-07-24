import os
import sys
import json
import hashlib
import glob
import pandas as pd
from datetime import datetime

# ENTSO-E API requires an API key passed via ENTSOE_API_KEY environment variable.
# Fallback support for public zip/CSV cache files in ./data/raw_cache

ZONES = ['DE_LU', 'FR', 'BE', 'NL']

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def update_manifest(filepath, file_hash):
    manifest_path = './data/data_manifest.json'
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            try:
                manifest = json.load(f)
            except Exception:
                pass
    
    basename = os.path.basename(filepath)
    if basename in manifest:
        expected_hash = manifest[basename]["sha256"]
        if file_hash != expected_hash:
            print(f"CRITICAL ERROR: SHA-256 mismatch for {basename}!")
            print(f"  Expected: {expected_hash}")
            print(f"  Got:      {file_hash}")
            raise ValueError(f"Integrity check failed: Hash mismatch for {basename}")
        else:
            print(f"Integrity check passed: SHA-256 matches for {basename}.")
    else:
        print(f"Registering new entry in manifest: {basename}")
        manifest[basename] = {
            "sha256": file_hash,
            "size_bytes": os.path.getsize(filepath)
        }
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=4)

def download_entsoe_imbalance(api_key=None):
    raw_dir = './data/raw_cache'
    proc_dir = './data/processed'
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)

    api_key = api_key or os.environ.get('ENTSOE_API_KEY')
    
    if api_key:
        from entsoe import EntsoePandasClient
        client = EntsoePandasClient(api_key=api_key)
        start = pd.Timestamp('2025-06-01', tz='UTC')
        end = pd.Timestamp('2026-06-30 23:59:59', tz='UTC')
        
        for zone in ZONES:
            print(f"\n==========================================")
            print(f"FETCHING ENTSO-E IMBALANCE PRICES FOR {zone}")
            print(f"==========================================")
            try:
                df = client.query_imbalance_prices(country_code=zone, start=start, end=end)
                csv_path = os.path.join(raw_dir, f"imbalance_{zone}_202506_202606.csv")
                df.to_csv(csv_path)
                file_hash = compute_sha256(csv_path)
                update_manifest(csv_path, file_hash)
                
                proc_path = os.path.join(proc_dir, f"imbalance_{zone}.feather")
                df.reset_index().to_feather(proc_path)
                print(f"Saved processed imbalance prices to {proc_path}")
            except Exception as e:
                print(f"API Error fetching {zone}: {e}")
    else:
        print("ENTSOE_API_KEY environment variable not found.")
        print("Pipeline fallback: scanning ./data/raw_cache for pre-acquired CSV files...")
        csv_files = glob.glob(os.path.join(raw_dir, "imbalance_*.csv"))
        if not csv_files:
            print("No cached CSV files found in ./data/raw_cache.")
            print("To run data pull, export ENTSOE_API_KEY=<token> or place raw CSV files in ./data/raw_cache.")
        else:
            for csv_file in csv_files:
                print(f"Processing raw cache file: {csv_file}")
                file_hash = compute_sha256(csv_file)
                update_manifest(csv_file, file_hash)

if __name__ == '__main__':
    download_entsoe_imbalance()
