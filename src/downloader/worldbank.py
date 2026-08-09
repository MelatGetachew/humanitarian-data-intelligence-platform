import requests
import json
import time
import os

def get_indicator_data(country_code, indicator_code, retries=3, delay=5):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}"
    params = {"format": "json", "per_page": 1000}
    
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All retries failed.")
                return None

def save_raw_data(data, country_code, indicator_code):
    folder = "data/raw/worldbank"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/{country_code}_{indicator_code}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {filename}")

if __name__ == "__main__":
    countries = ["ETH", "KEN", "NGA"]
    indicators = [
        "SP.POP.TOTL",      # Population, total
        "SP.DYN.LE00.IN",   # Life expectancy at birth
        "SE.PRM.ENRR",      # School enrollment, primary (% gross)
    ]

    for country in countries:
        for indicator in indicators:
            print(f"Fetching {indicator} for {country}...")
            result = get_indicator_data(country, indicator)
            if result:
                save_raw_data(result, country, indicator)
            else:
                print(f"Skipped {country} - {indicator} (failed after retries)")
            time.sleep(1) 