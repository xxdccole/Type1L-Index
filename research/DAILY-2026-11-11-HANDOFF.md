# Daily pass 2026-11-11 — handoff (America/Chicago)

Status: completed locally and validated. NOT published to GitHub. The Page has NOT been edited: ReadCanvas/EditCanvas were not available to the executor this run. A ready-to-apply patch is in research/pass-2026-11-11/page/.

## Result
- 147 verified additions, R1477–R1623 (1,475 → 1,622 resources; R428 still retired; 59 topics).
  - Old leads: R1477 Walraven & Reinhardt 1981 (HERON 26(1A)), R1478 Bache 1981 DSP (OSTI ETDEWEB 10168064), R1479 Gutt 1972 Aggregates from waste materials (TRID 106168).
  - Rejected: Nibbler, BRE CP 83/74 (off-topic: demolition equipment).
  - 144 discovery records R1480–R1623.
- Leads: 148 new leads found, all verified this run (144 promoted, 4 rejected as duplicate/superseded editions: ACI 223R-10→R178; RILEM AAC 1993 Spon→R828; ACI Mat J 1990 207.2R printing→R111; BSI 1947 ordinary/rapid-hardening PC→newer BSI record in this pass). Open leads: 0.
- Evidence: 48 abstract-level, 81 DOI metadata only, 14 catalogue records, 4 landing pages read. Nothing was read in full text.
- Languages: 144 en, 1 de, 1 ja, 1 ko (ja/ko descriptions are English glosses).
- Corrections to existing records: none.

## Files to publish (local → repo path)
| local (/workspace/type1l-index/) | repo |
|---|---|
| site-data.json | data/site-data.json |
| research/resource-notes.json | data/resource-notes.json |
| research/portable/verified-sources.jsonl | research/verified-sources.jsonl |
| research/portable/candidates.jsonl | research/candidates.jsonl |
| research-ledger.json | research/research-ledger.json |
| index.md | research/index.md |
After copying, run `python3 scripts/build.py`. It regenerates index.html, topics/*/index.html, feeds, sitemap.xml, llms.txt and added-dates.json; commit those too (70 files changed in the validation clone).
Optional provenance: research/pass-2026-11-11/ (scripts, search logs, triage, plan, verified-r1477-r1623.json).

## Validation (/tmp/t1l-validate, clone of HEAD faf26906cea2 at 2026-11-11 00:31 CST)
- `scripts/build.py --validate`: valid, 1622 resources, 59 topics, 60 undated (exit 0).
- `scripts/build.py` then `scripts/check_site.py`: "site check passed", 60 pages (exit 0). Running check_site before build reports stale-HTML problems; that is expected.
- The repo check_site.py already accepts status 'rejected' (line ~250). The 2026-11-10 patch is not needed.

## Page (canvas aa726421-3b9d-47e1-bf26-700f350c5345) — pending
- page/edit-ops.json: 9 exact old_string→new_string edits for EditCanvas:
  - D1111 block of 3 chunks (D1111_A–C) plus DAILY1111, inserted before `const EXTRA: Res[] = [`
  - RES.push and topic loop
  - scope line and evidence callout
  - What's new caption and row
  - change-log row
  - research gaps row
- page/canvas-2026-11-11-proposed.tsx: full proposed file, built from /workspace/lvpage/canvas_final.txt (Nov 10 state); it contains all 147 new IDs. Read the live canvas first; if it has drifted, apply the edits individually.

## Evidence limits
- TRID and TU Delft timed out, DTIC returned 403, J-GLOBAL 503 and SID 500. Records from these hosts were read via the search-index copy and are labelled catalog_metadata.
- ACI committee-report identities are inferred, not confirmed:
  - "Roller Compacted Mass Concrete" (1988) appears to be the ACI 207.5R report.
  - the 1992 "Guide for the Use of Preplaced Aggregate Concrete" appears to be ACI 304.1R-92.
  - Neither designation is registered with Crossref.
- Gutt 1972: month differs between sources (June vs Aug), so the record gives only the year.
- Three standard records (BSI, ASTM C926-26, ASTM C1697-26) have no Crossref issued date; their dates come from OpenAlex.
- No citation chasing this pass. That is the next-step priority.
