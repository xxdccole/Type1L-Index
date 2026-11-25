"""pass-2026-11-25 supplementary current-awareness sweep (2026-11-23 -> 2026-11-25), since the Nov 23 harvest (reused) ran to 2026-11-23."""
import json,urllib.request,urllib.parse,time
S_='s'
Q=[("current-2026",S_,"concrete","2026-11-23:",None),("current-2026",S_,"cement","2026-11-23:",None),("current-2026",S_,"mortar cementitious","2026-11-20:",None),
("current-2026",S_,"geopolymer alkali-activated","2026-11-15:",None),("current-2026",S_,"limestone calcined clay cement","2026-11-15:",None),("current-2026",S_,"supplementary cementitious materials","2026-11-15:",None),
("current-2026",S_,"ultra-high performance concrete","2026-11-15:",None),("current-2026",S_,"concrete durability chloride","2026-11-15:",None),("current-2026",S_,"low-carbon cement clinker","2026-11-10:",None)]
PR={tuple(x) for x in json.load(open('prior-queries-all.json'))}
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def get(u):
  for i in range(5):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    except Exception as e: err=e; time.sleep(4*(i+1))
  raise err
SEL='id,doi,title,publication_year,publication_date,type,language,cited_by_count,authorships,primary_location,abstract_inverted_index,is_retracted,open_access,biblio'
out={};log=[];sk=[]
for t,mode,q,per,lang in Q:
  if (t,q,per,lang) in PR: sk.append([t,q,per,lang]); continue
  a,b=per.split(':')
  f='type:article|book-chapter|report|dissertation|book|review|standard,from_publication_date:%s,to_publication_date:2026-11-25'%a
  p={'filter':f,'per-page':50,'sort':'relevance_score:desc','select':SEL,'mailto':'research@example.org','search':q}
  ent=dict(topic=t,mode='search',query=q,period=per,language=lang,n=0,errors=[])
  try:
    d=get('https://api.openalex.org/works?'+urllib.parse.urlencode(p))
    for w in d['results']:
      k=(w.get('doi') or w['id']).lower()
      if k in out: out[k]['queries'].append([t,q]); continue
      w['queries']=[[t,q]]; out[k]=w; ent['n']+=1
  except Exception as e: ent['errors'].append(str(e))
  log.append(ent); print(q,per,ent['n'],ent['errors'],flush=True)
json.dump(dict(log=log,skippedRepeats=sk),open('search-log-c.json','w'),indent=1); json.dump(out,open('api-hits-c.json','w')); print(len(out))
