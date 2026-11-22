"""Render the exact same canvas to raster, native Office shapes or semantic HTML."""
import base64
import html
import io
from functools import lru_cache
from PIL import Image, ImageDraw, ImageOps

from layout import font
from model import THEMES
from charts import add_office_chart, data_table, visual_bars

esc = html.escape


@lru_cache(maxsize=24)
def framed(path, w, h, fit="contain"):
    with Image.open(path) as raw:
        original = ImageOps.exif_transpose(raw).convert("RGB")
    if fit == "crop":
        out = io.BytesIO()
        ImageOps.fit(original,(w,h),method=Image.Resampling.LANCZOS).save(out,"JPEG",quality=90,optimize=True)
        return out.getvalue()
    # Preserve the silhouette of pack shots. Extend the adjacent edge into the bleed.
    inside = ImageOps.contain(original,(w,h),method=Image.Resampling.LANCZOS)
    iw,ih=inside.size
    x,y=(w-iw)//2,(h-ih)//2
    art=Image.new("RGB",(w,h))
    if y:
        art.paste(inside.crop((0,0,iw,1)).resize((w,y)),(0,0))
    if h-y-ih:
        art.paste(inside.crop((0,ih-1,iw,ih)).resize((w,h-y-ih)),(0,y+ih))
    if x:
        art.paste(inside.crop((0,0,1,ih)).resize((x,h)),(0,0))
    if w-x-iw:
        art.paste(inside.crop((iw-1,0,iw,ih)).resize((w-x-iw,h)),(x+iw,0))
    art.paste(inside,(x,y))
    out=io.BytesIO()
    art.save(out,"JPEG",quality=90,optimize=True)
    return out.getvalue()


def raster(c):
    im=Image.new("RGB",(c.width,c.height),c.bg)
    draw=ImageDraw.Draw(im)
    for n in c.layers:
        x,y,w,h=(n[k] for k in ("x","y","w","h"))
        if n["type"] == "chart":
            bars = visual_bars(n)
            bars.bg = c.bg
            im.paste(raster(bars), (x, y))
        elif n["type"]=="image":
            im.paste(Image.open(io.BytesIO(framed(n["path"],w,h,n.get("fit","contain")))),(x,y))
        elif n["type"]=="rect":
            draw.rectangle((x,y,x+w-1,y+h-1),fill=n["color"])
        else:
            f=font(n["style"],n["zh"],n["size"])
            for i,row in enumerate(n["rows"]):
                draw.text((x,y+i*n["pitch"]+int(n["size"]*.12)),row,font=f,fill=n["color"],anchor="lt")
    return im


def powerpoint(canvases, p, target):
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import MSO_AUTO_SIZE
    from pptx.oxml.xmlchemy import OxmlElement
    from pptx.oxml.ns import qn
    from pptx.opc.constants import RELATIONSHIP_TYPE as RT
    from pptx.util import Emu, Pt
    def unit(v): return Emu(round(v*9525))
    def rgb(v): return RGBColor.from_string(v[1:])
    deck=Presentation()
    deck.slide_width,deck.slide_height=unit(1280),unit(720)
    deck._element.sldSz.set("type", "screen16x9")
    deck.core_properties.author=p["brand"]
    deck.core_properties.title=p["pages"][0]["title"].replace("\n"," ")
    for c,page in zip(canvases,p["pages"]):
        slide=deck.slides.add_slide(deck.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb=rgb(c.bg)
        for n in c.layers:
            box=[unit(n[k]) for k in ("x","y","w","h")]
            if n["type"] == "chart":
                add_office_chart(slide, box, n)
            elif n["type"]=="image":
                picture=slide.shapes.add_picture(io.BytesIO(framed(n["path"],n["w"],n["h"],n.get("fit","contain"))),*box)
                picture._element.nvPicPr.cNvPr.set("descr",n["alt"])
            elif n["type"]=="rect":
                shape=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,*box)
                shape.fill.solid()
                shape.fill.fore_color.rgb=rgb(n["color"])
                shape.line.fill.background()
            else:
                shape=slide.shapes.add_textbox(*box)
                tf=shape.text_frame
                tf.auto_size=MSO_AUTO_SIZE.NONE
                tf.word_wrap=False
                tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
                for i,row in enumerate(n["rows"]):
                    para=tf.paragraphs[0] if i==0 else tf.add_paragraph()
                    para.space_before=para.space_after=Pt(0)
                    para.line_spacing=Pt(n["pitch"]*.75)
                    run=para.add_run()
                    run.text=row
                    run.font.name=n["family"]
                    run.font.bold=n["style"]=="bold"
                    run.font.size=Pt(n["size"]*.75)
                    run.font.color.rgb=rgb(n["color"])
                    east=OxmlElement("a:ea")
                    east.set("typeface",n["family"])
                    run._r.get_or_add_rPr().append(east)
                if page["kind"] == "close" and n["rows"] == [p["action"]]:
                    if p["url"] != "#sources":
                        shape.click_action.hyperlink.address = p["url"]
                    else:
                        proof = next((i for i, item in enumerate(p["pages"]) if item["kind"] in ("proof", "chart")), None)
                        if proof is not None:
                            shape.click_action.target_slide = deck.slides[proof]
        notes=page["notes"]
        if page["kind"] == "chart":
            notes += "\n" + page["chart"]["source"]
        if page["kind"]=="proof":
            notes+="\n"+"\n".join(f'{p["facts"][i]["value"]} — {p["facts"][i]["source"]}' for i in page["facts"])
        if page["kind"]=="close":
            notes+="\n"+p["url"]
        slide.notes_slide.notes_text_frame.text=notes
    # python-pptx creates the notes master relationship but omits its index.
    # Keynote requires the index, before the slide list, to import the file.
    master_list = OxmlElement("p:notesMasterIdLst")
    master = OxmlElement("p:notesMasterId")
    master.set(qn("r:id"), next(r.rId for r in deck.part.rels.values() if r.reltype == RT.NOTES_MASTER))
    master_list.append(master)
    deck._element.sldIdLst.addprevious(master_list)
    deck.save(target)


