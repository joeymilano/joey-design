# Design for the medium

## Presentation

Start by naming the room and decision. For a talk, write the headline as the sentence the audience should remember. For a sales presentation, anchor each claim to a product image or an approved specification. For a research review, expose the unit and data origin on or beside the figure.

Use a cover to set the scale, a feature to examine a mechanism, a spread for visual comparison, a proof page for comparable values and a close for the next action. The gallery theme frames photographic work on a pale stock. The spread takes exactly two plates, each with a local file, bilingual caption under label, and bilingual alt text. Include both plates in the artwork credit. See the complete working input in `assets/studies/lightwalk-deck.json`.

Open an exported PPTX in **Microsoft PowerPoint** when available. Read the projected slide at thumbnail scale, inspect the slide at normal size and verify its notes. If editable handoff matters, edit a copy of a text box in PowerPoint, save it, reopen it and check the result. Distinguish this check from inspecting the file structure.

## Xiaohongshu / 小红书

Pick the reader's reason to swipe. A how-to promises a practice, a comparison promises a choice, and a field note promises a specific observation. Use the first image for subject recognition. Place each subsequent observation next to the photograph that demonstrates it. End with something the reader can take outside the post, such as a small practice, a shopping criterion or a source list.

| Page layout | Editorial job | Required content |
|---|---|---|
| cover | Name one reason to look | tag, title, body, image |
| frame | Make one detail visible | tag, title, body, image |
| split | Give image and commentary different proportions | tag, title, body, image |
| pair | Compare visible evidence with explicit labels | tag, title, body, image, second, two labels |
| list | Leave a useful sequence to save | tag, title, two or three points |

Use 2–12 pages in this renderer. The examples use five pages at 1080×1440. Judge the cover as a small feed thumbnail and inspect body copy at normal phone width. Keep a continuous read from cover to final card. Write the post title, caption and tags in the reader's voice. The JPG files and caption are ready for manual posting after review.

## App / mobile product

Choose the task before the screen list. Build one path a person can finish, with an initial state, an action, feedback and a way back. Preserve the person's selection across navigation and reload when appropriate. Write the empty state and cancellation or reversal alongside the happy path.

| Task | Starting composition | Interaction to prove |
|---|---|---|
| Browse and collect | An editorial opener and a filterable collection | Open a detail, save it, reload, find it in the collection, remove it |
| Choose and reserve | A programme, a detail view and explicit time slots | Select a slot, confirm, change it and cancel |
| Shop or configure | Product view with options beside the decision | Change a variant, review the summary, edit the choice |
| Make or edit | A working canvas with reachable controls | Change an item, undo, save a draft and reopen it |
| Monitor or compare | A summary with a drill-down into the underlying evidence | Change scope, inspect a record and return with context |

The packaged app builder implements the first two paths. For shopping, editing, dashboards and other custom flows, use the supplied brief as design input and author the needed UI and state in the target project. A request for native SwiftUI, Compose or React Native calls for the requested stack and its corresponding build or simulator check.

Start with a narrow phone view. Give touch actions a 44 px design target, keep bottom navigation clear of the safe area, check focus after a route change and keep text readable with long names. On larger screens, use the extra width for composition and evidence. Test a real completion and an undo. In the bundled demos all saves and reservations are local to the browser.
