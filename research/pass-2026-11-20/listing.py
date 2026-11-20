"""pass-2026-11-20 listing (from pass-2026-11-19 listing.py): title screen with generic/bad regexes + per-topic relevance regex; caps per query-topic."""
import json,re,collections
h1=json.load(open('new-hits.json'))
gen=re.compile(r'cement|concrete|mortar|clinker|pozzol|geopolym|alkali.activ|shotcrete|grout|slag|silica fume|fly ash|Zement|Beton|ciment|béton|cemento|hormig|cimento|concreto|ettringit|calcined|metakaolin|calcestruzz|бетон|цемент|masonry|gunite|lime\b|limestone|plaster|pumice|rice husk|portlandite|alite|belite|calcium silicate hydrate|C-S-H|admixture|superplasticizer|aggregate|pavement|castable|refractor|betong|betón|beton|混凝土|水泥|セメント|コンクリート|bê tông|Bauwerk|Instandsetzung',re.I)
bad=re.compile(r'sediment|diagenes|calcite cement|carbonate cement|quartz|sandstone|reservoir|stratigraph|isotope|calcrete|cement(ed)? (zone|stone)|superhydrophobic|dental|tooth|teeth|bone cement|endodont|root canal|orthop|arthroplast|vertebro|glass ionomer|\bpulp|implant|surgical|clinical|patient|cancer|wastewater treatment|soil stabil|\bwell-being|bone|periodont|\bdrug|catalys|adsorption|dye removal|asphalt|bitumen|hot mix|platelet|protein|blood|aggregation of|aggregate demand|aggregate supply chain|macroeconomic|tumou?r|cell aggregat|amyloid|colloid aggregat',re.I)
TR={'cross-mix':r'admixture|grading|gradation|proportion|mix|fineness|paste|water.?reduc|plasticiz|air.?entrain|retard|aggregate',
'cross-chemistry':r'hydrat|silicate|portlandite|alite|belite|C3S|clinker|pore solution|phase|heat|calcium',
'cross-mechanics':r'strength|multiaxial|biaxial|triaxial|size effect|fatigue|stress|strain|shrinkage|creep|fracture|modulus|dynamic|impact',
'scm-limestone':r'limestone|calcareous|carbonat|carboaluminate|monocarbonate|dolomit|filler|CaCO3',
'binder-activated':r'alkali|geopolym|activat|waterglass|silicate',
'cross-durability':r'scaling|chloride|sewer|acid|leach|seawater|marine|alkali|carbonation|corrosion|frost|freez|sulfate|sulphate|durab',
'concrete-architectural':r'decorativ|surface|facade|façade|fib|colou?r|architect|exposed|textile|finish|void|aesthetic|panel|glass',
'concrete-scc':r'self.?compact|self.?consolidat|SCC|formwork|flowab|rheolog',
'concrete-polymer-refractory':r'epoxy|polyester|polymer|castable|refractor|sulfur|sulphur|resin|latex',
'concrete-circular':r'recycl|demolition|waste|C&D|carbonated|circular|reuse',
'concrete-pavement-pervious':r'pervious|porous|pavement|roller|airfield|runway|block paving|paver|whitetopping|road',
'concrete-repair-grout-overlay':r'overlay|repair|grout|microfine|injection|rehabilit|inhibitor|patch|strengthen|retrofit',
'concrete-precast-insitu-print':r'precast|hollow.?core|print|3D|additive|connection|spun|tilt|extru|prefab',
}
rows=[]
for k,w in h1.items():
  ti=w.get('title') or ''; t0,q0=w['queries'][0]
  if not gen.search(ti) or bad.search(ti) or w.get('is_retracted'): continue
  if w.get('type') in ('paratext','erratum','editorial','letter','retraction'): continue
  if not w.get('publication_year'): continue
  if t0 in TR and not re.search(TR[t0],ti,re.I): continue
  nseed=len(q0.split(',')) if t0=='citation-chase' else 0
  rows.append((t0,-nseed,-(w.get('cited_by_count') or 0),k,w))
rows.sort(key=lambda r:(r[0],r[1],r[2]))
CAP={'current-2026':30,'citation-chase':70,'citation-chase-fwd':30,'cross-tests-codes':8,'cross-chemistry':16,'cross-mix':16,'concrete-hpc':6}
cap=collections.Counter(); keys=[]
with open('listing.txt','w') as f:
  for t,ns,nc,k,w in rows:
    lim=CAP.get(t,6 if t.startswith('lang-') else 14)
    if cap[t]>=lim: continue
    cap[t]+=1; i=len(keys); keys.append(k)
    ab='A' if w.get('abstract_inverted_index') else '-'
    pl=((w.get('primary_location') or {}).get('source') or {}).get('display_name') or ''
    f.write(f"{i}|{t}|{w.get('publication_year')}|{-nc}|{(w.get('type') or '')[:4]}|{ab}|{(w.get('language') or '')}|{w['title'][:120]}|{pl[:30]}|{'doi' if w.get('doi') else 'nodoi'}|{-ns if ns else ''}\n")
json.dump(keys,open('listing-keys.json','w'))
print(len(rows),len(keys),dict(cap))
