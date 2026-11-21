"""Re-confirm the 13 CiNii Research promotables via the CiNii OpenSearch API (crid pages answer HTTP 202 to the box)."""
import json,urllib.parse
from rlib import *
R=json.load(open('confirm-promotable.json'))
for r in R:
    if r['route']!='cinii-opensearch': continue
    q='https://cir.nii.ac.jp/opensearch/all?format=json&count=20&q='+urllib.parse.quote(r['title'][:200]); j=getj(q,t=40)
    ids=[it.get('@id') or (it.get('link') or {}).get('@id') for it in (j or {}).get('items',[])]
    hit=[it for it in (j or {}).get('items',[]) if (it.get('@id') or (it.get('link') or {}).get('@id'))==r['bestUrl']]
    r['ciniiRecheck']=dict(query=q,found=bool(hit),title=hit[0].get('title') if hit else None,sim=round(sim(hit[0].get('title',''),r['title']),2) if hit else None)
    print(r['ciniiRecheck']['found'],r['ciniiRecheck']['sim'],r['title'][:60])
json.dump(R,open('confirm-promotable.json','w'),ensure_ascii=False,indent=1)
