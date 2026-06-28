"""
=============================================================
  Final Unified Data Cleaning
  Input:  full_data_clean.csv
  Output: unified_prices_final.csv + .parquet
=============================================================
"""
import pandas as pd
import numpy as np
import os
from pathlib import Path

BASE_DIR = Path("/opt/airflow/project/food_web_scraping/data/processed")

OUTPUT_PATH_CSV = BASE_DIR / "clean_data" / "unified_full_data.csv"
OUTPUT_PATH_PARQUET = BASE_DIR / "parquet" / "unified_full_data.parquet"

OUTPUT_PATH_CSV.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH_PARQUET.parent.mkdir(parents=True, exist_ok=True)


print(f"Processed directory: {BASE_DIR}")

amazon = pd.read_csv(BASE_DIR / "clean_data"/ "amazon_clean.csv")
noon = pd.read_csv(BASE_DIR / "clean_data"/ "noon_clean.csv")
wtp = pd.read_csv(BASE_DIR / "clean_data"/ "wfp_egypt_clean.csv")

merged_df = pd.concat([amazon, noon, wtp], ignore_index=True)

def get_product_type(product_name, sub_category):
    if pd.isna(product_name):
        return None

    name = str(product_name).lower()
    sub  = str(sub_category) if pd.notna(sub_category) else ""

    # ── Sub-categories that stay as-is ───────────────────
    if sub in ["Coffee", "Tea", "Water", "Milk", "Juices", "Soft Drinks"]:
        return sub

    # ── Rice & Pasta ──────────────────────────────────────
    if any(k in name for k in ["vermicelli"]):
        return "Vermicelli"
    if any(k in name for k in ["noodle", "ramen", "indomie", "samyang",
                                "saming", "nolds", "tobuki", "instant"]):
        return "Noodles"
    if any(k in name for k in ["rice", "basmati"]):
        return "Rice"
    if any(k in name for k in ["pasta", "spaghetti", "penne", "macaroni",
                                "fusilli", "lasagna", "fettuc", "risoni",
                                "serpentini", "elbow", "rings", "farfalli",
                                "orzo", "koshari", "gnocchi"]):
        return "Pasta"

    # ── Cereal & Oats ─────────────────────────────────────
    if any(k in name for k in ["oat", "oats"]):
        return "Oats"
    if any(k in name for k in ["cereal", "cornflakes", "granola", "muesli",
                                "corn flakes", "bran flakes"]):
        return "Cereal"

    # ── Cooking & Baking ──────────────────────────────────
    if any(k in name for k in ["sunflower oil", "olive oil", "corn oil",
                                "vegetable oil", "frying oil", "cooking oil",
                                " oil ", "mct oil"]):
        return "Oils"
    if any(k in name for k in ["vinegar"]):
        return "Oils"
    if any(k in name for k in ["flour", "pancake mix", "cake flour",
                                "dumpling flour"]):
        return "Flour"
    if any(k in name for k in ["sugar", "sweetener", "stevia", "fructose"]):
        return "Sugar"
    if any(k in name for k in [" salt", "sea salt", "rock salt"]):
        return "Salt"
    if any(k in name for k in ["baking powder", "yeast", "vanilla extract"]):
        return "Flour"

    # ── Herbs & Spices ────────────────────────────────────
    if any(k in name for k in ["spice", "pepper", "cumin", "cinnamon",
                                "turmeric", "seasoning", "thyme", "ginger",
                                "rosemary", "basil", "oregano", "paprika",
                                "cardamom", "saffron", "cajun", "baharat",
                                "stock cube", "bouillon"]):
        return "Spices"
    if any(k in name for k in ["herb", "parsley", "mint", "bay leaf"]):
        return "Herbs"

    # ── Jams & Spreads ────────────────────────────────────
    if any(k in name for k in ["honey", "عسل"]):
        return "Honey"
    if any(k in name for k in ["jam", "jelly", "marmalade"]):
        return "Jams"
    if any(k in name for k in ["nutella", "peanut butter", "tahini",
                                "halawa", "halva", "chocolate spread"]):
        return "Spreads"

    # ── Sauces ────────────────────────────────────────────
    if any(k in name for k in ["sauce", "ketchup", "mayo", "mayonnaise",
                                "mustard", "tomato paste", "hot sauce",
                                "tabasco", "ranch", "bbq", "dressing"]):
        return "Sauces"

    # ── Tea & Drinks ──────────────────────────────────────
    if any(k in name for k in ["tea", "earl gray", "lipton", "hibiscus",
                                "chamomile", "sage", "fennel", "rosehip",
                                "green tea", "black tea", "herbal",
                                "mint tea", "guava leaves", "ginseng"]):
        return "Tea"
    if any(k in name for k in ["juice", "nectar", "fruit drink"]):
        return "Juices"
    if any(k in name for k in ["water", "mineral water", "drinking water"]):
        return "Water"
    if any(k in name for k in ["coffee", "espresso", "cappuccino",
                                "nescafe", "latte", "americano"]):
        return "Coffee"
    if any(k in name for k in ["cola", "pepsi", "sprite", "fanta",
                                "soft drink", "energy drink", "carbonated",
                                "soda", "7up"]):
        return "Soft Drinks"

    # ── Dairy ─────────────────────────────────────────────
    if any(k in name for k in ["milk", "evaporated milk", "condensed milk",
                                "powder milk", "skimmed milk", "full cream",
                                "coconut milk", "carton"]):
        return "Milk"
    if any(k in name for k in ["cheese", "picon", "gouda", "cheddar"]):
        return "Cheese"
    if any(k in name for k in ["yogurt", "yoghurt", "laban"]):
        return "Yogurt"
    if any(k in name for k in ["butter", "ghee"]):
        return "Butter"
    if any(k in name for k in ["cream", "whipping cream"]):
        return "Milk"

    # ── Beans & Grains ────────────────────────────────────
    if any(k in name for k in ["lentil", "lentils", "red lentil",
                                "yellow lentil", "brown lentil"]):
        return "Lentils"
    if any(k in name for k in ["bean", "beans", "fava", "foul", "lupine",
                                "chickpea", "hummus", "black eyed peas"]):
        return "Beans"
    if any(k in name for k in ["wheat", "freekeh", "bulgur", "couscous",
                                "quinoa", "barley", "grits"]):
        return "Grains"

    return None


