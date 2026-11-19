import json,re,collections,subprocess
subprocess.run(['python3','dedupe.py','api-hits2.json','new-hits2.json','dedupe-dup2.json'])
h1=json.load(open('new-hits.json')); h2=json.load(open('new-hits2.json'))
# cross-dedupe h2 vs h1
h2={k:w for k,w in h2.items() if k not in h1}
gen=re.compile(r'cement|concrete|mortar|clinker|pozzol|geopolym|alkali.activ|shotcrete|grout|slag|silica fume|fly ash|Zement|Beton|ciment|béton|cemento|hormig|cimento|concreto|ettringit|calcined|metakaolin|calcestruzz|бетон|цемент|masonry|gunite|sprayed|lime\b|plaster|stucco|pumice|rice husk|zeolite|\bdams?\b|\bwell\b|betong|betón|beton|مل|混凝土|セメント|コンクリート|bê tông',re.I)
bad=re.compile(r'sediment|diagenes|calcite cement|carbonate cement|quartz|sandstone|Mississippian|reservoir|stratigraph|isotope|calcrete|cement(ed)? (zone|stone)|spray(ing)? (tests?|coat|dry)|superhydrophobic|photocatalytic|dental|tooth|teeth|bone cement|endodont|root canal|orthop|arthroplast|vertebro|glass ionomer|\bpulp|implant|surgical|clinical|patient|cancer|wastewater|soil stabil|\bwell-being|as well as|well[- ]known|as well\b|bone|periodont|\bdrug|polymer(ic)? (nano|membrane)|zeolite (membrane|catalyst)|catalys|adsorption|dye removal',re.I)
TR={
'concrete-lightweight':r'lightweight|light-weight|expanded|perlite|scoria|pumice|palm shell|polystyrene|\bEPS\b|cenosphere|no-fines|pervious|vermiculite|aggregate|low[- ]density|insulat',
'binder-cac-csa':r'alumina|aluminous|aluminate|ye.?elimite|sulfoaluminate|sulphoaluminate|\bCSA\b|\bCAC\b|ettringite|belite|fondu|conversion',
'binder-lc3':r'calcined|LC3|LC 3|limestone|metakaolin|kaolin|clay|ternary',
'binder-magnesium-carbonatable':r'magnesi|MgO|oxysulf|oxychlor|phosphate|struvite|carbonat|CO2|CO 2|wollastonite|dicalcium|calcium silicate|sorel',
'scm-silica':r'silica|microsilica|nano.?SiO|SiO2|fume',
'scm-slag':r'slag|GGBS|GGBFS|blast',
'scm-emerging':r'slag|glass|gangue|phosphogypsum|ceramic|recycled|biochar|sludge|marble|eggshell|waste|tailing|ash|powder|by-product|byproduct|red mud',
'binder-blended':r'blend|ternary|pozzolan|composite|multi|fly ash|slag|limestone|hydration|cement',
'concrete-structural':r'beam|prestress|punching|slab|column|confine|bond|creep|precast|post-tension|wall|reinforced|shear|girder|structural|flexur',
'cross-tests-codes':r'test|rebound|core|migration|permeab|freez|Eurocode|ACI|code|slump|specimen|accept|standard|specification|method|report|investigation|laboratory|durability',
'cross-environment-cost':r'CO2|CO 2|carbon|clinker|environment|EPD|footprint|uptake|decarbon|emission|heat recovery|recycl|cost|life.?cycle|LCA|sustainab|energy',
}
rows=[]
for src,h in (('h1',h1),('h2',h2)):
  for k,w in h.items():
    ti=w.get('title') or ''; t0=w['queries'][0][0]
    if not gen.search(ti) or bad.search(ti) or w.get('is_retracted'): continue
    if w.get('type') in ('paratext','erratum','editorial','letter'): continue
    if not w.get('publication_year'): continue
    if t0 in TR and not re.search(TR[t0],ti,re.I): continue
    rows.append((t0,w['queries'][0][1],-(w.get('cited_by_count') or 0),src,k,w))
rows.sort(key=lambda r:(r[0],r[2]))
CAP={'current-2026':45,'citation-chase':110,'citation-chase-fwd':45}
cap=collections.Counter(); keys=[]
with open('listing.txt','w') as f:
  for t,q,nc,src,k,w in rows:
    lim=CAP.get(t, 7 if t.startswith(('lang-','pll-')) else 24)
    if cap[t]>=lim: continue
    cap[t]+=1; i=len(keys); keys.append([src,k])
    ab='A' if w.get('abstract_inverted_index') else '-'
    pl=((w.get('primary_location') or {}).get('source') or {}).get('display_name') or ''
    f.write(f"{i}|{t}|{w.get('publication_year')}|{-nc}|{w.get('type')[:4]}|{ab}|{(w.get('language') or '')}|{w['title'][:115]}|{pl[:30]}|{'doi' if w.get('doi') else 'nodoi'}\n")
json.dump(keys,open('listing-keys.json','w'))
print(len(rows),len(keys),dict(cap))
