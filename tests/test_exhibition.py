import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile
from PIL import Image
from pptx import Presentation

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/joey-design'
sys.path.insert(0,str(SKILL/'scripts'))
from directions import build_directions
from joey import build
from studio import build_studio

class ExhibitionTests(unittest.TestCase):
    def test_proofs_are_distinct_and_rebuild(self):
        with TemporaryDirectory() as tmp:
            out=Path(tmp)/'proofs'
            brief=SKILL/'assets/studies/fold-deck.json'
            build_directions(brief,out)
            self.assertEqual(len(list(out.glob('*.jpg'))),12)
            self.assertEqual(len({p.read_bytes() for p in out.glob('zh-*-wide.jpg')}),3)
            with Image.open(out/'en-catalogue-portrait.jpg') as im:
                self.assertEqual(im.size,(900,1140))
            build_directions(brief,out)
    def test_native_deck_and_local_instrument(self):
        with TemporaryDirectory() as tmp:
            out=Path(tmp)/'deck'
            build(SKILL/'assets/studies/fold-deck.json',out)
            for lang in ('en','zh'):
                slide=Presentation(out/f'deck-{lang}.pptx').slides
                self.assertEqual(len(slide),5)
                self.assertTrue(all(s.has_notes_slide for s in slide))
                self.assertTrue(any(s.has_text_frame and '220 Hz' in s.text for s in slide[2].shapes))
            app=Path(tmp)/'app'
            build_studio(SKILL/'assets/studies/fold.json',app,'app')
            html=(app/'index.html').read_text()
            self.assertIn('AudioContext',html)
            self.assertIn('折频试听台</title>',html)
            self.assertIn('data:image/jpeg;base64,',html)
            social=Path(tmp)/'social'
            build_studio(SKILL/'assets/studies/fold.json',social,'social')
            with ZipFile(social/'images.zip') as pack:
                self.assertEqual(len([n for n in pack.namelist() if n.endswith('.jpg')]),5)
