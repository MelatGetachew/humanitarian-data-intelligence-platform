import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine

def load_data():
    engine = create_engine("postgresql://postgres:eastafrica2024@localhost:5432/humanitarian_data")
    df = pd.read_sql("SELECT * FROM country_indicators", engine)
    return df

df = load_data()
countries = sorted(df["country_code"].unique())

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("East Africa Humanitarian Data Dashboard"),
    
    html.Label("Select a country:"),
    dcc.Dropdown(
        id="country-dropdown",
        options=[{"label": c, "value": c} for c in countries],
        value="ETH"
    ),
    
    dcc.Graph(id="population-chart"),
    dcc.Graph(id="life-expectancy-chart"),
    dcc.Graph(id="education-chart"),
    dcc.Graph(id="displacement-chart"),
])

@app.callback(
    Output("population-chart", "figure"),
    Input("country-dropdown", "value")
)
def update_population_chart(selected_country):
    filtered = df[df["country_code"] == selected_country].dropna(subset=["population"])
    fig = px.line(filtered, x="year", y="population", title=f"Population: {selected_country}")
    return fig

@app.callback(
    Output("life-expectancy-chart", "figure"),
    Input("country-dropdown", "value")
)
def update_life_expectancy_chart(selected_country):
    filtered = df[df["country_code"] == selected_country].dropna(subset=["life_expectancy"])
    fig = px.line(filtered, x="year", y="life_expectancy", title=f"Life Expectancy: {selected_country}")
    return fig

@app.callback(
    Output("education-chart", "figure"),
    Input("country-dropdown", "value")
)
def update_education_chart(selected_country):
    filtered = df[df["country_code"] == selected_country].dropna(subset=["school_enrollment"])
    fig = px.line(filtered, x="year", y="school_enrollment", title=f"School Enrollment (%): {selected_country}")
    return fig

@app.callback(
    Output("displacement-chart", "figure"),
    Input("country-dropdown", "value")
)
def update_displacement_chart(selected_country):
    filtered = df[df["country_code"] == selected_country].dropna(subset=["refugees", "idps"], how="all")
    filtered = filtered.melt(
        id_vars=["year"],
        value_vars=["refugees", "idps"],
        var_name="type",
        value_name="count"
    )
    fig = px.bar(filtered, x="year", y="count", color="type", barmode="group",
                 title=f"Displacement: {selected_country}")
    return fig

if __name__ == "__main__":
    app.run(debug=True)