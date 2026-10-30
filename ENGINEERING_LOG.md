# Engineering log

Durable decisions and lessons only. Newest first.

## 2026-10-30 [R2 claude-sonnet-5-5]

**Decisions**
- The site is generated. `scripts/build.py` renders every page to static HTML from `data/site-data.json`, so crawlers and link previews see the full content without running JavaScript. `js/app.js` only adds search, filters and sorting.
- Per-topic pages (`topics/<id>/`) exist so each topic can be found and linked on its own. The home page keeps the topic summaries and links to them.
- Newsletter sending is not built into the site. A static site cannot send email. The form posts to an email service chosen in `data/site-config.json`, so changing service means editing config, not code.
- Digest feeds only include completed days and ISO weeks (UTC). An entry is never edited after an email service has picked it up. The cost is that the build depends on the date, so the workflow also runs daily.

**Root causes found**
- The canonical URL and README pointed to `/type1l-index/` (lowercase). GitHub Pages paths are case-sensitive, so that URL returns 404. The live site is `/Type1L-Index/`. The base URL now lives in `data/site-config.json` only.
- The "Type 1L" title used the digit one. The standard designation is Type IL (capital I, L).
- `news` listed R66 and R74, but those resources lacked the `news` tag, so cross-references only worked one way. `build.py` now checks both directions and fails the build on any mismatch.
- Type labels differed only by case ("News" and "news"), which created duplicate filter options. Validation now rejects that.

**Lessons**
- Check every external identifier against its registry, not just the page text. Crossref confirmed 29 DOIs. It rate-limits (HTTP 429) at 6 parallel requests, so retry sequentially with a pause.
- 403 and 202 responses to scripted GETs mean bot protection, not a dead link. Only 404 and a sign-in redirect (R39) were treated as defects.
- A test written to always pass is worse than no test. The default-sort check in the first browser run was one of these; the order was confirmed by hand instead.

**Open**
- R39 (ACA IS793): the DOI resolves to a Microsoft sign-in page from a script. A public URL was not found.
- R81 (NDSU thesis) is undated because its record sits behind a human-verification page.
- R42, R9 and others stay undated where no source date was found. Dates were never inferred.
- Takeaway text, for example the C595-26 sulfate designation wording, was not re-checked against standard text.
