from flask import Flask, render_template, request
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

app = Flask(__name__)

def setup_driver():
    """Sets up the Chrome WebDriver with retry mechanism."""
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    for _ in range(3):  # Retry up to 3 times
        try:
            return uc.Chrome(options=options)
        except Exception as e:
            print(f"Error setting up driver: {e}. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying
    print("Failed to setup driver after multiple retries.")
    return None

def construct_kayak_url(departure, arrival, start, return_date):
    """Constructs the Kayak URL."""
    return f"https://www.kayak.com/flights/{departure}-{arrival}/{start.strftime('%Y-%m-%d')}/{return_date.strftime('%Y-%m-%d')}?sort=price_a"

def wait_for_page_load(driver):
    """Waits for the page to fully load."""
    try:
        WebDriverWait(driver, 180).until(  # Increased wait time to 180 seconds
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'nrc6')]"))
        )
        return True
    except TimeoutException:
        print("❌ Page did not load in time.")
        return False

def extract_flight_data(driver, start_date, return_date):
    """Extracts flight data from the page with robust error handling."""
    try:
        cheapest_flight = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//div[contains(@class, 'nrc6')])[1]"))
        )

        airline = get_text(cheapest_flight, ".//div[contains(@class, 'c_cgF')]")
        price = get_text(cheapest_flight, ".//div[contains(@class, 'f8F1-price-text')]")
        duration = get_text(cheapest_flight, ".//div[contains(@class, 'vmXl')]")
        departure = driver.execute_script("return arguments[0].querySelector('span.depart-time')?.innerText || 'Unknown';", cheapest_flight)
        arrival = driver.execute_script("return arguments[0].querySelector('span.arrival-time')?.innerText || 'Unknown';", cheapest_flight)
        total_time = get_text(cheapest_flight, ".//div[contains(@class, 'xdW8')]/div[contains(@class, 'vmXl')]")

        print(f"✅ Cheapest Flight - Airline: {airline}, Price: {price}, Duration: {duration}, Departure: {departure}, Arrival: {arrival}, Total Time: {total_time}")
        return [start_date.strftime('%Y-%m-%d'), return_date.strftime('%Y-%m-%d'), airline, price, duration, departure, arrival, total_time]

    except TimeoutException:
        print(f"❌ Timeout: Flight data did not load in time for {start_date}.")
        return None
    except NoSuchElementException as e:
        print(f"❌ Element not found on page for {start_date}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error extracting flight data for {start_date}: {e}")
        return None

def get_text(element, xpath):
    """Helper function to extract text safely."""
    try:
        return element.find_element(By.XPATH, xpath).text.strip()
    except NoSuchElementException:
        return "Unknown"
    except Exception:
        return "Unknown"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        departure_airport = request.form['departure']
        arrival_airport = request.form['arrival']
        start_date_str = f"{request.form['start_year']}-{request.form['start_month']}-{request.form['start_day']}"
        days_between = int(request.form['days_between'])
        total_hours = int(request.form['total_hours'])

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = start_date + timedelta(hours=total_hours)
            all_flights = []
            driver = setup_driver()

            if driver:
                while start_date <= end_date:
                    return_date = start_date + timedelta(days=days_between)
                    url = construct_kayak_url(departure_airport, arrival_airport, start_date, return_date)
                    print(f"Scraping: {url}")
                    driver.get(url)

                    if wait_for_page_load(driver):
                        for _ in range(3):
                            flight_data = extract_flight_data(driver, start_date, return_date)
                            if flight_data:
                                all_flights.append(flight_data)
                                break
                            else:
                                print(f"Retrying data extraction for {start_date}...")
                                time.sleep(5)
                    else:
                        print(f"❌ Skipping {start_date} due to page load failure.")
                    start_date += timedelta(days=1)

                driver.quit()

                if all_flights:
                    return render_template('results.html', flights=all_flights)
                else:
                    return "No flights found."
            else:
                return "Failed to setup driver."
        except ValueError:
            return "Invalid date format."

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)