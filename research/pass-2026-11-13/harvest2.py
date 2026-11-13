"""pass-2026-11-13 harvest 2: (a) backward citation chase via OpenAlex referenced_works from the 2026-11-12 seeds dated <2000
(keep referenced works cited by >=2 seeds or published <1990); (b) forward citation chase (OpenAlex cites:) from six 2026-11-12
classics (R1634 Davidovits 1991, R1713 Mayfield 1988, R1744 Diamond 1975, R1747 Papadakis 1991, R1686 Tsivilis 1999, R1704 limestone-filled cements 1991):
top 12 citers by cited_by_count published <=2010 and top 6 citers published 2024-2026."""
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
seeds=json.load(open('seeds.json'))
sid={s[3].split('/')[-1]:s[0] for s in seeds if s[3]}
refs=collections.defaultdict(list)
ids=[s[3].split('/')[-1] for s in seeds if s[3]]
for i in range(0,len(ids),40):
  d=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'openalex:'+'|'.join(ids[i:i+40]),'per-page':50,'select':'id,referenced_works','mailto':'research@example.org'}))
  for w in d['results']:
    for r in w.get('referenced_works') or []: refs[r.split('/')[-1]].append(w['id'].split('/')[-1])
  time.sleep(1)
print('seed refs',len(refs),flush=True)
ref_ids=list(refs); got={}
for i in range(0,len(ref_ids),50):
  d=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'openalex:'+'|'.join(ref_ids[i:i+50]),'per-page':50,'select':SEL,'mailto':'research@example.org'}))
  for w in d['results']: got[w['id'].split('/')[-1]]=w
  time.sleep(0.6)
kept=0
for wid,w in got.items():
  cs=refs[wid]
  if len(set(cs))>=2 or (w.get('publication_year') or 9999)<1990:
    k=(w.get('doi') or w['id']).lower()
    w['queries']=[['citation-chase','refs of '+','.join(sorted({sid[c] for c in cs}))]]; w['_citedBySeeds']=sorted({sid[c] for c in cs})
    if k not in out: out[k]=w; kept+=1
log.append(dict(topic='citation-chase',mode='openalex referenced_works (backward)',query='seeds: %d records from pass-2026-11-12 dated <2000'%len(ids),period=None,language=None,n=kept,refsTotal=len(refs),refsFetched=len(got),rule='cited by >=2 seeds or published <1990',errors=[]))
print('kept back',kept,flush=True)
FW={'R1634':'W2114711884','R1713':'W2135757527','R1744':'W2061869571','R1747':'W2162114997','R1686':'W2044309764','R1704':'W379512433'}
for rid,wid in FW.items():
  for per,n in (('to_publication_date:2010-12-31',12),('from_publication_date:2024-01-01,to_publication_date:2026-11-12',6)):
    ent=dict(topic='citation-chase-fwd',mode='openalex cites (forward)',query='cites:%s (%s)'%(wid,rid),period=per,language=None,n=0,errors=[])
    try:
      d=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'cites:%s,%s,type:article|book-chapter|report|dissertation|book|review|standard'%(wid,per),'per-page':n,'sort':'cited_by_count:desc','select':SEL,'mailto':'research@example.org'}))
      for w in d['results']:
        k=(w.get('doi') or w['id']).lower()
        if k in out: continue
        w['queries']=[['citation-chase-fwd','cites '+rid]]; w['_citesSeed']=rid; out[k]=w; ent['n']+=1
    except Exception as e: ent['errors'].append(str(e))
    log.append(ent); print(ent,flush=True); time.sleep(0.6)
json.dump(log,open('search-log2.json','w'),indent=1); json.dump(out,open('api-hits2.json','w'))
print(len(out))
