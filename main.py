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
chrome_options.add_argument("--headless")       # بدون رابط گرافیکی
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")  # مسیر کروم‌درایور در GitHub Actions

# ----- اجرای مرورگر -----
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get("https://www.estjt.ir")
    time.sleep(5)  # صبر برای لود کامل

    rows = driver.find_elements(By.CSS_SELECTOR, "table.data-table tr")
    prices_text = ""
    keywords = ["سکه", "طلای", "نیم", "ربع", "گرم"]  # کلیدواژه‌های موردنظر

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 2:
            name = cols[0].text.strip()
            price = cols[1].text.strip()
            if any(keyword in name for keyword in keywords):
                prices_text += f"{name}: {price}\n"

    # ارسال فقط اگر داده‌ای پیدا شده باشد
    if prices_text.strip():
        send_to_telegram(prices_text.strip())
    else:
        send_to_telegram("⚠️ هیچ داده‌ای برای طلا/سکه پیدا نشد.")

finally:
    driver.quit()
