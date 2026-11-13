recs=[]; leads=[]
def tidy_title(c):
    t=clean(c.get('title'));st=c.get('subtitle') or []
    if st and clean(st[0]) and clean(st[0]).lower() not in t.lower(): t=t.rstrip(':')+': '+clean(st[0])
    return t
OPEN={635:'blocked: DOI 10.6052/j.issn.1000-4750.2021.01.0103 resolves at doi.org but is registered with neither Crossref nor JaLC; publisher site engineeringmechanics.cn returned HTTP 500 to curl and timed out to WebFetch, CNKI link timed out (2026-11-12). Retry next pass.'}
for k,w in sel.items():
    src_=w['_src']; idx=w['_idx']; q=w['queries'][0]
    base=T.get(idx) or ([q[0]] if q[0] in TOPICS else [])
    v=V[k]; c=v.get('crossref'); dc=v.get('datacite')
    lead=dict(status=None,topic=q[0],title=clean(w['title']),doi=(w.get('doi') or '').replace('https://doi.org/','') or None,year=w.get('publication_year'),authors=[a['author']['display_name'] for a in w['authorships']][:10] or None,venue=(((w.get('primary_location') or {}).get('source') or {}).get('display_name')),url=(w.get('primary_location') or {}).get('landing_page_url'),sourceApi='openalex',query=q[1],cited_by=w.get('cited_by_count'),notes='new lead discovered and verified in the same pass',addedOn=VD,pass_=PASS,openalexId=w['id'],reviewedOn=VD,reviewPass=PASS)
    if q[0]=='citation-chase': lead['citedBySeeds']=w.get('_citedBySeeds')
    if idx in OPEN:
        lead['_key']=k; lead['_open']=OPEN[idx]; leads.append(lead); continue
    if idx in ND:
        m=ND[idx]; title=m['title']
        ab=fixab(oa_abs(w))
        desc=GLOSS.get(idx) or m.get('desc') or first_sents(ab)
        rec=dict(title=title,authors=m['authors'],publisher=m['publisher'],type=m['type'],date=m['date'],url=m['url'],doi=m.get('doi'),ids=m['ids'],topics=topics_for(base,clean(w['title'])),geo=m.get('geo'),lang=m['lang'],desc=desc,access=m['access'],evidence='New lead (pass-2026-11-13 discovery) verified same day. '+m['ev'],edition=EDN.get(idx),rights=None)
    else:
        doi=lead['doi']
        if c:
            title=tidy_title(c); authors=[a for a in c['authors'] if a] or [a['author']['display_name'] for a in w['authorships']] or None
            asrc='Crossref' if [a for a in c['authors'] if a] else 'OpenAlex'
            date=fmt([c['issued']]) if c['issued'] and c['issued'][0] else (w.get('publication_date') and oadate(w['publication_date']))
            pub=PUB.get(c['publisher'],c['publisher']); cont=clean(c.get('container') or '')
            publisher=pub+(' ('+cont[:100]+')' if cont and cont!=pub else '')
            ids={}
            if cont: ids['journal']=('%s %s%s%s'%(cont[:80],c.get('volume') or '','(%s)'%c['issue'] if c.get('issue') else '',(':'+c['page']) if c.get('page') else '')).strip()
            if c.get('isbn'): ids['isbn']=c['isbn'][0]
            ab=fixab(c.get('abstract') or '') or fixab(oa_abs(w))
            typ=typ_of(c['type'],w.get('type'),title)
            reg='Crossref'
        else:
            title=clean(dc['title']); authors=dc['authors']; asrc='DataCite'; date=str(dc.get('year') or w.get('publication_year')); pub=dc['publisher']; publisher=pub; cont=None; ids={}
            ab=fixab(oa_abs(w)); typ='Thesis' if 'dissertation' in (w.get('type') or '') or dc.get('type')=='Dissertation' else 'Report'; reg='DataCite'
        access='abstract_metadata' if len(ab)>80 else 'doi_metadata'
        hd=v.get('doiHead','')
        ev='New lead (pass-2026-11-13 discovery) verified same day. %s metadata%s inspected %s; DOI registered (doi.org %s); full text not reviewed.'%(reg,' and abstract' if access=='abstract_metadata' else '',VD,hd.split(' ')[0])
        if reg=='Crossref' and asrc!='Crossref' and authors: ev+=' Authors from OpenAlex because Crossref registers none.'
        if not authors: ev+=' No authors registered (unknown).'
        if access=='abstract_metadata' and not fixab(c.get('abstract') if c else ''): ev=ev.replace('metadata and abstract','metadata and OpenAlex abstract')
        if q[0]=='citation-chase': ev+=' Found by backward citation chase from %s.'%', '.join(w.get('_citedBySeeds') or [])
        ed=EDN.get(idx)
        if c and c['type']=='standard' and 'ASTM' in (c['publisher'] or ''):
            des='ASTM '+re.sub(r'([A-Z])0+(\d)',r'\1\2',doi.split('/')[1].upper())
            title='%s Standard %s'%(des,title); typ='Standard catalogue record'; ed=ed or 'Latest edition registered in Crossref at verification (%s); earlier editions not indexed.'%des
            authors=['ASTM Committee '+(c['authors'][0].replace(' Committee','') if c['authors'] else '(not registered)')]
            desc='ASTM International catalogue record: %s.'%clean(c['title'])
        elif c and c['type']=='standard' and 'Beuth' in (c['publisher'] or ''):
            typ='Standard catalogue record'; authors=DINAUTH.get(idx,['DIN (committee not registered in Crossref)']); date=DINDATE[idx]
            ev+=' Crossref registers no issued date; edition date %s is part of the designation.'%DINDATE[idx]
            desc=GLOSS[idx]
        else:
            desc=GLOSS.get(idx) or first_sents(ab) or '%s%s%s; content beyond bibliographic metadata not reviewed.'%(typ,(' in '+cont[:90]) if cont else '',(' ('+date[:4]+')') if date else '')
        if c and not (c['issued'] and c['issued'][0]) and date and 'Beuth' not in (c['publisher'] or ''): ev+=' Date from OpenAlex (Crossref registers none).'
        if typ=='Other': typ='Book chapter' if '.ch' in doi else 'Paper'
        if idx==429: typ='Test method recommendation (RILEM)'
        title=re.sub(r'\bCO 2\b','CO2',title)
        lang=w.get('language') or 'en'
        if idx in GLOSS and lang!='en': ev+=' Title/abstract not in English; description is an English gloss.'
        rec=dict(title=title,authors=authors,publisher=publisher,type=typ,date=date,url='https://doi.org/'+doi,doi=doi,ids=ids,topics=topics_for(base,title),geo=oa_geo(w),lang=lang,desc=desc,access=access,evidence=ev,edition=ed,rights=None)
    rec['_key']=k; rec['_src']=src_; rec['_idx']=idx; rec['_topic']=q[0]
    recs.append(rec); lead['_key']=k; leads.append(lead)

