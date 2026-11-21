"""Compose once in design pixels. PowerPoint, posters and HTML share these layers."""
import os
import re
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path
from PIL import ImageFont

from model import THEMES

FAMILIES = {"sans": "Arial", "bold": "Arial", "serif": "Georgia", "mono": "Courier New"}
CJK = re.compile(r"[\u2e80-\u9fff\uf900-\ufaff\u3000-\u303f\uff00-\uffef]")


@lru_cache(maxsize=None)
def face(style, zh):
    family = FAMILIES[style]
    defaults = {
        "bold": ("Arial Bold.ttf", "DejaVuSans-Bold.ttf", "arialbd.ttf"),
        "sans": ("Arial.ttf", "DejaVuSans.ttf", "arial.ttf"),
        "serif": ("Georgia.ttf", "DejaVuSerif.ttf", "georgia.ttf"),
        "mono": ("Courier New.ttf", "DejaVuSansMono.ttf", "cour.ttf"),
    }
    if zh:
        family = "Noto Serif CJK SC" if style == "serif" else "Noto Sans CJK SC"
        override = os.getenv("JOEY_CJK_FONT")
        if override and Path(override).is_file():
            return override, ImageFont.truetype(override, 20).getname()[0]
        options = ("NotoSerifCJK-Regular.ttc", "Songti.ttc") if style == "serif" else (
            "NotoSansCJK-Regular.ttc", "PingFang.ttc", "msyh.ttc", "Arial Unicode.ttf")
    else:
        options = defaults[style]
    dirs = [Path("/System/Library/Fonts/Supplemental"), Path("/System/Library/Fonts"),
            Path(os.getenv("WINDIR", "C:/Windows")) / "Fonts", Path("/usr/share/fonts/truetype/dejavu"),
            Path("/usr/share/fonts/opentype/noto")]
    for item in options:
        for directory in dirs:
            p = directory / item
            if p.is_file():
                return str(p), ImageFont.truetype(str(p), 20).getname()[0]
    if shutil.which("fc-match"):
        query = f"{family}:lang=zh-cn" if zh else family + (":style=Bold" if style == "bold" else "")
        result = subprocess.check_output(["fc-match", "-f", "%{file}", query], text=True)
        if Path(result).is_file():
            return result, ImageFont.truetype(result,20).getname()[0]
    raise ValueError("Install a Latin font and a Chinese font. Set JOEY_CJK_FONT to a CJK font file.")


@lru_cache(maxsize=512)
def font(style, zh, size):
    return ImageFont.truetype(face(style, zh)[0], size)


def lines_for(text, f, width):
    rows = []
    for paragraph in text.split("\n"):
        line = ""
        for part in re.findall(r"[\u2e80-\u9fff\uf900-\ufaff\u3000-\u303f\uff00-\uffef]|[^\s\u2e80-\u9fff\uf900-\ufaff\u3000-\u303f\uff00-\uffef]+|[ \t]+", paragraph):
            combined = line + part
            if line.strip() and f.getlength(combined.rstrip()) > width:
                # Keep closing punctuation with the preceding glyph where possible.
                if part in "，。；：！？）】》、" and len(line.rstrip()) >= 2:
                    old = line.rstrip()
                    rows.append(old[:-1])
                    line = old[-1] + part
                else:
                    rows.append(line.rstrip())
                    line = part.lstrip()
            else:
                line = combined
        rows.append(line.rstrip())
    return rows


class Canvas:
    def __init__(self, width, height, bg):
        self.width, self.height, self.bg = width, height, bg
        self.layers = []

    def rect(self, x, y, w, h, color):
        self.layers.append(dict(type="rect", x=x,y=y,w=w,h=h,color=color))

    def image(self, x, y, w, h, p):
        ratio = w / h
        variant = "wide" if ratio >= 2.4 else "portrait" if ratio < 0.95 else ""
        path = p["variants"].get(variant, p["photo"])
        self.layers.append(dict(type="image", x=x,y=y,w=w,h=h,path=path,alt=p["alt"]))

    def text(self, x,y,w,h,value,size,color,style="sans",minimum=None,leading=1.16):
        zh = bool(CJK.search(value))
        floor = minimum or size
        for px in range(size, floor-1, -1):
            f = font(style, zh, px)
            rows = lines_for(value, f, w*.97)
            pitch = round(px*leading)
            if len(rows)*pitch <= h and all(f.getlength(row) <= w*.99 for row in rows):
                self.layers.append(dict(type="text", x=x,y=y,w=w,h=h,rows=rows,size=px,
                                        pitch=pitch,style=style,color=color,zh=zh,
                                        family=face(style,zh)[1]))
                return
        raise ValueError(f"Text does not fit {w}×{h} at {floor}px. Shorten or split: {value[:100]}")


