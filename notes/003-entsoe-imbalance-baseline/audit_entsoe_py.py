import os
import sys
import pandas as pd
from entsoe import EntsoePandasClient

token_path = '/home/volmax-studio/Documents/Kljucevi/apientso.txt'
with open(token_path, 'r') as f:
    api_key = f.read().strip()

client = EntsoePandasClient(api_key=api_key)

start = pd.Timestamp('2025-06-01', tz='UTC')
end = pd.Timestamp('2025-06-02', tz='UTC')

zones_to_test = {
    'NL': 'NL',
    'BE': 'BE',
    'FR': 'FR',
    'DK_1': 'DK_1',
    'DK_2': 'DK_2',
    'FI': 'FI',
    'AT': 'AT',
    'CZ': 'CZ',
    'PL': 'PL',
    'DE_LU': 'DE_LU'
}

print("=== AUDITING EUROPEAN IMBALANCE PRICES VIA ENTSOE-PY (ZIP UNPACKING) ===")

results = {}
for name, code in zones_to_test.items():
    try:
        df = client.query_imbalance_prices(country_code=code, start=start, end=end)
        cols = list(df.columns)
        freq = df.index.inferred_freq or "15min"
        results[name] = f"SUCCESS: {len(df)} intervals, columns={cols}, resolution={freq}"
    except Exception as e:
        results[name] = f"FAIL: {str(e)[:80]}"

print("\n--- FINAL ZONE AUDIT SUMMARY ---")
for name, status in results.items():
    print(f"{name:<10}: {status}")
