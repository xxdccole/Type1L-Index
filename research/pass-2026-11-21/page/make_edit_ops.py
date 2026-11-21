"""Build Private Page edit-ops for the 2026-11-21 daily pass (D1121 / DAILY1121) against a FRESH ReadCanvas source.
Usage:  python3 make_edit_ops.py FRESH_SOURCE.tsx [OUT_DIR]
Without an argument it falls back to page/canvas-2026-11-20-proposed.tsx (the Nov 20 edit as proposed; approximation, testing only).
Writes OUT_DIR/edit-ops.json (ordered {step, old_string, new_string}; apply in order, each old_string must match exactly once at that point),
OUT_DIR/canvas-2026-11-21-proposed.tsx and d1121-block.ts. Aborts naming the failing step if an anchor is missing or ambiguous.
Anchors: 'const AXIS: AxisTopic[] = [' (block insert); '...DAILY1119, ...DAILY1120);' and '...DAILY1119, ...DAILY1120]) {' (+DAILY1121);
Nov 20 scope line; Nov 20 evidence-callout ending 'the list now holds 61 leads and no leads remain open.'; What's-new caption/row; change-log row; gaps row;
13 AXIS take pointers (standards, dot, carbon, fresh, strength, durability, scm, pavement, apps, mix, field, supply, intl)."""
import json,re,sys,os
PD='/workspace/type1l-index/research/pass-2026-11-21/'
src=sys.argv[1] if len(sys.argv)>1 else '/workspace/type1l-index/research/pass-2026-11-21/page/canvas-2026-11-20-proposed.tsx'
OUT=sys.argv[2] if len(sys.argv)>2 else PD+'page/'
base=open(src).read()
G=json.load(open(PD+'page-d1121.json')); SUM=G['summary']
rows=G['rows']; n=len(rows); first,last=rows[0][0],rows[-1][0]; total=G['total']
def js(s): return json.dumps(s,ensure_ascii=False)
def row(r):
    href=r[6]; href='doi:'+href[len('https://doi.org/'):] if href.startswith('https://doi.org/') else href
    return '['+', '.join(js(x) for x in r[:6]+[href])+']'
chunks=[rows[i:i+50] for i in range(0,n,50)]
letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
blocks=['// D1121_%s (%s–%s)\nD1121.push(\n%s\n);\n'%(letters[ci],ch[0][0],ch[-1][0],',\n'.join(row(r) for r in ch)) for ci,ch in enumerate(chunks)]
head='// 2026-11-21 daily pass (%s–%s): %d records — %d promoted from the review/retry list (%s), 3 from the open queue, %d new discovery records verified the same day (%s). Compact rows: [id,title,publisher,type,date,topicsCSV,href] — "doi:" expands to https://doi.org/.\nconst D1121: string[][] = [];\n'%(first,last,n,SUM['retryPromoted'],SUM['retryPromotedRange'],SUM['newPromoted'],SUM['discoveryRange'])
tail='const DAILY1121: Res[] = D1121.map((x) => ({ id: x[0], t: x[1], pub: x[2], type: x[3], date: x[4], topics: x[5] ? x[5].split(",") : [], href: x[6].startsWith("doi:") ? "https://doi.org/" + x[6].slice(4) : x[6] }));\n'
open(OUT+'d1121-block.ts','w').write(head+''.join(blocks)+tail)
A='const AXIS: AxisTopic[] = ['
ops=[]
groups=[blocks[i:i+3] for i in range(0,len(blocks),3)]
for gi,g in enumerate(groups):
    txt=(head if gi==0 else '')+''.join(g)+(tail if gi==len(groups)-1 else '')
    ops.append(dict(step='Insert D1121 block part %d/%d before AXIS'%(gi+1,len(groups)),old_string=A,new_string=txt+A))
