#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import csv
import json
import re
import time
from urllib.parse import urljoin, urlparse, urlunparse

from httpx import options
from httpx import options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)

# =========================
# CONFIGS
# =========================
CONFIGS = [
    {
        "start_url": "https://www.noon.com/egypt-en/grocery-store/cooking-and-baking-supplies/oils-vinegars-and-salad-dressings/",
        "output_csv": "noonoils.csv",
        "category": "Grocery",
        "sub_category": "oils",
    },
    {
        "start_url": "https://www.noon.com/egypt-en/grocery-store/beverages-16314/juices/",
        "output_csv": "noonjuices.csv",
        "category": "Beverages",
        "sub_category": "juice",
    },
    {
        "start_url": "https://www.noon.com/egypt-en/grocery-store/Herbs%20&%20Spices/",
        "output_csv": "noonherbs.csv",
        "category": "Grocery",
        "sub_category": "Herbs&Spices",
    },
    {
        "start_url": "https://www.noon.com/egypt-en/grocery-store/breakfast-foods/",
        "output_csv": "noonbreakfast.csv",
        "category": "Grocery",
        "sub_category": "breakfast",
    },
    {
        "start_url": "https://www.noon.com/egypt-ar/grocery-store/dried-beans-grains-and-rice/",
        "output_csv": "noondriedbeans.csv",
        "category": "Grocery",
        "sub_category": "Dried Beans, Grains and Rice",
    },
    {
        "start_url": "https://www.noon.com/egypt-ar/grocery-store/beverages-16314/tea/",
        "output_csv": "noonte.csv",
        "category": "Grocery",
        "sub_category": "Tea",
    },
    {
        "start_url": "https://www.noon.com/egypt-ar/grocery-store/beverages-16314/coffee/",
        "output_csv": "nooncoffee.csv",
        "category": "Grocery",
        "sub_category": "Coffee",
    },
    {
        "start_url": "https://www.noon.com/egypt-ar/grocery-store/dairy-cheese-and-eggs/",
        "output_csv": "noondairy.csv",
        "category": "Grocery",
        "sub_category": "Dairy Cheese and Eggs",
    },
    {
        "start_url": "https://www.noon.com/egypt-ar/grocery-store/dried-beans-grains-and-rice/",
        "output_csv": "noondriedbeans.csv",
        "category": "Grocery",
        "sub_category": "Rice",
    },
    {
        "start_url": "https://www.noon.com/egypt-ar/grocery-store/beverages-16314/water-22803/",
        "output_csv": "noonwater.csv",
        "category": "Grocery",
        "sub_category": "Water",
    },
    {
        "start_url": "https://www.noon.com/egypt-en/grocery-store/beverages-16314/soft-drinks/",
        "output_csv": "noonsoftdrinks.csv",
        "category": "Beverages",
        "sub_category": "Soft Drinks",
    },
    {
        "start_url": "https://www.noon.com/egypt-en/grocery-store/canned-dry-and-packaged-foods/condiments-sauces/",
        "output_csv": "noonsauces.csv",
        "category": "Grocery",
        "sub_category": "Sauces",
    },
    {
        "start_url": "https://www.noon.com/egypt-en/eg-salt-sugar/",
        "output_csv": "noonsalt.csv",
        "category": "Grocery",
        "sub_category": "Salt",
    },
]

BASE_URL = "https://www.noon.com"
SOURCE = "noon"

HEADLESS = False
WAIT_SECONDS = 1
SCROLL_PAUSE = 1.2

# =========================
# DRIVER
# =========================
def make_driver():
    options = ChromeOptions()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # Force English (US)
    options.add_argument("--lang=en-US")

    prefs = {
        "intl.accept_languages": "en-US,en"
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    driver.maximize_window()
    return driver

# =========================
# HELPERS
# =========================
def clean(text):
    if not text:
        return None
    return re.sub(r"\s+", " ", str(text)).strip()


def normalize_url(href):
    if not href:
        return None
    href = urljoin(BASE_URL, href)
    parsed = urlparse(href)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))


# =========================
# SCRAPING LISTING
# =========================
def wait_for_products(driver):
    WebDriverWait(driver, WAIT_SECONDS).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/p/']"))
    )


def collect_product_links(driver):
    links = set()
    anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
    for a in anchors:
        try:
            href = normalize_url(a.get_attribute("href"))
            if href:
                links.add(href)
        except:
            continue
    return list(links)


def scroll(driver):

    last_count = 0
    same_count = 0

    while same_count < 3:

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        time.sleep(2.5)

        current = len(collect_product_links(driver))

        print("Links:", current)

        if current == last_count:
            same_count += 1
        else:
            same_count = 0
            last_count = current


