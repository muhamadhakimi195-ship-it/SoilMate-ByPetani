"""Build the project architecture from the repository review (15 Nov 2026)."""
from pathlib import Path
from html import escape
import json

OUT = Path(__file__).resolve().parent
NODES = {}

def node(key, title, status, purpose, inputs, outputs, tools, files, notes=''):
    NODES[key] = dict(title=title, status=status, purpose=purpose, inputs=inputs,
                      outputs=outputs, tools=tools, files=files, notes=notes)

node('sources', 'NASA data sources', 'Planned',
     'Bring satellite and weather measurements into SoilMate. These product names appear in the supplied data, but the project does not yet download them.',
     ['NASA POWER: weather and atmospheric fields', 'GPM IMERG: rainfall', 'SMAP L4: soil moisture', 'ECOSTRESS ESI: plant water stress'],
     ['Future raw measurements for the data pipeline'], ['earthaccess', 'httpx'],
     ['data/processed/data_processed.csv'],
     'Product names are recorded in CSV freshness fields and project notes. Live integration, product versions and coverage are not verified. Keep credentials on the server; no credentials are included here.')
node('ingest', 'Import measurements', 'Planned',
     'Fetch selected products and keep the original downloads. The script is currently empty.',
     ['Selected location, time range and NASA products'], ['Proposed raw files and source dates'],
     ['earthaccess', 'httpx', 'xarray', 'netCDF4', 'h5py'], ['analytics/data_ingestion.py'],
     'No scheduled job, downloader, raw-data folder or live refresh is implemented. HDF4 and other product-specific formats may require extra readers.')
node('clean', 'Prepare and check data', 'Planned',
     'Proposed step: clean dates, match locations, join measurements, and prepare the files used by the app.',
     ['Future raw weather and satellite data', 'Malaysia state boundaries'],
     ['Proposed state/date tables', 'Checked metrics and map values'],
     ['pandas', 'numpy', 'geopandas', 'rasterio', 'rioxarray', 'xarray'],
     ['analytics/data_cleaning.py'],
     'The script is empty. No automated lineage from NASA products to the existing CSVs is demonstrated. Validate units, cloud gaps and risk rules before generating statuses.')
node('forecast', 'Forecast future risk', 'Planned',
     'An optional future forecasting branch. It is separate from the current Simulation panel.',
     ['Proposed cleaned time-series data'], ['Future forecast values and evaluation results'],
     ['prophet', 'scikit-learn'], ['analytics/forecasting_model.py', 'models/'],
     'The forecasting script is empty and models/ has no model artifacts. No current route runs a model or returns predictions.')
node('snapshots', 'Weather and risk files', 'Current',
     'Local CSV files supply the weather card, four risk cards and the soil scene.',
     ['weather.csv: temperature, condition, humidity, rain, wind', 'LayerRisk.csv: supplied risk values, statuses and scene data'],
     ['Rows matching the requested state and date'], ['pandas', 'pathlib'],
     ['data/processed/weather.csv', 'data/processed/LayerRisk.csv'],
     'These are supplied local datasets. The app reads reported statuses rather than computing new drought classifications. Current code does not prove their upstream NASA lineage.')
node('geodata', 'Map data and boundaries', 'Current',
     'Combine state-level risk categories with Malaysia state shapes.',
     ['maps_data.csv: alert, rain, humidity, soil and plant categories', 'malay.geojson: state boundaries'],
     ['Map categories joined to state shapes for a selected date'], ['pandas', 'json', 'pathlib'],
     ['data/processed/maps_data.csv', 'data/Geo/malay.geojson'],
     'The map uses the selected date and shows all states. State names are normalised, including Melaka/Malacca and Pulau Pinang/Penang.')
node('history', 'Daily history files', 'Current',
     'Four CSVs hold summary rows and daily chart observations.',
     ['rainfall_graph.csv', 'humidity_graph.csv', 'soil_moisture_graph.csv', 'plant_stress_graph.csv'],
     ['Selected-date summary', 'Daily history for the chart window'], ['pandas'],
     ['data/processed/rainfall_graph.csv', 'data/processed/humidity_graph.csv', 'data/processed/soil_moisture_graph.csv', 'data/processed/plant_stress_graph.csv'],
     'The reader handles the extra header row and row offsets in these files. Missing days stay as gaps; values and reported statuses are preserved.')
node('server', 'FastAPI and page rendering', 'Current',
     'Receive browser requests, read matching data and render pages or HTML fragments using Jinja templates.',
     ['State and date query values', 'Optional weeks value for the soil scene', 'Local weather and risk CSV rows'],
     ['GET /: Overview page', 'GET /risk-layers: risk cards', 'GET /weather: weather card', 'GET /simulation: historical soil scene'],
     ['FastAPI', 'Jinja2', 'pandas', 'GZipMiddleware', 'StaticFiles'],
     ['backend/main.py', 'dashboard/templates/'],
     'The app is a server-rendered FastAPI application. Uvicorn is the declared ASGI runner. /simulation moves backwards from the chosen date; it is not a future forecast.')
