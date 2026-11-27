"""pass-2026-11-21 listing (from pass-2026-11-19 listing.py): title screen with generic/bad regexes + per-topic relevance regex; caps per query-topic."""
import json,re,collections
h1=json.load(open('new-hits-c.json'))
gen=re.compile(r'cement|concrete|mortar|clinker|pozzol|geopolym|alkali.activ|shotcrete|grout|slag|silica fume|fly ash|Zement|Beton|ciment|béton|cemento|hormig|cimento|concreto|ettringit|calcined|metakaolin|calcestruzz|бетон|цемент|masonry|gunite|lime\b|limestone|plaster|pumice|rice husk|portlandite|alite|belite|calcium silicate hydrate|C-S-H|admixture|superplasticizer|aggregate|pavement|castable|refractor|betong|betón|beton|混凝土|水泥|セメント|コンクリート|bê tông|Bauwerk|Instandsetzung',re.I)
bad=re.compile(r'sediment|diagenes|calcite cement|carbonate cement|quartz|sandstone|reservoir|stratigraph|isotope|calcrete|cement(ed)? (zone|stone)|superhydrophobic|dental|tooth|teeth|bone cement|endodont|root canal|orthop|arthroplast|vertebro|glass ionomer|\bpulp|implant|surgical|clinical|patient|cancer|wastewater treatment|soil stabil|\bwell-being|bone|periodont|\bdrug|catalys|adsorption|dye removal|asphalt|bitumen|hot mix|platelet|protein|blood|aggregation of|aggregate demand|aggregate supply chain|macroeconomic|tumou?r|cell aggregat|amyloid|colloid aggregat',re.I)
TR={'standards':r'standard|specification|ASTM|EN 197|CSA|AASHTO|classification|norm|code|regulation|requirement|performance',
'dot':r'DOT|highway|transportation|department|agency|bridge|pavement|AASHTO|specification|state|road',
'carbon':r'carbon|CO2|CO\u2082|emission|life.cycle|LCA|embodied|environment|decarbon|clinker|sustainab|climate|energy',
'fresh':r'workab|setting|slump|bleed|rheolog|plastic|pump|false set|fresh|flow|consisten|viscos|yield stress',
'strength':r'strength|early.age|maturity|modulus|flexural|compressive|cube|cylinder|stiffness|hardening',
'durability':r'thaumasite|sulfate|sulphate|freez|frost|chloride|permeab|service life|ettringite|abrasion|durab|deterior|scaling|corrosion|acid',
'scm':r'ternary|blended|fly ash|slag|pozzol|supplementary|composite cement|replacement|SCM|silica fume|limestone',
'pavement':r'pavement|joint|slipform|dowel|curling|warping|JPCP|CRCP|road|slab',
'apps':r'precast|prestress|masonry|pipe|ready.mix|dam|marine|girder|bridge|block|tunnel|pile|tank',
'mix':r'water.cement|w/c|mix|proportion|packing|optimi|high.volume|cement content|aggregate|design',
'field':r'finishing|hot weather|cold weather|curing|quality|placement|construction|field|defect|site|practice|surface',
'supply':r'plant|market|supply|kiln|fuel|quarry|raw material|transport|production|industry|clinker|manufactur',
'intl':r'India|China|Chinese|Brazil|Africa|Japan|Australia|Middle East|Saudi|Indonesia|Turkey|Korea|Europe|national|country|international'}
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
CAP={'current-2026':400,'citation-chase':70,'citation-chase-fwd':30}
cap=collections.Counter(); keys=[]
with open('listing-c.txt','w') as f:
  for t,ns,nc,k,w in rows:
    lim=CAP.get(t,6 if t.startswith('lang-') else 8)
    if cap[t]>=lim: continue
    cap[t]+=1; i=len(keys); keys.append(k)
    ab='A' if w.get('abstract_inverted_index') else '-'
    pl=((w.get('primary_location') or {}).get('source') or {}).get('display_name') or ''
    f.write(f"{i}|{t}|{w.get('publication_year')}|{-nc}|{(w.get('type') or '')[:4]}|{ab}|{(w.get('language') or '')}|{w['title'][:120]}|{pl[:30]}|{'doi' if w.get('doi') else 'nodoi'}|{-ns if ns else ''}\n")
json.dump(keys,open('listing-keys-c.json','w'))
print(len(rows),len(keys),dict(cap))
