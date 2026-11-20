"""Manual selection (Grok Bot, 2026-11-20) from listing.txt. Excluded on screening (EX): 16 bare journal-title record ("Cement and Concrete Research", no DOI);
76 two-page journal item titled after the edited book 'Materials science of concrete IV' (book-notice type item, not a primary source); 170 refractory high-entropy alloys (metallurgy, off-topic); 226 radiopacified tricalcium silicate (dental/biomedical cement); 287 "Concreteness" (Chinese-language
linguistics chapter); 289 "Memories of Concrete in Latvia" (cultural history book chapter); 307 antibiotic-loaded cement spacers (orthopaedic); 308 Android app for
cement transport logistics; 310 cement company financial study; 314 geopolymers as hydrogen-storage media (energy, not construction); 360 sedimentary limestone compaction (geology).
No-DOI items go to probe_nodoi.py."""
import json
EX={16,76,170,226,287,289,307,308,310,314,360}
keys=json.load(open('listing-keys.json')); h=json.load(open('new-hits.json'))
sel={};nodoi=[]
for i,k in enumerate(keys):
  if i in EX: continue
  w=dict(h[k]); w['_idx']=i; w.pop('referenced_works',None)
  if not w.get('doi'): nodoi.append(i); continue
  sel[k]=w
json.dump(sel,open('selected.json','w')); json.dump(nodoi,open('nodoi-idx.json','w'))
print(len(keys),len(EX),len(sel),'nodoi',len(nodoi),nodoi)
