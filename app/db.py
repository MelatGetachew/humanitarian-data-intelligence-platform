import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:eastafrica2024@localhost:5432/humanitarian_data")

COUNTRY_INFO = {
    "ETH": {
        "name": "Ethiopia", "iso2": "et",
        "blurb": "Home to Addis Ababa and one of the oldest continuous civilizations in the world, Ethiopia is the most populous country in East Africa.",
        "bbox": "32.9,3.4,48.0,14.9",
    },
    "KEN": {
        "name": "Kenya", "iso2": "ke",
        "blurb": "A major East African hub centered on Nairobi, known for the Great Rift Valley and its wildlife reserves.",
        "bbox": "33.9,-4.7,41.9,5.0",
    },
    "UGA": {
        "name": "Uganda", "iso2": "ug",
        "blurb": "Landlocked and bordering Lake Victoria, Uganda is often called the 'Pearl of Africa' for its landscape and biodiversity.",
        "bbox": "29.5,-1.5,35.0,4.2",
    },
    "TZA": {
        "name": "Tanzania", "iso2": "tz",
        "blurb": "Home to Mount Kilimanjaro and the Serengeti, Tanzania spans the East African coast down to Lake Tanganyika.",
        "bbox": "29.3,-11.8,40.5,-0.9",
    },
    "SOM": {
        "name": "Somalia", "iso2": "so",
        "blurb": "Located on the Horn of Africa with the continent's longest coastline, Somalia has faced prolonged conflict and displacement.",
        "bbox": "40.9,-1.7,51.4,12.0",
    },
    "SSD": {
        "name": "South Sudan", "iso2": "ss",
        "blurb": "The world's newest country, having gained independence in 2011, South Sudan continues to face significant humanitarian challenges.",
        "bbox": "24.1,3.4,35.9,12.2",
    },
    "RWA": {
        "name": "Rwanda", "iso2": "rw",
        "blurb": "Known as the 'land of a thousand hills,' Rwanda has undergone significant recovery and development since 1994.",
        "bbox": "28.8,-2.9,30.9,-1.0",
    },
    "BDI": {
        "name": "Burundi", "iso2": "bi",
        "blurb": "A small, densely populated nation on Lake Tanganyika in the African Great Lakes region.",
        "bbox": "28.9,-4.5,30.9,-2.3",
    },
    "DJI": {
        "name": "Djibouti", "iso2": "dj",
        "blurb": "Strategically located on the Bab-el-Mandeb strait, Djibouti is a key shipping and logistics hub for the Horn of Africa.",
        "bbox": "41.7,10.9,43.4,12.7",
    },
    "ERI": {
        "name": "Eritrea", "iso2": "er",
        "blurb": "A Red Sea coastal nation that gained independence from Ethiopia in 1993 after a long liberation struggle.",
        "bbox": "36.4,12.3,43.1,18.0",
    },
}

COUNTRY_NAMES = {code: info["name"] for code, info in COUNTRY_INFO.items()}

def get_country_data(code):
    query = text("SELECT * FROM country_indicators WHERE country_code = :code ORDER BY year")
    return pd.read_sql(query, engine, params={"code": code})
def get_overview():
    df = pd.read_sql("SELECT * FROM country_indicators ORDER BY year", engine)
    rows = []
    for code, name in COUNTRY_NAMES.items():
        c = df[df["country_code"] == code]

        def latest(col):
            r = c.dropna(subset=[col])
            return r.iloc[-1][col] if not r.empty else None

        refugees = latest("refugees")
        idps = latest("idps")
        if refugees is None and idps is None:
            displaced = None
        else:
            displaced = (refugees or 0) + (idps or 0)

        rows.append({
            "code": code,
            "name": name,
            "population": latest("population"),
            "life_expectancy": latest("life_expectancy"),
            "school_enrollment": latest("school_enrollment"),
            "displaced": displaced,
        })
    return rows
def get_map_data():
    rows = get_overview()
    for r in rows:
        r["info"] = COUNTRY_INFO[r["code"]]
    return rows