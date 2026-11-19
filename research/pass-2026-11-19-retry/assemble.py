import json,re,collections,copy,html,unicodedata,subprocess
B='/workspace/type1l-index/'
TODAY='2026-11-19'
P=json.load(open('pool.json')); R=json.load(open('retry-results.json'))
rows=[json.loads(l) for l in open(B+'research/portable/candidates.jsonl')]
S=json.load(open(B+'site-data.json')); TN={t['id']:t['name'] for t in S['topics']}
def find(prefix):
    return [i for i,p in enumerate(P) if p['title'].lower().startswith(prefix.lower())]
# ---- manual decisions
DUP={}   # pool idx -> R id (same work already indexed)
for pre,rid in [('Materials science of concrete','R3534'),('Mathematical modeling of creep and shrinkage','R3538'),('Fly Ash in Cement and Concrete','R3535'),('Über die Grundlagen des Verbundes','R3536'),('Ultra-High Performance Concrete: A State-of-the-Art','R155')]:
    for i in find(pre): DUP[i]=rid
EXCL={}
for i in find('[Influences of vibration on the film thickness'): EXCL[i]=('off-topic','off-topic: dental cement film thickness (PubMed, 1971); not a cement/concrete construction source')
for i in find('セメントコンクリート = Cement and concrete'): EXCL[i]=('not-a-real-source','not a single source: CiNii serial record for the journal セメントコンクリート (Cement and Concrete), not an article, book or report')
# ---- manual overrides of retry results (better edition-level records found on Open Library)
OV={}
def ol(ed,work,meta): return dict(route='openlibrary-edition',url='https://openlibrary.org'+ed,workUrl='https://openlibrary.org/works/'+work,meta=meta,match=1.0)
for i in find('PROPERTIES OF CONCRETE. 4TH'): OV[i]=ol('/books/OL21457761M','OL11330446W',dict(title='Properties of concrete',edition='4th ed.',author='A. M. Neville',publisher='Longman Scientific & Technical / Wiley',date='1995',isbn10='0470235276',lccn=['97148152','95031843'],oclc='33837400',alsoCatalogued='CiNii Books BB1086853X is the 2011 Pearson edition (5th)'))
for i in find('PROPERTIES OF CONCRETE, 3RD'): OV[i]=ol('/books/OL19004365M','OL11330446W',dict(title='Properties of concrete',edition='3rd ed.',author='A. M. Neville',publisher='Longman Scientific & Technical',date='1993 (printing; LCCN 80025198 is the 1981 Pitman 3rd-edition record)',isbn10='0582406269',lccn=['80025198'],oclc='506211734'))
for i in find('Design and Control of Concrete Mixtures'): OV[i]=ol('/books/OL19828424M','OL4130223W',dict(title='Design and control of concrete mixtures',edition='13th ed.',author='Steven H. Kosmatka; William C. Panarese',publisher='Portland Cement Association (Engineering Bulletin EB001)',date='1988',isbn10='0893120871',oclc='17465353',editionNote='Lead is dated 1991 (OpenAlex); the 13th edition (1988) was reprinted with revisions through the early 1990s. Open Library also lists the 5th Canadian ed. (1991, ISBN 0893120944) and the 14th ed. (2002). Promote as the 13th edition unless the 1991 printing is wanted specifically.'))
# ---- topic guess for grouping
MAPT={'pll-pavement':'pavement','pll-strength':'strength','pll-durability':'durability','pll-fresh':'fresh','pll-micro':'microcracking','pll-standards':'standards','pll-dot':'dot','pll-carbon':'carbon','pll-mix':'mix','pll-supply':'supply','pll-intl':'intl','pll-apps':'apps','pll-field':'field'}
KW=[('cross-durability',r'corozi|vodonepropust|watertight'),('cross-construction',r'vibracij|vibration'),('cross-mix',r'properties of concrete|guide du béton|tecnologia dei materiali|highway materials|technology of cement and concrete'),('binder-activated',r'alkali[- ]activ|geopolymer|alkalicky|activadas alcalin|alkali-geactiveerde|waterglass|sodium sulfate slag|f-concrete'),
('scm-limestone',r'limestone'),
('scm-flyash',r'fly ?ash|flyash|pozzolanicreac|f1y ash|f mineral admixture'),('scm-slag',r'slag|escoria'),('scm-natural',r'pozzolan|puzolan|rice hu[sk]h|metakaolin'),
('scm-emerging',r'red mud|magnesium slag|paper industry|hârtiei|sanitarnej|recycled brick|reciklirane opeke'),
('concrete-circular',r'recycl|altbeton|återvinning|kruszywo|recyklovan|waste aggregate|agregados recicl'),
('cross-durability',r'corros|carbonat|chlorid|seawater|frost|durab|reactive|aggregates? .*reactiv|alkali.?silica|deterioration|granulats reactifs|koroz|kloriddiff'),
('concrete-heavyweight',r'radiation shield'),('concrete-fibers',r'textil|fiber|fibre|duktil'),('concrete-scc',r'self[- ]?compact|selvkompakt|самоуплотн|selbstverd|خودتراکم'),
('concrete-pavement-pervious',r'pavement|läpäisevä|road cement concrete|overlay|sleepers|railway tie'),
('concrete-mass-rcc',r'dam|betongdammer'),('cross-mechanics',r'creep|kriechen|shrinkage|fracture|plastic|damage|endommag|unilat|smeared|shear|stress|modul|elastic|crack|risstend|mechanic|toughness|flexural|lentur|thermal behaviour|high temperat|hautes temp|wylfa'),
('cross-tests-codes',r'code|eurocode|din 1045|instrucci|pn-en|sni 2847|aci 318|testing|test|microscopy|maturity|caracterisation|zkoušení|wytrzyma'),
('cross-construction',r'curing|cure|construction joint|vibrat|consisten|konsistenz|mognad|early age|jeune âge|drying|formwork|muotti|thermal treatment|fresh concrete|mold'),
('cross-chemistry',r'hydrat|paste|phase liquide|calcium hydroxide|non-evaporable|pore structure|microstructure|glass content|zementleim|binding von chlorid'),
('cross-mix',r'admixture|domieszki|dodatki|mixture|mix design|aggregate|ballast|kameniv|water-reducing|air-entrain|bentonite'),
('cross-environment-cost',r'carbon|co2|climate|klimat|hiilijalan|vähähiil|environmental|miljø|life ?cycle|market|inneklima|uudelleenkäyttö|tarjouslasken'),
('concrete-structural',r'reinforced|bertulang|betonarme|prestress|bridge|silta|mostních|structur|beton armé|stahlbeton|żelbet|plattstrimlor'),
('binder-portland',r'portland|cement'),('cross-chemistry',r'')]
def guess(p):
    t=p.get('topic') or ''; t=t.split('::')[0]
    if t in MAPT: return MAPT[t]
    if t in TN: return t
    s=(p['title']+' '+(p.get('venue') or '')).lower()
    for tid,rx in KW:
        if re.search(rx,s): return tid
    return 'cross-chemistry'
