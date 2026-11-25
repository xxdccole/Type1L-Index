# Daily pass 2026-11-25 — handoff

- Zone: America/Chicago. Started from the Nov 22 published state (site-data lastUpdated 2026-11-22, 4,581 resources, R1–R4582, R428 retired, review list 111, 0 open candidates). Before any work the live repo main (xxdccole/Type1L-Index @ 344403e "Build site", after 5012467 "Daily pass 2026-11-22") was cloned read-only to /tmp/t1l-live25 and diffed against the box working files: `data/site-data.json`, `data/resource-notes.json`, `research/index.md`, `research/research-ledger.json`, `research/verified-sources.jsonl`, `research/review-retry.{md,jsonl}` and `research/candidates.jsonl` are all byte-identical to the box. No repo-only changes to merge. Repo-only files (reactions, calculator, scripts, header nav, `data/reactions.json`) are not in the bundle and stay untouched.
- Earlier runs: research/pass-2026-11-23/ is a partial run from Nov 23 that stopped about 06:51 before build/apply. Nothing from it reached the working files or the repo. No pass ran on Nov 24. This pass reused its OpenAlex harvest (api-hits/new-hits, listing, screening in select.py). Every lead was re-verified on 2026-11-25 (Crossref/DataCite, doi.org, landing pages, alternative routes). The retry list was retried from scratch today.
- Additions: **326 verified records, R4583–R4908** (3 from the review list, 323 from discovery). R428 stays retired. **Totals: 4,907 resources, 59 topics.** No corrections to existing records: apply.py asserts that R1–R4582 are byte-identical, and topic objects changed only by appended resourceIds/takeaways.
- Step 1, retry list (111 leads at start): all 111 were retried. retry_a.py covered OpenAlex locations, DOI via Crossref/DataCite/doi.org, direct https, handle.net and Wayback. retry_b.py, run in 4 slices, covered DOAJ, DSpace 7, NVA, DiVA, theses.fr, CiNii OpenSearch, Open Library, Crossref search, Google Books and Semantic Scholar. **3 promoted (R4583–R4585):**
  - R4583: Miura & Takeda 1993, "Application of Super Workable Concrete…", from its ACI abstracts-portal page.
  - R4584: Yamane & Chun 2019, JSCE deep-learning crack segmentation, from a Wayback copy of the CiNii record.
  - R4585: Brazilian Journal of Development 2021 recycled-sand mortar paper, from a Wayback copy of the journal page.
  - **1 matched to an existing record:** Phan, "Fire Performance of High-Strength Concrete" (NIST 1996). It opened through a Wayback copy of an Open Library record, but it is the same report as R4354 (NIST IR 5934, added Nov 22). It is now `matched-verified`, matchedTo R4354, with no new ID.
  - 8 more leads got only Semantic Scholar aggregator hits. These were recorded but not counted as inspection.
  - 107 remain, with lastTried 2026-11-25, attempts +1 and urlsTried/retryLog appended.
- Step 2, open queue: 0 open candidates at start, so nothing to process.
- Step 3, discovery: 342 leads were checked.
  - Sources: 294 listing rows from the Nov 23 harvest, minus 9 excluded at screening (select.py), plus 57 rows hand-picked from a 211-row current-awareness sweep run today (harvest_c.py: 9 OpenAlex queries for 2026-11-10/15/20/23 → 2026-11-25; listing-c.txt; listing-b-keys.json).
  - Outcomes: **323 promoted (R4586–R4908)**. **18 qualified-but-unavailable leads added to the review list**: 2 unregistered DOIs (ACI 10.14359/6402, DergiPark 10.16984/saufbed.12176) and 16 no-DOI leads (BazTech/yadda 403 ×5, TRID ×3, J-GLOBAL ×2, CQVIP, Structurae, Croatian/Spanish/Indonesian repositories). **1 rejected:** the OSTI record (PB-84-217694) of the 1983 World Bank "Energy efficiency and fuel substitution in the cement industry" is a second version of the CiNii-catalogued publication promoted the same day; the OSTI link is kept as an alternate identifier. 0 left open.
  - Other corrections from the inspected pages:
    - The NRC record "A new model for hydrated Portland cement…" took its date from the page's "date modified" (2026-11-25). It was corrected from the record to Feldman & Sereda, Engineering Journal 53(8-9):53-59, 1970-10-01, English.
    - The Amazon retail page for "Euro-Cements" (Dhir & Jones 1994) was not used as evidence. The Open Library work record is used instead (post_nl.py).
    - Theses.fr title suffix removed.
    - Repository-vs-OpenAlex year conflicts are noted in the evidence of two Spanish records.
