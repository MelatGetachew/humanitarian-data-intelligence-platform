import pandas as pd
import json
import os
import glob

def clean_worldbank_file(filepath):
    with open(filepath, "r") as f:
        raw = json.load(f)
    
    records = raw[1]
    
    rows = []
    for r in records:
        rows.append({
            "country": r["country"]["value"],
            "country_code": r["countryiso3code"],
            "indicator": r["indicator"]["id"],
            "year": r["date"],
            "value": r["value"]
        })
    
    return pd.DataFrame(rows)

def clean_all_worldbank_files():
    raw_folder = "data/raw/worldbank"
    all_files = glob.glob(f"{raw_folder}/*.json")
    
    all_dataframes = []
    for filepath in all_files:
        print(f"Cleaning {filepath}...")
        df = clean_worldbank_file(filepath)
        all_dataframes.append(df)
    
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    before = len(combined_df)
    combined_df = combined_df.drop_duplicates()
    after = len(combined_df)
    print(f"Removed {before - after} duplicate rows")
    
    before = len(combined_df)
    combined_df = combined_df.dropna(subset=["value"])
    after = len(combined_df)
    print(f"Removed {before - after} rows with missing values")
    
    combined_df["year"] = combined_df["year"].astype(int)
    
    return combined_df

if __name__ == "__main__":
    combined_df = clean_all_worldbank_files()
    
    print(f"\nTotal combined rows: {len(combined_df)}")
    print(combined_df.head())
    
    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/worldbank_clean.csv"
    combined_df.to_csv(output_path, index=False)
    print(f"\nSaved cleaned data to {output_path}")