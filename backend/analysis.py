"""Read the four Excel-style graph CSVs without changing their columns or files."""

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


DATA = Path(__file__).resolve().parent.parent / "data" / "processed"
# File, date format, first graph column, row offset, summary column count.
SOURCES = {
    "rain": ("rainfall_graph.csv", "%d-%b-%y", 12, 1, 9),
    "air": ("humidity_graph.csv", "%d/%m/%Y", 12, 1, 10),
    "soil": ("soil_moisture_graph.csv", "%d/%m/%Y", 10, 1, 8),
    "plant": ("plant_stress_graph.csv", "%d/%m/%Y", 11, 0, 8),
}
COLORS = {"Normal": "#27966B", "Getting dry": "#B18A16", "Very dry": "#D94B4B"}
TRACE_COUNTS = {"rain": 2, "air": 3, "soil": 1, "plant": 1}
DAILY_LABELS = {
    "rain": ["Rain daily (mm/day)", "Rain normal daily (mm/day)"],
    "air": ["Air VPD_mean chart (kPa)", "Air VPD_p90 chart (kPa)", "Air VPD_peak chart (kPa)"],
    "soil": ["Root-zone percentile"],
    "plant": ["Plant ESI chart (ratio)"],
}


@lru_cache(maxsize=4)
def read_source(key, modified_at):
    # The mtime cache key refreshes data after an Excel/CSV edit.
    filename, date_format, graph_start, offset, _ = SOURCES[key]
    frame = pd.read_csv(DATA / filename, header=1, dtype=str)
    frame["_date"] = pd.to_datetime(frame.iloc[:, 0], format=date_format, errors="coerce")
    frame["_graph_date"] = pd.to_datetime(frame.iloc[:, graph_start], format=date_format, errors="coerce")
    # Three files have a graph header embedded one row below the summary header.
    # Shift the STATE as well as using the graph's date, including at state boundaries.
    frame["_graph_state"] = frame.iloc[:, 1].shift(offset)
    for column in frame.columns[graph_start + 1:graph_start + 1 + TRACE_COUNTS[key]]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def number(row, position):
    return None if row is None or pd.isna(row.iloc[position]) else float(row.iloc[position])


def display(value, decimals=2):
    return "—" if value is None or pd.isna(value) else f"{value:,.{decimals}f}".rstrip("0").rstrip(".")


def values(series):
    # JSON null keeps genuine missing observations out of the plot.
    return [None if pd.isna(value) else float(value) for value in series]


def metric(label, value, unit=""):
    return {"label": label, "value": display(value), "unit": unit}


def figure(traces, unit, start, end, y_range=None):
    fig = go.Figure(traces)
    fig.update_layout(
        template=None, height=272, margin=dict(l=48, r=14, t=12, b=38),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, Arial, sans-serif", size=12, color="#234235"),
        showlegend=False, hovermode="x unified", dragmode="zoom",
        xaxis=dict(type="date", range=[(start - pd.Timedelta(hours=12)).isoformat(),
                                      (end + pd.Timedelta(hours=12)).isoformat()],
                   tickformat="%d %b", nticks=5, showgrid=False, zeroline=False,
                   linecolor="#DCE5DB", showline=True),
        yaxis=dict(title=dict(text=unit, font=dict(size=11)), gridcolor="#EDF1EB",
                   zeroline=False, nticks=5, range=y_range, automargin=True),
        hoverlabel=dict(bgcolor="#FFFFFF", font=dict(size=12, color="#234235")),
    )
    return fig


def line(x, y, name, color, dash="solid", unit=""):
    mode = "lines+markers" if y.notna().sum() < 3 else "lines"
    return go.Scatter(x=x, y=values(y), name=name, mode=mode, connectgaps=False,
                      marker=dict(size=5, color=color),
                      line=dict(color=color, width=2.5, dash=dash),
                      hovertemplate=f"{name}: %{{y:.2f}} {unit}<extra></extra>")


def view(label, fig, legend):
    return {"label": label, "figure": json.loads(fig.to_json()), "legend": legend}


def legend(label, color, kind="line"):
    return {"label": label, "color": color, "kind": kind}


