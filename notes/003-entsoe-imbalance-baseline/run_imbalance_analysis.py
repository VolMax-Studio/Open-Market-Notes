import os
import sys
import json
import glob
import re
import argparse
import pandas as pd
import numpy as np

def main():
    parser = argparse.ArgumentParser(description="ENTSO-E Baseline & Recurrence Analysis Script")
    parser.add_argument('--data-dir', type=str, default='.', help='Input data and manifest directory')
    args = parser.parse_args()

    data_dir = args.data_dir
    manifest_path = os.path.join(data_dir, 'data_manifest.json')
    if not os.path.exists(manifest_path):
        manifest_path = os.path.join(data_dir, 'data', 'data_manifest.json')

    if not os.path.exists(manifest_path):
        raise ValueError(f"MANIFEST ABORT: data_manifest.json missing at {manifest_path}")

    with open(manifest_path, 'r') as f:
        manifest_data = json.load(f)

    manifest_files_list = manifest_data.get("files", [])
    manifest_files_dict = {item["file_name"]: item for item in manifest_files_list if isinstance(item, dict) and "file_name" in item}

    proc_dir = os.path.join(data_dir, 'data', 'processed')
    if not os.path.exists(proc_dir):
        proc_dir = os.path.join(data_dir, 'processed')

    if not os.path.exists(proc_dir):
        raise ValueError(f"PROCESS DIR ABORT: Processed feather directory missing at {proc_dir}")

    proc_files = sorted(glob.glob(os.path.join(proc_dir, "imbalance_*.feather")))
    if not proc_files:
        raise ValueError(f"PROCESS DIR ABORT: No processed feather files found in {proc_dir}")

    print("=== EXECUTING VOLMAX NOTE #3: ENTSO-E IMBALANCE DURATION BASELINE ANALYSIS ===")
    print(f"Found {len(proc_files)} processed zone datasets in {proc_dir}.")

    results = {}

    for pfile in proc_files:
        basename = os.path.basename(pfile)
        zone = basename.replace("imbalance_", "").replace(".feather", "")
        
        # Exact zone manifest lookup with zero ambiguity and zero silent fallbacks
        matching_entries = [
            v for k, v in manifest_files_dict.items() 
            if re.search(rf'imbalance_{zone}_\d{{6}}_\d{{6}}\.csv', k)
        ]
        
        if not matching_entries:
            raise ValueError(f"MANIFEST ABORT: No registered provenance entry found in manifest for zone {zone}!")
            
        if len(matching_entries) > 1:
            # Baseline timeframe filtering (202506_202606) to prevent multi-file collision in probe runs
            baseline_entries = [e for e in matching_entries if '202506_202606' in e.get("file_name", "")]
            if len(baseline_entries) == 1:
                manifest_entry = baseline_entries[0]
            else:
                raise ValueError(f"MANIFEST ABORT: Ambiguous multiple manifest entries found for zone {zone}: {[e['file_name'] for e in matching_entries]}")
        else:
            manifest_entry = matching_entries[0]
            
        regime = manifest_entry.get("frozen_regime")
        m1_col_name = manifest_entry.get("m1_shortage_col")
        m2_col_name = manifest_entry.get("m2_surplus_col")
        
        if not regime or not m1_col_name or not m2_col_name:
            raise ValueError(f"MANIFEST ABORT: Incomplete regime metadata for zone {zone} u manifest! regime={regime}, m1_col={m1_col_name}, m2_col={m2_col_name}")
            
        df = pd.read_feather(pfile)
        
        if 'index' in df.columns:
            df = df.set_index('index')
        elif 'DateTime' in df.columns:
            df = df.set_index('DateTime')
            
        df.index = pd.to_datetime(df.index)
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC').tz_convert('Europe/Brussels')
        else:
            df.index = df.index.tz_convert('Europe/Brussels')
            
        cols = list(df.columns)
        
        if m1_col_name not in cols:
            raise ValueError(f"DATASET ABORT: Required M1 shortage column '{m1_col_name}' missing from feather file for {zone}! Available: {cols}")
        if m2_col_name not in cols:
            raise ValueError(f"DATASET ABORT: Required M2 surplus column '{m2_col_name}' missing from feather file for {zone}! Available: {cols}")
            
        p_short = df[m1_col_name]
        p_long = df[m2_col_name]
        
        print(f"\n--------------------------------------------------")
        print(f"ZONE: {zone} | FROZEN REGIME (MANIFEST): {regime} | TOTAL INTERVALS: {len(df)}")
        print(f"Columns bound -> Shortage (M1): '{m1_col_name}' | Surplus (M2): '{m2_col_name}'")
        print(f"--------------------------------------------------")
        
        def compute_m1(price_series, threshold):
            above = (price_series >= threshold).values
            events = []
            curr = 0
            for val in above:
                if val:
                    curr += 1
                else:
                    if curr > 0:
                        events.append(curr * 15)  # duration in minutes
                        curr = 0
            if curr > 0:
                events.append(curr * 15)
                
            if not events:
                return {"count": 0, "mean_min": 0, "median_min": 0, "p90_min": 0, "p95_min": 0, "p99_min": 0, "max_min": 0}
                
            return {
                "count": len(events),
                "mean_min": round(float(np.mean(events)), 1),
                "median_min": round(float(np.median(events)), 1),
                "p90_min": round(float(np.percentile(events, 90)), 1),
                "p95_min": round(float(np.percentile(events, 95)), 1),
                "p99_min": round(float(np.percentile(events, 99)), 1),
                "max_min": int(np.max(events))
            }

        m1_100 = compute_m1(p_short, 100.0)
        m1_250 = compute_m1(p_short, 250.0)
        
        print(f"M1 Scarcity >= €100/MWh (Shortage): {m1_100['count']} events | Mean: {m1_100['mean_min']}m | P90: {m1_100['p90_min']}m | Max: {m1_100['max_min']}m")
        print(f"M1 Scarcity >= €250/MWh (Shortage): {m1_250['count']} events | Mean: {m1_250['mean_min']}m | P90: {m1_250['p90_min']}m | Max: {m1_250['max_min']}m")
        
        df['date'] = df.index.date
        df['is_zero_neg'] = p_long <= 0.0
        df['is_cheap_25'] = p_long <= 25.0
        
        daily = df.groupby('date').agg(
            zero_neg_hours=('is_zero_neg', lambda x: x.sum() * 0.25),
            cheap_25_hours=('is_cheap_25', lambda x: x.sum() * 0.25)
        )
        
        total_days = len(daily)
        m2_8h_pct = round(float((daily['cheap_25_hours'] >= 9.5).sum() / total_days * 100.0), 1)
        m2_4h_pct = round(float((daily['cheap_25_hours'] >= 4.8).sum() / total_days * 100.0), 1)
        
        m2_zero_8h_pct = round(float((daily['zero_neg_hours'] >= 9.5).sum() / total_days * 100.0), 1)
        m2_zero_4h_pct = round(float((daily['zero_neg_hours'] >= 4.8).sum() / total_days * 100.0), 1)

        print(f"M2 Days Meeting 4h BESS Surplus Window (>=4.8h <=€25): {m2_4h_pct}% ({int((daily['cheap_25_hours'] >= 4.8).sum())}/{total_days} days)")
        print(f"M2 Days Meeting 8h BESS Surplus Window (>=9.5h <=€25): {m2_8h_pct}% ({int((daily['cheap_25_hours'] >= 9.5).sum())}/{total_days} days)")
        print(f"M2 Zero/Negative Days (>=4.8h <=€0): {m2_zero_4h_pct}% ({int((daily['zero_neg_hours'] >= 4.8).sum())}/{total_days} days)")
        
        results[zone] = {
            "regime": regime,
            "total_intervals": len(df),
            "total_days": total_days,
            "m1_100": m1_100,
            "m1_250": m1_250,
            "m2_cheap_25": {
                "pct_4h_bess": m2_4h_pct,
                "pct_8h_bess": m2_8h_pct,
                "mean_daily_hours": round(float(daily['cheap_25_hours'].mean()), 2)
            },
            "m2_zero_neg": {
                "pct_4h_bess": m2_zero_4h_pct,
                "pct_8h_bess": m2_zero_8h_pct,
                "mean_daily_hours": round(float(daily['zero_neg_hours'].mean()), 2)
            }
        }

    out_summary_path = os.path.join(data_dir, 'results.json')
    with open(out_summary_path, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"\n=== ANALYSIS COMPLETE: Saved {out_summary_path} ===")

if __name__ == '__main__':
    main()