def uri(data):
    return "data:image/jpeg;base64,"+base64.b64encode(data).decode("ascii")


def section_html(c, title, nested=False, action_url=None, action_label=None):
    nodes=[]
    for n in c.layers:
        pos=(f'left:{n["x"]/c.width*100:.4f}%;top:{n["y"]/c.height*100:.4f}%;'
             f'width:{n["w"]/c.width*100:.4f}%;height:{n["h"]/c.height*100:.4f}%;')
        if n["type"] == "chart":
            data = data_table(n["data"])
            drawing = section_html(visual_bars(n), "", nested=True)
            nodes.append(f'<div class="chart" style="{pos}"><div aria-hidden="true">{drawing}</div><div class="sr-data">{data}</div></div>')
        elif n["type"]=="image":
            src=uri(framed(n["path"],n["w"],n["h"],n.get("fit","contain")))
            nodes.append(f'<img style="{pos}" alt="{esc(n["alt"])}" src="{src}">')
        elif n["type"]=="rect":
            nodes.append(f'<i aria-hidden="true" style="{pos}background:{n["color"]}"></i>')
        else:
            family=esc(n["family"])
            weight=700 if n["style"]=="bold" else 400
            fallback={"serif":"serif","mono":"monospace"}.get(n["style"],"sans-serif")
            style=(f"{pos}font-family:'{family}',{fallback};font-weight:{weight};"
                   f'font-size:{n["size"]/12.8:.5f}cqw;line-height:{n["pitch"]/12.8:.5f}cqw;color:{n["color"]};')
            value="<br>".join(esc(row) for row in n["rows"])
            if action_url and action_label and " ".join(n["rows"]).replace(" ", "") == action_label.replace(" ", ""):
                nodes.append(f'<a class="slide-action" style="{style}" href="{esc(action_url)}">{value}</a>')
            else:
                nodes.append(f'<div style="{style}">{value}</div>')
    if nested:
        return "".join(nodes)
    return f'<section class="slide" aria-label="{esc(title)}" style="background:{c.bg}">{"".join(nodes)}</section>'


