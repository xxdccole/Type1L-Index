import json,re,html,unicodedata,subprocess,time,urllib.parse,concurrent.futures as cf,difflib,os,sys
P=json.load(open('pool.json'))
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
def nu(s):
    s=unicodedata.normalize('NFKC',html.unescape(s or '')).lower()
    s=unicodedata.normalize('NFKD',s); s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[\W_]+',' ',s).strip()
def curl(u,f=None,t=35):
    a=['curl','-sL','-m',str(t),'-A',UA,'-w','%{http_code} %{url_effective}','--compressed']
    a+=['-o',f or '/dev/null',u]
    p=subprocess.run(a,capture_output=True,text=True); return p.stdout
def getj(u,t=30):
    p=subprocess.run(['curl','-sL','-m',str(t),'-A','GrokBot-research/1.0',u],capture_output=True,text=True)
    try: return json.loads(p.stdout)
    except Exception: return None
def text_of(f):
    try: t=open(f,errors='ignore').read()
    except Exception: return '',{}
    meta={}
    for m in re.finditer(r'<meta\s+[^>]*?(?:name|property)\s*=\s*"([^"]+)"[^>]*?content\s*=\s*"([^"]*)"',t,re.I):
        k=m.group(1); v=html.unescape(m.group(2)).strip()
        if v and re.match(r'(citation_|dc\.|dcterms\.|og:title|description|publication_date|document_type)',k,re.I):
            meta.setdefault(k,[]).append(v)
    ti=re.findall(r'<title[^>]*>(.*?)</title>',t,re.S|re.I)
    if ti: meta['html_title']=[html.unescape(re.sub(r'\s+',' ',ti[0])).strip()]
    b=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S|re.I)
    b=html.unescape(re.sub(r'<[^>]+>',' ',b))
    return nu(b),meta
def match(title,txt):
    w=[x for x in nu(title).split() if len(x)>3 or (len(x)>=1 and not x.isascii())][:8]
    if not w: w=nu(title).split()[:8]
    if not w: return 0
    return sum(x in txt for x in w)/len(w)
def https(u): return re.sub(r'^http://','https://',u)
def sim(a,b): return difflib.SequenceMatcher(None,nu(a),nu(b)).ratio()
def snippet(txt,title,n=600):
    w=[x for x in nu(title).split() if len(x)>3][:1]
    i=txt.find(w[0]) if w else 0
    return txt[max(0,i):i+n]
