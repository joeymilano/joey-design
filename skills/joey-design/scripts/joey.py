"""Build both language editions locally. Run joey.py --help for usage."""
import argparse
import json
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


def copy_issues(value, path="$"):
    """Locate Chinese full stops without modifying the author's text."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"en", "file", "url", "action_url"}:
                continue
            yield from copy_issues(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from copy_issues(child, f"{path}[{index}]")
    elif isinstance(value, str) and "。" in value and not value.startswith(("https://", "http://", "data:")):
        yield path


def main():
    parser=argparse.ArgumentParser(description="Build a bilingual design kit from one creative brief.")
    parser.add_argument("command",choices=["build","check","social","app","directions","scenario","copycheck","ui","site","game"])
    parser.add_argument("brief",type=Path)
    parser.add_argument("--out",type=Path,default=None)
    args=parser.parse_args()
    try:
        if args.command in ("ui", "site", "game"):
            from projects import build_project
            dest = args.out or Path("joey-" + args.command)
            build_project(args.command, args.brief, dest)
            print(f"Open {dest / 'index.html'}")
            return
        if args.command == "copycheck":
            fields = list(copy_issues(json.loads(args.brief.read_text(encoding="utf-8"))))
            if fields:
                raise ValueError("Chinese full stops found in " + ", ".join(fields))
            print("Chinese copy contains no full stops")
            return
        if args.command == "scenario":
            from scenarios import build_scenario
            dest = args.out or Path("joey-scenario")
            build_scenario(args.brief, dest)
            print(f"Open {dest / 'index.html'}")
            return
        if args.command == "directions":
            from directions import build_directions
            dest = args.out or Path("joey-directions")
            build_directions(args.brief,dest)
            print(f"Built 12 cover studies in {dest}")
            return
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
