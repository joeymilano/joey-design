# Buying sheets, channel reviews and timetables

Start with one brief from `assets/scenarios`. Replace the data and project ID, then run the scenario command. The generated index.html embeds the content and any artwork. Open it offline or serve it as a static page.

| Reader's task | Brief / interface language | What to supply | Check the handoff |
| --- | --- | --- | --- |
| Ask an overseas supplier for samples | material-office.json / English | Real sample codes, material names, weight and width as supplied, a local hero image with alt text and credit, colour chips | Choose two cuts, reduce one quantity, download the English TXT draft and check its codes and quantities |
| Explain a change in enquiries | signal-ledger.json / Chinese | Two comparable periods, the same channel definitions, integer pairs of visits and enquiries, source and deduplication rules | Filter a channel, switch from counts to rate, export the active view and check its periods and denominator |
| Plan an evening across two rooms | night-school.json / Chinese | Session, track, venue, start and end with a UTC offset, IANA display timezone, one line about what attendees will do | Add adjacent sessions and one overlapping session, change rooms, reopen and import the downloaded ICS |

All three use `kind`, `id`, `title`, `edition`, `headline`, `intro`, `source`, and an `items` array. Use unique lowercase slugs for project and item IDs. Keep an item's ID stable across edits so a saved selection still refers to the same item. Change the project ID for an unrelated collection.

## Samples

Set kind to samples. Each item takes id, name, code, six-digit hex color, spec and note. Use a relative image path inside the brief folder. Colour chips are approximate. Label concept images and fictional catalogues. A request is a draft for a supplier, with no order or message sent.

## Report

Set kind to report. Give previous and current a date range each. Rename the indicators in metrics.visits, metrics.actions and metrics.rate when the funnel represents signups or bookings. The CSV includes the selected metric, difference and its raw counts in both periods. An item's previous and current arrays each contain visits and enquiries in that order. Enquiries must be a subset of visits. Calculate the aggregate from summed counts. Show a missing rate for zero visits. Express a change in rates as percentage points. Replace the example's definition if the supplied data uses another attribution rule.

## Agenda

Set kind to agenda. Give each item id, name, track, place, start, end and note. Supply ISO 8601 timestamps including offsets and the programme timezone. Track filters only change what is visible. Overlaps are checked across rooms. The calendar file uses UTC times and includes all selected sessions. A saved programme is personal to the current browser, not an event booking.
