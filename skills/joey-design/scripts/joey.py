"""Build both language editions locally. Run joey.py --help for usage."""
import argparse
import os
import tempfile
from pathlib import Path

from layout import compose, poster
from model import load_brief
from render import deck_html, powerpoint, raster, sales_page

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def build(source, dest, check=False):
    editions=load_brief(source)
    canvases={lang: [compose(p,i) for i in range(len(p["pages"]))] for lang,p in editions.items()}
    posters={lang: poster(p) for lang,p in editions.items()}
    if check:
        for p in editions.values():
            from PIL import Image
            plates = [plate["photo"] for page in p["pages"] for plate in page.get("plates", [])]
            for path in (p["photo"], *p["variants"].values(), *plates):
                with Image.open(path) as art:
                    art.verify()
        return
    dest=Path(dest).resolve()
    if dest.exists() and (not dest.is_dir() or any(dest.iterdir()) and not (dest/".joey-output").is_file()):
        raise ValueError("Choose a new/empty output directory or a previous Joey Design build.")
    dest.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".joey-",dir=dest.parent) as tmp:
        stage=Path(tmp)
        for lang,p in editions.items():
            slides=canvases[lang]
            (stage/f"deck-{lang}.html").write_text(deck_html(slides,p,ASSETS),encoding="utf-8")
            (stage/f"page-{lang}.html").write_text(sales_page(p,ASSETS),encoding="utf-8")
            powerpoint(slides,p,stage/f"deck-{lang}.pptx")
            raster(posters[lang]).save(stage/f"cover-{lang}.png")
            raster(slides[0]).save(stage/f"wide-{lang}.png")
        (stage/".joey-output").write_text("Joey Design build directory\n",encoding="utf-8")
        dest.mkdir(exist_ok=True)
        for item in stage.iterdir():
            os.replace(item,dest/item.name)


def main():
    parser=argparse.ArgumentParser(description="Build a bilingual design kit from one creative brief.")
    parser.add_argument("command",choices=["build","check","social","app"])
    parser.add_argument("brief",type=Path)
    parser.add_argument("--out",type=Path,default=None)
    args=parser.parse_args()
    try:
        if args.command in ("social","app"):
            from studio import build_studio
            dest = args.out or Path("joey-" + args.command)
            count = build_studio(args.brief, dest, args.command)
            print(f"Built {count} files in {dest}")
            return
        args.out = args.out or Path("joey-build")
        build(args.brief,args.out,check=args.command=="check")
    except (ValueError,TypeError,KeyError,AttributeError,OSError,ImportError) as e:
        parser.exit(2,f"joey-design: {e}\n")
    print("Both editions passed layout checks." if args.command=="check" else f"Built 10 files in {args.out}")


if __name__=="__main__":
    main()
