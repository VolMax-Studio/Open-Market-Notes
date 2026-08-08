import os
import json
import glob
import re
import argparse
import pandas as pd
import numpy as np

def main():
    parser = argparse.ArgumentParser(description="ENTSO-E Baseline & Recurrence Analysis Script")
    parser.add_argument('--data-dir', type=str, default='.', help='Input data and manifest directory')
    parser.add_argument('--out-dir', type=str, default=None, help='Output directory for results.json summary')
    parser.add_argument('--window-tag', type=str, default='202506_202606', help='Timeframe tag for matching manifest entries')
    args = parser.parse_args()

    data_dir = args.data_dir
    out_dir = args.out_dir or data_dir
    window_tag = args.window_tag

    os.makedirs(out_dir, exist_ok=True)

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
        
        escaped_tag = re.escape(window_tag)
        matching_entries = [
            v for k, v in manifest_files_dict.items() 
            if re.search(rf'imbalance_{zone}_{escaped_tag}\.csv', k)
        ]
        
        if not matching_entries:
            raise ValueError(f"MANIFEST ABORT: No registered provenance entry found in manifest for zone {zone} with window tag '{window_tag}'!")
            
        manifest_entry = matching_entries[0]
            
        regime = manifest_entry.get("frozen_regime")
        m1_col_name = manifest_entry.get("m1_shortage_col")
        m2_col_name = manifest_entry.get("m2_surplus_col")
        
        if not regime or not m1_col_name or not m2_col_name:
            raise ValueError(f"MANIFEST ABORT: Incomplete regime metadata for zone {zone} in manifest! regime={regime}, m1_col={m1_col_name}, m2_col={m2_col_name}")
            
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
        
        def compute_m1(df_sub, price_series, threshold):
            timestamps = pd.to_datetime(df_sub.index, utc=True)
            above = (price_series >= threshold).values
            events = []
            gap_breaches_count = 0
            bridged_events_count = 0
            curr_rows = []
            curr_had_gap = False
            
            for i, val in enumerate(above):
                if val:
                    if curr_rows:
                        prev_ts = timestamps[curr_rows[-1]]
                        curr_ts = timestamps[i]
                        gap_min = (curr_ts - prev_ts).total_seconds() / 60.0
                        if gap_min > 15.0:
                            gap_breaches_count += 1
                            curr_had_gap = True
                            events.append(len(curr_rows) * 15)
                            curr_rows = [i]
                        else:
                            curr_rows.append(i)
                    else:
                        curr_rows.append(i)
                        curr_had_gap = False
                else:
                    if curr_rows:
                        if curr_had_gap:
                            bridged_events_count += 1
                        events.append(len(curr_rows) * 15)
                        curr_rows = []
                        curr_had_gap = False
                        
            if curr_rows:
                if curr_had_gap:
                    bridged_events_count += 1
                events.append(len(curr_rows) * 15)
                
            if not events:
                return {"count": 0, "mean_min": 0, "median_min": 0, "p90_min": 0, "p95_min": 0, "p99_min": 0, "max_min": 0, "gap_breaches_count": 0, "bridged_events_count": 0}
                
            return {
                "count": len(events),
                "mean_min": round(float(np.mean(events)), 1),
                "median_min": round(float(np.median(events)), 1),
                "p90_min": round(float(np.percentile(events, 90, method='linear')), 1),
                "p95_min": round(float(np.percentile(events, 95, method='linear')), 1),
                "p99_min": round(float(np.percentile(events, 99, method='linear')), 1),
                "max_min": int(np.max(events)),
                "gap_breaches_count": gap_breaches_count,
                "bridged_events_count": bridged_events_count
            }

        m1_100 = compute_m1(df, p_short, 100.0)
        m1_250 = compute_m1(df, p_short, 250.0)
        
        print(f"M1 Scarcity >= €100/MWh (Shortage): {m1_100['count']} events | Mean: {m1_100['mean_min']}m | P90: {m1_100['p90_min']}m | Max: {m1_100['max_min']}m | Gap Breaches: {m1_100['gap_breaches_count']} (Bridged Events: {m1_100['bridged_events_count']})")
        print(f"M1 Scarcity >= €250/MWh (Shortage): {m1_250['count']} events | Mean: {m1_250['mean_min']}m | P90: {m1_250['p90_min']}m | Max: {m1_250['max_min']}m | Gap Breaches: {m1_250['gap_breaches_count']} (Bridged Events: {m1_250['bridged_events_count']})")
        
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

    out_summary_path = os.path.join(out_dir, 'results.json')
    with open(out_summary_path, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"\n=== ANALYSIS COMPLETE: Saved {out_summary_path} ===")

if __name__ == '__main__':
    main()