def year_of(meta):
    for k in ('citation_publication_date','citation_date','DC.date','dc.date','dcterms.issued','DC.issued','prism:publicationDate','dc:date','publication_date','first_publish_year','date','citation_online_date'):
        v=meta.get(k)
        if v is None: continue
        v=v[0] if isinstance(v,list) else v
        m=re.search(r'(1[89]\d\d|20\d\d)',str(v))
        if m: return int(m.group(1))
def flat(meta):
    out={}
    for k,v in (meta or {}).items():
        if k in ('description','DC.description') and isinstance(v,list): v=v[0][:400]
        if isinstance(v,list) and len(v)==1: v=v[0]
        out[k]=v
    return out
UNAV=[('trid.trb.org','TRID record pages time out from the box (HTTP 000/503)'),('pubsindex.trb.org','TRB pubsindex page times out (HTTP 000)'),('ci.nii.ac.jp/naid','CiNii article page returns HTTP 202 (CiNii Research JS shell), no record body'),('cir.nii.ac.jp','CiNii Research page returns HTTP 202, no record body'),('cnki.net','CNKI detail page needs JavaScript/login wall'),('cqvip.com','CQVIP page needs JavaScript'),('rosap.ntl.bts.gov','ROSA P returns HTTP 403'),('theseus.fi','Theseus returns HTTP 403'),('yadda.icm.edu.pl','yadda/BazTech returns HTTP 403 or an empty page'),('doaj.org','DOAJ returns HTTP 403'),('researchgate','ResearchGate blocks automated access (HTTP 403)'),('ebscohost','EBSCOhost needs a subscription login'),('diva-portal','DiVA record is a JavaScript-only page'),('urn.kb.se','DiVA/URN resolver returns HTTP 500 or a JavaScript-only page'),('hdl.handle.net/11250','Brage/NORA handle resolves to a JavaScript-only or 403 page'),('brage','Brage page is JavaScript-only'),('dspace','DSpace page is JavaScript-only or returned no record text'),('hdl.handle.net','repository handle resolves to a JavaScript-only page or an error'),('.pdf','PDF did not download or did not contain the title'),('pascal-francis','Pascal-Francis record page times out'),('solacolu','journal PDF returns HTTP 500 or no matching text'),('redalyc','Redalyc returns HTTP 502'),('cyberleninka','CyberLeninka blocks automated access'),('dergipark','DergiPark PDF download blocked'),('ijear.org','PDF unavailable'),('extras.springer','Springer extras file missing'),('lib.ugent.be','Ghent library catalogue page did not include the title (JS)'),('theses.fr','theses.fr page did not render the record'),('ibn.idsi.md','IBN Moldova returns HTTP 403'),('neliti','Neliti returns HTTP 403'),('pustaka.unand','library catalogue returns HTTP 500'),('lirias','Lirias PDF unavailable'),('dtu.dk','DTU Orbit file unavailable'),('ncsu','NCSU repository record unavailable'),('ajce.aut.ac.ir','journal PDF unavailable; DOI not registered'),('gsjournal','journal page unavailable; DOI not registered'),('umj.ac.id','journal PDF unavailable; DOI not registered')]
def why_unavail(p,r):
    urls=' '.join(r['oaUrls']+[p.get('url') or '']).lower(); reasons=[]
    for k,v in UNAV:
        if k in urls and v not in reasons: reasons.append(v)
    if r.get('doi'):
        dl=[l for l in r['log'] if l.startswith('doi.org')]
        if dl and 'crossref none' in dl[0] and 'datacite none' in dl[0]: reasons.insert(0,'DOI %s is not registered at Crossref or DataCite (%s)'%(r['doi'],dl[0].split(';')[0]))
    if not reasons: reasons.append('landing page did not open or did not contain the title')
    wb=[l for l in r['log'] if l.startswith('wayback none')]
    if wb: reasons.append('no usable Wayback snapshot')
    return '; '.join(reasons[:3])
