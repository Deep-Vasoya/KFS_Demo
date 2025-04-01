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

def construct_skyscanner_url(departure, arrival, start, return_date):
    """Constructs the Skyscanner URL."""
    return f"https://www.skyscanner.net/transport/flights/{departure.lower()}/{arrival.lower()}/{start.strftime('%y%m%d')}/{return_date.strftime('%y%m%d')}/?adultsv2=2&cabinclass=economy&childrenv2=&inboundaltsenabled=false&outboundaltsenabled=false&preferdirects=true&rtn=1"

def construct_kayak_url(departure, arrival, start, return_date):
    """Constructs the Kayak URL."""
    return f"https://www.kayak.com/flights/{departure.upper()}-{arrival.upper()}/{start.strftime('%Y-%m-%d')}/{return_date.strftime('%Y-%m-%d')}?sort=price_a"

def scroll_to_bottom(driver):
    """Scrolls to the bottom of the page."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)  # Wait for the page to load after scrolling

def wait_for_skyscanner_data_load(driver):
    """Waits for the Skyscanner data to fully load."""
    try:
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'FlightsTicket_container')]"))
        )
        return True
    except TimeoutException:
        logging.error("Skyscanner data did not load in time.")
        return False

def extract_skyscanner_flight_data(driver, start_date, return_date):
    """Extracts flight data from Skyscanner."""
    try:
        cheapest_flight = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "(//div[contains(@class, 'FlightsTicket_container')])[1]"))
        )
        if cheapest_flight:
            airline_element = WebDriverWait(cheapest_flight, 20).until(
                EC.presence_of_element_located((By.XPATH, ".//span[contains(@class, 'provider-name')]"))
            )
            airline = airline_element.text.strip() if airline_element and airline_element.is_displayed() else "Unknown"

            price_element = WebDriverWait(cheapest_flight, 20).until(
                EC.presence_of_element_located((By.XPATH, ".//span[contains(@class, 'price')]"))
            )
            price = price_element.text.strip() if price_element and price_element.is_displayed() else "Unknown"

            duration_element = WebDriverWait(cheapest_flight, 20).until(
                EC.presence_of_element_located((By.XPATH, ".//span[contains(@class, 'duration')]"))
            )
            duration = duration_element.text.strip() if duration_element and duration_element.is_displayed() else "Unknown"

            return ["Skyscanner", start_date.strftime('%Y-%m-%d'), return_date.strftime('%Y-%m-%d'), airline, price, duration]
        else:
            logging.warning("Skyscanner flight element NOT found.")
            return None

    except TimeoutException:
        logging.error(f"Timeout: Skyscanner data did not load in time for {start_date}.")
        return None
    except NoSuchElementException as e:
        logging.error(f"Element not found on Skyscanner for {start_date}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error extracting Skyscanner data for {start_date}: {e}")
        return None

def wait_for_kayak_data_load(driver):
    """Waits for the Kayak data to fully load."""
    try:
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-resultid]"))
        )
        return True
    except TimeoutException:
        logging.error("Kayak data did not load in time.")
        return False

def extract_kayak_flight_data(driver, start_date, return_date):
    """Extracts flight data from Kayak."""
    try:
        cheapest_flight = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "(//div[@data-resultid])[1]"))
        )
        if cheapest_flight:
            airline_element = WebDriverWait(cheapest_flight, 20).until(
                EC.presence_of_element_located((By.XPATH, ".//span[@data-code]"))
            )
            airline = airline_element.text.strip() if airline_element and airline_element.is_displayed() else "Unknown"

            price_element = WebDriverWait(cheapest_flight, 20).until(
                EC.presence_of_element_located((By.XPATH, ".//span[@data-price]"))
            )
            price = price_element.text.strip() if price_element and price_element.is_displayed() else "Unknown"

            duration_element = WebDriverWait(cheapest_flight, 20).until(
                EC.presence_of_element_located((By.XPATH, ".//div[@data-duration]"))
            )
            duration = duration_element.text.strip() if duration_element and duration_element.is_displayed() else "Unknown"

            return ["Kayak", start_date.strftime('%Y-%m-%d'), return_date.strftime('%Y-%m-%d'), airline, price, duration]
        else:
            logging.warning("Kayak flight element NOT found.")
            return None

    except TimeoutException:
        logging.error(f"Timeout: Kayak data did not load in time for {start_date}.")
        return None
    except NoSuchElementException as e:
        logging.error(f"Element not found on Kayak for {start_date}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error extracting Kayak data for {start_date}: {e}")
        return None

def main():
    """Main function to orchestrate the scraping with retry logic."""
    departure_airport = "LOND"
    arrival_airport = "DBV"
    start_date = datetime(2025, 4, 1)
    end_date = datetime(2025, 4, 10)
    all_flights = []
    driver = setup_driver()

    if driver is None:
        return

    try:
        while start_date <= end_date:
            return_date = start_date + timedelta(days=8)

            # Skyscanner scraping
            skyscanner_url = construct_skyscanner_url(departure_airport, arrival_airport, start_date, return_date)
            logging.info(f"Scraping Skyscanner: {skyscanner_url}")
            driver.get(skyscanner_url)
            scroll_to_bottom(driver)
            if wait_for_skyscanner_data_load(driver):
                skyscanner_data = extract_skyscanner_flight_data(driver, start_date, return_date)
                if skyscanner_data:
                    all_flights.append(skyscanner_data)

            # Kayak scraping
            kayak_url = construct_kayak_url(departure_airport, arrival_airport, start_date, return_date)
            logging.info(f"Scraping Kayak: {kayak_url}")
            driver.get(kayak_url)
            scroll_to_bottom(driver)
            if wait_for_kayak_data_load(driver):
                kayak_data = extract_kayak_flight_data(driver, start_date, return_date)
                if kayak_data:
                    all_flights.append(kayak_data)

            start_date += timedelta(days=1)

        if all_flights:
            df = pd.DataFrame(all_flights, columns=["Source", "Departure Date", "Return Date", "Airline", "Price", "Duration"])
            df.to_excel("flight_data.xlsx", index=False)
            logging.info("Data saved to flight_data.xlsx")

    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logging.error(f"Error while closing WebDriver:", e)

    sys.exit(0)

if __name__ == "__main__":
    main()