import pandas as pd
import numpy as np
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parents[2]  
RAW_PATH = PROJECT_ROOT / "noon" / "noon_products.csv"
print(f"Reading data from: {RAW_PATH}")

df = pd.read_csv(RAW_PATH)

# إزالة الصفوف اللي فيها SKU فاضي
df = df[df["sku"].notna()]

# fill missing values
df["unit_count"] = df["unit_count"].fillna(1)

# drop columns safely
df.drop(columns=["number_of_items", "package_weight"], inplace=True, errors="ignore")

# convert date
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# text columns cleaning
text_cols = df.select_dtypes(include="object").columns

for col in text_cols:
    df[col] = df[col].astype(str).str.lower().str.strip()

df.drop_duplicates(inplace=True)

for col in text_cols:
    df[col] = df[col].str.replace(r"\s+", " ", regex=True)

# drop unused columns
df.drop(columns=["Unnamed: 4", "rating"], inplace=True, errors="ignore")

# handle product_name missing values
df["product_name"] = df["product_name"].replace(
    ["?", "??", "???", "-", "--", ""],
    np.nan
)

df["product_name"] = df["product_name"].fillna("unknown")

# extract weight numbers
df["item_weight"] = df["item_weight"].astype(str).str.extract(r'(\d+)')
df["item_weight"] = pd.to_numeric(df["item_weight"], errors="coerce")

# safe median
median_weight = df["item_weight"].median()
if pd.isna(median_weight):
    median_weight = 0
else:
    median_weight = int(median_weight)

df["item_weight"] = df["item_weight"].fillna(median_weight).astype(int)

# save final file
df.to_csv(PROJECT_ROOT/ "data" / "processed" / "clean_data" / "noon_clean.csv", index=False)
df.to_parquet(PROJECT_ROOT / "data" / "processed" / "parquet" / "noon_clean.parquet", index=False, engine="pyarrow")