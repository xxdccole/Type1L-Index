import json,re,collections,subprocess
subprocess.run(['python3','dedupe.py','api-hits2.json','new-hits2.json','dedupe-dup2.json'])
h1=json.load(open('new-hits.json')); h2=json.load(open('new-hits2.json'))
# cross-dedupe h2 vs h1
h2={k:w for k,w in h2.items() if k not in h1}
gen=re.compile(r'cement|concrete|mortar|clinker|pozzol|geopolym|alkali.activ|shotcrete|grout|slag|silica fume|fly ash|Zement|Beton|ciment|béton|cemento|hormig|cimento|concreto|ettringit|calcined|metakaolin|calcestruzz|бетон|цемент|masonry|gunite|sprayed|lime\b|plaster|stucco|pumice|rice husk|zeolite|\bdams?\b|\bwell\b|betong|betón|beton|مل|混凝土|セメント|コンクリート|bê tông',re.I)
bad=re.compile(r'sediment|diagenes|calcite cement|carbonate cement|quartz|sandstone|Mississippian|reservoir|stratigraph|isotope|calcrete|cement(ed)? (zone|stone)|spray(ing)? (tests?|coat|dry)|superhydrophobic|photocatalytic|dental|tooth|teeth|bone cement|endodont|root canal|orthop|arthroplast|vertebro|glass ionomer|\bpulp|implant|surgical|clinical|patient|cancer|wastewater|soil stabil|\bwell-being|as well as|well[- ]known|as well\b|bone|periodont|\bdrug|polymer(ic)? (nano|membrane)|zeolite (membrane|catalyst)|catalys|adsorption|dye removal',re.I)
TR={
'concrete-mass-rcc':r'mass concrete|roller|\bRCC\b|\bdams?\b|thermal|hydration heat|heat of hydration|cooling|temperature (rise|field|control)|cemented|massive|early[- ]age crack|delayed ettring',
'concrete-heavyweight':r'heavy|shield|barite|baryte|magnetite|radiation|neutron|gamma|nuclear|high[- ]density|hematite|serpentine|radioactive|x-?ray',
'concrete-cellular':r'foam|aerat|cellular|\bAAC\b|autoclav|tobermorite|porous concrete|air[- ]entrain',
'binder-specialty':r'expansive|shrinkage[- ]compens|rapid[- ]harden|aluminate|ultrafine|quick|supersulf|sorel|oxychloride|sulfoaluminate|special cement|regulated|ye.elimite|belite|dental|oxysulfate|phosphate cement|magnesium phosphate|geopolymer cement|sulphoaluminate',
'concrete-shotcrete':r'shotcrete|sprayed|gunite|rebound|tunnel|spray',
'binder-white-masonry':r'masonry|white|lime|historic|roman|ancient|plaster|stucco|pointing|brick|heritage|restoration|render|hydraulic',
'binder-well':r'\bwell|oil|borehole|geothermal|slurry|\bAPI\b|cementing|zonal|wellbore|casing|downhole|sheath|retarder|abandon',
'binder-international':r'india|africa|brazil|japan|china|chinese|australia|mexic|indonesia|nigeria|pakistan|vietnam|turkey|egypt|russia|korea|standard|EN ?197|country|national|region|saudi|iran|europe|kenya|ethiopia|bangladesh|thailand|malaysia',
'scm-natural':r'pozzolan|volcanic|pumice|rice husk|zeolite|diatom|trass|bagasse|palm oil|\bash\b|biomass|agricultur|natural|husk|straw|sawdust|bamboo|corn|cob|shell',
'scm-clay':r'metakaolin|calcined|kaolin|clay|LC3|limestone calcined|thermal activ|brick powder|illite|dehydroxyl',
'cross-supply-region':r'market|plant|industry|demand|supply|production|kiln|fuel|trade|import|export|logistic|price|capacity|alternative fuel|co-?process|energy',
'cross-failure-repair':r'failure|collaps|forensic|deteriorat|distress|damage|investigat|case|petrograph|defect|diagnos|lesson|accident|crack',
'cross-construction':r'plac|pump|formwork|weather|curing|finish|compaction|vibrat|workability|consolidat|transport|hot|cold|screed|slump|construction',
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
