from flask import Blueprint, jsonify, request
from app.db import get_country_data, get_overview, COUNTRY_NAMES, COUNTRY_INFO
from functools import wraps
from flask import abort as flask_abort

API_KEY = "demo-key-12345"  # in production this would be an environment variable

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if key != API_KEY:
            return jsonify({"error": "Missing or invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated
api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/")
def api_root():
    return jsonify({
        "message": "East Africa Humanitarian Data API",
        "endpoints": {
            "/api/countries": "List all countries with latest key indicators",
            "/api/countries/<code>": "Full historical data for one country (e.g. /api/countries/eth)",
            "/api/health": "Life expectancy by country",
            "/api/displacement": "Displacement totals by country",
        }
    })

@api.route("/countries")
def list_countries():
    rows = get_overview()
    return jsonify(rows)


@api.route("/countries/<code>")
@require_api_key
def country_detail(code):
    code = code.upper()
    if code not in COUNTRY_NAMES:
        return jsonify({"error": "Country not found", "code": code}), 404

    df = get_country_data(code)
    df = df.where(df.notnull(), None)  # convert NaN to JSON-safe null
    records = df.to_dict(orient="records")

    return jsonify({
        "code": code,
        "name": COUNTRY_NAMES[code],
        "info": {
            "iso2": COUNTRY_INFO[code]["iso2"],
            "blurb": COUNTRY_INFO[code]["blurb"],
        },
        "data": records,
    })


@api.route("/health")
def health_indicators():
    rows = get_overview()
    result = [
        {"code": r["code"], "name": r["name"], "life_expectancy": r["life_expectancy"]}
        for r in rows
    ]
    return jsonify(result)


@api.route("/displacement")
def displacement_indicators():
    rows = get_overview()
    result = [
        {"code": r["code"], "name": r["name"], "displaced": r["displaced"]}
        for r in rows
    ]
    return jsonify(result)