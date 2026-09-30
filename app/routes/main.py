from flask import Blueprint, render_template, abort, request
import plotly.express as px
from app.db import get_country_data, get_overview, COUNTRY_NAMES

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("home.html", countries=COUNTRY_NAMES)

@main.route("/country/<code>")
def country(code):
    code = code.upper()
    if code not in COUNTRY_NAMES:
        abort(404)

    df = get_country_data(code)

    def latest(column):
        rows = df.dropna(subset=[column])
        return rows.iloc[-1][column] if not rows.empty else None

    stats = {
        "population": latest("population"),
        "life_expectancy": latest("life_expectancy"),
        "school_enrollment": latest("school_enrollment"),
        "idps": latest("idps"),
        "refugees": latest("refugees"),
    }

    charts = []
    chart_specs = [
        ("population", "Population"),
        ("life_expectancy", "Life Expectancy (years)"),
        ("school_enrollment", "Primary School Enrollment (% gross)"),
    ]
    for i, (column, title) in enumerate(chart_specs):
        data = df.dropna(subset=[column])
        fig = px.line(data, x="year", y=column, title=title)
        # Load the Plotly JavaScript once, on the first chart only
        charts.append(fig.to_html(full_html=False, include_plotlyjs="cdn" if i == 0 else False))

    return render_template(
        "country.html",
        code=code,
        name=COUNTRY_NAMES[code],
        stats=stats,
        charts=charts,
    )

@main.route("/countries")
def countries():
    q = request.args.get("q", "").strip().lower()
    sort = request.args.get("sort", "name")

    allowed = {"name", "population", "life_expectancy", "school_enrollment", "displaced"}
    if sort not in allowed:
        sort = "name"

    rows = get_overview()

    if q:
        rows = [r for r in rows if q in r["name"].lower() or q in r["code"].lower()]

    with_data = [r for r in rows if r[sort] is not None]
    without_data = [r for r in rows if r[sort] is None]
    with_data.sort(key=lambda r: r[sort], reverse=(sort != "name"))
    rows = with_data + without_data

    return render_template("countries.html", rows=rows, q=q, sort=sort)