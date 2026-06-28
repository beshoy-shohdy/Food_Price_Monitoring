"""
Noon Products - Complete Data Cleaning Pipeline
"""

import pandas as pd
import numpy as np
import re

INPUT_FILE = '../../noon/noon_products.csv'
OUTPUT_FILE = 'noon_clean.csv'

# LOAD
df = pd.read_csv(INPUT_FILE)
print(f"Loaded: {len(df):,} rows × {df.shape[1]} cols")

# REMOVE JUNK ROWS
# Drop rows where 'source' column contains a literal header repeat
df = df[df['source'].str.lower() != 'source'].copy()

# Drop fully-empty rows
df.dropna(how='all', inplace=True)

# Drop rows missing both price and product_name (un-recoverable)
df = df[~(df['price'].isna() & df['product_name'].isna())].copy()
print(f"After removing junk rows: {len(df):,} rows")

# FIX COLUMN NAMES
# BOM character on first column (﻿sku → sku)
df.columns = [c.strip().lstrip('\ufeff').lstrip('﻿') for c in df.columns]

# Drop useless columns
df.drop(columns=['Unnamed: 4', 'package_weight', 'unit_count'], inplace=True, errors='ignore')

# DEDUPLICATE
before = len(df)
df.drop_duplicates(inplace=True)
print(f"Dropped {before - len(df):,} exact duplicate rows")

# For same SKU on same date keep the row with the most non-null fields
df['_non_null'] = df.notna().sum(axis=1)
df.sort_values('_non_null', ascending=False, inplace=True)
df.drop_duplicates(subset=['sku', 'date'], keep='first', inplace=True)
df.drop(columns='_non_null', inplace=True)
print(f"After dedup on (sku, date): {len(df):,} rows")


# SOURCE — standardise
df['source'] = 'noon'


# CATEGORY — normalise case
df['category'] = df['category'].str.strip().str.title()   # 'grocery' → 'Grocery'

# SUB_CATEGORY — clean whitespace
df['sub_category'] = df['sub_category'].str.strip()


# PRODUCT_NAME — strip whitespace, drop blanks
df['product_name'] = df['product_name'].str.strip()
df = df[df['product_name'].notna() & (df['product_name'] != '')].copy()


# BRAND — clean whitespace, title-case
df['brand'] = df['brand'].str.strip().str.title()

# PRICE — remove 8 rows with null price; force numeric
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df = df[df['price'].notna() & (df['price'] > 0)].copy()
print(f"After price cleaning: {len(df):,} rows")


# 11. ITEM_WEIGHT → item_weight_grams
# Arabic unit maps → target unit
ARABIC_TO_UNIT = {
    'جرام': 'g', 'جم': 'g', 'غرام': 'g', 'غم': 'g',
    'كيلوجرام': 'kg', 'كجم': 'kg', 'كيلو': 'kg',
    'مل': 'ml', 'ملليلتر': 'ml',
    'لتر': 'L', 'لترات': 'L',
    'قطعة': 'piece', 'piece': 'piece', 'pieces': 'piece',
    'grams': 'g', 'gram': 'g',
    'G': 'g', 'g': 'g',
    'ml': 'ml', 'ML': 'ml',
    'L': 'L', 'l': 'L',
    'kg': 'kg', 'KG': 'kg',
    'oz': 'oz', 'fl oz': 'ml', 'floz': 'ml',
}

CONVERSION = {
    'g': 1.0,
    'kg': 1000.0,
    'ml': 1.0,       # treat ml ≈ g (water density)
    'L': 1000.0,
    'oz': 28.3495,
    'piece': np.nan, # not convertible to grams
}


