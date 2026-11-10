from common import *
import collections
ex_d=set();ex_t={}
for r in S['resources']:
    u=r['url'].lower()
    if 'doi.org/' in u: ex_d.add(u.split('doi.org/')[1].rstrip('/'))
    ex_t[norm(r['title'].split(' (')[0])]=r['id']
for v in VER:
    if v.get('doi'): ex_d.add(v['doi'].lower())
d2id={}
for r in S['resources']:
    u=r['url'].lower()
    if 'doi.org/' in u: d2id[u.split('doi.org/')[1].rstrip('/')]=r['id']
for v in VER:
    if v.get('doi'): d2id[v['doi'].lower()]=v['id']
rows=[]
for i,x in enumerate(CAN):
    if x['status']!='candidate': continue
    d=(x.get('doi') or '').lower()
    t=vt(d) if d else (ND.get(x['title'],{}).get('title') or x['title'])
    a=abstract(d) if d else clean(ND.get(x['title'],{}).get('abstract'))
    v=venue(d) if d else (ND.get(x['title'],{}).get('venue') or '')
    typ=((M.get(d,{}).get('crossref') or {}).get('type') or (M.get(d,{}).get('openalex') or {}).get('type')) if d else ND.get(x['title'],{}).get('type')
    dup=d2id.get(d) or ex_t.get(norm(t)) or ex_t.get(norm(x['title']))
    rel=bool(STRONG.search(t+' '+v)) ; rel2=bool(STRONG.search(a))
    rows.append(dict(i=i,doi=d,topic=x['topic'],title=t,venue=v,type=typ,year=x.get('year'),dup=dup,rel=rel,rel2=rel2,abs=a[:200]))
json.dump(rows,open('triage.json','w'),indent=0,ensure_ascii=False)
print(len(rows),collections.Counter((r['rel'],r['rel2']) for r in rows),'dups',sum(1 for r in rows if r['dup']))
for r in rows:
    if r['dup']: print('DUP',r['i'],r['dup'],r['doi'],r['title'][:80])
