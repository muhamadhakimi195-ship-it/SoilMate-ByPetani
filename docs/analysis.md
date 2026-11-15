# Analysis page

FastAPI/Jinja remains the app framework. `/analysis` uses the shared State/Date
controls and a 14/30/90-day chart window. It reads four existing CSVs without
changing their headers, values or reported statuses.

## Data layout

`backend/analysis.py` reads the second CSV row as the summary header. The graph
blocks have their own dates. Rain, air and soil graph data are offset by one row:
their state must also shift one row, including where the next state begins.
Plant graph data have no offset. `SOURCES` records these file layouts.

Summary values come from the selected date exactly. Daily plots use the graph
block's date and retain missing days as gaps. Rain summary values always cover
14 days; changing the plot window does not relabel them as 30/90-day totals.
The cache refreshes when a source file's modification time changes.

## Visual choices

- Rain: received vs usual accumulation, with a daily-rain alternative.
- Air: daily peak minus the supplied dry-air reference; above zero exceeds it.
- Soil: root percentile with the source's 20/40 reference bands and a 7-day change.
- Plant: observed ESI dots, a 7-day change and reading coverage.

ESI values and reported statuses need a domain review: the files contain values
above 1 and statuses that do not match the proposed 0.7/0.4 cutoffs. Preserve the
raw data and show the review note; do not clamp values or invent new statuses.

Plotly Basic is served locally and only loaded on Analysis. Gzip reduces its
transfer to about 407 KB. Desktop supports drag-to-zoom/reset; touch devices
retain page scrolling and tap tooltips. Native dialogs hold detailed data.

## References and checks

- [Plotly bundles](https://github.com/plotly/plotly.js/blob/main/dist/README.md)
- [Responsive plots](https://plotly.com/javascript/responsive-fluid-layout/)
- [Reference bands](https://plotly.com/javascript/shapes/)
- [Missing observations](https://www.datawrapper.de/docs/missing-data-in-line-charts)
- [ECOSTRESS ESI definition](https://lpdaac.usgs.gov/documents/342/ECO4ESIPTJPL_ATBD_V1.pdf)

Run backend checks from the project root with the active venv:
`python -m unittest discover -s tests -v`.
`output/qa/check_analysis_ui.py` additionally tests an isolated headless Chrome
against a running FastAPI instance on port 8001; it requires Playwright for QA.
