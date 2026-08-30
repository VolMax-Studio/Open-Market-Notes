"""
run_audit.py — Energinet Cross-Source Verification for Residual Gaps
====================================================================
Evaluates the 11 residual missing lookups across DK1 and DK2 from Note #003
against Energinet's Energi Data Service (ImbalancePrice).
"""

import os
import json
import hashlib
import requests
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(INSTANCE_DIR, "data")
TARGET_SET_PATH = os.path.join(INSTANCE_DIR, "target_set.json")

def run():
    print("=== 1. LOADING FROZEN TARGET SET ===")
    with open(TARGET_SET_PATH) as f:
        target_data = json.load(f)
    
    lookups = target_data['lookups']
    print(f"Total lookups to evaluate: {len(lookups)}")

    print("\n=== 2. FETCHING ENERGINET EDS ImbalancePrice FOR TARGET WINDOWS ===")
    windows = [
        ("2025-07-07T00:00", "2025-07-12T00:00"), # Covers July 7, 8, 11
        ("2026-04-30T00:00", "2026-05-01T00:00")  # Covers April 30
    ]

    eds_records = []
    manifest_chunks = []

    for start_w, end_w in windows:
        url = f"https://api.energidataservice.dk/dataset/ImbalancePrice?start={start_w}&end={end_w}&limit=2000"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        raw_bytes = r.content
        data = r.json().get('records', [])
        print(f"Window {start_w} -> {end_w}: returned {len(data)} records")
        eds_records.extend(data)
        manifest_chunks.append({
            "endpoint": url,
            "response_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "record_count": len(data)
        })

    manifest = {
        "retrieved_at_utc": pd.Timestamp.utcnow().isoformat(),
        "attribution": "Source: Energinet (www.energidataservice.dk)",
        "chunks": manifest_chunks,
        "total_records": len(eds_records)
    }
    manifest_path = os.path.join(INSTANCE_DIR, "data_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Data manifest written to: {manifest_path}")

    # Build lookup map (TimeUTC, PriceArea) -> ImbalancePriceEUR
    eds_lookup = {}
    for rec in eds_records:
        ts_str = rec['TimeUTC']
        area = rec['PriceArea']
        eds_lookup[(ts_str, area)] = rec['ImbalancePriceEUR']

    print("\n=== 3. EVALUATING 11 LOOKUPS AGAINST FROZEN DECISION RULE ===")
    results = []
    counts = {'CONFIRMED': 0, 'NOT_CONFIRMED': 0, 'NULL_VALUED': 0, 'UNRESOLVED': 0}

    for lk in lookups:
        ts_str = lk['TimeUTC']
        area = lk['PriceArea']
        zone_label = lk['zone']
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
    
    os.makedirs(DATA_DIR, exist_ok=True)
    csv_out = os.path.join(DATA_DIR, "energinet_lookup_results.csv")
    df_res.to_csv(csv_out, index=False)
    print(f"Lookup results table saved to: {csv_out}")

    summary = {
        "instance": "energinet-residual-gaps-probe",
        "target_set_sha256": hashlib.sha256(open(TARGET_SET_PATH, 'rb').read()).hexdigest(),
        "total_lookups": len(lookups),
        "counts": counts,
        "verdict_ratio": f"{counts['CONFIRMED']}/{len(lookups)} CONFIRMED"
    }

    json_out = os.path.join(INSTANCE_DIR, "results.json")
    with open(json_out, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n=== AGGREGATE SUMMARY ===")
    for k, v in counts.items():
        print(f"{k:15s}: {v:2d} / {len(lookups)}")

    print("\n=== COMPLETE VERDICT TABLE ===")
    print(df_res.to_string(index=False))

if __name__ == "__main__":
    run()
