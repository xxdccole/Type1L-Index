"""pass-2026-11-20 harvest (adapted from pass-2026-11-19 harvest.py + harvest2.py): OpenAlex title.search backfill for the ledger rotation head
(cross-mix, cross-chemistry, cross-mechanics, scm-limestone, binder-activated, cross-durability, concrete-architectural, concrete-scc,
concrete-polymer-refractory, concrete-circular, concrete-pavement-pervious, concrete-repair-grout-overlay, concrete-precast-insitu-print)
+ historical/government searches + language-filtered searches + current awareness 2026-11-01..2026-11-20 + specific missing titles
+ backward chase (refs of pre-2006 DOI records in focus topics, cited by >=2 seeds or <1990) + forward chase (top-25 cited focus records + top-10 Nov 19 additions).
All queries checked against prior-queries-all.json (passes to 2026-11-19); exact repeats skipped."""
import json,urllib.request,urllib.parse,time,re,collections
T='t';S_='s'
Q=[
("cross-mix",T,"aggregate grading",None,None),("cross-mix",T,"water reducing admixture",":2005",None),("cross-mix",T,"air entraining admixture",None,None),("cross-mix",T,"concrete mix proportioning",None,None),("cross-mix",T,"fineness modulus",None,None),("cross-mix",T,"paste volume",None,None),("cross-mix",T,"high range water reducer",None,None),("cross-mix",T,"retarding admixture",None,None),
("cross-chemistry",T,"tricalcium silicate hydration",None,None),("cross-chemistry",T,"calcium silicate hydrate","1950:2005",None),("cross-chemistry",T,"portlandite",None,None),("cross-chemistry",T,"alite hydration",None,None),("cross-chemistry",T,"belite",None,None),("cross-chemistry",T,"pore solution",":2010",None),("cross-chemistry",T,"heat of hydration",":2000",None),("cross-chemistry",T,"cement clinker phases",None,None),
("cross-mechanics",T,"tensile strength of concrete",None,None),("cross-mechanics",T,"multiaxial concrete",None,None),("cross-mechanics",T,"size effect concrete",None,None),("cross-mechanics",T,"fatigue of concrete",None,None),("cross-mechanics",T,"stress-strain curve concrete",None,None),("cross-mechanics",T,"drying shrinkage",":2000",None),("cross-mechanics",T,"autogenous shrinkage",None,None),("cross-mechanics",T,"strain rate concrete",None,None),
("scm-limestone",T,"limestone addition",None,None),("scm-limestone",T,"calcareous filler",None,None),("scm-limestone",T,"limestone fines",None,None),("scm-limestone",T,"monocarbonate",None,None),("scm-limestone",T,"carboaluminate",None,None),("scm-limestone",T,"dolomite powder",None,None),("scm-limestone",T,"limestone filler","2016:2026",None),
("binder-activated",T,"alkali activated metakaolin",None,None),("binder-activated",T,"sodium silicate activated slag",None,None),("binder-activated",T,"geopolymer mortar",None,None),("binder-activated",T,"geopolymer shrinkage",None,None),("binder-activated",T,"alkali activated cement","2008:2026",None),("binder-activated",T,"geopolymer carbonation",None,None),("binder-activated",T,"activated slag",":1995",None),
("cross-durability",T,"salt scaling",None,None),("cross-durability",T,"chloride binding",None,None),("cross-durability",T,"sewer concrete corrosion",None,None),("cross-durability",T,"calcium leaching",None,None),("cross-durability",T,"concrete in seawater",None,None),("cross-durability",T,"chloride threshold",None,None),("cross-durability",T,"alkali-silica reaction","2011:2026",None),("cross-durability",T,"carbonation depth",None,None),
("concrete-architectural",T,"decorative concrete",None,None),("concrete-architectural",T,"concrete surface finish",None,None),("concrete-architectural",T,"concrete facade",None,None),("concrete-architectural",T,"glass fibre reinforced concrete",None,None),("concrete-architectural",T,"surface voids concrete",None,None),("concrete-architectural",T,"concrete colour",None,None),("concrete-architectural",T,"textile reinforced concrete facade",None,None),
("concrete-scc",T,"self-compacting concrete","2006:2015",None),("concrete-scc",T,"self-compacting concrete","2016:2026",None),("concrete-scc",T,"self-compacting mortar",None,None),("concrete-scc",T,"formwork pressure",None,None),("concrete-scc",T,"self-compacting concrete durability",None,None),("concrete-scc",T,"self-consolidating concrete","2012:2026",None),
("concrete-polymer-refractory",T,"epoxy mortar",None,None),("concrete-polymer-refractory",T,"polyester concrete",None,None),("concrete-polymer-refractory",T,"polymer cement concrete",None,None),("concrete-polymer-refractory",T,"low cement castable",None,None),("concrete-polymer-refractory",T,"sulfur concrete",None,None),("concrete-polymer-refractory",T,"castable refractory",None,None),("concrete-polymer-refractory",T,"polymer concrete","2001:2026",None),
("concrete-circular",T,"recycled aggregate concrete","2016:2026",None),("concrete-circular",T,"recycled concrete powder",None,None),("concrete-circular",T,"recycled aggregate durability",None,None),("concrete-circular",T,"concrete recycling",":2005",None),("concrete-circular",T,"construction and demolition waste aggregate",None,None),("concrete-circular",T,"carbonated recycled aggregate",None,None),
("concrete-pavement-pervious",T,"pervious concrete","2013:2026",None),("concrete-pavement-pervious",T,"roller compacted concrete pavement",None,None),("concrete-pavement-pervious",T,"airfield concrete pavement",None,None),("concrete-pavement-pervious",T,"concrete block pavement",None,None),("concrete-pavement-pervious",T,"pervious concrete clogging",None,None),("concrete-pavement-pervious",T,"whitetopping",None,None),("concrete-pavement-pervious",T,"concrete pavement","2011:2026",None),
("concrete-repair-grout-overlay",T,"concrete overlay",None,None),("concrete-repair-grout-overlay",T,"repair material bond",None,None),("concrete-repair-grout-overlay",T,"microfine cement",None,None),("concrete-repair-grout-overlay",T,"crack injection",None,None),("concrete-repair-grout-overlay",T,"concrete rehabilitation",None,None),("concrete-repair-grout-overlay",T,"corrosion inhibitor concrete",None,None),("concrete-repair-grout-overlay",T,"grout",":1995",None),
("concrete-precast-insitu-print",T,"precast concrete","1996:2026",None),("concrete-precast-insitu-print",T,"hollow core slab",None,None),("concrete-precast-insitu-print",T,"3D concrete printing","2023:2026",None),("concrete-precast-insitu-print",T,"precast connection",None,None),("concrete-precast-insitu-print",T,"spun concrete",None,None),("concrete-precast-insitu-print",T,"printable mortar",None,None),("concrete-precast-insitu-print",T,"tilt-up",None,None),
# historical / government / standards (relevance search, old periods)
("cross-tests-codes",S_,"Bureau of Public Roads concrete investigation",":1970",None),("cross-chemistry",S_,"Portland Cement Association research laboratories bulletin cement",":1975",None),("cross-durability",S_,"Corps of Engineers concrete durability investigation",":1980",None),("cross-mix",S_,"Highway Research Board concrete proportioning",":1975",None),("cross-chemistry",S_,"National Bureau of Standards portland cement",":1960",None),("cross-durability",S_,"Building Research Station concrete",":1980",None),
# specific still-missing titles
("cross-mix",S_,"Design and Control of Concrete Mixtures Portland Cement Association",None,None),("cross-mechanics",S_,"Neville Properties of Concrete",None,None),("concrete-hpc",S_,"ultra-high performance concrete state-of-the-art report bridge community FHWA",None,None),
# languages (new terms)
("lang-es",T,"hormigón autocompactante",None,"es"),("lang-pt",T,"concreto permeável",None,"pt"),("lang-de",T,"Betoninstandsetzung",None,"de"),("lang-fr",T,"granulats recyclés",None,"fr"),("lang-it",T,"calcestruzzo",None,"it"),("lang-pl",T,"beton",None,"pl"),("lang-sv",T,"betong",None,"sv"),("lang-ja",T,"コンクリート",None,"ja"),("lang-zh",T,"混凝土",None,"zh"),("lang-ru",T,"бетон",None,"ru"),("lang-es",T,"geopolímero",None,"es"),("lang-pt",T,"concreto autoadensável",None,"pt"),
# current awareness
("current-2026",S_,"concrete","2026-11-01:",None),("current-2026",S_,"cement","2026-11-01:",None),("current-2026",S_,"geopolymer","2026-11-01:",None),("current-2026",S_,"recycled aggregate concrete","2026-11-01:",None),
]
PR={(a,b,c,d) for a,b,c,d in [tuple(x) for x in json.load(open('prior-queries-all.json'))]}
PR|={(a,'title.search:'+b if False else b,c,d) for a,b,c,d in PR}
out={};log=[];skipped=[]
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def get(u):
  err=None
  for i in range(5):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    except Exception as e: err=e; time.sleep(4*(i+1))
  raise err
