"""Build Page edit-ops for 2026-11-13 (same format as pass-2026-11-12/page/edit-ops.json) against the Nov 12 proposed canvas,
apply them sequentially to produce canvas-2026-11-13-proposed.tsx, and check each old_string matches exactly once."""
import json,re,collections
PD='/workspace/type1l-index/research/pass-2026-11-13/'
base=open('/workspace/type1l-index/research/pass-2026-11-12/page/canvas-2026-11-12-proposed.tsx').read()
G=json.load(open(PD+'page-d1113.json')); S=json.load(open('/workspace/type1l-index/site-data.json'))
SUM=json.load(open(PD+'apply-summary.json'))
rows=G['rows']; n=len(rows); first,last=rows[0][0],rows[-1][0]; total=G['total']
def js(s): return json.dumps(s,ensure_ascii=False)
def row(r):
    href=r[6]; href='doi:'+href[len('https://doi.org/'):] if href.startswith('https://doi.org/') else href
    return '['+', '.join(js(x) for x in r[:6]+[href])+']'
chunks=[rows[i:i+50] for i in range(0,n,50)]
letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
blocks=[]
for ci,ch in enumerate(chunks):
    blocks.append('// D1113_%s (%s–%s)\nD1113.push(\n%s\n);\n'%(letters[ci],ch[0][0],ch[-1][0],',\n'.join(row(r) for r in ch)))
head='// 2026-11-13 daily pass (%s–%s): 1 resolved open lead (%s) + %d discovery records verified same day. Compact rows: [id,title,publisher,type,date,topicsCSV,href] — "doi:" expands to https://doi.org/.\nconst D1113: string[][] = [];\n'%(first,last,first,n-1)
tail='const DAILY1113: Res[] = D1113.map((x) => ({ id: x[0], t: x[1], pub: x[2], type: x[3], date: x[4], topics: x[5] ? x[5].split(",") : [], href: x[6].startsWith("doi:") ? "https://doi.org/" + x[6].slice(4) : x[6] }));\n'
open('d1113-block.ts','w').write(head+''.join(blocks)+tail)
A='const AXIS: AxisTopic[] = ['
ops=[]
# split the block insertion into several ops (each <= 4 chunks) so no single edit is too large; each inserts before AXIS, preserving order
groups=[blocks[i:i+4] for i in range(0,len(blocks),4)]
for gi,g in enumerate(groups):
    txt=(head if gi==0 else '')+''.join(g)+(tail if gi==len(groups)-1 else '')
    ops.append(dict(step='Insert D1113 block part %d/%d before AXIS'%(gi+1,len(groups)),old_string=A,new_string=txt+A))
ops.append(dict(step='RES push',old_string='RES.push(...EXTRA, ...DEEP1, ...DEEP2, ...DEEP3, ...LEADVERIFY, ...DAILY1111, ...DAILY1112);',new_string='RES.push(...EXTRA, ...DEEP1, ...DEEP2, ...DEEP3, ...LEADVERIFY, ...DAILY1111, ...DAILY1112, ...DAILY1113);'))
ops.append(dict(step='topic loop',old_string='for (const r of [...DEEP1, ...DEEP2, ...DEEP3, ...LEADVERIFY, ...DAILY1111, ...DAILY1112]) {',new_string='for (const r of [...DEEP1, ...DEEP2, ...DEEP3, ...LEADVERIFY, ...DAILY1111, ...DAILY1112, ...DAILY1113]) {'))
old_scope='Updated November 12, 2026 (America/Chicago): 1,890 resource records (R1–R1891; R428 retired before publication). The Nov 12 daily pass added R1624–R1891'
new_scope='Updated November 13, 2026 (America/Chicago): {:,} resource records (R1–{}; R428 retired before publication). The Nov 13 daily pass added {}–{} (1 resolved open lead + {} new discovery records, incl. backward/forward citation chases and non-English sources). The Nov 12 daily pass added R1624–R1891'.format(total,last,first,last,n-1)
ops.append(dict(step='scope line',old_string=old_scope,new_string=new_scope))
old_cb='On Nov 12, 269 new leads were verified the same day (268 promoted R1624–R1891, 0 rejected); 1 lead remains open because its Chinese journal host was unreachable, and it is not an index entry.'
new_cb='On Nov 12, 269 new leads were verified the same day (268 promoted R1624–R1891, 0 rejected). On Nov 13 the 1 open lead was resolved (promoted as %s) and %d new leads were verified the same day (%d promoted %s–%s, %d rejected as duplicates); 3 leads remain open because their hosts were unreachable or DOIs unregistered, and they are not index entries.'%(first,SUM['newLeads'],SUM['newPromoted'],rows[1][0],last,SUM['newRejected'])
ops.append(dict(step='evidence callout',old_string=old_cb,new_string=new_cb))
ops.append(dict(step='whats new caption',old_string='<Section heading="What\'s new" id="new" caption="Last updated Nov 12, 2026 (America/Chicago)">',new_string='<Section heading="What\'s new" id="new" caption="Last updated Nov 13, 2026 (America/Chicago)">'))
wn=G['news']; a='          { lead: "Nov 12", title: "Daily pass: 268 verified additions (R1624–R1891)",'
ops.append(dict(step='whats new row',old_string=a,new_string='          { lead: %s, title: %s, detail: %s },\n'%(js(wn['date']),js(wn['title']),js(wn['detail']))+a))
cl=G['change']; a='          ["2026-11-12", "Daily pass 2026-11-12: 268 verified additions'
ops.append(dict(step='changelog row',old_string=a,new_string='          [%s, %s],\n'%(js(cl['date']),js(cl['entry']))+a))
a='            { title: "Daily pass limits (Nov 12)"'
ops.append(dict(step='gaps row',old_string=a,new_string='            { title: "Daily pass limits (Nov 13)", detail: %s },\n'%js(G['gap'])+a))
# topic takeaway pointers in AXIS
byid={r[0]:r for r in rows}
skipped=[]
for tid,txt in G['takeaways'].items():
    m=re.search(r'\{key:"%s",[^\n]*?take:"((?:[^"\\]|\\.)*)"\}'%re.escape(tid),base)
    if not m: skipped.append(tid); continue
    ids=[r[0] for r in rows if tid in r[5].split(',')]
    oldt=m.group(1)
    newt=oldt+' Nov 13 backfill: %d records (%s–%s), DOI/abstract/catalogue level.'%(len(ids),ids[0],ids[-1])
    ops.append(dict(step='AXIS take '+tid,old_string='take:"%s"}'%oldt,new_string='take:"%s"}'%newt))
cur=base
for o in ops:
    c=cur.count(o['old_string'])
    assert c==1,(o['step'],c)
    cur=cur.replace(o['old_string'],o['new_string'],1)
open('canvas-2026-11-13-proposed.tsx','w').write(cur)
json.dump(ops,open('edit-ops.json','w'),ensure_ascii=False,indent=1)
missing=[r[0] for r in rows if ('"%s"'%r[0]) not in cur]
print(len(ops),'ops; sizes',[len(o['new_string']) for o in ops][:6],'skipped takes',skipped,'missing ids',len(missing))
