"""pass-2026-11-19 build: verified records (R3048+) + lead decisions -> plan.json. apply.py writes working files.
Derived from research/pass-2026-11-18/build.py (same verification/metadata rules; adds BASEFIX for off-query-topic hits and date/authors/lang/note overrides for landing pages)."""
import json,re,sys,html,collections
B='/workspace/type1l-index/'
VD='2026-11-19'; PASS='pass-2026-11-19'
def clean(t): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',html.unescape(t or ''))).strip()
S=json.load(open(B+'site-data.json'))
TOPICS={t['id'] for t in S['topics']}
src=open('../pass-2026-11-10-leadverify/lv_build.py').read()
blk=src[src.index('CC={'):src.index('# ---------- existing index keys')]
blk=blk.replace("X['countries'].get(d) or []","[]")
exec(blk)
PUB.update({'ASTM International100 Barr Harbor Drive, PO Box C700, West Conshohocken, PA 19428-2959':'ASTM International','Beuth Verlag GmbH':'Beuth Verlag (DIN)','Birkhäuser Basel':'Birkhäuser','Springer Berlin Heidelberg':'Springer','FapUNIFESP (SciELO)':'SciELO','Editorial CSIC':'Editorial CSIC','CRC Press':'CRC Press','Thomas Telford Publishing':'ICE Publishing (Thomas Telford)'})
sel=json.load(open('selected.json')); V=json.load(open('doi-verify.json'))
PR={r['idx']:r for r in json.load(open('probe-nodoi.json'))}
PU=[r for r in json.load(open('probe-unreg.json')) if r['status']=='ok'] if __import__('os').path.exists('probe-unreg.json') else []
for r in PU: r['listedDoi']=r['doi']; r['idx']=int(r['idx']); PR[r['idx']]=r
PUI={int(r['idx']) for r in PU}
keys=json.load(open('listing-keys.json')); hh={'h1':json.load(open('new-hits.json')),'h2':json.load(open('new-hits2.json'))}
GL={int(k):v for k,v in json.load(open('glosses.json')).items()}
OV=json.load(open('overrides.json')) if __import__('os').path.exists('overrides.json') else {}
def fixab(a):
    a=clean(a)
    if 'First Name is required' in a or 'Last Name is required' in a or a.lower() in ('not available','resumen','abstract'): return ''
    a=re.sub(r'^(High Resolution Image\s*)?(Download MS PowerPoint Slide\s*)?','',a)
    a=re.sub(r'^(Summary|Abstract|Synopsis|Resumen|RESUMO|Resumo)(?=[A-Z\s])\s*','',a)
    return a
def oa_abs(w):
    ii=w.get('abstract_inverted_index')
    if not ii: return ''
    return ' '.join(x for _,x in sorted((p,x) for x,ps in ii.items() for p in ps))
def oa_geo(w):
    cs=[]
    for a in w.get('authorships',[]):
        for c in (a.get('countries') or [i.get('country_code') for i in a.get('institutions',[])]):
            if c and c not in cs: cs.append(c)
    return ' / '.join(CC.get(c,c) for c in cs[:4]) or None
def is_en(t):
    ws=re.findall(r"[a-zA-Z']+",t.lower())
    if len(ws)<8: return False
    return sum(w in ('the','of','and','in','to','is','a','for','with','are','this','by') for w in ws)/len(ws)>0.12
LANGNAME={'es':'Spanish','fr':'French','de':'German','pt':'Portuguese','zh':'Chinese','ja':'Japanese','ru':'Russian','uk':'Ukrainian','hr':'Croatian','hu':'Hungarian','id':'Indonesian','vi':'Vietnamese','sv':'Swedish','sk':'Slovak','ro':'Romanian','fa':'Persian','ar':'Arabic','it':'Italian','pl':'Polish','tr':'Turkish','nl':'Dutch','en':'English'}
MAPT={'pll-pavement':'pavement','pll-strength':'strength','pll-durability':'durability','pll-fresh':'fresh','pll-micro':'microcracking','pll-standards':'standards','pll-dot':'dot','pll-carbon':'carbon','pll-mix':'mix','pll-supply':'supply','pll-intl':'intl','pll-apps':'apps','pll-field':'field'}
BASEFIX=json.load(open('basefix.json')) if __import__('os').path.exists('basefix.json') else {}
def tidy_title(c):
    t=clean(c.get('title'));st=c.get('subtitle') or []
    if st and clean(st[0]) and clean(st[0]).lower() not in t.lower(): t=t.rstrip(':')+': '+clean(st[0])
    return t