SEL='id,doi,title,publication_year,publication_date,type,language,cited_by_count,authorships,primary_location,abstract_inverted_index,is_retracted,open_access,biblio'
def add(w,q):
  k=(w.get('doi') or w['id']).lower()
  if k in out: out[k]['queries'].append(q); return 0
  w['queries']=[q]; out[k]=w; return 1
for t,mode,q,per,lang in Q:
  if (t,q,per,lang) in PR or (t,'title.search:'+q,per,lang) in PR: skipped.append([t,q,per,lang]); continue
  ent={"topic":t,"mode":'title.search' if mode=='t' else 'search',"query":q,"period":per,"language":lang,"n":0,"errors":[]}
  f='type:article|book-chapter|report|dissertation|book|review|standard'
  if mode=='t': f='title.search:%s,'%q.replace(',',' ')+f
  if lang: f+=',language:'+lang
  cur=t=='current-2026'
  if per:
    a,b=per.split(':')
    if a: f+=',from_publication_date:%s'%(a if '-' in a else a+'-01-01')
    if b: f+=',to_publication_date:%s-12-31'%b
  if cur: f+=',to_publication_date:2026-11-20'
  p={'filter':f,'per-page':25,'sort':'relevance_score:desc' if mode=='s' else 'cited_by_count:desc','select':SEL,'mailto':'research@example.org'}
  if mode=='s': p['search']=q
  try:
    d=get('https://api.openalex.org/works?'+urllib.parse.urlencode(p)); ent['n']=sum(add(w,[t,q]) for w in d['results'])
  except Exception as e: ent['errors'].append(str(e))
  log.append(ent); print(t,q,per,lang,ent['n'],ent['errors'],flush=True); time.sleep(0.3)
