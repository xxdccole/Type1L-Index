# Daily pass 2026-11-13 — handoff

- Zone: America/Chicago. Additions: 670 verified records, R1892–R2561 (R1892 = the lead left open on Nov 12; R1893–R2561 = 669 new discovery records; R428 stays retired). Totals: 2,560 resources, 59 topics.
- Leads: queue before the pass had 1 open lead → resolved and promoted as R1892 (10.6052/j.issn.1000-4750.2021.01.0103, 工程力学/Engineering Mechanics 39(4):123–137, 2022; https publisher page returned 200 with citation metadata, CC BY 3.0; publisher issue pagination used, OpenAlex pagination differs). 676 new leads verified same run — 669 promoted, 4 rejected (duplicates: an ACI conference paper already indexed as R1185; two chapter-level records of the Broomfield book indexed as a whole; a duplicate printing of Hansson 1995), 3 open.
- Open leads (not index entries; retry next pass):
  - 10.5281/zenodo.23496439 "Assessment of the Carbon Footprint in the Clinker-Based Cement Production Process" — DOI 404 at doi.org/DataCite/Zenodo; journal host (journals.ayu.edu.kz) HTTP 500.
  - 10.4467/2353737XCT.14.077.2527 "Carbon nanotubes influence on the compressive strength of cement composites" (Czasopismo Techniczne) — Crossref prefix but no Crossref record; host HTTP 500.
  - 10.4467/2353737XCT.16.156.5767 "The effect of granulated fly ashes with phosphogypsum on the hardening of cement mortar" — same.
- Focus: binder-portland, scm-flyash, concrete-fibers, concrete-scc, concrete-architectural, concrete-polymer-refractory, concrete-pavement-pervious, concrete-repair-grout-overlay, concrete-precast-insitu-print, concrete-circular, concrete-hpc (least-covered rotation), Type IL legacy topics via PLC backfill (pavement, mix, field, mass, micro, apps, ttl), languages new to the rotation (it, nl, ru, pl, cs, tr, ko) plus de/fr/es/ja, 2026 current awareness, backward citation chase from 120 pre-2000 Nov 12 records and forward chase from R1634, R1686, R1704, R1713, R1744, R1747.
- Search yield: 105 + chase queries; 2,384 + 528 unique API hits; 928-row listing; 676 selected after dropping 49 no-DOI items whose pages could not be inspected (TRID 503, CiNii 500/202, JS-only DSpace/Primo, ROSA P 403).
- Access levels: {"doi_metadata": 440, "abstract_metadata": 217, "landing_page_inspected": 9, "catalog_metadata": 4}; languages: {"en": 641, "es": 7, "fr": 6, "de": 5, "tr": 4, "ru": 3, "zh": 1, "it": 1, "ko": 1, "pl": 1}. Provenance: 193 backward chase, 56 forward chase, 33 dated 2026, 23 in Type IL legacy topics.
- Decades: 1890s 2, 1900s 1, 1910s 1, 1930s 2, 1940s 8, 1950s 14, 1960s 15, 1970s 78, 1980s 107, 1990s 52, 2000s 143, 2010s 149, 2020s 98.
- Corrections to existing records: none. (Possible future correction: R1185 could carry its ACI DOI.)
- Repositories: OpenAlex works API (title.search with period splits; language filter; relevance search; referenced_works backward chase; cites: forward chase); Crossref works API (per-DOI); DataCite API; doi.org resolver (HEAD; handle API; RA lookup); ACI International Concrete Abstracts Portal (ACI 10.14359 DOIs that are not registered were verified on the portal, recorded as landing_page_inspected with listedDoi); NRC Publications Archive; Lund University Publications; REAL-EOD; IRIS Politecnico di Torino; Novye Ogneupory site; engineeringmechanics.cn.
- Full query log, periods, languages, citation chase, gaps and next steps: research/research-ledger.json (pass-2026-11-13). Pass scripts/logs: research/pass-2026-11-13/ (raw API hit dumps and landing HTML left out of the bundle for size).

## Validation (clone of xxdccole/Type1L-Index @ 2b9bc11 + working files, /tmp/t1l-v13)
- `scripts/build.py --validate`: valid: 2560 resources, 59 topics, 60 undated.
- `scripts/build.py`: index.html, 59 topic pages, sitemap.xml, llms.txt, 3 feeds (as of 2026-11-13).
- `scripts/check_site.py` with the unchanged script: **1 problem**, "home page still uses the Type IL-only document title". Cause: the guard searches the whole home HTML for the string "Portland-Limestone Cement (PLC)", and new record R2504 has that exact phrase in its real title ("Modeling of Hydration, Compressive Strength, and Carbonation of Portland-Limestone Cement (PLC) Concrete"). The home `<title>` is "Cement &amp; Concrete Index", so this is a false positive. The unchanged clean HEAD passes.
- Fix (bundled, publish with the data): scripts/check_site.py now applies that guard to the home `<title>` element only (diff: research/pass-2026-11-13/check_site-title-tag.patch). With the patch: checked 60 pages, site check passed, exit 0. The record title was not altered.

## Files to publish (bundle /workspace/publish-1113/publish-2026-11-13.tar.gz → repo paths)
| bundle path | repo path |
|---|---|
| stage/data/site-data.json | data/site-data.json |
| stage/data/resource-notes.json | data/resource-notes.json |
| stage/scripts/check_site.py | scripts/check_site.py (title-tag guard fix) |
| stage/research/index.md | research/index.md |
| stage/research/research-ledger.json | research/research-ledger.json |
| stage/research/candidates.jsonl | research/candidates.jsonl |
| stage/research/verified-sources.jsonl | research/verified-sources.jsonl |
| stage/research/DAILY-2026-11-13-HANDOFF.md | research/DAILY-2026-11-13-HANDOFF.md |
| stage/research/pass-2026-11-13/ | research/pass-2026-11-13/ |
Then run `python3 scripts/build.py --validate && python3 scripts/build.py && python3 scripts/check_site.py`, and commit the regenerated site files.

## Private Page patch
research/pass-2026-11-13/page/edit-ops.json, 24 ordered {step, old_string, new_string} ops written against canvas-2026-11-12-proposed.tsx (every old_string matched exactly once when applied in order):
- 4 ops insert the D1113 block (chunks D1113_A–D1113_N, 50 rows each) plus DAILY1113 before `const AXIS: AxisTopic[] = [`. Apply them in order; each re-inserts the anchor.
- RES.push and the topic loop gain `...DAILY1113`. Also updated: the scope line (Nov 13; 2,560 records; R1–R2561), the evidence callout, the What's new caption and row, the change log row, and the gaps row "Daily pass limits (Nov 13)".
- 12 AXIS takeaway pointers ("Nov 13 backfill: N records (Rx–Ry) …"). microcracking has no AXIS entry, so it was skipped.
- Result: page/canvas-2026-11-13-proposed.tsx; block alone: page/d1113-block.ts (node-checked: 670 rows, R1892–R2561, unique IDs).
