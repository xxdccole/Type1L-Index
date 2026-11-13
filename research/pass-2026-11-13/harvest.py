"""pass-2026-11-13 harvest: OpenAlex title.search (period-split) historical backfill for the next rotation topics
(least-searched family topics: binder-portland, scm-flyash, concrete-fibers, concrete-scc, concrete-architectural,
concrete-polymer-refractory, concrete-pavement-pervious, concrete-repair-grout-overlay, concrete-precast-insitu-print,
concrete-circular, concrete-hpc) + Type IL legacy topics (pavement, mix, field, mass, microcracking, apps via PLC/limestone
queries) + non-English (new languages it, nl, ru, pl, cs, tr, ko; new terms for de/fr/es) + current awareness 2026-10-01..11-12."""
import json,urllib.request,urllib.parse,time
Q=[
("binder-portland","t","portland cement clinker",":1975",None),("binder-portland","t","sulfate resisting portland cement",None,None),
("binder-portland","t","low heat portland cement",None,None),("binder-portland","t","air-entrained concrete",":1980",None),
("binder-portland","t","cement fineness",None,None),("binder-portland","t","alite belite",None,None),("binder-portland","t","gypsum optimum cement",None,None),
("scm-flyash","t","fly ash concrete",":1985",None),("scm-flyash","t","fly ash concrete","1986:2000",None),("scm-flyash","t","high-volume fly ash",None,None),
("scm-flyash","t","pulverized fuel ash",None,None),("scm-flyash","t","class C fly ash",None,None),("scm-flyash","t","fly ash pozzolanic reaction",None,None),
("concrete-fibers","t","steel fibre reinforced concrete",":1995",None),("concrete-fibers","t","fiber reinforced concrete","1996:2010",None),
("concrete-fibers","t","polypropylene fibre concrete",None,None),("concrete-fibers","t","engineered cementitious composites",None,None),
("concrete-fibers","t","textile reinforced concrete",None,None),("concrete-fibers","t","basalt fiber concrete",None,None),("concrete-fibers","t","glass fibre reinforced cement",":2005",None),
("concrete-scc","t","self-compacting concrete",":2005",None),("concrete-scc","t","self-consolidating concrete",None,None),("concrete-scc","t","self-compacting concrete rheology",None,None),
("concrete-scc","t","viscosity modifying admixture",None,None),("concrete-scc","t","passing ability",None,None),
("concrete-architectural","t","architectural concrete",None,None),("concrete-architectural","t","exposed concrete surface",None,None),("concrete-architectural","t","white concrete",None,None),
("concrete-architectural","t","pigmented concrete",None,None),("concrete-architectural","t","efflorescence",None,None),("concrete-architectural","t","fair-faced concrete",None,None),
("concrete-polymer-refractory","t","polymer concrete",":2000",None),("concrete-polymer-refractory","t","polymer-modified mortar",None,None),("concrete-polymer-refractory","t","polymer impregnated concrete",None,None),
("concrete-polymer-refractory","t","refractory concrete",None,None),("concrete-polymer-refractory","t","refractory castable",":2005",None),("concrete-polymer-refractory","t","latex modified concrete",None,None),
("concrete-pavement-pervious","t","concrete pavement",":1990",None),("concrete-pavement-pervious","t","concrete pavement","1991:2010",None),("concrete-pavement-pervious","t","pervious concrete",":2012",None),
("concrete-pavement-pervious","t","porous concrete",None,None),("concrete-pavement-pervious","t","dowel bar concrete pavement",None,None),("concrete-pavement-pervious","t","concrete pavement curling",None,None),
("concrete-repair-grout-overlay","t","concrete repair",":2000",None),("concrete-repair-grout-overlay","t","repair mortar",None,None),("concrete-repair-grout-overlay","t","cement grout",None,None),
("concrete-repair-grout-overlay","t","bonded overlay",None,None),("concrete-repair-grout-overlay","t","cathodic protection reinforced concrete",None,None),("concrete-repair-grout-overlay","t","patch repair concrete",None,None),
("concrete-precast-insitu-print","t","precast concrete",":1995",None),("concrete-precast-insitu-print","t","steam curing concrete",None,None),("concrete-precast-insitu-print","t","3D printed concrete",None,None),
("concrete-precast-insitu-print","t","slipform",None,None),("concrete-precast-insitu-print","t","extrusion cementitious",None,None),
("concrete-circular","t","recycled aggregate concrete",":2005",None),("concrete-circular","t","recycled concrete aggregate","2006:2015",None),("concrete-circular","t","demolition waste concrete",None,None),
("concrete-circular","t","CO2 curing concrete",None,None),("concrete-circular","t","crushed concrete fines",None,None),
("concrete-hpc","t","high-strength concrete",":1995",None),("concrete-hpc","t","high-performance concrete","1990:2005",None),("concrete-hpc","t","ultra-high performance concrete",":2012",None),
("concrete-hpc","t","reactive powder concrete",None,None),("concrete-hpc","t","autogenous shrinkage high-performance concrete",None,None),
# Type IL legacy collection topics (PLC-specific)
("pll-pavement","s","portland limestone cement concrete pavement performance",None,None),("pll-mix","s","portland limestone cement mix design proportioning",None,None),
("pll-field","s","portland limestone cement finishing bleeding field experience",None,None),("pll-mass","s","limestone cement heat of hydration mass concrete",None,None),
("pll-micro","s","limestone filler interfacial transition zone microstructure",None,None),("pll-apps","s","portland limestone cement precast bridge deck",None,None),
("pll-ttl","t","limestone cement",":2000",None),("pll-ttl","t","limestone filler","2001:2015",None),
# non-English (new languages/terms)
("lang-it","t","calcestruzzo",None,"it"),("lang-it","t","cemento",None,"it"),("lang-nl","t","beton",None,"nl"),("lang-ru","t","бетон",None,"ru"),("lang-ru","t","цемент",None,"ru"),
("lang-pl","t","beton",None,"pl"),("lang-pl","t","cement",None,"pl"),("lang-cs","t","beton",None,"cs"),("lang-tr","t","beton",None,"tr"),("lang-tr","t","çimento",None,"tr"),("lang-ko","s","concrete",None,"ko"),
("lang-de","t","Betonstraße",None,"de"),("lang-de","t","Zement","2011:2026","de"),("lang-fr","t","mortier",None,"fr"),("lang-es","t","mortero",None,"es"),("lang-ja","s","concrete","2000:2026","ja"),
# current awareness (Oct–Nov 2026)
("current-2026","s","portland cement clinker","2026-09-01:",None),("current-2026","s","fly ash concrete","2026-09-01:",None),("current-2026","s","fiber reinforced concrete","2026-10-01:",None),
("current-2026","s","self-compacting concrete","2026-09-01:",None),("current-2026","s","concrete pavement","2026-09-01:",None),("current-2026","s","concrete repair","2026-09-01:",None),
("current-2026","s","3D printing concrete","2026-10-01:",None),("current-2026","s","recycled aggregate concrete","2026-10-01:",None),("current-2026","s","ultra-high performance concrete","2026-10-01:",None),
("current-2026","s","polymer concrete","2026-08-01:",None),("current-2026","s","portland limestone cement","2026-08-01:",None),("current-2026","s","concrete","2026-10-20:",None),
]
out={};log=[]
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def get(u):
  err=None
  for i in range(5):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    except Exception as e: err=e; time.sleep(4*(i+1))
  raise err
