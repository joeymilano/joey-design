---
name: joey-design
description: Design bilingual Chinese and English product launches, distributor sell sheets, keynote decks, editorial campaigns and social covers. Use when a user wants art direction, an editable PowerPoint, a responsive sales page or a coordinated launch kit from one brief. Handles source-backed product specifications, bilingual typography, image art direction and offline exports.
---

# Joey Design

Design for the moment after someone sees the work. Name the audience, the decision they face and the piece of evidence that can move it. A distributor choosing a sample needs a different page from a buyer comparing specifications.

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

Open both HTML editions, test arrow keys, and inspect the desktop and mobile sales pages. Open the PPTX in an Office-compatible viewer. Check the shortest and longest titles at thumbnail size, source labels, and every action link. Rework copy or crop when text collides with evidence. Rebuild after every change to the brief.

Deliver the requested outputs with the editable brief and any reusable approved assets. Report what you opened, what still needs audience feedback, and the single next action for the intended reader.
