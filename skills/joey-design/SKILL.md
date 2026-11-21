---
name: joey-design
description: Create art-directed PPT and editable PowerPoint decks, Xiaohongshu (小红书/RED) carousel posts, interactive mobile app prototypes, sales pages and bilingual launch kits. Use for slide design, social image sequences, product UI/UX, cross-format brand systems and photography-led editorial work. Includes original examples, local renderers and medium-specific quality checks.
---

# Joey Design

Design for the moment after someone sees the work. Name the audience, the decision they face and the piece of evidence that can move it. A distributor choosing a sample needs a different page from a buyer comparing specifications.

## Choose the deliverable

Read [formats.md](references/formats.md) for the production sequence and visual checks. Start with the user's primary medium. A standalone 小红书 post or an App prototype can be authored from a single-language studio brief.

| Request | Deliverable | Runnable starting point |
|---|---|---|
| PPT, 路演, keynote, research or editorial talk | Editable .pptx with notes and a keyboard-operated HTML deck | `assets/studies/lightwalk-deck.json` |
| 小红书笔记, carousel, photo essay or swipe guide | Numbered 3:4 images, cover, caption, image pack and interactive preview | `assets/studies/lightwalk.json` or `side-b.json`, social command |
| Mobile App, product interaction or 高保真原型 | Responsive single-file web prototype with complete actions and persistent local state | Same studies, app command |
| Bilingual product launch or sales handout | Linked language editions, web page, PPTX, speaker notes and campaign art | `assets/starter.json`, build command |

Match recognisable assets, typography and voice across a campaign. Recompose for the reading distance and interaction of each medium. A slide can compare two photos side by side, a note can reveal them over five swipes, and an app can let someone save the next location.

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

For a social or app study, see [studio-brief.md](references/studio-brief.md). Run either command with a tailored copy of the study and its local images.

    .venv/bin/python "$SKILL/scripts/joey.py" social "$SKILL/assets/studies/lightwalk.json" --out lightwalk-note
    .venv/bin/python "$SKILL/scripts/joey.py" app "$SKILL/assets/studies/side-b.json" --out listening-app

Open both HTML editions of a bilingual deck, test arrow keys, and inspect the desktop and mobile sales pages. Open the PPTX in Microsoft PowerPoint when available. Check the shortest and longest titles at thumbnail size, source labels, and every action link. Rework copy or crop when text collides with evidence. Rebuild after every change to the brief.

Deliver the requested outputs with the editable brief and any reusable approved assets. Report what you opened, what still needs audience feedback, and the single next action for the intended reader.
