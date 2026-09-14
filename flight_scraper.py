import requests
import json
import re
import csv
from datetime import datetime

DEPARTURE_DATE = "2026-11-25"
RETURN_DATE = "2026-12-24"
ORIGIN = "LOS"
DESTINATION = "LAX"

all_results = []

# 1. SKYSCANNER
print("1. SCRAPING SKYSCANNER...")
try:
    url = "https://skyscanner-flights4.p.rapidapi.com/api/v1/roundtrip"
    payload = {"adults": 1, "cabin": "economy", "currency": "USD", "date": DEPARTURE_DATE,
               "destination": DESTINATION, "locale": "en-US", "market": "US", "origin": ORIGIN,
               "return_date": RETURN_DATE, "max_price": 2500}
    headers = {"x-rapidapi-key": "25ba7ed681msha2ad94ba1150594p1ccdd9jsnc853fc9e1ae9",
               "x-rapidapi-host": "skyscanner-flights4.p.rapidapi.com", "Content-Type": "application/json"}
    r = requests.post(url, json=payload, headers=headers, timeout=60).json()
    flights = sorted([f for f in r.get('results', []) if len(f.get('legs', [])) >= 2 and f['legs'][0].get('stops') == 1 and f['legs'][1].get('stops') == 1], key=lambda x: x.get('price_raw', 999999))
    for f in flights[:3]:
        all_results.append({
            "platform": "Skyscanner", "price": f.get('price_raw', 999999),
            "price_display": f.get('price', 'N/A'), "airline": ", ".join(f.get('carriers', [])),
            "out_depart": f['legs'][0].get('dep', 'N/A'), "out_arrive": f['legs'][0].get('arr', 'N/A'),
            "ret_depart": f['legs'][1].get('dep', 'N/A'), "ret_arrive": f['legs'][1].get('arr', 'N/A'),
            "split": "No",
            "link": f"https://www.skyscanner.com/transport/flights/los/lax/261125/261224/?adults=1&cabinclass=economy"
        })
    print(f"   Skyscanner: {len(flights)} flights found.")
except Exception as e:
    print(f"   Skyscanner Error: {e}")

# 2. BOOKING.COM
print("2. SCRAPING BOOKING.COM...")
try:
    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
    qs = {"adults": "1", "currency_code": "USD", "stops": "1", "departDate": DEPARTURE_DATE,
          "fromId": "LOS.AIRPORT", "toId": "LAX.AIRPORT", "returnDate": RETURN_DATE,
          "pageNo": "1", "sort": "CHEAPEST"}
    headers = {"x-rapidapi-key": "25ba7ed681msha2ad94ba1150594p1ccdd9jsnc853fc9e1ae9",
               "x-rapidapi-host": "booking-com15.p.rapidapi.com"}
    r = requests.get(url, headers=headers, params=qs, timeout=60).json()
    flights = r['data']['flightOffers']
    for f in flights[:3]:
        try:
            price = f['priceBreakdown']['total']['units']
            out = f['segments'][0]
            ret = f['segments'][1] if len(f['segments']) > 1 else {}
            airline = out['legs'][0]['carriersData'][0]['name']
            all_results.append({
                "platform": "Booking.com", "price": price, "price_display": f"${price}",
                "airline": airline, "out_depart": out.get('departureTime', 'N/A'),
                "out_arrive": out.get('arrivalTime', 'N/A'),
                "ret_depart": ret.get('departureTime', 'N/A'),
                "ret_arrive": ret.get('arrivalTime', 'N/A'), "split": "No",
                "link": f"https://flights.booking.com/flights/LOS.AIRPORT-LAX.AIRPORT/?type=ROUNDTRIP&adults=1&cabinClass=ECONOMY&depart={DEPARTURE_DATE}&return={RETURN_DATE}"
            })
        except: pass
    print(f"   Booking.com: {len(flights)} flights found.")
except Exception as e:
    print(f"   Booking Error: {e}")

