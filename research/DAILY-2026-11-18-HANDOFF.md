# Daily pass 2026-11-18 — handoff

- Zone: America/Chicago. Runs of Nov 14–17 left nothing; this pass resumed from the Nov 13 state (site-data lastUpdated 2026-11-13, 2,560 resources, R1–R2561). Additions: **486 verified records, R2562–R3047** (R2562–R2564 = the 3 leads left open on Nov 13; R2565–R3047 = 483 new discovery records; R428 stays retired). **Totals: 3,046 resources, 59 topics.** No corrections to existing records (R1–R2561 asserted byte-identical in apply.py).
- Open-lead queue (3 → 0):
  - R2562 10.5281/zenodo.23496439 (IJESGT, Kyrgyzstan 2026): journal page journals.ayu.edu.kz/…/view/6574 now returns 200; DC/citation metadata read (5 authors, issued 2026-09-30, vol 1 no 3, pp 56–64, ISSN 3080-8693, CC BY-NC-ND 4.0, abstract). The DOI printed on the page is NOT registered (doi.org/DataCite 404), so URL = journal page; recorded in identifiers.listedDoi.
  - R2563 10.4467/2353737XCT.14.077.2527 (Lelusz, carbon nanotubes, Czasopismo Techniczne 2014) and R2564 10.4467/2353737XCT.16.156.5767 (Borowski & Hycnar, granulated fly ash + phosphogypsum, 2016): doi.org still redirects to ejournals.eu (HTTP 500 today) and Crossref/DataCite have no record; the publisher article pages were read from Wayback Machine raw snapshots (2019-09-18 and 2018-04-19) — DC/citation metadata (issued dates 2014-06-10 / 2016-12-14, issue, pages 5–11 / 37–45, ISSN 2353-737X, English abstracts). Access level landing_page_inspected, with the archived-copy limitation stated in each evidence note. OpenAlex's 2015-03-25 date for the Lelusz paper differs from the publisher page; the publisher date is used.
- New leads this pass: 490 checked the same run → 483 promoted (R2565–R3047), 7 rejected as unverifiable (DOI not registered at doi.org/Crossref/DataCite and the OpenAlex landing page could not be inspected: ACI 10.14359/17303 via CiNii, Iranian AUT/GSJ journal DOIs via DOAJ 403/PDF, Indonesian 10.32502, Chinese CNKI-style 10.16198, Taiwan IJPRT via TRID), 0 open.
- Focus (rotation head per ledger): concrete-mass-rcc, concrete-heavyweight, concrete-cellular, binder-specialty, concrete-shotcrete, binder-white-masonry, binder-well, binder-international, scm-natural, scm-clay, cross-supply-region, cross-failure-repair, cross-construction; Type IL legacy topics via Portland-limestone backfill (strength, durability, fresh, pavement, microcracking, carbon, dot, standards); languages new to the rotation (ar, fa, hr, hu, id, ro, sk, sv, uk, vi) plus pt/es/fr/de/ja/zh re-queried; Nov 2026 current awareness; backward chase (628 existing DOI records in the 12 least-covered topics → 1,196 references) and forward chase (30 most-cited existing records).
- Search yield: 135 harvest queries + 85 page-2 re-queries of earlier-rotation queries (page 2 = deeper rows, not repeats) + chases; 2,938 + 2,813 unique API hits; 671 listed, 117 excluded on screening, 470 DOI hits verified (448 Crossref, 14 DataCite, rest unregistered), 84 no-DOI hits probed (20 landing pages read and added, plus 3 ACI/CET pages whose DOIs are unregistered, recorded with listedDoi) → 483 new records.
- Access levels: {"doi_metadata": 314, "abstract_metadata": 146, "landing_page_inspected": 26}. Languages: en 451, vi 6, hu 4, pt 4, de 3, hr 3, id 3, es 3, sv 3, fr 2, sk 2, ro 1, uk 1 (non-English descriptions are English glosses; 10 records had the OpenAlex language corrected from title/abstract, noted per record). Provenance: 85 backward chase, 43 forward chase, 36 dated 2026, 52 Type IL legacy-topic records. Decades: 1920s 1, 1930s 2, 1940s 1, 1950s 5, 1960s 2, 1970s 22, 1980s 35, 1990s 44, 2000s 93, 2010s 181, 2020s 100.
- Screened out: soil stabilisation/geotechnical, dental/biomedical cement, sedimentary-geology "cement", dam health-monitoring and seismic-fragility papers, generic structural-mechanics "failure" papers, dye/phenol adsorption on ashes, non-concrete uses of "concrete", duplicate titles; ~60 no-DOI hits not inspectable (TRID, CiNii, CNKI/CQVIP, JS-only catalogues).
- Crossref note: python urllib with a fake mailto in the User-Agent was rate-limited (HTTP 429) by Crossref's polite pool; the public pool without mailto worked (5 req/s, 1 concurrent).
- Gaps/next steps are in research-ledger.json (pass-2026-11-18): next rotation head = concrete-lightweight, binder-cac-csa, binder-lc3, binder-magnesium-carbonatable, scm-silica, scm-slag, scm-emerging, binder-blended, concrete-structural, cross-tests-codes, cross-environment-cost.

