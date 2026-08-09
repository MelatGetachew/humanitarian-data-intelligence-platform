import requests
import json
import time
import os

def get_who_indicator(indicator_code, retries=3, delay=5):
    url = f"https://ghoapi.azureedge.net/api/{indicator_code}"
    
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=15)
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

def save_raw_data(data, indicator_code):
    folder = "data/raw/who"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/{indicator_code}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {filename}")

if __name__ == "__main__":
    indicators = [
        "WHOSIS_000001",  # Life expectancy at birth
        "WHOSIS_000015",  # Under-5 mortality rate (check exact code below)
    ]

    for indicator in indicators:
        print(f"Fetching {indicator}...")
        result = get_who_indicator(indicator)
        if result:
            save_raw_data(result, indicator)
        else:
            print(f"Skipped {indicator} (failed after retries)")
        time.sleep(1)