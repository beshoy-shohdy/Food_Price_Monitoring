#!/usr/bin/env python
# coding: utf-8

# In[3]:


"""
=============================================================
  Amazon Egypt — Data Cleaning Script
=============================================================
"""

import pandas as pd
import numpy as np
import re
import os
from pathlib import Path

BASE_DIR = Path("/opt/airflow/project/food_web_scraping")

RAW_PATH = BASE_DIR / "amazon" / "final_amazon_product_details.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)


# =============================================================
#  HELPER FUNCTIONS
# =============================================================

def normalize_weight_to_grams(weight_str) -> float:
    """Convert any weight string to grams."""
    if pd.isna(weight_str):
        return np.nan
    s = str(weight_str).strip().lower()
    num_match = re.search(r"[\d\.]+", s)
    if not num_match:
        return np.nan
    value = float(num_match.group())
    if any(u in s for u in ["kg", "kilo", "kilogram"]):
        return value * 1000
    if any(u in s for u in ["gram", "grams"]):
        return value
    if any(u in s for u in ["liter", "litre"]):
        return value * 1000
    if any(u in s for u in ["ml", "milliliter"]):
        return value
    if any(u in s for u in ["ounce", "oz"]):
        return value * 28.35
    return np.nan


def clean_product_name(name: str) -> str:
    """Clean product name."""
    if pd.isna(name):
        return np.nan
    name = str(name).strip()
    name = name.split("|")[0].strip()
    name = re.sub(r"–", "-", name)
    name = re.sub(r"\s*-\s*$", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()


def get_product_type(product_name: str, sub_category: str) -> str:
    """
    Extract product type from product_name guided by sub_category.
    """
    if pd.isna(sub_category):
        return "Unknown"

    sub = str(sub_category).strip()
    name = str(product_name).lower() if pd.notna(product_name) else ""

    # ── Sub-categories that stay as-is ───────────────────
    if sub in ["Coffee", "Tea", "Water", "Milk",
               "Juices", "Soft Drinks", "Cooking & Baking"]:
        return sub

    # ── Rice & Pasta ──────────────────────────────────────
    if sub == "Rice & Pasta":
        if any(k in name for k in ["vermicelli", "vermecelli", "شعيرية"]):
            return "Vermicelli"
        if any(k in name for k in ["noodle", "indomie", "ramen"]):
            return "Noodles"
        if any(k in name for k in ["rice", "أرز", "basmati"]):
            return "Rice"
        if any(k in name for k in ["pasta", "spaghetti", "penne", "fettuc",
                                    "lasagna", "macaroni", "fusilli", "rigatoni",
                                    "risoni", "tagliatelle", "linguine", "مكرونة"]):
            return "Pasta"
        return "Rice & Pasta"

    # ── Cereal & Oats ─────────────────────────────────────
    if sub == "Cereal & Oats":
        if any(k in name for k in ["oat", "oats", "شوفان"]):
            return "Oats"
        if any(k in name for k in ["cereal", "cornflakes", "corn flakes",
                                    "granola", "muesli"]):
            return "Cereal"
        return "Cereal & Oats"

    # ── Herbs & Spices ────────────────────────────────────
    if sub == "Herbs & Spices":
        if any(k in name for k in ["spice", "seasoning", "pepper", "cumin",
                                    "cinnamon", "turmeric", "saffron", "stock",
                                    "mix", "powder", "salt", "baharat"]):
            return "Spices"
        if any(k in name for k in ["herb", "parsley", "basil", "thyme",
                                    "mint", "oregano", "rosemary"]):
            return "Herbs"
        return "Spices"

    # ── Jams, Honey & Spreads ─────────────────────────────
    if sub == "Jams, Honey & Spreads":
        if any(k in name for k in ["honey", "عسل"]):
            return "Honey"
        if any(k in name for k in ["jam", "jelly", "مربى"]):
            return "Jams"
        if any(k in name for k in ["spread", "butter", "nutella",
                                    "chocolate", "hazelnut", "tahini"]):
            return "Spreads"
        return "Jams"

    # ── Sauces, Gravies & Marinades ───────────────────────
    if sub == "Sauces, Gravies & Marinades":
        return "Sauces"

    return sub


# =============================================================
#  MAIN CLEANING FUNCTION
# =============================================================

def clean_amazon(path: str) -> pd.DataFrame:
    print("=" * 55)
    print("  AMAZON — Cleaning")
    print("=" * 55)

    # ── Load ─────────────────────────────────────────────
    df = pd.read_csv(path)
    print(f"  Raw shape              : {df.shape}")

    # ─────────────────────────────────────────────────────
    # STEP 1: Rename + Add source
    # ─────────────────────────────────────────────────────
    df = df.rename(columns={
        "SKU"        : "sku",
        "start_date" : "date",
    })
    df["source"] = "amazon"

    # ─────────────────────────────────────────────────────
    # STEP 2: Drop rows with null product_name
    # ─────────────────────────────────────────────────────
    before = len(df)
    df.dropna(subset=["product_name"], inplace=True)
    print(f"  Dropped null names     : {before - len(df)} rows")

    # ─────────────────────────────────────────────────────
    # STEP 3: Clean product_name
    # ─────────────────────────────────────────────────────
    df["product_name"] = df["product_name"].apply(clean_product_name)

    # ─────────────────────────────────────────────────────
    # STEP 4: Fix price
    # ─────────────────────────────────────────────────────
    df["price"] = df["price"].astype(str).str.replace(",", "", regex=False)
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    before = len(df)
    df = df[df["price"].notna() & (df["price"] > 0)]
    print(f"  Dropped invalid prices : {before - len(df)} rows")

    # ─────────────────────────────────────────────────────
    # STEP 5: item_weight → grams
    # ─────────────────────────────────────────────────────
    df["item_weight_grams"] = df["item_weight"].apply(normalize_weight_to_grams)
    df["package_weight_grams"] = df["package_weight"].apply(normalize_weight_to_grams)
    df["item_weight_grams"] = df["item_weight_grams"].fillna(df["package_weight_grams"])
    df.drop(columns=["item_weight", "package_weight",
                      "package_weight_grams", "unit_count"], inplace=True)

    # ─────────────────────────────────────────────────────
    # STEP 6: number_of_items
    # ─────────────────────────────────────────────────────
    df["number_of_items"] = pd.to_numeric(df["number_of_items"], errors="coerce")

    # ─────────────────────────────────────────────────────
    # STEP 7: price_per_unit
    # ─────────────────────────────────────────────────────
    df["price_per_unit"] = df["price"] / df["number_of_items"].fillna(1)

    # ─────────────────────────────────────────────────────
    # STEP 8: product_type
    # ─────────────────────────────────────────────────────
    df["product_type"] = df.apply(
        lambda row: get_product_type(row["product_name"], row["sub_category"]),
        axis=1
    )

    # ─────────────────────────────────────────────────────
    # STEP 9: Parse date
    # ─────────────────────────────────────────────────────
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # ─────────────────────────────────────────────────────
    # STEP 10: Fill nulls
    # ─────────────────────────────────────────────────────
    text_cols = ["brand", "category", "sub_category", "product_type"]
    for col in text_cols:
        df[col] = df[col].fillna("Unknown")

    # ─────────────────────────────────────────────────────
    # STEP 11: Drop duplicates
    # ─────────────────────────────────────────────────────
    before = len(df)
    df.drop_duplicates(subset=["sku", "date"], inplace=True)
    print(f"  Dropped duplicates     : {before - len(df)} rows")

    # ─────────────────────────────────────────────────────
    # STEP 12: Final column order
    # ─────────────────────────────────────────────────────
    df.reset_index(drop=True, inplace=True)
    final_cols = [
        "sku", "source", "category", "sub_category", "product_type",
        "product_name", "brand", "price", "price_per_unit",
        "number_of_items", "item_weight_grams", "date",
    ]
    df = df[[c for c in final_cols if c in df.columns]]

    # ─────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────
    print(f"\n  Clean shape            : {df.shape}")
    print(f"  Date range             : {df['date'].min()} → {df['date'].max()}")
    print(f"  Unique products        : {df['product_name'].nunique()}")
    print(f"  Null weights           : {df['item_weight_grams'].isna().sum()}")
    print(f"  Null number_of_items   : {df['number_of_items'].isna().sum()}")
    print(f"\n  Product types:")
    print(df["product_type"].value_counts().to_string())
    print(f"\n  Sample:")
    print(df.head(5).to_string())

    return df


# =============================================================
#  MAIN
# =============================================================

if __name__ == "__main__":
    df_amazon = clean_amazon(RAW_PATH)

    PARQUET_DIR = PROCESSED_DIR / "parquet"
    CSV_DIR = PROCESSED_DIR / "clean_data"

    PARQUET_DIR.mkdir(parents=True, exist_ok=True)
    CSV_DIR.mkdir(parents=True, exist_ok=True)

    df_amazon.to_parquet(PARQUET_DIR / "amazon_clean.parquet", index=False, engine="pyarrow")
    df_amazon.to_csv(CSV_DIR / "amazon_clean.csv", index=False)

    print("\n✅ Done!")
