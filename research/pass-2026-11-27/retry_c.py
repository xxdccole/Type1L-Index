"""pass-2026-11-26 step 1: retry the whole review/retry list via routes NOT used on 2026-11-25 (where possible):
(1) direct re-read of the lead URL (host status check; PDFs read with pdftotext),
(2) Wayback CDX API (all captures, prefix match incl. other version suffixes of ksdot.gov documents), raw snapshot read,
(3) OpenAlex title search for alternative versions/locations (then Crossref for any DOI found, or the landing page read),
(4) J-STAGE search API (Japanese leads), (5) NDL Search OpenSearch, DNB SRU, BnF SRU (national library catalogues),
(6) Internet Archive advancedsearch (digitised items), (7) DataCite query search, (8) Europe PMC (recorded as aggregator only).
Aggregator-only hits (Europe PMC, OpenAlex record without an openable location) are recorded but not counted as inspection."""
import json,re,os,urllib.parse,subprocess,time,html,concurrent.futures as cf,xml.etree.ElementTree as ET
from rlib import *
VD='2026-11-27'
L=[json.loads(l) for l in open('../review-retry.jsonl')]
def getjh(u,t=40,h=None):
    a=['curl','-sL','-g','-m',str(t),'-A','GrokBot-research/1.0 (mailto:research@example.org)']+(['-H',h] if h else [])+[u]
    p=subprocess.run(a,capture_output=True,text=True)
    try: return json.loads(p.stdout)
    except Exception: return None
def gett(u,t=40):
    p=subprocess.run(['curl','-sL','-g','-m',str(t),'-A','GrokBot-research/1.0 (mailto:research@example.org)',u],capture_output=True,text=True); return p.stdout
def readfile(f):
    try: head=open(f,'rb').read(5)
    except Exception: return '',{}
    if head.startswith(b'%PDF'):
        p=subprocess.run(['pdftotext','-l','4',f,'-'],capture_output=True,text=True); return nu(p.stdout),{'pdf':True,'pdfText':p.stdout[:3000]}
    return text_of(f)
def ok(a,b,th=0.9): return sim(a or '',b or '')>=th or (len(nu(b))>25 and nu(b) in nu(a or ''))
def yok(e,y):
    try: return not e.get('year') or not y or abs(int(str(y)[:4])-int(str(e['year'])[:4]))<=1
    except Exception: return True
KTITLE=lambda e: re.sub(r'^KDOT\s+','',e['title'])
def kdot_words(e):
    t=e['title']; m=re.search(r'(PQL\s*[\d.]+|Special Provision\s+[\d-]+(?:-R\d+)?)',t)
    return m.group(1) if m else None
