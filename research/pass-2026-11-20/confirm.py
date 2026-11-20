"""pass-2026-11-20 step 1a: re-confirm the 97 'promotable' retry entries (evidence recorded 2026-11-19).
Checks the stored evidence file (title match) and re-reads the record live (Wayback raw snapshot / direct page / CiNii Research JSON / Open Library JSON)."""
import json,re,os,urllib.parse,concurrent.futures as cf
from rlib import *
L=[json.loads(l) for l in open('../review-retry.jsonl')]
P=[x for x in L if x['retryOutcome']=='promotable']
def one(e):
    k=re.sub(r'\W+','',nu(e['title']))[:40]; r=dict(title=e['title'],route=e['retryRoute'],bestUrl=e['bestUrl'])
    ef=e.get('evidenceFile')
    if ef and os.path.exists(ef):
        txt,_=text_of(ef); r['storedMatch']=round(match(e['title'],txt),2)
    u=e['bestUrl']
    if e['retryRoute']=='wayback':
        ts=e['snapshot']; live=u.replace('/web/'+ts+'/','/web/'+ts+'id_/')
    elif e['retryRoute'].startswith('openlibrary'):
        live=u+'.json'
    elif e['retryRoute']=='cinii-opensearch':
        live=u+('.json' if 'cir.nii.ac.jp/crid/' in u else '')
    else: live=https(u)
    f='ev/%s-c.html'%k; hc=curl(live,f,t=60); txt,meta=text_of(f)
    if e['retryRoute'].startswith('openlibrary') or e['retryRoute']=='cinii-opensearch':
        raw=open(f,errors='ignore').read() if os.path.exists(f) else ''
        t2=nu(raw); m=match(re.sub(r'[:.].*','',e['verifiedMetadata'].get('title') or e['title']) if e['retryRoute'].startswith('openlibrary') else e['title'],t2)
    else: m=match(e['title'],txt)
    r.update(liveUrl=live,liveHttp=hc[:3],liveMatch=round(m,2),liveFile=f)
    return r
with cf.ThreadPoolExecutor(6) as ex: R=list(ex.map(one,P))
json.dump(R,open('confirm-promotable.json','w'),ensure_ascii=False,indent=1)
import collections
print(collections.Counter((r['route'],r['liveHttp'],r['liveMatch']>=0.75) for r in R))
for r in R:
    if not (r['liveHttp']=='200' and r['liveMatch']>=0.75): print(r)