node('mapengine', 'Build interactive maps', 'Current',
     'Folium builds a Leaflet map for the selected date and colours the state shapes using supplied categories.',
     ['maps_data.csv', 'malay.geojson', 'Date query value'],
     ['GET /maps/alert', 'GET /maps/rain', 'GET /maps/humid', 'GET /maps/soil', 'GET /maps/plants'],
     ['Folium', 'pandas', 'Leaflet'],
     ['backend/alert_map.py', 'backend/rain_map.py', 'backend/humid_map.py', 'backend/soil_map.py', 'backend/plants_map.py'],
     'The routes generate map HTML on request. The HTML files in dashboard/maps/ are standalone saved map outputs, not the live route data source. Folium defaults can load map tiles and browser assets from external providers.')
node('analysis', 'Prepare chart data', 'Current',
     'Read the four history files, match the state and date, and build Plotly chart specifications.',
     ['State and date query values', 'Chart window: 14, 30 or 90 days', 'Four daily history files'],
     ['GET /analysis: summaries, chart JSON and daily-data tables'],
     ['pandas', 'Plotly Python', 'functools.lru_cache', 'json'],
     ['backend/analysis.py'],
     'The in-memory cache refreshes when a source file changes. Rain summary totals always cover 14 days, even when the plot shows 30 or 90 days. ESI scale and status cutoffs still need domain review.')
node('overview', 'Overview dashboard', 'Current',
     'Help a grower see the chosen state and date at a glance.',
     ['Rendered page and weather/risk/scene fragments'],
     ['Weather card', 'Four risk cards: rain, air, soil, plants', 'Historical soil scene and captions'],
     ['HTML', 'CSS', 'JavaScript', 'Bootstrap', 'Fetch API'],
     ['dashboard/templates/index.html', 'dashboard/templates/weather_card.html', 'dashboard/templates/risk_layers.html', 'dashboard/templates/simulation.html', 'dashboard/static/dashboard.js'],
     'Simulation shows a soil image band from stored soil values. Week controls select earlier dates. The motion button only changes the visual animation.')
node('mapui', 'Five map layers', 'Current',
     'Explore Malaysia by switching between five state-coloured maps.',
     ['Folium-generated map HTML in an iframe', 'Selected date and layer'],
     ['Alert, rain, air dryness, soil and plant views', 'Pan, zoom and click-to-zoom on state shapes'],
     ['Leaflet', 'Folium HTML', 'JavaScript', 'Browser iframe'],
     ['dashboard/templates/index.html', 'dashboard/static/dashboard.js'],
     'Changing the date or layer reloads the iframe. Selecting a state changes the weather, risk and scene cards; it does not currently filter the map to that one state. The source column named Humidity is displayed as the air-dryness map layer.')
node('charts', 'Monitoring and Analysis', 'Current',
     'Show trends and the underlying observations in simple charts.',
     ['Plotly chart JSON and summary values from /analysis'],
     ['Rainfall balance, dry-air pressure, root-zone moisture and plant response', '14 / 30 / 90-day windows', 'Chart view switches, zoom reset and daily-data dialogs'],
     ['Plotly.js Basic (local)', 'JavaScript', 'HTML dialog', 'CSS'],
     ['dashboard/templates/analysis.html', 'dashboard/static/analysis.js', 'dashboard/static/analysis.css', 'dashboard/static/vendor/plotly-basic-4.3.0.min.js'],
     'Desktop supports drag-to-zoom. Touch devices keep page scrolling and tap tooltips. Charts preserve missing observations and show a note about ESI interpretation.')
node('browser', 'Grower in a web browser', 'Current',
     'Choose a Malaysian state and a date, then open Overview or Monitoring and Analysis.',
     ['State, date, chart period and map-layer choices'],
     ['HTTP requests to FastAPI', 'Visible cards, maps, charts and daily-data tables'],
     ['Web browser', 'JavaScript', 'Fetch API', 'CSS'],
     ['dashboard/templates/page_controls.html', 'dashboard/static/controls.js', 'dashboard/templates/base.html'],
     'Pages share state/date controls. Overview updates fragments with fetch; Analysis uses page requests. No login, database, production hosting setup or background scheduler is demonstrated in the inspected source.')