def rain_panel(row, history, columns, start, end):
    x = history.index.strftime("%Y-%m-%d").tolist()
    actual, usual = history[columns[0]], history[columns[1]]
    accumulated = figure([
        line(x, usual.cumsum(), "Usual", "#8B968F", "dash", "mm"),
        line(x, actual.cumsum(), "Received", "#397CA5", unit="mm"),
    ], "Accumulated mm", start, end)
    accumulated.data[1].fill = "tonexty"
    accumulated.data[1].fillcolor = "rgba(232,197,71,0.16)"
    daily = figure([
        go.Bar(x=x, y=values(actual), name="Daily rain", marker_color="#397CA5",
               hovertemplate="Rain: %{y:.2f} mm<extra></extra>"),
        line(x, usual, "Usual daily rain", "#8B968F", "dash", "mm"),
    ], "mm / day", start, end)
    daily.update_yaxes(rangemode="tozero")
    received, normal = number(row, 4), number(row, 5)
    scale = max(received or 0, normal or 0, 1)
    gap = None if received is None or normal is None else received - normal
    return {
        "title": "Rainfall balance", "question": "Enough rain vs usual?",
        "primary_label": "Rain received · last 14 days", "primary": display(received), "unit": "mm",
        "comparison": f"{display(normal)} mm usual",
        "insight": "No snapshot for this date" if gap is None else f"{display(abs(gap))} mm {'below' if gap < 0 else 'above'} usual",
        "bullet": {"actual": (received or 0) / scale * 100, "target": (normal or 0) / scale * 100} if row is not None else None,
        "stats": [metric("Rain difference · 14d", number(row, 6), "%"),
                  metric("Dry days · last 30d", number(row, 7), "/ 30"), metric("Current dry streak", number(row, 8), "days")],
        "views": [view("Rain gap", accumulated, [legend("Received", "#397CA5"), legend("Usual", "#8B968F", "dash"), legend("Gap", "#E8C547", "area")]),
                  view("Daily rain", daily, [legend("Daily rain", "#397CA5", "bar"), legend("Usual daily rain", "#8B968F", "dash")])],
    }


def air_panel(row, history, columns, start, end):
    x = history.index.strftime("%Y-%m-%d").tolist()
    mean, reference, peak = [history[column] for column in columns]
    difference = peak - reference
    observed = int(difference.notna().sum())
    above = int((difference > 0).sum())
    gap = figure([go.Bar(
        x=x, y=values(difference), name="Dry-air gap",
        marker_color=["#D46E4B" if pd.notna(value) and value > 0 else "#74A594" for value in difference],
        customdata=list(zip(values(peak), values(reference))),
        hovertemplate="Gap: %{y:+.2f} kPa<br>Peak: %{customdata[0]:.2f} kPa<br>Dry-air line: %{customdata[1]:.2f} kPa<extra></extra>",
    )], "Gap from dry-air line · kPa", start, end)
    gap.add_hline(y=0, line_color="#7F8A82", line_width=1)
    levels = figure([line(x, peak, "Afternoon peak", "#CE7751", unit="kPa"),
                     line(x, reference, "Dry-air line", "#8B968F", "dash", "kPa"),
                     line(x, mean, "Daily mean", "#B7C7BE", unit="kPa")], "VPD · kPa", start, end)
    return {
        "title": "Dry-air pressure", "question": "How many dry-air days?",
        "primary_label": "Days above the dry-air line", "primary": str(above) if observed else "—",
        "unit": f"/ {observed} observed", "comparison": "",
        "insight": "Above zero = dry-air line exceeded",
        "stats": [metric("Afternoon VPD", number(row, 4), "kPa"), metric("Dry-air line", number(row, 5), "kPa"),
                  metric("Humidity", number(row, 7), "%")],
        "views": [view("Dry-air days", gap, [legend("Above dry-air line", "#D46E4B", "bar"), legend("Below the line", "#74A594", "bar")]),
                  view("VPD levels", levels, [legend("Afternoon peak", "#CE7751"), legend("Dry-air line", "#8B968F", "dash"), legend("Daily mean", "#B7C7BE")])],
    }


def seven_day_change(series, end):
    previous = end - pd.Timedelta(days=7)
    if previous not in series.index or pd.isna(series.loc[end]) or pd.isna(series.loc[previous]):
        return None
    return float(series.loc[end] - series.loc[previous])


