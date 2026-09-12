import pandas as pd
from sqlalchemy import create_engine

def get_connection():
    return create_engine("postgresql://postgres:eastafrica2024@localhost:5432/humanitarian_data")

def load_data():
    engine = get_connection()
    df = pd.read_sql("SELECT * FROM country_indicators", engine)
    return df

def population_growth_summary(df):
    """For each country, compare earliest vs latest population to see growth."""
    results = []
    for country in df["country_code"].unique():
        country_df = df[df["country_code"] == country].dropna(subset=["population"])
        if len(country_df) < 2:
            continue
        earliest = country_df.sort_values("year").iloc[0]
        latest = country_df.sort_values("year").iloc[-1]
        growth_pct = ((latest["population"] - earliest["population"]) / earliest["population"]) * 100
        results.append({
            "country_code": country,
            "start_year": int(earliest["year"]),
            "end_year": int(latest["year"]),
            "start_population": int(earliest["population"]),
            "end_population": int(latest["population"]),
            "growth_pct": round(growth_pct, 1)
        })
    return pd.DataFrame(results).sort_values("growth_pct", ascending=False)

def life_expectancy_improvement(df):
    """For each country, how much has life expectancy improved over time?"""
    results = []
    for country in df["country_code"].unique():
        country_df = df[df["country_code"] == country].dropna(subset=["life_expectancy"])
        if len(country_df) < 2:
            continue
        earliest = country_df.sort_values("year").iloc[0]
        latest = country_df.sort_values("year").iloc[-1]
        improvement = latest["life_expectancy"] - earliest["life_expectancy"]
        results.append({
            "country_code": country,
            "start_year": int(earliest["year"]),
            "end_year": int(latest["year"]),
            "start_life_expectancy": round(earliest["life_expectancy"], 1),
            "end_life_expectancy": round(latest["life_expectancy"], 1),
            "improvement_years": round(improvement, 1)
        })
    return pd.DataFrame(results).sort_values("improvement_years", ascending=False)

def displacement_summary(df):
    """Total displacement burden per country (most recent year with data)."""
    df_2023 = df[df["year"] == 2023].copy()
    df_2023["total_displaced"] = df_2023["refugees"].fillna(0) + df_2023["idps"].fillna(0)
    return df_2023[["country_code", "refugees", "idps", "total_displaced"]].sort_values("total_displaced", ascending=False)

if __name__ == "__main__":
    df = load_data()
    
    import os
    os.makedirs("data/reports", exist_ok=True)
    
    pop_growth = population_growth_summary(df)
    pop_growth.to_csv("data/reports/population_growth.csv", index=False)
    
    life_exp = life_expectancy_improvement(df)
    life_exp.to_csv("data/reports/life_expectancy_improvement.csv", index=False)
    
    displacement = displacement_summary(df)
    displacement.to_csv("data/reports/displacement_summary.csv", index=False)
    
    print("Saved 3 reports to data/reports/")