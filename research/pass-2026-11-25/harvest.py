"""pass-2026-11-20 harvest (adapted from pass-2026-11-19 harvest.py + harvest2.py): OpenAlex title.search backfill for the ledger rotation head
(cross-mix, cross-chemistry, cross-mechanics, scm-limestone, binder-activated, cross-durability, concrete-architectural, concrete-scc,
concrete-polymer-refractory, concrete-circular, concrete-pavement-pervious, concrete-repair-grout-overlay, concrete-precast-insitu-print)
+ historical/government searches + language-filtered searches + current awareness 2026-11-01..2026-11-20 + specific missing titles
+ backward chase (refs of pre-2006 DOI records in focus topics, cited by >=2 seeds or <1990) + forward chase (top-25 cited focus records + top-10 Nov 19 additions).
All queries checked against prior-queries-all.json (passes to 2026-11-19); exact repeats skipped."""
import json,urllib.request,urllib.parse,time,re,collections
T='t';S_='s'
Q=[
("scm-natural",T,"natural pozzolan cement volcanic ash",None,None),("scm-natural",T,"pumice concrete pozzolanic",None,None),("scm-natural",T,"zeolite cement replacement",None,None),("scm-natural",T,"rice husk ash concrete strength",None,None),("scm-natural",T,"agricultural waste ash cement",None,None),("scm-natural",T,"diatomaceous earth pozzolan",None,None),("scm-natural",S_,"Roman concrete volcanic pozzolan mortar",None,None),
("binder-international",T,"cement standards India IS 269",None,None),("binder-international",T,"Chinese cement standard GB 175",None,None),("binder-international",T,"Brazilian cement CP II",None,None),("binder-international",T,"African cement industry blended",None,None),("binder-international",T,"Japanese cement JIS portland blast furnace",None,None),("binder-international",T,"Australian cement general purpose blended",None,None),("binder-international",T,"Middle East cement concrete hot climate",None,None),
("binder-blended",T,"ternary blended cement performance",None,None),("binder-blended",T,"composite cement CEM II strength",None,None),("binder-blended",T,"portland composite cement durability",None,None),("binder-blended",T,"blended cement hydration heat",None,None),("binder-blended",T,"pozzolanic cement sulfate resistance",None,None),("binder-blended",T,"limestone slag ternary cement",None,None),("binder-blended",S_,"blended cements early research",":1980",None),
("concrete-structural",T,"reinforced concrete beam shear strength",None,None),("concrete-structural",T,"prestressed concrete girder losses",None,None),("concrete-structural",T,"concrete column confinement",None,None),("concrete-structural",T,"punching shear flat slab",None,None),("concrete-structural",T,"creep and shrinkage prediction models",None,None),("concrete-structural",T,"concrete bridge deck cracking",None,None),("concrete-structural",T,"seismic performance reinforced concrete walls",None,None),
("cross-tests-codes",T,"concrete test method precision",None,None),("cross-tests-codes",T,"cement test standard comparison",None,None),("cross-tests-codes",T,"compressive strength testing cylinders cubes",None,None),("cross-tests-codes",T,"building code concrete provisions",None,None),("cross-tests-codes",T,"Eurocode 2 concrete",None,None),("cross-tests-codes",T,"ASTM C109 mortar cube",None,None),("cross-tests-codes",T,"interlaboratory study cement",None,None),
("cross-environment-cost",T,"life cycle cost concrete pavement",None,None),("cross-environment-cost",T,"embodied carbon concrete buildings",None,None),("cross-environment-cost",T,"environmental product declaration concrete",None,None),("cross-environment-cost",T,"cost comparison cement types",None,None),("cross-environment-cost",T,"carbon footprint cement production",None,None),("cross-environment-cost",T,"concrete recycling economic",None,None),("cross-environment-cost",T,"sustainable concrete assessment tool",None,None),
("cross-chemistry",T,"pore solution chemistry cement",None,None),("cross-chemistry",T,"calcium silicate hydrate structure",None,None),("cross-chemistry",T,"portlandite carbonation",None,None),("cross-chemistry",T,"aluminate hydration ettringite",None,None),("cross-chemistry",T,"cement hydration thermodynamic modelling",None,None),("cross-chemistry",T,"NMR cement hydrates",None,None),
("cross-mix",T,"concrete mixture proportioning method",None,None),("cross-mix",T,"particle packing concrete",None,None),("cross-mix",T,"water-reducing admixture dosage",None,None),("cross-mix",T,"aggregate gradation concrete performance",None,None),("cross-mix",T,"low cement concrete",None,None),("cross-mix",T,"machine learning concrete mix design",None,None),
("cross-mechanics",T,"concrete fracture mechanics size effect",None,None),("cross-mechanics",T,"modulus of elasticity concrete prediction",None,None),("cross-mechanics",T,"concrete tensile strength splitting",None,None),("cross-mechanics",T,"concrete triaxial behaviour",None,None),("cross-mechanics",T,"concrete fatigue",None,None),("cross-mechanics",T,"cement paste mechanical properties nanoindentation",None,None),
("scm-limestone",T,"Portland-limestone cement field performance",None,None),("scm-limestone",T,"limestone filler cement hydration",None,None),("scm-limestone",T,"carboaluminate formation limestone",None,None),("scm-limestone",T,"Type IL cement concrete pavement",None,None),("scm-limestone",T,"limestone powder fineness cement",None,None),("scm-limestone",T,"thaumasite limestone cement",None,None),
("cross-durability",T,"chloride diffusion concrete marine",None,None),("cross-durability",T,"carbonation of concrete service life",None,None),("cross-durability",T,"freeze-thaw salt scaling concrete",None,None),("cross-durability",T,"sulfate attack cement mortar",None,None),("cross-durability",T,"alkali-aggregate reaction expansion",None,None),("cross-durability",T,"concrete permeability test",None,None),
("concrete-polymer-refractory",T,"polymer modified concrete",None,None),("concrete-polymer-refractory",T,"polymer concrete epoxy resin",None,None),("concrete-polymer-refractory",T,"refractory castable calcium aluminate",None,None),("concrete-polymer-refractory",T,"latex modified concrete overlay",None,None),("concrete-polymer-refractory",T,"high temperature concrete residual strength",None,None),
("concrete-scc",T,"self-compacting concrete mix design",None,None),("concrete-scc",T,"self-compacting concrete rheology",None,None),("concrete-scc",T,"self-consolidating concrete precast",None,None),("concrete-scc",T,"self-compacting concrete segregation stability",None,None),("concrete-scc",T,"viscosity modifying admixture",None,None),
("scm-natural",S_,"natural pozzolans cement history",":1970",None),("binder-international",S_,"cement industry developing countries",":1985",None),("concrete-structural",S_,"reinforced concrete research history",":1950",None),("cross-tests-codes",S_,"concrete testing standards history",":1960",None),("cross-environment-cost",S_,"cement energy consumption survey",":1990",None),("cross-chemistry",S_,"chemistry of cement hydration early",":1960",None),("cross-mechanics",S_,"strength of concrete early experiments",":1950",None),("concrete-scc",S_,"self-compacting concrete early development Japan",":2000",None),
("lang-es",T,"cemento puzolánico",None,"es"),("lang-pt",T,"cimento Portland composto",None,"pt"),("lang-de",T,"Zement Hydratation",None,"de"),("lang-fr",T,"béton autoplaçant",None,"fr"),("lang-ja",T,"セメント 水和",None,"ja"),("lang-zh",T,"水泥 水化",None,"zh"),("lang-es",T,"durabilidad hormigón cloruros",None,"es"),("lang-pt",T,"concreto autoadensável",None,"pt"),("lang-de",T,"Betonfestigkeit Prüfung",None,"de"),("lang-fr",T,"durabilité des bétons",None,"fr"),("lang-ru",T,"портландцемент гидратация",None,"ru"),("lang-ko",T,"시멘트 수화",None,"ko"),("lang-id",T,"semen portland",None,"id"),("lang-it",T,"calcestruzzo durabilità",None,"it"),("lang-pl",T,"cement portlandzki",None,"pl"),("lang-tr",T,"çimento beton",None,"tr"),("lang-vi",T,"bê tông xi măng",None,"vi"),
("current-2026",S_,"concrete","2026-11-22:",None),("current-2026",S_,"cement","2026-11-22:",None),("current-2026",S_,"portland limestone cement","2026-11-01:",None),("current-2026",S_,"natural pozzolan","2026-10-15:",None),("current-2026",S_,"self-compacting concrete","2026-11-01:",None),("current-2026",S_,"cement hydration","2026-11-01:",None),
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
  if cur: f+=',to_publication_date:2026-11-23'
  p={'filter':f,'per-page':25,'sort':'relevance_score:desc' if mode=='s' else 'cited_by_count:desc','select':SEL,'mailto':'research@example.org'}
  if mode=='s': p['search']=q
  try:
    d=get('https://api.openalex.org/works?'+urllib.parse.urlencode(p)); ent['n']=sum(add(w,[t,q]) for w in d['results'])
  except Exception as e: ent['errors'].append(str(e))
  log.append(ent); print(t,q,per,lang,ent['n'],ent['errors'],flush=True); time.sleep(0.3)
json.dump(dict(log=log,skippedRepeats=skipped),open('search-log.json','w'),indent=1); json.dump(out,open('api-hits.json','w'))
# ---- citation chases
SD=json.load(open('../../site-data.json'))
FOCUS={'scm-natural','binder-international','binder-blended','concrete-structural','cross-tests-codes','cross-environment-cost','cross-chemistry','cross-mix','cross-mechanics','scm-limestone','cross-durability','concrete-polymer-refractory','concrete-scc'}
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
s19=[(r['id'],re.search(r'10\.\d{4,9}/[^\s?#]+',r['url']).group(0).lower().rstrip('/.')) for r in SD['resources'] if 4295<=int(r['id'][1:])<=4582 and re.search(r'10\.\d{4,9}/',r.get('url') or '')]
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
