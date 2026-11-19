"""Build Page edit-ops for 2026-11-19 (same format as pass-2026-11-18/page/edit-ops.json) against the current live Page source
(= Nov 13 proposed canvas + Nov 18 edit-ops applied; reconstructed as canvas-2026-11-18-live.tsx), apply them sequentially to produce
canvas-2026-11-19-proposed.tsx, and check each old_string matches exactly once."""
import json,re
PD='/workspace/type1l-index/research/pass-2026-11-19/'
R='/workspace/type1l-index/research/'
base13=open(R+'pass-2026-11-13/page/canvas-2026-11-13-proposed.tsx').read()
cur=base13
for o in json.load(open(R+'pass-2026-11-18/page/edit-ops.json')):
    assert cur.count(o['old_string'])==1,o['step']; cur=cur.replace(o['old_string'],o['new_string'],1)
assert cur==open(R+'pass-2026-11-18/page/canvas-2026-11-18-proposed.tsx').read()
open(PD+'page/canvas-2026-11-18-live.tsx','w').write(cur)
base=cur
G=json.load(open(PD+'page-d1119.json')); SUM=json.load(open(PD+'apply-summary.json'))
rows=G['rows']; n=len(rows); first,last=rows[0][0],rows[-1][0]; total=G['total']
def js(s): return json.dumps(s,ensure_ascii=False)
def row(r):
    href=r[6]; href='doi:'+href[len('https://doi.org/'):] if href.startswith('https://doi.org/') else href
    return '['+', '.join(js(x) for x in r[:6]+[href])+']'
chunks=[rows[i:i+50] for i in range(0,n,50)]
letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
blocks=[]
for ci,ch in enumerate(chunks):
    blocks.append('// D1119_%s (%s–%s)\nD1119.push(\n%s\n);\n'%(letters[ci],ch[0][0],ch[-1][0],',\n'.join(row(r) for r in ch)))
head='// 2026-11-19 daily pass (%s–%s): %d discovery records verified same day (no open leads at start). Compact rows: [id,title,publisher,type,date,topicsCSV,href] — "doi:" expands to https://doi.org/.\nconst D1119: string[][] = [];\n'%(first,last,n)
tail='const DAILY1119: Res[] = D1119.map((x) => ({ id: x[0], t: x[1], pub: x[2], type: x[3], date: x[4], topics: x[5] ? x[5].split(",") : [], href: x[6].startsWith("doi:") ? "https://doi.org/" + x[6].slice(4) : x[6] }));\n'
open(PD+'page/d1119-block.ts','w').write(head+''.join(blocks)+tail)
A='const AXIS: AxisTopic[] = ['
ops=[]
groups=[blocks[i:i+3] for i in range(0,len(blocks),3)]
for gi,g in enumerate(groups):
    txt=(head if gi==0 else '')+''.join(g)+(tail if gi==len(groups)-1 else '')
    ops.append(dict(step='Insert D1119 block part %d/%d before AXIS'%(gi+1,len(groups)),old_string=A,new_string=txt+A))
ops.append(dict(step='RES push',old_string='...DAILY1113, ...DAILY1118);',new_string='...DAILY1113, ...DAILY1118, ...DAILY1119);'))
ops.append(dict(step='topic loop',old_string='...DAILY1113, ...DAILY1118]) {',new_string='...DAILY1113, ...DAILY1118, ...DAILY1119]) {'))
old_scope='Updated November 18, 2026 (America/Chicago): 3,046 resource records (R1–R3047; R428 retired before publication). The Nov 18 daily pass added R2562–R3047'
new_scope='Updated November 19, 2026 (America/Chicago): {:,} resource records (R1–{}; R428 retired before publication). The Nov 19 daily pass added {}–{} ({} new discovery records verified the same day, incl. backward/forward citation chases, library-catalogue records for classic texts and non-English sources). The Nov 18 daily pass added R2562–R3047'.format(total,last,first,last,n)
ops.append(dict(step='scope line',old_string=old_scope,new_string=new_scope))
old_cb='7 rejected as unverifiable); no leads remain open.'
new_cb='7 rejected as unverifiable); no leads remain open. On Nov 19 no leads were open at the start; %d new leads were checked the same day (%d promoted %s–%s, %d rejected as unverifiable — no-DOI hits whose landing or catalogue pages could not be inspected); no leads remain open.'%(SUM['newLeads'],SUM['newPromoted'],first,last,SUM['newRejected'])
ops.append(dict(step='evidence callout',old_string=old_cb,new_string=new_cb))
ops.append(dict(step='whats new caption',old_string='<Section heading="What\'s new" id="new" caption="Last updated Nov 18, 2026 (America/Chicago)">',new_string='<Section heading="What\'s new" id="new" caption="Last updated Nov 19, 2026 (America/Chicago)">'))
wn=G['news']; a='          { lead: "Nov 18", title: "Daily pass: 486 verified additions (R2562–R3047)",'
ops.append(dict(step='whats new row',old_string=a,new_string='          { lead: %s, title: %s, detail: %s },\n'%(js(wn['date']),js(wn['title']),js(wn['detail']))+a))
cl=G['change']; a='          ["2026-11-18", "Daily pass 2026-11-18: 486 verified additions'
ops.append(dict(step='changelog row',old_string=a,new_string='          [%s, %s],\n'%(js(cl['date']),js(cl['entry']))+a))
a='            { title: "Daily pass limits (Nov 18)"'
ops.append(dict(step='gaps row',old_string=a,new_string='            { title: "Daily pass limits (Nov 19)", detail: %s },\n'%js(G['gap'])+a))
skipped=[]
for tid in G['takeaways']:
    m=re.search(r'\{key:"%s",[^\n]*?take:"((?:[^"\\]|\\.)*)"\}'%re.escape(tid),base)
    if not m: skipped.append(tid); continue
    ids=[r[0] for r in rows if tid in r[5].split(',')]
    oldt=m.group(1)
    newt=oldt+' Nov 19 backfill: %d records (%s–%s), DOI/abstract/catalogue level.'%(len(ids),ids[0],ids[-1])
    ops.append(dict(step='AXIS take '+tid,old_string='take:"%s"}'%oldt,new_string='take:"%s"}'%newt))
cur=base
for o in ops:
    c=cur.count(o['old_string'])
    assert c==1,(o['step'],c)
    cur=cur.replace(o['old_string'],o['new_string'],1)
open(PD+'page/canvas-2026-11-19-proposed.tsx','w').write(cur)
json.dump(ops,open(PD+'page/edit-ops.json','w'),ensure_ascii=False,indent=1)
missing=[r[0] for r in rows if ('"%s"'%r[0]) not in cur]
print(len(ops),'ops; max new_string',max(len(o['new_string'].encode()) for o in ops),'skipped takes',skipped,'missing ids',len(missing))
