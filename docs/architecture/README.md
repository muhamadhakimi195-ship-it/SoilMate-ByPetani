# SoilMate / Nasa Petani — System architecture

Reviewed from the local project on 15 November 2026. The diagrams retain the original planned architecture; subsequent repository cleanup removed the empty analytics/models placeholders and temporary QA exports. The current setup and file list are documented in the root README.

## Open the deliverables

- **soilmate-system-architecture.svg** — editable vector diagram with hover descriptions.
- **soilmate-system-architecture.png** — high-resolution image of the same diagram.
- **soilmate-architecture-interactive.html** — self-contained explorer; open in a browser. Click components, focus current/planned work, trace a request, zoom, or search all tools. No installation or internet is needed for this explorer.
- **architecture-data.json** — editable component and tool inventory.
- **build_architecture.py** — generator for SVG, HTML and JSON; Python standard library only. Run `python docs/architecture/build_architecture.py` from the project root. PNG is rendered offline from the SVG using Windows drawing libraries. Run render_svg.ps1 to regenerate it.

## What is implemented

The server is FastAPI with Jinja2 templates, static assets and GZip middleware. pandas reads local CSV files. Overview serves weather, supplied risk statuses and a historical soil scene. Folium joins map categories to Malaysia state boundaries and generates HTML maps. Leaflet displays them in an iframe. Analysis reads four daily-history CSVs, builds Plotly figures and embeds their JSON in a server-rendered page. The browser uses a local Plotly.js Basic bundle. The Analysis cache is in memory and uses file modification times to refresh parsed files.

The map routes use the selected date and all state boundaries. The selected state controls cards and Analysis; it does not filter the map. Current Simulation subtracts weeks from the chosen date and displays stored values and soil imagery; it does not predict future conditions. Chart periods are 14, 30 or 90 days, while rain summary totals remain 14-day totals. Daily gaps and supplied statuses are preserved.

## What is planned or unverified

The original empty ingestion/cleaning/forecasting placeholders and empty `models/` folder were removed during cleanup. NASA POWER, GPM IMERG, SMAP L4 and ESI source labels occur in the supplied dataset; they do not establish a working live integration or verified upstream lineage. The dashed pipeline is a proposed design, not implemented behavior. Its product selection, coverage, units and status rules need validation. The ESI scale and status cutoffs need domain review, as noted in `docs/analysis.md`.

`requirements.txt` now contains the six direct runtime dependencies used by the FastAPI/Jinja dashboard, pinned to verified versions. `requirements-dev.txt` adds HTTPX for the existing tests. The former starter list included unused Streamlit, pydeck, forecasting and satellite-processing packages; those are no longer installed. SQLite, Parquet and Dask remain optional/planned; no database is currently connected. No production hosting, authentication, background scheduler, automated refresh, model inference, or message-notification service is demonstrated in the inspected project.

The local intermediate CSVs `data_petani.csv` and `data_processed.csv` are not read by the current dashboard and are excluded from Git. `header.csv` is a runtime input used by the agriculture risk panel and is included. Their existence is not evidence of an automated preparation pipeline. Saved standalone map exports were removed; optional map-script exports now go to ignored `output/maps/`, while map routes generate their own HTML from CSV and GeoJSON. The application loads Bootstrap and Inter from external providers; Folium map output can use external map tiles and browser libraries. The explorer itself has no external dependencies.

## Source evidence

- `backend/main.py` — HTTP routes, template rendering, weather/risk/scene readers, static files and compression.
- `backend/analysis.py` and `docs/analysis.md` — history layouts, calculations, cache, plot periods and ESI notes.
- `backend/*_map.py` — live map generation from CSV and GeoJSON.
- `dashboard/templates/` and `dashboard/static/` — dashboard, controls, browser charts and soil imagery.
- `data/processed/` and `data/Geo/` — local data inputs.
- `requirements.txt` — current runtime dependencies; planned pipeline components remain documented in the diagram.
- `tests/test_analysis.py` — maintained backend regression tests; temporary browser QA tools were removed.

No credentials or private environment values are included. The diagram describes source structure and behavior; it is not a production deployment audit.
