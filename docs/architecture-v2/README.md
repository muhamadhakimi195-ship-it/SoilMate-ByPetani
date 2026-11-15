# SoilMate architecture — revision 2

The architecture was redrawn using separate structural and data views, following the C4 model and Microsoft architecture diagram guidance. Source reviewed on 15 November 2026.

## Files

- `01-system.svg` / `.png`: main C4-informed container diagram. It shows the grower, browser-delivered dashboard, single Python web application, local file store, external asset providers, system boundary and labelled relationships.
- `02-components.svg` / `.png`: zoom into the one Python application. The route/page handlers call Overview readers, the Analysis builder and the map builder. All are in the same application process. Local datasets appear outside that process boundary.
- `03-data-design.svg` / `.png`: proposed NASA acquisition and preparation architecture. Raw files, checked tables, the current serving interface and an optional unconnected forecast branch are distinguished.
- `soilmate-architecture.html`: offline interactive explorer. Switch views, click nodes, highlight their neighbours, trace labelled connections, zoom and search the full tool register.
- `soilmate-architecture.drawio`: editable diagrams.net source with three pages.
- `architecture-model.json`: structured nodes and relationships.
- `build.py` and `render_svg.ps1`: reproducible vector generation and offline Windows PNG renderer. The generator reuses the repository evidence inventory in `../architecture/architecture-data.json`. A copy is included as `evidence-data.json` for standalone use.

## Scope and interpretation

The System and Backend views represent the inspected source. Data design is a proposal, not a claim that live NASA ingestion is implemented. No hosting provider, SQL database, queue, authentication service or notification service is invented. Technologies are labelled on architectural elements instead of represented as separate services. In C4, a container is an application or a data store; it does not mean a Docker container.

The client container represents browser-executed HTML/CSS/JavaScript delivered by the server. It is not an independently hosted SPA. Pages are rendered with Jinja2. Overview uses fetch to obtain HTML fragments. Analysis receives chart JSON inside HTML and uses the local Plotly.js bundle. Maps are built on request with Folium and displayed in a Leaflet iframe. The server reads a filesystem store, not a database. Analysis uses an in-process file-change-aware cache, not Redis. Uvicorn is declared as a runner; no production process configuration is supplied.

The current Simulation panel selects earlier stored conditions and changes imagery; it is not a future prediction. The forecasting script is empty and no models are present. NASA products appear as source names in the supplied data; their precise versions, coverage, quality rules and lineage remain to be validated before integration. The ESI scale and thresholds need domain review, as recorded in `docs/analysis.md`. The starter manifest includes unused alternatives, which are separated in the tool register.

## Diagram conventions

- A coloured block is a typed architectural element with a technology and a short responsibility.
- A dashed outer rectangle is a scope boundary, not a network or deployment assertion.
- A solid directional arrow is a current relationship. Its label states the action and protocol/interface.
- An amber dashed arrow is a proposed integration. Amber blocks are proposed processes or stores. The Data design view mixes the existing file-reader interface with proposed upstream writers; its title explicitly marks this scope.
- File access and Python calls are labelled as such; they are not presented as HTTP or separate services.
- Request and response relationships in the main view are separate arrows. Connection tracing explores individual relationships; it is not an execution sequence.

## Sources used for the redraw

- https://c4model.com/diagrams/container — applications/data stores, technology, responsibilities and communication.
- https://c4model.com/diagrams/component — decomposition within one application container.
- https://c4model.com/diagrams/notation — element types, labels, technologies, direction and diagram keys.
- https://learn.microsoft.com/en-us/azure/well-architected/architect-role/design-diagrams — progressive detail, clear scope, meaningful arrows and accurate notation.

Original wording and drawings are used; the reference pages informed the approach.

## Project evidence

`backend/main.py`, `backend/analysis.py`, `backend/*_map.py`, `dashboard/templates/`, `dashboard/static/`, `data/processed/`, `data/Geo/`, `docs/analysis.md`, `analytics/`, `models/`, and `requirements.txt`. No credentials are included.
