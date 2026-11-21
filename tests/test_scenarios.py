import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills/joey-design"
sys.path.insert(0, str(SKILL / "scripts"))
from scenarios import build_scenario, load_scenario
from joey import copy_issues

STUDIES = SKILL / "assets/scenarios"


class ScenarioTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.work = Path(temp.name)

    def write(self, sample, alter):
        data = json.loads((STUDIES / (sample + ".json")).read_text())
        alter(data)
        source = self.work / (sample + ".json")
        source.write_text(json.dumps(data))
        return source

    def test_three_standalone_editions(self):
        for name in ["material-office", "signal-ledger", "night-school"]:
            out = self.work / name
            build_scenario(STUDIES / (name + ".json"), out)
            page = (out / "index.html").read_text()
            self.assertNotIn("@@DATA@@", page)
            self.assertFalse(re.search(r'<(?:script|link)\b[^>]*(?:src|href)="https?://', page))
            self.assertNotIn("。", page)
        with self.assertRaisesRegex(ValueError, "previous output"):
            build_scenario(STUDIES / "night-school.json", self.work / "signal-ledger")

    def test_zero_baseline_custom_metric_and_script_text(self):
        def edit(d):
            d["metrics"] = {"visits":"到访","actions":"报名","rate":"报名率"}
            d["items"][0]["previous"] = [0, 0]
            d["headline"] = "</script><x>报名</x>"
        src = self.write("signal-ledger", edit)
        out = self.work / "result"
        build_scenario(src, out)
        page = (out / "index.html").read_text()
        self.assertNotIn("</script><x>", page)
        self.assertIn("报名率", page)
        self.assertEqual(load_scenario(src)["items"][0]["previous"], [0, 0])

    def test_copy_reports_only_editable_fields(self):
        self.assertEqual(list(copy_issues({"zh": ["保留 2.5 mm", "这里换行。"], "en":"Quoted 。", "url":"https://test.invalid/a。"})), ["$.zh[1]"])
        for pattern in ("assets/studies/*.json", "assets/scenarios/*.json", "assets/starter.json"):
            for source in SKILL.glob(pattern):
                self.assertEqual(list(copy_issues(json.loads(source.read_text()))), [], source.name)

    def test_invalid_end_and_counts(self):
        src = self.write("night-school", lambda d: d["items"][0].update(end=d["items"][0]["start"]))
        with self.assertRaisesRegex(ValueError, "end must follow"):
            load_scenario(src)
        src = self.write("signal-ledger", lambda d: d["items"][0].update(previous=[3, 4]))
        with self.assertRaisesRegex(ValueError, "exceed"):
            load_scenario(src)
