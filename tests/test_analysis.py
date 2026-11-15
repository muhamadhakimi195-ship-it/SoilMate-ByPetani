import json
import gzip
import re
import unittest
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from backend.analysis import SOURCES, get_analysis
from backend.main import app, get_simulation


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.sources = {
            key: pd.read_csv(Path("data/processed") / settings[0], header=1, dtype=str)
            for key, settings in SOURCES.items()
        }

    def test_graph_values_at_state_boundaries(self):
        # The shifted graph rows must never inherit the next state's name.
        cases = [("Perlis", "2025-12-31"), ("Kedah", "2020-01-01"),
                 ("Kuala Lumpur", "2020-01-01"), ("Labuan", "2025-12-31")]
        for state, selected in cases:
            response = self.client.get("/analysis", params={"date": selected, "state": state, "days": 30})
            self.assertEqual(response.status_code, 200)
            cards = get_analysis(selected, state)["cards"]
            rendered = [json.loads(spec) for spec in re.findall(r'class="analysis-spec">(.*?)</script>', response.text, re.S)]
            self.assertEqual(rendered, [card["views"] for card in cards])
            for card in cards:
                _, date_format, graph_start, offset, _ = SOURCES[card["id"]]
                source = self.sources[card["id"]]
                dates = pd.to_datetime(source.iloc[:, 0], format=date_format, errors="coerce")
                index = source.index[(source.iloc[:, 1] == state) & (dates == pd.Timestamp(selected))][0] + offset
                expected = float(source.iloc[index, graph_start + 1])
                series = card["views"][0]["figure"]["data"][0]
                if card["id"] == "rain":
                    daily = card["views"][1]["figure"]["data"][0]["y"]
                    self.assertEqual(daily[-1], expected)
                    accumulated = card["views"][0]["figure"]["data"][1]["y"]
                    self.assertAlmostEqual(accumulated[-1], sum(value for value in daily if value is not None))
                elif card["id"] == "air":
                    reference = float(source.iloc[index, graph_start + 2])
                    peak = float(source.iloc[index, graph_start + 3])
                    self.assertAlmostEqual(series["y"][-1], peak - reference)
                    self.assertEqual(series["customdata"][-1], [peak, reference])
                else:
                    self.assertEqual(series["y"][-1], expected)
                for view in card["views"]:
                    json.dumps(view, allow_nan=False)

    def test_new_source_snapshots_and_comparisons(self):
        cards = get_analysis("2025-12-31", "Perlis")["cards"]
        self.assertEqual([card["primary"] for card in cards], ["12", "0", "67", "1.9"])
        self.assertEqual(cards[0]["comparison"], "68 mm usual")
        self.assertEqual(cards[0]["insight"], "56 mm below usual")
        self.assertEqual(cards[3]["warning"], "ESI scale needs review")

    def test_partial_history_preserves_missing_values(self):
        for days in [14, 30, 90]:
            cards = get_analysis("2020-01-01", "Perlis", days)["cards"]
            self.assertTrue(all(card["available"] == 1 for card in cards))
            self.assertEqual(cards[3]["views"][0]["figure"]["data"][0]["y"][-1], 1.217)
            soil = cards[2]["views"][0]["figure"]
            self.assertEqual(soil["data"][0]["y"].count(None), days - 1)
            self.assertEqual(len(soil["data"]), 1)
            self.assertEqual(soil["layout"]["yaxis"]["range"], [0, 100])

    def test_page_controls_and_empty_period(self):
        for days in [14, 30, 90]:
            response = self.client.get("/analysis", params={"date": "2025-12-31", "state": "Kuala Lumpur", "days": days})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(re.findall(r'<option\b[^>]*\sselected[^>]*>(.*?)</option>', response.text), ["Kuala Lumpur"])
            self.assertIn(f'name="days" value="{days}"', response.text)
            self.assertEqual(response.text.count("data-analysis-card"), 4)
            self.assertEqual(response.text.count("<dialog "), 4)
            self.assertEqual(response.text.count('id="map-date"'), 1)
        response = self.client.get("/analysis", params={"date": "2019-12-31", "state": "Perlis"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text.count("No observations in this period."), 4)
        self.assertTrue(all(card["primary"] == "—" for card in get_analysis("2019-12-31", "Perlis")["cards"]))
        self.assertEqual(self.client.get("/analysis", params={"days": 13}).status_code, 422)
        self.assertEqual(self.client.get("/analysis", params={"days": 91}).status_code, 422)

    def test_light_bundle_and_overview_regressions(self):
        vendor = self.client.get("/static/vendor/plotly-basic-4.3.0.min.js", headers={"Accept-Encoding": "gzip"})
        self.assertEqual(vendor.status_code, 200)
        self.assertEqual(vendor.headers["content-encoding"], "gzip")
        compressed_size = len(gzip.compress(vendor.content, compresslevel=5))
        self.assertLess(compressed_size, 450000)
        print("Plotly gzip bytes:", compressed_size)
        home = self.client.get("/", params={"date": "2020-01-01", "state": "Perlis"})
        self.assertEqual(home.status_code, 200)
        self.assertEqual(home.text.count('class="map-legend"'), 5)
        self.assertNotIn("plotly", home.text.lower())
        self.assertEqual([layer["value"] for layer in get_simulation("2020-01-01", "Perlis")["layers"]], ["-99", "1.7", "4", "1.22"])
        for endpoint in ["/weather", "/risk-layers", "/simulation"]:
            self.assertEqual(self.client.get(endpoint, params={"date": "2020-01-01", "state": "Perlis"}).status_code, 200)
        for asset in ["/static/analysis.js", "/static/analysis.css", "/static/simulation/simulation-soil-dry.webp"]:
            self.assertEqual(self.client.get(asset).status_code, 200)


if __name__ == "__main__":
    unittest.main()
