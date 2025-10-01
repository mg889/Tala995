import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# مقادیر از Secrets گیـت‌هاب
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
SITE_URL = "https://www.estjt.ir/"
CACHE_FILE = "last_prices.txt"

def fetch_prices():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # مسیر اجرایی Google Chrome در GitHub Actions
    options.binary_location = "/usr/bin/google-chrome"

    # مسیر chromedriver دانلود شده در Workflow
    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(SITE_URL)
    time.sleep(5)  # صبر برای لود کامل JS

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    def parse_table(title):
        header = soup.find("h3", string=title)
        if not header:
            return []
        table = header.find_next("table")
        rows = []
        for row in table.find_all("tr"):
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) >= 2:
                rows.append(f"{cols[0]} {cols[1]}")
        return rows

    gold = parse_table("قیمت طلا")
    coin = parse_table("قیمت سکه")
    return gold, coin

def send_to_channel(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHANNEL_USERNAME, "text": message})

def has_prices_changed(new_text):
    if not os.path.exists(CACHE_FILE):
        return True
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        old_text = f.read()
    return old_text != new_text

def save_prices(text):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    gold, coin = fetch_prices()
    text = "\n".join(gold)
