"""pass-2026-11-26 harvest (adapted from pass-2026-11-25 harvest.py; focus = ledger rotation head concrete-architectural, concrete-pavement-pervious, concrete-precast-insitu-print, concrete-circular, concrete-repair-grout-overlay, standards, dot, carbon, fresh, strength, durability, scm, pavement). Earlier header: pass-2026-11-20 harvest (adapted from pass-2026-11-19 harvest.py + harvest2.py): OpenAlex title.search backfill for the ledger rotation head
(cross-mix, cross-chemistry, cross-mechanics, scm-limestone, binder-activated, cross-durability, concrete-architectural, concrete-scc,
concrete-polymer-refractory, concrete-circular, concrete-pavement-pervious, concrete-repair-grout-overlay, concrete-precast-insitu-print)
+ historical/government searches + language-filtered searches + current awareness 2026-11-01..2026-11-20 + specific missing titles
+ backward chase (refs of pre-2006 DOI records in focus topics, cited by >=2 seeds or <1990) + forward chase (top-25 cited focus records + top-10 Nov 19 additions).
All queries checked against prior-queries-all.json (passes to 2026-11-19); exact repeats skipped."""
import json,urllib.request,urllib.parse,time,re,collections
T='t';S_='s'
Q=[
("concrete-architectural",T,"self-compacting architectural concrete surface",None,None),("concrete-architectural",T,"formwork release agent concrete surface",None,None),("concrete-architectural",T,"photocatalytic concrete titanium dioxide",None,None),("concrete-architectural",T,"textured concrete facade",None,None),("concrete-architectural",T,"concrete surface blowholes",None,None),("concrete-architectural",T,"glass fibre reinforced concrete cladding",None,None),
("concrete-pavement-pervious",T,"pervious concrete clogging",None,None),("concrete-pavement-pervious",T,"pervious concrete freeze-thaw",None,None),("concrete-pavement-pervious",T,"roller compacted concrete pavement",None,None),("concrete-pavement-pervious",T,"concrete pavement faulting",None,None),("concrete-pavement-pervious",T,"airfield concrete pavement",None,None),("concrete-pavement-pervious",T,"permeable pavement stormwater concrete",None,None),
("concrete-precast-insitu-print",T,"precast concrete connections",None,None),("concrete-precast-insitu-print",T,"hollow core slab",None,None),("concrete-precast-insitu-print",T,"3D concrete printing rheology",None,None),("concrete-precast-insitu-print",T,"printable cementitious materials",None,None),("concrete-precast-insitu-print",T,"precast prestressed concrete production",None,None),("concrete-precast-insitu-print",T,"tilt-up concrete",None,None),
("concrete-circular",T,"recycled concrete powder cement",None,None),("concrete-circular",T,"recycled aggregate concrete durability",None,None),("concrete-circular",T,"construction and demolition waste aggregate",None,None),("concrete-circular",T,"recycled aggregate adhered mortar",None,None),("concrete-circular",T,"returned concrete reuse",None,None),("concrete-circular",T,"waste glass concrete aggregate",None,None),
("concrete-repair-grout-overlay",T,"repair material bond strength concrete substrate",None,None),("concrete-repair-grout-overlay",T,"FRP strengthening concrete repair",None,None),("concrete-repair-grout-overlay",T,"crack injection epoxy concrete",None,None),("concrete-repair-grout-overlay",T,"self-healing concrete cracks",None,None),("concrete-repair-grout-overlay",T,"grout bleeding post-tensioned",None,None),("concrete-repair-grout-overlay",T,"concrete overlay debonding",None,None),
("standards",T,"cement specification compliance testing",None,None),("standards",T,"concrete standard specification durability exposure classes",None,None),("standards",T,"EN 206 concrete",None,None),("standards",T,"blended cement specifications comparison",None,None),("standards",T,"standard test methods cement chemical analysis",None,None),("standards",T,"Indian standard cement concrete",None,None),
("dot",T,"bridge deck concrete specification department of transportation",None,None),("dot",T,"high performance concrete bridges state highway",None,None),("dot",T,"concrete mixture approval highway agency",None,None),("dot",T,"FHWA concrete pavement report",None,None),("dot",T,"state transportation agency fly ash specification",None,None),("dot",T,"Kansas concrete pavement",None,None),
("carbon",T,"cement CO2 emissions reduction potential",None,None),("carbon",T,"concrete carbonation CO2 sequestration",None,None),("carbon",T,"alternative fuels cement kiln emissions",None,None),("carbon",T,"low clinker cement environmental assessment",None,None),("carbon",T,"carbon pricing cement industry",None,None),("carbon",T,"global warming potential concrete mixtures",None,None),
("fresh",T,"fresh concrete air content",None,None),("fresh",T,"superplasticizer slump retention",None,None),("fresh",T,"thixotropy cement paste",None,None),("fresh",T,"concrete setting ultrasonic",None,None),("fresh",T,"fresh concrete segregation",None,None),("fresh",T,"workability retention admixture",None,None),
("strength",T,"compressive strength prediction concrete",None,None),("strength",T,"strength gain blended cement concrete",None,None),("strength",T,"concrete core strength",None,None),("strength",T,"temperature effect concrete strength development",None,None),("strength",T,"rebound hammer concrete strength",None,None),("strength",T,"early age strength limestone cement",None,None),
("durability",T,"alkali silica reaction mitigation",None,None),("durability",T,"concrete deicing salt damage",None,None),("durability",T,"acid attack concrete",None,None),("durability",T,"concrete leaching calcium",None,None),("durability",T,"chloride threshold reinforcement corrosion",None,None),("durability",T,"marine concrete durability",None,None),
("scm",T,"supplementary cementitious materials reactivity test",None,None),("scm",T,"high volume supplementary cementitious materials",None,None),("scm",T,"pozzolan durability concrete",None,None),("scm",T,"slag fly ash blended concrete strength",None,None),("scm",T,"SCM supply shortage",None,None),("scm",T,"R3 test reactivity",None,None),
("pavement",T,"concrete pavement cracking",None,None),("pavement",T,"concrete pavement design method",None,None),("pavement",T,"concrete pavement rehabilitation",None,None),("pavement",T,"pavement concrete mixture",None,None),("pavement",T,"concrete pavement texture skid",None,None),("pavement",T,"concrete pavement thickness",None,None),
("concrete-architectural",S_,"architectural concrete history",":1980",None),("concrete-pavement-pervious",S_,"concrete roads early experience",":1950",None),("concrete-precast-insitu-print",S_,"precast concrete industry history",":1975",None),("concrete-circular",S_,"reuse of crushed concrete as aggregate",":1985",None),("concrete-repair-grout-overlay",S_,"repair of concrete structures",":1980",None),("standards",S_,"cement standard specification",":1940",None),("dot",S_,"state highway department concrete",":1960",None),("carbon",S_,"cement kiln fuel energy",":1980",None),("fresh",S_,"workability of concrete",":1960",None),("strength",S_,"strength of concrete water cement ratio",":1940",None),("durability",S_,"deterioration of concrete",":1960",None),("scm",S_,"pozzolanic admixtures concrete",":1960",None),("pavement",S_,"concrete pavement",":1940",None),
("lang-es",T,"hormigón reciclado",None,"es"),("lang-pt",T,"concreto permeável",None,"pt"),("lang-de",T,"Betonfahrbahn",None,"de"),("lang-fr",T,"béton recyclé",None,"fr"),("lang-ja",T,"コンクリート 舗装",None,"ja"),("lang-zh",T,"再生骨料混凝土",None,"zh"),("lang-it",T,"calcestruzzo durabilità",None,"it"),("lang-pl",T,"beton nawierzchnia",None,"pl"),("lang-ru",T,"бетон прочность",None,"ru"),("lang-tr",T,"geri dönüştürülmüş agrega beton",None,"tr"),("lang-id",T,"beton porous",None,"id"),("lang-ko",T,"콘크리트",None,"ko"),("lang-nl",T,"beton",None,"nl"),("lang-cs",T,"beton",None,"cs"),("lang-pt",T,"agregado reciclado concreto",None,"pt"),("lang-de",T,"Recyclingbeton",None,"de"),
("current-2026",S_,"concrete","2026-11-25:",None),("current-2026",S_,"cement","2026-11-25:",None),("current-2026",S_,"recycled aggregate concrete","2026-11-15:",None),("current-2026",S_,"concrete pavement","2026-11-10:",None),("current-2026",S_,"3D printed concrete","2026-11-10:",None),("current-2026",S_,"portland limestone cement","2026-11-10:",None),("current-2026",S_,"concrete carbon emissions","2026-11-15:",None),("current-2026",S_,"alkali-silica reaction","2026-11-01:",None),
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
  if cur: f+=',to_publication_date:2026-11-26'
  p={'filter':f,'per-page':25,'sort':'relevance_score:desc' if mode=='s' else 'cited_by_count:desc','select':SEL,'mailto':'research@example.org'}
  if mode=='s': p['search']=q
  try:
    d=get('https://api.openalex.org/works?'+urllib.parse.urlencode(p)); ent['n']=sum(add(w,[t,q]) for w in d['results'])
  except Exception as e: ent['errors'].append(str(e))
  log.append(ent); print(t,q,per,lang,ent['n'],ent['errors'],flush=True); time.sleep(0.3)
json.dump(dict(log=log,skippedRepeats=skipped),open('search-log.json','w'),indent=1); json.dump(out,open('api-hits.json','w'))
# ---- citation chases
SD=json.load(open('../../site-data.json'))
FOCUS={'concrete-architectural','concrete-pavement-pervious','concrete-precast-insitu-print','concrete-circular','concrete-repair-grout-overlay','standards','dot','carbon','fresh','strength','durability','scm','pavement'}
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
s19=[(r['id'],re.search(r'10\.\d{4,9}/[^\s?#]+',r['url']).group(0).lower().rstrip('/.')) for r in SD['resources'] if 4583<=int(r['id'][1:])<=4908 and re.search(r'10\.\d{4,9}/',r.get('url') or '')]
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
