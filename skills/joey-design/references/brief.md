# Brief and output contract

Copy `assets/starter.json` from the installed skill. Its FOLD 01 example names a photograph. Supply your own licensed image and update the fields. The complete runnable examples and images are available in the public repository's `examples/` directory.

| Field | Type | Meaning |
|---|---|---|
| theme | string | nocturne, folio, signal or gallery |
| brand | string | Shared wordmark or imprint |
| artwork.file | relative path | A local photograph or illustration, ideally 1200 px or wider. PNG/JPEG recommended. |
| artwork.wide, artwork.portrait | optional paths | Art-directed alternatives used for frames at least 2.4:1 or narrower than 0.95:1. |
| artwork.alt, artwork.credit | language pairs | Description of the image, rights or attribution, and whether it is conceptual |
| facts | object keyed by IDs | One to six entries. Each has a single canonical value string, a translated label, and a translated source. Preserve units. |
| action, action_url | language pair and string | Intended action and its supplied destination. Use an HTTPS address, mailto, or #sources for a self-contained concept. |
| slides | ordered array | Three to sixteen pages. Start with cover, add feature, spread or proof, finish with close. |
| Each slide | object | kind, kicker, title, body and notes. A spread adds two plates with a local file and bilingual label and alt. A proof adds a facts list of one to three existing IDs. |

A language pair has the form `{"en":"Reading light","zh":"阅读灯"}`. Add `{{mass}}` in prose to resolve the same supplied value in both languages. Build fails on unresolved references, missing translations, missing artwork or text beyond the available space. If copy fails to fit, split the slide or trim the sentence. To target one language at delivery, select its completed files.

## Output

Each language gets an offline keyboard-operated 16:9 HTML deck, a native editable PPTX with notes, a mobile-friendly HTML page, a 1080×1440 PNG cover and a 1280×720 PNG cover. The two sales pages link to each other and should travel together. Print the HTML deck in a modern browser to save a PDF. The source photos and print artwork remain raster objects inside the PowerPoint. Text, rules and backgrounds use editable Office elements. Font substitution can change appearance on a different machine.

## Fonts

The renderer searches common macOS, Windows and Linux font locations, then fontconfig if available. For Linux install DejaVu and Noto CJK. Set JOEY_CJK_FONT to a specific Chinese font file to use it for all Chinese text. A missing font or an overlong title should be fixed before publication. For Chinese typography, check the actual exported output on the presentation computer.

Use `plate` for full-bleed covers, macro detail pages, a specimen grid and a high-contrast close. Set `artwork.portrait` to a detail shot and describe it with bilingual `artwork.detail_alt`. The directions command uses the main and detail image to make three distinct cover compositions in both languages and both aspect ratios.
