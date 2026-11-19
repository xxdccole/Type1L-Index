"""Manual selection (Grok Bot, 2026-11-19) from listing.txt. Excluded on screening: dental/resin cements, zeolite synthesis/NMR, soil stabilisation/subgrade/
earth bricks/soil-cement piles, mine backfill, asphalt, seismic code/fragility building analyses, sociology/politics/history uses of 'cement'/'beton', a bare journal-title
record, a reproducibility-survey paper and an image-processing paper; no-DOI items go to probe_nodoi.py."""
import json
EX={21,34,43,99,161,169,303,313,338,350,355,356,361,365,367,376,379,384,400,401,431,434,436,438,440,451,453,454,456,465,483,486,487,490,494,496,559,610}
keys=json.load(open('listing-keys.json')); h={'h1':json.load(open('new-hits.json')),'h2':json.load(open('new-hits2.json'))}
sel={};nodoi=[]
for i,(src,k) in enumerate(keys):
  if i in EX: continue
  w=dict(h[src][k]); w['_src']=src; w['_idx']=i; w.pop('referenced_works',None)
  if not w.get('doi'): nodoi.append((i,w['title'][:80])); continue
  sel[k]=w
json.dump(sel,open('selected.json','w'))
print(len(keys),len(EX),len(sel),'nodoi dropped',nodoi)