# All declared Python dependencies plus the tools actually used in the app.
TOOLS = [
 ('FastAPI','Current','Python web application and routes'),
 ('Jinja2','Current','Server-side page and fragment templates'),
 ('pandas','Current','Read CSVs, filter rows and prepare daily series'),
 ('plotly','Current','Python chart specifications'),
 ('folium','Current','Build map HTML from state boundaries'),
 ('Plotly.js Basic','Current','Local browser charts; the checked-in filename is plotly-basic-4.3.0.min.js'),
 ('Leaflet','Current','Browser map engine generated by Folium'),
 ('HTML / CSS / JavaScript','Current','Dashboard pages, layout, controls and interactions'),
 ('Bootstrap','Current','CSS loaded by the base template; generated map HTML also includes Bootstrap assets'),
 ('Google Fonts / Inter','Current','Font stylesheet loaded by the base template'),
 ('Fetch API / iframe','Current','Refresh Overview sections and display map HTML'),
 ('GZipMiddleware / StaticFiles','Current','Compress responses and serve local assets'),
 ('functools.lru_cache','Current','Keep parsed Analysis files in memory until file modification times change'),
 ('unittest','Current','Backend Analysis tests in tests/test_analysis.py'),
 ('Playwright / Chrome','Current','Existing browser QA script in output/qa/check_analysis_ui.py'),
 ('uvicorn[standard]','Declared','ASGI server to run FastAPI; no production service configuration is provided'),
 ('pydantic','Declared','FastAPI validation dependency; no custom application data models found'),
 ('pydantic-settings','Planned','Environment configuration; no application use found'),
 ('earthaccess','Planned','Access NASA Earthdata products'),
 ('httpx','Planned','Call remote data APIs'),
 ('geopandas','Planned','Prepare and join geographic data'),
 ('rasterio','Planned','Read and process raster grids'),
 ('rioxarray','Planned','Geospatial raster operations with xarray'),
 ('numpy','Planned','Numerical calculations in the future pipeline'),
 ('xarray','Planned','Work with multidimensional satellite and weather data'),
 ('netCDF4','Planned','Read NetCDF products'),
 ('h5py','Planned','Read HDF5 products'),
 ('prophet','Planned','Time-series forecasting'),
 ('scikit-learn','Planned','Model evaluation and other future ML utilities'),
 ('pyarrow','Planned','Parquet storage support'),
 ('streamlit','Alternative','Starter manifest option; the current dashboard uses FastAPI and Jinja'),
 ('streamlit-folium','Alternative','Only needed if a Streamlit dashboard is adopted'),
 ('pydeck','Alternative','Alternative map rendering; no current use found'),
 ('SQLite / sqlite3','Optional','Mentioned in the starter manifest; no current database use found'),
 ('dask[array]','Optional','Commented-out dependency for lazy or chunked xarray processing'),
 ('jQuery / Awesome Markers / Font Awesome','Generated assets','Included in saved Folium map HTML; not the main dashboard framework'),
]

C = {'ink':'#18372f','muted':'#5e7169','green':'#187755','blue':'#276ea0','purple':'#7456a6','amber':'#9b6b22'}
parts=[]
def add(s): parts.append(s)
def text(x,y,t,size=18,fill=None,weight=400,**attrs):
    at=' '.join(f'{k.replace("_","-")}="{v}"' for k,v in attrs.items())
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill or C["ink"]}" font-weight="{weight}" {at}>{escape(t)}</text>')
def rect(x,y,w,h,fill,stroke='none',r=18,**attrs):
    at=' '.join(f'{k.replace("_","-")}="{v}"' for k,v in attrs.items())
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" {at}/>')

ICONS = {
 'satellite':'<path d="m9 9 6 6m-9-1 4 4m4-12 4 4M3 7l4-4 4 4-4 4zm10 10 4-4 4 4-4 4zM4 15a5 5 0 0 1 5 5m-6-1h2"/>',
 'download':'<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
 'filter':'<path d="M4 5h16l-6 7v6l-4 3v-9z"/><path d="m18 16 2 2 3-4"/>',
 'trend':'<path d="M3 20h18M4 16l6-6 4 3 7-9m-6 0h6v6"/>',
 'file':'<path d="M6 3h8l4 4v14H6zM14 3v5h4M9 12h6m-6 4h6"/>',
 'map':'<path d="m3 5 6-2 6 3 6-2v15l-6 2-6-3-6 2zm6-2v15m6-12v15"/>',
 'history':'<path d="M5 7a9 9 0 1 1-1 9M3 3v6h6m3-3v6l4 2"/>',
 'server':'<rect x="3" y="3" width="18" height="7" rx="2"/><rect x="3" y="14" width="18" height="7" rx="2"/><path d="M7 6h1m-1 11h1m4-11h5m-5 11h5"/>',
 'chart':'<path d="M3 3v18h18M7 16v-5m5 5V7m5 9V4"/>',
 'dashboard':'<rect x="3" y="3" width="7" height="8" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="3" y="15" width="7" height="6" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/>',
 'browser':'<rect x="2" y="3" width="20" height="18" rx="3"/><path d="M2 8h20M6 5.5h1m3 0h1M8 13l-3 2 3 2m8-4 3 2-3 2"/>',
 'leaf':'<path d="M20 3C7 2 2 8 5 15s15 7 15-12ZM5 21 16 9m-7 6v-4m4 0h4"/>',
}
def icon(x,y,name,color,size=30):
    add(f'<g transform="translate({x} {y}) scale({size/24})" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</g>')
