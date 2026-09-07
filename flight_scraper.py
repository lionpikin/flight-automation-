import requests
import csv
import json
from datetime import datetime

# PUT YOUR APIFY TOKEN HERE
APIFY_TOKEN = "apify_api_l2iSfxruKZ9Hht4WlU1vHMtce0lWfe35g5Lp"

# --- Step 1: Get today's date ---
today = datetime.now().strftime("%Y-%m-%d")
filename = f"today_flights_{today}.csv"

# --- Step 2: Scrape Google Flights via Apify ---
print(f"Scraping flights for {today}...")
flight_actor = "mtnrabi~google-flights-real-time-api"
flight_url = f"https://api.apify.com/v2/acts/{flight_actor}/run-sync-get-dataset-items?token={APIFY_TOKEN}"

# The exact request for your Dad and Aunt (Lagos to LA, Nov 20 - Dec 20, $800 max)
flight_payload = {
    "from_airport": "LOS",
    "to_airport": "LAX",
    "departure_date": "2026-11-20",
    "return_date": "2026-12-20",
    "passengers": [1, 1],
    "max_price": 800,
    "currency": "usd"
}

all_flights = []

try:
    response = requests.post(flight_url, json=flight_payload, timeout=180)
    data = response.json()
    
    if isinstance(data, list):
        print(f"Found {len(data)} flights.")
        for item in data:
            all_flights.append({
                "source": "google_flights",
                "airline": item.get('airline', 'N/A'),
                "departure_time": item.get('departure_time', 'N/A'),
                "arrival_time": item.get('arrival_time', 'N/A'),
                "price": item.get('price', 'N/A'),
                "link": item.get('link', 'N/A'),
                "date": today
            })
    else:
        print(f"Flight error: {data}")
except Exception as e:
    print(f"Flight Error: {e}")

# --- Step 3: Save ---
if all_flights:
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["source", "airline", "departure_time", "arrival_time", "price", "link", "date"])
        writer.writeheader()
        writer.writerows(all_flights)
    print(f"DONE! Saved {len(all_flights)} flights to {filename}")
else:
    print("No flights found. The flights might be over $800.")
