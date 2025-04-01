import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd


def scrape_kayak_flights(origin, destination, start_date, end_date):
    """
    Scrapes flight data from Kayak for a given origin, destination, and date range.

    Args:
        origin (str): IATA code of the origin airport.
        destination (str): IATA code of the destination airport.
        start_date (datetime): Start date of the search range.
        end_date (datetime): End date of the search range.

    Returns:
        list: A list of dictionaries, where each dictionary contains flight data.
    """

    flight_data = []

    current_departure_date = start_date
    while current_departure_date <= end_date:
        return_date = current_departure_date + timedelta(days=8)

        # Format dates for Kayak URL
        departure_str = current_departure_date.strftime("%Y-%m-%d")
        return_str = return_date.strftime("%Y-%m-%d")

        # Construct Kayak URL
        url = f"https://www.kayak.com/flights/JFK-DPS/2025-04-01/2025-04-09?sort=price_a"

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract flight data (this part needs careful adjustment based on Kayak's HTML structure)
            flight_listings = soup.find_all("div", class_="nrc6")  # Adjust this class name as needed.

            for listing in flight_listings:
                try:
                    price_element = listing.find("span", class_="price-text")  # Adjust this class name as needed.
                    price_text = price_element.text.strip().replace("$", "").replace(",", "") if price_element else None
                    price = float(price_text) if price_text else None

                    airline_element = listing.find("span",
                                                   class_="codeshares-airline-names")  # Adjust this class name as needed.
                    airline = airline_element.text.strip() if airline_element else None

                    duration_element = listing.find("div", class_="stops-text")  # Adjust this class name as needed.
                    duration_text = duration_element.text.strip() if duration_element else None

                    # Parse duration (basic example, may need more robust parsing)
                    if duration_text:
                        hours_match = [int(s) for s in duration_text.split() if s.isdigit()]
                        if hours_match:
                            total_hours = hours_match[0]
                        else:
                            total_hours = 21  # default to over 20.
                    else:
                        total_hours = 21  # default to over 20.
                    if total_hours < 20:
                        flight_data.append({
                            "departure_date": departure_str,
                            "return_date": return_str,
                            "airline": airline,
                            "duration": duration_text,
                            "price_usd": price,
                        })

                except AttributeError as e:
                    print(f"Error extracting data: {e}")
                except ValueError as e:
                    print(f"Error converting price: {e}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL: {e}")

        current_departure_date += timedelta(days=1)

    return flight_data


# Example usage
origin_airport = "JFK"  # New York
destination_airports = "DPS"  # Denpasar bali.
start_date = datetime(2025, 4, 1)
end_date = datetime(2026, 2, 28)

all_results = []
for destination in destination_airports:
    results = scrape_kayak_flights(origin_airport, destination, start_date, end_date)
    all_results.extend(results)

df = pd.DataFrame(all_results)
print(df)

# Save to CSV
df.to_csv("kayak_flight_data.csv", index=False)
