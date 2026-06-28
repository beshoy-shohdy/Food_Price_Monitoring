#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Amazon Category Scraping

# In[2]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# =========================
# Setup
# =========================
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

url = "https://www.amazon.eg/gp/browse.html?node=26082334031&ref_=nav_cs_supermarket"
driver.get(url)

time.sleep(5)  # wait page load

# =========================
# Get Main Category
# =========================
category = driver.find_element(
    By.XPATH, "//div[contains(@class,'bxcGridText')]//h2/span"
).text

print("Category:", category)

# =========================
# Get Sub Categories
# =========================
sub_categories = driver.find_elements(
    By.XPATH, "//a[contains(@class,'bxcGridOverlayLink')]"
)

data = []

for sub in sub_categories:
    try:
        # sub category name
        name = sub.get_attribute("aria-label")

        # sub category link
        link = sub.get_attribute("href")

        data.append({
            "category": category,
            "sub_category": name,
            "link": link
        })

    except Exception as e:
        print("Error:", e)

# =========================
# Save to CSV
# =========================
df = pd.DataFrame(data)
df.to_csv("amazon_categories.csv", index=False, encoding="utf-8-sig")

print("Saved successfully!")

driver.quit()

# In[ ]:


# Real category links

# In[3]:


import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================
# Load CSV
# =========================
df = pd.read_csv("amazon_categories.csv")

# =========================
# Setup Selenium
# =========================
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

updated_links = []

# =========================
# Loop over links
# =========================
for index, row in df.iterrows():
    url = row["link"]
    print(f"Processing: {url}")

    driver.get(url)

    try:
        # scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # =========================
        # Get "See all" button
        # =========================
        see_all = wait.until(EC.presence_of_element_located((
            By.XPATH, "//a[contains(., 'See all') or contains(., 'عرض الكل')]"
        )))

        new_link = see_all.get_attribute("href")
        print("Found:", new_link)

    except:
        print("No see all found, keep original")
        new_link = url

    updated_links.append(new_link)

# =========================
# Update CSV
# =========================
df["see_all_link"] = updated_links

df.to_csv("amazon_categories_updated.csv", index=False, encoding="utf-8-sig")

driver.quit()

print("Done ✅")
