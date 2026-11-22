"""pass-2026-11-20 harvest (adapted from pass-2026-11-19 harvest.py + harvest2.py): OpenAlex title.search backfill for the ledger rotation head
(cross-mix, cross-chemistry, cross-mechanics, scm-limestone, binder-activated, cross-durability, concrete-architectural, concrete-scc,
concrete-polymer-refractory, concrete-circular, concrete-pavement-pervious, concrete-repair-grout-overlay, concrete-precast-insitu-print)
+ historical/government searches + language-filtered searches + current awareness 2026-11-01..2026-11-20 + specific missing titles
+ backward chase (refs of pre-2006 DOI records in focus topics, cited by >=2 seeds or <1990) + forward chase (top-25 cited focus records + top-10 Nov 19 additions).
All queries checked against prior-queries-all.json (passes to 2026-11-19); exact repeats skipped."""
import json,urllib.request,urllib.parse,time,re,collections
T='t';S_='s'
Q=[
("microcracking",T,"microcracks in concrete",None,None),("microcracking",T,"interfacial transition zone cracking",None,None),("microcracking",T,"drying shrinkage microcracking cement paste",None,None),("microcracking",T,"acoustic emission concrete cracking",None,None),("microcracking",T,"X-ray microtomography cement paste cracks",None,None),("microcracking",T,"thermal microcracking aggregate cement",None,None),("microcracking",S_,"microcracking concrete early investigation",":1980",None),
("mass",T,"mass concrete temperature control",None,None),("mass",T,"thermal cracking of massive concrete",None,None),("mass",T,"heat of hydration concrete dam",None,None),("mass",T,"mass concrete foundation placement",None,None),("mass",T,"adiabatic temperature rise concrete",None,None),("mass",T,"delayed ettringite formation mass concrete",None,None),("mass",S_,"mass concrete heat generation cement type",":1975",None),
("binder-portland",T,"ordinary portland cement clinker phases",None,None),("binder-portland",T,"alite belite hydration kinetics",None,None),("binder-portland",T,"portland cement Bogue composition",None,None),("binder-portland",T,"cement fineness strength development",None,None),("binder-portland",T,"cement sulfate optimum gypsum",None,None),("binder-portland",T,"clinker microstructure kiln",None,None),("binder-portland",T,"portland cement history manufacture",None,None),("binder-portland",S_,"portland cement chemistry compounds",":1950",None),
("concrete-fibers",T,"steel fibre reinforced concrete flexural",None,None),("concrete-fibers",T,"polypropylene fibre concrete cracking",None,None),("concrete-fibers",T,"fibre reinforced concrete fire spalling",None,None),("concrete-fibers",T,"fibre-matrix bond pullout concrete",None,None),("concrete-fibers",T,"macro synthetic fibers concrete",None,None),("concrete-fibers",T,"glass fibre reinforced cement",None,None),("concrete-fibers",T,"basalt fibre concrete",None,None),
("scm-flyash",T,"fly ash cement pozzolanic reaction",None,None),("scm-flyash",T,"class C fly ash concrete",None,None),("scm-flyash",T,"fly ash alkali-silica reaction mitigation",None,None),("scm-flyash",T,"fly ash classification standard",None,None),("scm-flyash",T,"high-calcium fly ash cement",None,None),("scm-flyash",T,"fly ash carbon content air entrainment",None,None),("scm-flyash",S_,"fly ash in concrete early use",":1975",None),
("concrete-hpc",T,"high performance concrete durability",None,None),("concrete-hpc",T,"ultra-high performance concrete mix design",None,None),("concrete-hpc",T,"high strength concrete autogenous shrinkage",None,None),("concrete-hpc",T,"HPC bridge decks",None,None),("concrete-hpc",T,"ultra-high performance concrete bridge connections",None,None),("concrete-hpc",T,"reactive powder concrete",None,None),("concrete-hpc",T,"high-strength concrete columns",None,None),
("scm-clay",T,"metakaolin concrete properties",None,None),("scm-clay",T,"calcined clay pozzolan reactivity",None,None),("scm-clay",T,"calcined clay limestone cement durability",None,None),("scm-clay",T,"kaolinite thermal activation",None,None),("scm-clay",T,"calcined shale cement",None,None),("scm-clay",T,"calcined clay field trial concrete",None,None),
("cross-construction",T,"concrete construction scheduling formwork",None,None),("cross-construction",T,"concrete pour sequence",None,None),("cross-construction",T,"formwork pressure self-consolidating",None,None),("cross-construction",T,"concrete maturity method",None,None),("cross-construction",T,"concrete placing in cold weather",None,None),("cross-construction",T,"construction joints concrete",None,None),
("cross-failure-repair",T,"concrete structure failure investigation",None,None),("cross-failure-repair",T,"concrete deterioration case study",None,None),("cross-failure-repair",T,"concrete forensic engineering",None,None),("cross-failure-repair",T,"concrete bridge collapse cause",None,None),("cross-failure-repair",T,"reinforcement corrosion repair patch",None,None),("cross-failure-repair",T,"concrete structure condition assessment",None,None),
("cross-supply-region",T,"cement industry regional market",None,None),("cross-supply-region",T,"cement imports tariff",None,None),("cross-supply-region",T,"cement production capacity country",None,None),("cross-supply-region",T,"regional aggregate availability concrete",None,None),("cross-supply-region",T,"cement industry United States history",None,None),("cross-supply-region",T,"Midwest cement plant",None,None),
("concrete-heavyweight",T,"heavyweight concrete radiation shielding",None,None),("concrete-heavyweight",T,"barite concrete",None,None),("concrete-heavyweight",T,"magnetite concrete density",None,None),("concrete-heavyweight",T,"high density concrete gamma",None,None),("concrete-heavyweight",T,"nuclear shielding concrete",None,None),
("binder-white-masonry",T,"white portland cement",None,None),("binder-white-masonry",T,"masonry cement",None,None),("binder-white-masonry",T,"mortar cement lime masonry",None,None),("binder-white-masonry",T,"masonry mortar strength bond",None,None),("binder-white-masonry",T,"coloured concrete pigment",None,None),("binder-white-masonry",T,"plastering mortar cement",None,None),
("concrete-mass-rcc",T,"roller compacted concrete dam",None,None),("concrete-mass-rcc",T,"roller compacted concrete pavement",None,None),("concrete-mass-rcc",T,"RCC mix design",None,None),("concrete-mass-rcc",T,"rollcrete cementitious content",None,None),("concrete-mass-rcc",T,"RCC lift joint",None,None),
# historical
("mass",S_,"concrete dam construction temperature history",":1960",None),("concrete-hpc",S_,"high strength concrete early research",":1990",None),("binder-white-masonry",S_,"masonry mortar tests history",":1960",None),("cross-failure-repair",S_,"concrete failures causes early reports",":1960",None),("cross-supply-region",S_,"cement industry survey report",":1970",None),("concrete-mass-rcc",S_,"roller compacted concrete early dams",":1995",None),("concrete-fibers",S_,"fibre reinforced concrete early investigations",":1985",None),("scm-clay",S_,"pozzolanic clays burnt",":1970",None),
# languages
("lang-es",T,"hormigón armado fisuración",None,"es"),("lang-pt",T,"concreto massa temperatura",None,"pt"),("lang-de",T,"Flugasche Beton",None,"de"),("lang-fr",T,"béton fibré",None,"fr"),("lang-ja",T,"コンクリート ひび割れ",None,"ja"),("lang-zh",T,"粉煤灰 混凝土",None,"zh"),("lang-es",T,"cemento blanco",None,"es"),("lang-pt",T,"argamassa de assentamento",None,"pt"),("lang-de",T,"Massenbeton",None,"de"),("lang-fr",T,"ciment portland clinker",None,"fr"),("lang-ru",T,"бетон цемент",None,"ru"),("lang-ko",T,"콘크리트 균열",None,"ko"),("lang-id",T,"beton serat",None,"id"),("lang-it",T,"calcestruzzo cemento",None,"it"),("lang-pl",T,"beton cement",None,"pl"),
# current awareness
("current-2026",S_,"concrete","2026-11-21:",None),("current-2026",S_,"cement","2026-11-21:",None),("current-2026",S_,"fly ash concrete","2026-11-01:",None),("current-2026",S_,"calcined clay","2026-11-01:",None),("current-2026",S_,"fibre reinforced concrete","2026-11-01:",None),("current-2026",S_,"mass concrete","2026-10-01:",None),
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
  if cur: f+=',to_publication_date:2026-11-22'
  p={'filter':f,'per-page':25,'sort':'relevance_score:desc' if mode=='s' else 'cited_by_count:desc','select':SEL,'mailto':'research@example.org'}
  if mode=='s': p['search']=q
  try:
    d=get('https://api.openalex.org/works?'+urllib.parse.urlencode(p)); ent['n']=sum(add(w,[t,q]) for w in d['results'])
  except Exception as e: ent['errors'].append(str(e))
  log.append(ent); print(t,q,per,lang,ent['n'],ent['errors'],flush=True); time.sleep(0.3)
json.dump(dict(log=log,skippedRepeats=skipped),open('search-log.json','w'),indent=1); json.dump(out,open('api-hits.json','w'))
# ---- citation chases
SD=json.load(open('../../site-data.json'))
FOCUS={'microcracking','mass','binder-portland','concrete-fibers','scm-flyash','concrete-hpc','scm-clay','cross-construction','cross-failure-repair','cross-supply-region','concrete-heavyweight','binder-white-masonry','concrete-mass-rcc'}
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
s19=[(r['id'],re.search(r'10\.\d{4,9}/[^\s?#]+',r['url']).group(0).lower().rstrip('/.')) for r in SD['resources'] if 4046<=int(r['id'][1:])<=4294 and re.search(r'10\.\d{4,9}/',r.get('url') or '')]
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