def scrape_listing(driver, start_url):
    driver.get(start_url)

    all_links = set()
    page = 1

    while True:
        print(f"\n========== PAGE {page} ==========")

        wait_for_products(driver)
        scroll(driver)

        links = collect_product_links(driver)

        all_links.update(links)

        print(f"Current page links : {len(links)}")
        print(f"Total unique links : {len(all_links)}")

        # الانتقال للصفحة التالية
        try:
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "a[aria-label='Next page']"
                    )
                )
            )

            next_url = next_btn.get_attribute("href")

            if not next_url:
                break

            driver.get(urljoin(driver.current_url, next_url))

            page += 1

        except Exception as e:
            print("No more pages.", e)
            break

    return list(all_links)


# =========================
# SCRAPING PRODUCT
# =========================
def first_text(driver, selector):
    try:
        return clean(driver.find_element(By.CSS_SELECTOR, selector).text)
    except:
        return None

def accept_popups(driver):
    selectors = [
        (By.XPATH, "//button[contains(., 'Accept') or contains(., 'قبول') or contains(., 'موافق')]"),
        (By.XPATH, "//button[contains(., 'Got it') or contains(., 'حسناً')]"),
        (By.CSS_SELECTOR, "[data-qa*='cookie'] button"),
        (By.CSS_SELECTOR, "button[aria-label*='close' i]"),
        (By.CSS_SELECTOR, "button[aria-label*='إغلاق']"),
    ]

    for by, selector in selectors:
        try:
            elements = driver.find_elements(by, selector)
            for element in elements[:3]:
                if element.is_displayed() and element.is_enabled():
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(0.4)
        except WebDriverException:
            continue

def get_body_lines(driver):
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text
        return [clean(line) for line in body_text.splitlines() if clean(line)]
    except WebDriverException:
        return []

