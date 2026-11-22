"""pass-2026-11-20 step 1c: round B for leads still unresolved after round A. Sanctioned public metadata APIs only:
DOAJ article API, DSpace 7 REST (pid/find) behind handle.net targets, NVA (Sikt) publication API for NTNU/Brage handles, DiVA MODS export
(incl. urn.kb.se resolution), Redalyc citation meta, theses.fr API, Crossref bibliographic search, Semantic Scholar search, Google Books volumes API."""
import json,re,os,urllib.parse,subprocess,time,html
from rlib import *
IN=os.environ.get('RETRY_IN','../review-retry.jsonl'); INA=os.environ.get('RETRY_A','retry-a.json'); OUTB=os.environ.get('RETRY_OUT','retry-b.json')
L=[json.loads(l) for l in open(IN)]; U={x['title']:x for x in L if x['retryOutcome']!='promotable'}
RA=json.load(open(INA))[65:77]
def getjh(u,t=40,h=None):
    a=['curl','-sL','-m',str(t),'-A','GrokBot-research/1.0 (mailto:research@example.org)']+(['-H',h] if h else [])+[u]
    p=subprocess.run(a,capture_output=True,text=True)
    try: return json.loads(p.stdout)
    except Exception: return None
def gettext(u,t=40):
    p=subprocess.run(['curl','-sL','-g','-m',str(t),'-A',UA,u],capture_output=True,text=True); return p.stdout
