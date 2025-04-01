from playwright.sync_api import sync_playwright
from playwright_stealth import stealth
import time
import random
import pandas as pd
from datetime import datetime, timedelta


def generate_urls():
    base_url = "https://www.kayak.com/flights/JFK-DPS/{}/{}"
    start_date = datetime(2025, 4, 1)
    end_date = datetime(2026, 2, 28)
    urls = []

    while start_date <= end_date:
        return_date = start_date + timedelta(days=8)  # 8-night return
        url = base_url.format(start_date.strftime("%Y-%m-%d"), return_date.strftime("%Y-%m-%d"))
        urls.append(url)
        start_date += timedelta(days=1)  # Move to next day

    return urls


def scrape_kayak(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set to False for debugging
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36")
        page = context.new_page()
        stealth.apply(page)

        time.sleep(random.uniform(3, 7))  # Random delay to avoid detection

        try:
            page.goto(url,
                      wait_until="domcontentloaded",
                      timeout=60000)
            page.wait_for_selector("[data-testid='price-text']", timeout=30000)

            # Extract flight data
            flight_prices = page.locator("[data-testid='price-text']").all_text_contents()
            flight_names = page.locator("[data-testid='airline-name']").all_text_contents()
            durations = page.locator("[data-testid='duration']").all_text_contents()

            # Extract date from URL
            departure_date = url.split("/")[-2]

            # Process data
            flights = []
            for i in range(len(flight_prices)):
                price = flight_prices[i].replace("$", "").replace(",", "").strip()
                duration = durations[i]
                hours = int(duration.split("h")[0]) if "h" in duration else 0

                if hours <= 20:  # Only keep flights under 20 hours
                    flights.append((departure_date, flight_names[i], duration, price))

            # Return the cheapest flight
            if flights:
                flights.sort(key=lambda x: int(x[3]))  # Sort by price
                return flights[0]  # Return only the cheapest flight

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

        finally:
            browser.close()


# Generate all URLs
urls = generate_urls()
results = []

for url in urls:
    print(f"Scraping: {url}")
    flight = scrape_kayak(url)
    if flight:
        results.append(flight)
    else:
        print(f"❌ No valid flight found for {url}")

# Save to Excel
df = pd.DataFrame(results, columns=["Date", "Flight Name", "Duration", "Price (USD)"])
df.to_excel("lowest_price_flights_JFK_DPS.xlsx", index=False)

print("✅ Data saved successfully!")
