# SoilMate / Nasa Petani

An agriculture dashboard for Malaysian states, built with FastAPI, Jinja, pandas,
Folium and Plotly. It displays stored risk assessments, weather, illustrative soil
scenes, maps and historical analysis from local CSV files.

## Run locally (Windows PowerShell)

The current environment uses Python 3.14. Direct dependency versions are pinned;
transitive dependencies are resolved by pip.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000. Run commands from the repository root.

## Configuration

**No `.env` or NASA API key is required by the current application.** It reads
local files and does not load dotenv or make authenticated NASA API requests.
Unused local `.env` and `Nasa-Api-Key.txt` files were removed; both remain ignored if recreated. An `.env.example` is
unnecessary until configuration variables are actually implemented.

The browser uses external fonts, Bootstrap, map libraries and map tiles;
internet access is needed for those resources. Live NASA ingestion and forecasting
are not implemented. Empty analytics placeholders were removed during cleanup.

## Dependencies and tests

`requirements.txt` contains six direct runtime dependencies. Jinja2 and Uvicorn
are explicit because templates and the HTTP server need them. NumPy, Pydantic and
other transitive packages are installed automatically. Streamlit, pydeck, Prophet,
scikit-learn, Earthdata, raster processing and database packages are not used by
the current dashboard and are not installed.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The development requirements add HTTPX for the existing FastAPI TestClient tests.
Offline image preparation tools are separate from the running app; local
experiments and reports go under ignored `output/`. The maintained image optimizer
is `tools/optimize_dashboard_images.py`; install `requirements-tools.txt` only
when using that offline tool. Simulation image notes are in `docs/simulation-images.md`.

## Repository contents

- `backend/`: routes, CSV readers, map generation and chart calculations.
- `dashboard/templates/`, `dashboard/static/`: templates, styles, scripts, icons
  and prepared images. Keep the image manifest and generated image lookup.
- `data/Geo/malay.geojson`: Malaysia boundaries.
- Eight runtime CSVs in `data/processed/`: `header.csv`, `LayerRisk.csv`,
  `weather.csv`, `maps_data.csv`, `rainfall_graph.csv`, `humidity_graph.csv`,
  `soil_moisture_graph.csv` and `plant_stress_graph.csv`.
- `tests/` and `docs/`: tests and documentation.

Runtime CSVs are included so a fresh clone runs without manual data setup. Local
uploads, duplicate state PNG masters, intermediate CSVs, environments, generated
maps, previews and backups are ignored. Original photos stay locally in
`uploads/state-hero`; runtime uses WebP/AVIF images referenced by
`dashboard/static/state-hero/manifest.json`.

Photo credits and license details are in `dashboard/static/state-hero/CREDITS.md`
and the weather templates. Simulation images are AI-generated illustrations.
The Kelantan tourism photo has no explicit reuse license on its source page;
resolve permission or replace it before distributing those assets publicly.
Project code is covered by the [MIT license](LICENSE). Third-party assets retain
their individual license terms and are not relicensed by the project's MIT license.

## First upload to GitHub

Create an **empty** GitHub repository without adding a README, license or
gitignore there. Then run in PowerShell:

```powershell
Set-Location C:\Users\User\Nasa_Petani
git init -b main
git add .
git status --short
git diff --cached --stat
git commit -m "Initial SoilMate dashboard"
git remote add origin https://github.com/YOUR_USERNAME/Nasa_Petani.git
git push -u origin main
```

Replace the remote URL with your own repository URL. Before committing, confirm
that `.env`, `Nasa-Api-Key.txt`, `.venv`, `uploads` and `output` are absent from
the staged list. `.gitignore` does not untrack previously committed files.

See [GitHub's instructions](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github?platform=windows).
