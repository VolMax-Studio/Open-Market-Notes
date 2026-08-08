import os
import sys
import json
import glob
import pandas as pd
import numpy as np

# Path resolution for manifest and processed feather files
data_dir = '.'
manifest_path = os.path.join(data_dir, 'data_manifest.json')
if not os.path.exists(manifest_path):
    manifest_path = os.path.join(data_dir, 'data', 'data_manifest.json')

with open(manifest_path, 'r') as f:
    manifest_data = json.load(f)

proc_dir = os.path.join(data_dir, 'data', 'processed')
if not os.path.exists(proc_dir):
    proc_dir = os.path.join(data_dir, 'processed')

proc_files = sorted(glob.glob(os.path.join(proc_dir, "imbalance_*.feather")))

print("=== EXECUTING VOLMAX NOTE #3: ENTSO-E IMBALANCE DURATION BASELINE ANALYSIS ===")
print(f"Found {len(proc_files)} processed zone datasets in {proc_dir}.")

results = {}

for pfile in proc_files:
    basename = os.path.basename(pfile)
    zone = basename.replace("imbalance_", "").replace(".feather", "")
    
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
        
    cols = [c for c in df.columns if c not in ['index', 'DateTime']]
    
    # Regime determination according to frozen rules
    if len(cols) == 1:
        regime = "SINGLE_PRICING"
        p_short = df[cols[0]]
        p_long = df[cols[0]]
    else:
        p_long_temp = df['Long'] if 'Long' in cols else df.iloc[:, 0]
        p_short_temp = df['Short'] if 'Short' in cols else df.iloc[:, 1]
        valid_mask = p_long_temp.notna() & p_short_temp.notna()
        diff = (p_long_temp[valid_mask] - p_short_temp[valid_mask]).abs()
        if (diff < 1e-4).all():
            regime = "SINGLE_PRICING"
            p_short = p_short_temp
            p_long = p_long_temp
        else:
            regime = "DUAL_PRICING"
            p_short = df['Short']
            p_long = df['Long']
            
    print(f"\n--------------------------------------------------")
    print(f"ZONE: {zone} | REGIME: {regime} | TOTAL INTERVALS: {len(df)}")
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
