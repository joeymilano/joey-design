"""Export three cover studies from the same bilingual brief and original art."""
from pathlib import Path
from tempfile import TemporaryDirectory
from layout import Canvas
from model import load_brief, THEMES
from plates import INK, PAPER, plate, score
from render import raster

SHOTS=("field","catalogue","detail")


def covers(p):
    art={"photo":p["photo"],"alt":p["alt"]}
    detail={"photo":p["variants"].get("portrait",p["photo"]),"alt":p["detail_alt"]}
    s=p["pages"][0]
    for name in SHOTS:
        for portrait in (False,True):
            w,h=(900,1140) if portrait else (1440,800)
            c=Canvas(w,h,PAPER)
            if name=="field":
                if portrait:
                    plate(c,art,(0,286,w,h-286))
                    c.rect(0,0,w,286,INK)
                    c.text(33,28,w-65,43,p["brand"],22,PAPER,"mono",16)
                    c.text(29,91,w-50,155,s["title"].replace("\n"," "),105,PAPER,"bold",52,1.03)
                    c.rect(0,h-96,w,96,INK)
                    c.text(34,h-72,w-55,64,s["body"],30,PAPER,"bold",19)
                else:
                    plate(c,art,(0,0,w,h))
                    c.text(47,37,815,55,p["brand"],26,PAPER,"mono",18)
                    c.text(37,126,777,407,s["title"],170,PAPER,"bold",76,.99)
                    c.text(50,577,436,89,s["body"],32,PAPER,"bold",23)
            elif name=="catalogue":
                accent=THEMES[p["theme"]]["dark"]
                if portrait:
                    c.text(33,36,w-68,52,p["brand"],25,INK,"mono",16)
                    c.text(27,133,w-65,294,s["title"],130,accent,"bold",66,1.02)
                    plate(c,art,(35,492,w-70,405))
                    c.text(36,948,w-85,145,s["body"],40,INK,minimum=25)
                else:
                    c.text(44,36,1190,54,p["brand"],25,INK,"mono",16)
                    c.rect(45,98,w-90,2,INK)
                    c.text(36,166,689,362,s["title"],143,accent,"bold",66,1.01)
                    plate(c,art,(779,191,613,361))
                    c.text(48,596,1004,96,s["body"],34,INK,minimum=23)
                    score(c,48,718,1338,32,INK)
            else:
                plate(c,detail,(0,0,w,h))
                strip=345 if portrait else 188
                c.rect(0,h-strip,w,strip,INK)
                if portrait:
                    c.text(32,h-strip+25,w-65,62,p["brand"],25,PAPER,"mono",16)
                    c.text(26,h-strip+110,w-56,175,s["title"].replace("\n"," "),104,PAPER,"bold",48,1.05)
                else:
                    c.text(33,h-strip+30,880,135,s["title"].replace("\n"," "),105,PAPER,"bold",49,1.03)
                    c.text(975,h-strip+47,410,100,s["body"],26,PAPER,minimum=18)
            yield f"{name}-{'portrait' if portrait else 'wide'}.jpg",c


PROOF_ROOM = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>封面校样 / Cover proofs</title>
<style>*{box-sizing:border-box}body{margin:4%;background:#171819;color:#f6f4eb;font:16px/1.4 system-ui,sans-serif}header,main{max-width:1800px;margin:auto}header{display:flex;justify-content:space-between;align-items:center;gap:15px;flex-wrap:wrap}h1{font-size:clamp(28px,4vw,64px);letter-spacing:-.06em;margin:0}label{display:inline-flex;align-items:center;gap:6px;margin:5px}select{padding:8px;font:inherit}main{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1.5%;margin-top:25px}figure{margin:0}img{width:100%;height:auto;display:block}figcaption{margin:9px 0 20px}@media(max-width:650px){main{grid-template-columns:1fr;gap:18px}}</style>
<header><h1>封面校样</h1><div><label>语言 <select id="lang"><option value="zh">中文</option><option value="en">English</option></select></label><label>画幅 <select id="ratio"><option value="wide">横版</option><option value="portrait">竖版</option></select></label></div></header>
<main><figure><img src="zh-field-wide.jpg" data-name="field" alt="场域版封面"><figcaption>场域 / Field</figcaption></figure><figure><img src="zh-catalogue-wide.jpg" data-name="catalogue" alt="图录版封面"><figcaption>图录 / Catalogue</figcaption></figure><figure><img src="zh-detail-wide.jpg" data-name="detail" alt="微距版封面"><figcaption>微距 / Detail</figcaption></figure></main>
<script>const language=document.querySelector('#lang'),ratio=document.querySelector('#ratio');function update(){document.querySelectorAll('[data-name]').forEach(img=>img.src=[language.value,img.dataset.name,ratio.value].join('-')+'.jpg')}language.onchange=ratio.onchange=update;</script></html>'''


def build_directions(path, dest):
    editions=load_brief(path)
    dest=Path(dest).resolve()
    marker=dest/".joey-directions"
    if dest.exists() and (not dest.is_dir() or (any(dest.iterdir()) and not marker.is_file())):
        raise ValueError("Choose an empty directory or a previous directions build")
    dest.parent.mkdir(parents=True,exist_ok=True)
    with TemporaryDirectory(dir=dest.parent) as temp:
        tmp=Path(temp)
        for language,p in editions.items():
            for name,canvas in covers(p):
                raster(canvas).save(tmp/f"{language}-{name}",quality=90,optimize=True)
        (tmp/"index.html").write_text(PROOF_ROOM,encoding="utf8")
        (tmp/marker.name).write_text("Joey Design cover studies\n",encoding="utf8")
        dest.mkdir(exist_ok=True)
        for f in tmp.iterdir():
            f.replace(dest/f.name)
