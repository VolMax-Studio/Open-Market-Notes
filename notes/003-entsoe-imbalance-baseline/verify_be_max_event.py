import pandas as pd
import numpy as np

df = pd.read_feather("./data/processed/imbalance_BE.feather")
if 'index' in df.columns:
    df = df.set_index('index')
elif 'DateTime' in df.columns:
    df = df.set_index('DateTime')
    
df.index = pd.to_datetime(df.index)
cols = [c for c in df.columns if c not in ['index', 'DateTime']]
price = df[cols[0]]

above = (price >= 100.0).values

# Find max contiguous block
max_len = 0
max_start_idx = 0
curr_len = 0
curr_start = 0

for i, val in enumerate(above):
    if val:
        if curr_len == 0:
            curr_start = i
        curr_len += 1
    else:
        if curr_len > max_len:
            max_len = curr_len
            max_start_idx = curr_start
        curr_len = 0

if curr_len > max_len:
    max_len = curr_len
    max_start_idx = curr_start

print("=== VERIFYING BELGIUM MAX SCARCITY EVENT (>= €100/MWh) ===")
print(f"Max contiguous length: {max_len} intervals ({max_len * 15} minutes = {max_len * 15 / 60:.2f} hours)")

start_time = df.index[max_start_idx]
end_time = df.index[max_start_idx + max_len - 1]

print(f"Event Start Time: {start_time}")
print(f"Event End Time:   {end_time}")

sub_df = df.iloc[max_start_idx : max_start_idx + max_len]
print("\nPrice Statistics during Max Event:")
print(f"Min Price during event: €{sub_df[cols[0]].min():.2f}/MWh")
print(f"Max Price during event: €{sub_df[cols[0]].max():.2f}/MWh")
print(f"Mean Price during event: €{sub_df[cols[0]].mean():.2f}/MWh")

print("\nSample first 10 intervals of max event:")
print(sub_df[[cols[0]]].head(10))

print("\nSample last 10 intervals of max event:")
print(sub_df[[cols[0]]].tail(10))