json.dump(dict(log=log,skippedRepeats=skipped),open('search-log.json','w'),indent=1); json.dump(out,open('api-hits.json','w'))
# ---- citation chases
SD=json.load(open('../../site-data.json'))
FOCUS={'cross-mix','cross-chemistry','cross-mechanics','scm-limestone','binder-activated','cross-durability','concrete-architectural','concrete-scc','concrete-polymer-refractory','concrete-circular','concrete-pavement-pervious','concrete-repair-grout-overlay','concrete-precast-insitu-print'}
seeds=[]
for r in SD['resources']:
  if not FOCUS & set(r['topics']): continue
  m=re.search(r'10\.\d{4,9}/[^\s?#]+',r.get('url') or '')
  if m: seeds.append((r['id'],m.group(0).lower().rstrip('/.')))
print('seeds',len(seeds),flush=True)
oa={}
for i in range(0,len(seeds),40):
  try: d=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'doi:'+'|'.join('https://doi.org/'+x for _,x in seeds[i:i+40]),'per-page':50,'select':'id,doi,publication_year,cited_by_count,referenced_works','mailto':'research@example.org'}))
  except Exception as ex: print('seed err',ex); continue
  for w in d['results']: oa[(w['doi'] or '').replace('https://doi.org/','').lower()]=w
  time.sleep(0.3)
