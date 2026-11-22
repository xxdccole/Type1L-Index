"""pass-2026-11-20 dedupe (from pass-2026-11-19 dedupe.py): drop API hits already in the index (DOI or normalised title), in verified-sources, or in the candidate queue (any status incl. retry)."""
import json,re,sys
def nt(s): return re.sub(r'[^a-z0-9]','',(s or '').lower())[:120]
d=json.load(open('../../site-data.json'))
vs=[json.loads(l) for l in open('../portable/verified-sources.jsonl')]
cands=[json.loads(l) for l in open('../portable/candidates.jsonl')]
dois={};titles={}
for r in d['resources']:
  m=re.search(r'10\.\d{4,9}/\S+',(r.get('url') or '').lower())
  if m: dois[m.group(0).rstrip('/.')]=r['id']
  titles[nt(r['title'])]=r['id']
for r in vs:
  if r.get('doi'): dois[r['doi'].lower().replace('https://doi.org/','')]=r['id']
  titles[nt(r['title'])]=r['id']
cd={};ct={};oi={}
for i,c in enumerate(cands):
  if c.get('doi'): cd[c['doi'].lower().replace('https://doi.org/','')]=(i,c['status'])
  ct[nt(c.get('title'))]=(i,c['status'])
  if c.get('openalexId'): oi[c['openalexId'].lower()]=(i,c['status'])
hits=json.load(open(sys.argv[1])); new={};dup=[]
for k,w in hits.items():
  doi=(w.get('doi') or '').lower().replace('https://doi.org/',''); t=nt(w.get('title'))
  if not w.get('title'): dup.append((k,'no-title'));continue
  why=None
  if doi and doi in dois: why='existing '+dois[doi]
  elif t in titles: why='existing-title '+titles[t]
  elif doi and doi in cd: why='candidate %s'%(cd[doi],)
  elif t in ct: why='candidate-title %s'%(ct[t],)
  elif w['id'].lower() in oi: why='candidate-openalex %s'%(oi[w['id'].lower()],)
  if why: dup.append((k,why))
  else: new[k]=w
print(len(hits),len(new),len(dup))
json.dump(new,open(sys.argv[2],'w')); json.dump(dup,open(sys.argv[3],'w'),indent=0)