def ok(a,b,th=0.9): return sim(a or '',b or '')>=th or (nu(b) and nu(b) in nu(a or '') and len(nu(b))>25)
out=[]
for r in RA:
    if r['result']: out.append(r); continue
    e=U[r['title']]; k=re.sub(r'\W+','',nu(e['title']))[:40]; tried=r['urlsTried']; log=r['log']; res=None; urls=r['urls']
    for u in urls:
        if res: break
        m=re.search(r'doaj\.org/article/([0-9a-f]{32})',u)
        if m:
            q='https://doaj.org/api/articles/'+m.group(1); j=getjh(q); tried.append(q)
            bj=(j or {}).get('bibjson') or {}
            log.append('doaj api: %s'%(bj.get('title') and round(sim(bj['title'],e['title']),2)))
            if bj and ok(bj.get('title'),e['title']):
                json.dump(j,open('ev/%s-doaj.json'%k,'w'),ensure_ascii=False)
                res=dict(route='doaj-api',url='https://doaj.org/article/'+m.group(1),apiUrl=q,meta=dict(title=bj.get('title'),author=[a.get('name') for a in bj.get('author',[])],year=bj.get('year'),journal=(bj.get('journal') or {}).get('title'),publisher=(bj.get('journal') or {}).get('publisher'),volume=(bj.get('journal') or {}).get('volume'),number=(bj.get('journal') or {}).get('number'),start_page=bj.get('start_page'),end_page=bj.get('end_page'),identifier=bj.get('identifier'),link=[l.get('url') for l in bj.get('link',[])],keywords=bj.get('keywords'),abstract=(bj.get('abstract') or '')[:1500],language=(bj.get('journal') or {}).get('language')),evidenceFile='ev/%s-doaj.json'%k)
        mh=re.search(r'(?:hdl\.handle\.net|/handle)/(\d+(?:\.\d+)*/[\w.]+)',u) or re.search(r'lib\.ncsu\.edu/resolver/(\d+(?:\.\d+)*/\d+)',u)
        if mh and not res:
            hd=mh.group(1); j=getjh('https://hdl.handle.net/api/handles/'+hd); tgs=[v['data']['value'] for v in (j or {}).get('values',[]) if v.get('type')=='URL']
            for tg in tgs:
                if res: break
                mn=re.search(r'nva\.sikt\.no/registration/([\w-]+)',tg)
                if mn:
                    q='https://api.nva.unit.no/publication/'+mn.group(1); jj=getjh(q,h='Accept: application/json'); tried.append(q)
                    ed=(jj or {}).get('entityDescription') or {}
                    log.append('nva api: %s'%(ed.get('mainTitle') and round(sim(ed['mainTitle'],e['title']),2)))
                    if ed and ok(ed.get('mainTitle'),e['title'],0.85):
                        json.dump(jj,open('ev/%s-nva.json'%k,'w'),ensure_ascii=False)
                        ref=ed.get('reference') or {}; pi=(ref.get('publicationInstance') or {}); pc=ref.get('publicationContext') or {}
                        res=dict(route='nva-api',url=tg,apiUrl=q,meta=dict(title=ed.get('mainTitle'),author=[(c.get('identity') or {}).get('name') for c in ed.get('contributors',[])],date=ed.get('publicationDate'),language=ed.get('language'),abstract=(ed.get('abstract') or '')[:1500],instanceType=pi.get('type'),publisher=((pc.get('publisher') or {}).get('name') if isinstance(pc.get('publisher'),dict) else None),series=((pc.get('series') or {}).get('title') if isinstance(pc.get('series'),dict) else None),seriesNumber=pc.get('seriesNumber'),handle='https://hdl.handle.net/'+hd),evidenceFile='ev/%s-nva.json'%k)
                    continue
                mt=re.match(r'(https?://[^/]+)(/.*)?/handle/',tg) or re.match(r'(https?://[^/]+)/',tg)
                if mt:
                    q=https(mt.group(1))+'/server/api/pid/find?id=hdl:'+hd; jj=getjh(q); tried.append(q)
                    md=(jj or {}).get('metadata') or {}
                    t0=((md.get('dc.title') or [{}])[0]).get('value') or (jj or {}).get('name')
                    log.append('dspace7 rest %s: %s'%(q,t0 and round(sim(t0,e['title']),2)))
                    if t0 and ok(t0,e['title'],0.85):
                        json.dump(jj,open('ev/%s-dspace.json'%k,'w'),ensure_ascii=False)
                        g=lambda f:[x.get('value') for x in md.get(f,[])]
                        res=dict(route='dspace7-rest',url='https://hdl.handle.net/'+hd,apiUrl=q,landing=tg,meta={f:g(f) for f in md if f.split('.')[1] in ('title','contributor','date','publisher','type','language','description','identifier','subject','relation','source','thesis') and not f.startswith('dc.description.provenance')},evidenceFile='ev/%s-dspace.json'%k)
                        res['meta'].pop('dc.description.abstract',None)
                        res['meta']['abstract']=' '.join(g('dc.description.abstract'))[:1500]
    pid=None
    for u in urls:
        m=re.search(r'pid=(diva2:\d+)',u)
        if m: pid=m.group(1)
        if 'urn.kb.se' in u and not pid:
            p=subprocess.run(['curl','-s','-m','30','-o','/dev/null','-w','%{redirect_url}',https(u)],capture_output=True,text=True); tried.append(https(u))
            m=re.search(r'(diva2:\d+)',p.stdout or ''); log.append('urn.kb.se -> %s'%(p.stdout[:120] or 'no redirect'))
            if m: pid=m.group(1)
    if pid and not res:
        q='https://www.diva-portal.org/smash/references?referenceFormat=MODS&pids=[%s]&fileName=export.xml'%pid; x=gettext(q,60); tried.append(q)
        ti=' '.join(re.findall(r'<title>(.*?)</title>',x)[:1]); st=' '.join(re.findall(r'<subTitle>(.*?)</subTitle>',x)[:1])
        log.append('diva mods: %s'%(ti and round(sim(ti,e['title']),2)))
        if ti and (ok(ti,e['title'],0.85) or ok(ti+' '+st,e['title'],0.85)):
            open('ev/%s-diva.xml'%k,'w').write(x)
            nm=re.findall(r'<name type="personal"[^>]*>(.*?)</name>',x,re.S)
            au=[' '.join(reversed(re.findall(r'<namePart type="(?:family|given)">(.*?)</namePart>',n))) for n in nm]
            res=dict(route='diva-mods',url='https://www.diva-portal.org/smash/record.jsf?pid='+pid,apiUrl=q,meta=dict(title=html.unescape(ti),subTitle=html.unescape(st) or None,author=[html.unescape(a) for a in au if a][:10],dateIssued=re.findall(r'<dateIssued>(.*?)</dateIssued>',x)[:1],publisher=[html.unescape(p) for p in re.findall(r'<publisher>(.*?)</publisher>',x)][:2],genre=re.findall(r'<genre authority="diva" type="publicationTypeCode">(.*?)</genre>',x)[:1],language=re.findall(r'<languageTerm[^>]*>(.*?)</languageTerm>',x)[:1],series=[html.unescape(s) for s in re.findall(r'<relatedItem type="series">.*?<title>(.*?)</title>',x,re.S)][:1],urn=re.findall(r'<identifier type="urn">(.*?)</identifier>',x)[:1],abstract=html.unescape(' '.join(re.findall(r'<abstract[^>]*>(.*?)</abstract>',x,re.S)[:1]))[:1500]),evidenceFile='ev/%s-diva.xml'%k)
    for u in urls:
        if res: break
        if 'redalyc.org' in u:
            f='ev/%s-redalyc.html'%k; hc=curl(https(u),f); txt,meta=text_of(f); tried.append(https(u))
            t0=(meta.get('citation_title') or meta.get('html_title') or [''])[0]; log.append('redalyc %s title-sim %.2f'%(hc[:3],sim(t0,e['title'])))
            if hc.startswith('200') and ok(t0,e['title']): res=dict(route='direct',url=hc.split(' ',1)[1],http='200',match=1.0,meta=meta,evidenceFile=f)
        if 'theses.fr' in u:
            nnt=u.rstrip('/').split('/')[-1]
            for q in ('https://theses.fr/api/v1/theses/these/'+nnt,'https://theses.fr/'+nnt):
                if res: break
                j=getjh(q,50); tried.append(q); log.append('theses.fr %s -> %s'%(q,'json' if j else 'none'))
                if j and ok(j.get('titrePrincipal') or (j.get('titres') or {}).get('fr'),e['title'],0.85):
                    json.dump(j,open('ev/%s-thesesfr.json'%k,'w'),ensure_ascii=False); res=dict(route='thesesfr-api',url='https://theses.fr/'+nnt,apiUrl=q,meta={x:j.get(x) for x in ('titrePrincipal','titres','auteurs','directeurs','dateSoutenance','etabSoutenanceN','discipline','langues','status') if j.get(x)},evidenceFile='ev/%s-thesesfr.json'%k)
    if not res:
        q='https://cir.nii.ac.jp/opensearch/all?format=json&count=10&q='+urllib.parse.quote(e['title'][:200]); j=getjh(q,40); tried.append(q); best=None
        for it in (j or {}).get('items',[]):
            s=sim(it.get('title',''),e['title']); y=str(it.get('prism:publicationDate') or it.get('dc:date') or '')[:4]
            if s>=0.9 and (not e.get('year') or not y.isdigit() or abs(int(y)-int(e['year']))<=1) and (not best or s>best[0]): best=(s,it)
        log.append('cinii opensearch: %d items, best %s'%(len((j or {}).get('items',[])),round(best[0],2) if best else None))
        if best:
            it=best[1]; res=dict(route='cinii-opensearch',url=it.get('@id') or (it.get('link') or {}).get('@id'),match=best[0],meta={k2:it.get(k2) for k2 in ('title','dc:creator','dc:publisher','prism:publicationName','prism:publicationDate','dc:date','prism:volume','prism:number','prism:startingPage','prism:endingPage','dc:identifier','description') if it.get(k2)})
    if not res:
        q='https://openlibrary.org/search.json?limit=10&title='+urllib.parse.quote(re.sub(r'[:.,;].*','',e['title'])[:150]); j=getjh(q); tried.append(q); best=None
        au=[a.split()[-1].lower() for a in (e.get('authors') or []) if a.split()]
        for d in (j or {}).get('docs',[]):
            s=sim(d.get('title',''),re.sub(r'[:.,;].*','',e['title'])); aun=' '.join(d.get('author_name',[])).lower()
            if s>=0.88 and au and any(a in aun for a in au) and (not best or s>best[0]): best=(s,d)
        log.append('openlibrary: %d docs, best %s'%(len((j or {}).get('docs',[])),round(best[0],2) if best else None))
        if best:
            d=best[1]; res=dict(route='openlibrary',url='https://openlibrary.org'+d['key'],match=best[0],meta=dict(title=d.get('title'),author_name=d.get('author_name'),first_publish_year=d.get('first_publish_year'),publisher=(d.get('publisher') or [])[:5],isbn=(d.get('isbn') or [])[:3],edition_count=d.get('edition_count'),oclc=(d.get('oclc') or [])[:3]))
    if not res:
        q='https://api.crossref.org/works?rows=5&query.bibliographic='+urllib.parse.quote(e['title'][:200]); j=getjh(q); tried.append(q); best=None
        for it in ((j or {}).get('message') or {}).get('items',[]):
            t0=' '.join(it.get('title') or []); y=((it.get('issued') or {}).get('date-parts') or [[None]])[0][0]
            if sim(t0,e['title'])>=0.93 and (not e.get('year') or not y or abs(y-int(e['year']))<=1): best=it; break
        log.append('crossref bibliographic search: %s'%(best['DOI'] if best else 'no match'))
        if best: res=dict(route='crossref-search',url='https://doi.org/'+best['DOI'],doi=best['DOI'],meta=dict(title=best.get('title'),author=[(a.get('given','')+' '+a.get('family','')).strip() for a in best.get('author',[])],issued=best.get('issued'),container=best.get('container-title'),publisher=best.get('publisher'),type=best.get('type'),volume=best.get('volume'),issue=best.get('issue'),page=best.get('page')))
    if not res:
        q='https://www.googleapis.com/books/v1/volumes?maxResults=5&q='+urllib.parse.quote('intitle:'+e['title'][:120]); j=getjh(q); tried.append(q); best=None
        for it in (j or {}).get('items',[]):
            vi=it.get('volumeInfo',{}); t0=vi.get('title','')+((': '+vi['subtitle']) if vi.get('subtitle') else '')
            y=(vi.get('publishedDate') or '')[:4]; au=' '.join(vi.get('authors') or []).lower()
            aok=not e.get('authors') or any(a.split()[-1].lower() in au for a in e['authors'] if a.split())
            if (sim(t0,e['title'])>=0.9 or sim(vi.get('title',''),e['title'])>=0.9) and aok and (not y.isdigit() or not e.get('year') or abs(int(y)-int(e['year']))<=1): best=it; break
        log.append('google books: %s'%((j or {}).get('totalItems'),)+(' match '+best['id'] if best else ' no match'))
        if best:
            vi=best['volumeInfo']; json.dump(best,open('ev/%s-gbooks.json'%k,'w'),ensure_ascii=False)
            res=dict(route='google-books',url='https://books.google.com/books?id='+best['id'],apiUrl='https://www.googleapis.com/books/v1/volumes/'+best['id'],meta={x:vi.get(x) for x in ('title','subtitle','authors','publisher','publishedDate','industryIdentifiers','pageCount','language','description') if vi.get(x)},evidenceFile='ev/%s-gbooks.json'%k)
    if not res:
        q='https://api.semanticscholar.org/graph/v1/paper/search?limit=5&fields=title,year,authors,venue,externalIds,url,publicationVenue&query='+urllib.parse.quote(e['title'][:200])
        j=None
        for att in range(3):
            j=getjh(q,25)
            if j and 'data' in j: break
            time.sleep(6)
        tried.append(q); best=None
        for d in (j or {}).get('data') or []:
            if sim(d.get('title',''),e['title'])>=0.92 and (not e.get('year') or not d.get('year') or abs(d['year']-int(e['year']))<=1): best=d; break
        log.append('semanticscholar: %s'%('hit '+best['paperId'] if best else ('none' if j and 'data' in j else 'HTTP 429/no response')))
        if best:
            dois=(best.get('externalIds') or {}).get('DOI'); res=dict(route='semanticscholar',url=best.get('url'),doi=dois,meta=best)
        time.sleep(3)
    r['result']=res; out.append(r); print('OK' if res else '--',(res or {}).get('route'),e['title'][:70],flush=True)
    json.dump(out,open(OUTB,'w'),ensure_ascii=False,indent=1)
json.dump(out,open(OUTB,'w'),ensure_ascii=False,indent=1)
