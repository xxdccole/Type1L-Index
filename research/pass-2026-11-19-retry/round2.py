import json,re,urllib.parse,time,sys,concurrent.futures as cf
from retry import *
R=json.load(open('retry-results.json'))
todo=[i for i,r in enumerate(R) if not r['result']]
def trid_variants(u):
    m=re.search(r'(?:trid|pubsindex)\.trb\.org/(?:view\.aspx\?id=|view/|View/)(\d+)',u,re.I)
    if not m: return []
    n=m.group(1); return ['trid.trb.org/View/'+n,'trid.trb.org/view/'+n,'trid.trb.org/view.aspx?id='+n,'trid.trb.org/View.aspx?id='+n,'pubsindex.trb.org/view.aspx?id='+n]
def wb(p,uu,k,tried,log):
    av=getj('https://archive.org/wayback/available?url='+urllib.parse.quote(uu,safe=''),t=40); tried.append('https://archive.org/wayback/available?url='+uu)
    snap=((av or {}).get('archived_snapshots') or {}).get('closest')
    if not snap: log.append('wayback none for '+uu); return None
    su=https(snap['url']); ts=snap['timestamp']; raw=su.replace('/web/'+ts+'/','/web/'+ts+'id_/')
    f='ev/%s-wb2.html'%k; hc=curl(raw,f,t=60); tried.append(raw)
    txt,meta=text_of(f); m=match(p['title'],txt); log.append('wayback %s -> %s match=%.2f'%(raw,hc[:3],m))
    if hc.startswith('200') and m>=0.75 and len(txt)>300: return dict(route='wayback',url=su,original=uu,snapshot=ts,http=hc[:3],match=m,meta=meta,snippet=snippet(txt,p['title']),evidenceFile=f)
def r2(i):
    p=P[i]; r=R[i]; k=re.sub(r'\W+','',nu(p['title']))[:40]; tried=[]; log=[]; res=None
    for u in r['oaUrls']:
        for v in trid_variants(u):
            if res: break
            res=wb(p,v,k,tried,log)
    if not res:
        q='https://cir.nii.ac.jp/opensearch/all?format=json&count=10&q='+urllib.parse.quote(p['title'][:200]); j=getj(q,t=40); tried.append(q); best=None
        for it in (j or {}).get('items',[]):
            s=sim(it.get('title',''),p['title']); y=str(it.get('prism:publicationDate') or it.get('dc:date') or '')[:4]
            if s>=0.9 and y.isdigit() and p.get('year') and abs(int(y)-int(p['year']))<=1 and (not best or s>best[0]): best=(s,it)
        log.append('cinii opensearch: %d items, best %s'%(len((j or {}).get('items',[])),round(best[0],2) if best else None))
        if best:
            it=best[1]; res=dict(route='cinii-opensearch',url=it.get('@id'),match=best[0],meta={k2:it.get(k2) for k2 in ('title','dc:creator','dc:publisher','prism:publicationName','prism:publicationDate','dc:date','prism:volume','prism:number','prism:startingPage','prism:endingPage','dc:identifier') if it.get(k2)})
    if not res:
        q='https://openlibrary.org/search.json?limit=10&title='+urllib.parse.quote(re.sub(r'[:.,;].*','',p['title'])[:150]); j=getj(q); tried.append(q); best=None
        au=[a.split()[-1].lower() for a in (p.get('authors') or []) if a.split()]
        for d in (j or {}).get('docs',[]):
            s=sim(d.get('title',''),re.sub(r'[:.,;].*','',p['title'])); aun=' '.join(d.get('author_name',[])).lower()
            if s>=0.88 and au and any(a in aun for a in au) and (not best or s>best[0]): best=(s,d)
        log.append('openlibrary: %d docs, best %s'%(len((j or {}).get('docs',[])),round(best[0],2) if best else None))
        if best:
            d=best[1]; res=dict(route='openlibrary',url='https://openlibrary.org'+d['key'],match=best[0],meta=dict(title=d.get('title'),author_name=d.get('author_name'),first_publish_year=d.get('first_publish_year'),publisher=(d.get('publisher') or [])[:5],isbn=(d.get('isbn') or [])[:3],edition_count=d.get('edition_count'),oclc=(d.get('oclc') or [])[:3]))
    return i,res,tried,log
with cf.ThreadPoolExecutor(10) as ex: out=list(ex.map(r2,todo))
for i,res,tried,log in out:
    R[i]['urlsTried']+=tried; R[i]['log']+=log
    if res: R[i]['result']=res
json.dump(R,open('retry-results.json','w'),ensure_ascii=False,indent=1); print('phase1 saved',flush=True)
# semantic scholar sequential for still-unresolved
for i in [i for i in todo if not R[i]['result']]:
    p=P[i]; q='https://api.semanticscholar.org/graph/v1/paper/search?limit=5&fields=title,year,authors,venue,externalIds,url,openAccessPdf&query='+urllib.parse.quote(p['title'][:200])
    for att in range(2):
        j=getj(q,t=20)
        if j and 'data' in j: break
        time.sleep(5)
    R[i]['urlsTried'].append(q); best=None
    for d in (j or {}).get('data') or []:
        s=sim(d.get('title',''),p['title'])
        if s>=0.92 and (not p.get('year') or not d.get('year') or abs(d['year']-int(p['year']))<=1) and (not best or s>best[0]): best=(s,d)
    R[i]['log'].append('semanticscholar: %s'%('hit %.2f'%best[0] if best else ('none' if j and 'data' in j else 'no response/429')))
    if best: R[i]['s2']=best[1]
    time.sleep(3)
    json.dump(R,open('retry-results.json','w'),ensure_ascii=False,indent=1)
json.dump(R,open('retry-results.json','w'),ensure_ascii=False,indent=1)
import collections; print(collections.Counter((r['result'] or {}).get('route','none') for r in R)); print('s2 hits',sum(1 for r in R if r.get('s2')))