SKIPDIRECT=('ebscohost',)
def one(p):
    k=re.sub(r'\W+','',nu(p['title']))[:40]
    log=[]; res=None; tried=[]
    urls=[u for u in [p.get('url')]+p.get('alt',[]) if u]
    oa=None
    if p.get('openalexId'):
        oa=getj('https://api.openalex.org/works/'+p['openalexId'].split('/')[-1]+'?mailto=research@example.org')
        if oa:
            for l in oa.get('locations') or []:
                for u in (l.get('landing_page_url'),l.get('pdf_url')):
                    if u and html.unescape(u) not in urls: urls.append(html.unescape(u))
            if oa.get('doi') and not p.get('doi'): p['doi']=oa['doi']
    doi=(p.get('doi') or '').replace('https://doi.org/','') or None
    if doi:
        cr=getj('https://api.crossref.org/works/'+urllib.parse.quote(doi)); tried.append('https://api.crossref.org/works/'+doi)
        dc=getj('https://api.datacite.org/dois/'+urllib.parse.quote(doi)); tried.append('https://api.datacite.org/dois/'+doi)
        hd=curl('https://doi.org/'+doi,t=25); tried.append('https://doi.org/'+doi)
        log.append('doi.org '+hd[:3]+'; crossref '+('found' if cr and cr.get('message') else 'none')+'; datacite '+('found' if dc and dc.get('data') else 'none'))
        if cr and cr.get('message'):
            m=cr['message']; res=dict(route='crossref',url='https://doi.org/'+doi,meta=dict(title=m.get('title'),author=[(a.get('given','')+' '+a.get('family','')).strip() for a in m.get('author',[])],issued=m.get('issued'),container=m.get('container-title'),publisher=m.get('publisher'),type=m.get('type')))
        if not doi.startswith('10.'): pass
        if 'doi.org/' not in ' '.join(urls): urls.append('https://doi.org/'+doi)
    if not res:
        for u in urls:
            if any(s in u for s in SKIPDIRECT): continue
            u2=https(u); f='ev/%s-%d.html'%(k,len(tried)); hc=curl(u2,f); tried.append(u2)
            txt,meta=text_of(f); m=match(p['title'],txt)
            log.append('direct %s -> %s match=%.2f'%(u2,hc[:3],m))
            if hc.startswith('200') and m>=0.75 and len(txt)>300:
                res=dict(route='direct',url=hc.split(' ',1)[1],http=hc[:3],match=m,meta=meta,snippet=snippet(txt,p['title']),evidenceFile=f); break
            else: os.path.exists(f) and os.remove(f)
    if not res:
        for u in urls:
            if any(s in u for s in SKIPDIRECT): continue
            uu=re.sub(r'^https?://','',u)
            av=getj('https://archive.org/wayback/available?url='+urllib.parse.quote(uu,safe=''),t=40); tried.append('https://archive.org/wayback/available?url='+uu)
            snap=((av or {}).get('archived_snapshots') or {}).get('closest')
            if not snap: log.append('wayback none for '+uu); continue
            su=https(snap['url']); ts=snap['timestamp']; raw=su.replace('/web/'+ts+'/','/web/'+ts+'id_/')
            f='ev/%s-wb%d.html'%(k,len(tried)); hc=curl(raw,f,t=60); tried.append(raw)
            txt,meta=text_of(f); m=match(p['title'],txt)
            log.append('wayback %s -> %s match=%.2f'%(raw,hc[:3],m))
            if hc.startswith('200') and m>=0.75 and len(txt)>300:
                res=dict(route='wayback',url=su,original=u,snapshot=ts,http=hc[:3],match=m,meta=meta,snippet=snippet(txt,p['title']),evidenceFile=f); break
            else: os.path.exists(f) and os.remove(f)
    if not res and (any('nii.ac.jp' in u for u in urls) or p.get('language') in ('ja',) or p.get('type') in ('book','other')):
        q='https://cir.nii.ac.jp/opensearch/all?format=json&count=10&q='+urllib.parse.quote(p['title'][:200])
        j=getj(q,t=40); tried.append(q)
        best=None
        for it in (j or {}).get('items',[]):
            s=sim(it.get('title',''),p['title']); y=str(it.get('prism:publicationDate') or it.get('dc:date') or '')[:4]
            if s>=0.9 and (not p.get('year') or not y or abs(int(y)-int(p['year']))<=1) and (not best or s>best[0]): best=(s,it)
        log.append('cinii opensearch: %d items, best %s'%(len((j or {}).get('items',[])),round(best[0],2) if best else None))
        if best:
            it=best[1]; res=dict(route='cinii-opensearch',url=it.get('@id') or it.get('link',{}).get('@id'),match=best[0],meta={k2:it.get(k2) for k2 in ('title','dc:creator','dc:publisher','prism:publicationName','prism:publicationDate','dc:date','prism:volume','prism:number','prism:startingPage','prism:endingPage','dc:identifier','description') if it.get(k2)})
    if not res and (p.get('type') in ('book','other') or re.search(r'edition|handbook|manual',p['title'],re.I)):
        q='https://openlibrary.org/search.json?limit=10&title='+urllib.parse.quote(p['title'][:150])
        j=getj(q); tried.append(q); best=None
        au=[a.split()[-1].lower() for a in (p.get('authors') or []) if a.split()]
        for d in (j or {}).get('docs',[]):
            s=sim(d.get('title',''),p['title'].split(':')[0]); aun=' '.join(d.get('author_name',[])).lower()
            okA=(not au) or any(a in aun for a in au)
            if s>=0.85 and okA and (not best or s>best[0]): best=(s,d)
        log.append('openlibrary: %d docs, best %s'%(len((j or {}).get('docs',[])),round(best[0],2) if best else None))
        if best:
            d=best[1]; res=dict(route='openlibrary',url='https://openlibrary.org'+d['key'],match=best[0],meta=dict(title=d.get('title'),author_name=d.get('author_name'),first_publish_year=d.get('first_publish_year'),publisher=(d.get('publisher') or [])[:5],isbn=(d.get('isbn') or [])[:3],edition_count=d.get('edition_count'),lccn=(d.get('lccn') or [])[:3],oclc=(d.get('oclc') or [])[:3]))
    return dict(key=p['title'],result=res,log=log,urlsTried=tried,oaUrls=urls,doi=doi,lastTried=time.strftime('%Y-%m-%d'))
if __name__=='__main__':
    sel=[p for p in P if not p.get('skip')]
    lim=int(sys.argv[1]) if len(sys.argv)>1 else len(sel)
    with cf.ThreadPoolExecutor(8) as ex: R=list(ex.map(one,sel[:lim]))
    json.dump(R,open('retry-results.json','w'),ensure_ascii=False,indent=1)
    import collections; print(collections.Counter((r['result'] or {}).get('route','none') for r in R))
