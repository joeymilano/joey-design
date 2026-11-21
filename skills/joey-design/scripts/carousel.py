"""Five editorial compositions for 3:4 image notes."""
from PIL import Image, ImageOps, ImageDraw
from layout import Canvas, font

W, H = 1080, 1440


def make_card(data, page, index, total):
    night = data["theme"] == "afterdark"
    paper, ink = ("#eae0c6","#251910") if night else ("#edece2","#17241f")
    accent = "#b03e2f" if night else "#b0ef70"
    dark = "#201814" if night else "#183025"
    c = Canvas(W,H,paper)
    im = Image.new("RGB",(W,H),paper)
    draw = ImageDraw.Draw(im)
    def photo(key, box):
        x,y,w,h = box
        with Image.open(data["images"][page[key]]["path"]) as raw:
            pic = ImageOps.fit(ImageOps.exif_transpose(raw).convert("RGB"),(w,h),method=Image.Resampling.LANCZOS)
        im.paste(pic,(x,y))

    def text(x,y,w,h,value,size,color=ink,style="sans",minimum=None,leading=1.17):
        c.text(x,y,w,h,value,size,color,style,minimum or size,leading)

    def bar(x,y,w,h,color):
        draw.rectangle((x,y,x+w-1,y+h-1),fill=color)

    def mast(color):
        text(56,42,680,65,data["imprint"],36,color,"mono",22)
        text(811,44,216,65,f"{index:02d} / {total:02d}",31,color,"mono")

    def foot(color):
        bar(56,1352,968,2,color)
        text(56,1371,968,52,page["tag"],28,color,minimum=20)

    face = "serif" if night else "bold"
    layout = page["layout"]
    if layout == "cover" and not night:
        photo("image",(0,0,W,H))
        # A photographic scrim preserves the highlights under the title.
        mask=Image.new("L",(1,H))
        mask.putdata([round(226*(max(0,(y-460)/(H-460))**.68)) for y in range(H)])
        im.paste(Image.new("RGB",(W,H),"#09190f"),(0,0),mask.resize((W,H)))
        bar(0,0,W,115,dark)
        mast("#e7f1df")
        text(52,752,972,360,page["title"],145,"#fff9e9",face,84,1.12)
        text(58,1184,957,95,page["body"],41,"#e7f1df",minimum=26)
        foot(accent)
    elif layout == "cover":
        bar(0,0,W,H,"#a93426"); mast("#fff4db")
        text(50,168,978,365,page["title"],136,"#fff3d8",face,78,1.12)
        photo("image",(54,562,972,662))
        text(58,1254,954,86,page["body"],38,"#fff4db",minimum=27)
        foot("#ffe8c1")
    elif layout == "frame":
        mast(ink); photo("image",(52,151,976,790))
        text(52,982,971,135,page["title"],81,ink,face,48)
        text(55,1158,952,162,page["body"],40,ink,minimum=32)
        foot(ink)
    elif layout == "split":
        bar(0,0,W,H,dark);mast("#f4ead6")
        photo("image",(453,143,627,1114))
        text(52,190,363,490,page["title"],77,"#fff7e9",face,48,1.16)
        text(54,749,350,465,page["body"],36,"#f0eadc",minimum=28)
        foot("#f9d2a4" if night else accent)
    elif layout == "pair":
        mast(ink)
        text(52,149,975,165,page["title"],92,ink,face,52)
        for i,key in enumerate(("image","second")):
            x=55+i*493
            photo(key,(x,359,474,642))
            text(x,1036,471,86,page["labels"][i],38,ink,"bold",26)
        text(55,1159,949,147,page["body"],39,ink,minimum=31)
        foot(ink)
    else:
        bg = "#e8d2ae" if night else accent
        bar(0,0,W,H,bg);mast(ink)
        text(51,189,980,304,page["title"],95,ink,face,56,1.14)
        for i,point in enumerate(page["points"]):
            y=577+i*221
            bar(56,y,965,3,ink)
            text(56,y+34,113,84,f"{i+1:02d}",47,ink,"mono")
            text(193,y+33,811,155,point,48,ink,minimum=34)
        foot(ink)
    for layer in c.layers:
        f=font(layer["style"],layer["zh"],layer["size"])
        for n,line in enumerate(layer["rows"]):
            draw.text((layer["x"],layer["y"]+int(layer["size"]*.12)+n*layer["pitch"]),line,
                      font=f,fill=layer["color"],anchor="lt",
                      stroke_width=1 if layer["style"]=="bold" and layer["size"]>=70 else 0)
    return im
