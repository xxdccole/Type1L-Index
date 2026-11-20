"""Build Private Page edit-ops for the 2026-11-20 daily pass against a FRESH ReadCanvas source.
Usage:  python3 make_edit_ops.py FRESH_SOURCE.tsx [OUT_DIR]
  FRESH_SOURCE.tsx = the current live Page source exactly as ReadCanvas returns it (wrapper stripped or not; only anchor strings matter).
  Without an argument it falls back to research/pass-2026-11-19/page/live-applied.tsx (an approximation, for testing only).
Writes OUT_DIR/edit-ops.json (ordered {step, old_string, new_string}; apply in order, each old_string must match exactly once in the
current text at that point), OUT_DIR/canvas-2026-11-20-proposed.tsx (the fresh source with all ops applied) and d1120-block.ts.
Anchors (all checked here; the script aborts with the failing step if an anchor is missing or ambiguous):
  1. 'const AXIS: AxisTopic[] = ['  -> D1120 block (chunks of <=50 rows, <=3 chunks per op) + DAILY1120 inserted before it (re-inserted each op)
  2. '...DAILY1118, ...DAILY1119);'  (RES.push)      -> adds ', ...DAILY1120'
  3. '...DAILY1118, ...DAILY1119]) {' (topic loop)   -> adds ', ...DAILY1120'
  4. 'Updated November 19, 2026 (America/Chicago): 3,559 resource records (R1–R3560; R428 retired before publication). The Nov 19 daily pass added R3048–R3560'  (scope line)
  5. '67 rejected as unverifiable — no-DOI hits whose landing or catalogue pages could not be inspected); no leads remain open.'  (evidence callout; adds Nov 20 sentence + review-list link)
  6. '<Section heading="What\\'s new" id="new" caption="Last updated Nov 19, 2026 (America/Chicago)">'  (caption)
  7. '          { lead: "Nov 19", title: "Daily pass: 513 verified additions (R3048–R3560)",'  (What's new row inserted before)
  8. '          ["2026-11-19", "Daily pass 2026-11-19: 513 verified additions'  (change-log row inserted before)
  9. '            { title: "Daily pass limits (Nov 19)"'  (gaps row inserted before)
 10. AXIS takeaways: for each of the 13 focus topics, the current take:"..." of {key:"<topic>",...} gets ' Nov 20 backfill: N records (Rx–Ry), ...' appended.
 11. Review-list note: if 'Type1L-Index/review/' is absent, the evidence-callout sentence (op 5) carries the link.
Leading whitespace of anchors 7–9 must match the fresh source; if ReadCanvas returns different indentation, the script retries the anchor stripped of leading spaces."""
import json,re,sys,os
PD='/workspace/type1l-index/research/pass-2026-11-20/'
src=sys.argv[1] if len(sys.argv)>1 else '/workspace/type1l-index/research/pass-2026-11-19/page/live-applied.tsx'
OUT=sys.argv[2] if len(sys.argv)>2 else PD+'page/'
base=open(src).read()
G=json.load(open(PD+'page-d1120.json')); SUM=G['summary']
rows=G['rows']; n=len(rows); first,last=rows[0][0],rows[-1][0]; total=G['total']
def js(s): return json.dumps(s,ensure_ascii=False)
def row(r):
    href=r[6]; href='doi:'+href[len('https://doi.org/'):] if href.startswith('https://doi.org/') else href
    return '['+', '.join(js(x) for x in r[:6]+[href])+']'
chunks=[rows[i:i+50] for i in range(0,n,50)]
letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
blocks=['// D1120_%s (%s–%s)\nD1120.push(\n%s\n);\n'%(letters[ci],ch[0][0],ch[-1][0],',\n'.join(row(r) for r in ch)) for ci,ch in enumerate(chunks)]
head='// 2026-11-20 daily pass (%s–%s): %d records — %d promoted from the review/retry list (%s), %d new discovery records verified the same day (%s). Compact rows: [id,title,publisher,type,date,topicsCSV,href] — "doi:" expands to https://doi.org/.\nconst D1120: string[][] = [];\n'%(first,last,n,SUM['retryPromoted'],SUM['retryPromotedRange'],SUM['newPromoted'],SUM['discoveryRange'])
tail='const DAILY1120: Res[] = D1120.map((x) => ({ id: x[0], t: x[1], pub: x[2], type: x[3], date: x[4], topics: x[5] ? x[5].split(",") : [], href: x[6].startsWith("doi:") ? "https://doi.org/" + x[6].slice(4) : x[6] }));\n'
open(OUT+'d1120-block.ts','w').write(head+''.join(blocks)+tail)
A='const AXIS: AxisTopic[] = ['
ops=[]
groups=[blocks[i:i+3] for i in range(0,len(blocks),3)]
for gi,g in enumerate(groups):
    txt=(head if gi==0 else '')+''.join(g)+(tail if gi==len(groups)-1 else '')
    ops.append(dict(step='Insert D1120 block part %d/%d before AXIS'%(gi+1,len(groups)),old_string=A,new_string=txt+A))
