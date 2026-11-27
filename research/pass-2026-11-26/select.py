"""Manual selection (Grok Bot, 2026-11-26) from listing.txt (main harvest, idx 0-314) and listing-b.txt (supplementary language sweep, idx 400+j).
Excluded on screening (EX): 177 lateritic 'earth concrete' (soil stabilisation, as lateritic soil-cement excluded before); 181 steel-plate composite walls and
95 concrete-encased steel composite columns (steel-concrete composite, excluded as before); 188 dentin/resin dental cements; 191 bioceramic medical cement;
192 econometric production-function study of one cement plant (single-firm economics, excluded as before);
445 SMA asphalt-concrete pavement and 447 EME asphalt-concrete (asphalt, not cement concrete); 449 news notice of a US PICP webinar (not a source).
No-DOI items go to probe_nodoi.py."""
import json
EX={177,181,95,188,191,192,445,447,449}
keys=json.load(open('listing-keys.json')); kb=json.load(open('listing-b-keys.json'))
h=json.load(open('new-hits.json')); h.update(json.load(open('new-hits-b.json'))); json.dump(h,open('all-hits.json','w'))
idx=[(i,k) for i,k in enumerate(keys)]+[(400+j,k) for j,k in enumerate(kb)]
sel={};nodoi=[]
for i,k in idx:
  if i in EX: continue
  w=dict(h[k]); w['_idx']=i; w.pop('referenced_works',None)
  if not w.get('doi'): nodoi.append(i); continue
  sel[k]=w
json.dump(sel,open('selected.json','w')); json.dump(nodoi,open('nodoi-idx.json','w'))
print(len(idx),len(EX),len(sel),'nodoi',len(nodoi))
