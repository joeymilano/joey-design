import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from lxml import etree, html
from pptx import Presentation
from pptx.chart.data import CategoryChartData

SKILL = Path(__file__).resolve().parents[1] / "skills/joey-design"
sys.path.insert(0, str(SKILL / "scripts"))
from charts import localized_chart
from joey import build
from review import read_steps


class ChartAndReviewTest(unittest.TestCase):
    def setUp(self):
        self.brief = SKILL / "assets/studies/listening-room.json"
        self.slide = json.loads(self.brief.read_text())["slides"][1]

    def test_invalid_comparisons_are_rejected(self):
        for invalid in [True, float("nan"), -1, "18", float("inf")]:
            with self.subTest(invalid=invalid):
                self.slide["chart"]["rows"][0]["value"] = invalid
                with self.assertRaises(ValueError):
                    localized_chart(self.slide, "zh", "slide")

    def test_zeroes_keep_a_positive_axis_and_bad_domain_fails(self):
        chart = self.slide["chart"]
        chart.pop("max")
        for row in chart["rows"]:
            row["value"] = 0
        self.assertGreater(localized_chart(self.slide, "en", "slide")["maximum"], 0)
        chart["rows"][0]["value"] = 12
        chart["max"] = 3
        with self.assertRaises(ValueError):
            localized_chart(self.slide, "en", "slide")

    def test_workbook_chart_preview_notes_and_edit_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            build(self.brief, dest)
            for lang in ["zh", "en"]:
                deck = Presentation(dest / f"deck-{lang}.pptx")
                slide = deck.slides[1]
                chart = next(s.chart for s in slide.shapes if s.has_chart)
                self.assertEqual(chart.series[0].values, (0, 6, 18))
                self.assertEqual(chart.value_axis.minimum_scale, 0)
                self.assertIn(self.slide["chart"]["source"][lang], slide.notes_slide.notes_text_frame.text)
                with ZipFile(dest / f"deck-{lang}.pptx") as z:
                    path = next(p for p in z.namelist() if p.startswith("ppt/embeddings/") and p.endswith(".xlsx"))
                    with ZipFile(io.BytesIO(z.read(path))) as book:
                        ws = etree.fromstring(book.read("xl/worksheets/sheet1.xml"))
                        self.assertEqual(ws.xpath('//*[local-name()="c" and @r="B4"]/*[local-name()="v"]/text()'), ["18"])
                preview = html.fromstring((dest / f"deck-{lang}.html").read_bytes().decode())
                self.assertEqual(preview.xpath("//table//td/text()"), ["0", "6", "18"])
                self.assertEqual(preview.xpath('//a[@class="slide-action"]/@href'), ["#slide-2"])
                edited = CategoryChartData()
                edited.categories = ["A", "B", "C"]
                edited.add_series("Waiting", [0, 6, 10])
                chart.replace_data(edited)
                edited_path = dest / f"edited-{lang}.pptx"
                deck.save(edited_path)
                reopened = Presentation(edited_path)
                self.assertEqual(next(s.chart for s in reopened.slides[1].shapes if s.has_chart).series[0].values[-1], 10)

    def test_sample_journeys_and_invalid_steps(self):
        for path in (SKILL/"assets/journeys").glob("*.json"):
            self.assertGreater(len(read_steps(path)), 1)
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.json"
            p.write_text('[{"action":"click"}]')
            with self.assertRaisesRegex(ValueError, "selector"):
                read_steps(p)