def clean_unified(df):
    print("=" * 55)
    print("  Final Unified Cleaning")
    print("=" * 55)
    print(f"  Raw shape           : {df.shape}")

    # ─────────────────────────────────────────────────────
    # STEP 1: Keep Amazon + Noon only → شيل WFP
    # ─────────────────────────────────────────────────────
    df = df[df["source"].isin(["amazon", "noon"])].copy()
    print(f"  After source filter : {df.shape}")

    # ─────────────────────────────────────────────────────
    # STEP 2: Drop useless columns
    # ─────────────────────────────────────────────────────
    cols_to_drop = [
        "item_weight", "unit_count", "rating_count",
        "country", "market_name", "product_id",
        "currency", "unit"
    ]
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)

    # ─────────────────────────────────────────────────────
    # STEP 3: Drop rows with null price or product_name
    # ─────────────────────────────────────────────────────
    before = len(df)
    df.dropna(subset=["price", "product_name"], inplace=True)
    print(f"  Dropped null rows   : {before - len(df)}")

    # ─────────────────────────────────────────────────────
    # STEP 4: Drop price outliers
    # ─────────────────────────────────────────────────────
    before = len(df)
    df = df[df["price"] <= 50000]
    print(f"  Dropped outliers    : {before - len(df)}")

    # ─────────────────────────────────────────────────────
    # STEP 5: Fix product_type
    # ─────────────────────────────────────────────────────
    needs_fix = (
        df["product_type"].isna() |
        df["product_type"].isin(["Rice & Pasta", "Cereal & Oats",
                                  "Cooking & Baking", "Unknown"])
    )
    df.loc[needs_fix, "product_type"] = df[needs_fix].apply(
        lambda row: get_product_type(row["product_name"], row["sub_category"]),
        axis=1
    )

    # شيل اللي لسه None أو Unknown
    before = len(df)
    df = df[df["product_type"].notna()]
    df = df[df["product_type"] != "Unknown"]
    df.reset_index(drop=True, inplace=True)
    print(f"  Dropped no-type     : {before - len(df)}")

    # ─────────────────────────────────────────────────────
    # STEP 6: Fill text nulls
    # ─────────────────────────────────────────────────────
    df["brand"] = df["brand"].fillna("Unknown")

    # ─────────────────────────────────────────────────────
    # STEP 7: Parse date
    # ─────────────────────────────────────────────────────
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # حساب price_per_unit لو فاضية
    df["price_per_unit"] = df["price_per_unit"].fillna(df["price"] / df["number_of_items"].fillna(1))

    # ─────────────────────────────────────────────────────
    # STEP 8: Final column order
    # ─────────────────────────────────────────────────────
    final_cols = [
        "sku", "source", "category", "sub_category", "product_type",
        "product_name", "brand", "price", "price_per_unit",
        "number_of_items", "item_weight_grams", "date"
    ]
    df = df[[c for c in final_cols if c in df.columns]]

    # ─────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────
    print(f"\n  Final shape         : {df.shape}")
    print(f"  Nulls:")
    print(df.isnull().sum().to_string())
    print(f"\n  Source counts:")
    print(df["source"].value_counts().to_string())
    print(f"\n  Product types:")
    print(df["product_type"].value_counts().to_string())

    return df


if __name__ == "__main__":
    df = clean_unified(merged_df)

    # Save
    df.to_csv(OUTPUT_PATH_CSV, index=False)
    df.to_parquet(OUTPUT_PATH_PARQUET, index=False, engine="pyarrow")

    print("\n✅ Done!")