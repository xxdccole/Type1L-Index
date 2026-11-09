import json,urllib.request,urllib.parse,time,sys
Q={
"concrete-heavyweight":[("radiation shielding concrete magnetite barite gamma attenuation",None),("heavyweight concrete high-density aggregate nuclear",":1999"),("ilmenite hematite aggregate neutron shielding concrete serpentine",None)],
"binder-portland":[("tricalcium aluminate sulfate resistance Type V portland cement",":1995"),("air-entraining portland cement history Type IA freeze thaw",":1990"),("Bogue calculation clinker phase composition portland cement",None)],
"binder-white-masonry":[("white portland cement clinker iron content whiteness",None),("masonry cement mortar air content bond strength ASTM C91",None),("plastic cement stucco portland cement plaster",None)],
"concrete-fibers":[("steel fiber reinforced concrete flexural toughness residual strength",":2000"),("synthetic macro fiber concrete slab on ground",None),("glass fiber reinforced concrete GFRC durability aging",None)],
"concrete-mass-rcc":[("roller compacted concrete dam construction history",":1995"),("roller-compacted concrete pavement mixture design compaction",None),("mass concrete temperature differential cracking dam cooling pipes",":1990")],
"concrete-polymer-refractory":[("polymer modified mortar latex styrene butadiene bridge deck overlay",None),("polymer concrete epoxy resin mechanical properties",":2000"),("refractory castable calcium aluminate cement high temperature",None)],
"concrete-scc":[("self-compacting concrete Okamura development",":2005"),("self-consolidating concrete static stability segregation formwork pressure",None),("self-consolidating concrete precast prestressed bond",None)],
"scm-flyash":[("fly ash concrete Class F Class C alkali silica reaction mitigation",None),("harvested reclaimed landfilled fly ash concrete",None),("fly ash concrete early research Davis Berkeley",":1960")],
"scm-limestone":[("limestone filler cement hydration carboaluminate",None),("limestone powder self-compacting concrete filler effect",None),("thaumasite sulfate attack limestone filler cement",None)],
"scm-natural":[("natural pozzolan concrete volcanic ash pumice ASTM C618 Class N",None),("Roman concrete pozzolana durability",None),("zeolite natural pozzolan cement strength",None)],
"binder-international":[("EN 197-1 cement types CEM II composite durability",None),("Chinese cement standard GB 175 common portland cement",None),("Indian portland pozzolana cement IS 1489",None)],
"concrete-architectural":[("architectural concrete surface quality bugholes formwork",None),("exposed aggregate concrete decorative surface finish",None),("colored concrete pigments efflorescence",None)],
"current-2026":[("cement concrete 2026",None)],
}
out={};log=[]
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def get(u):
    r=urllib.request.Request(u,headers=UA)
    return json.load(urllib.request.urlopen(r,timeout=40))
for t,qs in Q.items():
  for q,dr in qs:
    ent={"topic":t,"query":q,"dateFilter":dr,"openalex":0,"crossref":0,"errors":[]}
    try:
      f='type:article|book-chapter|report|dissertation|book'
      if dr: f+=',to_publication_date:%s-12-31'%dr[1:]
      if t=='current-2026': f='from_publication_date:2026-01-01'
      u='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':q,'filter':f,'per-page':15,'sort':'relevance_score:desc','mailto':'research@example.org'})
      d=get(u)
      for w in d['results']:
        k=(w.get('doi') or w['id']).lower()
        out.setdefault(k,{"src":"openalex","topic":t,"query":q,"title":w.get('title'),"year":w.get('publication_year'),"doi":w.get('doi'),"oa":w.get('open_access',{}).get('oa_url'),"isOA":w.get('open_access',{}).get('is_oa'),"cited":w.get('cited_by_count'),"type":w.get('type'),"venue":((w.get('primary_location') or {}).get('source') or {}).get('display_name'),"authors":[a['author']['display_name'] for a in w.get('authorships',[])][:8],"id":w['id']})
        ent['openalex']+=1
    except Exception as e: ent['errors'].append('openalex:'+str(e))
    time.sleep(1.2)
    try:
      p={'query.bibliographic':q,'rows':10,'select':'DOI,title,author,issued,type,container-title,publisher,is-referenced-by-count'}
      if dr: p['filter']='until-pub-date:%s'%dr[1:]
      d=get('https://api.crossref.org/works?'+urllib.parse.urlencode(p)+'&mailto=research@example.org')
      for w in d['message']['items']:
        k=('https://doi.org/'+w['DOI']).lower()
        out.setdefault(k,{"src":"crossref","topic":t,"query":q,"title":(w.get('title') or [''])[0],"year":(w.get('issued',{}).get('date-parts') or [[None]])[0][0],"doi":'https://doi.org/'+w['DOI'],"cited":w.get('is-referenced-by-count'),"type":w.get('type'),"venue":(w.get('container-title') or [''])[0],"publisher":w.get('publisher'),"authors":[(a.get('given','')+' '+a.get('family','')).strip() for a in w.get('author',[])][:8]})
        ent['crossref']+=1
    except Exception as e: ent['errors'].append('crossref:'+str(e))
    log.append(ent);print(t,q,ent['openalex'],ent['crossref'],ent['errors'],flush=True)
    time.sleep(1)
json.dump(log,open('search-log.json','w'),indent=1);json.dump(out,open('api-hits.json','w'),indent=1)
print(len(out))
