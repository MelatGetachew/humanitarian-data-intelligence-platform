import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:eastafrica2024@localhost:5432/humanitarian_data")

COUNTRY_NAMES = {
    "BDI": "Burundi",
    "DJI": "Djibouti",
    "ERI": "Eritrea",
    "ETH": "Ethiopia",
    "KEN": "Kenya",
    "RWA": "Rwanda",
    "SOM": "Somalia",
    "SSD": "South Sudan",
    "TZA": "Tanzania",
    "UGA": "Uganda",
}

def get_country_data(code):
    query = text("SELECT * FROM country_indicators WHERE country_code = :code ORDER BY year")
    return pd.read_sql(query, engine, params={"code": code})