def base_for(w,idx=None):
    if idx is not None and str(idx) in BASEFIX: return BASEFIX[str(idx)]
    q=w['queries'][0][0]
    if q in TOPICS: return [q]
    if q in MAPT: return [MAPT[q]]+(['scm-limestone'] if re.search('limestone',w['title'],re.I) else [])
    return []
recs=[]; leads=[]; REJ={}
LANGFIX={int(k):v for k,v in json.load(open('langfix.json')).items()} if __import__('os').path.exists('langfix.json') else {}
for k,w in sel.items():
    idx=w['_idx']; q=w['queries'][0]; base=base_for(w,idx)
    if idx in PUI: continue
    v=V[k]; c=v.get('crossref'); dc=v.get('datacite'); doi=(w.get('doi') or '').replace('https://doi.org/','')
    lead=dict(status=None,topic=q[0],title=clean(w['title']),doi=doi or None,year=w.get('publication_year'),authors=[a['author']['display_name'] for a in w['authorships']][:10] or None,venue=(((w.get('primary_location') or {}).get('source') or {}).get('display_name')),url=(w.get('primary_location') or {}).get('landing_page_url'),sourceApi='openalex',query=q[1],cited_by=w.get('cited_by_count'),notes='new lead discovered and verified in the same pass',addedOn=VD,pass_=PASS,openalexId=w['id'],reviewedOn=VD,reviewPass=PASS)
    if not (c or dc):
        lead['_key']=k; lead['_open']='unverified: DOI not registered at Crossref/DataCite on %s (doi.org %s); no inspectable record'%(VD,(v.get('doiHead') or '?').split(' ')[0]); lead['_reject']=True; leads.append(lead); continue
    if c:
        title=tidy_title(c); authors=[a for a in c['authors'] if a] or [a['author']['display_name'] for a in w['authorships']] or None
        asrc='Crossref' if [a for a in c['authors'] if a] else 'OpenAlex'
        date=fmt([c['issued']]) if c['issued'] and c['issued'][0] else (w.get('publication_date') and oadate(w['publication_date']))
        pub=PUB.get(c['publisher'],c['publisher']) or 'unknown'; cont=clean(c.get('container') or '')
        publisher=pub+(' ('+cont[:100]+')' if cont and cont!=pub else '')
        ids={}
        if cont: ids['journal']=('%s %s%s%s'%(cont[:80],c.get('volume') or '','(%s)'%c['issue'] if c.get('issue') else '',(':'+c['page']) if c.get('page') else '')).strip()
        if c.get('isbn'): ids['isbn']=c['isbn'][0]
        ab=fixab(c.get('abstract') or '') or fixab(oa_abs(w))
        typ=typ_of(c['type'],w.get('type'),title); reg='Crossref'
    else:
        title=clean(dc['title']); authors=dc['authors']; asrc='DataCite'; date=str(dc.get('year') or w.get('publication_year')); pub=dc['publisher']; publisher=pub; cont=None; ids={}
        ab=fixab(oa_abs(w)); typ='Thesis' if 'dissertation' in (w.get('type') or '') or dc.get('type')=='Dissertation' else {'JournalArticle':'Paper','Text':'Preprint','Preprint':'Preprint','BookChapter':'Book chapter','Book':'Book','ConferencePaper':'Conference paper'}.get(dc.get('type'),'Report'); reg='DataCite'
        if doi.lower().startswith('10.17863/'): publisher=pub+' (University of Cambridge Apollo repository record)'
        if doi.lower().startswith('10.13140/'): publisher='ResearchGate (DataCite DOI; publisher field "%s")'%pub
    lang=LANGFIX.get(idx) or w.get('language') or 'en'
    access='abstract_metadata' if len(ab)>80 else 'doi_metadata'
    hd=v.get('doiHead','')
    ev='New lead (pass-2026-11-19 discovery) verified same day. %s metadata%s inspected %s; DOI registered (doi.org %s); full text not reviewed.'%(reg,' and abstract' if access=='abstract_metadata' else '',VD,hd.split(' ')[0])
    if reg=='Crossref' and asrc!='Crossref' and authors: ev+=' Authors from OpenAlex because Crossref registers none.'
    if not authors: ev+=' No authors registered (unknown).'
    if access=='abstract_metadata' and not fixab(c.get('abstract') if c else ''): ev=ev.replace('metadata and abstract','metadata and OpenAlex abstract')
    if q[0]=='citation-chase': ev+=' Found by backward citation chase (%s).'%q[1].replace('refs of ','from ')
    if q[0]=='citation-chase-fwd': ev+=' Found by forward citation chase (%s).'%q[1]
    ed=None
    if c and c['type']=='standard' and 'ASTM' in (c['publisher'] or ''):
        des='ASTM '+re.sub(r'([A-Z])0+(\d)',r'\1\2',doi.split('/')[1].upper()).replace('_','/')
        title=('%s %s' if title.lower().startswith('standard') else '%s Standard %s')%(des,title); typ='Standard catalogue record'; ed='Latest edition registered in Crossref at verification (%s); earlier editions not indexed.'%des
        authors=['ASTM Committee '+(c['authors'][0].replace(' Committee','') if c['authors'] else '(not registered)')]
        desc='ASTM International catalogue record: %s.'%clean(c['title'])
    else:
        ens=first_sents(ab) if (lang=='en' or is_en(ab)) else ''
        if idx in LANGFIX and (w.get('language') or 'en')!=lang: ev+=' Language set to %s from the title/abstract (OpenAlex lists %s).'%(lang,w.get('language'))
        if idx in GL: desc=GL[idx]; ev+=' Title/abstract not in English; description is an English gloss.'
        elif ens: desc=ens
        elif lang!='en': desc='%s-language %s%s (%s); title-level record only, content not reviewed.'%(LANGNAME.get(lang,lang),typ.lower(),(' in '+cont[:80]) if cont else '',(date or '')[:4]); ev+=' Non-English record; no English description available.'
        else: desc='%s%s%s; content beyond bibliographic metadata not reviewed.'%(typ,(' in '+cont[:90]) if cont else '',(' ('+date[:4]+')') if date else '')
    if c and not (c['issued'] and c['issued'][0]) and date: ev+=' Date from OpenAlex (Crossref registers none).'
    if typ=='Other': typ='Book chapter' if '.ch' in doi else 'Paper'
    title=re.sub(r'\bCO 2\b','CO2',title)
    rec=dict(title=title,authors=authors,publisher=publisher,type=typ,date=date,url='https://doi.org/'+doi,doi=doi,ids=ids,topics=topics_for(base,title),geo=oa_geo(w),lang=lang,desc=desc,access=access,evidence=ev,edition=ed,rights=None)
    rec['_key']=k; rec['_idx']=idx; rec['_topic']=q[0]; recs.append(rec); lead['_key']=k; leads.append(lead)