def parse_price(text):
    if not text:
        return None

    patterns = [
        r"(?:جنيه|EGP)\s*([0-9][0-9,]*(?:\.[0-9]+)?)",
        r"([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:جنيه|EGP)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).replace(",", "")

    return None

def extract_json_ld(driver):
    data = {}

    try:
        scripts = driver.find_elements(By.CSS_SELECTOR, "script[type='application/ld+json']")
    except WebDriverException:
        return data

    for script in scripts:
        try:
            raw = script.get_attribute("innerHTML")
            if not raw:
                continue

            parsed = json.loads(raw)
            items = parsed if isinstance(parsed, list) else [parsed]

            for item in items:
                if not isinstance(item, dict):
                    continue

                if item.get("@type") == "Product":
                    data["product_name"] = clean(item.get("name"))

                    brand = item.get("brand")
                    if isinstance(brand, dict):
                        data["brand"] = clean(brand.get("name"))
                    elif isinstance(brand, str):
                        data["brand"] = clean(brand)

                    offers = item.get("offers")
                    if isinstance(offers, dict):
                        data["price"] = clean(offers.get("price"))

                    rating = item.get("aggregateRating")
                    if isinstance(rating, dict):
                        data["rating"] = clean(rating.get("ratingValue"))
                        data["rating_count"] = clean(
                            rating.get("ratingCount") or rating.get("reviewCount")
                        )

        except Exception:
            continue

    return data

def parse_weight(text):
    if not text:
        return None

    pattern = (
        r"([0-9]+(?:[.,][0-9]+)?\s*"
        r"(?:كيلوجرام|كيلو جرام|كيلو|كجم|كغ|kg|"
        r"غرام|جرام|جم|g|"
        r"ملليلتر|مللي|مل|ml|"
        r"لتر|liter|litre|l))"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return clean(match.group(1).replace(",", "."))

    return None


def parse_units(text):
    if not text:
        return None

    patterns = [
        r"(?:عبوة من|pack of)\s*([0-9]+)",
        r"([0-9]+)\s*(?:قطعة|قطع|pcs|pieces|count|عبوة|علبة|زجاجة)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return None

def parse_rating(text):
    if not text:
        return None, None

    patterns = [
        r"\b([0-5](?:\.[0-9])?)\s+([0-9,]+)\s*(?:تقييم|تقييمات|Ratings?|Reviews?)",
        r"\b([0-5](?:\.[0-9])?)\b.*?([0-9,]+)\s*(?:تقييم|تقييمات|Ratings?|Reviews?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2).replace(",", "")

    rating_match = re.search(r"\b([0-5](?:\.[0-9])?)\b", text)
    if rating_match and ("تقييم" in text or "rating" in text.lower()):
        return rating_match.group(1), None

    return None, None

def value_after_label(lines, labels):
    for index, line in enumerate(lines):
        for label in labels:
            if line == label and index + 1 < len(lines):
                return lines[index + 1]

            if line.startswith(label + " "):
                return clean(line.replace(label, "", 1))

            if line.startswith(label + ":"):
                return clean(line.replace(label + ":", "", 1))

    return None

def scrape_product(driver, url, category, sub_category):
    row = {
        "source": SOURCE,
        "category": category,
        "sub_category": sub_category,
        "product_name": None,
        "product_link": url,
        "price": None,
        "brand": None,
        "item_weight": None,
        "unit_count": None,
        "number_of_items": None,
        "package_weight": None,
        "rating": None,
        "rating_count": None,
    }

    try:
        driver.get(url)
        accept_popups(driver)

        WebDriverWait(driver, WAIT_SECONDS).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        time.sleep(1)
    except TimeoutException:
        print(f"[WARN] Timeout product page: {url}")
        return row
    except WebDriverException as e:
        print(f"[WARN] Failed product page: {url} | {e}")
        return row

    lines = get_body_lines(driver)
    full_text = "\n".join(lines)

    json_ld = extract_json_ld(driver)

    row["product_name"] = json_ld.get("product_name") or first_text(
        driver,
        [
            (By.CSS_SELECTOR, "[data-qa*='product-name']"),
            (By.CSS_SELECTOR, "[data-qa*='product-title']"),
            (By.TAG_NAME, "h1"),
        ],
    )

    row["brand"] = json_ld.get("brand") or first_text(
        driver,
        [
            (By.CSS_SELECTOR, "[data-qa*='brand']"),
            (By.CSS_SELECTOR, "a[href*='brand']"),
            (By.XPATH, "//h1/preceding::a[1]"),
        ],
    )

    row["price"] = json_ld.get("price") or parse_price(full_text)

    parsed_rating, parsed_rating_count = parse_rating(full_text)
    row["rating"] = json_ld.get("rating") or parsed_rating
    row["rating_count"] = json_ld.get("rating_count") or parsed_rating_count

    item_weight = value_after_label(
        lines,
        [
            "الحجم",
            "الوزن",
            "وزن السلعة",
            "السعة",
            "Item Weight",
            "Size",
            "Net Weight",
            "Capacity",
            "Volume",
        ],
    )

    package_weight = value_after_label(
        lines,
        [
            "وزن العبوة",
            "Package Weight",
            "Package weight",
            "وزن الشحنة",
        ],
    )

    unit_count = value_after_label(
        lines,
        [
            "عدد الوحدات",
            "عدد القطع",
            "Unit Count",
            "Number of Items",
            "Pack Count",
        ],
    )

    row["item_weight"] = (
        item_weight
        or parse_weight(row["product_name"])
        or parse_weight(full_text)
    )

    row["package_weight"] = package_weight

    row["unit_count"] = (
        unit_count
        or parse_units(row["product_name"])
        or parse_units(full_text)
    )

    row["number_of_items"] = row["unit_count"]

    return row


# =========================
# SAFE SAVE + BACKUP
# =========================
def save(rows, path):
    if not rows:
        return

    keys = rows[0].keys()
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def save_backup(rows, path):
    if not rows:
        return

    backup_path = path.replace(".csv", "_backup.csv")
    try:
        keys = rows[0].keys()
        with open(backup_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
    except Exception as e:
        print("[BACKUP ERROR]", e)


# =========================
# PIPELINE
# =========================
def run_config(driver, cfg):
    print(f"\n[START] {cfg['start_url']}")

    links = scrape_listing(driver, cfg["start_url"])
    print(f"[INFO] links: {len(links)}")

    rows = []

    for i, link in enumerate(links, 1):
        print(f"[PRODUCT] {i}/{len(links)}")

        try:
            row = scrape_product(
                driver,
                link,
                cfg["category"],
                cfg["sub_category"],
            )
            rows.append(row)

        except Exception as e:
            print("[ERROR]", e)

        # ✅ auto-save every 10 items
        if i % 10 == 0:
            save(rows, cfg["output_csv"])
            save_backup(rows, cfg["output_csv"])

    # final save
    save(rows, cfg["output_csv"])
    save_backup(rows, cfg["output_csv"])

    print(f"[DONE] saved {cfg['output_csv']}")


# =========================
# MAIN (CRASH SAFE)
# =========================
def main():
    driver = make_driver()

    try:
        for cfg in CONFIGS:
            try:
                run_config(driver, cfg)
            except Exception as e:
                print("[CONFIG CRASH]", e)
                continue

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