def why_qual(p):
    bits=[]
    if p.get('authors'): bits.append('named author(s) %s'%', '.join(p['authors'][:2]))
    if p.get('venue'): bits.append('venue/catalogue "%s"'%p['venue'][:60])
    if p.get('year'): bits.append('dated %s'%p['year'])
    src=[s['kind'] for s in p['sources']]
    srcd='OpenAlex record (%s)'%('citation-chase hit: cited by existing index records' if 'citation-chase' in (p.get('topic') or '') else 'search hit on query topic %s'%p.get('topic'))
    return 'On-topic title (%s); %s; %s'%(TN.get(guess(p)), srcd, '; '.join(bits) or 'bibliographic record only')
ret_out=[]; promotable=[]; stay=collections.Counter(); dropped_excl=[]
cand_updates={}; new_lines=[]
for i,p in enumerate(P):
    r=R[i]; res=OV.get(i) or r['result']
    if i in DUP or i in EXCL:
        dropped_excl.append((i,DUP.get(i) or EXCL[i][0]))
        for ci in p.get('candIdx',[]):
            if i in DUP: cand_updates[ci]=dict(rejectCategory='duplicate',duplicateOf=DUP[i],previousRejectReason=rows[ci]['rejectReason'],rejectReason='duplicate of %s (same work already indexed; re-checked 2026-11-19 when the review/retry list was built)'%DUP[i],retryReviewedOn=TODAY)
            else: cand_updates[ci]=dict(rejectCategory=EXCL[i][0],previousRejectReason=rows[ci]['rejectReason'],rejectReason=EXCL[i][1],retryReviewedOn=TODAY)
        continue
    attempts=p['priorAttempts']+1
    tried=[]
    for u in (p.get('urlsTried') or [])+r['urlsTried']:
        if u not in tried: tried.append(u)
    topic=guess(p)
    e=dict(status='retry',title=p['title'],authors=p.get('authors') or [],venue=p.get('venue'),year=p.get('year'),doi=(r.get('doi') or None),url=p.get('url'),openalexId=p.get('openalexId'),
           reviewTopic=topic,reviewTopicName=TN.get(topic),firstSeen=p['firstSeen'],lastTried=TODAY,attempts=attempts,urlsTried=tried,
           retryReason=None,retryLog=r['log'][-8:],sourcesSeen=[{k:v for k,v in s.items()} for s in p['sources']])
    unav=why_unavail(p,r)
    if res: unav=unav.replace('; no usable Wayback snapshot','')
    if res:
        vm=flat(res.get('meta')); vy=None
        if res.get('evidenceFile'):
            tx=re.sub(r'<[^>]+>',' ',open(res['evidenceFile'],errors='ignore').read())
            mm=re.search(r'(?:Date published|Publication Date:?|Publication date:?)\s*(1[89]\d\d|20\d\d)',tx)
            if mm: vy=int(mm.group(1))
        vy=vy or year_of(res.get('meta') or {})
        note=None
        if p.get('year') and vy and abs(vy-int(p['year']))>1: note='Record found is dated %s but the lead is dated %s: likely a different edition/printing or an OpenAlex date error. Check before promoting.'%(vy,p['year'])
        if 'editionNote' in vm: note=vm['editionNote']
        e.update(retryOutcome='promotable',retryRoute=res['route'],bestUrl=res['url'],
                 verifiedOn=TODAY,verifiedMetadata=vm,verifiedYear=vy,verificationNote=note,
                 accessLevel={'direct':'landing_page_inspected','wayback':'landing_page_inspected (Wayback Machine archived copy)','cinii-opensearch':'catalog_metadata (CiNii Research record)','openlibrary':'catalog_metadata (Open Library work record)','openlibrary-edition':'catalog_metadata (Open Library edition record)'}[res['route']],
                 retryReason='%s. Previously unavailable: %s. Now inspectable on %s via %s: %s'%(why_qual(p),unav,TODAY,res['route'],res['url']))
        if res['route']=='direct' and ('ci.nii.ac.jp/ncid' in res['url'] or 'show_detail' in res['url']): e['accessLevel']='catalog_metadata (library catalogue record: %s)'%('CiNii Books' if 'nii' in res['url'] else 'Polsri library')
        if res['route']=='direct' and 'ntlsearch.bts.gov' in res['url']: e['accessLevel']='catalog_metadata (USDOT National Transportation Library record with abstract)'
        if res['route']=='wayback': e['archivedFrom']=res.get('original'); e['snapshot']=res.get('snapshot')
        if res.get('evidenceFile'): e['evidenceFile']='/workspace/retry-work/'+res['evidenceFile']
        promotable.append(e)
    else:
        e.update(retryOutcome='still-unavailable',bestUrl=p.get('url'),retryReason='%s. Unavailable: %s. Retried %s via OpenAlex locations, %sWayback Machine, CiNii Research, Open Library; Semantic Scholar answered HTTP 429.'%(why_qual(p),unav,TODAY,'DOI/Crossref/DataCite, ' if r.get('doi') else ''))
    ret_out.append(e)
    cis=p.get('candIdx',[])
    if cis:
        for ci in cis: cand_updates[ci]=dict(e,_merge=True)
    else: new_lines.append(e)
