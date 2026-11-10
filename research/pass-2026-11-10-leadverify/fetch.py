# Lead verification pass 2026-11-10: per-DOI Crossref + OpenAlex + doi.org registration check (polite, backoff).
import json,urllib.request,urllib.parse,urllib.error,time,sys,os,threading
from concurrent.futures import ThreadPoolExecutor
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
OUT='lead-meta.json'
res=json.load(open(OUT)) if os.path.exists(OUT) else {}
lock=threading.Lock()
def get(url,tries=4):
    err=None
    for a in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=40)),None
        except urllib.error.HTTPError as e:
            err='HTTP %d'%e.code
            if e.code==404: return None,err
            time.sleep(3*(a+1)*(3 if e.code==429 else 1))
        except Exception as e:
            err=str(e)[:100]; time.sleep(3*(a+1))
    return None,err
class NR(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**k): return None
op=urllib.request.build_opener(NR)
def doireg(d):
    try:
        h=op.open(urllib.request.Request('https://doi.org/'+urllib.parse.quote(d,safe='/'),headers=UA,method='HEAD'),timeout=30); return h.status,h.headers.get('Location')
    except urllib.error.HTTPError as e: return e.code,e.headers.get('Location')
    except Exception as e: return None,str(e)[:80]
def one(d):
    r={}
    x,e=get('https://api.crossref.org/works/'+urllib.parse.quote(d,safe='/'))
    if x:
        x=x['message']
        r['crossref']={'title':x.get('title'),'subtitle':x.get('subtitle'),'authors':[(a.get('given','')+' '+a.get('family','')).strip() or a.get('name') for a in x.get('author',[])],'publisher':x.get('publisher'),'container':x.get('container-title'),'issued':x.get('issued',{}).get('date-parts'),'type':x.get('type'),'volume':x.get('volume'),'issue':x.get('issue'),'page':x.get('page'),'license':[l.get('URL') for l in x.get('license',[])],'abstract':(x.get('abstract') or '')[:1500],'citedby':x.get('is-referenced-by-count'),'isbn':x.get('ISBN'),'issn':x.get('ISSN'),'language':x.get('language'),'relation':x.get('relation'),'update-to':x.get('update-to'),'resource':(x.get('resource') or {}).get('primary',{}).get('URL')}
    else: r['crossrefErr']=e
    y,e=get('https://api.openalex.org/works/doi:'+urllib.parse.quote(d,safe='/')+'?mailto=research@example.org')
    if y:
        inv=y.get('abstract_inverted_index') or {}
        pos=sorted((p,w) for w,ps in inv.items() for p in ps)
        pl=y.get('primary_location') or {}
        r['openalex']={'id':y.get('id'),'title':y.get('title'),'authors':[a['author']['display_name'] for a in y.get('authorships',[])],'date':y.get('publication_date'),'venue':(pl.get('source') or {}).get('display_name'),'publisher':(pl.get('source') or {}).get('host_organization_name'),'oa':y.get('open_access'),'type':y.get('type'),'license':pl.get('license'),'landing':pl.get('landing_page_url'),'lang':y.get('language'),'abstract':' '.join(w for p,w in pos)[:1500],'cited':y.get('cited_by_count'),'retracted':y.get('is_retracted'),'concepts':[c['display_name'] for c in (y.get('concepts') or [])[:8]]}
    else: r['openalexErr']=e
    if 'crossref' not in r:
        z,e=get('https://api.datacite.org/dois/'+urllib.parse.quote(d,safe='/'))
        if z:
            a=z['data']['attributes']
            r['datacite']={'title':[t.get('title') for t in a.get('titles',[])],'authors':[c.get('name') for c in a.get('creators',[])],'publisher':a.get('publisher') if isinstance(a.get('publisher'),str) else (a.get('publisher') or {}).get('name'),'year':a.get('publicationYear'),'type':(a.get('types') or {}).get('resourceTypeGeneral'),'url':a.get('url'),'abstract':' '.join(x.get('description','') for x in a.get('descriptions',[]))[:1500],'rights':[x.get('rights') for x in a.get('rightsList',[])]}
        else: r['dataciteErr']=e
    r['doiStatus'],r['doiLocation']=doireg(d)
    with lock:
        res[d]=r
        if len(res)%50==0:
            json.dump(res,open(OUT,'w'),ensure_ascii=False); print(len(res),flush=True)
    time.sleep(0.6)
c=[json.loads(l) for l in open('../portable/candidates.jsonl')]
dois=sorted({x['doi'].lower() for x in c if x['status']=='candidate' and x.get('doi')}-set(res))
print('todo',len(dois),flush=True)
with ThreadPoolExecutor(4) as ex: list(ex.map(one,dois))
json.dump(res,open(OUT,'w'),ensure_ascii=False); print('done',len(res))
