from flask import Blueprint, render_template, abort, request, redirect, url_for
import plotly.express as px
import plotly.graph_objects as go
from app.db import get_country_data, get_overview, get_map_data, COUNTRY_NAMES, COUNTRY_INFO
from flask_login import current_user, login_required
from app.models.user import db, Favorite

main = Blueprint("main", __name__)


@main.route("/")
def home():
    rows = get_map_data()

    codes = [r["code"] for r in rows]
    pops = [r["population"] for r in rows]

    hover_text = []
    for r in rows:
        pop = f"{r['population']:,.0f}" if r["population"] is not None else "No data"
        life = f"{r['life_expectancy']:.1f} yrs" if r["life_expectancy"] is not None else "No data"
        disp = f"{r['displaced']:,.0f}" if r["displaced"] is not None else "No data"
        hover_text.append(
            f"<b>{r['name']}</b><br>Population: {pop}<br>Life expectancy: {life}<br>Displaced: {disp}"
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
    fig.update_geos(
        scope="africa",
        fitbounds="locations",
        visible=False,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=420,
    )

    map_html = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        div_id="east-africa-map",
    )

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
        charts.append(fig.to_html(full_html=False, include_plotlyjs="cdn" if i == 0 else False))

    is_favorited = False
    if current_user.is_authenticated:
        is_favorited = Favorite.query.filter_by(user_id=current_user.id, country_code=code).first() is not None

    return render_template(
        "country.html",
        code=code,
        name=COUNTRY_NAMES[code],
        info=COUNTRY_INFO[code],
        stats=stats,
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