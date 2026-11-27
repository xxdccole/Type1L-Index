"""pass-2026-11-27 (tranche B = listing-b.txt rows 400+, excluded: 406 soil stabilisation, 420/424/425/427/429 economics/management/fertiliser/cartel studies of cement firms, 454/457/459/470-473/476/556 biomedical/dental/MTA cements, 471 masonry seismic damage model, 507 knitted formwork, 531 bridge-deck economics, 538 cold-formed steel bond-slip, 539 pipe-void polymer grouting, 592 piezoceramic-SAC sensor composite, 607 pumice geology). Tranche A: manual screening (Grok Bot) of listing.txt (256 rows). Excluded as off-topic: 12,13,95 dental/resin/MTA cements; 6,8 piezoresistive-sensor / graphene-oxide composites; 27,30,32 management/economics of Indian cement firms (ISM, supplier selection, profitability); 31,35,29,50 soil/subgrade stabilisation with cement (not concrete/binder); 54 dawsonite (sedimentary diagenetic cement); 68 magnesium phosphate for hard tissue (biomedical); 112,113,114,116 recycled aggregate / HDPE plastic (not heavyweight); 128 FRP-sandwich bridge deck; 149 segmental/shotcrete tunnel structural analysis; 162 real-estate marketing; 164 steel-concrete composite; 178 slope stability."""
import json
EXB={406,420,424,425,427,429,454,457,459,470,471,472,473,476,507,531,538,539,556,592,607}
EX={12,13,95,6,8,27,30,32,31,35,29,50,54,68,112,113,114,116,128,149,162,164,178}
keys=json.load(open('listing-keys.json')); kb=json.load(open('listing-b-keys.json')); h=json.load(open('new-hits.json')); json.dump(h,open('all-hits.json','w'))
sel={};nodoi=[]
for i,k in [(i,k) for i,k in enumerate(keys)]+[(400+j,k) for j,k in enumerate(kb)]:
  if i in EX or i in EXB: continue
  w=dict(h[k]); w['_idx']=i; w.pop('referenced_works',None)
  if not w.get('doi'): nodoi.append(i); continue
  sel[k]=w
json.dump(sel,open('selected.json','w')); json.dump(nodoi,open('nodoi-idx.json','w'))
print(len(keys)+len(kb),len(EX)+len(EXB),len(sel),'nodoi',len(nodoi))
