# SoilMate — ByPetani

Agricultural risk monitoring dashboard for Malaysian states, built with FastAPI,
Jinja, pandas, Folium and Plotly. It displays local CSV-based drought alerts,
weather, interactive maps, illustrative soil scenes and historical analysis.

## Run

Use Python 3.14. From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000. No `.env` or NASA API key is needed for this version.
The browser needs internet access for external fonts, Bootstrap, map libraries
and map tiles. Live NASA ingestion and forecasting are not implemented.

## Docker deployment on DigitalOcean

The deployment runs two services: `app` (FastAPI, pandas, Jinja, Folium and
Plotly) and `caddy` (reverse proxy and automatic HTTPS). Cloudflare can manage
your domain's DNS and proxy; the application runs on your DigitalOcean Droplet.

- `Dockerfile`: Python 3.14 image, non-root application user and `/health` check.
- `.dockerignore`: allowlist of application files and required data.
- `compose.yaml`: both services, process restart policies, log rotation and
  persistent Caddy certificate volumes.
- `Caddyfile`: routes your domain to the application.
- `.env.example`: hostname and optional image-tag settings; copy it to `.env`.

Only Caddy publishes public ports (80 and 443). App port 8080 is published on
`127.0.0.1` for server-side diagnostics. Application code and CSVs are baked
into the image, so updating them requires an image rebuild. The image excludes
credentials, uploads, private documents, tests and local Python environments.

### Preview locally on Windows

Start Docker Desktop in Linux-container mode. From the repository root:

```powershell
Copy-Item .env.example .env -NoClobber
docker compose config --quiet
docker compose up -d --build --wait app
Invoke-RestMethod http://127.0.0.1:8080/health
```

Open http://127.0.0.1:8080. This starts only the application, without requiring
a public domain or local certificate installation. If `.env` already exists,
keep its settings instead of copying over it. To stop the preview:

```powershell
docker compose stop app
```

### Prepare the server and DNS

