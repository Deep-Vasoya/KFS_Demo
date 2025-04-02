import sys
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime, timedelta
import random
import time  # Import the time module for static waits

# Setup Chrome
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=options)

# Define Airports
departure_airport = "JFK"
arrival_airport = "DPS"

# Date Range
start_date = datetime(2025, 5, 1)
end_date = datetime(2025, 5, 30)

all_flights = []

# Loop through the date range
while start_date <= end_date:
    return_date = start_date + timedelta(days=8)

    url = f"https://www.kayak.com/flights/{departure_airport}-{arrival_airport}/{start_date.strftime('%Y-%m-%d')}/{return_date.strftime('%Y-%m-%d')}?sort=price_a"

    print(f"Scraping: {url}")
    driver.get(url)

    try:
        # Static wait for 30 seconds
        print("Waiting 30 seconds for page to load...")
        time.sleep(30)  # Static wait for 30 seconds

        # Now, try to find the flight results.
        WebDriverWait(driver, random.randint(30, 40)).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'nrc6')]"))
        )
        cheapest_flight = driver.find_element(By.XPATH, "(//div[contains(@class, 'nrc6')])[1]")

        # Extract details
        airline = cheapest_flight.find_elements(By.XPATH, ".//div[contains(@class, 'c_cgF')]")
        price = cheapest_flight.find_elements(By.XPATH, ".//div[contains(@class, 'f8F1-price-text')]")
        duration = cheapest_flight.find_elements(By.XPATH, ".//div[contains(@class, 'vmXl')]")

        # Extract departure and arrival times
        departure = driver.execute_script(
            "return arguments[0].querySelector('span.depart-time')?.innerText || 'Unknown';", cheapest_flight)
        arrival = driver.execute_script(
            "return arguments[0].querySelector('span.arrival-time')?.innerText || 'Unknown';", cheapest_flight)

        # Extract total travel time
        total_time_element = cheapest_flight.find_elements(By.XPATH, ".//div[contains(@class, 'xdW8')]/div[contains(@class, 'vmXl')]")
        total_time = total_time_element[0].text.strip() if total_time_element else "Unknown"

        # Extract text safely
        airline = airline[0].text if airline else "Unknown"
        price = price[0].text if price else "Unknown"
        duration = duration[0].text if duration else "Unknown"

        print(f"✅ Cheapest Flight - Airline: {airline}, Price: {price}, Duration: {duration}, Departure: {departure}, Arrival: {arrival}, Total Time: {total_time}")

        # Save only the cheapest flight for that date
        all_flights.append([
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
        print("❌ Error: No flight data found for this date. Skipping...", e)

    start_date += timedelta(days=1)

# Save to Excel
df = pd.DataFrame(all_flights, columns=["Departure Date", "Return Date", "Airline", "Price", "Duration", "Departure Time", "Arrival Time", "Total Time"])
df.to_excel("kayak_cheapest_flights_v3.xlsx", index=False)
print("✅ Data saved to kayak_cheapest_flights_v3.xlsx")

# Quit WebDriver
try:
    driver.quit()
except Exception as e:
    print("Error while closing WebDriver:", e)

sys.exit(0)
