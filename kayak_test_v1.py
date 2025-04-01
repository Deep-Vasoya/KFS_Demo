import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Configure Chrome in headless mode
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)

# Open Kayak flight search page
url = "https://www.kayak.com/flights/JFK-DPS/2025-04-01/2025-04-09?ucs=1rh1zr6&sort=price_a&fs=legdur=-1800;airlines=-MULT,flylocal;stops=1"
driver.get(url)

# Wait for results to load
time.sleep(10)  # Increase this if needed

# Extract flight details
flights = driver.find_elements(By.CLASS_NAME, "nrc6")
data = []  # Store data in a list

for flight in flights[:10]:  # Get first 10 flights
    try:
        price = flight.find_element(By.CLASS_NAME, "f8F1-price-text").text
        airline = flight.find_element(By.CLASS_NAME, "c_cgF").text
        duration = flight.find_element(By.CLASS_NAME, "vmXl").text

        # Append to list
        data.append({"Airline": airline, "Price": price, "Duration": duration})
    except:
        continue

# Convert to DataFrame and save to Excel
df = pd.DataFrame(data)
df.to_excel("kayak_flights.xlsx", index=False)

print("✅ Data saved to kayak_flights.xlsx")

driver.quit()
