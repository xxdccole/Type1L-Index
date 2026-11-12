"""pass-2026-11-12 harvest 2: (a) retry 4 rate-limited title.search queries; (b) backward citation chase via OpenAlex referenced_works
from the 2026-11-11 historical seeds (records dated <2005 with OpenAlex IDs): keep referenced works cited by >=2 seeds or published <1995."""
import json,urllib.request,urllib.parse,time,collections
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def get(u):
  err=None
  for i in range(5):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    except Exception as e: err=e; time.sleep(5*(i+1))
  raise err
SEL='id,doi,title,publication_year,publication_date,type,language,cited_by_count,authorships,primary_location,abstract_inverted_index,is_retracted,open_access,biblio'
out={};log=[]
R=[("cross-durability","sulfate attack concrete",":2000"),("cross-durability","acid attack concrete",None),("binder-cac-csa","calcium aluminate cement",":1995"),("binder-cac-csa","ettringite binder",None)]
for t,q,per in R:
  ent={"topic":t,"mode":"title.search","query":q,"period":per,"language":None,"n":0,"errors":[],"retry":True}
  f='title.search:%s,type:article|book-chapter|report|dissertation|book|review|standard'%q
  if per:
    a,b=per.split(':')
    if b: f+=',to_publication_date:%s-12-31'%b
  try:
    d=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':f,'per-page':25,'sort':'cited_by_count:desc','select':SEL,'mailto':'research@example.org'}))
    for w in d['results']:
      k=(w.get('doi') or w['id']).lower()
      if k in out: out[k]['queries'].append([t,q]); continue
      w['queries']=[[t,q]]; out[k]=w; ent['n']+=1
  except Exception as e: ent['errors'].append(str(e))
  log.append(ent); print(ent,flush=True); time.sleep(1)
seeds=json.load(open('seeds.json'))
refs=collections.defaultdict(list)
ids=[s[3].split('/')[-1] for s in seeds if s[3]]
for i in range(0,len(ids),40):
  d=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'openalex:'+'|'.join(ids[i:i+40]),'per-page':50,'select':'id,referenced_works','mailto':'research@example.org'}))
  for w in d['results']:
    for r in w.get('referenced_works') or []: refs[r.split('/')[-1]].append(w['id'].split('/')[-1])
  time.sleep(1)
print('seed refs',len(refs))
sid={s[3].split('/')[-1]:s[0] for s in seeds if s[3]}
ref_ids=list(refs)
got={}
for i in range(0,len(ref_ids),50):
  d=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'openalex:'+'|'.join(ref_ids[i:i+50]),'per-page':50,'select':SEL,'mailto':'research@example.org'}))
  for w in d['results']: got[w['id'].split('/')[-1]]=w
  time.sleep(0.6)
kept=0
for wid,w in got.items():
  cs=refs[wid]
  if len(set(cs))>=2 or (w.get('publication_year') or 9999)<1995:
    k=(w.get('doi') or w['id']).lower()
    w['queries']=[['citation-chase','refs of '+','.join(sorted({sid[c] for c in cs}))]]; w['_citedBySeeds']=sorted({sid[c] for c in cs})
    if k not in out: out[k]=w; kept+=1
log.append(dict(topic='citation-chase',mode='openalex referenced_works (backward)',query='seeds: %d records from pass-2026-11-11 dated <2005'%len(ids),period=None,language=None,n=kept,refsTotal=len(refs),refsFetched=len(got),rule='cited by >=2 seeds or published <1995',errors=[]))
print('kept',kept)
json.dump(log,open('search-log2.json','w'),indent=1); json.dump(out,open('api-hits2.json','w'))