# 3. EXPEDIA
print("3. SCRAPING EXPEDIA...")
try:
    url = "https://expedia-data1.p.rapidapi.com/flights/search"
    payload = {"cabin_class": "COACH", "currency": "USD", "filters": {"sort": "PRICE", "stops": 1},
               "include_available_filters": False,
               "legs": [{"date": {"day": 25, "month": 11, "year": 2026}, "destination": "Los Angeles (LAX - All Airports)", "origin": "Lagos (LOS - All Airports)"},
                        {"date": {"day": 24, "month": 12, "year": 2026}, "destination": "Lagos (LOS - All Airports)", "origin": "Los Angeles (LAX - All Airports)"}],
               "page_size": 5, "travelers": {"adults": 1}, "trip_type": "ROUND_TRIP"}
    headers = {"x-rapidapi-key": "25ba7ed681msha2ad94ba1150594p1ccdd9jsnc853fc9e1ae9",
               "x-rapidapi-host": "expedia-data1.p.rapidapi.com", "Content-Type": "application/json"}
    r = requests.post(url, json=payload, headers=headers, timeout=60).json()
    flights = sorted(r.get('results', []), key=lambda x: x.get('price', {}).get('amount', 999999))
    for f in flights[:3]:
        legs = f.get('legs', [])
        if len(legs) < 2: continue
        out_segs = legs[0].get('segments', [])
        airline = out_segs[0].get('airline', 'Unknown') if out_segs else 'Unknown'
        out_id = legs[0].get('origin_destination_id', '')
        ret_id = legs[1].get('origin_destination_id', '')
        out_times = re.findall(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})', out_id)
        ret_times = re.findall(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})', ret_id)
        booking_link = f.get('book_on_expedia') or f.get('url', 'https://www.expedia.com/Flights-Search')
        all_results.append({
            "platform": "Expedia", "price": f.get('price', {}).get('amount', 999999),
            "price_display": f.get('price', {}).get('display', 'N/A'), "airline": airline,
            "out_depart": out_times[0] if out_times else 'N/A',
            "out_arrive": out_times[-1] if out_times else 'N/A',
            "ret_depart": ret_times[0] if ret_times else 'N/A',
            "ret_arrive": ret_times[-1] if ret_times else 'N/A', "split": "No",
            "link": booking_link
        })
    print(f"   Expedia: {len(flights)} flights found.")
except Exception as e:
    print(f"   Expedia Error: {e}")

# 4. KAYAK
print("4. SCRAPING KAYAK...")
try:
    url = "https://kayak-flights1.p.rapidapi.com/api/kayak/flights/round-trip"
    qs = {"page": "1", "locale": "en-US", "children": "0", "infants_in_seat": "0", "adults": "1",
          "include_price_prediction": "true", "include_display_metadata": "false", "cabin": "economy",
          "currency": "USD", "sort": "price", "infants_on_lap": "0",
          "return_date": RETURN_DATE, "destination": DESTINATION, "origin": ORIGIN, "departure_date": DEPARTURE_DATE}
    headers = {"x-rapidapi-key": "25ba7ed681msha2ad94ba1150594p1ccdd9jsnc853fc9e1ae9",
               "x-rapidapi-host": "kayak-flights1.p.rapidapi.com"}
    r = requests.get(url, headers=headers, params=qs, timeout=60).json()
    flights = [f for f in r.get('flights', []) if f.get('type') == 'core']
    def kp(f):
        try: return f['bookingOptions'][0]['displayPrice']['price']
        except: return 999999
    flights = sorted(flights, key=kp)
    for f in flights[:3]:
        booking = f['bookingOptions'][0]
        price = booking['displayPrice']['price']
        booking_url = booking.get('bookingUrl', {}).get('url', '')
        full_link = f"https://www.kayak.com{booking_url}" if booking_url else "https://www.kayak.com"
        splits = booking.get('splitBookingOptions', [])
        if splits:
            all_legs = []
            for s in splits:
                for leg in s.get('scheduleData', []):
                    all_legs.append(leg)
            airline = " + ".join(set(l.get('airline', 'Unknown') for l in all_legs))
            out_dep = all_legs[0].get('departure', 'N/A') if all_legs else 'N/A'
            ret_dep = all_legs[-1].get('departure', 'N/A') if all_legs else 'N/A'
            split_flag = "YES"
        else:
            airline = "Unknown"
            out_dep = ret_dep = 'N/A'
            split_flag = "No"
        all_results.append({
            "platform": "Kayak", "price": price,
            "price_display": booking['displayPrice']['localizedPrice'], "airline": airline,
            "out_depart": out_dep, "out_arrive": 'N/A',
            "ret_depart": ret_dep, "ret_arrive": 'N/A', "split": split_flag,
            "link": full_link
        })
    print(f"   Kayak: {len(flights)} flights found.")
except Exception as e:
    print(f"   Kayak Error: {e}")

# --- SAVE RESULTS TO CSV ---
all_results = sorted(all_results, key=lambda x: x['price'])
today = datetime.now().strftime("%Y-%m-%d")
filename = f"today_flights_{today}.csv"

with open(filename, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["platform", "price", "price_display", "airline", "out_depart", "out_arrive", "ret_depart", "ret_arrive", "split", "link"])
    writer.writeheader()
    writer.writerows(all_results)

print(f"\nDONE! Saved {len(all_results)} flights to {filename}")
if all_results:
    print(f"CHEAPEST: {all_results[0]['price_display']} on {all_results[0]['platform']}")
