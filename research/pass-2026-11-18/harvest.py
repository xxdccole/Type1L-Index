"""pass-2026-11-18 harvest: OpenAlex title.search/search backfill for next rotation head (concrete-mass-rcc, concrete-heavyweight, concrete-cellular,
binder-specialty, concrete-shotcrete, binder-white-masonry, binder-well, binder-international, scm-natural, scm-clay, cross-supply-region, cross-failure-repair,
cross-construction) + Type IL legacy topics + languages + current awareness 2026-11-12..11-18."""
import json,urllib.request,urllib.parse,time,sys
Q=[
("concrete-mass-rcc","t","roller-compacted concrete",":2000",None),("concrete-mass-rcc","t","roller compacted concrete","2001:2026",None),("concrete-mass-rcc","t","mass concrete",":1990",None),("concrete-mass-rcc","t","mass concrete","1991:2026",None),
("concrete-mass-rcc","t","concrete dam",None,None),("concrete-mass-rcc","t","thermal cracking massive concrete",None,None),("concrete-mass-rcc","t","pipe cooling concrete",None,None),("concrete-mass-rcc","t","hydration heat temperature rise concrete",None,None),
("concrete-mass-rcc","t","cemented material dam",None,None),("concrete-mass-rcc","t","delayed ettringite formation",None,None),
("concrete-heavyweight","t","heavyweight concrete",None,None),("concrete-heavyweight","t","radiation shielding concrete",None,None),("concrete-heavyweight","t","barite concrete",None,None),("concrete-heavyweight","t","magnetite concrete",None,None),
("concrete-heavyweight","t","neutron shielding concrete",None,None),("concrete-heavyweight","t","nuclear concrete",None,None),("concrete-heavyweight","t","high density concrete",None,None),("concrete-heavyweight","t","gamma ray attenuation concrete",None,None),
("concrete-cellular","t","foamed concrete",None,None),("concrete-cellular","t","aerated concrete",None,None),("concrete-cellular","t","autoclaved aerated concrete",None,None),("concrete-cellular","t","cellular concrete",None,None),
("concrete-cellular","t","lightweight foamed concrete",None,None),("concrete-cellular","t","tobermorite autoclaved",None,None),("concrete-cellular","t","foam stability cement paste",None,None),
("binder-specialty","t","expansive cement",None,None),("binder-specialty","t","shrinkage compensating concrete",None,None),("binder-specialty","t","rapid hardening cement",None,None),("binder-specialty","t","calcium aluminate cement",":2000",None),
("binder-specialty","t","ultrafine cement",None,None),("binder-specialty","t","quick setting cement",None,None),("binder-specialty","t","supersulfated cement",None,None),("binder-specialty","t","dental cement",None,None),("binder-specialty","t","sorel cement",None,None),
("concrete-shotcrete","t","shotcrete",":1995",None),("concrete-shotcrete","t","shotcrete","1996:2012",None),("concrete-shotcrete","t","sprayed concrete",None,None),("concrete-shotcrete","t","accelerator shotcrete",None,None),
("concrete-shotcrete","t","tunnel lining shotcrete",None,None),("concrete-shotcrete","t","wet-mix shotcrete rebound",None,None),("concrete-shotcrete","t","dry-mix shotcrete",None,None),("concrete-shotcrete","t","gunite",None,None),
("binder-white-masonry","t","masonry cement",None,None),("binder-white-masonry","t","white portland cement",None,None),("binder-white-masonry","t","lime mortar",None,None),("binder-white-masonry","t","historic mortar",None,None),
("binder-white-masonry","t","masonry mortar",None,None),("binder-white-masonry","t","hydraulic lime",None,None),("binder-white-masonry","t","stucco plaster cement",None,None),("binder-white-masonry","t","Roman concrete",None,None),
("binder-well","t","oil well cement",None,None),("binder-well","t","well cementing",None,None),("binder-well","t","cement slurry",None,None),("binder-well","t","geothermal well cement",None,None),("binder-well","t","API Class G cement",None,None),
("binder-well","t","well cement carbon storage CO2",None,None),("binder-well","t","zonal isolation cement sheath",None,None),("binder-well","t","retarder cement oilwell",None,None),
("binder-international","t","cement standard comparison EN 197",None,None),("binder-international","t","cement India",None,None),("binder-international","t","cement Africa",None,None),("binder-international","t","cement Brazil",None,None),
("binder-international","t","cement Japan",None,None),("binder-international","t","cement industry China",None,None),("binder-international","t","cement Australia",None,None),("binder-international","t","cement Mexico",None,None),
("scm-natural","t","natural pozzolan",None,None),("scm-natural","t","volcanic ash cement",None,None),("scm-natural","t","pumice concrete",None,None),("scm-natural","t","rice husk ash",None,None),("scm-natural","t","zeolite cement",None,None),
("scm-natural","t","diatomite cement",None,None),("scm-natural","t","trass",None,None),("scm-natural","t","bagasse ash",None,None),("scm-natural","t","palm oil fuel ash",None,None),
("scm-clay","t","metakaolin",":2008",None),("scm-clay","t","metakaolin","2009:2026",None),("scm-clay","t","calcined clay",None,None),("scm-clay","t","calcined clay cement durability",None,None),("scm-clay","t","kaolinite thermal activation",None,None),("scm-clay","t","burnt clay pozzolan",None,None),
("cross-supply-region","s","cement supply shortage regional market",None,None),("cross-supply-region","t","cement market",None,None),("cross-supply-region","t","cement plant fuel alternative",None,None),("cross-supply-region","t","cement demand",None,None),("cross-supply-region","t","cement transport logistics",None,None),
("cross-failure-repair","t","concrete failure investigation",None,None),("cross-failure-repair","t","structural collapse concrete",None,None),("cross-failure-repair","t","forensic concrete",None,None),("cross-failure-repair","t","concrete deterioration case study",None,None),("cross-failure-repair","t","petrography concrete distress",None,None),
("cross-construction","t","concrete placing",None,None),("cross-construction","t","concrete pumping",None,None),("cross-construction","t","formwork pressure concrete",None,None),("cross-construction","t","hot weather concreting",None,None),("cross-construction","t","cold weather concreting",None,None),("cross-construction","t","concrete curing",":2000",None),("cross-construction","t","concrete finishing",None,None),
# Type IL legacy
("pll-strength","s","portland limestone cement compressive strength early age",None,None),("pll-durability","s","portland limestone cement sulfate resistance thaumasite",None,None),("pll-fresh","s","portland limestone cement setting time workability",None,None),
("pll-pavement","s","limestone cement concrete pavement scaling deicer",None,None),("pll-standards","s","Type IL cement ASTM C595 AASHTO M240",None,None),("pll-dot","s","state DOT portland limestone cement specification",None,None),("pll-carbon","s","portland limestone cement CO2 reduction life cycle",None,None),
("pll-micro","s","limestone calcium carboaluminate hydration",None,None),
# languages
("lang-pt","t","concreto",None,"pt"),("lang-pt","t","cimento",None,"pt"),("lang-es","t","hormigón",None,"es"),("lang-es","t","cemento",None,"es"),("lang-fr","t","béton",None,"fr"),("lang-fr","t","ciment",None,"fr"),
("lang-de","t","Beton",None,"de"),("lang-zh","s","cement concrete",None,"zh"),("lang-ja","s","cement",None,"ja"),("lang-id","t","beton",None,"id"),("lang-vi","s","concrete",None,"vi"),("lang-uk","t","бетон",None,"uk"),("lang-ar","s","concrete",None,"ar"),("lang-fa","s","concrete",None,"fa"),
("lang-sv","t","betong",None,"sv"),("lang-sk","t","betón",None,"sk"),("lang-hr","t","beton",None,"hr"),("lang-ro","t","beton",None,"ro"),("lang-hu","t","beton",None,"hu"),
# current awareness
("current-2026","s","cement","2026-11-10:",None),("current-2026","s","concrete","2026-11-10:",None),("current-2026","s","shotcrete","2026-09-01:",None),("current-2026","s","foamed concrete","2026-09-01:",None),
("current-2026","s","calcined clay cement","2026-10-15:",None),("current-2026","s","mass concrete","2026-09-01:",None),("current-2026","s","oil well cement","2026-08-01:",None),("current-2026","s","natural pozzolan","2026-09-01:",None),
("current-2026","s","masonry mortar","2026-09-01:",None),("current-2026","s","radiation shielding concrete","2026-08-01:",None),
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
  if cur: f+=',to_publication_date:2026-11-18'
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
