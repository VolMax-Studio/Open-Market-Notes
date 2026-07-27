import os
import glob
import pandas as pd
import numpy as np
from collections import Counter

proc_files = sorted(glob.glob("./data/processed/imbalance_*.feather"))

print("=== VERIFYING M1 DURATION HISTOGRAMS & SEPARATION LOGIC ===")

for pfile in proc_files:
    zone = os.path.basename(pfile).replace("imbalance_", "").replace(".feather", "")
    df = pd.read_feather(pfile)
    cols = [c for c in df.columns if c not in ['index', 'DateTime']]
    
    if 'Short' in cols:
        price = df['Short']
    else:
        price = df[cols[0]]
        
    above = (price >= 100.0).values
    
    # Method 1: Strict contiguous blocks (no gap bridging)
    blocks_nobridge = []
    curr = 0
    for val in above:
        if val:
            curr += 1
        else:
            if curr > 0:
                blocks_nobridge.append(curr * 15)
                curr = 0
    if curr > 0:
        blocks_nobridge.append(curr * 15)
        
    # Method 2: With <30 min (1-interval) gap bridging
    blocks_bridged = []
    curr = 0
    gap = 0
    for val in above:
        if val:
            if gap == 1:
                curr += 2  # add 1 bridged gap + 1 current
                gap = 0
            else:
                if curr > 0:
                    blocks_bridged.append(curr * 15)
                curr = 1
                gap = 0
        else:
            if curr > 0:
                gap += 1
                if gap >= 2:
                    blocks_bridged.append(curr * 15)
                    curr = 0
                    gap = 0
    if curr > 0:
        blocks_bridged.append(curr * 15)
        
    hist_nobridge = Counter(blocks_nobridge)
    hist_bridged = Counter(blocks_bridged)
    
    print(f"\n--- ZONE: {zone} ---")
    print(f"NO-BRIDGE Total Events: {len(blocks_nobridge)}")
    print("NO-BRIDGE Histogram (minutes: count):", sorted(hist_nobridge.items())[:10])
    p50_nb = np.percentile(blocks_nobridge, 50) if blocks_nobridge else 0
    p90_nb = np.percentile(blocks_nobridge, 90) if blocks_nobridge else 0
    p95_nb = np.percentile(blocks_nobridge, 95) if blocks_nobridge else 0
    p99_nb = np.percentile(blocks_nobridge, 99) if blocks_nobridge else 0
    print(f"NO-BRIDGE Percentiles -> P50:{p50_nb}, P90:{p90_nb}, P95:{p95_nb}, P99:{p99_nb}, Mean:{np.mean(blocks_nobridge):.1f}")
    
    print(f"\nBRIDGED (<30m gap) Total Events: {len(blocks_bridged)}")
    print("BRIDGED Histogram (minutes: count):", sorted(hist_bridged.items())[:10])
    p50_b = np.percentile(blocks_bridged, 50) if blocks_bridged else 0
    p90_b = np.percentile(blocks_bridged, 90) if blocks_bridged else 0
    p95_b = np.percentile(blocks_bridged, 95) if blocks_bridged else 0
    p99_b = np.percentile(blocks_bridged, 99) if blocks_bridged else 0
    print(f"BRIDGED Percentiles -> P50:{p50_b}, P90:{p90_b}, P95:{p95_b}, P99:{p99_b}, Mean:{np.mean(blocks_bridged):.1f}")
