"""Build an editorial carousel or a standalone mobile prototype from a studio brief."""
import base64
from html import escape
import io
import json
from pathlib import Path
import re
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageOps

from carousel import make_card

ASSETS = Path(__file__).resolve().parents[1] / "assets"
ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def required(obj, keys, location):
    if not isinstance(obj, dict):
        raise ValueError(f"{location} must be an object")
    for key in keys.split():
        if not isinstance(obj.get(key), str) or not obj[key].strip():
            raise ValueError(f"{location}.{key} needs text")


def strings(values, low, high, location):
    if not isinstance(values, list) or not low <= len(values) <= high or not all(isinstance(v,str) and v.strip() for v in values):
        raise ValueError(f"{location} needs {low}–{high} nonempty strings")


def load(path, mode):
    path = Path(path).resolve()
    data = json.loads(path.read_text(encoding="utf8"))
    required(data, "id brand imprint theme credit", "brief")
    if not ID.fullmatch(data["id"]) or data["theme"] not in ("daylight","afterdark","plate"):
        raise ValueError("Use a lowercase slug for id and daylight, afterdark or plate for theme")
    images = data.get("images")
    if not isinstance(images, dict) or not images:
        raise ValueError("Provide at least one image")
    for key, image in images.items():
        required(image, "file alt", f"images.{key}")
        resolved = (path.parent / image["file"]).resolve()
        if not resolved.is_relative_to(path.parent) or not resolved.is_file():
            raise ValueError(f"Missing local image: {image['file']}")
        image["path"] = resolved

    def image_ref(obj, key):
        if obj.get(key) not in images:
            raise ValueError(f"Unknown image in {key}: {obj.get(key)}")

    if mode == "social":
        social = data.get("social")
        required(social, "title caption", "social")
        pages = social.get("pages")
        if not isinstance(pages,list) or not 2 <= len(pages) <= 12:
            raise ValueError("Provide 2–12 carousel pages")
        for i,page in enumerate(pages):
            required(page, "layout title tag", f"social.pages[{i}]")
            kind = page["layout"]
            if kind not in ("cover","frame","split","pair","list"):
                raise ValueError(f"Unknown carousel layout {kind}")
            if kind == "list":
                strings(page.get("points"),2,3,"points")
            else:
                required(page,"body",f"social.pages[{i}]")
                image_ref(page,"image")
            if kind == "pair":
                image_ref(page,"second")
                strings(page.get("labels"),2,2,"labels")
        if pages[0]["layout"] != "cover":
            raise ValueError("Start the carousel with a cover")
    elif mode == "app":
        app = data.get("app")
        required(app, "mode title subtitle", "app")
        if app["mode"] == "instrument":
            required(app, "hero", "app")
            image_ref(app, "hero")
            return data
        required(app, "home saved action undo list detail", "app")
        if app["mode"] not in ("collect","reserve"):
            raise ValueError("app.mode must be collect, reserve or instrument")
        items = app.get("items")
        if not isinstance(items,list) or not 1 <= len(items) <= 30:
            raise ValueError("Supply 1–30 app items")
        ids = set()
        for item in items:
            required(item, "id category title meta body", "app item")
            if item["id"] in ids or not ID.fullmatch(item["id"]):
                raise ValueError("Item IDs must be unique lowercase slugs")
            ids.add(item["id"])
            image_ref(item,"image")
            if not isinstance(item.get("facts"),list) or not 1 <= len(item["facts"]) <= 5:
                raise ValueError("Each app item needs 1–5 detail facts")
            for fact in item["facts"]:
                strings(fact,2,2,"detail fact")
            if app["mode"] == "reserve":
                strings(item.get("slots"),1,8,"slots")
                if len(set(item["slots"])) != len(item["slots"]):
                    raise ValueError("Slot labels must be unique per item")
    else:
        raise ValueError("Choose social or app")
    return data


def uri(blob):
    return "data:image/jpeg;base64," + base64.b64encode(blob).decode("ascii")


def jpeg(im, quality=91):
    stream = io.BytesIO()
    im.convert("RGB").save(stream, "JPEG", quality=quality, optimize=True)
    return stream.getvalue()


def markup(template, payload, title):
    js = json.dumps(payload,ensure_ascii=False).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    return (ASSETS / template).read_text(encoding="utf8").replace("{{TITLE}}",escape(" ".join(title.split()))).replace("{{DATA}}",js)


def app_files(data):
    images = {}
    for key, entry in data["images"].items():
        with Image.open(entry["path"]) as raw:
            image = ImageOps.exif_transpose(raw).convert("RGB")
            image.thumbnail((1500,1500),Image.Resampling.LANCZOS)
            images[key] = {"src":uri(jpeg(image)), "alt":entry["alt"]}
    payload = {k:data[k] for k in ("brand","theme","imprint","id","credit","app")}
    payload["images"] = images
    template = "instrument.html" if data["app"]["mode"] == "instrument" else "mobile.html"
    title = data["brand"] + " · " + data["app"]["title"]
    return {"index.html":markup(template,payload,title).encode("utf8")}


def social_files(data):
    out, pages = {}, []
    social = data["social"]
    for i,page in enumerate(social["pages"],1):
        pixels = make_card(data,page,i,len(social["pages"]))
        name = f'{data["id"]}-{i:02}.jpg'
        blob = jpeg(pixels,93)
        out[name] = blob
        alt = page["title"].replace("\n"," ") + "。" + page.get("body","")
        for key in ("image","second"):
            if key in page:
                alt += " " + data["images"][page[key]]["alt"]
        if page["layout"] == "list":
            alt += " " + " ".join(page["points"])
        pages.append({"name":name,"src":uri(blob),"alt":alt})
    caption = social["title"]+"\n\n"+social["caption"]+"\n"
    out["caption.txt"] = caption.encode("utf8")
    archive = io.BytesIO()
    with ZipFile(archive,"w",compression=ZIP_DEFLATED) as bundle:
        for name, blob in out.items():
            bundle.writestr(name,blob)
        bundle.writestr("credits.txt",data["credit"]+"\n")
    out["images.zip"] = archive.getvalue()
    out["index.html"] = markup("carousel.html",dict(brand=data["brand"],imprint=data["imprint"],credit=data["credit"],
        title=social["title"],pages=pages,caption=caption),social["title"]).encode("utf8")
    return out


def build_studio(path, dest, mode):
    data = load(path,mode)
    dest = Path(dest).resolve()
    marker = ".joey-studio"
    identity = mode + "/" + data["id"]
    if dest.exists() and (not dest.is_dir() or any(dest.iterdir()) and
            (not (dest/marker).is_file() or (dest/marker).read_text(encoding="utf8") != identity)):
        raise ValueError("Use a new folder or the previous output of this same study and format")
    files = social_files(data) if mode == "social" else app_files(data)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=dest.parent) as work:
        stage = Path(work)
        for name,blob in files.items():
            (stage/name).write_bytes(blob)
        (stage/marker).write_text(identity,encoding="utf8")
        dest.mkdir(exist_ok=True)
        for file in stage.iterdir():
            file.replace(dest/file.name)
        # Rebuilding a shorter carousel should remove only its obsolete numbered exports.
        if mode == "social":
            for old in dest.glob(data["id"]+"-[0-9][0-9].jpg"):
                if old.name not in files:
                    old.unlink()
    return len(files)