def deck_html(canvases,p,assets):
    source_page = next((i for i, s in enumerate(p["pages"], 1) if s["kind"] in ("proof", "chart")), None)
    url = p["url"]
    if url == "#sources":
        url = f"#slide-{source_page}" if source_page else "#notes-panel"
    content = "".join(section_html(c, s["title"], action_url=url if s["kind"] == "close" else None,
                                   action_label=p["action"]) for c, s in zip(canvases, p["pages"]))
    en=p["lang"]=="en"
    note_items=[]
    for page in p["pages"]:
        source_items = []
        for key in page.get("facts", []):
            f=p["facts"][key]
            source_items.append(f'<li>{esc(f["label"])} · {esc(f["value"])} — {esc(f["source"])}</li>')
        action=""
        if page["kind"]=="close":
            if p["url"]=="#sources":
                source_items.extend(f'<li>{esc(f["value"])} — {esc(f["source"])}</li>' for f in p["facts"].values())
            else:
                action=f'<p><a href="{esc(p["url"])}">{esc(p["action"])}</a></p>'
        refs=f'<ul>{"".join(source_items)}</ul>' if source_items else ""
        note_items.append(f'<article hidden><p>{esc(page["notes"])}</p>{refs}{action}</article>')
    notes=''.join(note_items)
    title=esc(p["pages"][0]["title"].replace("\n"," "))
    return (f'<!doctype html><html lang="{p["lang"]}"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>'
            f'<style>{(assets/"deck.css").read_text(encoding="utf-8")}</style><main>{content}</main>'
            f'<nav aria-label="{"Presentation" if en else "演示导航"}"><button id="prev" aria-label="{"Previous" if en else "上一页"}">←</button>'
            f'<output aria-live="polite"></output><button id="next" aria-label="{"Next" if en else "下一页"}">→</button>'
            f'<button id="notes" aria-expanded="false" aria-controls="notes-panel">{"Notes" if en else "讲者备注"}</button></nav>'
            f'<aside id="notes-panel" hidden aria-label="{"Speaker notes" if en else "讲者备注"}">{notes}</aside>'
            f'<script>{(assets/"deck.js").read_text(encoding="utf-8")}</script></html>')


def sales_page(p,assets):
    t=THEMES[p["theme"]]
    cover=p["pages"][0]
    closing=p["pages"][-1]
    src=uri(framed(p["photo"],1200,800))
    switch="中文" if p["lang"]=="en" else "English"
    other="zh" if p["lang"]=="en" else "en"
    sources="Sources & credits" if p["lang"]=="en" else "资料来源与图像署名"
    def txt(s): return esc(s).replace("\n","<br>")
    sections=[]
    for slide in p["pages"][1:-1]:
        cards=""
        if slide["kind"]=="proof":
            cards="<dl>"+"".join(f'<div><dt>{txt(p["facts"][k]["label"])}</dt><dd>{txt(p["facts"][k]["value"])}</dd></div>' for k in slide["facts"])+"</dl>"
        if slide["kind"] == "chart":
            cards = data_table(slide["chart"]) + f'<p>{txt(slide["chart"]["source"])}</p>'
        if slide["kind"]=="spread":
            plates = []
            for plate in slide["plates"]:
                image = uri(framed(plate["photo"],700,400,"crop"))
                plates.append(f'<figure style="margin:0"><img src="{image}" alt="{esc(plate["alt"])}" style="width:100%"><figcaption>{txt(plate["label"])}</figcaption></figure>')
            cards='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,210px),1fr));gap:16px;margin-top:22px">'+''.join(plates)+'</div>'
        sections.append(f'<section class="story"><p class="k">{txt(slide["kicker"])}</p><div><h2>{txt(slide["title"])}</h2><p>{txt(slide["body"])}</p>{cards}</div></section>')
    references="".join(f'<li><strong>{txt(f["label"])} · {txt(f["value"])}</strong><br>{txt(f["source"])}</li>' for f in p["facts"].values())
    colors=";".join(f"--{k}:{v}" for k,v in t.items() if k!="face")
    titlefont="Georgia,serif" if p["theme"]=="folio" else "Arial,sans-serif"
    return f"""<!doctype html><html lang="{p['lang']}"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(cover['title'].replace(chr(10),' '))}</title>
<style>:root{{{colors};--head:{titlefont}}}{(assets/'page.css').read_text(encoding='utf-8')}</style>
<header><b>{txt(p['brand'])}</b><a lang="{other}" hreflang="{other}" href="page-{other}.html">{switch}</a></header>
<main><section class="hero"><div><p class="k">{txt(cover['kicker'])}</p><h1>{txt(cover['title'])}</h1><p>{txt(cover['body'])}</p></div><img src="{src}" alt="{esc(p['alt'])}"></section>
{''.join(sections)}<section class="finish"><p class="k">{txt(closing['kicker'])}</p><h2>{txt(closing['title'])}</h2><p>{txt(closing['body'])}</p><a class="cta" href="{esc(p['url'])}">{txt(p['action'])} ↗</a></section></main>
<footer id="sources" tabindex="-1"><h2>{sources}</h2><ul>{references}</ul><p>{txt(p['credit'])}</p></footer></html>"""