def parse_weight_to_grams(raw):
    """Return weight in grams (float) or NaN."""
    if pd.isna(raw) or str(raw).strip() == '':
        return np.nan

    raw = str(raw).strip()

    # Format B: "650g  |  EGP 8.96/100g" → take the part before |
    if '|' in raw:
        raw = raw.split('|')[0].strip()

    # Remove bracketed content like "(30gx12 Piece)"
    # Keep the first number+unit group
    raw = re.sub(r'\(.*?\)', '', raw).strip()

    # Try to extract numeric value and unit
    # Pattern: number(s)  then optional space  then unit text
    match = re.match(
        r'^([\d]+(?:[.,][\d]+)?)\s*'
        r'(جرام|جم|غرام|غم|كيلوجرام|كجم|كيلو|مل|ملليلتر|لتر|لترات|'
        r'grams?|kg|KG|ml|ML|L\b|l\b|g\b|G\b|oz|fl\s*oz|floz|pieces?|قطعة)?',
        raw, re.IGNORECASE
    )

    if not match:
        return np.nan

    value_str = match.group(1).replace(',', '.')
    unit_raw = (match.group(2) or '').strip()

    try:
        value = float(value_str)
    except ValueError:
        return np.nan

    if value <= 0:
        return np.nan

    # Map unit to canonical
    unit = ARABIC_TO_UNIT.get(unit_raw, ARABIC_TO_UNIT.get(unit_raw.lower(), None))

    if unit is None:
        # No unit found — if value looks like reasonable grams (1–50000) keep it
        if 1 <= value <= 50000:
            return value
        return np.nan

    factor = CONVERSION.get(unit, np.nan)
    if pd.isna(factor):
        return np.nan

    return round(value * factor, 4)


df['item_weight_grams'] = df['item_weight'].apply(parse_weight_to_grams)
df.drop(
    columns=['item_weight'],
    inplace=True,
    errors='ignore'
)

# 12. NUMBER_OF_ITEMS — fill missing with 1
df['number_of_items'] = pd.to_numeric(df['number_of_items'], errors='coerce')
df['number_of_items'] = df['number_of_items'].fillna(1.0)


# 13. PRICE_PER_UNIT (feature engineering)
#     = price / number_of_items
df['price_per_unit'] = (df['price'] / df['number_of_items']).round(4)


# 14. RATING — clip to valid range [0, 5]
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df.loc[df['rating'] < 0, 'rating'] = np.nan
df.loc[df['rating'] > 5, 'rating'] = np.nan
df['rating'] = df['rating'].round(2)
df['rating_count'] = pd.to_numeric(df['rating_count'], errors='coerce').astype('Int64')

# DATE — parse and standardise to YYYY-MM-DD
df['start_date'] = pd.to_datetime(
    df['date'],
    errors='coerce'
).dt.strftime('%Y-%m-%d')

df.drop(columns=['date'], inplace=True)

# FINAL TYPE ENFORCEMENT
str_cols = ['sku', 'source', 'category', 'sub_category',
            'product_name', 'brand', 'start_date']
for c in str_cols:
    df[c] = df[c].astype('string')

float_cols = ['price', 'price_per_unit', 'number_of_items', 'rating']
for c in float_cols:
    df[c] = pd.to_numeric(df[c], errors='coerce')

# SAVE
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding='utf-8-sig'
)

df.to_parquet(
    'noon_clean.parquet',
    index=False
)


# 20. SUMMARY REPORT
print("\n" + "=" * 55)
print("CLEANING SUMMARY")
print("=" * 55)
print(f"Output rows      : {len(df):,}")
print(f"Output columns   : {list(df.columns)}")
print(f"\nNull counts per column:")
print(df.isnull().sum().to_string())
print(f"\nItem weight coverage : {df['item_weight_grams'].notna().sum():,} / {len(df):,}")
print(f"Rating coverage      : {df['rating'].notna().sum():,} / {len(df):,}")
print(f"\nPrice range    : {df['price'].min():.2f} – {df['price'].max():.2f}")
print(f"Categories     : {sorted(df['category'].dropna().unique().tolist())}")
print(f"\nSaved → {OUTPUT_FILE}")