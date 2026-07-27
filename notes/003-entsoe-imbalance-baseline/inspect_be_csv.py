import pandas as pd

df = pd.read_csv("./data/raw_cache/imbalance_BE_202506_202606.csv")
print("=== BE RAW CACHE CSV INSPECTION ===")
print("Columns:", list(df.columns))
print("Shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head(5))
