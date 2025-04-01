import sys
import undetected_chromedriver as uc  # Bypasses bot detection by Kayak
from selenium.webdriver.chrome.options import Options  # selenium.webdriver = Automates web interactions, Options = running headless and disabling detection
from selenium.webdriver.common.by import By  # locate elements on a webpage
from selenium.webdriver.support.ui import WebDriverWait  # wait for elements to load dynamically
from selenium.webdriver.support import expected_conditions as EC  # a set of predefined conditions used to wait for elements (expected_conditions)
import pandas as pd  # Stores and processes flight data
from datetime import datetime, timedelta  # Handles date manipulations

# Setup Chrome (Configures Chrome to appear as a regular user by disabling detection features)
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled") # Disables browser automation detection
driver = uc.Chrome(options=options) # Initializes undetected chromedriver with the configured options

# Define Airports
departure_airport = "JFK" # Sets the departure airport to JFK (John F. Kennedy International Airport)
arrival_airport = "DPS" # Sets the arrival airport to DPS (Ngurah Rai International Airport, Bali)

# Date Range
start_date = datetime(2025, 4, 1) # Sets the start date for the search to April 1, 2025
end_date = datetime(2025, 4, 10) # Sets the end date for the search to April 10, 2025

all_flights = [] # Initializes an empty list to store the extracted flight data

# Loop through the date range
while start_date <= end_date: # Loop continues as long as the start date is less than or equal to the end date
    return_date = start_date + timedelta(days=8) # Calculates the return date, 8 days after the departure date

    url = f"https://www.kayak.com/flights/{departure_airport}-{arrival_airport}/{start_date.strftime('%Y-%m-%d')}/{return_date.strftime('%Y-%m-%d')}?sort=price_a" # Constructs the Kayak URL for the specific departure, arrival, and dates, sorted by price

    print(f"Scraping: {url}") # Prints the URL being scraped
    driver.get(url) # Opens the Kayak URL in the Chrome browser

    try:
        # Wait for flight results to appear
        WebDriverWait(driver, 30).until( # Waits up to 20 seconds for the element to load
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'nrc6')]")) # Waits for the element with the class 'nrc6' to be present, which contains flight results
        )
        cheapest_flight = driver.find_element(By.XPATH, "(//div[contains(@class, 'nrc6')])[1]") # Finds the first element with the class 'nrc6', which is assumed to be the cheapest flight

        # Get only the first (cheapest) flight

        # Extract details
        airline = cheapest_flight.find_elements(By.XPATH, ".//div[contains(@class, 'c_cgF')]") # Finds the airline name
        price = cheapest_flight.find_elements(By.XPATH, ".//div[contains(@class, 'f8F1-price-text')]") # Finds the price of the flight
        duration = cheapest_flight.find_elements(By.XPATH, ".//div[contains(@class, 'vmXl')]") # Finds the duration of the flight

        # Extract departure and arrival times
        departure = driver.execute_script( # Executes JavaScript to extract the departure time
            "return arguments[0].querySelector('span.depart-time')?.innerText || 'Unknown';", cheapest_flight)
        arrival = driver.execute_script( # Executes JavaScript to extract the arrival time
            "return arguments[0].querySelector('span.arrival-time')?.innerText || 'Unknown';", cheapest_flight)

        # Extract total travel time using the fixed XPath
        total_time_element = cheapest_flight.find_elements(By.XPATH, ".//div[contains(@class, 'xdW8')]/div[contains(@class, 'vmXl')]") # Finds the total travel time
        total_time = total_time_element[0].text.strip() if total_time_element else "Unknown" # Retrieves the text if element is found, otherwise sets to "Unknown"

        # Extract text safely
        airline = airline[0].text if airline else "Unknown" # Retrieves the airline name if found, otherwise sets to "Unknown"
        price = price[0].text if price else "Unknown" # Retrieves the price if found, otherwise sets to "Unknown"
        duration = duration[0].text if duration else "Unknown" # Retrieves the duration if found, otherwise sets to "Unknown"

        print(f"✅ Cheapest Flight - Airline: {airline}, Price: {price}, Duration: {duration}, Departure: {departure}, Arrival: {arrival}, Total Time: {total_time}") # Prints the extracted flight details

        # Save only the cheapest flight for that date
        all_flights.append([ # Appends the flight details to the all_flights list
            start_date.strftime('%Y-%m-%d'), # Departure date
            return_date.strftime('%Y-%m-%d'), # Return date
            airline, # Airline name
            price, # Price
            duration, # Duration
            departure, # Departure time
            arrival, # Arrival time
            total_time # Total Travel time
        ])

    except Exception as e: # Handles any exceptions that occur during the scraping process
        print("❌ Error: No flight data found for this date. Skipping...", e) # Prints an error message if flight data is not found

    start_date += timedelta(days=1) # Increments the start date by one day

# Save to Excel
df = pd.DataFrame(all_flights, columns=["Departure Date", "Return Date", "Airline", "Price", "Duration", "Departure Time", "Arrival Time", "Total Time"]) # Creates a pandas DataFrame from the all_flights list
df.to_excel("kayak_cheapest_flights_v3.xlsx", index=False) # Saves the DataFrame to an Excel file
print("✅ Data saved to kayak_cheapest_flights_v3.xlsx") # Prints a success message

# Quit WebDriver
try:
    driver.quit() # Closes the WebDriver
except Exception as e:
    print("Error while closing WebDriver:", e) # Handles any errors that occur while closing the WebDriver

sys.exit(0) # Exits the program with a success code