sid={x:rid for rid,x in seeds}
refs=collections.defaultdict(list)
for x,w in oa.items():
  if (w.get('publication_year') or 9999)<2006:
    for r in w.get('referenced_works') or []: refs[r.split('/')[-1]].append(sid.get(x,x))
ids=[k for k,v in refs.items() if len(set(v))>=2]+[k for k,v in refs.items() if len(set(v))<2]
print('refs',len(refs),flush=True); got={}
for i in range(0,len(ids),50):
  try: d=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'openalex:'+'|'.join(ids[i:i+50]),'per-page':50,'select':SEL,'mailto':'research@example.org'}))
  except Exception as ex: print('ref err',ex); continue
  for w in d['results']: got[w['id'].split('/')[-1]]=w
  time.sleep(0.3)
kb=0
for wid,w in got.items():
  cs=refs[wid]
  if len(set(cs))>=2 or (w.get('publication_year') or 9999)<1990: kb+=add(w,['citation-chase','refs of '+','.join(sorted(set(cs))[:6])])
print('backward',kb,flush=True)
top=sorted(oa.values(),key=lambda w:-(w.get('cited_by_count') or 0))[:25]
s19=[(r['id'],re.search(r'10\.\d{4,9}/[^\s?#]+',r['url']).group(0).lower().rstrip('/.')) for r in SD['resources'] if 3048<=int(r['id'][1:])<=3560 and re.search(r'10\.\d{4,9}/',r.get('url') or '')]
oa19={}
for i in range(0,len(s19),40):
  try: d=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'doi:'+'|'.join('https://doi.org/'+x for _,x in s19[i:i+40]),'per-page':50,'select':'id,doi,publication_year,cited_by_count','mailto':'research@example.org'}))
  except Exception as ex: print('s19 err',ex); continue
  for w in d['results']: oa19[(w['doi'] or '').replace('https://doi.org/','').lower()]=w
  time.sleep(0.3)
sid.update({x:rid for rid,x in s19})
top19=sorted(oa19.values(),key=lambda w:-(w.get('cited_by_count') or 0))[:10]
fwdseeds=[sid.get((w['doi'] or '').replace('https://doi.org/','').lower()) for w in top+top19]
print('fwd seeds',fwdseeds,flush=True)
kf=0
for w in top+[w for w in top19 if w not in top]:
  wid=w['id'].split('/')[-1]; sd=sid.get((w['doi'] or '').replace('https://doi.org/','').lower())
  for lab,extra in (('old','to_publication_date:2010-12-31'),('new','from_publication_date:2025-01-01')):
    try:
      d=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'cites:%s,%s,type:article|book-chapter|report|dissertation|book|review'%(wid,extra),'per-page':6 if lab=='old' else 4,'sort':'cited_by_count:desc','select':SEL,'mailto':'research@example.org'}))
      kf+=sum(add(x,['citation-chase-fwd','cites '+str(sd)]) for x in d['results'])
    except Exception as ex: print('fwd err',ex)
    time.sleep(0.3)
print('forward',kf,flush=True)
json.dump(dict(log=log,skippedRepeats=skipped,chase=dict(seeds=len(seeds),seedsInOpenAlex=len(oa),refs=len(refs),refsFetched=len(got),backwardKept=kb,forwardSeeds=fwdseeds,forwardKept=kf)),open('search-log.json','w'),indent=1)
json.dump(out,open('api-hits.json','w')); print('total',len(out))
