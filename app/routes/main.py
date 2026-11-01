from flask import Blueprint, render_template, abort, request, redirect, url_for
import plotly.express as px
import plotly.graph_objects as go
from app.db import (
    get_country_data, get_overview, get_map_data, summarize,
    INDICATOR_META, COUNTRY_NAMES, COUNTRY_INFO,
)
from flask_login import current_user, login_required
from app.models.user import db, Favorite

main = Blueprint("main", __name__)


def hover_line(label, value, year, fmt):
    if value is None:
        return f"{label}: Data not available"
    return f"{label} ({year}): {fmt.format(value)}"


@main.route("/")
def home():
    rows = get_map_data()

    codes = [r["code"] for r in rows]
    pops = [r["population"] for r in rows]

    hover_text = []
    for r in rows:
        hover_text.append(
            f"<b>{r['name']}</b><br>"
            + hover_line("Population", r["population"], r["population_year"], "{:,.0f}") + "<br>"
            + hover_line("Life expectancy", r["life_expectancy"], r["life_expectancy_year"], "{:.1f} years") + "<br>"
            + hover_line("Total displaced", r["displaced"], r["displaced_year"], "{:,.0f}")
        )

    fig = go.Figure(go.Choropleth(
        locations=codes,
        z=pops,
        locationmode="ISO-3",
        text=hover_text,
        hovertemplate="%{text}<extra></extra>",
        customdata=codes,
        colorscale="Teal",
        marker_line_color="white",
        colorbar_title="Population",
    ))
    fig.update_geos(scope="africa", fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

    map_html = fig.to_html(full_html=False, include_plotlyjs="cdn", div_id="east-africa-map")

    favorite_codes = set()
    if current_user.is_authenticated:
        favorite_codes = {f.country_code for f in Favorite.query.filter_by(user_id=current_user.id).all()}

    return render_template(
        "home.html",
        countries=COUNTRY_INFO,
        rows=rows,
        map_html=map_html,
        favorite_codes=favorite_codes,
    )


@main.route("/country/<code>")
def country(code):
    code = code.upper()
    if code not in COUNTRY_NAMES:
        abort(404)

    df = get_country_data(code)
    stats = summarize(df)

    def fmt_or_na(key):
        v = stats[key]["value"]
        return INDICATOR_META[key]["fmt"].format(v) if v is not None else "data not available"

    cards = []
    for key in ["population", "life_expectancy", "school_enrollment", "displaced"]:
        meta = INDICATOR_META[key]
        item = stats[key]
        card = {
            "label": meta["label"],
            "value": meta["fmt"].format(item["value"]) if item["value"] is not None else None,
            "year": item["year"],
            "source": meta["source"],
            "detail": None,
        }
        if key == "displaced" and item["value"] is not None:
            card["detail"] = f"IDPs: {fmt_or_na('idps')} | Refugees: {fmt_or_na('refugees')}"
        cards.append(card)

    charts = []
    chart_specs = [
        ("population", "Population"),
        ("life_expectancy", "Life expectancy at birth (years)"),
        ("school_enrollment", "Primary school gross enrolment rate (%)"),
    ]
    for i, (column, title) in enumerate(chart_specs):
        data = df.dropna(subset=[column])
        fig = px.line(data, x="year", y=column, title=title, markers=True)
        fig.update_traces(line_color="#1c5d7a", line_width=3, marker_size=6, marker_color="#0d1b2a")
        fig.update_layout(
            title_font_size=16,
            title_font_color="#1a2332",
            font_family="Inter, Arial, sans-serif",
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=40, r=20, t=50, b=40),
            xaxis=dict(showgrid=False, title=None),
            yaxis=dict(showgrid=True, gridcolor="#eef0f2", title=None),
        )
        years = (
            f"{int(data['year'].min())} to {int(data['year'].max())}"
            if not data.empty else "Data not available"
        )
        charts.append({
            "html": fig.to_html(full_html=False, include_plotlyjs="cdn" if i == 0 else False),
            "source": INDICATOR_META[column]["source"],
            "years": years,
        })

    is_favorited = False
    if current_user.is_authenticated:
        is_favorited = Favorite.query.filter_by(user_id=current_user.id, country_code=code).first() is not None

    return render_template(
        "country.html",
        code=code,
        name=COUNTRY_NAMES[code],
        info=COUNTRY_INFO[code],
        cards=cards,
        charts=charts,
        is_favorited=is_favorited,
    )


@main.route("/favorite/<code>", methods=["POST"])
@login_required
def add_favorite(code):
    code = code.upper()
    if code in COUNTRY_NAMES:
        exists = Favorite.query.filter_by(user_id=current_user.id, country_code=code).first()
        if not exists:
            db.session.add(Favorite(user_id=current_user.id, country_code=code))
            db.session.commit()
    return redirect(request.referrer or url_for("main.home"))


@main.route("/unfavorite/<code>", methods=["POST"])
@login_required
def remove_favorite(code):
    code = code.upper()
    fav = Favorite.query.filter_by(user_id=current_user.id, country_code=code).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
    return redirect(request.referrer or url_for("main.home"))


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