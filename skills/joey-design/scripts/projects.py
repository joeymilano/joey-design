"""Build standalone product, portfolio and game examples from editable briefs."""
import json
import re
import tempfile
from collections import deque
from html import escape
from pathlib import Path

from PIL import Image, ImageOps
from studio import ASSETS, ID, jpeg, required, uri


def shortest_route(rows):
    """Visit every boarding stop before docking. Walls never consume a move."""
    if not isinstance(rows, list) or not 2 <= len(rows) <= 12 or not all(
        isinstance(row, str) and 2 <= len(row) <= 12 and re.fullmatch(r"[.#SBE]+", row)
        for row in rows
    ) or len({len(row) for row in rows}) != 1:
        raise ValueError("Use a rectangular 2–12 cell map with . # S B E")
    tiles = "".join(rows)
    if tiles.count("S") != 1 or tiles.count("E") != 1 or not 1 <= tiles.count("B") <= 5:
        raise ValueError("A map needs one start, one exit and 1–5 stops")
    width = len(rows[0])
    bits = {n: 1 << i for i, n in enumerate(n for n, c in enumerate(tiles) if c == "B")}
    full = (1 << len(bits)) - 1
    start = tiles.index("S")
    queue = deque([(start, 0, 0)])
    seen = {(start, 0)}
    while queue:
        pos, mask, distance = queue.popleft()
        if tiles[pos] == "E" and mask == full:
            return distance
        y, x = divmod(pos, width)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            xx, yy = x + dx, y + dy
            if not (0 <= xx < width and 0 <= yy < len(rows)) or rows[yy][xx] == "#":
                continue
            dest = yy * width + xx
            state = dest, mask | bits.get(dest, 0)
            if state not in seen:
                seen.add(state)
                queue.append((*state, distance + 1))
    raise ValueError("A stop or exit cannot be reached")


def build_project(mode, source, dest):
    if mode not in ("game", "site", "ui"):
        raise ValueError("Choose game, site or ui")
    source = Path(source).resolve()
    data = json.loads(source.read_text(encoding="utf8"))
    required(data, "id title mast intro credit", "brief")
    if not ID.fullmatch(data["id"]):
        raise ValueError("Use a lowercase project id")
    images = {}
    def asset(entry, key):
        path = (source.parent / entry[key]).resolve()
        if not path.is_relative_to(source.parent) or not path.is_file():
            raise ValueError(f"Missing local artwork: {entry[key]}")
        if entry[key] not in images:
            with Image.open(path) as raw:
                photo = ImageOps.exif_transpose(raw).convert("RGB")
                photo.thumbnail((1500, 1050))
                images[entry[key]] = uri(jpeg(photo, 84))
    if mode == "game":
        required(data, "image alt", "game")
        asset(data, "image")
        levels = data.get("levels")
        if not isinstance(levels, list) or not 1 <= len(levels) <= 20:
            raise ValueError("Provide 1–20 levels")
        for level in levels:
            required(level, "name", "level")
            minimum = shortest_route(level.get("map"))
            if type(level.get("budget")) is not int or not minimum <= level["budget"] <= 500:
                raise ValueError(f"{level['name']} needs a move budget of at least {minimum} and at most 500")
    else:
        items = data.get("items")
        if not isinstance(items, list) or not 1 <= len(items) <= 80:
            raise ValueError("Provide 1–80 projects or frames")
        seen = set()
        for item in items:
            required(item, "id title series image alt note", "item")
            if not ID.fullmatch(item["id"]) or item["id"] in seen:
                raise ValueError("Use unique lowercase item ids")
            seen.add(item["id"])
            asset(item, "image")
            if mode == "site":
                required(item, "detail detail_alt detail_note", "project")
                asset(item, "detail")
    data["art"] = images
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = (ASSETS / "lab" / f"{mode}.html").read_text(encoding="utf8")
    parts = {"TITLE": escape(data["title"]), "BRIEF": payload}
    page = re.sub(r"@@(TITLE|BRIEF)@@", lambda match: parts[match[1]], template)
    dest = Path(dest).resolve()
    marker = dest / ".joey-project"
    key = f"{mode}/{data['id']}"
    if dest.exists() and (not dest.is_dir() or any(dest.iterdir()) and
                          (not marker.is_file() or marker.read_text() != key)):
        raise ValueError("Choose a new directory or the previous output of this project")
    dest.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=dest) as tmp:
        for name, content in [("index.html", page), (marker.name, key)]:
            p = Path(tmp) / name
            p.write_text(content, encoding="utf8")
            p.replace(dest / name)
