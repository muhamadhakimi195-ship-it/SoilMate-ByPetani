from pathlib import Path
import folium
import json
import pandas as pd

project_root = Path(__file__).resolve().parent.parent
output = project_root / "output" / "maps" / "alert_level.html"
geo_json_data = project_root / "data" / "Geo" / "malay.geojson"
csv_data = project_root / "data" / "processed" / "maps_data.csv"


def create_alert_map(selected_date=None):
    features = ["Date", "States", "Alert_level"]
    df = pd.read_csv(csv_data, usecols=features)

    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
    selected_date = pd.Timestamp(selected_date) if selected_date else df["Date"].max()
    df = df[df["Date"] == selected_date]
    df["States"] = df["States"].str.strip().str.lower().replace({
        "melaka": "malacca",
        "pulau pinang": "penang",
    })
    alerts = df.set_index("States")["Alert_level"].to_dict()
    colors = {0: "#27966B", 1: "#E8C547", 2: "#E98B36", 3: "#D94B4B"}

    geojson = json.loads(geo_json_data.read_text(encoding="utf-8"))
    for feature in geojson["features"]:
        state = feature["properties"]["shapeName"].strip().lower()
        level = alerts.get(state)
        feature["properties"]["Alert_measurement"] = int(level) if pd.notna(level) else None

    min_lon, max_lon = 99.3, 119.6
    min_lat, max_lat = 0.5, 7.7
    m = folium.Map(
        location=[4.1, 109.5],
        control_scale=True,
        zoom_start=5,
        min_zoom=5,
        max_zoom=12,
        max_bounds=True,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        max_bounds_viscosity=1.0,
    )
    folium.GeoJson(
            geojson,
            name="Malaysia", 
            zoom_on_click=True,
            style_function=lambda feature: {
            "fillColor": colors.get(feature["properties"]["Alert_measurement"], "#9CA3AF"),
            "fillOpacity": 0.4,
            "color": "black",
            "opacity": 0.8,
            "weight": 0.8,
            "dashArray": "5, 5",
        },
        ).add_to(m)

    return m


if __name__ == "__main__":
    output.parent.mkdir(parents=True, exist_ok=True)
    create_alert_map().save(str(output))
