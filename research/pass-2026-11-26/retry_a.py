"""pass-2026-11-20 step 1b: retry the 66 still-unavailable leads. Round A: fresh OpenAlex locations + DOI (Crossref/DataCite/doi.org) + direct https re-read + handle.net API target + Wayback for every URL variant."""
import json,re,os,urllib.parse,concurrent.futures as cf,time
from rlib import *
IN=os.environ.get('RETRY_IN','../review-retry.jsonl'); OUT=os.environ.get('RETRY_OUT','retry-a.json')
L=[json.loads(l) for l in open(IN)]
U=[x for x in L if x['retryOutcome']!='promotable']
def tryurl(e,u,k,tag,tried,log):
    f='ev/%s-%s.html'%(k,tag); hc=curl(https(u),f,t=40); tried.append(https(u))
    txt,meta=text_of(f); m=match(e['title'],txt); log.append('direct %s -> %s match=%.2f'%(https(u),hc[:3],m))
    if hc.startswith('200') and m>=0.75 and len(txt)>300: return dict(route='direct',url=hc.split(' ',1)[1],http=hc[:3],match=m,meta=meta,snippet=snippet(txt,e['title']),evidenceFile=f)
    os.path.exists(f) and os.remove(f)
def one(e):
    k=re.sub(r'\W+','',nu(e['title']))[:40]; tried=[]; log=[]; res=None; urls=[e['url']] if e.get('url') else []
    if e.get('openalexId'):
        oa=getj('https://api.openalex.org/works/'+e['openalexId'].split('/')[-1]+'?mailto=research@example.org'); tried.append('https://api.openalex.org/works/'+e['openalexId'].split('/')[-1])
        for l in (oa or {}).get('locations') or []:
            for u in (l.get('landing_page_url'),l.get('pdf_url')):
                if u and html.unescape(u) not in urls: urls.append(html.unescape(u))
        if oa and oa.get('doi') and not e.get('doi'): e['doi']=oa['doi'].replace('https://doi.org/',''); log.append('OpenAlex now lists DOI '+e['doi'])
    doi=e.get('doi')
    if doi:
        cr=getj('https://api.crossref.org/works/'+urllib.parse.quote(doi)); tried.append('https://api.crossref.org/works/'+doi)
        dc=getj('https://api.datacite.org/dois/'+urllib.parse.quote(doi)); tried.append('https://api.datacite.org/dois/'+doi)
        hd=curl('https://doi.org/'+doi,t=25); tried.append('https://doi.org/'+doi)
        log.append('doi.org %s; crossref %s; datacite %s'%(hd[:3],'found' if cr and cr.get('message') else 'none','found' if dc and dc.get('data') else 'none'))
        if cr and cr.get('message'):
            m=cr['message']; res=dict(route='crossref',url='https://doi.org/'+doi,meta=dict(title=m.get('title'),author=[(a.get('given','')+' '+a.get('family','')).strip() for a in m.get('author',[])],issued=m.get('issued'),container=m.get('container-title'),publisher=m.get('publisher'),type=m.get('type'),volume=m.get('volume'),issue=m.get('issue'),page=m.get('page')))
        elif dc and dc.get('data'): res=dict(route='datacite',url='https://doi.org/'+doi,meta=dc['data']['attributes'])
    for u in list(urls):
        mh=re.search(r'hdl\.handle\.net/(\d+(?:\.\d+)*/[\w.]+)',u)
        if mh:
            j=getj('https://hdl.handle.net/api/handles/'+mh.group(1)); tried.append('https://hdl.handle.net/api/handles/'+mh.group(1))
            t=[v['data']['value'] for v in (j or {}).get('values',[]) if v.get('type')=='URL']
            log.append('handle API -> %s'%(t or 'none'))
            for x in t:
                if x not in urls: urls.append(x)
    n=0
    for u in urls:
        if res: break
        n+=1; res=tryurl(e,u,k,'d%d'%n,tried,log)
    for u in urls:
        if res: break
        uu=re.sub(r'^https?://','',u)
        av=getj('https://archive.org/wayback/available?url='+urllib.parse.quote(uu,safe=''),t=40); tried.append('https://archive.org/wayback/available?url='+uu)
        snap=((av or {}).get('archived_snapshots') or {}).get('closest')
        if not snap: log.append('wayback none for '+uu); continue
        su=https(snap['url']); ts=snap['timestamp']; raw=su.replace('/web/'+ts+'/','/web/'+ts+'id_/')
        f='ev/%s-wb.html'%k; hc=curl(raw,f,t=60); tried.append(raw); txt,meta=text_of(f); m=match(e['title'],txt)
        log.append('wayback %s -> %s match=%.2f'%(raw,hc[:3],m))
        if hc.startswith('200') and m>=0.75 and len(txt)>300: res=dict(route='wayback',url=su,original=u,snapshot=ts,http=hc[:3],match=m,meta=meta,snippet=snippet(txt,e['title']),evidenceFile=f)
        else: os.path.exists(f) and os.remove(f)
    return dict(title=e['title'],result=res,log=log,urlsTried=tried,urls=urls,doi=doi)
with cf.ThreadPoolExecutor(8) as ex: R=list(ex.map(one,U))
json.dump(R,open(OUT,'w'),ensure_ascii=False,indent=1)
import collections; print(collections.Counter((r['result'] or {}).get('route','none') for r in R))
for r in R:
    if r['result']: print('OK',r['result']['route'],r['title'][:70],r['result']['url'][:100])
