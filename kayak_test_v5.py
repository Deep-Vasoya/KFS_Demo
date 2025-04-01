import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless=new")  # Use new headless mode
options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass bot detection
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options)

try:
    driver.get("https://www.kayak.com")
    time.sleep(5)
    print("Current URL:", driver.current_url)
    print("Title:", driver.title)
finally:
    driver.quit()  # Ensures ChromeDriver exits properly
    print("Driver closed successfully.")
