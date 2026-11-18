"""Manual selection (Grok Bot, 2026-11-18) from listing.txt. Excluded on screening: soil-stabilisation/geotechnical, dental/biomedical cement, sedimentary-geology
cement, dam health-monitoring and seismic-fragility papers, structural-mechanics papers retrieved by generic 'failure' queries, adsorption/dye-removal with ashes,
non-concrete social-science/art 'concrete', ML-prediction papers in minor venues, duplicate titles, no-DOI items."""
import json
EX=set()
for a in [24,28,30,34,35,37,39,42,45,47, 50,51,57,61,62,63,66,68,69,71, 76,77,81,88,93, 97,108,105,115,205,247,
 275,78,299,300,302,305,306,307,310,312,314,317,318,319,320,321,322, 338,341,344, 350,364,370,
 372,374,375,376,377,378,379,380,383,384,385,386,387,388,389,390,391,393,394,
 397,398,400,401,405,407,408,411,418, 432,435,444,455,457,459,463,
 466,467,477,479,481,503,505,506,508,511,516,523,524,525,526,527,533,539,540,544,558,
 647,649,652,655,656,659,665]: EX.add(a)
keys=json.load(open('listing-keys.json')); h={'h1':json.load(open('new-hits.json')),'h2':json.load(open('new-hits2.json'))}
sel={};nodoi=[]
for i,(src,k) in enumerate(keys):
  if i in EX: continue
  w=dict(h[src][k]); w['_src']=src; w['_idx']=i; w.pop('referenced_works',None)
  if not w.get('doi'): nodoi.append((i,w['title'][:80])); continue
  sel[k]=w
json.dump(sel,open('selected.json','w'))
print(len(keys),len(EX),len(sel),'nodoi dropped',nodoi)