- Focus (rotation head after the Nov 22 head; news/gaps/guides skipped as meta topics): scm-natural, binder-international, binder-blended, concrete-structural, cross-tests-codes, cross-environment-cost, cross-chemistry, cross-mix, cross-mechanics, scm-limestone, cross-durability, concrete-polymer-refractory, concrete-scc.
  - Also covered: historical searches; languages es, pt, de, fr, ja, zh, ru, ko, id, it, pl, tr, vi; backward chase (3,108 seeds, 8,725 refs) and forward chase (35 seeds).
  - Notable additions:
    - 2026 Type IL/PLC work: UIC thesis on PLC with >15% limestone, Type IL(HE) vs Type III, Type IL paste under acid attack.
    - Thaumasite in limestone cements.
    - Classic C-S-H/NMR and creep/shrinkage papers.
    - Eurocode 2 items.
    - Historical cement-industry reports from the UK, Mexico, the World Bank, NASA and the 1917 USDA potash study.
    - German hydration literature back to 1903.
- Access levels (all 326): abstract_metadata 158, doi_metadata 130, landing_page_inspected 28, catalog_metadata 10.
  - Types: Paper 278, Review paper 12, Thesis 12, Book 11, Report 6, Book chapter 4, Preprint 2, Standard 1.
  - Languages: en 276, pt 7, de 7, id 6, vi 6, it 6, ja 5, es 5, fr 5, tr 3. Non-English records carry title-level English glosses (mkgloss.py).
  - Other counts: 38 no-DOI records; 79 dated 2026; 64 backward-chase and 28 forward-chase records.
- Topic fixes in build.py: glosses are used for topic inference; spurious concrete-structural (from "structure") and concrete-polymer-refractory (from "geopolymer") tags are dropped unless the title supports them; a keyword fallback replaces bare cross-chemistry where the title is mechanical or durability. Manual overrides are in overrides.json.
- Review list: research/review-retry.md/.jsonl regenerated (mkmd.py). **125 leads** (107 carried over, 18 new). Page: https://xxdccole.github.io/Type1L-Index/review/.
- Ledger: pass record pass-2026-11-25 with Nov 23 queries (runDate noted) and Nov 25 current queries. prior-queries-all.json updated in this folder. Focus topics were rotated to the end of globalNextQueue.

## Validation (fresh clone of main @ 344403e + working files, /tmp/t1l-v25; nothing pushed by this run)
- `python3 scripts/build.py --validate`: valid: 4907 resources, 59 topics, 62 undated.
- `python3 scripts/build.py`: built index.html, 59 topic pages, sitemap.xml, llms.txt and 3 feeds (as of 2026-11-25). review/index.html shows "125 leads · unverified, not index resources".
- `python3 scripts/check_site.py`: checked 60 pages and 2 reaction pages; site check passed. The build also rewrites the footer date in reactions/index.html and calculator/index.html; commit those too.

## Files to publish
See /workspace/publish-1125/FILES.md (bundle publish-2026-11-25.tar.gz, same layout as Nov 22). Expected live check: R4583 (first new) and R4908 (last), 4,907 resources, lastUpdated 2026-11-25, R428 absent, review page 125 leads, reactions/ and calculator/ load.

## Private Page patch
Run `research/pass-2026-11-25/page/make_edit_ops.py FRESH_SOURCE.tsx [OUT_DIR]`. It builds edit-ops.json (24 ordered {step, old_string, new_string}), d1125-block.ts and canvas-2026-11-25-proposed.tsx. FRESH_SOURCE must already contain the Nov 22 edits (DAILY1122 etc.). The script exits loudly if any anchor does not match exactly once.

Dry run against page/canvas-2026-11-22-base-for-test.tsx (= /workspace/publish-1122/pageout/canvas-2026-11-22-proposed.tsx): all 24 anchors matched once, all 13 AXIS takes found, output parses with esbuild and all 326 IDs are present. This run had no Page read/edit tool, so **the Page was NOT edited**.
