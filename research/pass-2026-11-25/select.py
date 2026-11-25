"""Manual selection (Grok Bot, 2026-11-23) from listing.txt. Excluded on screening (EX): 16 bare journal-title record; 55 book-notice item; 128 mathematics-education book; 265 financial-performance study of listed cement/concrete firms; 201 demand-forecasting/inventory study for one cement company; 85/96/98 concrete-filled steel tube columns (steel-concrete composite, excluded as on Nov 22); 9 lateritic soil-cement bricks (soil stabilisation). No-DOI items go to probe_nodoi.py."""
import json
EX={16,55,128,265,201,85,96,98,9}
keys=json.load(open('listing-keys.json')); h=json.load(open('new-hits.json'))
sel={};nodoi=[]
for i,k in enumerate(keys):
  if i in EX: continue
  w=dict(h[k]); w['_idx']=i; w.pop('referenced_works',None)
  if not w.get('doi'): nodoi.append(i); continue
  sel[k]=w
json.dump(sel,open('selected.json','w')); json.dump(nodoi,open('nodoi-idx.json','w'))
print(len(keys),len(EX),len(sel),'nodoi',len(nodoi),nodoi)