SEL='id,doi,title,publication_year,publication_date,type,language,cited_by_count,authorships,primary_location,abstract_inverted_index,is_retracted,open_access,biblio'
for t,mode,q,per,lang in Q:
  ent={"topic":t,"mode":'title.search' if mode=='t' else 'search',"query":q,"period":per,"language":lang,"n":0,"errors":[]}
  f='type:article|book-chapter|report|dissertation|book|review|standard'
  if mode=='t': f='title.search:%s,'%q.replace(',',' ')+f
  if lang: f+=',language:'+lang
  cur=t=='current-2026'
  if per:
    a,b=per.split(':')
    if a: f+=',from_publication_date:%s'%(a if '-' in a else a+'-01-01')
    if b: f+=',to_publication_date:%s-12-31'%b
  if cur: f+=',to_publication_date:2026-11-12'
  p={'filter':f,'per-page':25,'sort':'relevance_score:desc' if (mode=='s') else 'cited_by_count:desc','select':SEL,'mailto':'research@example.org'}
  if mode=='s': p['search']=q
  try:
    d=get('https://api.openalex.org/works?'+urllib.parse.urlencode(p))
    for w in d['results']:
      k=(w.get('doi') or w['id']).lower()
      if k in out: out[k]['queries'].append([t,q]); continue
      w['queries']=[[t,q]]; out[k]=w; ent['n']+=1
  except Exception as e: ent['errors'].append(str(e))
  log.append(ent); print(t,q,per,lang,ent['n'],ent['errors'],flush=True); time.sleep(0.5)
json.dump(log,open('search-log.json','w'),indent=1); json.dump(out,open('api-hits.json','w'))
print(len(out))
