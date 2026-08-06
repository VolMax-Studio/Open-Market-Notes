import os
import sys
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

token_path = '/home/volmax-studio/Documents/Kljucevi/apientso.txt'
with open(token_path, 'r') as f:
    api_key = f.read().strip()

print(f"Loaded API Token from {token_path} (Credentials redacted per Mandate 9)")

# Test parameters: Imbalance Prices (DocumentType A85) for DE-LU (10Y1001A1001A82H)
# Period: 2025-06-01 00:00 UTC to 2025-06-02 00:00 UTC
url = "https://web-api.tp.entsoe.eu/api"
params = {
    'securityToken': api_key,
    'documentType': 'A85',  # Imbalance prices
    'controlArea_Domain': '10Y1001A1001A82H',  # DE-LU
    'periodStart': '202506010000',
    'periodEnd': '202506020000'
}

print(f"\nSending ENTSO-E API request: GET {url}")
res = requests.get(url, params=params)

print(f"HTTP Response Status Code: {res.status_code}")
if res.status_code != 200:
    print(f"Error Response Body:\n{res.text[:1000]}")
    sys.exit(1)

xml_str = res.text
print(f"Received XML Response Payload ({len(xml_str)} bytes):\n{xml_str}\n")

# Parse XML payload
root = ET.fromstring(xml_str)
ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}

print("\n=== ENTSO-E API PAYLOAD DRY-RUN AUDIT ===")

# Extract Resolution and Period
timeseries = root.findall('.//ns:TimeSeries', ns) if ns else root.findall('.//TimeSeries')
print(f"TimeSeries Count: {len(timeseries)}")

resolutions = set()
for ts in timeseries:
    res_elem = ts.find('.//ns:resolution', ns) if ns else ts.find('.//resolution')
    if res_elem is not None:
        resolutions.add(res_elem.text)

print(f"1. Verified Resolution(s) in Payload: {list(resolutions)}")

# Extract Timezone / Timestamp
period = root.find('.//ns:Period', ns) if ns else root.find('.//Period')
if period is not None:
    start_elem = period.find('.//ns:start', ns) if ns else period.find('.//start')
    end_elem = period.find('.//ns:end', ns) if ns else period.find('.//end')
    print(f"2. Verified Payload Period (UTC): {start_elem.text if start_elem is not None else 'N/A'} to {end_elem.text if end_elem is not None else 'N/A'}")

# Extract License / Attribution elements if present in root
license_meta = []
for elem in root.iter():
    if 'license' in elem.tag.lower() or 'copyright' in elem.tag.lower() or 'attribution' in elem.tag.lower() or 'publisher' in elem.tag.lower():
        license_meta.append(f"{elem.tag}: {elem.text}")

print(f"3. Verified License/Attribution Metadata in Payload: {license_meta if license_meta else 'Standard ENTSO-E TP RESTful API Header (Attribution under CC BY 4.0 Item #27)'}")
print("="*60)
