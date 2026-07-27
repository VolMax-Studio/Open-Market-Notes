import io
import zipfile
import requests
import xml.etree.ElementTree as ET

token_path = '/home/volmax-studio/Documents/Kljucevi/apientso.txt'
with open(token_path, 'r') as f:
    api_key = f.read().strip()

url = "https://web-api.tp.entsoe.eu/api"

params = {
    'securityToken': api_key,
    'documentType': 'A85',
    'controlArea_Domain': '10YBE----------X',  # BE
    'periodStart': '202506150000',
    'periodEnd': '202506160000'
}


res = requests.get(url, params=params)
print("=== BE RAW XML PAYLOAD AUDIT ===")
print("Status:", res.status_code)
print("Content-Type:", res.headers.get('Content-Type'))

if res.content.startswith(b'PK'):
    z = zipfile.ZipFile(io.BytesIO(res.content))
    xml_data = z.read(z.namelist()[0]).decode('utf-8')
else:
    xml_data = res.text

print("Raw XML Snippet:")
print(xml_data[:1500])

