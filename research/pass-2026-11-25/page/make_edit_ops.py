"""Build Private Page edit-ops for the 2026-11-25 daily pass (D1125 / DAILY1125) against a FRESH ReadCanvas source.
Usage:  python3 make_edit_ops.py FRESH_SOURCE.tsx [OUT_DIR]
FRESH_SOURCE must already contain the Nov 22 changes (D1122 / DAILY1122, the Nov 22 scope line, evidence callout, what's-new row, change-log row and gaps row).
There is no fallback source: without an argument the script prints this text and exits. Dry run: page/canvas-2026-11-22-base-for-test.tsx (= /workspace/publish-1122/pageout/canvas-2026-11-22-proposed.tsx, the Nov 22 edit as proposed against the then-fresh Page).
Writes OUT_DIR/edit-ops.json (ordered {step, old_string, new_string}; apply in order, each old_string must match exactly once at that point),
OUT_DIR/canvas-2026-11-25-proposed.tsx and OUT_DIR/d1125-block.ts (OUT_DIR default: this script's folder). Fails loudly (SystemExit naming the step and the match count) if
any anchor is missing or ambiguous; nothing is written in that case.
Anchors: 'const AXIS: AxisTopic[] = [' (block insert); '...DAILY1121, ...DAILY1122);' and '...DAILY1121, ...DAILY1122]) {' (+DAILY1125); the Nov 22 scope line;
the Nov 22 evidence-callout ending 'the list now holds 111 leads and no leads remain open.'; the What's-new caption and Nov 22 row; the Nov 22 change-log row; the Nov 22 gaps row;
AXIS take pointers (only for topics that carry one on the Page; the others are listed as skipped)."""
import json,re,sys,os
if len(sys.argv)<2: raise SystemExit(__doc__)
HERE=os.path.dirname(os.path.abspath(__file__))
PD='/workspace/type1l-index/research/pass-2026-11-25/'
src=sys.argv[1]; OUT=(sys.argv[2] if len(sys.argv)>2 else HERE).rstrip('/')+'/'
base=open(src).read()
G=json.load(open(PD+'page-d1125.json')); SUM=G['summary']
rows=G['rows']; n=len(rows); first,last=rows[0][0],rows[-1][0]; total=G['total']
def js(s): return json.dumps(s,ensure_ascii=False)
def row(r):
    href=r[6]; href='doi:'+href[len('https://doi.org/'):] if href.startswith('https://doi.org/') else href
    return '['+', '.join(js(x) for x in r[:6]+[href])+']'
chunks=[rows[i:i+50] for i in range(0,n,50)]
letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
blocks=['// D1125_%s (%s–%s)\nD1125.push(\n%s\n);\n'%(letters[ci],ch[0][0],ch[-1][0],',\n'.join(row(r) for r in ch)) for ci,ch in enumerate(chunks)]
head='// 2026-11-25 daily pass (%s–%s): %d records — %d promoted from the review/retry list (%s), %d from the open queue (empty), %d new discovery records verified the same day (%s). Compact rows: [id,title,publisher,type,date,topicsCSV,href] — "doi:" expands to https://doi.org/.\nconst D1125: string[][] = [];\n'%(first,last,n,SUM['retryPromoted'],SUM['retryPromotedRange'],SUM['openQueuePromoted'],SUM['newPromoted'],SUM['discoveryRange'])
tail='const DAILY1125: Res[] = D1125.map((x) => ({ id: x[0], t: x[1], pub: x[2], type: x[3], date: x[4], topics: x[5] ? x[5].split(",") : [], href: x[6].startsWith("doi:") ? "https://doi.org/" + x[6].slice(4) : x[6] }));\n'
open(OUT+'d1125-block.ts','w').write(head+''.join(blocks)+tail)
A='const AXIS: AxisTopic[] = ['
ops=[]
groups=[blocks[i:i+3] for i in range(0,len(blocks),3)]
for gi,g in enumerate(groups):
    txt=(head if gi==0 else '')+''.join(g)+(tail if gi==len(groups)-1 else '')
    ops.append(dict(step='Insert D1125 block part %d/%d before AXIS'%(gi+1,len(groups)),old_string=A,new_string=txt+A))
