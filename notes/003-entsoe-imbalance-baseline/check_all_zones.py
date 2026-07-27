import os
import sys
import requests
import xml.etree.ElementTree as ET

token_path = '/home/volmax-studio/Documents/Kljucevi/apientso.txt'
with open(token_path, 'r') as f:
    api_key = f.read().strip()

url = "https://web-api.tp.entsoe.eu/api"

zones_to_test = {
    'NL': '10YNL----------L',
    'BE': '10YBE----------X',
    'FR': '10YFR-RTE------C',
    'DK_1': '10YDK-1--------W',
    'DK_2': '10YDK-2--------T',
    'FI': '10YFI-1--------U',
    'SE_3': '10YSE-EON------K',
    'AT': '10YAT-APG------L',
    'CZ': '10YCZ-CEPS-----N',
    'PL': '10YPL-AREA-----S'
}

print("=== AUDITING ALL EUROPEAN ZONES FOR ENTSO-E IMBALANCE PRICES (A85) ===")

results = {}
for name, eic in zones_to_test.items():
    params = {
        'securityToken': api_key,
        'documentType': 'A85',
        'controlArea_Domain': eic,
        'periodStart': '202506010000',
        'periodEnd': '202506020000'
    }
    res = requests.get(url, params=params)
    if res.status_code == 200:
        try:
            root = ET.fromstring(res.text)
            reasons = root.findall('.//{*}text')
            if reasons:
                results[name] = f"FAIL: {reasons[0].text[:80]}"
            else:
                ts = root.findall('.//{*}TimeSeries')
                res_elem = root.find('.//{*}resolution')
                resol = res_elem.text if res_elem is not None else "Unknown"
                results[name] = f"SUCCESS: {len(ts)} TimeSeries, Resolution {resol}"
        except Exception as e:
            results[name] = f"XML PARSE FAIL ({res.text[:40]}...)"
    else:
        results[name] = f"HTTP {res.status_code} FAIL"


for name, status in results.items():
    print(f"{name:<10}: {status}")
