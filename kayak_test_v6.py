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

all_flights = []

# Loop through the date range
while start_date <= end_date:
    return_date = start_date + timedelta(days=8)

    url = f"https://www.kayak.com/flights/{departure_airport}-{arrival_airport}/{start_date.strftime('%Y-%m-%d')}/{return_date.strftime('%Y-%m-%d')}?sort=price_a"

    print(f"Scraping: {url}")
    driver.get(url)

    try:
        # ✅ Wait for flight results to appear
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'nrc6')]"))
        )

        flights = driver.find_elements(By.XPATH, "//div[contains(@class, 'nrc6')]")

        for flight in flights:
            try:
                airline = flight.find_elements(By.XPATH, ".//div[contains(@class, 'c_cgF')]")
                price = flight.find_elements(By.XPATH, ".//div[contains(@class, 'f8F1-price-text')]")
                duration = flight.find_elements(By.XPATH, ".//div[contains(@class, 'vmXl')]")

                # ✅ Extract departure and arrival using JavaScript (more reliable)
                departure = driver.execute_script(
                    "return arguments[0].querySelector('span.depart-time')?.innerText || 'Unknown';", flight)
                arrival = driver.execute_script(
                    "return arguments[0].querySelector('span.arrival-time')?.innerText || 'Unknown';", flight)

                # ✅ Extract text safely
                airline = airline[0].text if airline else "Unknown"
                price = price[0].text if price else "Unknown"
                duration = duration[0].text if duration else "Unknown"

                print(f"✅ Found Flight - Airline: {airline}, Price: {price}, Duration: {duration}, Departure: {departure}, Arrival: {arrival}")

                # ✅ Filter flights under 30 hours
                if "h" in duration:
                    duration_parts = duration.replace("m", "").split("h")
                    hours = int(duration_parts[0]) if duration_parts[0].isdigit() else 0
                else:
                    hours = 0  # Default if duration is missing

                if hours <= 30:
                    all_flights.append([
                        start_date.strftime('%Y-%m-%d'),
                        return_date.strftime('%Y-%m-%d'),
                        airline,
                        price,
                        duration,
                        departure,
                        arrival
                    ])
            except Exception as e:
                print("❌ Skipping flight due to error:", e)

    except Exception as e:
        print("❌ Error: No flight data found for this date. Skipping...", e)

    start_date += timedelta(days=1)

# ✅ Save to Excel
df = pd.DataFrame(all_flights, columns=["Departure Date", "Return Date", "Airline", "Price", "Duration", "Departure Time", "Arrival Time"])
df.to_excel("kayak_flights_fixed_v2.xlsx", index=False)
print("✅ Data saved to kayak_flights_fixed_v2.xlsx")

# ✅ Gracefully quit WebDriver
try:
    driver.quit()
except Exception as e:
    print("Error while closing WebDriver:", e)

sys.exit(0)
