# No-DOI leads: locate OpenAlex work (from pass api-hits or title search), record landing page + metadata, probe landing URL.
import json,urllib.request,urllib.parse,urllib.error,time,re,glob
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def norm(t): return re.sub(r'[^a-z0-9]','',(t or '').lower())[:60]
hits={}
for f in glob.glob('../pass-2026-11-*/api-hits.json')+glob.glob('../pass-2026-11-08/unique-hits.json'):
    H=json.load(open(f)); H=H.values() if isinstance(H,dict) else H
    for h in H:
        if isinstance(h,dict) and h.get('title'): hits.setdefault(norm(h['title']),h)
def get(u):
    for a in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40))
        except urllib.error.HTTPError as e:
            if e.code==404: return None
            time.sleep(4*(a+1))
        except Exception: time.sleep(4*(a+1))
def probe(u):
    try:
        h=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30); return h.status,h.geturl()
    except urllib.error.HTTPError as e: return e.code,u
    except Exception as e: return None,str(e)[:80]
c=[json.loads(l) for l in open('../portable/candidates.jsonl')]
out={}
for x in c:
    if x['status']!='candidate' or x.get('doi') or x.get('sourceApi')=='manual': continue
    h=hits.get(norm(x['title'])); wid=(h or {}).get('id'); w=None
    if wid: w=get('https://api.openalex.org/works/'+wid.split('/')[-1]+'?mailto=research@example.org')
    if not w:
        s=get('https://api.openalex.org/works?filter=title.search:'+urllib.parse.quote(re.sub(r'[,:|()]',' ',x['title'])[:150])+'&per-page=5&mailto=research@example.org')
        for r in (s or {}).get('results',[]):
            if norm(r.get('title'))[:40]==norm(x['title'])[:40]: w=r; break
    r={'found':bool(w)}
    if w:
        inv=w.get('abstract_inverted_index') or {}
        pos=sorted((p,q) for q,ps in inv.items() for p in ps)
        locs=[l.get('landing_page_url') for l in w.get('locations',[]) if l.get('landing_page_url')]
        pl=w.get('primary_location') or {}
        r.update(id=w['id'],title=w.get('title'),doi=w.get('doi'),authors=[a['author']['display_name'] for a in w.get('authorships',[])],date=w.get('publication_date'),venue=(pl.get('source') or {}).get('display_name'),publisher=(pl.get('source') or {}).get('host_organization_name'),type=w.get('type'),landing=pl.get('landing_page_url'),locations=locs,oa=w.get('open_access'),abstract=' '.join(q for p,q in pos)[:1500],lang=w.get('language'),cited=w.get('cited_by_count'))
        u=(w.get('open_access') or {}).get('oa_url') or pl.get('landing_page_url') or (locs[0] if locs else None)
        if u: r['probeUrl']=u; r['probe']=probe(u)
    out[x['title']]=r; print(r.get('found'),r.get('probe'),x['title'][:70],flush=True); time.sleep(0.7)
json.dump(out,open('nodoi-meta.json','w'),indent=1,ensure_ascii=False)
