import pandas as pd
from sqlalchemy import create_engine

def load_master_dataset():
    # Read the cleaned, merged CSV
    df = pd.read_csv("data/processed/master_dataset.csv")
    
    # Rename columns to match our database table
    df = df.rename(columns={
        "SP.POP.TOTL": "population",
        "SP.DYN.LE00.IN": "life_expectancy",
        "SE.PRM.ENRR": "school_enrollment"
    })
    
    # Keep only the columns that exist in our table
    columns_needed = [
        "country_code", "year", "population", "life_expectancy",
        "school_enrollment", "refugees", "asylum_seekers", "idps",
        "returned_refugees", "returned_idps"
    ]
    df = df[[col for col in columns_needed if col in df.columns]]
    
    # Connect to PostgreSQL
    # Format: postgresql://username:password@host:port/database_name
    engine = create_engine("postgresql://postgres:eastafrica2024@localhost:5432/humanitarian_data")
    
    # Load into the table, replacing existing data each time this runs
    df.to_sql("country_indicators", engine, if_exists="replace", index=False)
    
    print(f"Loaded {len(df)} rows into country_indicators table")

if __name__ == "__main__":
    load_master_dataset()