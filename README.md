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
