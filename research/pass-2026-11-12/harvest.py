"""pass-2026-11-12 harvest: OpenAlex title.search (period-split) historical backfill for the next rotation topics
(never daily-backfilled: cross-durability, cross-tests-codes, cross-environment-cost, binder-cac-csa, binder-activated,
binder-magnesium-carbonatable, scm-silica, scm-emerging, scm-slag, concrete-lightweight, binder-lc3) + Type IL legacy topics
(standards, dot, carbon, fresh, strength via PLC/limestone queries) + non-English (language filter) + current awareness 2026-09..11."""
import json,urllib.request,urllib.parse,time
# (topic, mode, query, period, lang)  mode: t=title.search, s=search
Q=[
("cross-durability","t","alkali-silica reaction",":1990",None),("cross-durability","t","alkali-aggregate reaction","1991:2010",None),
("cross-durability","t","delayed ettringite formation",None,None),("cross-durability","t","freeze-thaw resistance concrete",":2005",None),
("cross-durability","t","chloride diffusion concrete",":2000",None),("cross-durability","t","carbonation of concrete",":2000",None),
("cross-durability","t","sulfate attack concrete",":2000",None),("cross-durability","t","corrosion of reinforcement concrete",":1995",None),
("cross-durability","t","service life prediction concrete",None,None),("cross-durability","t","acid attack concrete",None,None),
("cross-tests-codes","t","rapid chloride permeability",None,None),("cross-tests-codes","t","maturity method concrete",None,None),
("cross-tests-codes","t","nondestructive testing concrete",":2005",None),("cross-tests-codes","t","ultrasonic pulse velocity concrete",None,None),
("cross-tests-codes","t","surface resistivity concrete",None,None),("cross-tests-codes","t","round robin test concrete",None,None),
("cross-tests-codes","t","precision of test method cement",None,None),
("cross-environment-cost","t","life cycle assessment concrete",":2012",None),("cross-environment-cost","t","embodied carbon concrete",None,None),
("cross-environment-cost","t","cement kiln emissions",None,None),("cross-environment-cost","t","carbon capture cement plant",None,None),
("cross-environment-cost","t","alternative fuels cement kiln",None,None),("cross-environment-cost","t","energy consumption cement production",None,None),
("binder-cac-csa","t","calcium aluminate cement",":1995",None),("binder-cac-csa","t","calcium aluminate cement","1996:2015",None),
("binder-cac-csa","t","sulfoaluminate cement",":2010",None),("binder-cac-csa","t","ettringite binder",None,None),("binder-cac-csa","t","belite calcium sulfoaluminate",None,None),
("binder-activated","t","alkali-activated slag",":2005",None),("binder-activated","t","geopolymer",":2007",None),("binder-activated","t","alkali activated fly ash",None,None),
("binder-activated","t","one-part geopolymer",None,None),("binder-activated","t","alkali-activated concrete durability",None,None),
("binder-magnesium-carbonatable","t","magnesium oxychloride cement",None,None),("binder-magnesium-carbonatable","t","magnesium phosphate cement",None,None),
("binder-magnesium-carbonatable","t","Sorel cement",None,None),("binder-magnesium-carbonatable","t","carbonation curing concrete",None,None),("binder-magnesium-carbonatable","t","reactive magnesia",None,None),
("scm-silica","t","silica fume",":1995",None),("scm-silica","t","condensed silica fume",None,None),("scm-silica","t","rice husk ash",":2010",None),("scm-silica","t","nano-silica cement",None,None),
("scm-emerging","t","waste glass pozzolan",None,None),("scm-emerging","t","sugarcane bagasse ash",None,None),("scm-emerging","t","palm oil fuel ash",None,None),
("scm-emerging","t","municipal solid waste incineration ash cement",None,None),("scm-emerging","t","red mud cement",None,None),("scm-emerging","t","steel slag cementitious",None,None),
("scm-slag","t","blast-furnace slag",":1985",None),("scm-slag","t","slag activity index",None,None),("scm-slag","t","granulated slag cement","1986:2005",None),
("concrete-lightweight","t","lightweight aggregate concrete",":1995",None),("concrete-lightweight","t","expanded clay aggregate",None,None),("concrete-lightweight","t","internal curing lightweight aggregate",None,None),
("concrete-lightweight","t","pumice lightweight concrete",None,None),("concrete-lightweight","t","sintered fly ash aggregate",None,None),
("binder-lc3","t","calcined clay limestone",None,None),("binder-lc3","t","LC3",None,None),
# Type IL legacy collection topics (PLC-specific)
("pll-std","s","portland-limestone cement ASTM C595 Type IL specification",None,None),("pll-std","s","limestone content cement standard EN 197-1 CEM II/A-L CEM II/B-LL",None,None),
("pll-dot","s","portland limestone cement state department of transportation field trial",None,None),("pll-carbon","s","portland limestone cement CO2 reduction environmental product declaration",None,None),
("pll-fresh","s","limestone cement setting time workability water demand",None,None),("pll-strength","s","interground limestone cement fineness strength development",None,None),
# non-English historical/national literature (language filter)
("lang-de","t","Zement",":2010","de"),("lang-de","t","Beton",":2010","de"),("lang-fr","t","ciment",None,"fr"),("lang-fr","t","béton",None,"fr"),
("lang-es","t","cemento",None,"es"),("lang-es","t","hormigón",None,"es"),("lang-pt","t","cimento",None,"pt"),("lang-pt","t","concreto",None,"pt"),
("lang-ja","s","cement concrete",None,"ja"),("lang-zh","s","cement concrete",None,"zh"),
# current awareness (Sept–Nov 2026)
("current-2026","s","cement","2026-09-15:",None),("current-2026","s","concrete","2026-09-15:",None),("current-2026","s","calcium sulfoaluminate","2026-07-01:",None),
("current-2026","s","geopolymer concrete","2026-09-01:",None),("current-2026","s","magnesium cement","2026-07-01:",None),("current-2026","s","lightweight aggregate concrete","2026-07-01:",None),
("current-2026","s","life cycle assessment concrete","2026-08-01:",None),("current-2026","s","alkali-silica reaction","2026-07-01:",None),("current-2026","s","silica fume","2026-07-01:",None),
("current-2026","s","standard specification cement","2026-01-01:",None),
]
out={};log=[]
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def get(u):
  err=None
  for i in range(4):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    except Exception as e: err=e; time.sleep(3*(i+1))
  raise err
SEL='id,doi,title,publication_year,publication_date,type,language,cited_by_count,authorships,primary_location,abstract_inverted_index,is_retracted,open_access,biblio,referenced_works'
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
  log.append(ent); print(t,q,per,lang,ent['n'],ent['errors'],flush=True); time.sleep(0.4)
json.dump(log,open('search-log.json','w'),indent=1); json.dump(out,open('api-hits.json','w'))
print(len(out))
