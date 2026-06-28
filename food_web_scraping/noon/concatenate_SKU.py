#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import os
import re

files = [
    'noonbreakfast.csv',
    'nooncoffee.csv',
    'noondairy.csv',
    'noondriedbeans.csv',
    'noonherbs.csv',
    'noonjuices.csv',
    'noonoils.csv',
    'noonsalt.csv',
    'noonsauces.csv',
    'noonsoftdrinks.csv',
    'noonte.csv',
    'noonwater.csv'
]

frames = []

# -------------------------
# Load new files safely
# -------------------------
for file in files:
    try:
        if not os.path.exists(file):
            print(f"Skip missing: {file}")
            continue

        try:
            df = pd.read_csv(file)
        except UnicodeDecodeError:
            df = pd.read_csv(file, encoding="latin1")

        frames.append(df)

    except Exception as e:
        print(f"Error loading {file}: {e}")

if not frames:
    raise ValueError("No new files loaded")

new_data = pd.concat(frames, ignore_index=True)

def extract_sku(url):
    if pd.isna(url):
        return None

    match = re.search(r'/([A-Z0-9]+)/(?:p/|\?)', url)
    if match:
        return match.group(1)

    return None

# Apply extraction
new_data["sku"] = new_data["product_link"].apply(extract_sku)

# Move SKU column to first position
cols = ['sku'] + [col for col in new_data.columns if col != 'sku' and col != 'product_link']
new_data = new_data[cols]

# add date
new_data["date"] = pd.to_datetime("today").strftime("%Y-%m-%d")

# -------------------------
# If old file exists → append it
# -------------------------
output_file = "noon_products.csv"

if os.path.exists(output_file):
    try:
        old_data = pd.read_csv(output_file)
        combined = pd.concat([old_data, new_data], ignore_index=True)
        print("Existing file found → appending data")
    except Exception as e:
        print(f"Could not read existing file, rewriting: {e}")
        combined = new_data
else:
    print("No existing file → creating new one")
    combined = new_data

# -------------------------
# Save final result
# -------------------------
combined.to_csv(output_file, index=False)

print(f"Done! Total rows: {len(combined)}")

# In[3]:


# Move processed files to bin

import os 
import shutil 

files = [
    'noonbreakfast.csv',
    'nooncoffee.csv',
    'noondairy.csv',
    'noondriedbeans.csv',
    'noonherbs.csv',
    'noonjuices.csv',
    'noonoils.csv',
    'noonsalt.csv',
    'noonsauces.csv',
    'noonsoftdrinks.csv',
    'noonte.csv',
    'noonwater.csv'
]

# create bin folder if it doesn't exist
bin_folder = "bin"
os.makedirs(bin_folder, exist_ok=True)
for file in files:
    if os.path.exists(file):
        destination = os.path.join(bin_folder, file)
        shutil.move(file, destination)
        print(f"Moved: {file} → {bin_folder}/")
    else:
        print(f"Not found: {file}")
