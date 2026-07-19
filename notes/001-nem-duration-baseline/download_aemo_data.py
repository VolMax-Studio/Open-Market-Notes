import os
import sys
import json
import hashlib
import glob
import pandas as pd
from nemosis import dynamic_data_compiler

# Static capacity lookup from AEMO Generation Information (April 2026)
BESS_CAPACITIES = {
    # Candidates >= 50 MW
    'HPR1': 150.0,
    'VBB1': 360.0,      # Corrected to registered capacity
    'WANDB1': 123.0,    # Corrected to registered capacity
    'WDBESS1': 255.0,   # Corrected to Stage 1 registered capacity
    'TIB1': 250.0,      # Torrens Island BESS (Corrected to registered capacity)
    'HBESS1': 200.0,    # Hazelwood BESS (Corrected to registered capacity)
    'RANGEB1': 260.0,   # Rangebank BESS (Corrected to registered capacity)
    'TARBESS1': 393.0,  # Tarong BESS (Corrected to registered capacity)
    'TEMPB1': 111.0,    # Templers BESS (Corrected to registered capacity)
    'CHBESS1': 100.0,
    'BLYTHB1': 281.0,   # Blyth BESS (Corrected to registered capacity)
    'BHB1': 50.0,
    'BBATTERY1': 50.0,
    'ULPBESS1': 52.0,   # Ulinda Park BESS (Corrected to registered capacity)
    'WTAHB1': 1096.0,   # Waratah Super Battery (Corrected to registered capacity)
    'WALGRV1': 50.0,
    'KESSB1': 185.0,    # Koorangie BESS (Added, grid-forming battery)
    'RESS1': 60.0,      # Riverina BESS 1 (Added)
    'RIVNB2': 65.0,     # Riverina BESS 2 (Added)
    'CAPBES1': 100.0,   # Capital BESS (Added)

    # Excluded candidates < 50 MW
    'DPNTB1': 25.0,     # Darlington Point BESS (Corrected capacity to 25 MW, moved to Excluded)
    'TB2B1': 41.5,      # Tailem Bend 2 BESS (Corrected capacity to 41.5 MW, moved to Excluded)
    'BALB1': 30.0,
    'GANNB1': 25.0,
    'LBB1': 25.0,
    'QBYNB1': 8.0,
    'MANNUMB1': 30.0,
    'TALWB1': 41.5,
    'PIBESS1': 5.0,
    'GREENB1': 5.0,
    'GSWF1B1': 10.0,
    'BRYB1WF1': 20.0,
}

ALL_BESS_DUIDS = list(BESS_CAPACITIES.keys())

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

def purge_cache(table_name, year, month):
    # Find and delete raw CSV and feather files in the cache to free space
    raw_dir = './data/raw_cache'
    pattern = f"*{table_name}*{year}{month:02d}*"
    files_to_delete = glob.glob(os.path.join(raw_dir, pattern))
    for f in files_to_delete:
        try:
            os.remove(f)
            print(f"Purged raw cache file: {f}")
        except Exception as e:
            print(f"Failed to delete {f}: {e}")