def card(key,x,y,w,h,color,ic,lines,tags):
    d=NODES[key]; status=d['status']; planned=status=='Planned'
    add(f'<g class="node {status.lower()}" id="n-{key}" data-key="{key}" tabindex="0" role="button" aria-label="{escape(d["title"])}. {status}. Open details.">')
    add(f'<title>{escape(d["title"]+": "+d["purpose"])}</title>')
    rect(x,y,w,h,'#ffffff', '#c8c3b6' if planned else '#d9e4dd',16,stroke_dasharray='6 5' if planned else 'none', **{'class':'card-bg'})
    rect(x+16,y+18,46,46,{'#9b6b22':'#faf1df','#276ea0':'#e9f3fa','#187755':'#e8f4ee','#7456a6':'#f0ecf9'}.get(color,'#eef3ee'),r=13)
    icon(x+24,y+26,ic,color)
    text(x+76,y+39,d['title'],23,color,650)
    text(x+76,y+61,'PLANNED' if planned else 'IN THE CURRENT APP',11.5,C['muted'],600,letter_spacing=1.2)
    for i,line in enumerate(lines): text(x+20,y+94+i*26,line,18)
    text(x+20,y+h-19,tags,14.5,C['muted'],500)
    add('</g>')
def arrow(d,color='#648579',planned=False,label=None,lx=None,ly=None):
    add(f'<path class="edge {"planned" if planned else "current"}" d="{d}" fill="none" stroke="{color}" stroke-width="2.2" marker-end="url(#{"arrow-plan" if planned else "arrow"})" {"stroke-dasharray=\"7 6\"" if planned else ""}/>')
    if label: text(lx,ly,label,13.5,color,500,text_anchor='middle')

add('<svg xmlns="http://www.w3.org/2000/svg" width="1840" height="1500" viewBox="0 0 1840 1500" role="img" aria-labelledby="diagram-title diagram-desc">')
add('<title id="diagram-title">SoilMate | Nasa Petani system architecture</title><desc id="diagram-desc">Current local CSV data flows through FastAPI into a browser dashboard with Folium maps and Plotly charts. A separate dashed lane shows planned NASA import, data preparation and forecasting. Open the accompanying HTML file for filters, click details, a request walkthrough and the full tool inventory.</desc>')
add('<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="m0 0 8 4-8 4z" fill="#648579"/></marker><marker id="arrow-plan" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="m0 0 8 4-8 4z" fill="#9b6b22"/></marker></defs>')
add('<style>text{font-family:Segoe UI,Arial,sans-serif}.node{cursor:pointer;outline:none}.node:hover .card-bg,.node:focus .card-bg{stroke:#18372f;stroke-width:3}.node,.edge{transition:opacity .15s}.node.dim,.edge.dim{opacity:.14}.node.active .card-bg{stroke:#18372f;stroke-width:4}@media(prefers-reduced-motion:reduce){.node,.edge{transition:none}}</style>')
rect(0,0,1840,1500,'#f6f8f4',r=0)
rect(48,42,56,56,'#183f32',r=17); icon(61,55,'leaf','#ffffff',30)
text(122,66,'SOILMATE  /  NASA PETANI',15,C['green'],650,letter_spacing=2)
text(122,108,'System architecture',40,C['ink'],700)
text(50,149,'From environmental data to a clear view of rain, air, soil and plant conditions.',21,C['muted'])
rect(1410,48,380,74,'#ffffff','#dbe4dd',15)
text(1430,77,'Code-based architecture',19,C['ink'],650)
text(1430,102,'Reviewed 15 Nov 2026  ·  Current + planned',15,C['muted'])

rect(48,183,1744,320,'#f5f0e6','#e3d8bf',22)
text(72,218,'01  FUTURE DATA PIPELINE',16,C['amber'],700,letter_spacing=1.7)
text(1770,218,'Dashed boxes and arrows = planned; no live NASA feed yet',16,C['amber'],500,text_anchor='end')
card('sources',72,244,390,211,C['amber'],'satellite',['POWER weather · GPM IMERG rain','SMAP L4 soil · ECOSTRESS ESI'], 'Named in supplied data; download not built')
card('ingest',506,244,370,211,C['amber'],'download',['Download selected measurements','Keep raw files and source dates'], 'earthaccess · httpx · xarray · NetCDF / HDF5')
card('clean',920,244,398,211,C['amber'],'filter',['Match dates and state boundaries','Check units, gaps and risk rules'], 'pandas · NumPy · geospatial tools')
card('forecast',1362,244,406,211,C['amber'],'trend',['Optional future model branch','No forecast is used by the app'], 'Prophet · scikit-learn · no trained model')
arrow('M462 351H499',C['amber'],True)
arrow('M876 351H913',C['amber'],True)
arrow('M1318 351H1355',C['amber'],True)
arrow('M1119 455V479H306V570',C['amber'],True)
rect(328,463,270,29,'#f5f0e6',r=5); text(341,484,'Proposed prepared CSV output',15,C['amber'],500)

