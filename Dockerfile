FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install -r requirements.txt \
    && useradd --create-home --uid 10001 soilmate

COPY backend/ ./backend/
COPY dashboard/ ./dashboard/
COPY data/Geo/malay.geojson ./data/Geo/malay.geojson
COPY data/processed/LayerRisk.csv data/processed/header.csv data/processed/weather.csv data/processed/maps_data.csv data/processed/rainfall_graph.csv data/processed/humidity_graph.csv data/processed/soil_moisture_graph.csv data/processed/plant_stress_graph.csv ./data/processed/

USER soilmate
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=5).read()"]
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "--forwarded-allow-ips", "*"]
