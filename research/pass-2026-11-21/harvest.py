"""pass-2026-11-20 harvest (adapted from pass-2026-11-19 harvest.py + harvest2.py): OpenAlex title.search backfill for the ledger rotation head
(cross-mix, cross-chemistry, cross-mechanics, scm-limestone, binder-activated, cross-durability, concrete-architectural, concrete-scc,
concrete-polymer-refractory, concrete-circular, concrete-pavement-pervious, concrete-repair-grout-overlay, concrete-precast-insitu-print)
+ historical/government searches + language-filtered searches + current awareness 2026-11-01..2026-11-20 + specific missing titles
+ backward chase (refs of pre-2006 DOI records in focus topics, cited by >=2 seeds or <1990) + forward chase (top-25 cited focus records + top-10 Nov 19 additions).
All queries checked against prior-queries-all.json (passes to 2026-11-19); exact repeats skipped."""
import json,urllib.request,urllib.parse,time,re,collections
T='t';S_='s'
Q=[
("standards",T,"ASTM C595 blended hydraulic cement",None,None),("standards",T,"ASTM C1157 performance specification hydraulic cement",None,None),("standards",T,"EN 197-1 cement composition specifications",None,None),("standards",T,"cement standards harmonisation Europe",None,None),("standards",T,"limestone content cement standard permitted",None,None),("standards",T,"CSA A3001 cementitious materials",None,None),("standards",T,"performance-based cement specification",None,None),("standards",T,"cement classification standard history",None,None),("standards",S_,"ASTM C150 portland cement specification revision",None,None),
("dot",T,"state highway agency cement specification",None,None),("dot",T,"department of transportation concrete mixtures",None,None),("dot",T,"transportation agency supplementary cementitious materials specification",None,None),("dot",T,"bridge deck concrete cracking specification",None,None),("dot",T,"highway concrete performance specification",None,None),("dot",T,"AASHTO concrete specification performance engineered mixtures",None,None),("dot",T,"concrete pavement state DOT implementation",None,None),("dot",S_,"Federal Highway Administration cement concrete research report",":2000",None),
("carbon",T,"cement industry carbon dioxide emissions",None,None),("carbon",T,"life cycle assessment concrete",None,None),("carbon",T,"clinker substitution CO2",None,None),("carbon",T,"embodied carbon concrete",None,None),("carbon",T,"cement decarbonisation roadmap",None,None),("carbon",T,"environmental product declaration cement",None,None),("carbon",T,"carbon capture cement plant",None,None),("carbon",T,"low carbon concrete",None,None),
("fresh",T,"concrete workability",None,None),("fresh",T,"setting time of cement",None,None),("fresh",T,"concrete slump loss",None,None),("fresh",T,"concrete bleeding",None,None),("fresh",T,"cement paste rheology",None,None),("fresh",T,"plastic shrinkage cracking",None,None),("fresh",T,"concrete pumping",None,None),("fresh",T,"cement false set",None,None),
("strength",T,"compressive strength development of concrete",None,None),("strength",T,"early age strength cement",None,None),("strength",T,"strength activity index",None,None),("strength",T,"maturity method concrete",None,None),("strength",T,"cement mortar strength test",None,None),("strength",T,"flexural strength concrete",None,None),("strength",T,"concrete elastic modulus",None,None),("strength",T,"cube strength cylinder strength",None,None),
("durability",T,"thaumasite sulfate attack",None,None),("durability",T,"freeze-thaw resistance concrete",None,None),("durability",T,"chloride penetration resistance concrete",None,None),("durability",T,"concrete permeability",None,None),("durability",T,"concrete service life prediction",None,None),("durability",T,"sulfate resistance of cement",None,None),("durability",T,"delayed ettringite formation",None,None),("durability",T,"concrete abrasion resistance",None,None),
("scm",T,"ternary blended cement",None,None),("scm",T,"supplementary cementitious materials availability",None,None),("scm",T,"fly ash and slag in concrete",None,None),("scm",T,"cement replacement materials",None,None),("scm",T,"composite cement",None,None),("scm",T,"pozzolanic activity test",None,None),
("pavement",T,"concrete pavement joint",None,None),("pavement",T,"concrete pavement durability",None,None),("pavement",T,"slipform paving",None,None),("pavement",T,"dowel bar concrete pavement",None,None),("pavement",T,"concrete pavement curling warping",None,None),("pavement",T,"jointed plain concrete pavement",None,None),("pavement",T,"continuously reinforced concrete pavement",None,None),
("apps",T,"precast concrete bridge girders",None,None),("apps",T,"prestressed concrete",None,None),("apps",T,"concrete masonry units",None,None),("apps",T,"concrete pipe",None,None),("apps",T,"ready-mixed concrete",None,None),("apps",T,"concrete dam",None,None),("apps",T,"marine concrete structures",None,None),
("mix",T,"water cement ratio",None,None),("mix",T,"concrete mix design method",None,None),("mix",T,"particle packing concrete",None,None),("mix",T,"optimization of concrete mixtures",None,None),("mix",T,"high volume fly ash concrete",None,None),("mix",T,"concrete mixture cement content minimum",None,None),
("field",T,"concrete finishing",None,None),("field",T,"hot weather concreting",None,None),("field",T,"cold weather concreting",None,None),("field",T,"concrete curing",None,None),("field",T,"concrete quality control",None,None),("field",T,"concrete placement construction practice",None,None),("field",T,"field performance of concrete",None,None),("field",T,"concrete surface defects",None,None),
("supply",T,"cement plant production",None,None),("supply",T,"cement market",None,None),("supply",T,"cement supply chain",None,None),("supply",T,"cement kiln fuel alternative",None,None),("supply",T,"limestone quarry cement raw materials",None,None),("supply",T,"cement transport and distribution",None,None),
("intl",T,"cement in India",None,None),("intl",T,"cement in China",None,None),("intl",T,"cement in Brazil",None,None),("intl",T,"cement in Africa",None,None),("intl",T,"cement regulations Japan",None,None),("intl",T,"cement Australia standard",None,None),("intl",T,"cement in the Middle East",None,None),
# historical
("standards",S_,"specifications for portland cement history",":1960",None),("fresh",S_,"consistency of concrete tests early",":1960",None),("strength",S_,"strength of concrete laboratory investigation",":1950",None),("durability",S_,"durability of concrete exposure tests",":1960",None),("pavement",S_,"concrete roads design",":1960",None),("mix",S_,"proportioning concrete mixtures bulletin",":1960",None),("field",S_,"concrete construction practice handbook",":1970",None),("apps",S_,"reinforced concrete practice textbook",":1950",None),
# languages
("lang-es",T,"cemento portland adicionado",None,"es"),("lang-pt",T,"cimento portland composto",None,"pt"),("lang-de",T,"Zement Normen",None,"de"),("lang-fr",T,"ciment résistance",None,"fr"),("lang-ja",T,"セメント",None,"ja"),("lang-zh",T,"水泥",None,"zh"),("lang-es",T,"durabilidad del hormigón",None,"es"),("lang-pt",T,"durabilidade do concreto",None,"pt"),("lang-de",T,"Betonfahrbahn",None,"de"),("lang-fr",T,"béton routier",None,"fr"),("lang-tr",T,"çimento",None,"tr"),("lang-ko",T,"시멘트",None,"ko"),("lang-id",T,"semen beton",None,"id"),
# current awareness
("current-2026",S_,"concrete","2026-11-20:",None),("current-2026",S_,"cement","2026-11-20:",None),("current-2026",S_,"limestone calcined clay cement","2026-11-01:",None),("current-2026",S_,"portland limestone cement","2026-10-01:",None),("current-2026",S_,"low carbon concrete","2026-11-01:",None),
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
  if cur: f+=',to_publication_date:2026-11-21'
  p={'filter':f,'per-page':25,'sort':'relevance_score:desc' if mode=='s' else 'cited_by_count:desc','select':SEL,'mailto':'research@example.org'}
  if mode=='s': p['search']=q
  try:
    d=get('https://api.openalex.org/works?'+urllib.parse.urlencode(p)); ent['n']=sum(add(w,[t,q]) for w in d['results'])
  except Exception as e: ent['errors'].append(str(e))
  log.append(ent); print(t,q,per,lang,ent['n'],ent['errors'],flush=True); time.sleep(0.3)
json.dump(dict(log=log,skippedRepeats=skipped),open('search-log.json','w'),indent=1); json.dump(out,open('api-hits.json','w'))
# ---- citation chases
SD=json.load(open('../../site-data.json'))
FOCUS={'standards','dot','carbon','fresh','strength','durability','scm','pavement','apps','mix','field','supply','intl'}
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
s19=[(r['id'],re.search(r'10\.\d{4,9}/[^\s?#]+',r['url']).group(0).lower().rstrip('/.')) for r in SD['resources'] if 3561<=int(r['id'][1:])<=4045 and re.search(r'10\.\d{4,9}/',r.get('url') or '')]
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
