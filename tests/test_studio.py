"""Regression checks for the installed studies and two format-specific builders."""
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
SKILL = ROOT/"skills/joey-design"
sys.path.insert(0,str(SKILL/"scripts"))
from studio import build_studio, load
from joey import build


class StudioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.studies = self.work/"studies"
        shutil.copytree(SKILL/"assets/studies",self.studies)

    def test_image_pack_matches_the_five_rendered_pages(self):
        for name in ("lightwalk","side-b"):
            with self.subTest(name=name):
                out=self.work/name
                build_studio(self.studies/(name+".json"),out,"social")
                pages=sorted(out.glob("*.jpg"))
                self.assertEqual(len(pages),5)
                with ZipFile(out/"images.zip") as bundle:
                    for p in pages:
                        self.assertEqual(bundle.read(p.name),p.read_bytes())
                        with Image.open(p) as im:
                            self.assertEqual(im.size,(1080,1440))
                    self.assertEqual(bundle.read("caption.txt"),(out/"caption.txt").read_bytes())

    def test_format_independent_inputs_and_escaped_script_data(self):
        p=self.studies/"side-b.json"
        data=json.loads(p.read_text(encoding="utf8"))
        del data["social"]
        data["app"]["title"]="</script><em>Plain text</em>"
        p.write_text(json.dumps(data),encoding="utf8")
        out=self.work/"app"
        build_studio(p,out,"app")
        page=(out/"index.html").read_text(encoding="utf8")
        self.assertNotIn(data["app"]["title"],page)
        self.assertIn("data:image/jpeg;base64,",page)
        self.assertFalse((out/"images.zip").exists())

    def test_unknown_image_or_slot_is_rejected(self):
        p=self.studies/"side-b.json"
        d=json.loads(p.read_text(encoding="utf8"))
        d["app"]["items"][0]["slots"]=["slot","slot"]
        p.write_text(json.dumps(d),encoding="utf8")
        with self.assertRaisesRegex(ValueError,"unique"):load(p,"app")
        d["social"]["pages"][0]["image"]="missing"
        p.write_text(json.dumps(d),encoding="utf8")
        with self.assertRaisesRegex(ValueError,"Unknown image"):load(p,"social")

    def test_shorter_carousel_removes_stale_cards_and_preserves_unrelated_files(self):
        p=self.studies/"lightwalk.json"
        out=self.work/"note"
        build_studio(p,out,"social")
        (out/"notes.txt").write_text("keep")
        d=json.loads(p.read_text(encoding="utf8"))
        d["social"]["pages"]=d["social"]["pages"][:2]
        p.write_text(json.dumps(d),encoding="utf8")
        build_studio(p,out,"social")
        self.assertEqual(len(list(out.glob("*.jpg"))),2)
        self.assertEqual((out/"notes.txt").read_text(),"keep")
        with self.assertRaisesRegex(ValueError,"previous output"):build_studio(p,out,"app")

    def test_photo_spread_has_two_distinct_editable_pictures_and_native_captions(self):
        out=self.work/"deck"
        build(self.studies/"lightwalk-deck.json",out)
        for lang in ("en","zh"):
            slide=Presentation(out/f"deck-{lang}.pptx").slides[2]
            pictures=[s.image.blob for s in slide.shapes if s.shape_type==13]
            self.assertEqual(len(set(pictures)),2)
            text=[s.text for s in slide.shapes if s.has_text_frame]
            self.assertTrue(any(t.startswith("A / ") for t in text))
            self.assertTrue(any(t.startswith("B / ") for t in text))