text(50,548,'02  CURRENT APPLICATION',16,C['green'],700,letter_spacing=1.7)
text(1790,548,'Solid arrows = local data read and rendered into the browser',16,C['muted'],500,text_anchor='end')
for x,w,fill,stroke in [(48,520,'#eaf2f7','#d4e2ec'),(660,520,'#eaf3ed','#d1e3d7'),(1272,520,'#f0edf7','#e0d9ed')]:
    rect(x,577,w,658,fill,stroke,22)
icon(70,598,'file',C['blue'],25); text(109,620,'Stored data',26,C['blue'],700)
icon(682,598,'server',C['green'],25); text(721,620,'Python application',26,C['green'],700)
icon(1294,598,'browser',C['purple'],25); text(1333,620,'Browser dashboard',26,C['purple'],700)
card('snapshots',70,646,476,169,C['blue'],'file',['Weather values and risk statuses','Rows selected by state + date'], 'weather.csv · LayerRisk.csv')
card('server',682,646,476,169,C['green'],'server',['Serve pages, cards and soil scenes','Return HTML using Jinja templates'], 'FastAPI · Jinja2 · pandas · GZip')
card('overview',1294,646,476,169,C['purple'],'dashboard',['Weather + four risk cards','Soil scene from historical values'], 'HTML · CSS · JavaScript · Bootstrap')
card('geodata',70,840,476,169,C['blue'],'map',['Five risk categories by state','Malaysia state boundary shapes'], 'maps_data.csv · malay.geojson')
card('mapengine',682,840,476,169,C['green'],'map',['Join state values to boundaries','Generate five map endpoints'], 'Folium · pandas · GeoJSON')
card('mapui',1294,840,476,169,C['purple'],'map',['Alert · rain · air · soil · plants','Pan, zoom and switch map layers'], 'Leaflet map HTML inside an iframe')
card('history',70,1034,476,169,C['blue'],'history',['Rain · air · soil · plant history','Daily observations + summaries'], 'Four *_graph.csv files')
card('analysis',682,1034,476,169,C['green'],'chart',['Read daily series and build charts','Cache reads until a file changes'], 'pandas · Plotly Python · lru_cache')
card('charts',1294,1034,476,169,C['purple'],'chart',['14 / 30 / 90-day trend views','Tooltips, zoom and daily-data tables'], 'Plotly.js Basic · local browser bundle')
for y,l1,l2 in [(730,'CSV rows','HTML'),(924,'Rows + shapes','Map HTML'),(1118,'Daily series','Chart JSON*')]:
    arrow(f'M546 {y}H675',label=l1,lx=614,ly=y-14)
    arrow(f'M1158 {y}H1287',label=l2,lx=1225,ly=y-14)
text(1767,1223,'* Embedded in the /analysis HTML page',12.5,C['muted'],400,text_anchor='end')

add('<g class="node current" data-key="browser" id="n-browser" tabindex="0" role="button" aria-label="Grower in a web browser. Open request details.">')
rect(48,1258,1744,88,'#183f32',r=19,**{'class':'card-bg'})
icon(73,1284,'browser','#dceee3',31)
text(121,1294,'GROWER REQUEST',13,'#b9d9c8',650,letter_spacing=1.5)
text(121,1322,'Choose state + date',22,'#ffffff',600)
for x,label in [(438,'FastAPI receives request'),(858,'Read local files'),(1218,'Render cards, maps and charts')]:
    text(x,1312,'→',25,'#a9cbb9',500)
    text(x+38,1312,label,21,'#ffffff',500)
add('</g>')
text(50,1391,'CURRENT STORAGE',13,C['blue'],700,letter_spacing=1.2)
text(50,1419,'Local CSV + GeoJSON files; no database is connected.',18,C['ink'])
text(690,1391,'SIMULATION MEANS HISTORY',13,C['green'],700,letter_spacing=1.2)
text(690,1419,'Earlier stored soil conditions, not a future prediction.',18,C['ink'])
text(1320,1391,'INTERACTIVE EXPLORER',13,C['purple'],700,letter_spacing=1.2)
text(1320,1419,'Open the HTML for details and every tool.',18,C['ink'])
add('<path d="M48 1450H1792" stroke="#dce4dc"/>')
text(50,1478,'Evidence: backend/ · dashboard/ · data/ · analytics/ · requirements.txt · docs/analysis.md',14,C['muted'])
text(1790,1478,'Solid = current     Dashed = planned',14,C['muted'],500,text_anchor='end')
add('</svg>')
SVG=''.join(parts)
(OUT/'soilmate-system-architecture.svg').write_text(SVG,encoding='utf-8')