ops.append(dict(step='RES push',old_string='...DAILY1121, ...DAILY1122);',new_string='...DAILY1121, ...DAILY1122, ...DAILY1125);'))
ops.append(dict(step='topic loop',old_string='...DAILY1121, ...DAILY1122]) {',new_string='...DAILY1121, ...DAILY1122, ...DAILY1125]) {'))
old_scope='Updated November 22, 2026 (America/Chicago): 4,581 resource records (R1–R4582; R428 retired before publication). The Nov 22 daily pass added R4295–R4582'
new_scope='Updated November 25, 2026 (America/Chicago): {:,} resource records (R1–{}; R428 retired before publication). The Nov 25 daily pass added {}–{} ({} promoted from the review/retry list, {}; open queue empty; then {} new discovery records verified the same day, {}). The Nov 22 daily pass added R4295–R4582'.format(total,last,first,last,SUM['retryPromoted'],SUM['retryPromotedRange'],SUM['newPromoted'],SUM['discoveryRange'])
ops.append(dict(step='scope line',old_string=old_scope,new_string=new_scope))
old_cb='the list now holds 111 leads and no leads remain open.'
new_cb=('On Nov 25 (after an unpublished partial Nov 23 run and no Nov 24 pass) the review/retry list was worked first: %d of its 111 leads were promoted (%s; opened on the Nov 25 retry: an ACI abstracts-portal record page, a CiNii record and a Brazilian journal page, the last two via Wayback copies), 1 was matched to the existing record R4354 (same NIST report) and %d stay on it after another retry; the open queue was empty; %d new leads were checked the same day (%d promoted %s, %d qualified but unavailable added to the review list, 1 rejected as a duplicate version); the list now holds %d leads and no leads remain open.'
  %(SUM["retryPromoted"],SUM["retryPromotedRange"],SUM["retryStill"],SUM["newLeads"],SUM["newPromoted"],SUM["discoveryRange"],SUM["retryNewDiscovery"],SUM["retryTotal"]))
ops.append(dict(step='evidence callout (+ review list link)',old_string=old_cb,new_string='the list then held 111 leads and no leads remained open. '+new_cb))
ops.append(dict(step='whats new caption',old_string='<Section heading="What\'s new" id="new" caption="Last updated Nov 22, 2026 (America/Chicago)">',new_string='<Section heading="What\'s new" id="new" caption="Last updated Nov 25, 2026 (America/Chicago)">'))
wn=G['news']; a='{ lead: "Nov 22", title: "Daily pass: 288 verified additions (R4295–R4582)'
ops.append(dict(step='whats new row',old_string=a,new_string='{ lead: %s, title: %s, detail: %s },\n          '%(js(wn['date']),js(wn['title']),js(wn['detail']))+a))
cl=G['change']; a='["2026-11-22", "Daily pass 2026-11-22: 288 verified additions'
ops.append(dict(step='changelog row',old_string=a,new_string='[%s, %s],\n          '%(js(cl['date']),js(cl['entry']))+a))
a='{ title: "Daily pass limits (Nov 22)"'
ops.append(dict(step='gaps row',old_string=a,new_string='{ title: "Daily pass limits (Nov 25)", detail: %s },\n            '%js(G['gap'])+a))
skipped=[]
for tid in G['takeaways']:
    m=re.search(r'\{key:"%s",[^\n]*?take:"((?:[^"\\]|\\.)*)"\}'%re.escape(tid),base)
    if not m: skipped.append(tid); continue
    ids=[r[0] for r in rows if tid in r[5].split(',')]
    if not ids: continue
    oldt=m.group(1)
    ops.append(dict(step='AXIS take '+tid,old_string='take:"%s"}'%oldt,new_string='take:"%s Nov 25 backfill: %d records (%s–%s), DOI/abstract/record-page/catalogue level."}'%(oldt,len(ids),ids[0],ids[-1])))
cur=base
for o in ops:
    c=cur.count(o['old_string'])
    if c!=1: raise SystemExit('FAIL at step "%s": old_string matches %d times (need exactly 1). Is the source the Page after the Nov 22 changes?'%(o['step'],c))
    cur=cur.replace(o['old_string'],o['new_string'],1)
missing=[r[0] for r in rows if ('"%s"'%r[0]) not in cur]
if missing: raise SystemExit('FAIL: %d new ids missing from the output, e.g. %s'%(len(missing),missing[:3]))
open(OUT+'canvas-2026-11-25-proposed.tsx','w').write(cur)
json.dump(ops,open(OUT+'edit-ops.json','w'),ensure_ascii=False,indent=1)
print(src,'->',len(ops),'ops; max new_string',max(len(o['new_string'].encode()) for o in ops),'bytes; skipped takes',skipped,'; all',n,'ids present')
