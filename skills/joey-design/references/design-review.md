# Direct and test a design

## Find the subject in the task

Name the person, the decision, the material they inspect and the smallest action that advances it. Put a long real title and a difficult state in the first draft. For an existing product inherit its type, color and components. For a new product, pick one recognizable convention from its world and give it work to do.

| Medium | A useful comparison to sketch | Evidence to keep |
| --- | --- | --- |
| Deck | A room-sized claim against a page the audience needs to read closely | Check the chart's units and source, change a value in its workbook, reopen the deck |
| Interface | A dense side-by-side decision against a mobile sequence | Keep the decision and its consequence visible together, check keyboard, undo and restored state |
| Website | A striking entry through one project against an index for returning visitors | Open a deep link cold, find the next project and return to the same selection |
| Game | A first move learned through play against a first move learned by reading | Check whether feedback explains the cost of one move, then replay a loss and a win |

For open-ended visual work, sketch two different ways to put the *same* content in front of the user. Change scale, reading order and relationship to the object. Name the tradeoff and build the stronger one. Keep the alternatives when the user asks to choose. A statement about the art direction earns its place when you can point to the specific crop, type treatment or control it changed.

In a working UI, place the two items people actually compare within sight of each other. Express the current state in words and in a second cue. Test what happens to focus when the activating control disappears. At phone width let the primary action follow the thing it changes. For Chinese copy, read the screen aloud with the interface hidden. Replace a vague button with the result of pressing it.

## Open the deliverable

For offline HTML, run the optional Chromium review from the same Python environment as Joey. Install it once with `python -m pip install playwright` and `python -m playwright install chromium`.

    python "$SKILL/scripts/joey.py" review my-page.html --journey journey.json --out review-01

Without a journey, the command checks the opening screen. With one, it repeats the same user task from a fresh context at 1280 × 800 and 390 × 844, with the network off and reduced motion requested. The fresh output directory holds opening and final viewport captures and report.json. Failures produce a nonzero exit. Use a stable unique selector per step. Text expectations check visible elements for a substring.

    [
      {"action":"click","selector":"#pick"},
      {"action":"text","selector":"#total","value":"1 张入选"},
      {"action":"reload"},
      {"action":"text","selector":"#total","value":"1 张入选"}
    ]

Supported actions are click, press, reload, visible, disabled and text. Substitute selectors and state from the actual site. Include a check after each important change. Test touch gestures and physical devices separately when the design depends on them.

Inspect the captures at their own size. Look for a subject that gets lost, an inaccessible next action or a label whose meaning changes after clipping. Fix the most consequential issue first and repeat the same journey. Record the specific improvement. A clean report covers these sampled states, not aesthetics, accessibility conformance or every supported screen.

## Source projects

Study how [Guizang PPT](https://github.com/op7418/guizang-ppt-skill) changes pace between a visual opening and its evidence, how [Huashu Design](https://github.com/alchaincyf/huashu-design) presents alternative directions, and how [Frontend Slides](https://github.com/zarazhangrui/frontend-slides) makes a style decision from previews. For interfaces compare the subject-led choices in [Frontend Design](https://github.com/anthropics/skills/tree/main/skills/frontend-design), the project-wide patterns in [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) and the focused review passes in [Impeccable](https://github.com/pbakaus/impeccable). The chart renderer, browser journeys and briefs here are original implementations.
