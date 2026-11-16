from pathlib import Path
from datetime import date, timedelta
import json
from backend.analysis import get_analysis
import pandas as pd
from backend.alert_map import create_alert_map, csv_data
from backend.rain_map import create_rain_map
from backend.humid_map import create_humid_map
from backend.soil_map import create_soil_map
from backend.plants_map import create_plants_map
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

Project_Root = Path(__file__).resolve().parent.parent
Dashboard = Project_Root / "dashboard"

# Mount static files
app.mount("/static", StaticFiles(directory=Dashboard / "static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory=Dashboard / "templates")
hero_manifest = Dashboard / "static" / "state-hero" / "manifest.json"


def get_state_hero(slug):
    # Pick up refreshed photo assets without requiring an application restart.
    if not hero_manifest.exists():
        return None
    return json.loads(hero_manifest.read_text(encoding="utf-8")).get(slug)


templates.env.globals["get_state_hero"] = get_state_hero


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


layer_csv = Project_Root / "data" / "processed" / "LayerRisk.csv"
weather_csv = Project_Root / "data" / "processed" / "weather.csv"
header_csv = Project_Root / "data" / "processed" / "header.csv"


def get_agriculture_risk(selected_date, state):
    columns = ["Date", "States ", "Alert_level", "Alert_name", "Advice", "Trend arrow",
               "Trend", "Plant now?", "soil_check", "soil_pass", "rain_check",
               "rain_pass", "warn_check", "warn_pass"]
    df = pd.read_csv(header_csv, usecols=columns)
    dates = pd.to_datetime(df["Date"], format="%d/%m/%Y")
    rows = df[(dates == pd.Timestamp(selected_date)) & (df["States "] == state)]
    if rows.empty:
        return None
    row = rows.iloc[0].fillna("").to_dict()
    row["icon"] = {"Normal": "sprout", "Watch": "eye", "Warning": "triangle-alert",
                   "Flash drought": "sun"}.get(row["Alert_name"], "circle-help")
    row["trend_icon"] = {"better": "trending-down", "same": "arrow-right",
                         "worse": "trending-up"}.get(row["Trend arrow"], "circle-help")
    row["date_label"] = pd.Timestamp(selected_date).strftime("%d %b %Y")
    return row


def get_weather(selected_date, state):
    df = pd.read_csv(weather_csv)
    dates = pd.to_datetime(df["Date"], format="%d/%m/%Y")
    rows = df[(dates == pd.Timestamp(selected_date)) & (df["States"] == state)]
    return rows.iloc[0].to_dict() if not rows.empty else None


def get_risk_layers(selected_date, state):
    layers = [
        ("Rainfall deficit", "4_rain_def", "4_rain_stats", "4_rain_perc", "%"),
        ("Air dryness", "4_airVDA", "4_air_stats", "4_air_perc", "kPa"),
        ("Soil moisture", "4_air_percentile", "4_soil_stats", "4_soil_perc", "percentile"),
        ("Plant stress", "4_plantESI", "4_plant_stats", "4_plant_bar", "ESI"),
    ]
    columns = ["date", "states"] + [column for layer in layers for column in layer[1:4]]
    df = pd.read_csv(layer_csv, usecols=columns)
    dates = pd.to_datetime(df["date"], format="%d-%b-%y")
    rows = df[(dates == pd.Timestamp(selected_date)) & (df["states"] == state)]
    row = rows.iloc[0] if not rows.empty else {}
    colors = {"Normal": "#27966B", "Getting dry": "#E8C547", "Very dry": "#D94B4B"}
    result = []
    for title, value_column, status_column, bar_column, unit in layers:
        value = row.get(value_column)
        status = row.get(status_column)
        percent = row.get(bar_column)
        result.append({
            "title": title,
            "value": f"{float(value):g}" if pd.notna(value) else "—",
            "unit": unit if pd.notna(value) else "",
            "status": status if pd.notna(status) else "No data",
            "percent": float(percent) if pd.notna(percent) else None,
            "color": colors.get(status, "#9CA3AF"),
        })
    return result


def get_simulation(selected_date, state):
    layers = [
        ("Rainfall deficit", "rain_deficit", "rain_stat", "Sim_rain_stats", "%"),
        ("Air dryness", "Sim_air_VPD", "Sim_air_status", "Sim_air_say", "kPa"),
        ("Soil moisture", "Sim_soil", "Sim_soil_status", "Sim_soil_say", "percentile"),
        ("Plant stress", "Sim_plant_ESI", "Sim_plant_status", "Sim_plant_say", "ESI"),
    ]
    columns = ["date", "states"] + [column for layer in layers for column in layer[1:4]]
    df = pd.read_csv(layer_csv, usecols=columns)
    dates = pd.to_datetime(df["date"], format="%d-%b-%y")
    rows = df[(dates == pd.Timestamp(selected_date)) & (df["states"] == state)]
    if rows.empty:
        return None
    row = rows.iloc[0]
    colors = {"Normal": "#27966B", "Getting dry": "#E8C547", "Very dry": "#D94B4B"}
    result = []
    for title, value_column, status_column, say_column, unit in layers:
        result.append({
            "title": title,
            "value": f"{row[value_column]:g}",
            "unit": unit,
            "status": row[status_column],
            "say": row[say_column],
            "color": colors.get(row[status_column], "#9CA3AF"),
        })
    # Temporary image bands only; risk statuses still come directly from the CSV.
    soil = row["Sim_soil"]
    scene = "dry" if soil < 25 else "normal" if soil < 50 else "damp" if soil < 75 else "wet"
    labels = {"dry": "Dry soil", "normal": "Normal soil", "damp": "Slightly wet soil", "wet": "Wet soil"}
    image_name = "simulation-soil-wet-v2.webp" if scene == "wet" else f"simulation-soil-{scene}.webp"
    return {"layers": result, "image": image_name, "image_label": labels[scene], "scene": scene}


def get_page_context(selected_date=None, state=None):
    dates = pd.read_csv(csv_data, usecols=["Date"])["Date"]
    dates = pd.to_datetime(dates, format="%d/%m/%Y")
    states = pd.read_csv(layer_csv, usecols=["states"])["states"].dropna().unique().tolist()
    return {
        "selected_date": (selected_date or dates.max().date()).isoformat(),
        "date_label": pd.Timestamp(selected_date or dates.max()).strftime("%d %b %Y"),
        "min_date": dates.min().strftime("%Y-%m-%d"),
        "max_date": dates.max().strftime("%Y-%m-%d"),
        "risk_states": states,
        "selected_state": state or states[0],
    }


@app.get("/", response_class=HTMLResponse, name="home")
def home(request: Request, selected_date: date | None = Query(None, alias="date"), state: str | None = None):
    context = get_page_context(selected_date, state)
    selected_date = context["selected_date"]
    state = context["selected_state"]
    context.update({
        "active_page": "overview",
        "agriculture_risk": get_agriculture_risk(selected_date, state),
        "risk_layers": get_risk_layers(selected_date, state),
        "weather": get_weather(selected_date, state),
        "simulation": get_simulation(selected_date, state),
        "simulation_date": pd.Timestamp(selected_date).strftime("%d %b %Y"),
    })
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )


@app.get("/agriculture-risk", response_class=HTMLResponse)
def agriculture_risk(request: Request, state: str, selected_date: date = Query(alias="date")):
    return templates.TemplateResponse(
        request=request,
        name="agriculture_risk.html",
        context={"agriculture_risk": get_agriculture_risk(selected_date, state),
                 "selected_state": state, "selected_date": selected_date.isoformat()},
    )


@app.get("/risk-layers", response_class=HTMLResponse)
def risk_layers(request: Request, state: str, selected_date: date = Query(alias="date")):
    return templates.TemplateResponse(
        request=request,
        name="risk_layers.html",
        context={"risk_layers": get_risk_layers(selected_date, state)},
    )


@app.get("/weather", response_class=HTMLResponse)
def weather(request: Request, state: str, selected_date: date = Query(alias="date")):
    return templates.TemplateResponse(
        request=request,
        name="weather_card.html",
        context={
            "weather": get_weather(selected_date, state),
            "selected_date": selected_date.isoformat(),
            "selected_state": state,
        },
    )


@app.get("/simulation", response_class=HTMLResponse)
def simulation(request: Request, state: str, selected_date: date = Query(alias="date"), weeks: int = 0):
    simulation_date = selected_date - timedelta(weeks=weeks)
    return templates.TemplateResponse(
        request=request,
        name="simulation.html",
        context={
            "simulation": get_simulation(simulation_date, state),
            "simulation_date": simulation_date.strftime("%d %b %Y"),
            "selected_state": state,
        },
    )


@app.get("/maps/alert", response_class=HTMLResponse)
def alert_map(selected_date: date | None = Query(None, alias="date")):
    return create_alert_map(selected_date).get_root().render()

@app.get("/maps/rain", response_class=HTMLResponse)
def rain_map(selected_date: date | None = Query(None, alias="date")):
    return create_rain_map(selected_date).get_root().render()

@app.get("/maps/humid", response_class=HTMLResponse)
def humid_map(selected_date: date | None = Query(None, alias="date")):
    return create_humid_map(selected_date).get_root().render()

@app.get("/maps/soil", response_class=HTMLResponse)
def soil_map(selected_date: date | None = Query(None, alias="date")):
    return create_soil_map(selected_date).get_root().render()

@app.get("/maps/plants", response_class=HTMLResponse)
def plants_map(selected_date: date | None = Query(None, alias="date")):
    return create_plants_map(selected_date).get_root().render()

@app.get("/analysis", response_class=HTMLResponse, name="analysis")
def analysis(request: Request, selected_date: date | None = Query(None, alias="date"), state: str | None = None, days: int = Query(30, ge=14, le=90)):
    context = get_page_context(selected_date, state)
    context.update(get_analysis(context["selected_date"], context["selected_state"], days))
    context["active_page"] = "analysis"
    return templates.TemplateResponse(
        request=request,
        name="analysis.html",
        context=context,
    )
