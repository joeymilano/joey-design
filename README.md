# Joey Design

[![Joey Design — three bilingual launch kits](docs/gallery.jpg)](https://joeymilano.github.io/joey-design/)

**从同一份产品资料，做出台上讲的 PPT、发给买家的销售页，以及社媒上第一眼看到的封面。**

An open-source design skill for bilingual product launches. One brief keeps the story, specifications and art direction together across Office, web and print-ready artwork.

[打开作品集 / Live gallery](https://joeymilano.github.io/joey-design/) · [下载英文样例 PPTX](https://github.com/joeymilano/joey-design/raw/refs/heads/main/docs/afterhours-deck-en.pptx) · [中文样例简报](examples/afterhours/brief.json)

| 案例 | 设计决定 | 成品 |
|---|---|---|
| **After hours.** 便携照明 | 把银色灯臂放在钴蓝色背景上，规格页转为浅底，让采购方读清设计目标。 | [看演示](https://joeymilano.github.io/joey-design/afterhours-deck-zh.html) · [英文销售页](https://joeymilano.github.io/joey-design/afterhours-page-en.html) |
| **Paper radio.** 唱片试听会 | 以书籍衬线和唱片局部构图做邀请函，竖版保留封套的纸感。 | [看演示](https://joeymilano.github.io/joey-design/paper-radio-deck-zh.html) · [竖版封面](docs/paper-radio-cover-zh.png) |
| **Tide index.** 潮位观测 | 用模拟测站曲线开场，接着交代采样方案，数据和来源随文件一起交付。 | [看演示](https://joeymilano.github.io/joey-design/tide-index-deck-en.html) · [研究页](https://joeymilano.github.io/joey-design/tide-index-page-zh.html) |

## Installation

```sh
npx skills add joeymilano/joey-design --skill joey-design
```

Choose your agent in the installer. Or copy the complete [skills/joey-design](skills/joey-design) directory into the skills folder used by your agent. The skill includes the renderer, templates and design references.

Try this in Codex or Claude Code:

> 用 joey-design 把附件里的阅读灯资料做成给德国经销商看的中英文发布套件。采用真实产品图。演示控制在 4 页，写清样机规格，最后引导预约看样。交付可编辑 PPTX、销售页和竖版封面。

## Run the renderer

From a fresh clone with Python 3.9+:

```sh
git clone https://github.com/joeymilano/joey-design.git
cd joey-design
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r skills/joey-design/requirements.txt
python skills/joey-design/scripts/joey.py check examples/afterhours/brief.json
python skills/joey-design/scripts/joey.py build examples/afterhours/brief.json --out joey-build
```

On Windows activate with `.venv\Scripts\activate`. Linux users need Latin and Chinese fonts, for example DejaVu and Noto CJK. A preinstalled Python environment with the two packages works offline. The compiler runs locally and requires no API key. A connected design agent is optional for drafting copy or generating original artwork.

Each build produces **ten files** across two languages. PowerPoint titles, copy, numbers and rules can be edited. Photos and illustration plates are embedded images. The HTML deck supports arrow keys, Home/End, speaker notes (N) and browser print. The sales pages link between languages, adapt to mobile and carry sources. PNGs are 1080×1440 and 1280×720.

## Change one specification

Open `examples/afterhours/brief.json`. Change `facts.light.value` from `2700 K` to `3000 K`, then rebuild. The new value appears in the specification slide, closing copy, speaker notes and both sales pages. Edit the two headlines independently. Every exported format uses the same resolved facts.

[Brief format](skills/joey-design/references/brief.md) · [Art direction](skills/joey-design/references/art-direction.md) · [Regression checks](tests/test_joey.py)

## Design credits

By **Joey Zhao**. The three projects are fictional demonstrations. The lighting image was generated for this project, and Paper Radio and Tide Index use original procedural artwork. The two reference projects informed the choice of problem: [Guizang PPT Skill](https://github.com/op7418/guizang-ppt-skill) explores browser presentations and live delivery, and [Huashu Design](https://github.com/alchaincyf/huashu-design) explores visual directions across media. Joey Design's instructions, layouts, renderer and examples were independently authored.

[MIT License](LICENSE) · [Joey Zhao](https://www.joeyzhao.cc/)
