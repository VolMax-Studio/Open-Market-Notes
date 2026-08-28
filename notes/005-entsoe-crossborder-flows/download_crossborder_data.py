#!/usr/bin/env python3
"""
Open Market Note #005 — ENTSO-E Cross-Border Physical Flows
L0/L1 Dry-Run API Data Ingestion Script

Fetches physical flow data between key European bidding zones via ENTSO-E TP RESTful API.
License: CC BY 4.0 (ENTSO-E Terms of Use Article 2.5, Open Data List Item #18: Physical flows 12.1.g)
"""

import os
import sys
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# ENTSO-E EIC Codes for evaluated bidding zones
EIC_MAP = {
    'NL': '10YNL----------L',
    'DE': '10Y1001A1001A83F',
    'BE': '10YBE----------2',
    'AT': '10YAT-APG------L',
    'DK1': '10YDK-1--------W',
    'FR': '10YFR-RTE------C'
}

def get_api_token():
    token_path = "/home/volmax-studio/Documents/Kljucevi/apientso.txt"
    if os.path.exists(token_path):
        with open(token_path, "r") as f:
            return f.read().strip()
    return os.environ.get("ENTSOE_API_TOKEN", "")

def dry_run_physical_flow(in_domain, out_domain, start_str="202606010000", end_str="202606020000"):
    token = get_api_token()
    if not token:
        print("[ERROR] ENTSO-E API token not found.")
        sys.exit(1)
        
    url = "https://web-api.tp.entsoe.eu/api"
    params = {
        'securityToken': token,
        'documentType': 'A11',  # Physical Flow
        'in_Domain': EIC_MAP[in_domain],
        'out_Domain': EIC_MAP[out_domain],
        'periodStart': start_str,
        'periodEnd': end_str
    }
    
    print(f"[L0 API CHECK] Fetching Physical Flow: {out_domain} -> {in_domain} ({start_str} to {end_str})...")
    try:
        res = requests.get(url, params=params, timeout=30)
        print(f"[HTTP Status] {res.status_code}")
        
        if res.status_code == 200:
            root = ET.fromstring(res.text)
            ns = {'ns': 'urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0'}
            timeseries = root.findall('.//ns:TimeSeries', ns) if 'urn:iec62325' in res.text else root.findall('.//TimeSeries')
            print(f"[SUCCESS] Payload received. TimeSeries elements found: {len(timeseries) if timeseries else 'XML parsed (standard format)'}")
            return True
        else:
            print(f"[FAILED] API Error Payload:\n{res.text[:500]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[NETWORK OFFLINE / RESTRICTED] Cannot connect to ENTSO-E API: {e}")
        return False

if __name__ == '__main__':
    print("=== Open Market Note #005 — L0 Ingestion Dry-Run ===")
    success = dry_run_physical_flow('NL', 'DE')
    if success:
        print("[L0 VERIFICATION PASSED] API endpoint physical flows (A11) active and responsive.")
    else:
        print("[L0 VERIFICATION FAILED] Inspect response payload.")
