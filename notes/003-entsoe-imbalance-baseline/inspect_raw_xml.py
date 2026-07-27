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

# Query raw XML payload for DK_1 (Denmark West) for 1 day
params = {
    'securityToken': api_key,
    'documentType': 'A85',  # Imbalance prices
    'controlArea_Domain': '10YDK-1--------W',  # DK_1
    'periodStart': '202506010000',
    'periodEnd': '202506020000'
}

print("=== INSPECTING RAW ENTSO-E XML PAYLOAD FOR DK_1 (DENMARK WEST) ===")
res = requests.get(url, params=params)

print(f"HTTP Response Status: {res.status_code}")
print(f"Content-Type: {res.headers.get('Content-Type')}")

if res.content.startswith(b'PK'):
    print("Response is a ZIP Archive. Unpacking XML files...")
    z = zipfile.ZipFile(io.BytesIO(res.content))
    for name in z.namelist():
        print(f"\n--- ZIP Entry File: {name} ---")
        xml_data = z.read(name).decode('utf-8')
        root = ET.fromstring(xml_data)
        
        # Look for TimeSeries and BusinessType / Price Category elements
        timeseries = root.findall('.//{*}TimeSeries')
        print(f"Total TimeSeries in XML: {len(timeseries)}")
        
        for idx, ts in enumerate(timeseries):
            mkt_ps_type = ts.find('.//{*}mktPSRType/{*}psrType')
            biz_type = ts.find('.//{*}businessType')
            flow_dir = ts.find('.//{*}flowDirection/{*}direction')
            
            print(f"  TimeSeries #{idx+1}:")
            if biz_type is not None:
                print(f"    businessType: {biz_type.text}")
            if flow_dir is not None:
                print(f"    flowDirection: {flow_dir.text}")
                
            points = ts.findall('.//{*}Point')
            print(f"    Points count: {len(points)}")
            if points:
                first_price = points[0].find('.//{*}price.amount')
                print(f"    First Point Price: {first_price.text if first_price is not None else 'N/A'}")
else:
    print("Response is XML string:")
    print(res.text[:1000])
