import sys
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from datetime import datetime, timedelta
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    """Sets up the Chrome WebDriver with retry mechanism."""
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    for _ in range(3):  # Retry up to 3 times
        try:
            return uc.Chrome(options=options)
        except Exception as e:
            logging.error(f"Error setting up driver: {e}. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying
    logging.error("Failed to setup driver after multiple retries.")
    return None

def construct_skyscanner_url(departure, arrival, start, return_date, config_value):
    """Constructs the Skyscanner URL."""
    return f"https://www.skyscanner.net/transport/flights/{departure.lower()}/{arrival.lower()}/{start.strftime('%y%m%d')}/{return_date.strftime('%y%m%d')}/config/{config_value}?adultsv2=2&cabinclass=economy&childrenv2=&inboundaltsenabled=false&outboundaltsenabled=false&preferdirects=true&rtn=1&priceSourceId=&priceTrace=202503310647*D*LGW*FCO*20250601*wizz*W4%7C202503310710*D*FCO*LGW*20250606*wizz*W4&qp_prevCurrency=INR&qp_prevPrice=6029&qp_prevProvider=ins_month&currency=GBP&locale=en-GB&market=UK"

def scroll_to_bottom(driver):
    """Scrolls to the bottom of the page."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)  # Wait for the page to load after scrolling

def wait_for_data_load(driver):
    """Waits for the data to fully load."""
    try:
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'FlightsTicket_container')]"))
        )
        return True
    except TimeoutException:
        logging.error("Data did not load in time.")
        return False

def extract_flight_data(driver, start_date, return_date):
    """Extracts flight data from the page with robust error handling."""
    try:
        cheapest_flight = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "(//div[contains(@class, 'FlightsTicket_container')])[1]"))
        )
        if cheapest_flight:
            logging.info("Cheapest flight element found.")
            logging.info(f"Cheapest flight HTML: {cheapest_flight.get_attribute('innerHTML')}")
        else:
            logging.warning("Cheapest flight element NOT found.")
            return None

        # Updated XPath expressions
        airline_element = WebDriverWait(cheapest_flight, 20).until(
            EC.presence_of_element_located((By.XPATH, ".//span[@class='BpkText_bpk-text_MjhhY BpkText_bpk-text --xs_ZTBkZ']"))
        )
        airline = airline_element.text.strip() if airline_element and airline_element.is_displayed() else "Unknown"

        price_element = WebDriverWait(cheapest_flight, 20).until(
            EC.presence_of_element_located((By.XPATH, ".//span[@class='BpkText_bpk-text_MjhhY BpkText_bpk-text --heading-4_Y2FIY']"))
        )
        price = price_element.text.strip() if price_element and price_element.is_displayed() else "Unknown"

        duration_element = WebDriverWait(cheapest_flight, 20).until(
            EC.presence_of_element_located((By.XPATH, ".//span[@class='BpkText_bpk-text_MjhhY BpkText_bpk-text --caption_ZTYON Duration_duration_ZmY3M']"))
        )
        duration = duration_element.text.strip() if duration_element and duration_element.is_displayed() else "Unknown"

        logging.info(f"Cheapest Flight - Airline: {airline}, Price: {price}, Duration: {duration}")
        return [start_date.strftime('%Y-%m-%d'), return_date.strftime('%Y-%m-%d'), airline, price, duration]

    except TimeoutException:
        logging.error(f"Timeout: Flight data did not load in time for {start_date}.")
        return None
    except NoSuchElementException as e:
        logging.error(f"Element not found on page for {start_date}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error extracting flight data for {start_date}: {e}")
        return None

def main():
    """Main function to orchestrate the scraping with retry logic."""
    departure_airport = "LOND"
    arrival_airport = "ROME"
    start_date = datetime(2025, 6, 1)
    end_date = datetime(2025, 6, 10)
    config_value = "13542-2506012120--30596-0-11493-2506020055%7C11493-2506060710--30596-0-13542-2506060855" # Example config value
    all_flights = []
    driver = setup_driver()

    if driver is None:
        return

    try:
        while start_date <= end_date:
            return_date = start_date + timedelta(days=5) #5 days return date
            url = construct_skyscanner_url(departure_airport, arrival_airport, start_date, return_date, config_value)
            logging.info(f"Scraping: {url}")
            driver.get(url)

            scroll_to_bottom(driver) #scroll to bottom of page

            if wait_for_data_load(driver):
                flight_data = extract_flight_data(driver, start_date, return_date)
                if flight_data:
                    all_flights.append(flight_data)
            else:
                logging.warning(f"Skipping {start_date} due to data load failure.")

            start_date += timedelta(days=1)

        if all_flights:
            df = pd.DataFrame(all_flights, columns=["Departure Date", "Return Date", "Airline", "Price", "Duration"])
            df.to_excel("skyscanner_cheapest_flights.xlsx", index=False)
            logging.info("Data saved to skyscanner_cheapest_flights.xlsx")

    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logging.error(f"Error while closing WebDriver:", e)

    sys.exit(0)

if __name__ == "__main__":
    main()