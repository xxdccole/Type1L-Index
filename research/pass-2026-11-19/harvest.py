"""pass-2026-11-19 harvest: OpenAlex title.search/search backfill for next rotation head (concrete-lightweight, binder-cac-csa, binder-lc3,\nbinder-magnesium-carbonatable, scm-silica, scm-slag, scm-emerging, binder-blended, concrete-structural, cross-tests-codes, cross-environment-cost)\n+ historical/government/standards sweep + Type IL legacy topics + languages + current awareness 2026-11-17..11-19. Copied from pass-2026-11-18."""
import json,urllib.request,urllib.parse,time,sys
Q=[
("concrete-lightweight","t","lightweight concrete",":2000",None),("concrete-lightweight","t","lightweight concrete","2001:2026",None),("concrete-lightweight","t","expanded shale",None,None),("concrete-lightweight","t","expanded perlite concrete",None,None),
("concrete-lightweight","t","scoria aggregate",None,None),("concrete-lightweight","t","oil palm shell concrete",None,None),("concrete-lightweight","t","polystyrene concrete",None,None),("concrete-lightweight","t","cenosphere",None,None),
("concrete-lightweight","t","lightweight self-compacting concrete",None,None),("concrete-lightweight","t","artificial lightweight aggregate",None,None),("concrete-lightweight","t","no-fines concrete",None,None),("concrete-lightweight","t","vermiculite concrete",None,None),
("binder-cac-csa","t","high alumina cement","1996:2026",None),("binder-cac-csa","t","aluminous cement",None,None),("binder-cac-csa","t","monocalcium aluminate",None,None),
("binder-cac-csa","t","ye'elimite",None,None),("binder-cac-csa","t","calcium sulfoaluminate","2016:2026",None),("binder-cac-csa","t","sulfoaluminate clinker",None,None),("binder-cac-csa","t","ettringite formation expansion",None,None),("binder-cac-csa","t","calcium aluminate cement hydration",None,None),
("binder-lc3","t","limestone calcined clay","2023:2026",None),("binder-lc3","t","LC3 concrete",None,None),("binder-lc3","t","ternary limestone metakaolin",None,None),("binder-lc3","t","calcined clay carbonation",None,None),("binder-lc3","t","calcined clay chloride",None,None),
("binder-lc3","t","low grade calcined clay",None,None),("binder-lc3","t","flash calcined clay",None,None),("binder-lc3","t","kaolinite content calcined clay",None,None),
("binder-magnesium-carbonatable","t","magnesium oxysulfate cement",None,None),("binder-magnesium-carbonatable","t","magnesium potassium phosphate",None,None),("binder-magnesium-carbonatable","t","MgO cement",None,None),("binder-magnesium-carbonatable","t","CO2 curing",None,None),
("binder-magnesium-carbonatable","t","accelerated carbonation curing",None,None),("binder-magnesium-carbonatable","t","wollastonite carbonation",None,None),("binder-magnesium-carbonatable","t","gamma dicalcium silicate",None,None),("binder-magnesium-carbonatable","t","calcium silicate carbonation",None,None),("binder-magnesium-carbonatable","t","magnesia cement",None,None),
("scm-silica","t","microsilica",None,None),("scm-silica","t","silica fume",":2000",None),("scm-silica","t","silica fume","2001:2026",None),("scm-silica","t","nano silica concrete",None,None),("scm-silica","t","colloidal silica cement",None,None),("scm-silica","t","densified silica fume",None,None),("scm-silica","t","silica fume mortar",None,None),
("scm-slag","t","slag cement",":1990",None),("scm-slag","t","slag cement","1991:2026",None),("scm-slag","t","ground granulated blast furnace slag",":2005",None),("scm-slag","t","ground granulated blast furnace slag","2006:2026",None),("scm-slag","t","GGBS concrete",None,None),
("scm-slag","t","slag hydration",None,None),("scm-slag","t","copper slag concrete",None,None),("scm-slag","t","slag concrete durability",None,None),("scm-slag","t","steel slag aggregate",None,None),
("scm-emerging","t","ferronickel slag",None,None),("scm-emerging","t","waste glass concrete",None,None),("scm-emerging","t","coal gangue cement",None,None),("scm-emerging","t","phosphogypsum cement",None,None),("scm-emerging","t","ceramic waste powder",None,None),
("scm-emerging","t","recycled concrete powder",None,None),("scm-emerging","t","biochar cement",None,None),("scm-emerging","t","sewage sludge ash",None,None),("scm-emerging","t","marble powder concrete",None,None),("scm-emerging","t","eggshell powder",None,None),
("binder-blended","t","blended cement",":1995",None),("binder-blended","t","blended cement","1996:2026",None),("binder-blended","t","ternary blended",None,None),("binder-blended","t","portland pozzolan cement",None,None),("binder-blended","t","composite cement",":2010",None),
("binder-blended","t","multi-component cement",None,None),("binder-blended","t","blended cement hydration",None,None),("binder-blended","t","pozzolanic cement",":1990",None),
("concrete-structural","t","reinforced concrete beams",":1990",None),("concrete-structural","t","prestressed concrete",":1980",None),("concrete-structural","t","punching shear",None,None),("concrete-structural","t","reinforced concrete columns confinement",None,None),
("concrete-structural","t","bond reinforcing bars concrete",None,None),("concrete-structural","t","creep of concrete",None,None),("concrete-structural","t","precast concrete",None,None),("concrete-structural","t","post-tensioned concrete",None,None),("concrete-structural","t","reinforced concrete shear walls",None,None),("concrete-structural","t","high strength concrete columns",None,None),
("cross-tests-codes","t","rebound hammer",None,None),("cross-tests-codes","t","concrete core strength",None,None),("cross-tests-codes","t","chloride migration test",None,None),("cross-tests-codes","t","water permeability concrete",None,None),
("cross-tests-codes","t","freeze-thaw test",None,None),("cross-tests-codes","t","Eurocode 2",None,None),("cross-tests-codes","t","ACI 318",None,None),("cross-tests-codes","t","building code concrete",None,None),("cross-tests-codes","t","slump test",None,None),("cross-tests-codes","t","specimen size compressive strength concrete",None,None),("cross-tests-codes","t","acceptance testing concrete",None,None),
("cross-environment-cost","t","cement industry CO2",None,None),("cross-environment-cost","t","clinker substitution",None,None),("cross-environment-cost","t","environmental product declaration",None,None),("cross-environment-cost","t","carbon footprint concrete",None,None),
("cross-environment-cost","t","CO2 uptake carbonation concrete",None,None),("cross-environment-cost","t","cement decarbonization",None,None),("cross-environment-cost","t","waste heat recovery cement",None,None),("cross-environment-cost","t","concrete recycling",":2005",None),("cross-environment-cost","t","cost analysis concrete",None,None),
# historical / government / standards / theses
("cross-tests-codes","s","Bureau of Reclamation concrete laboratory report",":1980",None),("cross-tests-codes","s","National Bureau of Standards portland cement investigation",":1975",None),("cross-tests-codes","s","Highway Research Board concrete durability",":1975",None),
("cross-tests-codes","s","FHWA report concrete performance",None,None),("cross-tests-codes","s","standard specification portland cement history",":1960",None),("binder-blended","s","blended cement dissertation thesis",None,None),("scm-slag","s","slag cement historical development",":1970",None),
# Type IL legacy
("pll-mix","s","portland limestone cement concrete mix design proportioning",None,None),("pll-supply","s","portland limestone cement market adoption producers",None,None),("pll-intl","s","limestone cement CEM II/A-L Europe experience",None,None),
("pll-apps","s","portland limestone cement precast ready mixed applications",None,None),("pll-field","s","portland limestone cement field trial bridge deck",None,None),("pll-mix","s","limestone filler concrete packing water demand",None,None),("pll-strength","s","limestone powder blended cement strength development",None,None),("pll-durability","s","limestone cement chloride carbonation resistance",None,None),
# languages (new: it, pl, tr, cs, ru, ko, nl, no, da, fi; re-queried with new terms: pt, es, de, fr, zh, ja)
("lang-it","t","malta",None,"it"),("lang-it","t","leganti",None,"it"),("lang-pl","t","betonu",None,"pl"),("lang-pl","t","zaprawy",None,"pl"),("lang-tr","t","betonarme",None,"tr"),("lang-tr","t","harç",None,"tr"),("lang-cs","t","betonu",None,"cs"),
("lang-ru","t","бетона",None,"ru"),("lang-ru","t","цемента",None,"ru"),("lang-ko","s","cement",None,"ko"),("lang-nl","t","cement",None,"nl"),("lang-no","t","betong",None,"no"),("lang-da","t","beton",None,"da"),("lang-fi","t","betoni",None,"fi"),
("lang-pt","t","argamassa",None,"pt"),("lang-es","t","puzolana",None,"es"),("lang-de","t","Mörtel",None,"de"),("lang-fr","t","liant",None,"fr"),("lang-zh","s","slag",None,"zh"),("lang-ja","s","fly ash",None,"ja"),
# current awareness
("current-2026","s","cement","2026-11-17:",None),("current-2026","s","concrete","2026-11-17:",None),("current-2026","s","lightweight concrete","2026-09-15:",None),("current-2026","s","calcium sulfoaluminate","2026-10-01:",None),
("current-2026","s","limestone calcined clay cement","2026-09-15:",None),("current-2026","s","carbonation curing","2026-09-15:",None),("current-2026","s","silica fume","2026-10-01:",None),("current-2026","s","blast furnace slag","2026-10-15:",None),
("current-2026","s","blended cement","2026-10-01:",None),("current-2026","s","reinforced concrete beam","2026-11-01:",None),("current-2026","s","concrete test method","2026-10-01:",None),("current-2026","s","cement life cycle assessment","2026-10-15:",None),("current-2026","s","waste glass cement","2026-09-15:",None),
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
  if cur: f+=',to_publication_date:2026-11-19'
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
