"""pass-2026-11-26: alternative routes for no-DOI discovery leads whose landing page failed or was skipped in probe_nodoi.py.
Order: CiNii Research OpenSearch (titles cleaned of conference paper numbers / trailing session labels), Open Library (books), then retry_c.one()
(direct re-read incl. PDFs via pdftotext, Wayback CDX, OpenAlex alternative versions, J-STAGE, NDL/DNB/BnF catalogues, Internet Archive, DataCite)."""
import json,re,urllib.parse,concurrent.futures as cf
from rlib import *
import retry_c
keys=json.load(open('listing-keys.json')); kb=json.load(open('listing-b-keys.json')); h=json.load(open('all-hits.json'))
K=lambda i: keys[i] if i<400 else kb[i-400]
PR={r['idx']:r for r in json.load(open('probe-nodoi.json'))}
def clean_t(t): return re.sub(r'\s*[\(（][^()（）]*[\)）]\s*$','',re.sub(r'^\d{3,4}\s+','',t)).strip()
def one(i):
    w=h[K(i)]; t=html.unescape(w['title']); e=dict(title=t,authors=[a['author']['display_name'] for a in w['authorships']][:10],year=w.get('publication_year'),openalexId=w['id'],url=(w.get('primary_location') or {}).get('landing_page_url'))
    tried=[]; log=[]; res=None; ct=clean_t(t)
    q='https://cir.nii.ac.jp/opensearch/all?format=json&count=10&q='+urllib.parse.quote(ct[:200]); j=retry_c.getjh(q); tried.append(q); best=None
    for it in (j or {}).get('items',[]):
        s=max(sim(it.get('title',''),t),sim(it.get('title',''),ct)); y=str(it.get('prism:publicationDate') or it.get('dc:date') or '')[:4]
        if s>=0.9 and (not e.get('year') or not y.isdigit() or abs(int(y)-int(e['year']))<=1) and (not best or s>best[0]): best=(s,it)
    log.append('cinii opensearch: %d items, best %s'%(len((j or {}).get('items',[])),round(best[0],2) if best else None))
    if best:
        it=best[1]; res=dict(route='cinii-opensearch',url=it.get('@id') or (it.get('link') or {}).get('@id'),match=best[0],meta={k2:it.get(k2) for k2 in ('title','dc:creator','dc:publisher','prism:publicationName','prism:publicationDate','dc:date','prism:volume','prism:number','prism:startingPage','prism:endingPage','dc:identifier','description') if it.get(k2)})
    if not res and w.get('type') in ('book','report','dissertation'):
        q='https://openlibrary.org/search.json?limit=10&title='+urllib.parse.quote(re.sub(r'[:.,;/].*','',t)[:150]); j=retry_c.getjh(q); tried.append(q)
        au=[a.split()[-1].lower() for a in (e.get('authors') or []) if a.split()]
        for d in (j or {}).get('docs',[]):
            if sim(d.get('title',''),re.sub(r'\s*/.*','',t))>=0.9 and (not au or any(x in ' '.join(d.get('author_name') or []).lower() for x in au)):
                res=dict(route='openlibrary',url='https://openlibrary.org'+d['key'],meta=dict(title=d.get('title'),author_name=d.get('author_name'),first_publish_year=d.get('first_publish_year'),publisher=(d.get('publisher') or [])[:5],isbn=(d.get('isbn') or [])[:3],edition_count=d.get('edition_count'),oclc=(d.get('oclc') or [])[:3])); break
        log.append('openlibrary: %s'%('match' if res else 'no match'))
    if not res:
        r=retry_c.one(e); res=r['result']; tried+=r['urlsTried']; log+=r['log']
        if not res and r['agg']: log.append('aggregator only: '+'; '.join(r['agg']))
    return dict(idx=i,title=t,result=res,log=log,urlsTried=tried)
if __name__=='__main__':
    todo=[i for i,r in PR.items() if r['status']!='ok']
    with cf.ThreadPoolExecutor(5) as ex: R=list(ex.map(one,todo))
    json.dump(R,open('newlead.json','w'),ensure_ascii=False,indent=1)
    import collections; print(collections.Counter((r['result'] or {}).get('route','none') for r in R))
    for r in R: print('OK' if r['result'] else '--',r['idx'],(r['result'] or {}).get('route'),r['title'][:60],(r['result'] or {}).get('url','')[:90])
