"""Run with python -m unittest discover -s tests from the repository root."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from PIL import Image
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/joey-design/scripts"))
from joey import build


class LaunchKitTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        shutil.copytree(ROOT / "examples/afterhours", self.work / "brief")
        self.source = self.work / "brief/brief.json"
        self.dest = self.work / "deliverables"
        self.data = json.loads(self.source.read_text(encoding="utf-8"))

    def save(self):
        self.source.write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")

    def test_fact_reaches_both_editions_and_editable_powerpoint(self):
        self.data["facts"]["light"]["value"] = "3000 K"
        self.save()
        build(self.source, self.dest)
        self.assertEqual(10, len([p for p in self.dest.iterdir() if not p.name.startswith(".")]))
        for lang in ("en","zh"):
            for name in ("deck","page"):
                html = (self.dest / f"{name}-{lang}.html").read_text(encoding="utf-8")
                self.assertIn("3000 K", html)
                self.assertNotIn("2700 K", html)
            pptx = self.dest / f"deck-{lang}.pptx"
            with ZipFile(pptx) as archive:
                self.assertIsNone(archive.testzip())
            presentation = Presentation(pptx)
            self.assertEqual(len(self.data["slides"]), len(presentation.slides))
            proof = presentation.slides[2]
            shapes = [s.text for s in proof.shapes if s.has_text_frame]
            self.assertIn("3000 K", shapes)
            self.assertIn("3000 K", proof.notes_slide.notes_text_frame.text)
            for name,size in (("cover",(1080,1440)),("wide",(1280,720))):
                with Image.open(self.dest / f"{name}-{lang}.png") as image:
                    self.assertEqual(size,image.size)

    def test_broken_reference_writes_nothing(self):
        self.data["slides"][1]["body"]["en"] = "{{missing_spec}}"
        self.save()
        with self.assertRaisesRegex(ValueError, "unknown fact"):
            build(self.source, self.dest)
        self.assertFalse(self.dest.exists())

    def test_overflow_is_rejected_before_export(self):
        self.data["slides"][0]["title"]["zh"] = "灯具研发" * 100
        self.save()
        with self.assertRaisesRegex(ValueError, "does not fit"):
            build(self.source, self.dest)
        self.assertFalse(self.dest.exists())

    def test_unrelated_folder_is_preserved(self):
        self.dest.mkdir()
        previous = self.dest / "read-me.txt"
        previous.write_text("keep")
        with self.assertRaisesRegex(ValueError, "output directory"):
            build(self.source, self.dest)
        self.assertEqual("keep", previous.read_text())

    def test_examples_fit_both_languages(self):
        for example in sorted((ROOT / "examples").glob("*/brief.json")):
            with self.subTest(example=example.parent.name):
                build(example, self.dest, check=True)


if __name__ == "__main__":
    unittest.main()
