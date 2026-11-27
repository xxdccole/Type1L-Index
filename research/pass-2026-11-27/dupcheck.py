"""pass-2026-11-26: fuzzy duplicate check of plan.json records against the index (title similarity >=0.9 with year within 1, same URL, same DOI)."""
import json,re,difflib,collections
from rlib import nu
S=json.load(open('../../site-data.json')); P=json.load(open('plan.json'))
def k(t): return nu(t)
idx=collections.defaultdict(list)
for r in S['resources']: idx[k(r['title'])[:12]].append(r)
urls={r['url'].rstrip('/').lower():r['id'] for r in S['resources']}
out=[]
for r in P['recs']:
    hit=None
    if r['url'].rstrip('/').lower() in urls: hit=(urls[r['url'].rstrip('/').lower()],'same URL')
    if not hit:
        kt=k(r['title'])
        for x in S['resources']:
            kx=k(x['title'])
            if abs(len(kx)-len(kt))>40: continue
            s=difflib.SequenceMatcher(None,kt,kx).ratio()
            if s>=0.9:
                y1=(r.get('date') or '')[:4]; y2=(x.get('date') or '')[:4]
                if not (y1 and y2) or abs(int(y1)-int(y2))<=1: hit=(x['id'],'title sim %.2f: %s (%s)'%(s,x['title'][:90],x.get('date'))); break
    if hit: out.append(dict(title=r['title'],origin=r['_origin'],match=hit)); print(r['_origin'][:14],'|',r['title'][:80],'|',hit)
json.dump(out,open('dupcheck.json','w'),ensure_ascii=False,indent=1)
