import sys
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime, timedelta

# Setup Chrome
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=options)

# Define Airports
departure_airport = "JFK"
arrival_airport = "DPS"

# Date Range
start_date = datetime(2025, 4, 1)
end_date = datetime(2025, 4, 10)

cheapest_flights = []

# Loop through the date range
while start_date <= end_date:
    return_date = start_date + timedelta(days=8)

    url = f"https://www.kayak.com/flights/{departure_airport}-{arrival_airport}/{start_date.strftime('%Y-%m-%d')}/{return_date.strftime('%Y-%m-%d')}?sort=price_a"

    print(f"Scraping: {url}")
    driver.get(url)

    try:
        # ✅ Wait for the cheapest flight to appear
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'nrc6')]"))
        )

        # ✅ Select ONLY the cheapest flight (first result)
        cheapest_flight = driver.find_element(By.XPATH, "(//div[contains(@class, 'nrc6')])[1]")

        airline = cheapest_flight.find_element(By.XPATH, ".//div[contains(@class, 'c_cgF')]").text
        price = cheapest_flight.find_element(By.XPATH, ".//div[contains(@class, 'f8F1-price-text')]").text
        duration = cheapest_flight.find_element(By.XPATH, ".//div[contains(@class, 'vmXl')]").text

        # ✅ Extract departure & arrival times using JavaScript
        departure = driver.execute_script(
            "return arguments[0].querySelector('span.depart-time')?.innerText || 'Unknown';", cheapest_flight)
        arrival = driver.execute_script(
            "return arguments[0].querySelector('span.arrival-time')?.innerText || 'Unknown';", cheapest_flight)

        # ✅ Convert duration into total hours & minutes
        if "h" in duration:
            duration_parts = duration.replace("m", "").split("h")
            hours = int(duration_parts[0]) if duration_parts[0].isdigit() else 0
            minutes = int(duration_parts[1]) if len(duration_parts) > 1 and duration_parts[1].isdigit() else 0
        else:
            hours = 0
            minutes = 0

        total_time = f"{hours}h {minutes}m"

        print(f"✅ Cheapest Flight - Airline: {airline}, Price: {price}, Duration: {duration}, Departure: {departure}, Arrival: {arrival}, Total Time: {total_time}")

        cheapest_flights.append([
            start_date.strftime('%Y-%m-%d'),
            return_date.strftime('%Y-%m-%d'),
            airline,
            price,
            duration,
            departure,
            arrival,
            total_time
        ])

    except Exception as e:
        print("❌ No cheapest flight found for this date. Skipping...", e)

    start_date += timedelta(days=1)

# ✅ Save to Excel
df = pd.DataFrame(cheapest_flights, columns=["Departure Date", "Return Date", "Airline", "Price", "Duration", "Departure Time", "Arrival Time", "Total Time"])
df.to_excel("cheapest_flights.xlsx", index=False)
print("✅ Data saved to cheapest_flights.xlsx")

# ✅ Close WebDriver
try:
    driver.quit()
except Exception as e:
    print("Error while closing WebDriver:", e)

sys.exit(0)