# relevance-not-established stays rejected (inspectable; relevance is the issue)
# apply to candidates
out=[]
for ci,row in enumerate(rows):
    u=cand_updates.get(ci)
    if u and u.get('_merge'):
        nr=dict(row); nr['previousStatus']='rejected'
        for k,v in u.items():
            if k in ('_merge','title','authors','venue','year','url','openalexId','sourcesSeen'): continue
            if k=='doi' and row.get('doi'): continue
            nr[k]=v
        nr['status']='retry'; out.append(nr)
    elif u:
        nr=dict(row); nr.update(u); out.append(nr)
    else: out.append(row)
for e in new_lines:
    nl=dict(e); nl.update(topic=(P and e['reviewTopic']),sourceApi='openalex',notes='Qualified no-DOI hit that was screened in but never added because its page could not be inspected; added to the review/retry list on 2026-11-19.',addedOn=TODAY,pass_='retry-list-2026-11-19')
    nl.pop('sourcesSeen',None); nl['sourcesSeen']=e['sourcesSeen']
    out.append(nl)
with open('candidates.jsonl','w') as f:
    for x in out: f.write(json.dumps(x,ensure_ascii=False)+'\n')
with open('review-retry.jsonl','w') as f:
    for x in sorted(ret_out,key=lambda x:(x['reviewTopicName'] or '',x['title'].lower())): f.write(json.dumps(x,ensure_ascii=False)+'\n')
st=collections.Counter(x['status'] for x in out); rc=collections.Counter(x.get('rejectCategory') for x in out if x['status']=='rejected')
summary=dict(poolUnique=len(P),retryTotal=len(ret_out),fromRejected=sum(1 for ci,u in cand_updates.items() if u.get('_merge')),newQualifiedAdded=len(new_lines),promotable=len(promotable),stillUnavailable=len(ret_out)-len(promotable),
  excluded=[(P[i]['title'][:70],why) for i,why in dropped_excl],candStatus=dict(st),rejectedByCategory=dict(rc),candLines=len(out),
  routes=dict(collections.Counter(e['retryRoute'] for e in promotable)))
json.dump(summary,open('summary.json','w'),ensure_ascii=False,indent=1)
print(json.dumps(summary,ensure_ascii=False,indent=1))
