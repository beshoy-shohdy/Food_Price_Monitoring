import pandas as pd
import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parents[2]  
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "clean_data"
os.makedirs(PROCESSED_DIR, exist_ok=True)

print(f"Processed directory: {PROCESSED_DIR}")

amazon = pd.read_csv(PROCESSED_DIR / "amazon_clean.csv")
noon = pd.read_csv(PROCESSED_DIR / "noon_clean.csv")
wtp = pd.read_csv(PROCESSED_DIR / "wfp_egypt_clean.csv")

merged_df = pd.concat([amazon, noon, wtp], ignore_index=True)
merged_df.to_csv(PROCESSED_DIR / "full_data_clean.csv", index=False)