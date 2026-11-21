"""Read a bilingual creative brief and resolve facts before any renderer runs."""
import re
import json
from pathlib import Path
from urllib.parse import urlsplit

LANGS = ("en", "zh")
THEMES = {
    "plate": dict(bg="#ef3212", ink="#fffaf2", muted="#fff2de", accent="#152bb2", paper="#f4f1e9", dark="#111111", face="sans"),
    "gallery": dict(bg="#ecece1", ink="#17271e", muted="#4a584e", accent="#315b39", paper="#f3f2e9", dark="#17271e", face="sans"),
    "nocturne": dict(bg="#10161e", ink="#fcf6e9", muted="#b9c4ce", accent="#f8b86c", paper="#f4efe5", dark="#182029", face="sans"),
    "folio": dict(bg="#f3ead8", ink="#2d241f", muted="#67574d", accent="#8f3528", paper="#ece1c9", dark="#2d241f", face="serif"),
    "signal": dict(bg="#e4efbf", ink="#162a26", muted="#48573f", accent="#235c4b", paper="#f2f4df", dark="#162a26", face="sans"),
}
TOKEN = re.compile(r"\{\{([a-zA-Z][\w-]*)\}\}")


def field(obj, key, where):
    if not isinstance(obj, dict) or key not in obj:
        raise ValueError(f"{where}: missing {key}")
    return obj[key]


def string(value, where):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where}: expected non-empty text")
    return value.strip()


def pair(value, where):
    return {lang: string(field(value, lang, where), f"{where}.{lang}") for lang in LANGS}


def load_brief(path):
    path = Path(path).resolve()
    data = json.loads(path.read_text(encoding="utf-8"))
    theme = field(data, "theme", "brief")
    if theme not in THEMES:
        raise ValueError(f"theme must be one of {', '.join(THEMES)}")
    brand = string(field(data, "brand", "brief"), "brand")
    artwork = field(data, "artwork", "brief")
    file = (path.parent / string(field(artwork, "file", "artwork"), "artwork.file")).resolve()
    if not file.is_relative_to(path.parent) or not file.is_file():
        raise ValueError("artwork.file must name a file inside the brief directory")
    variants = {}
    for shape in ("wide", "portrait"):
        if shape in artwork:
            variant = (path.parent / string(artwork[shape], f"artwork.{shape}")).resolve()
            if not variant.is_relative_to(path.parent) or not variant.is_file():
                raise ValueError(f"artwork.{shape} must name a file inside the brief directory")
            variants[shape] = variant
    alt = pair(field(artwork, "alt", "artwork"), "artwork.alt")
    detail_alt = pair(artwork.get("detail_alt",artwork["alt"]), "artwork.detail_alt")
    credit = pair(field(artwork, "credit", "artwork"), "artwork.credit")
    facts = field(data, "facts", "brief")
    if not isinstance(facts, dict) or not 1 <= len(facts) <= 6:
        raise ValueError("Provide 1–6 sourced facts")
    canonical = {}
    for key, fact in facts.items():
        if not re.fullmatch(r"[a-zA-Z][\w-]*", key):
            raise ValueError(f"Invalid fact ID {key!r}")
        canonical[key] = dict(value=string(field(fact, "value", key), key),
                              label=pair(field(fact, "label", key), key),
                              source=pair(field(fact, "source", key), key))
    url = string(field(data, "action_url", "brief"), "action_url")
    dest = urlsplit(url)
    if not (url == "#sources" or (dest.scheme == "https" and dest.hostname)
            or (dest.scheme == "mailto" and "@" in dest.path)):
        raise ValueError("action_url must be #sources, an HTTPS link or a mailto address")
    slides = field(data, "slides", "brief")
    if not isinstance(slides, list) or not 3 <= len(slides) <= 16:
        raise ValueError("A deck needs 3–16 slides")
    if slides[0].get("kind") != "cover" or slides[-1].get("kind") != "close":
        raise ValueError("Open with a cover and finish with a close")
    localized = {}
    for lang in LANGS:
        def resolve(obj, key, where):
            raw = pair(field(obj, key, where), f"{where}.{key}")[lang]
            def replacement(match):
                fact_id = match[1]
                if fact_id not in canonical:
                    raise ValueError(f"{where}.{key}: unknown fact {fact_id!r}")
                return canonical[fact_id]["value"]
            result = TOKEN.sub(replacement, raw)
            if "{{" in result or "}}" in result:
                raise ValueError(f"{where}.{key}: malformed fact reference")
            return result
        pages = []
        for i, slide in enumerate(slides):
            where = f"slides[{i}]"
            kind = field(slide, "kind", where)
            if kind not in ("cover", "feature", "proof", "spread", "close"):
                raise ValueError(f"{where}: unsupported layout {kind}")
            if (kind == "cover" and i != 0) or (kind == "close" and i != len(slides)-1):
                raise ValueError(f"{where}: cover/close must be at the ends")
            page = {k: resolve(slide, k, where) for k in ("kicker", "title", "body", "notes")}
            page["kind"] = kind
            if kind == "spread":
                plates = field(slide, "plates", where)
                if not isinstance(plates,list) or len(plates) != 2:
                    raise ValueError(f"{where}.plates needs two photographs")
                page["plates"] = []
                for plate in plates:
                    file_name = string(field(plate, "file", where), where)
                    local = (path.parent / file_name).resolve()
                    if not local.is_relative_to(path.parent) or not local.is_file():
                        raise ValueError(f"Missing local plate: {file_name}")
                    page["plates"].append(dict(photo=local, variants={}, fit="crop",
                        alt=resolve(plate, "alt", where), label=resolve(plate, "label", where)))
            if kind == "proof":
                ids = field(slide, "facts", where)
                if not isinstance(ids, list) or not 1 <= len(ids) <= 3 or any(k not in canonical for k in ids):
                    raise ValueError(f"{where}.facts needs 1–3 existing fact IDs")
                page["facts"] = ids
            pages.append(page)
        localized[lang] = dict(lang=lang, brand=brand, theme=theme, photo=file, variants=variants, alt=alt[lang], detail_alt=detail_alt[lang],
                               credit=credit[lang], action=resolve(data, "action", "brief"), url=url,
                               facts={k: {a: (v[lang] if isinstance(v,dict) else v) for a,v in f.items()}
                                      for k,f in canonical.items()}, pages=pages)
    return localized