# ---- no-DOI landing-page records (page read and title matched)
for i,p in sorted(PR.items()):
    if p['status']!='ok': continue
    s,k=keys[i]; w=hh[s][k]; q=w['queries'][0]; o=OV.get(str(i),{}); lang=o.get('lang') or LANGFIX.get(i) or w.get('language') or 'en'
    pl=w.get('primary_location') or {}; host=(pl.get('source') or {}).get('display_name') or re.sub(r'^https?://([^/]+)/.*',r'\1',p['url'])
    au=o.get('authors') or [a['author']['display_name'] for a in w['authorships']] or None
    title=clean(w['title']); date=o.get('date') or str(w['publication_year']); ab=fixab(oa_abs(w))
    ens=first_sents(ab) if (lang=='en' or is_en(ab)) else ''
    ev='New lead (pass-2026-11-19 discovery) verified same day. No DOI registered/listed; landing page %s read 2026-11-19 (HTTP 200; title matches the record%s). Authors and year from OpenAlex, consistent with the page where shown; full text not reviewed.'%(p['url'],'')+((' '+o['note']) if o.get('note') else '')
    if i in LANGFIX and (w.get('language') or 'en')!=lang: ev+=' Language set to %s from the title/abstract (OpenAlex lists %s).'%(lang,w.get('language'))
    if o.get('desc'): desc=o['desc']
    elif i in GL: desc=GL[i]; ev+=' Title/abstract not in English; description is an English gloss.'
    elif ens: desc=ens
    else: desc='%s-language record (%s) hosted at %s; title-level only, content not reviewed.'%(LANGNAME.get(lang,lang),date,host[:70]) if lang!='en' else 'Record hosted at %s (%s); catalogue/landing-page level only, content not reviewed.'%(host[:70],date)
    if q[0]=='citation-chase': ev+=' Found by backward citation chase (%s).'%q[1].replace('refs of ','from ')
    if q[0]=='citation-chase-fwd': ev+=' Found by forward citation chase (%s).'%q[1]
    typ=o.get('type') or ('Book' if w.get('type')=='book' else 'Report' if w.get('type')=='report' else 'Thesis' if w.get('type')=='dissertation' else 'Paper')
    rec=dict(title=title,authors=au,publisher=o.get('publisher') or host,type=typ,date=date,url=o.get('url') or p['url'],doi=None,ids=dict({'openalex':w['id'].split('/')[-1]},**({'listedDoi':p['listedDoi'].replace('https://doi.org/','')+' (listed by OpenAlex; not registered at doi.org/Crossref/DataCite on 2026-11-19)'} if p.get('listedDoi') else {})),topics=topics_for(base_for(w,i),title),geo=oa_geo(w),lang=lang,desc=desc,access=o.get('access') or 'landing_page_inspected',evidence=ev,edition=o.get('edition'),rights=None)
    lead=dict(status=None,topic=q[0],title=title,doi=None,year=w.get('publication_year'),authors=au,venue=host,url=o.get('url') or p['url'],sourceApi='openalex',query=q[1],cited_by=w.get('cited_by_count'),notes='new lead discovered and verified in the same pass',addedOn=VD,pass_=PASS,openalexId=w['id'],reviewedOn=VD,reviewPass=PASS)
    rec['_key']=k; rec['_idx']=i; rec['_topic']=q[0]; recs.append(rec); lead['_key']=k; leads.append(lead)
