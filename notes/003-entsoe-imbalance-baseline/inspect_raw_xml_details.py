import os
import sys
import io
import zipfile
import requests
import xml.etree.ElementTree as ET

token_path = '/home/volmax-studio/Documents/Kljucevi/apientso.txt'
with open(token_path, 'r') as f:
    api_key = f.read().strip()

url = "https://web-api.tp.entsoe.eu/api"

zones = {'DK_1': '10YDK-1--------W', 'BE': '10YBE----------X', 'NL': '10YNL----------L', 'FR': '10YFR-RTE------C'}

print("=== AUDITING RAW ENTSO-E XML CATEGORY TAGS (A04 vs A05) ===")

for name, eic in zones.items():
    params = {
        'securityToken': api_key,
        'documentType': 'A85',
        'controlArea_Domain': eic,
        'periodStart': '202506010000',
        'periodEnd': '202506020000'
    }
    res = requests.get(url, params=params)
    if res.content.startswith(b'PK'):
        z = zipfile.ZipFile(io.BytesIO(res.content))
        xml_data = z.read(z.namelist()[0]).decode('utf-8')
    else:
        xml_data = res.text
        
    root = ET.fromstring(xml_data)
    ts_list = root.findall('.//{*}TimeSeries')
    
    categories = []
    for ts in ts_list:
        cat_elem = ts.find('.//{*}imbalance_Price.category')
        if cat_elem is not None:
            categories.append(cat_elem.text)
        else:
            # Check inside points
            p_cat = ts.find('.//{*}Point/{*}imbalance_Price.category')
            categories.append(p_cat.text if p_cat is not None else "Unknown")
            
    print(f"Zone {name:<5}: Found {len(ts_list)} TimeSeries. Categories: {categories}")