def compose(p, index):
    s = p["pages"][index]
    t = THEMES[p["theme"]]
    cover, feature, proof = (s["kind"] == k for k in ("cover", "feature", "proof"))
    heading = "serif" if t["face"] == "serif" else "bold"
    bg = t["paper"] if feature or proof else t["bg"]
    ink = t["dark"] if feature or proof else t["ink"]
    c = Canvas(1280, 720, bg)
    if cover:
        if p["theme"] == "folio":
            c.image(754,32,494,656,p)
            c.text(48,149,685,283,s["title"],116,ink,heading,62,1.04)
            c.text(52,470,630,112,s["body"],30,ink,minimum=23)
        elif p["theme"] == "signal":
            c.image(0,0,1280,330,p)
            c.text(42,342,1195,42,s["kicker"],22,ink,"mono",16)
            c.text(40,391,707,193,s["title"],94,ink,heading,48,1.04)
            c.text(776,398,450,185,s["body"],33,ink,minimum=23)
        else:
            c.image(599,0,681,720,p)
            c.rect(48,131,74,5,t["accent"])
            c.text(44,169,535,260,s["title"],113,ink,heading,56,1.04)
            c.text(49,465,500,114,s["body"],29,ink,minimum=21)
        if p["theme"] != "signal":
            c.text(49,49,525,52,s["kicker"],21,t["muted"],"mono",15)
    elif feature:
        c.text(48,43,1130,52,s["kicker"],19,ink,"mono",15)
        c.image(48,117,571,495,p)
        c.text(671,130,551,258,s["title"],67,ink,heading,40,1.1)
        c.text(674,411,531,195,s["body"],28,ink,minimum=21)
    elif proof:
        c.text(48,42,1150,48,s["kicker"],20,ink,"mono",15)
        c.text(45,106,1177,138,s["title"],74,ink,heading,40,1.06)
        c.text(50,260,1160,96,s["body"],26,ink,minimum=20)
        ids=s["facts"]
        width=1182/len(ids)
        for i,key in enumerate(ids):
            x=50+round(i*width)
            f=p["facts"][key]
            c.rect(x,384,int(width)-23,3,ink)
            c.text(x,415,int(width)-27,102,f["value"],77,ink,heading,35,1.05)
            c.text(x,531,int(width)-29,103,f["label"],24,ink,minimum=17)
    else:
        c.rect(48,115,1184,4,t["accent"])
        c.text(48,46,1150,54,s["kicker"],22,t["muted"],"mono",15)
        c.text(42,167,1188,237,s["title"],104,ink,heading,54,1.03)
        c.text(50,437,995,100,s["body"],30,ink,minimum=22)
        c.text(50,567,1165,69,p["action"],24,t["accent"],"bold",18)
    left = 49
    footer_w = 497 if cover and p["theme"]=="nocturne" else 658 if cover and p["theme"]=="folio" else 1160
    c.rect(left,654,footer_w,2,ink)
    c.text(left,670,footer_w-76,34,p["brand"],19,ink,"mono",14)
    c.text(left+footer_w-65,670,66,34,f"{index+1:02}/{len(p['pages']):02}",18,ink,"mono",14)
    return c


def poster(p):
    t=THEMES[p["theme"]]
    c=Canvas(1080,1440,t["bg"])
    s=p["pages"][0]
    ink=t["ink"]
    c.text(53,37,965,65,p["brand"],28,ink,"mono",18)
    if p["theme"] == "folio":
        c.rect(55,113,970,3,ink)
        c.text(49,150,970,270,s["title"],114,ink,"serif",58,1.04)
        c.image(54,457,972,705,p)
        c.text(56,1222,965,162,s["body"],40,ink,minimum=26)
    else:
        c.image(0,112,1080,712,p)
        c.text(51,874,972,56,s["kicker"],27,t["muted"],"mono",18)
        c.text(44,973,986,237,s["title"],112,ink,"bold",62,1.03)
        c.text(52,1268,955,130,s["body"],37,ink,minimum=25)
    return c