# ---- no-DOI hits whose landing page could not be inspected: recorded as rejected (unverifiable) leads with the probe outcome (2026-11-19 addition; Nov 18 left these out of the queue)
for i,p in sorted(PR.items()):
    if p['status']=='ok': continue
    s,k=keys[i]; w=hh[s][k]; q=w['queries'][0]
    why=('host not inspectable from the box (%s)'%re.sub(r'^https?://([^/]+)/.*',r'\1',p['url'])) if p['status']=='skipped-host' else ('landing page HTTP %s'%(p.get('http') or '000').split(' ')[0] + ('' if (p.get('http') or '').startswith(('403','404','5','000')) else ' but title not found on the page (JS-only page or PDF)'))
    lead=dict(status=None,topic=q[0],title=clean(w['title']),doi=None,year=w.get('publication_year'),authors=[a['author']['display_name'] for a in w['authorships']][:10] or None,venue=((w.get('primary_location') or {}).get('source') or {}).get('display_name'),url=p['url'] or None,sourceApi='openalex',query=q[1],cited_by=w.get('cited_by_count'),notes='new lead discovered and checked in the same pass',addedOn=VD,pass_=PASS,openalexId=w['id'],reviewedOn=VD,reviewPass=PASS)
    lead['_key']=k; lead['_open']='unverifiable: no DOI; %s on %s'%(why,VD); lead['_reject']=True; leads.append(lead)
STRIP={'binder-well','cross-failure-repair','concrete-repair-grout-overlay','concrete-architectural'}
for r in recs:
    base=base_for(sel[r['_key']],r['_idx']) if r['_key'] in sel else base_for(hh[keys[r['_idx']][0]][keys[r['_idx']][1]],r['_idx'])
    r['topics']=[t for t in r['topics'] if not (t in STRIP and t not in base and t!=r['_topic'])] or ['cross-chemistry']
def tkey(t): return re.sub(r'\W+',' ',t.lower()).strip()
seen={tkey(r['title']) for r in S['resources']}
keep=[]
for r in recs:
    if tkey(r['title']) in seen:
        # same title as an existing/earlier record: distinguish by year+venue
        r['title']='%s (%s, %s)'%(r['title'],(r['date'] or '')[:4],(r['ids'].get('journal') or r['publisher'])[:70])
    seen.add(tkey(r['title'])); keep.append(r)
json.dump(dict(recs=keep,rejected=REJ,leads=leads),open('plan.json','w'),indent=1,ensure_ascii=False)
print(len(recs),len(keep),sum(1 for l in leads if l.get('_reject')))
print(collections.Counter(r['access'] for r in keep)); print(collections.Counter(r['lang'] for r in keep)); print(collections.Counter(t for r in keep for t in r['topics']).most_common())
