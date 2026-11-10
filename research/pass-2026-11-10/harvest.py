import json,urllib.request,urllib.parse,time,sys
Q={
"binder-blended":[("portland-pozzolan cement Type IP blended cement performance",":1995"),("portland blast-furnace slag cement Type IS history",":1990"),("ternary blended cement concrete performance review",None)],
"scm-clay":[("metakaolin pozzolanic reactivity concrete",":2005"),("calcined clay kaolinite content reactivity R3 test",None),("calcined clay pozzolan history Brazil India surkhi",":1990")],
"concrete-structural":[("reinforced concrete history Hennebique Ransome",None),("shear strength reinforced concrete beams without stirrups size effect",":2000"),("prestressed concrete creep shrinkage loss bridge girders",":1995")],
"concrete-hpc":[("high-performance concrete definition silica fume durability",":2000"),("high-strength concrete mechanical properties state of the art",":1995"),("ultra-high performance concrete reactive powder concrete Richard Cheyrezy",":2000")],
"concrete-pavement-pervious":[("pervious concrete porosity permeability strength",None),("jointed plain concrete pavement performance history AASHO road test",":1990"),("continuously reinforced concrete pavement performance",None)],
"concrete-precast-insitu-print":[("3D printing concrete extrusion buildability interlayer bond",None),("precast concrete steam curing delayed ettringite",":2005"),("digital fabrication concrete review",None)],
"concrete-circular":[("recycled concrete aggregate mechanical properties review",None),("recycled aggregate concrete early research",":1990"),("concrete carbonation CO2 uptake recycled aggregate mineralization",None)],
"concrete-repair-grout-overlay":[("concrete repair compatibility patch durability",":2005"),("bonded concrete overlay bridge deck latex silica fume",None),("post-tensioning grout voids tendon corrosion",None)],
"cross-chemistry":[("cement hydration mechanisms review C-S-H",None),("ettringite formation sulfate hydration cement early",":1980"),("thermodynamic modelling cement hydrates GEMS",None)],
"cross-mix":[("concrete mix design proportioning Abrams water-cement ratio law",":1960"),("particle packing aggregate gradation optimization concrete",None),("superplasticizer polycarboxylate dispersion mechanism",None)],
"cross-construction":[("concrete curing methods evaporation hot weather",None),("concrete consolidation vibration",":1990"),("formwork stripping early-age strength maturity in-place",None)],
"cross-mechanics":[("concrete creep shrinkage model B3 Bazant",None),("fracture mechanics concrete fictitious crack model Hillerborg",":1990"),("concrete modulus of elasticity compressive strength relation",None)],
"current-2026":[("calcined clay cement 2026",None),("recycled concrete aggregate 2026",None),("3D printed concrete 2026",None),("ultra-high performance concrete bridge 2026",None),("pervious concrete 2026",None)],
}
out={};log=[]
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40))
for t,qs in Q.items():
  for q,dr in qs:
    ent={"topic":t,"query":q,"dateFilter":dr,"openalex":0,"crossref":0,"errors":[]}
    try:
      f='type:article|book-chapter|report|dissertation|book'
      if dr: f+=',to_publication_date:%s-12-31'%dr[1:]
      if t=='current-2026': f+=',from_publication_date:2026-01-01'
      u='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':q.replace(' 2026',''),'filter':f,'per-page':15,'sort':'cited_by_count:desc' if t!='current-2026' else 'relevance_score:desc','mailto':'research@example.org'})
      d=get(u)
      for w in d['results']:
        k=(w.get('doi') or w['id']).lower()
        out.setdefault(k,{"src":"openalex","topic":t,"query":q,"title":w.get('title'),"year":w.get('publication_year'),"date":w.get('publication_date'),"doi":w.get('doi'),"oa":w.get('open_access',{}).get('oa_url'),"isOA":w.get('open_access',{}).get('is_oa'),"cited":w.get('cited_by_count'),"type":w.get('type'),"venue":((w.get('primary_location') or {}).get('source') or {}).get('display_name'),"authors":[a['author']['display_name'] for a in w.get('authorships',[])][:10],"id":w['id']})
        ent['openalex']+=1
    except Exception as e: ent['errors'].append('openalex:'+str(e))
    time.sleep(1)
    try:
      p={'query.bibliographic':q.replace(' 2026',''),'rows':8,'select':'DOI,title,author,issued,type,container-title,publisher,is-referenced-by-count'}
      if dr: p['filter']='until-pub-date:%s'%dr[1:]
      if t=='current-2026': p['filter']='from-pub-date:2026-01-01'
      d=get('https://api.crossref.org/works?'+urllib.parse.urlencode(p)+'&mailto=research@example.org')
      for w in d['message']['items']:
        k=('https://doi.org/'+w['DOI']).lower()
        out.setdefault(k,{"src":"crossref","topic":t,"query":q,"title":(w.get('title') or [''])[0],"year":(w.get('issued',{}).get('date-parts') or [[None]])[0][0],"doi":'https://doi.org/'+w['DOI'],"cited":w.get('is-referenced-by-count'),"type":w.get('type'),"venue":(w.get('container-title') or [''])[0],"publisher":w.get('publisher'),"authors":[(a.get('given','')+' '+a.get('family','')).strip() for a in w.get('author',[])][:10]})
        ent['crossref']+=1
    except Exception as e: ent['errors'].append('crossref:'+str(e))
    log.append(ent);print(t,q,ent['openalex'],ent['crossref'],ent['errors'],flush=True)
    time.sleep(1)
json.dump(log,open('search-log.json','w'),indent=1);json.dump(out,open('api-hits.json','w'),indent=1)
print(len(out))
