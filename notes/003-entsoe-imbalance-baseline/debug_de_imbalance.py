import os
import sys
import requests
import xml.etree.ElementTree as ET

token_path = '/home/volmax-studio/Documents/Kljucevi/apientso.txt'
with open(token_path, 'r') as f:
    api_key = f.read().strip()

url = "https://web-api.tp.entsoe.eu/api"

# Test various parameter combinations for DE-LU Imbalance Prices
test_configs = [
    {"name": "DE-LU biddingZone_Domain A85", "params": {'documentType': 'A85', 'biddingZone_Domain': '10Y1001A1001A82H'}},
    {"name": "DE-LU controlArea_Domain A85", "params": {'documentType': 'A85', 'controlArea_Domain': '10Y1001A1001A82H'}},
    {"name": "DE-LU biddingZone_Domain A84", "params": {'documentType': 'A84', 'biddingZone_Domain': '10Y1001A1001A82H'}},
    {"name": "DE-LU controlArea_Domain A86", "params": {'documentType': 'A86', 'controlArea_Domain': '10Y1001A1001A82H'}},
    {"name": "DE-50Hz TSO A85", "params": {'documentType': 'A85', 'controlArea_Domain': '10YDE-VE-------2'}},
    {"name": "DE-Amprion TSO A85", "params": {'documentType': 'A85', 'controlArea_Domain': '10YDE-RWENET---I'}},
]

print("=== TESTING GERMANY (DE-LU) ENTSO-E IMBALANCE API PARAMETERS ===")

for config in test_configs:
    params = {'securityToken': api_key, 'periodStart': '202506010000', 'periodEnd': '202506020000'}
    params.update(config['params'])
    
    res = requests.get(url, params=params)
    print(f"\nConfiguration: {config['name']}")
    print(f"HTTP Status: {res.status_code}")
    xml_str = res.text
    
    root = ET.fromstring(xml_str)
    # Check if Acknowledgement / Reason text exists
    reasons = root.findall('.//{*}text')
    if reasons:
        reason_text = reasons[0].text
        print(f"API Response: REASON -> {reason_text}")
    else:
        # Check TimeSeries count
        timeseries = root.findall('.//{*}TimeSeries')
        print(f"API Response: SUCCESS! Found {len(timeseries)} TimeSeries elements in payload.")
        if timeseries:
            res_elem = root.find('.//{*}resolution')
            print(f"Resolution: {res_elem.text if res_elem is not None else 'N/A'}")
            period_elem = root.find('.//{*}Period')
            if period_elem is not None:
                start_elem = period_elem.find('.//{*}start')
                end_elem = period_elem.find('.//{*}end')
                print(f"Period: {start_elem.text if start_elem is not None else 'N/A'} to {end_elem.text if end_elem is not None else 'N/A'}")