def soil_panel(row, history, columns, start, end):
    x = history.index.strftime("%Y-%m-%d").tolist()
    root = history[columns[0]]
    fig = figure([line(x, root, "Root-zone percentile", "#27966B")], "Percentile", start, end, [0, 100])
    # 20 and 40 are explicitly identified in the soil graph's embedded header.
    fig.add_hrect(y0=0, y1=20, fillcolor="rgba(217,75,75,0.10)", line_width=0, layer="below")
    fig.add_hrect(y0=20, y1=40, fillcolor="rgba(232,197,71,0.15)", line_width=0, layer="below")
    fig.add_hline(y=20, line_color="#D94B4B", line_dash="dot", line_width=1)
    fig.add_hline(y=40, line_color="#9A9773", line_dash="dash", line_width=1)
    change = seven_day_change(root, end)
    return {
        "title": "Water around the roots", "question": "Are roots losing moisture?",
        "primary_label": "Root-zone moisture", "primary": display(number(row, 4)), "unit": "percentile",
        "comparison": "Relative to past years",
        "insight": "7-day comparison unavailable" if change is None else f"{'↑' if change >= 0 else '↓'} {display(abs(change))} percentile points in 7 days",
        "stats": [metric("Root wetness · 5d", number(row, 5), "/ 1"), metric("Topsoil wetness", number(row, 6), "/ 1"),
                  metric("Topsoil change · 3d", number(row, 7), "%")],
        "views": [view("Moisture path", fig, [legend("Root zone", "#27966B"), legend("40 · normal reference", "#9A9773", "dash"),
                                           legend("20 · very dry reference", "#D94B4B", "dash")])],
    }


def plant_panel(row, history, columns, start, end):
    x = history.index.strftime("%Y-%m-%d").tolist()
    esi = history[columns[0]]
    fig = figure([go.Scatter(x=x, y=values(esi), name="Plant ESI", mode="markers", connectgaps=False,
                            marker=dict(color="#287A6C", size=7),
                            hovertemplate="ESI: %{y:.3f}<extra></extra>")], "ESI · raw ratio", start, end)
    change = seven_day_change(esi, end)
    out_of_scale = bool(((esi < 0) | (esi > 1)).any())
    return {
        "title": "Plant response", "question": "Which way is ESI moving?",
        "primary_label": "Latest reported ESI", "primary": display(number(row, 4)), "unit": "ESI",
        "comparison": "No value on selected date" if row is None else f"Reading: {row.iloc[5]}",
        "insight": "7-day comparison unavailable" if change is None else f"{'↑' if change >= 0 else '↓'} {display(abs(change), 3)} ESI in 7 days",
        "warning": "ESI scale needs review" if out_of_scale else "ESI cutoffs not yet validated",
        "stats": [metric("Plotted readings", int(esi.notna().sum()), f"/ {len(history)}"),
                  metric("Clear readings · 30d", number(row, 6), "/ 30"), metric("Cloudy days · 30d", number(row, 7), "/ 30")],
        "views": [view("Observed readings", fig, [legend("Actual observations", "#287A6C", "dot")])],
    }


BUILDERS = {"rain": rain_panel, "air": air_panel, "soil": soil_panel, "plant": plant_panel}


def get_analysis(selected_date, state, days=30):
    end = pd.Timestamp(selected_date)
    start = end - pd.Timedelta(days=days - 1)
    cards = []
    for key, (filename, _, graph_start, _, summary_count) in SOURCES.items():
        path = DATA / filename
        frame = read_source(key, path.stat().st_mtime_ns)
        snapshot = frame[(frame.iloc[:, 1] == state) & (frame["_date"] == end)]
        row = None if snapshot.empty else snapshot.iloc[0]
        columns = frame.columns[graph_start + 1:graph_start + 1 + TRACE_COUNTS[key]].tolist()
        history = frame[(frame["_graph_state"] == state) & frame["_graph_date"].between(start, end)]
        history = history.set_index("_graph_date")[columns].reindex(pd.date_range(start, end))
        card = BUILDERS[key](row, history, columns, start, end)
        card.update({
            "id": key, "status": "No snapshot" if row is None else row.iloc[2],
            "status_color": COLORS.get(None if row is None else row.iloc[2], "#7E8981"),
            "available": int(history[columns[0]].notna().sum()),
            "source": filename,
            "metadata": [] if row is None else [{"label": name, "value": str(value)} for name, value in row.iloc[:summary_count].items()],
            "daily_columns": DAILY_LABELS[key],
            "daily_rows": [{"date": day.strftime("%d %b %Y"), "values": [display(value, 3) for value in data]} for day, data in zip(history.index, history.itertuples(index=False, name=None))],
        })
        cards.append(card)
    return {"cards": cards, "days": days, "period_start": start.strftime("%d %b %Y"), "period_end": end.strftime("%d %b %Y")}
