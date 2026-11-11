"""pass-2026-11-11 harvest 2: OpenAlex title.search (precise) historical backfill for least-covered topics; periods split to surface older work."""
import json,urllib.request,urllib.parse,time
Q=[
("concrete-cellular","autoclaved aerated concrete",":1999"),("concrete-cellular","autoclaved aerated concrete","2000:2015"),
("concrete-cellular","foamed concrete",None),("concrete-cellular","foam concrete",":2012"),("concrete-cellular","cellular concrete",None),
("concrete-heavyweight","shielding concrete",None),("concrete-heavyweight","heavyweight concrete",None),("concrete-heavyweight","barite concrete",None),("concrete-heavyweight","irradiated concrete",None),("concrete-heavyweight","high-density concrete",None),
("concrete-mass-rcc","roller compacted concrete",":2005"),("concrete-mass-rcc","roller-compacted concrete","2006:2020"),("concrete-mass-rcc","mass concrete",":2000"),("concrete-mass-rcc","mass concrete","2001:2018"),("concrete-mass-rcc","RCC dam",None),
("cross-failure-repair","concrete deterioration case study",None),("cross-failure-repair","collapse reinforced concrete",None),("cross-failure-repair","concrete bridge deterioration",":2005"),("cross-failure-repair","failure analysis concrete",None),("cross-failure-repair","high alumina cement",":1995"),
("binder-specialty","expansive cement",":2000"),("binder-specialty","shrinkage-compensating",None),("binder-specialty","expansive agent concrete",None),("binder-specialty","rapid hardening cement",None),
("binder-white-masonry","masonry cement",None),("binder-white-masonry","white cement",None),("binder-white-masonry","hydraulic lime mortar",None),("binder-white-masonry","cement-lime mortar",None),("binder-white-masonry","portland cement plaster",None),
("binder-international","blast furnace cement",None),("binder-international","composite cement",None),("binder-international","CEM II",None),("binder-international","CEM III",None),
("binder-well","oil well cement",":2005"),("binder-well","well cement","2006:2020"),("binder-well","geothermal cement",None),
("concrete-shotcrete","shotcrete",":2000"),("concrete-shotcrete","sprayed concrete",None),
("scm-natural","natural pozzolan",":2005"),("scm-natural","pumice cement",None),("scm-natural","volcanic ash cement",None),
("cross-supply-region","cement industry",":2005"),("cross-supply-region","cement industry","2006:2020"),("cross-supply-region","cement production",None),("cross-supply-region","aggregate resources",None),("cross-supply-region","sand mining",None),
("scm-limestone","limestone filler",":2008"),("scm-limestone","limestone powder concrete",None),
("concrete-heavyweight","radiation shielding concrete",None),
("pll-mix","portland-limestone cement",None),("pll-mix","limestone cement",":2010"),("pll-mix","portland limestone cement concrete",None),
]
out={};log=[]
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def get(u):
  for i in range(4):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    except Exception as e: err=e; time.sleep(3*(i+1))
  raise err
SEL='id,doi,title,publication_year,publication_date,type,language,cited_by_count,authorships,primary_location,abstract_inverted_index,is_retracted,open_access,biblio'
for t,q,per in Q:
  ent={"topic":t,"titleSearch":q,"period":per,"n":0,"errors":[]}
  f='title.search:%s,type:article|book-chapter|report|dissertation|book|review|standard'%q
  if per:
    a,b=per.split(':')
    if a: f+=',from_publication_date:%s-01-01'%a
    if b: f+=',to_publication_date:%s-12-31'%b
  try:
    d=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':f,'per-page':25,'sort':'cited_by_count:desc','select':SEL,'mailto':'research@example.org'}))
    for w in d['results']:
      k=(w.get('doi') or w['id']).lower()
      if k in out: out[k]['queries'].append([t,q]); continue
      w['queries']=[[t,q]]; out[k]=w; ent['n']+=1
  except Exception as e: ent['errors'].append(str(e))
  log.append(ent); print(t,q,per,ent['n'],ent['errors'],flush=True); time.sleep(0.4)
json.dump(log,open('search-log2.json','w'),indent=1); json.dump(out,open('api-hits2.json','w'))
print(len(out))
