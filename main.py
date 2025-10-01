import json
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# ----- تنظیمات تلگرام (هاردکد شده طبق توافق) -----
TOKEN = "8267872006:AAFV-CA7QtN1X8AkRPIgfZPdApi6OFdYnRM"
CHAT_ID = "@tala995"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# فایل ذخیره آخرین قیمت‌ها
LAST_FILE = "last_prices.json"


def send_to_telegram(text):
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        response = requests.post(TELEGRAM_API_URL, json=payload)
        print("Telegram API Response:", response.text)
    except Exception as e:
        print("Error sending to Telegram:", e)


def scrape_prices():
    """دریافت قیمت‌ها از estjt.ir با Selenium"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://www.estjt.ir/")
    time.sleep(5)  # برای لود کامل صفحه

    tables = driver.find_elements(By.TAG_NAME, "table")
    data = {}
    for table_index, table in enumerate(tables):
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) == 3:
                # ستون 0: نام، ستون 1: قیمت، ستون 2: تغییرات
                name = cols[0].text.strip()
                price = cols[1].text.strip()
                if name and price:
                    data[name] = price
    driver.quit()
    return data


def prices_changed(new_data):
    """بررسی اینکه قیمت‌ها تغییر کرده‌اند یا نه"""
    if not os.path.exists(LAST_FILE):
        return True
    try:
        with open(LAST_FILE, "r", encoding="utf-8") as f:
            last_data = json.load(f)
        return new_data != last_data
    except:
        return True


def save_prices(data):
    """ذخیره قیمت‌ها برای دفعه بعد"""
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    prices = scrape_prices()

    if prices_changed(prices):
        # بخش‌بندی پیام
        message_gold = "🏆 قیمت طلا:\n"
        message_coin = "💰 قیمت سکه:\n"

        for name, price in prices.items():
            if "سکه" in name:
                message_coin += f"{name}: {price}\n"
            else:
                message_gold += f"{name}: {price}\n"

        final_message = f"{message_gold.strip()}\n\n{message_coin.strip()}"
        send_to_telegram(final_message)
        save_prices(prices)
    else:
        print("🔄 قیمت‌ها تغییری نکرده‌اند، پیامی ارسال نشد.")
