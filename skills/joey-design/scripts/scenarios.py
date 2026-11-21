"""Compile a buying sheet, channel report or workshop programme to offline HTML."""
import json
import re
import tempfile
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from PIL import Image, ImageOps
from studio import ASSETS, ID, jpeg, required, uri

TEMPLATES = ASSETS / "scenarios"
KINDS = {"samples", "report", "agenda"}


def instant(value):
    moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if moment.utcoffset() is None:
        raise ValueError("Each session time needs a UTC offset")
    return moment.astimezone(timezone.utc)


def load_scenario(source):
    source = Path(source).resolve()
    data = json.loads(source.read_text(encoding="utf-8"))
    required(data, "kind id title edition headline intro source", "brief")
    kind = data["kind"]
    if kind not in KINDS or not ID.fullmatch(data["id"]):
        raise ValueError("Use samples, report or agenda and a lowercase project id")
    if kind == "samples":
        required(data, "image alt", "brief")
        path = (source.parent / data["image"]).resolve()
        if not path.is_relative_to(source.parent) or not path.is_file():
            raise ValueError("Provide a local image beside the brief")
        with Image.open(path) as im:
            photo = ImageOps.exif_transpose(im)
            photo.thumbnail((1400, 1400))
            data["image"] = uri(jpeg(photo, 83))
    if kind == "report":
        required(data, "previous current", "brief")
        defaults = {"visits": "访问", "actions": "询盘", "rate": "询盘率"}
        labels = data.setdefault("metrics", defaults)
        required(labels, "visits actions rate", "metrics")
    if kind == "agenda":
        required(data, "timezone", "brief")
        try:
            ZoneInfo(data["timezone"])
        except ZoneInfoNotFoundError as e:
            raise ValueError("Use a named IANA timezone") from e
    items = data.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= 100:
        raise ValueError("Supply 1 to 100 items")
    ids = set()
    for item in items:
        required(item, "id name", "item")
        if not ID.fullmatch(item["id"]) or item["id"] in ids:
            raise ValueError("Item IDs must be unique lowercase slugs")
        ids.add(item["id"])
        if kind == "samples":
            required(item, "code color spec note", "sample")
            if not re.fullmatch(r"#[0-9a-fA-F]{6}", item["color"]):
                raise ValueError("Use a six-digit hex swatch color")
        elif kind == "report":
            for period in ("previous", "current"):
                pair = item.get(period)
                if not isinstance(pair, list) or len(pair) != 2 or any(type(n) is not int or not 0 <= n <= 10**12 for n in pair):
                    raise ValueError("Each period needs nonnegative integer visits and enquiries")
                if pair[1] > pair[0]:
                    raise ValueError("Enquiries cannot exceed visits under this definition")
        else:
            required(item, "track place start end note", "session")
            if instant(item["end"]) <= instant(item["start"]):
                raise ValueError("Session end must follow start")
    if kind == "agenda":
        items.sort(key=lambda item: instant(item["start"]))
    return data


def build_scenario(source, dest):
    data = load_scenario(source)
    dest = Path(dest).resolve()
    marker = dest / ".joey-scenario"
    identity = f"{data['kind']}/{data['id']}"
    if dest.exists() and (not dest.is_dir() or any(dest.iterdir()) and
                          (not marker.is_file() or marker.read_text() != identity)):
        raise ValueError("Use a new directory or the previous output of this scenario")
    template = (TEMPLATES / "page.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    parts = {"LANG": "en" if data["kind"] == "samples" else "zh-CN",
             "KIND": data["kind"], "TITLE": escape(data["title"]), "DATA": payload,
             "STYLE": (TEMPLATES / "scenes.css").read_text(encoding="utf-8"),
             "LOGIC": (TEMPLATES / "scenes.js").read_text(encoding="utf-8")}
    page = re.sub(r"@@(LANG|KIND|TITLE|DATA|STYLE|LOGIC)@@", lambda m: parts[m[1]], template)
    dest.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=dest) as tmp:
        for name, value in [("index.html", page), (marker.name, identity)]:
            path = Path(tmp) / name
            path.write_text(value, encoding="utf-8")
            path.replace(dest / name)
