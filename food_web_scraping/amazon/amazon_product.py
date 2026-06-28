#!/usr/bin/env python
# coding: utf-8

# In[3]:


# Product links

# In[ ]:


import pandas as pd
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# =========================
# Load input
# =========================
print("Loading input...")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

csv_path = os.path.join(BASE_DIR, "amazon_categories_updated.csv")

df = pd.read_csv(csv_path)

output_file = os.path.join(BASE_DIR, "amazon_products.csv")

# لو الملف موجود، كمل عليه
if os.path.exists(output_file):
    products_df = pd.read_csv(output_file)
    collected_links = set(products_df["product_link"].tolist())
else:
    products_df = pd.DataFrame(columns=["category", "sub_category", "product_link"])
    collected_links = set()

# =========================
# Setup Selenium
# =========================

options = Options()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--blink-settings=imagesEnabled=false")

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

driver.set_page_load_timeout(30)
driver.set_script_timeout(30)
# =========================
# Helper: save instantly
# =========================
def save_data(new_rows):
    global products_df

    temp_df = pd.DataFrame(new_rows)
    products_df = pd.concat([products_df, temp_df], ignore_index=True)

    products_df.drop_duplicates(inplace=True)

    products_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Saved {len(products_df)} rows 💾")

# =========================
# Scraping
# =========================
try:
    for _, row in df.iterrows():
        category = row["category"]
        sub_category = row["sub_category"]
        url = row["see_all_link"]

        print(f"\nStart: {sub_category}")

        try:
            driver.get(url)
        except Exception as e:
            print("Page load failed:", e)

        while True:
            time.sleep(2)

            try:
                wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[@data-component-type='s-search-result']")
                ))
            except:
                print("Page load issue")

            products = driver.find_elements(
                By.XPATH,
                "//a[contains(@class,'s-link-style') and contains(@class,'a-text-normal')]"
            )

            new_rows = []

            for p in products:
                link = p.get_attribute("href")

                if link and link not in collected_links:
                    collected_links.add(link)

                    new_rows.append({
                        "category": category,
                        "sub_category": sub_category,
                        "product_link": link
                    })

            # 🔥 حفظ بعد كل صفحة
            if new_rows:
                save_data(new_rows)

            print(f"Page done, new: {len(new_rows)}")

            # =========================
            # Next page
            # =========================
            try:
                next_btn = driver.find_element(
                    By.XPATH,
                    "//a[contains(@class,'s-pagination-next') and not(contains(@class,'disabled'))]"
                )

                driver.execute_script("arguments[0].click();", next_btn)

            except:
                print("No more pages ✅")
                break

except Exception as e:
    print("🔥 ERROR:", e)
    print("Saving what we have before exit...")
    products_df.to_csv(output_file, index=False, encoding="utf-8-sig")

finally:
    driver.quit()
    print("Finished safely ✅")

# In[5]:


# Product data

# In[ ]:


import pandas as pd
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================
# Load products
# =========================
df = pd.read_csv(os.path.join(BASE_DIR, "amazon_products.csv"))

output_file = os.path.join(BASE_DIR, "amazon_product_details.csv")

# Resume
if os.path.exists(output_file):
    saved_df = pd.read_csv(output_file)
    done_links = set(saved_df["product_link"].tolist())
else:
    saved_df = pd.DataFrame()
    done_links = set()

# =========================
# Setup Selenium
# =========================
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# =========================
# Helper
# =========================
def safe_get(xpath):
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()
    except:
        return None

def save_row(row):
    global saved_df
    saved_df = pd.concat([saved_df, pd.DataFrame([row])], ignore_index=True)
    saved_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print("Saved 💾")

# =========================
# Scraping
# =========================
try:
    i = 0
    for _, r in df.iterrows():
        link = r["product_link"]

        if link in done_links:
            continue

        category = r["category"]
        sub_category = r["sub_category"]

        print(f"\n{i}: Open: {link}")
        i += 1
        driver.get(link)

        time.sleep(2)

        # =========================
        # Name
        # =========================
        name = safe_get("//span[@id='productTitle']")

        # =========================
        # Price (combine)
        # =========================
        try:
            whole = driver.find_element(By.CLASS_NAME, "a-price-whole").text
            fraction = driver.find_element(By.CLASS_NAME, "a-price-fraction").text
            price = f"{whole}.{fraction}"
        except:
            price = None

        # =========================
        # Click Top highlights
        # =========================
        try:
            btn = driver.find_element(
                By.XPATH, "//span[contains(text(),'Top highlights') or contains(text(),'أهم')]"
            )
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(1)
        except:
            pass

        # =========================
        # Extract Highlights
        # =========================
        def get_feature(row_class):
            try:
                return driver.find_element(
                    By.XPATH, f"//tr[contains(@class,'{row_class}')]//td[2]//span"
                ).text
            except:
                return None

        brand = get_feature("po-brand")
        item_weight = get_feature("po-item_weight")
        unit_count = get_feature("po-unit_count")
        num_items = get_feature("po-number_of_items")
        package_weight = get_feature("po-item_package_weight")

        # =========================
        # Save
        # =========================
        row_data = {
            "category": category,
            "sub_category": sub_category,
            "product_link": link,
            "product_name": name,
            "price": price,
            "brand": brand,
            "item_weight": item_weight,
            "unit_count": unit_count,
            "number_of_items": num_items,
            "package_weight": package_weight
        }

        save_row(row_data)
        done_links.add(link)

except Exception as e:
    print("🔥 ERROR:", e)
    print("Saving before exit...")
    saved_df.to_csv(output_file, index=False, encoding="utf-8-sig")

finally:
    driver.quit()
    print("Finished ✅")

# In[2]:


# add id and date

# In[2]:


import pandas as pd
import re
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(BASE_DIR, "amazon_product_details.csv")
output_file = os.path.join(BASE_DIR, "final_amazon_product_details.csv")

df = pd.read_csv(input_file)

link_column = "product_link"


def extract_asin(url):
    if pd.isna(url):
        return None
    

    patterns = [
        r"/dp/([A-Z0-9]{10})",
        r"/gp/product/([A-Z0-9]{10})",
        r"/product/([A-Z0-9]{10})"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, str(url))
        if match:
            return match.group(1)
    
    return None


df["SKU"] = df[link_column].apply(extract_asin)
df["start_date"] = datetime.date.today()

df.drop(columns=[link_column], inplace=True)
df.dropna(subset=["SKU"], inplace=True)

columns_order = [ "SKU","product_name", "price", "brand", "item_weight", "unit_count", "number_of_items", "package_weight", "category", "sub_category",  "start_date"]

df = df[columns_order]


df.to_csv(output_file, index=False)

print("Done ✅ File saved as:", output_file)
