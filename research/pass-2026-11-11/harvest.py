"""pass-2026-11-11 harvest: OpenAlex searches (new queries, not repeating ledger history)."""
import json,urllib.request,urllib.parse,time,sys
Q={
# least-covered real-axis topics (historical backfill) -- (query, to_year or None, from_year or None)
"cross-supply-region":[("cement industry regional production capacity trade",None,None),("clinker import export cement market developing countries",None,None),("aggregate supply shortage sand mining concrete",None,None),("cement plant location kiln technology China India",None,None)],
"concrete-mass-rcc":[("roller compacted concrete dam lift joint permeability",None,None),("adiabatic temperature rise mass concrete low heat cement",":2010",None),("RCC dam thermal stress analysis",None,None),("roller compacted concrete pavement durability freeze thaw",None,None)],
"concrete-cellular":[("autoclaved aerated concrete tobermorite properties",None,None),("foamed concrete thermal conductivity density",None,None),("cellular concrete history Ytong autoclaved",":1995",None),("foam concrete fly ash compressive strength drying shrinkage",None,None)],
"concrete-heavyweight":[("barite concrete mechanical properties high temperature",None,None),("steel slag aggregate heavyweight concrete gamma",None,None),("concrete biological shield nuclear power plant aging irradiation",None,None)],
"cross-failure-repair":[("concrete structure collapse forensic investigation",None,None),("bridge deck deterioration chloride field survey",None,None),("parking structure deterioration repair case study",None,None),("high alumina cement concrete failure roof beams",":2000",None)],
"binder-specialty":[("shrinkage compensating concrete type K expansive cement",None,None),("rapid hardening cement repair early strength calcium sulfoaluminate belite",None,None),("expansive additive MgO CaO concrete restrained expansion",None,None)],
"binder-white-masonry":[("lime mortar natural hydraulic lime masonry restoration",None,None),("white cement concrete photocatalytic TiO2 self-cleaning",None,None),("Portland cement lime mortar bond masonry unit",None,None)],
"binder-international":[("CEM III blast furnace cement durability Europe",None,None),("Japanese cement JIS R 5210 portland",None,None),("composite cement CEM II/C CEM VI EN 197-5",None,None)],
"binder-well":[("oil well cement slurry gas migration additives",None,None),("CO2 resistant well cement carbonation sequestration",None,None)],
"scm-natural":[("pumice pozzolan concrete alkali silica reaction",None,None),("diatomaceous earth pozzolan cement",None,None)],
"concrete-shotcrete":[("sprayed concrete tunnel lining accelerator alkali-free",None,None),("shotcrete rebound early strength",None,None)],
# Type IL / PLC legacy collection topics
"pll-mix":[("portland limestone cement concrete mixture proportioning strength",None,None),("portland limestone cement scaling freeze thaw deicer",None,None),("portland limestone cement pavement",None,None),("portland limestone cement sulfate resistance thaumasite low temperature",None,None),("portland limestone cement chloride carbonation",None,None),("portland limestone cement Canada CSA A3000 GU",None,None)],
# current awareness
"current-2026":[("cement",None,"2026-09-01"),("concrete durability",None,"2026-09-01"),("supplementary cementitious material",None,"2026-09-01"),("limestone calcined clay",None,"2026-08-01"),("portland limestone cement",None,"2026-03-01"),("alkali activated",None,"2026-09-01"),("roller compacted concrete",None,"2026-01-01"),("foamed concrete",None,"2026-06-01"),("radiation shielding concrete",None,"2026-06-01"),("oil well cement",None,"2026-06-01")],
}
out={};log=[]
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def get(u):
  for i in range(4):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    except Exception as e:
      err=e; time.sleep(3*(i+1))
  raise err
SEL='id,doi,title,publication_year,publication_date,type,language,cited_by_count,authorships,primary_location,abstract_inverted_index,is_retracted,open_access,biblio'
for t,qs in Q.items():
  for q,to,fr in qs:
    ent={"topic":t,"query":q,"to":to,"from":fr,"n":0,"errors":[]}
    f='type:article|book-chapter|report|dissertation|book|review|standard'
    if to: f+=',to_publication_date:%s-12-31'%to[1:]
    if fr: f+=',from_publication_date:%s'%fr
    sort='relevance_score:desc' if fr else 'cited_by_count:desc'
    if t=='current-2026': f+=',to_publication_date:2026-11-11'
    try:
      u='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':q,'filter':f,'per-page':20 if t!='current-2026' else 25,'sort':sort,'select':SEL,'mailto':'research@example.org'})
      d=get(u)
      for w in d['results']:
        k=(w.get('doi') or w['id']).lower()
        if k in out: out[k]['queries'].append([t,q]); continue
        w['queries']=[[t,q]]; out[k]=w; ent['n']+=1
    except Exception as e: ent['errors'].append(str(e))
    log.append(ent); print(t,q,ent['n'],ent['errors'],flush=True); time.sleep(0.5)
json.dump(log,open('search-log.json','w'),indent=1); json.dump(out,open('api-hits.json','w'))
print(len(out))
