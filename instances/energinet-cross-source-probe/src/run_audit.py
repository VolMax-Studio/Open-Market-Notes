"""
run_audit.py — Energinet Cross-Source Verification for Note #003
================================================================
Verifies whether the 44 missing synchronous intervals of 2025-08-10 (DK1 & DK2)
on the ENTSO-E Transparency Platform exist in Energinet's Energi Data Service.
"""

import os
import json
import requests
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.dirname(SCRIPT_DIR)
REPO_DIR = os.path.dirname(os.path.dirname(INSTANCE_DIR))
DATA_DIR = os.path.join(INSTANCE_DIR, "data")
DK1_PATH = os.path.join(REPO_DIR, "notes", "003-entsoe-imbalance-baseline", "data", "processed", "imbalance_DK_1.feather")

def run():
    print("=== 1. LOADING NOTE #003 DK_1 BASELINE ===")
    df_dk1 = pd.read_feather(DK1_PATH)
    df_dk1['dt_utc'] = pd.to_datetime(df_dk1['index']).dt.tz_convert('UTC')

    day_start = pd.Timestamp('2025-08-10 00:00:00', tz='UTC')
    day_end = pd.Timestamp('2025-08-10 23:45:00', tz='UTC')
    nominal_day = pd.date_range(day_start, day_end, freq='15min')

    present_timestamps = set(df_dk1['dt_utc'])
    missing_day_stamps = [ts for ts in nominal_day if ts not in present_timestamps]
    print(f"Target missing synchronous timestamps (2025-08-10): {len(missing_day_stamps)}")

    print("\n=== 2. FETCHING ENERGINET EDS ImbalancePrice ===")
    url = "https://api.energidataservice.dk/dataset/ImbalancePrice?start=2025-08-10T00:00&end=2025-08-11T00:00&limit=500"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    eds_data = r.json().get('records', [])
    print(f"Total records returned by Energinet EDS: {len(eds_data)}")

    eds_lookup = {}
    for rec in eds_data:
        ts_str = rec['TimeUTC']
        area = rec['PriceArea']
        eds_lookup[(ts_str, area)] = rec['ImbalancePriceEUR']

    print("\n=== 3. EVALUATING 88 LOOKUPS AGAINST FROZEN DECISION RULE ===")
    results = []
    counts = {'CONFIRMED': 0, 'NOT_CONFIRMED': 0, 'NULL_VALUED': 0, 'UNRESOLVED': 0}

    for ts in missing_day_stamps:
        ts_str = ts.strftime('%Y-%m-%dT%H:%M:%S')
        for area, zone_label in [('DK1', 'DK_1'), ('DK2', 'DK_2')]:
            key = (ts_str, area)
            if key not in eds_lookup:
                verdict = 'NOT_CONFIRMED'
                val = None
            else:
                val = eds_lookup[key]
                if val is None or pd.isna(val):
                    verdict = 'NULL_VALUED'
                else:
                    verdict = 'CONFIRMED'
            counts[verdict] += 1
            results.append({
                'TimeUTC': ts_str,
                'PriceArea': area,
                'Note003_Zone': zone_label,
                'ImbalancePriceEUR': val,
                'Verdict': verdict
            })

    df_res = pd.DataFrame(results)
    
    csv_out = os.path.join(DATA_DIR, "energinet_lookup_results.csv")
    df_res.to_csv(csv_out, index=False)
    print(f"Detailed lookup table saved to: {csv_out}")

    summary = {
        "instance": "energinet-cross-source-probe",
        "target_date": "2025-08-10",
        "total_lookups": 88,
        "counts": counts,
        "verdict_ratio": f"{counts['CONFIRMED']}/88 CONFIRMED"
    }

    json_out = os.path.join(INSTANCE_DIR, "results.json")
    with open(json_out, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n=== AGGREGATE SUMMARY ===")
    for k, v in counts.items():
        print(f"{k:15s}: {v:2d} / 88")

if __name__ == "__main__":
    run()
