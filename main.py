import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# ----- تنظیمات تلگرام -----
TOKEN = "8267872006:AAFV-CA7QtN1X8AkRPIgfZPdApi6OFdYnRM"
CHAT_ID = "@tala995"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

def send_to_telegram(text):
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    try:
        response = requests.post(TELEGRAM_API_URL, json=payload)
        print("Telegram API Response:", response.text)
    except Exception as e:
        print("Error sending to Telegram:", e)

# ----- تنظیمات Selenium -----
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get("https://www.estjt.ir/")
    time.sleep(5)  # برای لود کامل

    message_gold = "🏆 قیمت طلا:\n"
    message_coin = "💰 قیمت سکه:\n"

    tables = driver.find_elements(By.TAG_NAME, "table")
    for table_index, table in enumerate(tables):
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) == 3:
                # ترتیب واقعی HTML: نام، قیمت، تغییرات
                name = cols[0].text.strip()
                price = cols[1].text.strip()

                if name and price:
                    if table_index == 0:  # جدول اول = طلا
                        message_gold += f"{name}: {price}\n"
                    elif table_index == 1:  # جدول دوم = سکه
                        message_coin += f"{name}: {price}\n"

    final_message = message_gold.strip() + "\n\n" + message_coin.strip()
    send_to_telegram(final_message)

finally:
    driver.quit()
