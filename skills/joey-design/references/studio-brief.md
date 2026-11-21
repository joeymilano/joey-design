# Inputs for social and app builds

The two runnable studies ship inside the skill, in `assets/studies/`. Copy that directory or copy one JSON file and the images it names into a project. Run only the requested command. An app-only brief may omit social, and a social-only brief may omit app.

| Shared field | Meaning |
|---|---|
| id | Lowercase project slug. Choose a distinct ID for independently saved prototype state. |
| brand, imprint | Display name and short printed wordmark |
| theme | daylight for a light editorial system, or afterdark for warm paper and a dark app |
| credit | Source and rights caption. Identify speculative or synthetic work. |
| images | Map from lookup key to a local file and descriptive alt text. Keep files inside the brief directory. |

## Social

The social object has title, caption and an ordered pages array. Each page names its layout. The table in [formats.md](formats.md) lists the per-layout fields. The CLI checks text fit at the minimum type size. Resolve an overset title by breaking at a phrase boundary, shortening the title or choosing a different composition.

    python "$SKILL/scripts/joey.py" social "$SKILL/assets/studies/lightwalk.json" --out lightwalk-note

The output contains numbered JPGs, caption.txt, images.zip and index.html. Open the preview to flip through images, save an individual image or copy the caption. Keep images.zip beside index.html for the complete-set download.

## App

The app object names mode (collect or reserve), title, subtitle, home and saved navigation labels, action and undo button labels, list and detail headings, and items. Each item needs a unique id, category, title, meta line, body, image key and facts. A fact is a pair of label and value strings. Reserve items also specify unique slot labels. Optional feature_action, empty_title and empty_body tailor the first button and empty state to the product.

    python "$SKILL/scripts/joey.py" app "$SKILL/assets/studies/side-b.json" --out listening-app

Open index.html on a phone or in a desktop browser. It embeds the images and has no network dependency. On a static web server, the same browser and origin retain local state across reloads. The reservation example makes no request to a booking service.