## Validation (fresh clone of xxdccole/Type1L-Index @ 33e7fdc "Build site" (parent chain …dad6cab Nov 13 pass) + working files, /tmp/t1l-v18; nothing pushed)
- `python3 scripts/build.py --validate`: valid: 3046 resources, 59 topics, 60 undated.
- `python3 scripts/build.py`: built index.html, 59 topic pages, sitemap.xml, llms.txt, 3 feeds (as of 2026-11-18).
- `python3 scripts/check_site.py` (repo script unchanged; it already carries the Nov 13 title-tag guard): checked 60 pages, site check passed, exit 0.

## Files to publish (bundle /workspace/publish-1118/publish-2026-11-18.tar.gz → repo paths)
| bundle path | repo path |
|---|---|
| stage/data/site-data.json | data/site-data.json |
| stage/data/resource-notes.json | data/resource-notes.json |
| stage/research/index.md | research/index.md |
| stage/research/research-ledger.json | research/research-ledger.json |
| stage/research/candidates.jsonl | research/candidates.jsonl |
| stage/research/verified-sources.jsonl | research/verified-sources.jsonl |
| stage/research/DAILY-2026-11-18-HANDOFF.md | research/DAILY-2026-11-18-HANDOFF.md |
| stage/research/pass-2026-11-18/ | research/pass-2026-11-18/ |
No script change is needed. Then run `python3 scripts/build.py --validate && python3 scripts/build.py && python3 scripts/check_site.py` and commit the regenerated site files. Expected live check: R2562 (first) and R3047 (last), 3,046 resources, lastUpdated 2026-11-18, R428 absent.
The pass folder omits the raw API dumps (api-hits*.json, new-hits*.json, landing HTML, selected.json) for size; they remain on the box under /workspace/type1l-index/research/pass-2026-11-18/.

## Private Page patch
research/pass-2026-11-18/page/edit-ops.json: 25 ordered {step, old_string, new_string} ops against canvas-2026-11-13-proposed.tsx (= live Page; each old_string matched exactly once when applied in order; largest new_string ≈ 51 KB):
- 3 ops insert the D1118 block (chunks D1118_A–D1118_J, 50 rows each, 486 rows R2562–R3047; ≤4 chunks per op) plus DAILY1118 before `const AXIS: AxisTopic[] = [` (each re-inserts the anchor; apply in order).
- RES.push and the topic loop gain `...DAILY1118`; scope line (Nov 18; 3,046 records; R1–R3047), evidence callout (3 old leads resolved, none open), What's new caption + row, change-log row, gaps row "Daily pass limits (Nov 18)".
- 14 AXIS takeaway pointers ("Nov 18 backfill: N records (Rx–Ry)…") for the 13 focus topics + scm-limestone; the Type IL "durability" topic has no AXIS entry and was skipped.
- Result: page/canvas-2026-11-18-proposed.tsx (esbuild --loader=tsx parse OK after stripping the ReadCanvas wrapper, same as the Nov 13 file); block alone: page/d1118-block.ts (486 rows, unique IDs R2562–R3047).
