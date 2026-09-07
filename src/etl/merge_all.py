import pandas as pd
import os

def load_and_pivot(filepath, value_name):
    df = pd.read_csv(filepath)
    pivoted = df.pivot_table(
        index=["country_code", "year"],
        columns="indicator",
        values="value",
        aggfunc="first"
    ).reset_index()
    return pivoted

def merge_all_sources():
    # Pivot World Bank and WHO from long to wide format
    worldbank = load_and_pivot("data/processed/worldbank_clean.csv", "value")
    who = load_and_pivot("data/processed/who_clean.csv", "value")
    
    # UN data is already wide, just load it
    un = pd.read_csv("data/processed/un_clean.csv")
    un = un.drop(columns=["country"])  # avoid duplicate country name column
    
    print(f"World Bank shape: {worldbank.shape}")
    print(f"WHO shape: {who.shape}")
    print(f"UN shape: {un.shape}")
    
    # Merge World Bank + WHO on country_code and year
    merged = pd.merge(worldbank, who, on=["country_code", "year"], how="outer")
    
    # Merge in UN data
    merged = pd.merge(merged, un, on=["country_code", "year"], how="outer")
    
    return merged

if __name__ == "__main__":
    merged_df = merge_all_sources()
    
    print(f"\nFull merged shape (all countries): {merged_df.shape}")
    
    # East Africa focus countries
    focus_countries = ["ETH", "KEN", "UGA", "TZA", "SOM", "SSD", "RWA", "BDI", "DJI", "ERI"]
    filtered_df = merged_df[merged_df["country_code"].isin(focus_countries)]
    
    print(f"Filtered shape (East Africa only): {filtered_df.shape}")
    print(filtered_df.head(10))
    
    output_path = "data/processed/master_dataset.csv"
    filtered_df.to_csv(output_path, index=False)
    print(f"\nSaved filtered master dataset to {output_path}")