HTML='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SoilMate — Architecture explorer</title>
<style>
:root{--ink:#18372f;--muted:#5e7169;--line:#dbe4dd;--green:#187755;--bg:#f6f8f4}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 'Segoe UI',Arial,sans-serif}button,input{font:inherit}button{cursor:pointer;border:1px solid var(--line);border-radius:9px;padding:8px 12px;background:white;color:var(--ink)}button:hover,button:focus-visible{border-color:var(--green);outline:2px solid #b7d6c3;outline-offset:2px}button[aria-pressed=true]{background:#183f32;color:white;border-color:#183f32}header{padding:20px 26px;border-bottom:1px solid var(--line);background:#fff;display:flex;align-items:center;justify-content:space-between;gap:15px;flex-wrap:wrap}h1{font-size:24px;line-height:1.3;margin:0}header p{margin:4px 0 0;color:var(--muted)}.tag{font-size:12px;background:#e9f2ec;color:#187755;border-radius:20px;padding:6px 12px;white-space:nowrap}.toolbar{padding:14px 26px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;border-bottom:1px solid var(--line);background:#f9fbf8}.group{display:flex;gap:6px;align-items:center;flex-wrap:wrap}.label{color:var(--muted);font-size:13px;margin-right:3px}.layout{display:grid;grid-template-columns:minmax(0,1fr) 330px;align-items:start;gap:0}.workspace{min-width:0;padding:20px}.canvas{overflow:auto;border:1px solid var(--line);border-radius:16px;background:#f6f8f4;max-height:calc(100vh - 230px);min-height:400px}.diagram{width:100%;min-width:900px}.diagram>svg{display:block;width:100%;height:auto}.tip{color:var(--muted);font-size:13px;margin:12px 4px}.detail{padding:22px;border-left:1px solid var(--line);background:#fff;min-height:calc(100vh - 175px);overflow-wrap:anywhere}.detail h2{font-size:22px;line-height:1.3;margin:12px 0}.detail h3{font-size:12px;text-transform:uppercase;letter-spacing:1.1px;margin:22px 0 7px;color:var(--muted)}.detail p{margin:8px 0}.detail ul{padding-left:18px;margin:5px 0}.detail li{margin:7px 0}.status{display:inline-block;border-radius:16px;padding:4px 10px;background:#e9f3ed;color:#187755;font-size:12px;font-weight:650}.status.planned{background:#faf1df;color:#9b6b22}.file{display:block;padding:6px 8px;background:#f4f6f2;border:1px solid #e1e7df;border-radius:6px;font:12px/1.5 Consolas,monospace;margin-top:6px}.chip{display:inline-block;padding:3px 8px;background:#edf1f6;border-radius:5px;margin:3px 3px 3px 0;font-size:12px}.note{border-left:3px solid #b18a42;padding:8px 12px;background:#faf6ed}.step{font-size:13px;color:#355c46;flex:1;min-width:180px}.tools{padding:24px;max-width:1100px;margin:auto}.tools h2{margin-top:0}.search{padding:10px;border:1px solid var(--line);border-radius:9px;width:min(450px,100%);margin:8px 0 18px}table{border-collapse:collapse;width:100%;background:#fff;border:1px solid var(--line);border-radius:10px}th,td{text-align:left;padding:12px;border-bottom:1px solid var(--line);vertical-align:top}th{font-size:13px;background:#eef3ed}td:first-child{font-weight:600}td:nth-child(2){white-space:nowrap;font-size:13px;color:#52685c}.table-scroll{overflow:auto}.tools p{color:var(--muted)}[hidden]{display:none!important}footer{padding:16px 26px;color:var(--muted);border-top:1px solid var(--line);font-size:12px}a{color:#187755}.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}@media(max-width:1000px){.layout{grid-template-columns:minmax(0,1fr)}.detail{border-left:0;border-top:1px solid var(--line);min-height:0}.canvas{max-height:65vh}.workspace{padding:12px}header,.toolbar{padding:14px 16px}.tools{padding:16px}th,td{padding:9px}.diagram{min-width:1000px}}@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style></head><body>
<header><div><h1>SoilMate architecture explorer</h1><p>See the data, the Python app, the dashboard, and what is still planned.</p></div><span class="tag">Inspected source · 15 Nov 2026</span></header>
<nav class="toolbar" aria-label="Architecture controls">
<div class="group" aria-label="Page"><button id="diagram-tab" aria-pressed="true">Architecture</button><button id="tools-tab" aria-pressed="false">All tools</button></div>
<div class="group" id="filters" aria-label="Show components"><span class="label">Focus</span><button data-filter="all" aria-pressed="true">All</button><button data-filter="current" aria-pressed="false">Current</button><button data-filter="planned" aria-pressed="false">Planned</button></div>
<div class="group" id="zoom-tools"><button id="zoom-out" aria-label="Zoom out">−</button><button id="fit">Fit</button><button id="zoom-in" aria-label="Zoom in">+</button></div>
<button id="trace">Trace a request</button><button id="reset">Reset</button><span class="step" id="step" role="status" aria-live="polite">Click any component to see what it does.</span>
</nav>
<main id="architecture" class="layout"><section class="workspace" aria-label="Architecture diagram"><div class="canvas" tabindex="0" aria-label="Scrollable architecture canvas"><div class="diagram">__SVG__</div></div><p class="tip">Click a card for its inputs, outputs, tools and source files. Use Focus to separate the working app from planned work. On smaller screens, scroll inside the diagram.</p></section><aside class="detail" id="detail" aria-live="polite"></aside></main>
<section class="tools" id="toolbox" hidden aria-labelledby="tools-title"><h2 id="tools-title">Every tool and its role</h2><p>Current = found in the source or existing QA. Declared = listed in the starter manifest. Planned / alternative / optional = not part of the working dashboard. The manifest is not a verified lockfile.</p><label for="search">Find a tool or role</label><br><input class="search" id="search" type="search" placeholder="Try maps, NASA, cache or forecasting"><p id="tool-count" role="status"></p><div class="table-scroll"><table><thead><tr><th scope="col">Tool</th><th scope="col">Status</th><th scope="col">What it does</th></tr></thead><tbody id="tools-body"></tbody></table></div></section>
<footer>Architecture reflects the inspected project files, not a production deployment audit. Current NASA downloads, forecasting, a database, login and scheduled refresh are not demonstrated. The explorer itself works offline. The application’s external browser assets and map tiles may need internet access.</footer>
<script>
const nodes=__NODES__, tools=__TOOLS__;
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const detail=document.getElementById('detail'), step=document.getElementById('step');
function list(title,values,cls=''){return '<h3>'+title+'</h3>'+(cls?values.map(v=>'<span class="'+cls+'">'+esc(v)+'</span>').join(''):'<ul>'+values.map(v=>'<li>'+esc(v)+'</li>').join('')+'</ul>')}
function show(key){const n=nodes[key];document.querySelectorAll('.node').forEach(el=>el.classList.toggle('active',el.dataset.key===key));detail.innerHTML='<span class="status '+n.status.toLowerCase()+'">'+n.status+'</span><h2>'+esc(n.title)+'</h2><p>'+esc(n.purpose)+'</p>'+list('Inputs',n.inputs)+list('Outputs',n.outputs)+list('Tools',n.tools,'chip')+list('Source files',n.files,'file')+(n.notes?'<h3>Read this first</h3><p class="note">'+esc(n.notes)+'</p>':'')}
function welcome(){document.querySelectorAll('.node').forEach(el=>el.classList.remove('active'));detail.innerHTML='<span class="status">Architecture guide</span><h2>Follow the data</h2><p>The current app reads local files, prepares the results in Python, and shows them in a web browser.</p><h3>Three working paths</h3><ul><li><b>Weather and risk:</b> CSV rows → FastAPI + Jinja → cards and a historical soil scene.</li><li><b>Maps:</b> CSV + GeoJSON → Folium → five Leaflet views.</li><li><b>Analysis:</b> daily CSVs → pandas + Plotly → trend charts and daily-data tables.</li></ul><h3>How to explore</h3><ul><li>Select any card for inputs, outputs and file names.</li><li>Choose <b>Current</b> or <b>Planned</b> to focus the diagram.</li><li>Use <b>Trace a request</b> for a step-by-step Analysis example.</li><li>Open <b>All tools</b> for the complete inventory.</li></ul><p class="note">The NASA pipeline and forecast branch are planned. Current Simulation selects earlier stored conditions; it does not predict the future.</p>'}
let filter='all', zoom=100, traceIndex=-1;
function focusFilter(value){filter=value;document.querySelectorAll('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.filter===value));document.querySelectorAll('.node,.edge').forEach(el=>el.classList.toggle('dim',value!=='all'&&!el.classList.contains(value)))}
document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{focusFilter(b.dataset.filter);traceIndex=-1;document.getElementById('trace').textContent='Trace a request';step.textContent=b.dataset.filter==='all'?'Showing the current app and the planned pipeline.':b.textContent+' components are highlighted.'}));
document.querySelectorAll('.node').forEach(el=>{el.addEventListener('click',()=>show(el.dataset.key));el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();show(el.dataset.key)}})});
function setZoom(value){zoom=Math.max(60,Math.min(200,value));document.querySelector('.diagram').style.width=zoom+'%';document.getElementById('fit').textContent=zoom===100?'Fit':zoom+'%'}
document.getElementById('zoom-in').onclick=()=>setZoom(zoom+20);document.getElementById('zoom-out').onclick=()=>setZoom(zoom-20);document.getElementById('fit').onclick=()=>setZoom(100);
const steps=[['browser','1 / 6 — Choose a state, date and 30-day chart window in the browser.'],['analysis','2 / 6 — GET /analysis sends those values to FastAPI.'],['history','3 / 6 — Read the four daily CSVs; reuse the cache if the files have not changed.'],['analysis','4 / 6 — Filter observations, keep gaps, and build Plotly chart JSON.'],['charts','5 / 6 — Jinja returns the Analysis page; Plotly.js draws the charts.'],['browser','6 / 6 — Read tooltips and daily data, or change filters to request another view.']];
document.getElementById('trace').onclick=()=>{switchTab(false);focusFilter('current');traceIndex=(traceIndex+1)%steps.length;show(steps[traceIndex][0]);step.textContent=steps[traceIndex][1];document.getElementById('trace').textContent=traceIndex===steps.length-1?'Replay request':'Next step';document.getElementById('n-'+steps[traceIndex][0]).scrollIntoView({block:'nearest',inline:'nearest',behavior:'instant'})};
function switchTab(toolMode){document.getElementById('architecture').hidden=toolMode;document.getElementById('toolbox').hidden=!toolMode;document.getElementById('diagram-tab').setAttribute('aria-pressed',String(!toolMode));document.getElementById('tools-tab').setAttribute('aria-pressed',String(toolMode));document.getElementById('filters').hidden=toolMode;document.getElementById('zoom-tools').hidden=toolMode;step.textContent=toolMode?'Search the full inventory below.':'Click any component to see what it does.'}
document.getElementById('diagram-tab').onclick=()=>switchTab(false);document.getElementById('tools-tab').onclick=()=>switchTab(true);
function renderTools(){const q=document.getElementById('search').value.toLowerCase();const rows=tools.filter(r=>r.join(' ').toLowerCase().includes(q));document.getElementById('tools-body').innerHTML=rows.map(r=>'<tr>'+r.map(c=>'<td>'+esc(c)+'</td>').join('')+'</tr>').join('');document.getElementById('tool-count').textContent=rows.length+' of '+tools.length+' tools and tool groups'}
document.getElementById('search').oninput=renderTools;
document.getElementById('reset').onclick=()=>{switchTab(false);focusFilter('all');setZoom(100);traceIndex=-1;document.getElementById('trace').textContent='Trace a request';document.getElementById('search').value='';renderTools();welcome();document.querySelector('.canvas').scrollTo(0,0)};
renderTools();welcome();
</script></body></html>'''.replace('__SVG__',SVG).replace('__NODES__',json.dumps(NODES)).replace('__TOOLS__',json.dumps(TOOLS))
(OUT/'soilmate-architecture-interactive.html').write_text(HTML,encoding='utf-8')
(OUT/'architecture-data.json').write_text(json.dumps({'review_date':'2026-11-15','nodes':NODES,'tools':TOOLS},indent=2),encoding='utf-8')
(OUT/'README.md').write_text('''# SoilMate / Nasa Petani — System architecture

