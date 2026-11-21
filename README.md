# Joey Design

一个为演示、小红书和移动界面做设计的开源 Skill。每种媒介都带可运行的生成器和可直接打开的成品。

[打开完整作品集 / Live gallery](https://joeymilano.github.io/joey-design/) · [下载中文版 PPTX](https://joeymilano.github.io/joey-design/lightwalk-deck-zh.pptx) · [翻看一篇小红书](https://joeymilano.github.io/joey-design/side-b-social.html) · [试用预约 App](https://joeymilano.github.io/joey-design/side-b-app.html)

[![摄影演示、唱片封套笔记与机位收藏界面](docs/studio-hero.jpg)](https://joeymilano.github.io/joey-design/)

## 作品集

| 媒介 | 能拿到什么 | 公开案例 |
| --- | --- | --- |
| PowerPoint | 4 组中英双语演示，8 份可编辑 PPTX。均含演讲者备注、网页演示、项目页、横竖封面。 | [光隙 · 建筑摄影](https://joeymilano.github.io/joey-design/lightwalk-deck-zh.html) · [After hours. · 工业产品](https://joeymilano.github.io/joey-design/afterhours-deck-zh.html) · [Paper radio. · 文化活动](https://joeymilano.github.io/joey-design/paper-radio-deck-zh.html) · [Tide index. · 数据研究](https://joeymilano.github.io/joey-design/tide-index-deck-zh.html) |
| 小红书 | 2 篇各 5 张的 1080 × 1440 图文，含封面、分解页、对照页和清单。整套可下载，附正文与话题标签。 | [追一束下午的光](https://joeymilano.github.io/joey-design/lightwalk-social.html) · [落针之前，读一张封套。](https://joeymilano.github.io/joey-design/side-b-social.html) |
| 移动 App | 2 个可操作的响应式网页原型。摄影工具支持筛选、详情与收藏。唱片室支持选场、预约、改期与取消。演示状态保存在当前浏览器。 | [光隙 · 机位手记](https://joeymilano.github.io/joey-design/lightwalk-app.html) · [反面唱片室 · 试听预约](https://joeymilano.github.io/joey-design/side-b-app.html) |

想看设计如何随媒介改变，可以从《光隙》开始。演示把建筑照片横排，让观众比较人物和台阶怎样引导视线。小红书把两个拍摄动作拆开，让读者边滑边学。手机端把照片做成机位卡，出门前能按光线筛选，再存下想练的那张。

## Installation

```sh
npx skills add joeymilano/joey-design --skill joey-design
```

在安装器中选择你的 Agent，也可以将整个 [skills/joey-design](skills/joey-design) 目录复制到支持 Skills 的客户端。

试着给 Codex 或 Claude Code 这条简报：

> 用 joey-design 为独立书店的摄影散步做三份东西。讲座需要 4 页可编辑中文 PPT，小红书需要 5 张给初学者的构图笔记，手机端让读者按光线筛选机位并收藏。三份都用我上传的照片，给我能直接打开的成品。

## 本地生成

从项目根目录运行。需要 Python 3.9+。图片、文案及渲染均可在本地处理，无需 API 密钥。

```sh
git clone https://github.com/joeymilano/joey-design.git
cd joey-design
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r skills/joey-design/requirements.txt

# 核对简报，生成双语演示与项目页
python skills/joey-design/scripts/joey.py check skills/joey-design/assets/studies/lightwalk-deck.json
python skills/joey-design/scripts/joey.py build skills/joey-design/assets/studies/lightwalk-deck.json --out build/ppt

# 生成整篇图文、逐张 JPG、正文与 ZIP
python skills/joey-design/scripts/joey.py social skills/joey-design/assets/studies/lightwalk.json --out build/social

# 生成可在手机浏览器打开的界面
python skills/joey-design/scripts/joey.py app skills/joey-design/assets/studies/side-b.json --out build/app
```

Windows 通过 `.venv\Scripts\activate` 激活环境。Linux 建议安装 DejaVu 与 Noto CJK 字体。

替换素材时，先复制整份 [摄影与唱片室示例](skills/joey-design/assets/studies)，保留 JSON 引用图片的相对路径。在 [工业产品示例](examples/afterhours/brief.json) 中，把 `facts.light.value` 从 `2700 K` 改成 `3000 K` 后重建，规格页、结尾、备注和双语销售页会一起更新。

[媒介选择与验收](skills/joey-design/references/formats.md) · [演示简报格式](skills/joey-design/references/brief.md) · [图文与 App 简报格式](skills/joey-design/references/studio-brief.md) · [美术指导](skills/joey-design/references/art-direction.md)

## Design credits

Designed by **Joey Zhao**. All projects are fictional studies. The lighting, architecture and record-store images were generated for these examples. Paper Radio and Tide Index use original procedural artwork.

项目参考了 [Guizang PPT Skill](https://github.com/op7418/guizang-ppt-skill) 对浏览器演示的探索，以及 [Huashu Design](https://github.com/alchaincyf/huashu-design) 对跨媒介设计的组织方式。Joey Design 的说明、渲染器、版式与案例独立编写。

[MIT License](LICENSE) · [Joey Zhao](https://www.joeyzhao.cc/)
