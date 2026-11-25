"""pass-2026-11-25: no-DOI leads whose landing page failed (probe-nodoi.json) or had no probe (C listing) -> pool for retry_a/retry_b (newlead-a/b)."""
import json
h=json.load(open('new-hits.json')); keys=json.load(open('listing-keys.json')); kb=json.load(open('listing-b-keys.json'))
P={r['idx']:r for r in json.load(open('probe-nodoi.json'))}
idx=json.load(open('nodoi-idx.json'))+[400+j for j,k in enumerate(kb) if not h[k].get('doi')]
with open('nodoi-fail-pool.jsonl','w') as f:
  for i in idx:
    p=P.get(i)
    if p and p['status']=='ok': continue
    w=h[keys[i] if i<400 else kb[i-400]]
    f.write(json.dumps(dict(idx=i,title=w['title'],authors=[a['author']['display_name'] for a in w['authorships']][:10],year=w.get('publication_year'),doi=None,url=(w.get('primary_location') or {}).get('landing_page_url'),openalexId=w['id'],retryOutcome='new',firstSeen='2026-11-25',probe=p),ensure_ascii=False)+'\n')
print(sum(1 for _ in open('nodoi-fail-pool.jsonl')))
