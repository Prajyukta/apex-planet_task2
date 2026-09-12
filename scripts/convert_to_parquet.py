
import os
import pandas as pd

# Repository root (two levels up from this script)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, 'data', 'processed', 'telco_cleaned.csv')
PARQUET = os.path.join(ROOT, 'data', 'processed', 'telco_cleaned.parquet')
PICKLE = os.path.join(ROOT, 'data', 'processed', 'telco_cleaned.pkl')

if not os.path.exists(CSV):
    raise SystemExit(f"CSV not found: {CSV}")

print('Reading CSV:', CSV)
df = pd.read_csv(CSV)

# Try to write parquet (requires pyarrow or fastparquet)
try:
    df.to_parquet(PARQUET, index=False)
    print('Wrote Parquet:', PARQUET)
except Exception as e:
    print('Parquet write failed:', repr(e))
    print('Falling back to pickle for faster loads')
    df.to_pickle(PICKLE)
    print('Wrote Pickle:', PICKLE)

print('Done')
