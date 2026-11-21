import json
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills/joey-design"
sys.path.insert(0, str(SKILL / "scripts"))
from projects import build_project, shortest_route


class ProjectTests(unittest.TestCase):
    def test_route_collects_every_stop_before_finishing(self):
        self.assertEqual(shortest_route(["SEB", ".#."]), 3)
        with self.assertRaisesRegex(ValueError, "cannot be reached"):
            shortest_route(["S#E", "B#."])
        with self.assertRaisesRegex(ValueError, "rectangular"):
            shortest_route(["SB", "E.."])

    def test_starters_work_offline_and_do_not_overwrite_other_projects(self):
        with tempfile.TemporaryDirectory() as tmp:
            for mode, name in [("site","stillroom"), ("ui","contact-sheet"), ("game","last-ferry")]:
                folder=Path(tmp)/mode
                build_project(mode, SKILL/"assets/studies"/(name+".json"), folder)
                text=(folder/"index.html").read_text()
                self.assertIn("data:image/jpeg;base64,",text)
                self.assertNotIn("@@BRIEF@@",text)
                self.assertNotIn("。",text)
            with self.assertRaisesRegex(ValueError, "previous output"):
                build_project("game", SKILL/"assets/studies/last-ferry.json", Path(tmp)/"site")

    def test_shipped_maps_fit_their_fuel_budgets(self):
        sample=json.loads((SKILL/"assets/studies/last-ferry.json").read_text())
        self.assertEqual([shortest_route(l["map"]) for l in sample["levels"]], [10,17,16])
        self.assertTrue(all(shortest_route(l["map"]) <= l["budget"] for l in sample["levels"]))