ops.append(dict(step='RES push',old_string='...DAILY1119, ...DAILY1120);',new_string='...DAILY1119, ...DAILY1120, ...DAILY1121);'))
ops.append(dict(step='topic loop',old_string='...DAILY1119, ...DAILY1120]) {',new_string='...DAILY1119, ...DAILY1120, ...DAILY1121]) {'))
old_scope='Updated November 20, 2026 (America/Chicago): 4,044 resource records (R1–R4045; R428 retired before publication). The Nov 20 daily pass added R3561–R4045'
new_scope='Updated November 21, 2026 (America/Chicago): {:,} resource records (R1–{}; R428 retired before publication). The Nov 21 daily pass added {}–{} ({} promoted from the review/retry list, {}; {} from the open queue; then {} new discovery records verified the same day, {}). The Nov 20 daily pass added R3561–R4045'.format(total,last,first,last,SUM['retryPromoted'],SUM['retryPromotedRange'],3,SUM['newPromoted'],SUM['discoveryRange'])
ops.append(dict(step='scope line',old_string=old_scope,new_string=new_scope))
old_cb='the list now holds 61 leads and no leads remain open.'
review_note=''
new_cb='On Nov 21 the review/retry list was worked first: %d of its 61 leads were promoted (%s; opened on the Nov 21 retry: an NRC Publications Archive record, a CiNii Books record and a Crossref DOI record) and %d stay on it after another retry; the 5 source leads that the reactions-table commit added to the repository were then checked (3 promoted R4049–R4051, 2 reference-data pages rejected); %d new leads were checked the same day (%d promoted %s, %d qualified but unavailable added to the review list); the list now holds %d leads and no leads remain open.'%(SUM["retryPromoted"],SUM["retryPromotedRange"],SUM["retryStill"],SUM["newLeads"],SUM["newPromoted"],SUM["discoveryRange"],SUM["retryNew"],SUM["retryTotal"])
ops.append(dict(step='evidence callout (+ review list link)',old_string=old_cb,new_string=new_cb))
ops.append(dict(step='whats new caption',old_string='<Section heading="What\'s new" id="new" caption="Last updated Nov 20, 2026 (America/Chicago)">',new_string='<Section heading="What\'s new" id="new" caption="Last updated Nov 21, 2026 (America/Chicago)">'))
wn=G['news']; a='          { lead: "Nov 20", title: "Daily pass: 485 verified additions (R3561–R4045)'
ops.append(dict(step='whats new row',old_string=a,new_string='          { lead: %s, title: %s, detail: %s },\n'%(js(wn['date']),js(wn['title']),js(wn['detail']))+a))
cl=G['change']; a='          ["2026-11-20", "Daily pass 2026-11-20: 485 verified additions'
ops.append(dict(step='changelog row',old_string=a,new_string='          [%s, %s],\n'%(js(cl['date']),js(cl['entry']))+a))
a='            { title: "Daily pass limits (Nov 20)"'
ops.append(dict(step='gaps row',old_string=a,new_string='            { title: "Daily pass limits (Nov 21)", detail: %s },\n'%js(G['gap'])+a))
skipped=[]
for tid in G['takeaways']:
    m=re.search(r'\{key:"%s",[^\n]*?take:"((?:[^"\\]|\\.)*)"\}'%re.escape(tid),base)
    if not m: skipped.append(tid); continue
    ids=[r[0] for r in rows if tid in r[5].split(',')]
    if not ids: continue
    oldt=m.group(1)
    newt=oldt+' Nov 21 backfill: %d records (%s–%s), DOI/abstract/record-page/catalogue level.'%(len(ids),ids[0],ids[-1])
    ops.append(dict(step='AXIS take '+tid,old_string='take:"%s"}'%oldt,new_string='take:"%s"}'%newt))
cur=base
for o in ops:
    c=cur.count(o['old_string'])
    if c!=1 and o['old_string'].startswith(' '):
        s=o['old_string'].lstrip(' ')
        if cur.count(s)==1: o['old_string']=s; o['new_string']=o['new_string'].lstrip(' ').replace('\n          ','\n',1) if False else o['new_string'].lstrip(' '); c=1
    assert c==1,(o['step'],c)
    cur=cur.replace(o['old_string'],o['new_string'],1)
open(OUT+'canvas-2026-11-21-proposed.tsx','w').write(cur)
json.dump(ops,open(OUT+'edit-ops.json','w'),ensure_ascii=False,indent=1)
missing=[r[0] for r in rows if ('"%s"'%r[0]) not in cur]
print(src,'->',len(ops),'ops; max new_string',max(len(o['new_string'].encode()) for o in ops),'bytes; skipped takes',skipped,'missing ids',len(missing),'review note added' if review_note else 'review link already present')