Use a fresh Linux Droplet in Singapore, starting with 1 GiB RAM. The Docker
Marketplace image includes Docker and Compose. If using a plain Ubuntu image,
follow [Docker's Ubuntu installation instructions](https://docs.docker.com/engine/install/ubuntu/).
Check `docker version` and `docker compose version` on the server.

Attach a DigitalOcean Cloud Firewall with TCP 22 allowed from your administrator
IP, and TCP 80/443 from the Internet (IPv4 and IPv6). Allow outbound traffic.
Port 8080 does not need a public rule. Enable Docker to start after reboot:

```bash
sudo systemctl enable --now docker
```

In Cloudflare DNS, create an A record pointing your chosen hostname at the
Droplet's public IPv4. Use `@` for the root domain or `soilmate` for a subdomain.
Start with **DNS only** while testing origin HTTPS. Keep existing unrelated DNS
records; if using an AAAA record, it must point to this server's working IPv6.

### First deployment

First commit and push the Docker deployment files and `/health` backend change
from your computer to the repository's `main` branch. On a fresh server, clone
the repository into an unused directory, for example `/opt/soilmate`:

```bash
sudo apt update
sudo apt install -y git curl
sudo git clone https://github.com/muhamadhakimi195-ship-it/SoilMate-ByPetani.git /opt/soilmate
cd /opt/soilmate
```

Run the remaining Docker commands as a user with Docker access (or prefix them
with `sudo`). A private GitHub repository needs a read-only SSH deploy key or
another configured Git authentication method.

```bash
cp .env.example .env
nano .env
```

Replace `DOMAIN=localhost` with your actual hostname, such as
`DOMAIN=soilmate.example.com`. Use a hostname without a scheme or path.
Leave `IMAGE_TAG=latest` for the commands below. Then:

```bash
docker compose config --quiet
docker compose build app
docker compose up -d --wait --wait-timeout 180
docker compose ps
docker compose logs --tail=100 app caddy
curl -fsS http://127.0.0.1:8080/health
```

Run the commands one at a time and stop on any failure. The health response
should be `{"status":"ok"}`. Caddy waits for the application's health check
before starting and obtains a certificate for your configured hostname. DNS
propagation and first certificate issuance may take longer than app startup.

Open `https://YOUR_HOSTNAME/health`, then test `/`, `/analysis`, every map layer,
date/state changes and simulation weeks. Confirm browser assets load over HTTPS.
An HTTP health response alone does not validate CSV analysis or map generation.
Use `docker stats --no-stream` while testing analysis to check memory headroom;
the 1 GiB starting size has not yet been validated against this application's load.

Once origin HTTPS works, set Cloudflare **SSL/TLS > Overview > Full (strict)**,
then enable **Proxied** on that DNS record. See
[Cloudflare Full (strict)](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/).

### Operations, updates and rollback

Both services use `restart: unless-stopped`; they do not sleep when idle.
Docker restarts an exited process, but a failing health check alone does not
restart a running container. Monitor health externally and check logs on errors.
This is a single-server deployment; a server outage or an update can interrupt
availability. Do not delete the `caddy_data` volume: it holds certificate state.

For application/CSV-only updates, with `IMAGE_TAG=latest`, run one command at a
time and stop on failure. Keep the server checkout clean and edit code in Git:

```bash
cd /opt/soilmate
docker image tag soilmate:latest soilmate:previous
git rev-parse HEAD
git pull --ff-only origin main
docker compose build app
docker compose up -d --no-deps --wait --wait-timeout 180 app
curl -fsS http://127.0.0.1:8080/health
docker compose ps
```

Record the old Git revision printed above. If the new application fails, restore
the previous image using the same Compose configuration:

```bash
docker image tag soilmate:previous soilmate:latest
docker compose up -d --no-deps --force-recreate --wait --wait-timeout 180 app
```

Then repeat the domain and feature checks. This restores the old application
and its baked-in CSVs, not changes to Compose, Caddy, DNS or external services.
Review infrastructure changes separately, and preserve the previous configuration
before applying them. Validate Caddy configuration before reloading it:

```bash
docker compose exec caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
```

The application currently stores no user uploads or database writes. Preserve
your `.env` settings and keep the source CSVs in Git. If writable application
storage is added later, configure persistent storage and backups for that data.

## Runtime files

- `backend/`: routes, data readers, maps and analysis.
- `dashboard/`: templates and prepared static assets.
- `data/Geo/malay.geojson`: state boundaries.
- `data/processed/`: the eight CSVs required by the dashboard.
- `requirements.txt`: six pinned direct runtime dependencies; pip installs their dependencies.

Private documentation, offline tools, tests, uploads, virtual environments and
extra development requirements are kept locally and excluded from this repository.

## License and asset credits

Project code uses the [MIT license](LICENSE). Third-party images and icons retain
their individual terms. Resized/compressed photo variants and CSS cropping are
used for display; photo credits are also shown in the dashboard.
Simulation images are AI-generated educational illustrations, not observed farm photographs.

Lucide icons are unmodified SVGs from `lucide-static` 0.468.0,
[Lucide](https://lucide.dev), with the ISC notice retained in
`dashboard/static/icons/lucide/LICENSE`. Their colors are supplied by CSS masks.
The state flag PNGs were supplied by the project owner; preserve the original
source terms provided with those downloads.

### State photographs

| State asset | Photographer | Source | License |
| --- | --- | --- | --- |
| johor | Aimanabdulharis | [Photo](https://commons.wikimedia.org/wiki/File:Istana_Bukit_Serene_-_The_Royal_Crown_(night,_2015).jpg) | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| kedah | MosheA | [Photo](https://commons.wikimedia.org/wiki/File:MasjidZahir.jpg) | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| kelantan | Tourism Kelantan | [Photo](https://tourism.kelantan.my/index.php/pelancongan/alam-semulajadi/pantai-tasik/pantai-cahaya-bulan) | [See source](https://tourism.kelantan.my/index.php/pelancongan/alam-semulajadi/pantai-tasik/pantai-cahaya-bulan) |
| kuala-lumpur | CEphoto, Uwe Aranas | [Photo](https://commons.wikimedia.org/wiki/File:Kuala_Lumpur_Malaysia_Sultan-Abdul-Samad-Building-05.jpg) | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0) |
| labuan | Aidlfarhn | [Photo](https://commons.wikimedia.org/wiki/File:Masjid_Jamek_Annur,_2021.jpg) | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| malacca | Irwan Shah Bin Abdullah / https://ehalal.io/muslim-friendly-travel-2024/Malacca | [Photo](https://commons.wikimedia.org/wiki/File:A_Famosa_Portugese_fort_in_Malacca_with_a_canon.jpg) | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| negeri-sembilan | Zahirulnukman | [Photo](https://commons.wikimedia.org/wiki/File:Istana_Seri_Menanti_(30042023)_32.jpg) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0) |
| pahang | PenangLion | [Photo](https://commons.wikimedia.org/wiki/File:Kuantan_skyline,_August_2025.jpg) | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| penang | DvTor8303 | [Photo](https://commons.wikimedia.org/wiki/File:Penang_Bridge_20250222.jpg) | [CC0](http://creativecommons.org/publicdomain/zero/1.0/deed.en) |
| perak | cahaya tuah | [Photo](https://www.pexels.com/photo/old-brick-castle-on-hill-against-cloudy-storm-sky-14727506/) | [Pexels License](https://www.pexels.com/license/) |
| perlis | DanialNajmi | [Photo](https://commons.wikimedia.org/wiki/File:Sunset_at_Al-Hussain_Floating_Mosque.jpg) | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| putrajaya | Scruffy | [Photo](https://www.pexels.com/photo/putra-mosque-27797400/) | [Pexels License](https://www.pexels.com/license/) |
| sabah | Ihsan Adityawarman | [Photo](https://www.pexels.com/photo/trees-and-mountains-behind-15874776/) | [Pexels License](https://www.pexels.com/license/) |
| sarawak | Muhammad Uthman Muhammed Suhaimi | [Photo](https://www.pexels.com/photo/state-legislative-assembly-building-in-kuching-34862419/) | [Pexels License](https://www.pexels.com/license/) |
| selangor | Muyu yao | [Photo](https://www.pexels.com/photo/magnificent-blue-mosque-dome-and-minarets-in-daylight-39946482/) | [Pexels License](https://www.pexels.com/license/) |
| terengganu | Faizal Ortho | [Photo](https://www.pexels.com/photo/an-aerial-photography-of-terengganu-drawbridge-4467146/) | [Pexels License](https://www.pexels.com/license/) |

The Tourism Kelantan source does not state an explicit reuse license for the
Pantai Cahaya Bulan photo; its permission remains unverified.

### Weather photographs

These illustrate weather conditions, not the selected state or date. Display
uses CSS cropping; optimized delivery files retain the source dimensions.

| Condition / local file | Photographer | Source | License |
| --- | --- | --- | --- |
| Partly cloudy / partly-cloudy.jpg | HampusWennberg | [Sky with clouds and sun](https://commons.wikimedia.org/wiki/File:Sky_with_clouds_and_sun.jpg), photographed 20 July 2012 | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| Showers / showers.jpg | Merikanto | [Rain shower after cold front 3](https://commons.wikimedia.org/wiki/File:Rain_shower_after_cold_front_3.JPG), photographed 19 August 2007 | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) |
| Light rain / light-rain.jpg | W.carter | [Light rain on a roof](https://commons.wikimedia.org/wiki/File:Light_rain_on_a_roof.jpg), photographed 11 June 2018 | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| Sunny and hot / sunny-hot.jpg | Carla Nunziata | [Sun in the sky](https://commons.wikimedia.org/wiki/File:Sun_in_the_sky.jpg), uploaded 30 November 2009 | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) |
