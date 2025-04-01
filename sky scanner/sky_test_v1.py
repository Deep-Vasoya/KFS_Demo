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
departure_airport = "LOND"
arrival_airport = "DBV"

# Date Range
start_date = datetime(2025, 4, 1)
end_date = datetime(2025, 4, 10)

all_flights = []

# Loop through the date range
while start_date <= end_date:
    return_date = start_date + timedelta(days=8)

    url = f"https://www.skyscanner.net/transport/flights/{departure_airport.lower()}/{arrival_airport.lower()}/{start_date.strftime('%y%m%d')}/{return_date.strftime('%y%m%d')}/?adultsv2=2&cabinclass=economy&childrenv2=&inboundaltsenabled=false&outboundaltsenabled=false&preferdirects=true&rtn=1"

    print(f"Scraping: {url}")
    driver.get(url)

    try:
        # ✅ Wait for flight results to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'FlightsTicket_container')]"))
        )

        flights = driver.find_elements(By.XPATH, "//div[contains(@class, 'FlightsTicket_container')]")

        if flights:
            cheapest_flight = flights[0]  # ✅ Extract only the cheapest flight

            airline = cheapest_flight.find_elements(By.XPATH, ".//div[contains(@class, 'AgentDetails_agentNameContainer__MjB1M')]")
            price = cheapest_flight.find_elements(By.XPATH, ".//div[contains(@class, 'TotalPrice_mainPriceContainer__Nj1iZ')]//span[contains(@class, 'BpkText_bpk-text')]")
            duration = cheapest_flight.find_elements(By.XPATH, "//div[contains(@class, 'LegInfo_stopsContainer__NDZmZ')]//span[contains(@class, 'Duration_duration')]")

            airline = airline[0].text if airline else "Unknown"
            price = price[0].text if price else "Unknown"
            duration = duration[0].text if duration else "Unknown"

            print(f"✅ Cheapest Flight - Airline: {airline}, Price: {price}, Duration: {duration}")

            all_flights.append([
                start_date.strftime('%Y-%m-%d'),
                return_date.strftime('%Y-%m-%d'),
                airline,
                price,
                duration
            ])
        else:
            print("❌ No flights found on this date.")

    except Exception as e:
        print("❌ Error: No flight data found for this date. Skipping...", e)

    start_date += timedelta(days=1)

# ✅ Save to Excel
df = pd.DataFrame(all_flights, columns=["Departure Date", "Return Date", "Airline", "Price", "Duration"])
df.to_excel("skyscanner_cheapest_flights.xlsx", index=False)
print("✅ Data saved to skyscanner_cheapest_flights.xlsx")

# ✅ Gracefully quit WebDriver
driver.quit()
sys.exit(0)
