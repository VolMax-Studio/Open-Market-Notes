import os
import sys
import json
import time
import hashlib
import glob
import requests
import pandas as pd
from datetime import datetime, date, timedelta, timezone

MARKET_TZ = 'Europe/London'
BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices"

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def update_manifest(filepath, file_hash, source_url, acquisition_mode):
    note_dir = os.path.dirname(os.path.abspath(__file__))
    manifest_path = os.path.join(note_dir, 'data_manifest.json')
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            try:
                manifest = json.load(f)
            except Exception:
                pass
    
    basename = os.path.basename(filepath)
    acquired_at = datetime.now(timezone.utc).isoformat()
    
    manifest[basename] = {
        "sha256": file_hash,
        "size_bytes": os.path.getsize(filepath),
        "source_url": source_url,
        "acquisition_mode": acquisition_mode,
        "acquired_at_utc": acquired_at
    }
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=4)
    print(f"Manifest registered: {basename} ({file_hash[:12]}...)")

def analyze_regime_classification(df):
    """
    Procedural Pricing Regime Detection for GB Market:
    Evaluates pairwise relation between systemSellPrice and systemBuyPrice.
    """
    print(f"\n==========================================")
    print(f"PROCEDURAL REGIME ANALYSIS: GREAT BRITAIN (GB / ELEXON)")
    print(f"==========================================")
    print(f"Columns present: {list(df.columns)}")
    
    if 'systemSellPrice' in df.columns and 'systemBuyPrice' in df.columns:
        p_sell = df['systemSellPrice']
        p_buy = df['systemBuyPrice']
    else:
        p_sell = df.iloc[:, 0]
        p_buy = df.iloc[:, 0]
        
    valid_mask = p_sell.notna() & p_buy.notna()
    total_valid = int(valid_mask.sum())
    diff = (p_sell[valid_mask] - p_buy[valid_mask]).abs()
    matches = int((diff < 1e-4).sum())
    match_pct = (matches / total_valid * 100.0) if total_valid > 0 else 0.0
    max_diff = float(diff.max()) if total_valid > 0 else 0.0
    
    if matches == total_valid and total_valid > 0:
        regime = "SINGLE_PRICING"
    else:
        regime = "DUAL_PRICING"
        
    print(f"Time Range:            {df.index.min()} to {df.index.max()}")
    print(f"Total Valid Intervals: {total_valid}")
    print(f"Matching Intervals:    {matches} ({match_pct:.2f}%)")
    print(f"Max Abs Divergence:    {max_diff:.4f} GBP/MWh")
    print(f"Empirical Outcome:     {regime}")
    
    return {
        "zone": "GB",
        "regime": regime,
        "total_valid": total_valid,
        "matching_intervals": matches,
        "match_pct": round(match_pct, 4),
        "max_diff": max_diff
    }

def fetch_elexon_system_prices(start_date="2025-06-01", end_date="2026-06-30"):
    note_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(note_dir, 'data', 'raw_cache')
    proc_dir = os.path.join(note_dir, 'data', 'processed')
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)

    start_dt = date.fromisoformat(start_date)
    end_dt = date.fromisoformat(end_date)
    csv_name = f"gb_system_prices_{start_dt.strftime('%Y%m')}_{end_dt.strftime('%Y%m')}.csv"
    csv_path = os.path.join(raw_dir, csv_name)
    
    print(f"Fetching GB System Prices from Elexon Insights API ({start_date} to {end_date})...")
    records = []
    
    curr = start_dt
    day_count = 0
    while curr <= end_dt:
        date_str = curr.isoformat()
        url = f"{BASE_URL}/{date_str}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    records.extend(data)
                elif isinstance(data, dict) and "data" in data:
                    records.extend(data["data"])
            else:
                print(f"Warning: HTTP {resp.status_code} for {date_str}")
        except Exception as e:
            print(f"Error fetching {date_str}: {e}")
            
        curr += timedelta(days=1)
        day_count += 1
        if day_count % 30 == 0:
            print(f"  Downloaded {day_count} days... ({len(records)} settlement periods)")
            time.sleep(0.1)

    df = pd.DataFrame(records)
    print(f"Fetched total {len(df)} settlement periods across {day_count} days.")
    
    # Parse timestamps localized to Europe/London
    df['startTime'] = pd.to_datetime(df['startTime'])
    df = df.set_index('startTime').tz_convert(MARKET_TZ)
    df = df.sort_index()
    
    # Save raw CSV
    df.to_csv(csv_path)
    
    source_url = f"{BASE_URL}/{{settlementDate}} (Open Elexon Insights API)"
    file_hash = compute_sha256(csv_path)
    update_manifest(csv_path, file_hash, source_url=source_url, acquisition_mode="live_open_api_query")
    
    # Run procedural regime analysis
    analyze_regime_classification(df)
    
    # Save processed Feather
    proc_path = os.path.join(proc_dir, "gb_system_prices.feather")
    df.reset_index().to_feather(proc_path)
    feather_hash = compute_sha256(proc_path)
    update_manifest(proc_path, feather_hash, source_url="Elexon Ingestion Pipeline", acquisition_mode="feather_serialization")
    print(f"Saved processed data to {proc_path}")
    return df

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Download Elexon telemetry for OMN-004")
    parser.add_argument("--start-date", default="2025-06-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", default="2026-06-30", help="End date (YYYY-MM-DD)")
    args = parser.parse_args()
    fetch_elexon_system_prices(args.start_date, args.end_date)
