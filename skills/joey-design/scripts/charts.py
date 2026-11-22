"""A single-series comparison, drawn from the same data in each medium."""
import html
import math

from model import THEMES, pair, field


def localized_chart(slide, lang, where):
    chart = field(slide, "chart", where)
    unit = pair(field(chart, "unit", where), where + ".unit")[lang]
    source = pair(field(chart, "source", where), where + ".source")[lang]
    rows = field(chart, "rows", where)
    if not isinstance(rows, list) or not 2 <= len(rows) <= 6:
        raise ValueError(f"{where}: provide 2–6 chart rows")
    values = []
    for row in rows:
        label = pair(field(row, "label", where), where + ".label")[lang]
        value = field(row, "value", where)
        if type(value) not in (float, int) or not 0 <= value <= 1e12 or not math.isfinite(value):
            raise ValueError(f"{where}: chart values must be finite numbers between 0 and 1 trillion")
        if label in [name for name, _ in values]:
            raise ValueError(f"{where}: chart category labels must be distinct")
        values.append((label, value))
    maximum = chart.get("max", max(value for _, value in values) or 1)
    if type(maximum) not in (float, int) or not 0 < maximum <= 1e12 or maximum < max(value for _, value in values):
        raise ValueError(f"{where}: chart max must be positive and cover every value")
    return dict(unit=unit, source=source, rows=values, maximum=maximum)


def slide_canvas(project, index):
    from layout import Canvas
    s = project["pages"][index]
    data = s["chart"]
    t = THEMES[project["theme"]]
    ink = t["dark"]
    c = Canvas(1280, 720, t["paper"])
    c.text(50, 42, 1178, 40, s["kicker"], 19, ink, "mono", 15)
    c.text(48, 96, 1180, 98, s["title"], 69, ink, "bold", 35)
    c.text(50, 208, 1178, 56, s["body"], 25, ink, minimum=19)
    c.text(50, 277, 1178, 36, data["unit"], 22, ink, "bold", 16)
    c.layers.append(dict(type="chart", x=50, y=320, w=1178, h=275,
                         data=data, ink=ink, accent=ink))
    visual_bars(c.layers[-1])  # Validate category and value labels at minimum size.
    c.rect(50, 623, 1178, 2, ink)
    c.text(50, 640, 1040, 60, data["source"], 19, ink, minimum=15)
    c.text(1138, 646, 90, 43, f"{index+1:02}/{len(project['pages']):02}", 18, ink, "mono", 14)
    return c


def data_table(data):
    esc = html.escape
    body = ''.join(f'<tr><th scope="row">{esc(label)}</th><td>{value}</td></tr>'
                   for label, value in data["rows"])
    return f'<table><caption>{esc(data["unit"])}</caption><tbody>{body}</tbody></table>'


def visual_bars(n):
    from layout import Canvas
    c = Canvas(n["w"], n["h"], "#ffffff")
    rows = n["data"]["rows"]
    height = n["h"] // len(rows)
    label_width, track_width = int(n["w"] * .23), int(n["w"] * .60)
    for index, (label, value) in enumerate(rows):
        center = index * height + height // 2
        c.text(0, center - 17, label_width-12, 36, label, 24, n["ink"], minimum=15)
        length = round(track_width * value / n["data"]["maximum"])
        if length:
            c.rect(label_width, center-8, length, 16, n["accent"])
        c.text(label_width + track_width + 16, center - 17, n["w"]-label_width-track_width-16,
               36, str(value), 24, n["ink"], "bold", 15)
    return c


def add_office_chart(slide, box, layer):
    from pptx.chart.data import CategoryChartData
    from pptx.dml.color import RGBColor
    from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
    from pptx.util import Pt

    data = layer["data"]
    workbook = CategoryChartData()
    workbook.categories = [name for name, _ in data["rows"]]
    workbook.add_series(data["unit"], [value for _, value in data["rows"]])
    chart = slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, *box, workbook).chart
    chart.has_legend = False
    chart.has_title = False
    chart.category_axis.reverse_order = True
    chart.value_axis.minimum_scale = 0
    chart.value_axis.maximum_scale = data["maximum"]
    chart.value_axis.visible = False
    chart.value_axis.has_major_gridlines = False
    chart.category_axis.format.line.fill.background()
    ink = RGBColor.from_string(layer["ink"][1:])
    chart.category_axis.tick_labels.font.size = Pt(15)
    chart.category_axis.tick_labels.font.color.rgb = ink
    series = chart.series[0]
    series.format.fill.solid()
    series.format.fill.fore_color.rgb = RGBColor.from_string(layer["accent"][1:])
    plot = chart.plots[0]
    plot.gap_width = 100
    plot.has_data_labels = True
    labels = plot.data_labels
    labels.show_value = True
    labels.position = XL_LABEL_POSITION.OUTSIDE_END
    labels.font.size = Pt(14)
    labels.font.color.rgb = ink