Reviewed from the local project on 15 November 2026.

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

`analytics/data_ingestion.py`, `analytics/data_cleaning.py` and `analytics/forecasting_model.py` are empty. `models/` contains no model artifacts. NASA POWER, GPM IMERG, SMAP L4 and ESI source labels occur in the supplied dataset; they do not establish a working live integration or verified upstream lineage. The dashed pipeline is a proposed design, not implemented behavior. Its product selection, coverage, units and status rules need validation. The ESI scale and status cutoffs need domain review, as noted in `docs/analysis.md`.

`requirements.txt` explicitly describes itself as a starter manifest, not a tested lockfile. Streamlit, streamlit-folium and pydeck are unused alternatives to the implemented FastAPI/Jinja dashboard. Prophet, scikit-learn and satellite/geospatial processing dependencies support future work. SQLite, Parquet and Dask are optional/planned; no database is currently connected. No production hosting, authentication, background scheduler, automated refresh, model inference, or message-notification service is demonstrated in the inspected project.

Some additional CSVs (`data_petani.csv`, `data_processed.csv`, `header.csv`) are present but are not directly read by the current route and Analysis modules. Their existence is not evidence of an automated preparation pipeline. `dashboard/maps/*.html` are saved standalone exports; current map routes generate their own HTML from CSV and GeoJSON. The application loads Bootstrap and Inter from external providers; Folium map output can use external map tiles and browser libraries. The explorer itself has no external dependencies.

## Source evidence

- `backend/main.py` — HTTP routes, template rendering, weather/risk/scene readers, static files and compression.
- `backend/analysis.py` and `docs/analysis.md` — history layouts, calculations, cache, plot periods and ESI notes.
- `backend/*_map.py` — live map generation from CSV and GeoJSON.
- `dashboard/templates/` and `dashboard/static/` — dashboard, controls, browser charts and soil imagery.
- `data/processed/` and `data/Geo/` — local data inputs.
- `analytics/`, `models/` and `requirements.txt` — planned pipeline and dependency intent.
- `tests/test_analysis.py` and `output/qa/check_analysis_ui.py` — existing backend and browser QA tools.

No credentials or private environment values are included. The diagram describes source structure and behavior; it is not a production deployment audit.
''',encoding='utf-8')
print('Created SVG, interactive HTML, JSON and README in',OUT)
