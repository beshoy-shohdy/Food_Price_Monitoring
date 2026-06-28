#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
=============================================================
  WFP Egypt — Data Cleaning Script
=============================================================
"""

import pandas as pd
import os

RAW_PATH      = "/content/wfp_food_prices_database.csv"
PROCESSED_DIR = "/content/data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)


def clean_wfp(path: str) -> pd.DataFrame:
    print("=" * 55)
    print("  WFP — Cleaning")
    print("=" * 55)

    # ── Load ─────────────────────────────────────────────
    df = pd.read_csv(path, low_memory=False)
    print(f"  Raw shape (all countries) : {df.shape}")

    # ─────────────────────────────────────────────────────
    # STEP 1: Filter Egypt only
    # ─────────────────────────────────────────────────────
    df = df[df["adm0_id"] == 40765.0].copy()
    print(f"  After Egypt filter        : {df.shape}")

    # ─────────────────────────────────────────────────────
    # STEP 2: Build date FIRST
    # ─────────────────────────────────────────────────────
    df["date"] = pd.to_datetime(
        df["mp_year"].astype(int).astype(str) + "-" +
        df["mp_month"].astype(int).astype(str).str.zfill(2) + "-01"
    )

    # ─────────────────────────────────────────────────────
    # STEP 3: Drop useless columns
    # ─────────────────────────────────────────────────────
    cols_to_drop = [
        "adm0_id",
        "adm1_id",
        "adm1_name",
        "mkt_id",
        "cur_id",
        "pt_id",
        "pt_name",
        "um_id",
        "mp_commoditysource",
        "mp_month",
        "mp_year",
    ]
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)
    print(f"  After dropping columns    : {df.shape}")

    # ─────────────────────────────────────────────────────
    # STEP 4: Rename columns
    # ─────────────────────────────────────────────────────
    df = df.rename(columns={
        "adm0_name" : "country",
        "mkt_name"  : "market_name",
        "cm_id"     : "product_id",
        "cm_name"   : "product_name",
        "cur_name"  : "currency",
        "um_name"   : "unit",
        "mp_price"  : "price",
    })

    # ─────────────────────────────────────────────────────
    # STEP 5: Clean product_name
    # ─────────────────────────────────────────────────────
    df["product_name"] = df["product_name"].str.replace(
        r"\s*-\s*Retail$", "", regex=True
    ).str.strip()

    # ─────────────────────────────────────────────────────
    # STEP 6: Reset index
    # ─────────────────────────────────────────────────────
    df.reset_index(drop=True, inplace=True)

    # ─────────────────────────────────────────────────────
    # STEP 7: Final column order
    # ─────────────────────────────────────────────────────
    final_cols = [
        "country",
        "market_name",
        "product_id",
        "product_name",
        "currency",
        "unit",
        "price",
        "date",
    ]
    df = df[final_cols]

    # ─────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────
    print(f"\n  Clean shape               : {df.shape}")
    print(f"  Date range                : {df['date'].min()} → {df['date'].max()}")
    print(f"  Unique products           : {df['product_name'].nunique()}")
    print(f"  Unique markets            : {df['market_name'].nunique()}")
    print(f"  Null prices               : {df['price'].isna().sum()}")
    print(f"\n  Products found:")
    print(df["product_name"].unique())
    print(f"\n  Sample:")
    print(df.head(5).to_string())

    return df


if __name__ == "__main__":
    df_wfp = clean_wfp(RAW_PATH)

    # Save
    df_wfp.to_parquet("/content/wfp_egypt_clean3.parquet", index=False, engine="pyarrow")
    df_wfp.to_csv("/content/wfp_egypt_clean3.csv", index=False)

    # Download to your laptop
    from google.colab import files
    files.download("/content/wfp_egypt_clean3.parquet")
    files.download("/content/wfp_egypt_clean3.csv")

    print("✅ Done!")
