---
name: joey-design
description: Low-AI-aesthetic design skill (低 AI 味) for editable PowerPoint / PPT, high-craft Web and App UI/UX, responsive websites and playable games. Use for pitch and product decks, application interfaces and dashboards, portfolio and landing sites, game UI, menus, HUDs and browser prototypes. Includes bilingual decks, Xiaohongshu carousels and runnable reference projects.
---

# Joey Design

Build an artifact the reader can use. Start with their task and existing material, then choose the medium. For Chinese public copy and visual hierarchy use the low-AI-aesthetic (低 AI 味) guidance in [product-work.md](references/product-work.md) and [chinese-copy.md](references/chinese-copy.md).

## Choose the primary task

| Request | Example / command | What to deliver |
|---|---|---|
| PPT, pitch or product presentation | fold-deck.json / build | Editable bilingual PowerPoint with speaker notes, images and an HTML preview |
| High-craft Web or App UI/UX, product flow or dashboard | contact-sheet.json / ui | A working interface with decisions, keyboard and touch controls, empty states and recovery |
| Portfolio, brand website or product landing page | stillroom.json / site | A responsive site with useful navigation, inspectable details and shareable project links |
| Game prototype, title screen, game UI or HUD | last-ferry.json / game | A playable loop with visible controls, victory, failure, retry and progression |

The four included starters are in `assets/studies/`. For a user's existing product, preserve their stack, navigation, content and saved data. Implement their actual workflow. Choose a new layout or mechanic when the bundled example is a poor fit. Reserve social and specialist tools for requests that call for them. Xiaohongshu uses [studio-brief.md](references/studio-brief.md), sourcing and channel reports use [scenarios.md](references/scenarios.md).

## 低 AI 味

Use the subject to choose the dominant shape, image and type. Give every section a distinct job. Remove made-up metrics, vague taglines, filler badges and repeated card grids that add no information. One primary action must take a visitor somewhere real. Write Chinese UI labels as actions, keep full stops out of authored Chinese display copy and preserve decimals, filenames, URLs and quotations. A copy check locates punctuation; assess tone by reading the piece in context. Run the project-specific checks in [product-work.md](references/product-work.md).

    python3 "$SKILL/scripts/joey.py" copycheck brief.json

## Set an art direction people can see

For a brief that calls for stronger visual work, read [exhibition.md](references/exhibition.md). Make three cover studies of the same subject before extending the selected geometry into a deck, a vertical sequence and a working interface. Compare type size, subject scale, crop and reading order at equal size. Carry one motif across media. Let someone perform the action the motif suggests.

    python3 "$SKILL/scripts/joey.py" directions brief.json --out cover-studies

A complete example ships in `assets/studies/fold-deck.json` and `assets/studies/fold.json`. Use the plate theme for full-bleed exhibition work, or its listening-desk app for playing, tuning, storing and exporting a sound.

## Direct the piece

1. Extract the product name, market, decision, available imagery, approved specifications and asset rights. Pull explicit facts from the supplied brief. Mark estimates as estimates in both languages. Omit unverified superlatives, testimonials, performance figures and certifications.
2. Write an opening line that could belong only to this subject. Pair it with one image that shows the object, use or evidence. Use the real pack shot for sales work. For a speculative concept, create original art and label it in the credit.
3. Choose a composition from [art-direction.md](references/art-direction.md). Give one reason it serves the audience. A specified brand system takes priority. If the user wants exploration, present genuinely different compositions using the same copy and image.
4. Write each language for its reader. Set a conclusion before an explanation. Let a Chinese headline break at a phrase boundary. Use a line break only where it still reads well in that language. Keep quantities and units in the shared facts map. Refer to a repeated value with {{fact_id}}.
5. For a coordinated kit, use the packaged compiler. For one requested format, compile in a temporary build folder and hand over that format. For a bespoke composition outside the packaged layouts, use the brief as the content contract and implement the requested layout in the project. Identify which outputs actually went through the checks.

## Build

Resolve this skill's directory first. Set SKILL to its absolute path. Use Python 3.9+ with Pillow and python-pptx. Keep the user's environment isolated when dependencies need installation.

    python3 -m venv .venv
    .venv/bin/python -m pip install -r "$SKILL/requirements.txt"
    cp "$SKILL/assets/starter.json" brief.json

Replace all starter content. Place an authorized image beside the brief, then update artwork.file, alt and credit. Optional artwork.wide and artwork.portrait supply alternate compositions. [brief.md](references/brief.md) describes the complete input and file contract.

    .venv/bin/python "$SKILL/scripts/joey.py" check brief.json
    .venv/bin/python "$SKILL/scripts/joey.py" build brief.json --out joey-build

For the three new standalone paths, run a command with its own brief:

    .venv/bin/python "$SKILL/scripts/joey.py" ui "$SKILL/assets/studies/contact-sheet.json" --out product-ui
    .venv/bin/python "$SKILL/scripts/joey.py" site "$SKILL/assets/studies/stillroom.json" --out studio-site
    .venv/bin/python "$SKILL/scripts/joey.py" game "$SKILL/assets/studies/last-ferry.json" --out harbor-game

For a social or app study, see [studio-brief.md](references/studio-brief.md). Run either command with a tailored copy of the study and its local images.

    .venv/bin/python "$SKILL/scripts/joey.py" social "$SKILL/assets/studies/lightwalk.json" --out lightwalk-note
    .venv/bin/python "$SKILL/scripts/joey.py" app "$SKILL/assets/studies/side-b.json" --out listening-app

Open both HTML editions of a bilingual deck, test arrow keys, and inspect the desktop and mobile sales pages. Open the PPTX in Microsoft PowerPoint when available. Check the shortest and longest titles at thumbnail size, source labels, and every action link. Rework copy or crop when text collides with evidence. Rebuild after every change to the brief.

Deliver the requested outputs with the editable brief and any reusable approved assets. Report what you opened, what still needs audience feedback, and the single next action for the intended reader.
