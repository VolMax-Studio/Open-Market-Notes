import pandas as pd

df = pd.read_feather("./data/processed/imbalance_NL.feather")
print("=== VERIFYING NL FEATHER COLUMNS ===")
print("Columns:", list(df.columns))

if 'Long' in df.columns and 'Short' in df.columns:
    diff_mask = df['Long'] != df['Short']
    print(f"Total rows: {len(df)}")
    print(f"Divergent rows: {diff_mask.sum()}")
    print("\nSample divergent rows (Long vs Short):")
    print(df[diff_mask][['Long', 'Short']].head(10))
    
    # Check distribution of Long vs Short during negative/low prices
    low_long = df['Long'] <= 25.0
    low_short = df['Short'] <= 25.0
    print(f"Low price count (<=25) on Long:  {low_long.sum()}")
    print(f"Low price count (<=25) on Short: {low_short.sum()}")
