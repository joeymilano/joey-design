"""Large-scale image plates, a specimen spread and a typographic score."""
from layout import Canvas

PAPER = "#f4f1e9"
INK = "#111111"
BLUE = "#1835df"
RED = "#ef3212"


def plate(canvas, image, box):
    canvas.image(*box, {**image, "fit": "crop", "variants": {}})


def score(canvas, x, y, w, h, color):
    """A margin ruler for the printed edition."""
    for n in range(33):
        tick = h if n % 8 == 0 else h // 2 if n % 4 == 0 else h // 4
        canvas.rect(x + round(n * (w-2) / 32), y+h-tick, 2, tick, color)


def slide(p, index):
    s = p["pages"][index]
    kind = s["kind"]
    c = Canvas(1280, 720, INK if kind in ("feature","close") else PAPER)
    image = {"photo": p["photo"], "alt": p["alt"]}
    detail = {"photo": p["variants"].get("portrait",p["photo"]), "alt": p.get("detail_alt",p["alt"])}
    page_no = f"{index+1:02d} / {len(p['pages']):02d}"
    if kind == "cover":
        plate(c, image, (0,0,1280,720))
        c.text(42,35,730,56,s["kicker"],23,PAPER,"mono",18)
        c.text(33,106,650,345,s["title"],147,PAPER,"bold",78,1.03)
        c.text(47,474,380,115,s["body"],29,PAPER,"bold",22)
        c.rect(47,642,245,2,PAPER)
        c.text(46,656,360,43,p["brand"],17,PAPER,"mono",15)
    elif kind == "feature":
        plate(c, detail, (462,0,818,720))
        c.text(42,35,408,70,s["kicker"],20,PAPER,"mono",15)
        c.text(38,151,403,312,s["title"],75,PAPER,"bold",41,1.07)
        c.text(43,486,375,142,s["body"],25,PAPER,minimum=19)
        c.text(44,654,335,40,page_no,19,PAPER,"mono")
    elif kind == "proof":
        c.text(43,34,805,54,s["kicker"],20,INK,"mono",15)
        c.text(41,105,1175,158,s["title"],78,INK,"bold",44,1.05)
        c.text(45,272,1166,86,s["body"],25,INK,minimum=20)
        ids = s["facts"]
        width = 1188 // len(ids)
        for n,key in enumerate(ids):
            left=44+n*width
            fact=p["facts"][key]
            c.rect(left,395,width-20,3,INK)
            c.text(left,415,width-24,133,fact["value"],98,BLUE,"bold",46,1.04)
            c.text(left+3,554,width-34,73,fact["label"],22,INK,minimum=17)
        score(c,45,646,1092,21,INK)
        c.text(1151,644,99,43,page_no,17,INK,"mono",14)
    elif kind == "spread":
        c.text(43,32,1148,50,s["kicker"],20,INK,"mono",15)
        c.text(41,89,1190,126,s["title"],67,INK,"bold",41,1.05)
        for n,item in enumerate(s["plates"]):
            x=44+n*602
            plate(c,item,(x,236,580,309))
            c.text(x,555,577,66,item["label"],22,INK,"bold",16)
        c.text(45,643,1090,50,s["body"],20,INK,minimum=15)
    else:
        c.rect(0,0,1280,720,BLUE)
        c.text(46,31,1030,55,s["kicker"],20,PAPER,"mono",15)
        c.text(34,134,1200,300,s["title"],135,PAPER,"bold",62,1.03)
        c.text(45,449,1100,93,s["body"],30,PAPER,minimum=22)
        c.rect(45,601,1180,2,PAPER)
        c.text(45,630,1070,56,p["action"],26,PAPER,"bold",18)
        c.text(1120,642,121,39,page_no,18,PAPER,"mono")
    return c


def card(data, page, index, total):
    from render import raster
    kind=page["layout"]
    c=Canvas(1080,1440,{"cover":PAPER,"frame":INK,"split":PAPER,"pair":INK,"list":BLUE}[kind])
    light=kind in ("cover","frame","pair","list")
    fg=PAPER if light else INK
    def pic(key,box):
        entry=data["images"][page[key]]
        plate(c,{"photo":entry["path"],"alt":entry["alt"]},box)
    if kind=="cover":
        pic("image",(0,0,1080,1440))
        c.rect(0,0,1080,410,RED)
        c.text(36,95,1008,283,page["title"],136,PAPER,"bold",72,1.04)
        c.rect(0,1205,1080,235,INK)
        c.text(41,1241,996,134,page["body"],48,PAPER,minimum=32)
    elif kind=="frame":
        pic("image",(0,125,1080,834))
        c.text(37,1000,1002,138,page["title"],83,PAPER,"bold",47)
        c.text(42,1192,976,177,page["body"],40,PAPER,minimum=31)
    elif kind=="split":
        c.text(32,156,1014,245,page["title"],113,INK,"bold",56,1.05)
        pic("image",(0,449,1080,617))
        c.text(42,1150,981,207,page["body"],45,INK,minimum=30)
    elif kind=="pair":
        c.text(35,135,1008,195,page["title"],84,PAPER,"bold",50)
        for n,k in enumerate(("image","second")):
            x=36+n*513
            pic(k,(x,379,495,650))
            c.text(x,1055,491,110,page["labels"][n],35,PAPER,"bold",23)
        c.text(39,1215,981,132,page["body"],38,PAPER,minimum=28)
    else:
        c.text(33,142,1016,281,page["title"],107,PAPER,"bold",58,1.06)
        for n,point in enumerate(page["points"]):
            y=508+n*247
            c.rect(40,y,998,3,PAPER)
            c.text(41,y+22,100,100,f"{n+1:02d}",40,PAPER,"mono")
            c.text(167,y+19,861,170,point,50,PAPER,"bold",32)
        score(c,42,1337,994,37,PAPER)
    c.text(42,33,745,59,data["imprint"],32,fg,"mono",21)
    c.text(857,33,186,59,f"{index:02d} / {total:02d}",32,fg,"mono",21)
    return raster(c)
