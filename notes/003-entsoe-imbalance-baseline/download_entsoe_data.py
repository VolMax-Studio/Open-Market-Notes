import os
import sys
import json
import hashlib
import glob
import pandas as pd
from datetime import datetime, timezone

# ENTSO-E API requires an API key passed via ENTSOE_API_KEY environment variable.
# Baseline scope: 1 June 2025 00:00:00 CEST to 30 June 2026 23:59:59 CEST (Europe/Brussels)

ZONES = {
    'DE_LU': '10Y1001A1001A82H',
    'FR': '10YFR-RTE------C',
    'BE': '10YBE----------X',
    'NL': '10YNL----------L'
}

MARKET_TZ = 'Europe/Brussels'

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def update_manifest(filepath, file_hash, source_url, acquisition_mode):
    manifest_path = './data/data_manifest.json'
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            try:
                manifest = json.load(f)
            except Exception:
                pass
    
    basename = os.path.basename(filepath)
    acquired_at = datetime.now(timezone.utc).isoformat()
    
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
        print(f"Registering new entry with provenance metadata in manifest: {basename}")
        manifest[basename] = {
            "sha256": file_hash,
            "size_bytes": os.path.getsize(filepath),
            "source_url": source_url,
            "acquisition_mode": acquisition_mode,
            "acquired_at_utc": acquired_at
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
        start = pd.Timestamp('2025-06-01 00:00:00', tz=MARKET_TZ)
        end = pd.Timestamp('2026-06-30 23:59:59', tz=MARKET_TZ)
        
        for zone_code, eic in ZONES.items():
            print(f"\n==========================================")
            print(f"FETCHING ENTSO-E IMBALANCE PRICES FOR {zone_code} ({MARKET_TZ})")
            print(f"==========================================")
            try:
                # Query ENTSO-E imbalance prices
                df = client.query_imbalance_prices(country_code=zone_code, start=start, end=end)
                
                # Inspect and log column structure (Dual-pricing vs Single-pricing schema check)
                print(f"Schema Inspection for {zone_code}:")
                print(f"  Columns returned: {list(df.columns)}")
                print(f"  Data shape: {df.shape}")
                print(f"  Sample head:\n{df.head(2)}")
                
                csv_path = os.path.join(raw_dir, f"imbalance_{zone_code}_202506_202606.csv")
                df.to_csv(csv_path)
                
                source_endpoint = f"ENTSO-E REST API DocumentType A85 (Area EIC: {eic}, Zone: {zone_code})"
                file_hash = compute_sha256(csv_path)
                update_manifest(csv_path, file_hash, source_url=source_endpoint, acquisition_mode="live_api_query")
                
                proc_path = os.path.join(proc_dir, f"imbalance_{zone_code}.feather")
                df.reset_index().to_feather(proc_path)
                print(f"Saved processed imbalance prices to {proc_path}")
            except Exception as e:
                print(f"API Error fetching {zone_code}: {e}")
                raise e
    else:
        print("ENTSOE_API_KEY environment variable not set.")
        print("Checking data_manifest.json for registered raw cache files with proven provenance...")
        manifest_path = './data/data_manifest.json'
        if not os.path.exists(manifest_path):
            raise ValueError("ENTSOE_API_KEY required for live API ingestion and no data_manifest.json exists.")
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
            
        csv_files = glob.glob(os.path.join(raw_dir, "imbalance_*.csv"))
        if not csv_files:
            raise ValueError("ENTSOE_API_KEY required for live pre-registered API ingestion. No raw cache files found.")
            
        for csv_file in csv_files:
            basename = os.path.basename(csv_file)
            if basename not in manifest or "source_url" not in manifest[basename]:
                raise ValueError(f"File {basename} lacks verified provenance in data_manifest.json! Silent unanchored cache fallback rejected.")
            print(f"Verifying pre-registered cache file: {basename}")
            file_hash = compute_sha256(csv_file)
            update_manifest(csv_file, file_hash, source_url=manifest[basename]["source_url"], acquisition_mode="manifest_verified_cache")

if __name__ == '__main__':
    download_entsoe_imbalance()