def download_month(year, month):
    start_time = f"{year}/{month:02d}/01 00:00:00"
    # Calculate end time
    if month == 12:
        end_time = f"{year+1}/01/01 00:00:00"
    else:
        end_time = f"{year}/{month+1:02d}/01 00:00:00"
        
    raw_dir = './data/raw_cache'
    proc_dir = './data/processed'
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)

    print(f"\n==========================================")
    print(f"PROCESSING {year}-{month:02d} ({start_time} to {end_time})")
    print(f"==========================================")

    # 1. DISPATCH_UNIT_SCADA
    print(f"\n--- Downloading DISPATCH_UNIT_SCADA ---")
    try:
        scada_df = dynamic_data_compiler(
            start_time=start_time,
            end_time=end_time,
            table_name='DISPATCH_UNIT_SCADA',
            raw_data_location=raw_dir
        )
        
        # Find raw CSV file in raw_dir
        csv_files = glob.glob(os.path.join(raw_dir, f"*DISPATCH_UNIT_SCADA*{year}{month:02d}*.CSV"))
        if csv_files:
            raw_csv = csv_files[0]
            print(f"Computing hash for raw CSV: {raw_csv}")
            file_hash = compute_sha256(raw_csv)
            update_manifest(raw_csv, file_hash)
        
        # Filter BESS units
        print("Filtering and processing SCADA...")
        scada_df['SCADAVALUE'] = pd.to_numeric(scada_df['SCADAVALUE'], errors='coerce')
        scada_df['SETTLEMENTDATE'] = pd.to_datetime(scada_df['SETTLEMENTDATE'])
        filtered_scada = scada_df[scada_df['DUID'].isin(ALL_BESS_DUIDS)].copy()
        
        out_path = os.path.join(proc_dir, f"scada_{year}{month:02d}.feather")
        filtered_scada.reset_index(drop=True).to_feather(out_path)
        print(f"Saved processed SCADA to {out_path} ({len(filtered_scada)} rows)")
        
        # Purge raw files
        purge_cache('DISPATCH_UNIT_SCADA', year, month)
        
    except Exception as e:
        print(f"Error processing SCADA for {year}-{month:02d}: {e}")

    # 2. DISPATCHLOAD
    print(f"\n--- Downloading DISPATCHLOAD ---")
    try:
        dispatch_df = dynamic_data_compiler(
            start_time=start_time,
            end_time=end_time,
            table_name='DISPATCHLOAD',
            raw_data_location=raw_dir
        )
        
        # Find raw CSV file in raw_dir
        csv_files = glob.glob(os.path.join(raw_dir, f"*DISPATCHLOAD*{year}{month:02d}*.CSV"))
        if csv_files:
            raw_csv = csv_files[0]
            print(f"Computing hash for raw CSV: {raw_csv}")
            file_hash = compute_sha256(raw_csv)
            update_manifest(raw_csv, file_hash)
            
        # Filter BESS units
        print("Filtering and processing DISPATCHLOAD...")
        for col in ['TOTALCLEARED', 'INITIALMW', 'RAMPDOWNRATE', 'RAMPUPRATE']:
            if col in dispatch_df.columns:
                dispatch_df[col] = pd.to_numeric(dispatch_df[col], errors='coerce')
        dispatch_df['SETTLEMENTDATE'] = pd.to_datetime(dispatch_df['SETTLEMENTDATE'])
        filtered_dispatch = dispatch_df[dispatch_df['DUID'].isin(ALL_BESS_DUIDS)].copy()
        
        out_path = os.path.join(proc_dir, f"dispatch_{year}{month:02d}.feather")
        filtered_dispatch.reset_index(drop=True).to_feather(out_path)
        print(f"Saved processed DISPATCHLOAD to {out_path} ({len(filtered_dispatch)} rows)")
        
        # Purge raw files
        purge_cache('DISPATCHLOAD', year, month)
        
    except Exception as e:
        print(f"Error processing DISPATCHLOAD for {year}-{month:02d}: {e}")

    # 3. DISPATCHPRICE
    print(f"\n--- Downloading DISPATCHPRICE ---")
    try:
        price_df = dynamic_data_compiler(
            start_time=start_time,
            end_time=end_time,
            table_name='DISPATCHPRICE',
            raw_data_location=raw_dir
        )
        
        # Find raw CSV file in raw_dir
        csv_files = glob.glob(os.path.join(raw_dir, f"*DISPATCHPRICE*{year}{month:02d}*.CSV"))
        if csv_files:
            raw_csv = csv_files[0]
            print(f"Computing hash for raw CSV: {raw_csv}")
            file_hash = compute_sha256(raw_csv)
            update_manifest(raw_csv, file_hash)
            
        # Process and save price data (keep all rows since it's very small)
        print("Processing and saving DISPATCHPRICE...")
        price_df['RRP'] = pd.to_numeric(price_df['RRP'], errors='coerce')
        price_df['SETTLEMENTDATE'] = pd.to_datetime(price_df['SETTLEMENTDATE'])
        
        out_path = os.path.join(proc_dir, f"price_{year}{month:02d}.feather")
        price_df.reset_index(drop=True).to_feather(out_path)
        print(f"Saved processed DISPATCHPRICE to {out_path} ({len(price_df)} rows)")
        
        # Purge raw files
        purge_cache('DISPATCHPRICE', year, month)
        
    except Exception as e:
        print(f"Error processing DISPATCHPRICE for {year}-{month:02d}: {e}")

def run_pipeline():
    # Loop over the 12 months from June 2025 to May 2026
    months = [
        (2025, 6), (2025, 7), (2025, 8), (2025, 9), (2025, 10), (2025, 11), (2025, 12),
        (2026, 1), (2026, 2), (2026, 3), (2026, 4), (2026, 5), (2026, 6)
    ]
    for y, m in months:
        download_month(y, m)
    print("\n--- Pipeline Completed Successfully! ---")

if __name__ == '__main__':
    run_pipeline()
