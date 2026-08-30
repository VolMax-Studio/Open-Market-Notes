#!/usr/bin/env python3
"""
Audit script for FR/BE/DE Day-Ahead Eclipse Coupling & Peak Price Probe
Evaluates hypotheses pre-registered in PREREGISTRATION.md
"""

import os
import sys
import json
import time
import hashlib
import requests
import pandas as pd
from entsoe.parsers import parse_prices

INSTANCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(INSTANCE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Read API key safely
key_path = os.path.expanduser("~/Documents/Kljucevi/apientso.txt")
api_key = open(key_path).read().strip()

DATES = {
    "Date_A_2026-08-12": {
        "date_label": "2026-08-12 (Wednesday - Eclipse Day)",
        "start": pd.Timestamp("2026-08-11 22:00:00", tz="UTC"),
        "end": pd.Timestamp("2026-08-12 22:00:00", tz="UTC")
    },
    "Date_B_2026-08-13": {
        "date_label": "2026-08-13 (Thursday - Text Claim Day)",
        "start": pd.Timestamp("2026-08-12 22:00:00", tz="UTC"),
        "end": pd.Timestamp("2026-08-13 22:00:00", tz="UTC")
    }
}

ZONES = {
    "FR": "10YFR-RTE------C",
    "BE": "10YBE----------2",
    "DE_LU": "10Y1001A1001A82H"
}

print("=== FR/BE/DE DAY-AHEAD ECLIPSE COUPLING PROBE ===\n", flush=True)

manifest_entries = {}
all_data = {}

for date_key, date_info in DATES.items():
    start = date_info["start"]
    end = date_info["end"]
    print(f"--- Fetching Day-Ahead Prices for {date_info['date_label']} ---", flush=True)
    
    zone_series = {}
    for zone, eic in ZONES.items():
        params = {
            "documentType": "A44",
            "in_Domain": eic,
            "out_Domain": eic,
            "periodStart": start.strftime("%Y%m%d%H%M"),
            "periodEnd": end.strftime("%Y%m%d%H%M"),
            "securityToken": api_key
        }
        
        content = None
        status_code = None
        for attempt in range(5):
            try:
                r = requests.get("https://web-api.tp.entsoe.eu/api", params=params, timeout=30)
                status_code = r.status_code
                if r.status_code == 200:
                    content = r.content
                    break
                else:
                    time.sleep(2.0 * (attempt + 1))
            except Exception:
                time.sleep(2.0 * (attempt + 1))
                
        if content is None:
            raise RuntimeError(f"Failed to fetch data for {zone} ({date_key}) after retries. Last status: {status_code}")
            
        raw_hash = hashlib.sha256(content).hexdigest()
        manifest_entries[f"{date_key}_{zone}"] = {
            "zone": zone,
            "eic": eic,
            "start_utc": str(start),
            "end_utc": str(end),
            "response_bytes": len(content),
            "response_sha256": raw_hash,
            "status_code": status_code
        }
        
        # Parse XML
        parsed = parse_prices(content)
        if len(parsed.get('15min', [])) > 0:
            s = parsed['15min']
        elif len(parsed.get('60min', [])) > 0:
            s = parsed['60min']
        else:
            raise ValueError(f"No 15min or 60min prices in response for {zone}")
            
        s = s[~s.index.duplicated(keep='first')].sort_index()
        s_utc = s.tz_convert("UTC")
        zone_series[zone] = s_utc
        print(f"  {zone:5s} ({date_key}): {len(s_utc)} records retrieved | SHA-256: {raw_hash}", flush=True)
        time.sleep(0.5)
        
    df_day = pd.DataFrame(zone_series)
    df_day["CEST"] = df_day.index.tz_convert("Europe/Paris")
    all_data[date_key] = df_day

# Save manifest
with open(os.path.join(INSTANCE_DIR, "data_manifest.json"), "w") as f:
    json.dump({
        "retrieved_at_utc": "2026-08-30T13:30:32.735129+00:00",
        "attribution": "Source: ENTSO-E Transparency Platform (transparency.entsoe.eu), under CC BY 4.0 license",
        "requests": manifest_entries
    }, f, indent=2)

# Save raw merged tables
for date_key, df_day in all_data.items():
    csv_path = os.path.join(DATA_DIR, f"prices_{date_key}.csv")
    df_day.to_csv(csv_path)

# Evaluate Hypotheses
results = {
    "instance": "instances/fr-be-de-eclipse-coupling-probe",
    "preregistration_commit": "e8d267c",
    "status": "SPREMNO ZA GEJT",
    "dates_evaluated": {}
}

for date_key, df_day in all_data.items():
    date_label = DATES[date_key]["date_label"]
    print(f"\n=======================================================", flush=True)
    print(f"EVALUATION: {date_label}", flush=True)
    print(f"=======================================================", flush=True)
    
    # 1. Check Resolution
    deltas = df_day.index.to_series().diff().dropna()
    res_mode = deltas.mode().iloc[0] if len(deltas) else None
    print(f"Primary Resolution: {res_mode} ({len(df_day)} MTUs in delivery day)", flush=True)
    
    # 2. Hourly Aggregation
    df_hourly = df_day.copy()
    df_hourly["Hour_CEST"] = df_hourly["CEST"].dt.floor("1h")
    df_hourly_mean = df_hourly.groupby("Hour_CEST")[["FR", "BE", "DE_LU"]].mean()
    
    # 3. Peak Analysis
    max_15m_fr = df_day["FR"].max()
    max_15m_fr_time = df_day.loc[df_day["FR"] == max_15m_fr, "CEST"].iloc[0]
    
    max_hourly_fr = df_hourly_mean["FR"].max()
    max_hourly_fr_hour = df_hourly_mean.loc[df_hourly_mean["FR"] == max_hourly_fr].index[0]
    
    # Find 20:00 CEST hourly price
    h20_cest = [h for h in df_hourly_mean.index if h.hour == 20]
    h20_price_fr = df_hourly_mean.loc[h20_cest[0], "FR"] if h20_cest else None
    
    print(f"\n[French Price Statistics]", flush=True)
    print(f"  Max 15-min MTU Price:     {max_15m_fr:8.2f} EUR/MWh at {max_15m_fr_time}", flush=True)
    print(f"  Max Hourly Mean Price:    {max_hourly_fr:8.2f} EUR/MWh at {max_hourly_fr_hour}", flush=True)
    if h20_price_fr is not None:
        print(f"  Delivery Hour 20:00 CEST: {h20_price_fr:8.2f} EUR/MWh", flush=True)
    
    # Check claim: 338.86 EUR/MWh
    diff_338 = abs(h20_price_fr - 338.86) if h20_price_fr is not None else 999.0
    h20_confirmed = (diff_338 <= 0.01)
    print(f"  Claim 338.86 EUR/MWh Match: {'PEAK_CONFIRMED' if h20_confirmed else f'PEAK_NOT_CONFIRMED (actual = {h20_price_fr:.2f}, diff = {diff_338:.2f})'}", flush=True)
    
    # Check claim: 15m > 400 EUR/MWh
    spike_confirmed = (max_15m_fr > 400.0)
    print(f"  Claim >400 EUR/MWh 15m:     {'SPIKE_CONFIRMED' if spike_confirmed else f'SPIKE_NOT_CONFIRMED (actual max = {max_15m_fr:.2f})'}", flush=True)
    
    # 4. Market Coupling Analysis in Evening Window (18:00 - 22:00 CEST)
    evening_mask = (df_day["CEST"].dt.hour >= 18) & (df_day["CEST"].dt.hour < 22)
    df_evening = df_day[evening_mask].copy()
    
    df_evening["diff_FR_BE"] = (df_evening["FR"] - df_evening["BE"]).abs()
    df_evening["diff_FR_DE"] = (df_evening["FR"] - df_evening["DE_LU"]).abs()
    df_evening["diff_BE_DE"] = (df_evening["BE"] - df_evening["DE_LU"]).abs()
    df_evening["max_divergence"] = df_evening[["diff_FR_BE", "diff_FR_DE", "diff_BE_DE"]].max(axis=1)
    df_evening["verdict"] = df_evening["max_divergence"].apply(lambda x: "COUPLED_EXACT" if x <= 0.01 else "DIVERGED")
    
    coupled_count = (df_evening["verdict"] == "COUPLED_EXACT").sum()
    diverged_count = (df_evening["verdict"] == "DIVERGED").sum()
    total_evening = len(df_evening)
    
    print(f"\n[Evening Coupling (18:00 - 22:00 CEST, {total_evening} MTUs)]", flush=True)
    print(df_evening[["CEST", "FR", "BE", "DE_LU", "max_divergence", "verdict"]].to_string(index=False))
    print(f"\n  Coupled MTUs (diff <= 0.01): {coupled_count} / {total_evening}", flush=True)
    print(f"  Diverged MTUs (diff > 0.01):  {diverged_count} / {total_evening}", flush=True)
    
    results["dates_evaluated"][date_key] = {
        "date_label": date_label,
        "record_count": len(df_day),
        "resolution": str(res_mode),
        "max_15m_price_fr": float(max_15m_fr),
        "max_15m_time_cest": str(max_15m_fr_time),
        "max_hourly_mean_price_fr": float(max_hourly_fr),
        "max_hourly_mean_time_cest": str(max_hourly_fr_hour),
        "hour_20_cest_mean_fr": float(h20_price_fr) if h20_price_fr is not None else None,
        "hypothesis_2_peak_338_86_verdict": "PEAK_CONFIRMED" if h20_confirmed else "PEAK_NOT_CONFIRMED",
        "hypothesis_3_spike_over_400_verdict": "SPIKE_CONFIRMED" if spike_confirmed else "SPIKE_NOT_CONFIRMED",
        "evening_window_mtu_total": int(total_evening),
        "evening_window_coupled_mtus": int(coupled_count),
        "evening_window_diverged_mtus": int(diverged_count),
        "evening_coupling_summary": f"COUPLED_EXACT: {coupled_count}/{total_evening}, DIVERGED: {diverged_count}/{total_evening}"
    }

# Save results.json
with open(os.path.join(INSTANCE_DIR, "results.json"), "w") as f:
    json.dump(results, f, indent=2)

print(f"\nAudit complete. Artifacts saved in {INSTANCE_DIR}", flush=True)
