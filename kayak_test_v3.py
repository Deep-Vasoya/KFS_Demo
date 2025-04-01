from playwright.sync_api import sync_playwright
from playwright_stealth import stealth  # Correct import
import time
import random
import pandas as pd

def scrape_kayak(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36"
        )
        page = context.new_page()

        # Apply stealth correctly
        stealth.stealth(page)  # ✅ Corrected usage

        time.sleep(random.uniform(3, 7))

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector(".nrc6", timeout=30000)  # Wait for price elements

            flight_prices = page.locator(".nrc6").all_text_contents()
            flight_names = page.locator(".vmXl").all_text_contents()

            data = list(zip(flight_names, flight_prices))
            return data

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

        finally:
            browser.close()

# List of URLs to scrape
urls = [
    "https://www.kayak.com/flights/JFK-DPS/2025-04-01/2025-04-09",
    "https://www.kayak.com/flights/JFK-DPS/2025-05-01/2025-05-09"
]

results = []

for url in urls:
    print(f"Scraping: {url}")
    flights = scrape_kayak(url)
    if flights:
        results.extend(flights)
    else:
        print(f"❌ Could not extract flight details for {url}")

# Save data to Excel
df = pd.DataFrame(results, columns=["Flight Name", "Price"])
df.to_excel("cheapest_flights_JFK_DPS.xlsx", index=False)

print("✅ Data saved successfully!")
