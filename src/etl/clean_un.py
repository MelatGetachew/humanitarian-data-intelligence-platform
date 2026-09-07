import pandas as pd
import json
import os
import glob

def clean_un_file(filepath):
    with open(filepath, "r") as f:
        raw = json.load(f)
    
    records = raw["items"]
    
    if not records:
        print(f"  No data found in {filepath}")
        return pd.DataFrame()  # empty DataFrame, but won't break concat
    
    rows = []
    for r in records:
        rows.append({
            "country_code": r["coo_iso"],
            "country": r["coo_name"],
            "year": r["year"],
            "refugees": r["refugees"],
            "asylum_seekers": r["asylum_seekers"],
            "idps": r["idps"],
            "returned_refugees": r["returned_refugees"],
            "returned_idps": r["returned_idps"]
        })
    
    return pd.DataFrame(rows)

def clean_all_un_files():
    raw_folder = "data/raw/un"
    all_files = glob.glob(f"{raw_folder}/*.json")
    
    all_dataframes = []
    for filepath in all_files:
        print(f"Cleaning {filepath}...")
        df = clean_un_file(filepath)
        all_dataframes.append(df)
    
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    before = len(combined_df)
    combined_df = combined_df.drop_duplicates()
    after = len(combined_df)
    print(f"Removed {before - after} duplicate rows")
    
    return combined_df

if __name__ == "__main__":
    combined_df = clean_all_un_files()
    
    print(f"\nTotal combined rows: {len(combined_df)}")
    print(combined_df)
    
    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/un_clean.csv"
    combined_df.to_csv(output_path, index=False)
    print(f"\nSaved cleaned data to {output_path}")