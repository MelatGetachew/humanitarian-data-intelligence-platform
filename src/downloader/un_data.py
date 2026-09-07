import requests
import json
import time
import os

def get_unhcr_data(country_code, year, retries=3, delay=5):
    url = "https://api.unhcr.org/population/v1/population/"
    params = {
        "coo": country_code,   # country of origin
        "year": year,
        "limit": 100
    }
    
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params, timeout=15)
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

def save_raw_data(data, country_code, year):
    folder = "data/raw/un"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/{country_code}_{year}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {filename}")

if __name__ == "__main__":
    countries = ["ETH", "KEN", "UGA", "TZA", "SOM", "SSD", "RWA", "BDI", "DJI", "ERI"]
    years = [2023]

    for country in countries:
        for year in years:
            print(f"Fetching displacement data for {country} ({year})...")
            result = get_unhcr_data(country, year)
            if result:
                save_raw_data(result, country, year)
            else:
                print(f"Skipped {country} - {year} (failed after retries)")
            time.sleep(1)