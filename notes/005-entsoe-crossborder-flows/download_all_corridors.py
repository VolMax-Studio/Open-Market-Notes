#!/usr/bin/env python3
"""
Open Market Note #005 — Real ENTSO-E Physical Flow Data Downloader (L1)
Fetches raw A11 XML payloads for 5 evaluated corridors across 13 months (202506 - 202606).
"""

import os
import sys
import time
import json
import hashlib
import requests
from datetime import datetime, timedelta

NOTE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(NOTE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw_xml")
os.makedirs(RAW_DIR, exist_ok=True)

EIC_MAP = {
    'NL': '10YNL----------L',
    'DE': '10Y1001A1001A83F',
    'BE': '10YBE----------2',
    'AT': '10YAT-APG------L',
    'DK1': '10YDK-1--------W',
    'FR': '10YFR-RTE------C'
}

CORRIDORS = [
    {"id": "NL_DE", "out_domain": "DE", "in_domain": "NL"},
    {"id": "DE_NL", "out_domain": "NL", "in_domain": "DE"},
    {"id": "BE_NL", "out_domain": "NL", "in_domain": "BE"},
    {"id": "NL_BE", "out_domain": "BE", "in_domain": "NL"},
    {"id": "AT_DE", "out_domain": "DE", "in_domain": "AT"},
    {"id": "DE_AT", "out_domain": "AT", "in_domain": "DE"},
    {"id": "DK1_DE", "out_domain": "DE", "in_domain": "DK1"},
    {"id": "DE_DK1", "out_domain": "DK1", "in_domain": "DE"},
    {"id": "FR_BE", "out_domain": "BE", "in_domain": "FR"},
    {"id": "BE_FR", "out_domain": "FR", "in_domain": "BE"},
]

def get_api_token():
    token_path = "/home/volmax-studio/Documents/Kljucevi/apientso.txt"
    if os.path.exists(token_path):
        with open(token_path, "r") as f:
            return f.read().strip()
    return os.environ.get("ENTSOE_API_TOKEN", "")

def fetch_monthly_flow(in_code, out_code, year, month):
    token = get_api_token()
    url = "https://web-api.tp.entsoe.eu/api"
    
    start_dt = datetime(year, month, 1, 0, 0)
    if month == 12:
        end_dt = datetime(year + 1, 1, 1, 0, 0)
    else:
        end_dt = datetime(year, month + 1, 1, 0, 0)
        
    start_str = start_dt.strftime("%Y%m%d%H%M")
    end_str = end_dt.strftime("%Y%m%d%H%M")
    
    params = {
        'securityToken': token,
        'documentType': 'A11',
        'in_Domain': EIC_MAP[in_code],
        'out_Domain': EIC_MAP[out_code],
        'periodStart': start_str,
        'periodEnd': end_str
    }
    
    res = requests.get(url, params=params, timeout=30)
    if res.status_code == 200:
        return res.text
    else:
        print(f"[WARN] HTTP {res.status_code} for {out_code}->{in_code} {start_str}: {res.text[:200]}")
        return None

def download_dataset():
    print("=== Open Market Note #005 — ENTSO-E Real Telemetry Downloader ===")
    months = [
        (2025, 6), (2025, 7), (2025, 8), (2025, 9), (2025, 10), (2025, 11), (2025, 12),
        (2026, 1), (2026, 2), (2026, 3), (2026, 4), (2026, 5), (2026, 6)
    ]
    
    manifest_hashes = {}
    
    for c in CORRIDORS:
        c_id = f"{c['out_domain']}_TO_{c['in_domain']}"
        print(f"\n[FETCHING CORRIDOR] {c['out_domain']} -> {c['in_domain']}...")
        
        for yr, mo in months:
            filename = f"flow_{c_id}_{yr}{mo:02d}.xml"
            filepath = os.path.join(RAW_DIR, filename)
            
            if os.path.exists(filepath):
                print(f"  [CACHE HIT] {filename}")
            else:
                xml_data = fetch_monthly_flow(c['in_domain'], c['out_domain'], yr, mo)
                if xml_data and "<Publication_MarketDocument" in xml_data:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(xml_data)
                    print(f"  [DOWNLOADED] {filename} ({len(xml_data)} bytes)")
                else:
                    print(f"  [NO DATA / EMPTY] {filename}")
                time.sleep(0.5)  # Rate limiting courtesy pause
                
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    manifest_hashes[filename] = hashlib.sha256(f.read()).hexdigest()

    # Write data_manifest.json
    manifest_path = os.path.join(DATA_DIR, "data_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump({
            "source": "ENTSO-E Transparency Platform (DocumentType A11)",
            "license": "CC BY 4.0 (ENTSO-E ToU Item #27)",
            "download_timestamp": datetime.utcnow().isoformat() + "Z",
            "file_hashes": manifest_hashes
        }, f, indent=2)
    print(f"\n[L1 COMPLETE] Real ENTSO-E XML payload manifest written to {manifest_path}")

if __name__ == "__main__":
    download_dataset()
