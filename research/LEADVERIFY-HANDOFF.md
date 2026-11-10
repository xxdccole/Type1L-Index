# Lead verification pass handoff — 2026-11-10 (America/Chicago)
Owner instruction (Nov 10): unverified leads are verified immediately; the daily pass is discovery only.

## Result
- Processed all 1,255 open leads in research/portable/candidates.jsonl.
- Promoted 1,109 verified records **R367–R1476** (R428 was withdrawn before publication as an off-topic false positive — "Advancements" matched "cement"; its lead is rejected and the ID retired). R1–R366 are unchanged (IDs, URLs, titles, topics, notes).
- Rejected 138 with reasons: 75 off-topic, 58 duplicates (same DOI or title as an existing R, superseded or alternate standard editions, other registrations of the same work, umbrella leads), 3 not real sources (front matter or a book index), 1 retracted, 1 relevance not established.
- 4 leads were the same work as another lead: status `matched-verified`, topics merged.
- Still open: 4, each with an `openReason` (TU Delft timeout; CiNii 500; TRID 503 ×2, none with an abstract).
- Totals: 1,475 resources and 59 topics. `lastUpdated` is 2026-11-10. Membership union holds on both sides.

## Files to publish (local path → repo path)
- site-data.json → data/site-data.json
- research/resource-notes.json → data/resource-notes.json (+R367–R1476; each note equals its verified-sources `evidenceNote`)
- research/portable/verified-sources.jsonl → research/verified-sources.jsonl
  - Also fixes R200's local `evidenceNote` to match the note already on the repo.
- research/portable/candidates.jsonl → research/candidates.jsonl
  - New status `rejected` with `rejectCategory` / `rejectReason` / `duplicateOf`.
  - Every reviewed line has `reviewedOn` and `reviewPass`.
- research-ledger.json → research/research-ledger.json
  - Pass `pass-2026-11-10-leadverify`, topic `resourceIds`/counts, stats.
  - New `policy.leadVerification`.
- index.md → research/index.md
  - Header line, new section "2026-11-10 — lead verification pass" with the record list and rejected list.
  - Line 327 R187 is restored to "(Avet, Scrivener)", matching the repo.
- **scripts/check_site.py**: REQUIRED.
  - The current checker rejects any status other than candidate, promoted or matched-verified.
  - The patch accepts `rejected`, requires `rejectReason`, and checks that `duplicateOf` IDs exist.
  - Patched file: research/pass-2026-11-10-leadverify/check_site.py
  - Diff: check_site-rejected-status.patch
- research/pass-2026-11-10-leadverify/ (provenance) → research/pass-2026-11-10-leadverify/:
  - Fetch scripts: fetch.py, fetch_nodoi.py, probe_nodoi.py, fetch_extra.py
  - Planning and apply scripts: common.py, triage.py, decisions.py, lv_build.py, apply.py
  - Data and outputs: lead-meta.json, nodoi-meta.json, extra-meta.json, triage.json, plan.json, verified-r367-r1476.json, apply-summary.json, page-leadverify-patch.js
- Optional local mirrors: research/portable/verified-sources.json and candidates.json.

## Validation (local clone of main with these files)
- `scripts/build.py --validate`: valid, 1,475 resources, 59 topics.
- Build: OK, 59 topic pages and 3 feeds.
- `scripts/check_site.py` (patched): site check passed.
- With the unpatched checker, the only failure is "unknown status 'rejected'" ×137.

## Evidence level and limits
- Access levels: 693 `abstract_metadata`, 407 `doi_metadata`, 6 `catalog_metadata`, 3 `landing_page_inspected`.
- Nothing was full-text reviewed.
- Descriptions are the opening sentences of the registered abstract. Without an abstract, the description is a metadata-only statement.
- Topics are the lead's queued topic plus title-keyword rules on the binder, SCM, concrete and cross axes. Type IL collection topics were not auto-assigned.
- Geography comes from OpenAlex affiliation countries, otherwise null.
- Standards: one record per document, at the latest edition registered in Crossref.
  - ASTM C845, C1600 and C1866 editions close against R179, R180 and R185.
  - BSI CAC closes against R181 (EN 14647).
  - BSI records carry no BS/EN designation in Crossref; it is marked unknown.
- Blocked or limited hosts:
  - TRID 503; TU Delft timeout; Deep Blue, Curtin and UOW 403; UPC 418.
  - Items behind them with a registered abstract were promoted at abstract level.
- IDEALS and the UT repository were reachable this time. That resolved the pass-3 manual leads: Talbot 1907 → promoted, Hilsdorf 1970, Riding 2007, K. Mather 1980 and the UPenn theses.
- Backups: research/backups/pre-leadverify-2026-11-10/.

## Page
- Updated in place on 2026-11-10 (canvas aa726421-3b9d-47e1-bf26-700f350c5345), in 17 EditCanvas calls:
  - Scaffolding: `const LV: string[][]`, 12 compact chunks LEADVERIFY_A–LEADVERIFY_L (`LV.push(...)` rows of [id,title,publisher,type,date,topicsCSV,href]), and `LEADVERIFY = LV.map(...)`. It is merged with `RES.push(..., ...DEEP3, ...LEADVERIFY)` and added to the topic loop.
  - Text: the scope line now says 1,475 records (R1–R1476; R428 retired), and the evidence-boundary callout says the queue was cleared. Added a What's new row (LEADVERIFY_NEWS), a change-log row and a Research gaps row.
- Verified with ReadCanvas: all 1,109 LV rows match /workspace/lvpage/chunk00–11.txt exactly. The page holds 1,475 distinct IDs (R1–R1476 minus R428), including R367 and R1476.
- Note: research/pass-2026-11-10-leadverify/verified-r367-r1476.json is the pre-fix build output and still contains R428 (1,110 rows). The published data files and the Page exclude it.