def one(e):
    k=re.sub(r'\W+','',nu(e['title']))[:40] or 'x%d'%abs(hash(e['title']))
    tried=[]; log=[]; res=None; agg=[]; u0=e.get('url')
    kd='ksdot.gov' in (u0 or '')
    def pagecheck(f,title,minm=0.75):
        txt,meta=readfile(f)
        if kd:
            key=kdot_words(e); kk=nu(key or '')
            return (kk and kk in txt and len(txt)>300), txt, meta, 1.0 if kk and kk in txt else 0.0
        m=match(title,txt); return (m>=minm and len(txt)>300), txt, meta, m
    # (1) direct re-read
    if u0:
        f='ev/%s-d.bin'%k; hc=curl(https(html.unescape(u0)),f,t=40); tried.append(https(u0))
        okk,txt,meta,m=pagecheck(f,e['title'])
        log.append('direct %s -> %s match=%.2f'%(https(u0),hc[:3],m))
        if hc.startswith('200') and okk: res=dict(route='direct',url=hc.split(' ',1)[1],http=hc[:3],match=m,meta=meta,snippet=snippet(txt,e['title']),evidenceFile=f)
        elif os.path.exists(f): os.remove(f)
    # (2) Wayback CDX (prefix; for ksdot documents: any version of the same document number)
    if u0 and not res:
        uu=re.sub(r'^https?://','',html.unescape(u0))
        pref=None
        mk=re.search(r'(ksdot\.gov/home/showpublisheddocument/\d+/)',uu)
        if mk: pref='www.'+mk.group(1)
        cands=[(pref,'prefix')] if pref else []
        cands+=[(uu,'exact')]
        mt=re.search(r'trid\.trb\.org/view(?:\.aspx\?id=|/)(\d+)',uu,re.I)
        if mt: cands+=[('trid.trb.org/view/'+mt.group(1),'exact'),('trid.trb.org/View/'+mt.group(1),'exact'),('trid.trb.org/view.aspx?id='+mt.group(1),'exact')]
        for q,mtp in cands:
            if res: break
            cu='https://web.archive.org/cdx/search/cdx?url=%s&matchType=%s&output=json&filter=statuscode:200&limit=-5'%(urllib.parse.quote(q,safe=''),mtp)
            j=getjh(cu,60); tried.append(cu)
            rows=(j or [])[1:]
            log.append('wayback cdx %s (%s): %d captures'%(q,mtp,len(rows)))
            for row in sorted(rows,key=lambda r:r[1],reverse=True)[:2]:
                ts,orig=row[1],row[2]; raw='https://web.archive.org/web/%sid_/%s'%(ts,orig)
                f='ev/%s-cdx.bin'%k; hc=curl(raw,f,t=90); tried.append(raw)
                okk,txt,meta,m=pagecheck(f,e['title'])
                log.append('wayback raw %s -> %s match=%.2f'%(raw,hc[:3],m))
                if hc.startswith('200') and okk:
                    res=dict(route='wayback',url='https://web.archive.org/web/%s/%s'%(ts,orig),original=orig,snapshot=ts,http=hc[:3],match=m,meta=meta,snippet=snippet(txt,e['title']),evidenceFile=f,cdx=True); break
                elif os.path.exists(f): os.remove(f)
    if kd:
        return dict(title=e['title'],result=res,log=log,urlsTried=tried,agg=agg)
    t=e['title']; tq=urllib.parse.quote(t[:200])
    # (3) OpenAlex title search for other versions
    if not res:
        q='https://api.openalex.org/works?per-page=8&mailto=research@example.org&search='+urllib.parse.quote(re.sub(r'[^\w\s]',' ',t)[:200])
        j=getjh(q); tried.append(q); hits=[w for w in (j or {}).get('results') or [] if ok(w.get('title') or w.get('display_name'),t) and yok(e,w.get('publication_year'))]
        log.append('openalex title search: %d results, %d title matches'%(len((j or {}).get('results') or []),len(hits)))
        own=(e.get('openalexId') or '').split('/')[-1]
        for w in hits:
            if res: break
            wid=w['id'].split('/')[-1]
            if w.get('doi'):
                doi=w['doi'].replace('https://doi.org/','')
                cr=getjh('https://api.crossref.org/works/'+urllib.parse.quote(doi)); tried.append('https://api.crossref.org/works/'+doi)
                if cr and cr.get('message') and ok((cr['message'].get('title') or [''])[0],t,0.85):
                    m=cr['message']; res=dict(route='crossref-search',url='https://doi.org/'+doi,doi=doi,viaOpenAlex=wid,meta=dict(title=m.get('title'),author=[(a.get('given','')+' '+a.get('family','')).strip() or a.get('name') for a in m.get('author',[])],issued=m.get('issued'),container=m.get('container-title'),publisher=m.get('publisher'),type=m.get('type'),volume=m.get('volume'),issue=m.get('issue'),page=m.get('page'),abstract=m.get('abstract')))
                    log.append('openalex alt version %s has DOI %s registered at Crossref'%(wid,doi)); break
                dc=getjh('https://api.datacite.org/dois/'+urllib.parse.quote(doi)); tried.append('https://api.datacite.org/dois/'+doi)
                if dc and dc.get('data'):
                    a=dc['data']['attributes']; tt=(a.get('titles') or [{}])[0].get('title')
                    if ok(tt,t,0.85): res=dict(route='datacite',url='https://doi.org/'+doi,doi=doi,viaOpenAlex=wid,meta=a); log.append('openalex alt version %s DOI %s at DataCite'%(wid,doi)); break
            for l in w.get('locations') or []:
                if res: break
                for uu in (l.get('landing_page_url'),l.get('pdf_url')):
                    if not uu or uu==u0 or https(uu) in tried or any(x in uu for x in ('cnki.net','cqvip.com','trid.trb.org','researchgate','ebscohost','doi.org/')): continue
                    f='ev/%s-oal.bin'%k; hc=curl(https(html.unescape(uu)),f,t=40); tried.append(https(uu))
                    okk,txt,meta,m=pagecheck(f,t)
                    log.append('openalex location %s (%s) -> %s match=%.2f'%(uu,wid,hc[:3],m))
                    if hc.startswith('200') and okk: res=dict(route='direct',url=hc.split(' ',1)[1],http=hc[:3],match=m,meta=meta,snippet=snippet(txt,t),evidenceFile=f,viaOpenAlex=wid); break
                    elif os.path.exists(f): os.remove(f)
            if not res and wid!=own: agg.append('OpenAlex %s (title match, no openable location)'%wid)
    # (4) J-STAGE (Japanese / jglobal leads)
    if not res and (re.search(r'[\u3040-\u30ff\u4e00-\u9fff]',t) or 'jglobal' in (u0 or '') or 'jst.go.jp' in (u0 or '')):
        q='https://api.jstage.jst.go.jp/searchapi/do?service=3&count=10&article='+urllib.parse.quote(t[:80])
        x=gett(q); tried.append(q); n=0
        for ent in re.findall(r'<entry>(.*?)</entry>',x,re.S):
            n+=1; ti=[html.unescape(re.sub(r'<[^>]+>','',a)).strip() for a in re.findall(r'<article_title>(.*?)</article_title>',ent,re.S)]
            tj=' '.join(ti); lk=re.search(r'<link[^>]*href="([^"]+)"',ent) or re.search(r'<article_link>.*?<(?:ja|en)>(.*?)</',ent,re.S)
            if any(ok(a,t) for a in re.findall(r'<(?:ja|en)>(.*?)</(?:ja|en)>',tj+' '+ent[:2000])) and lk:
                url=html.unescape(lk.group(1)); f='ev/%s-js.html'%k; hc=curl(url,f,t=40); tried.append(url); okk,txt,meta,m=pagecheck(f,t)
                log.append('j-stage hit %s -> %s match=%.2f'%(url,hc[:3],m))
                if hc.startswith('200') and okk: res=dict(route='direct',url=hc.split(' ',1)[1],http=hc[:3],match=m,meta=meta,snippet=snippet(txt,t),evidenceFile=f,via='J-STAGE search API'); break
        log.append('j-stage api: %d entries%s'%(n,'' if res else ', no match'))
    # (5) national library catalogues
    if not res and re.search(r'[\u3040-\u30ff\u4e00-\u9fff]',t):
        q='https://ndlsearch.ndl.go.jp/api/opensearch?cnt=10&title='+urllib.parse.quote(t[:60]); time.sleep(2); x=gett(q); tried.append(q); n=0
        for it in re.findall(r'<item>(.*?)</item>',x,re.S):
            n+=1; ti=html.unescape(re.sub(r'<[^>]+>','',(re.search(r'<title>(.*?)</title>',it,re.S) or [None,''])[1]))
            if ok(ti,t,0.85):
                lk=(re.search(r'<link>(.*?)</link>',it) or [None,''])[1]; md=dict(title=ti,creator=re.findall(r'<dc:creator>(.*?)</dc:creator>',it),publisher=re.findall(r'<dc:publisher>(.*?)</dc:publisher>',it),date=re.findall(r'<dcterms:issued[^>]*>(.*?)</dcterms:issued>',it) or re.findall(r'<dc:date>(.*?)</dc:date>',it),source=re.findall(r'<dcndl:publicationName>(.*?)</dcndl:publicationName>',it),ident=re.findall(r'<dc:identifier[^>]*>(.*?)</dc:identifier>',it))
                if yok(e,(md['date'] or [None])[0]): open('ev/%s-ndl.xml'%k,'w').write(it); res=dict(route='ndl-opensearch',url=lk,meta=md,evidenceFile='ev/%s-ndl.xml'%k); break
        log.append('ndl opensearch: %s items%s'%(n,'' if res else ', no match' if x else ' (no response)'))
    if not res:
        for name,base,schema,idx in (('dnb','https://services.dnb.de/sru/dnb?version=1.1&operation=searchRetrieve&recordSchema=oai_dc&maximumRecords=10&query=','oai_dc','tit'),('bnf','https://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&recordSchema=dublincore&maximumRecords=10&query=','dc','bib.title all')):
            if res: break
            words=' '.join([w for w in re.findall(r'\w+',t) if len(w)>3][:6])
            if not words: continue
            cq=('tit=%s'%words.replace(' ',' and tit=')) if name=='dnb' else 'bib.title all "%s"'%words
            q=base+urllib.parse.quote(cq); x=gett(q,45); tried.append(q)
            recs=re.findall(r'<(?:srw:)?recordData>(.*?)</(?:srw:)?recordData>',x,re.S); hit=None
            for rd in recs:
                ti=html.unescape(re.sub(r'<[^>]+>','',(re.search(r'<dc:title>(.*?)</dc:title>',rd,re.S) or [None,''])[1])).strip()
                ti0=re.split(r'\s+/\s+',ti)[0]
                if ok(ti0,t,0.85) or ok(ti,t,0.85):
                    md=dict(title=ti0,creator=[html.unescape(x_) for x_ in re.findall(r'<dc:creator>(.*?)</dc:creator>',rd)],publisher=[html.unescape(x_) for x_ in re.findall(r'<dc:publisher>(.*?)</dc:publisher>',rd)],date=re.findall(r'<dc:date>(.*?)</dc:date>',rd),ident=re.findall(r'<dc:identifier[^>]*>(.*?)</dc:identifier>',rd),lang=re.findall(r'<dc:language[^>]*>(.*?)</dc:language>',rd),type=re.findall(r'<dc:type[^>]*>(.*?)</dc:type>',rd))
                    if yok(e,(re.findall(r'\d{4}',' '.join(md['date'])) or [None])[0]): hit=(rd,md); break
            log.append('%s sru: %d records%s'%(name,len(recs),', match' if hit else ', no match'))
            if hit:
                rd,md=hit; open('ev/%s-%s.xml'%(k,name),'w').write(rd)
                link=[i for i in md['ident'] if i.startswith('http')]
                res=dict(route=name+'-sru',url=(link[0] if link else q),apiUrl=q,meta=md,evidenceFile='ev/%s-%s.xml'%(k,name))
    # (6) Internet Archive items
    if not res:
        words=' '.join([w for w in re.findall(r'\w+',t) if len(w)>3][:6])
        q='https://archive.org/advancedsearch.php?q='+urllib.parse.quote('title:(%s)'%words)+'&fl[]=identifier&fl[]=title&fl[]=creator&fl[]=year&fl[]=publisher&fl[]=mediatype&rows=10&output=json'
        j=getjh(q,45); tried.append(q); docs=((j or {}).get('response') or {}).get('docs') or []
        for d in docs:
            if ok(d.get('title'),t,0.88) and yok(e,d.get('year')) and d.get('mediatype') in ('texts',):
                mu='https://archive.org/metadata/'+d['identifier']; mj=getjh(mu,45); tried.append(mu)
                md=(mj or {}).get('metadata') or {}
                if md and ok(md.get('title'),t,0.85):
                    json.dump(md,open('ev/%s-ia.json'%k,'w'),ensure_ascii=False)
                    res=dict(route='internet-archive',url='https://archive.org/details/'+d['identifier'],apiUrl=mu,meta=md,files=len((mj or {}).get('files') or []),evidenceFile='ev/%s-ia.json'%k); break
        log.append('internet archive search: %d docs%s'%(len(docs),', match' if res else ', no match'))
    # (7) DataCite query search
    if not res:
        q='https://api.datacite.org/dois?page[size]=5&query='+urllib.parse.quote('titles.title:"%s"'%re.sub(r'["\\]','',t[:150]))
        j=getjh(q); tried.append(q); n=0
        for d in (j or {}).get('data') or []:
            n+=1; a=d['attributes']; tt=(a.get('titles') or [{}])[0].get('title')
            if ok(tt,t) and yok(e,a.get('publicationYear')): res=dict(route='datacite',url='https://doi.org/'+a['doi'],doi=a['doi'],meta=a); break
        log.append('datacite query: %d%s'%(n,', match' if res else ', no match'))
    # (8) Europe PMC (aggregator; recorded only)
    if not res:
        q='https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&pageSize=5&query='+urllib.parse.quote('TITLE:"%s"'%re.sub(r'["]','',t[:150]))
        j=getjh(q); tried.append(q)
        for d in ((j or {}).get('resultList') or {}).get('result') or []:
            if ok(d.get('title'),t): agg.append('Europe PMC %s:%s (aggregator record)'%(d.get('source'),d.get('id'))); break
        log.append('europe pmc: %s'%('aggregator match' if any('Europe PMC' in a for a in agg) else 'no match'))
    return dict(title=e['title'],result=res,log=log,urlsTried=tried,agg=agg)
if __name__=='__main__':
    import sys
    U=L if len(sys.argv)<2 else L[int(sys.argv[1]):int(sys.argv[2])]
    with cf.ThreadPoolExecutor(6) as ex: R=list(ex.map(one,U))
    out=os.environ.get('RETRY_OUT','retry-c.json'); json.dump(R,open(out,'w'),ensure_ascii=False,indent=1)
    import collections; print(collections.Counter((r['result'] or {}).get('route','none') for r in R))
    for r in R:
        if r['result']: print('OK',r['result']['route'],r['title'][:70],r['result']['url'][:110])
        elif r['agg']: print('AGG',r['title'][:70],r['agg'])