ops.append(dict(step='RES push',old_string='...DAILY1118, ...DAILY1119);',new_string='...DAILY1118, ...DAILY1119, ...DAILY1120);'))
ops.append(dict(step='topic loop',old_string='...DAILY1118, ...DAILY1119]) {',new_string='...DAILY1118, ...DAILY1119, ...DAILY1120]) {'))
old_scope='Updated November 19, 2026 (America/Chicago): 3,559 resource records (R1–R3560; R428 retired before publication). The Nov 19 daily pass added R3048–R3560'
new_scope='Updated November 20, 2026 (America/Chicago): {:,} resource records (R1–{}; R428 retired before publication). The Nov 20 daily pass added {}–{} ({} promoted from the review/retry list, {}, then {} new discovery records verified the same day, {}). The Nov 19 daily pass added R3048–R3560'.format(total,last,first,last,SUM['retryPromoted'],SUM['retryPromotedRange'],SUM['newPromoted'],SUM['discoveryRange'])
ops.append(dict(step='scope line',old_string=old_scope,new_string=new_scope))
old_cb='67 rejected as unverifiable — no-DOI hits whose landing or catalogue pages could not be inspected); no leads remain open.'
review_note='' if 'Type1L-Index/review/' in base else ' Leads that look real but could not be inspected yet are listed, unverified and without R numbers, at https://xxdccole.github.io/Type1L-Index/review/ (research/review-retry.md).'
new_cb=old_cb+' On Nov 20 the review/retry list was worked first: %d of its 163 leads were promoted (%s; %d with re-confirmed 2026-11-19 evidence, %d opened on the Nov 20 retry) and %d stay on it after another retry; then %d new leads were checked the same day (%d promoted %s, %d qualified but unavailable added to the review list%s); the list now holds %d leads and no leads remain open.%s'%(SUM['retryPromoted'],SUM['retryPromotedRange'],SUM['retryReconfirmed'],SUM['retryOpenedToday'],SUM['retryStill'],SUM['newLeads'],SUM['newPromoted'],SUM['discoveryRange'],SUM['retryNew'],(', %d rejected as duplicates of leads already on the list'%SUM['newRejectedDup']) if SUM.get('newRejectedDup') else '',SUM['retryTotal'],review_note)
ops.append(dict(step='evidence callout (+ review list link)',old_string=old_cb,new_string=new_cb))
ops.append(dict(step='whats new caption',old_string='<Section heading="What\'s new" id="new" caption="Last updated Nov 19, 2026 (America/Chicago)">',new_string='<Section heading="What\'s new" id="new" caption="Last updated Nov 20, 2026 (America/Chicago)">'))
wn=G['news']; a='          { lead: "Nov 19", title: "Daily pass: 513 verified additions (R3048–R3560)",'
ops.append(dict(step='whats new row',old_string=a,new_string='          { lead: %s, title: %s, detail: %s },\n'%(js(wn['date']),js(wn['title']),js(wn['detail']))+a))
cl=G['change']; a='          ["2026-11-19", "Daily pass 2026-11-19: 513 verified additions'
ops.append(dict(step='changelog row',old_string=a,new_string='          [%s, %s],\n'%(js(cl['date']),js(cl['entry']))+a))
a='            { title: "Daily pass limits (Nov 19)"'
ops.append(dict(step='gaps row',old_string=a,new_string='            { title: "Daily pass limits (Nov 20)", detail: %s },\n'%js(G['gap'])+a))
skipped=[]
for tid in G['takeaways']:
    m=re.search(r'\{key:"%s",[^\n]*?take:"((?:[^"\\]|\\.)*)"\}'%re.escape(tid),base)
    if not m: skipped.append(tid); continue
    ids=[r[0] for r in rows if tid in r[5].split(',')]
    if not ids: continue
    oldt=m.group(1)
    newt=oldt+' Nov 20 backfill: %d records (%s–%s), DOI/abstract/record-page/catalogue level.'%(len(ids),ids[0],ids[-1])
    ops.append(dict(step='AXIS take '+tid,old_string='take:"%s"}'%oldt,new_string='take:"%s"}'%newt))
cur=base
for o in ops:
    c=cur.count(o['old_string'])
    if c!=1 and o['old_string'].startswith(' '):
        s=o['old_string'].lstrip(' ')
        if cur.count(s)==1: o['old_string']=s; o['new_string']=o['new_string'].lstrip(' ').replace('\n          ','\n',1) if False else o['new_string'].lstrip(' '); c=1
    assert c==1,(o['step'],c)
    cur=cur.replace(o['old_string'],o['new_string'],1)
open(OUT+'canvas-2026-11-20-proposed.tsx','w').write(cur)
json.dump(ops,open(OUT+'edit-ops.json','w'),ensure_ascii=False,indent=1)
missing=[r[0] for r in rows if ('"%s"'%r[0]) not in cur]
print(src,'->',len(ops),'ops; max new_string',max(len(o['new_string'].encode()) for o in ops),'bytes; skipped takes',skipped,'missing ids',len(missing),'review note added' if review_note else 'review link already present')
