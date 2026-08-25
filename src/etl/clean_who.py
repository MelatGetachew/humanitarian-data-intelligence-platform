import pandas as pd
import json
import os
import glob

def clean_who_file(filepath):
    with open(filepath, "r") as f:
        raw = json.load(f)
    
    records = raw["value"]  # WHO nests the data under a "value" key
    
    rows = []
    for r in records:
        rows.append({
            "country_code": r["SpatialDim"],
            "indicator": r["IndicatorCode"],
            "year": r["TimeDim"],
            "sex": r["Dim1"],
            "value": r["NumericValue"]
        })
    
    return pd.DataFrame(rows)

def clean_all_who_files():
    raw_folder = "data/raw/who"
    all_files = glob.glob(f"{raw_folder}/*.json")
    
    all_dataframes = []
    for filepath in all_files:
        print(f"Cleaning {filepath}...")
        df = clean_who_file(filepath)
        all_dataframes.append(df)
    
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Keep only "both sexes" rows, so we don't triple-count
    before = len(combined_df)
    combined_df = combined_df[combined_df["sex"] == "SEX_BTSX"]
    after = len(combined_df)
    print(f"Filtered to 'both sexes' only: kept {after} of {before} rows")
    
    combined_df = combined_df.drop(columns=["sex"])
    
    before = len(combined_df)
    combined_df = combined_df.drop_duplicates()
    after = len(combined_df)
    print(f"Removed {before - after} duplicate rows")
    
    before = len(combined_df)
    combined_df = combined_df.dropna(subset=["value"])
    after = len(combined_df)
    print(f"Removed {before - after} rows with missing values")
    
    return combined_df

if __name__ == "__main__":
    combined_df = clean_all_who_files()
    
    print(f"\nTotal combined rows: {len(combined_df)}")
    print(combined_df.head())
    
    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/who_clean.csv"
    combined_df.to_csv(output_path, index=False)
    print(f"\nSaved cleaned data to {output_path}")