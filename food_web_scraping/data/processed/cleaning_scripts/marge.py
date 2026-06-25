import pandas as pd
import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parents[2]  
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" 
os.makedirs(PROCESSED_DIR, exist_ok=True)

print(f"Processed directory: {PROCESSED_DIR}")

amazon = pd.read_csv(PROCESSED_DIR / "clean_data"/ "amazon_clean.csv")
noon = pd.read_csv(PROCESSED_DIR / "clean_data"/ "noon_clean.csv")
wtp = pd.read_csv(PROCESSED_DIR / "clean_data"/ "wfp_egypt_clean.csv")

merged_df = pd.concat([amazon, noon, wtp], ignore_index=True)
merged_df.to_csv(PROCESSED_DIR / "clean_data"/ "full_data_clean.csv", index=False)
merged_df.to_parquet(PROCESSED_DIR / "parquet"/ "full_data_clean.parquet", index=False, engine="pyarrow")