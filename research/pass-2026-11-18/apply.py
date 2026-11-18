"""pass-2026-11-18 apply: open-lead outcomes (R2562-R2564) + new verified records and lead outcomes into working files (atomic writes). Run once from pre-pass state.
Derived from research/pass-2026-11-13/apply.py."""
import json,os,re,collections
os.chdir('/workspace/type1l-index'); VD='2026-11-18'; PASS='pass-2026-11-18'; PD='research/pass-2026-11-18/'
P=json.load(open(PD+'plan.json'))
S=json.load(open('site-data.json')); L=json.load(open('research-ledger.json')); N=json.load(open('research/resource-notes.json'))
VER=[json.loads(l) for l in open('research/portable/verified-sources.jsonl')]
CAN=[json.loads(l) for l in open('research/portable/candidates.jsonl')]
NBEFORE=len(S['resources'])
assert NBEFORE==2560 and S['resources'][-1]['id']=='R2561' and S['lastUpdated']=='2026-11-13','expected pre-pass state'
OPEN=[i for i,c in enumerate(CAN) if c['status']=='candidate']; assert len(OPEN)==3,OPEN
assert not any(r['id']=='R428' for r in S['resources'])
before={r['id']:json.dumps(r,sort_keys=True) for r in S['resources']}
out=[]; nxt=2562
def mk(r,origin,cidx=None):
    global nxt
    rid='R%d'%nxt; nxt+=1
    S['resources'].append({'id':rid,'title':r['title'],'publisher':r['publisher'],'type':r['type'],'date':r['date'],'url':r['url'],'topics':list(r['topics'])})
    out.append(dict(id=rid,status='verified',title=r['title'],authors=r.get('authors'),publisher=r['publisher'],type=r['type'],date=r['date'],url=r['url'],doi=r.get('doi'),identifiers=r.get('ids') or {},topics=list(r['topics']),geography=r.get('geo'),language=r.get('lang','en'),description=r['desc'],access=r['access'],evidenceNote=r['evidence'],edition=r.get('edition'),rights=r.get('rights'),version=None,verifiedOn=VD,provenance=PASS,origin=origin,promotedFromCandidate=True,candidateIndex=cidx,added=VD))
    N[rid]=r['evidence']; return rid
WB='Wayback Machine snapshot (web.archive.org id_ raw copy) of the ejournals.eu article page, snapshot %s, fetched 2026-11-18'
OLD=[
(OPEN[0],dict(title='Assessment of the Carbon Footprint in the Clinker-Based Cement Production Process',authors=['Damira Sambaeva','Chynara Jayloobaikyzy','Zarlik Maimekov','Miraida Turgunbekova','Janarbek Izakov'],publisher='International Journal of Environmental Science and Green Technology (journals.ayu.edu.kz)',type='Paper',date='2026-09-30',
  url='https://journals.ayu.edu.kz/index.php/ijesgt/article/view/6574',doi='10.5281/zenodo.23496439',ids={'journal':'International Journal of Environmental Science and Green Technology 1(3):56–64','issn':'3080-8693','listedDoi':'10.5281/zenodo.23496439 (listed on the article page; not registered at doi.org/DataCite on 2026-11-18, HTTP 404)','openalex':'W7223170440'},
  topics=['cross-environment-cost','binder-portland','binder-international','cross-supply-region'],geo='Kyrgyzstan',lang='en',
  desc='Analyses the economic activity of several cement plants in the republic from their ecological passports and computes a maximum-entropy thermodynamic model of CO2/CO release from calcium carbonate decomposition for a model cement-clinker composition based on raw-material data from the Terek-Tash plant (Chui Region, Kyrgyzstan), giving total carbon load versus temperature (abstract-level).',
  access='landing_page_inspected',rights='Article page states CC BY-NC-ND 4.0 (copyright 2026 the journal).',
  evidence='Resolved open lead (2026-11-13: journal host HTTP 500, DOI unregistered). 2026-11-18: the https article page journals.ayu.edu.kz/index.php/ijesgt/article/view/6574 returned 200 and its Dublin Core/citation metadata were read (title, five authors, issued 2026-09-30, vol 1 no 3, pp 56–64, ISSN 3080-8693, abstract, CC BY-NC-ND 4.0). The DOI shown on the page (10.5281/zenodo.23496439) is NOT registered (doi.org, DataCite 404), so the record URL is the journal page. Paper text not reviewed.')),
(OPEN[1],dict(title='Carbon nanotubes influence on the compressive strength of cement composites',authors=['Małgorzata Lelusz'],publisher='Portal Czasopism Naukowych Ejournals.eu (Czasopismo Techniczne)',type='Paper',date='2014-06-10',
  url='https://doi.org/10.4467/2353737XCT.14.077.2527',doi='10.4467/2353737XCT.14.077.2527',ids={'journal':'Czasopismo Techniczne, Budownictwo Zeszyt 1-B (5) 2014, pp. 5–11','issn':'2353-737X','openalex':'W1830840438','archivedPage':'http://www.ejournals.eu/Czasopismo-Techniczne/2014/Budownictwo-Zeszyt-1-B-(5)-2014/art/2855/'},
  topics=['concrete-fibers','cross-mechanics','binder-portland','cross-mix'],geo='Poland',lang='en',
  desc='Presents technological guidelines for preparing cement composites containing carbon nanotubes and laboratory results on the effect of carbon nanotubes on the compressive strength of cement mortar (abstract-level; page language tag pl, abstract in English).',
  access='landing_page_inspected',rights=None,
  evidence='Resolved open lead (2026-11-13: host HTTP 500; Crossref has no record). 2026-11-18: doi.org still redirects to the ejournals.eu page (host HTTP 500 today) and Crossref/DataCite have no record; the publisher article page was read in an archived copy (%s) — Dublin Core/citation metadata: title, author, issued 2014-06-10, issue Budownictwo Zeszyt 1-B (5) 2014, pp. 5–11, ISSN 2353-737X, DOI 10.4467/2353737XCT.14.077.2527, English abstract, keywords. OpenAlex lists 2015-03-25 and a Kraków repository copy (suw.biblos.pk.edu.pl/44577); publisher-page date used. Paper text not reviewed.'%(WB%'2019-09-18')))
,(OPEN[2],dict(title='The effect of granulated fly ashes with phosphogypsum on the hardening of cement mortar',authors=['Gabriel Borowski','Jan J. Hycnar'],publisher='Portal Czasopism Naukowych Ejournals.eu (Czasopismo Techniczne)',type='Paper',date='2016-12-14',
  url='https://doi.org/10.4467/2353737XCT.16.156.5767',doi='10.4467/2353737XCT.16.156.5767',ids={'journal':'Czasopismo Techniczne, Budownictwo Zeszyt 2-B 2016, pp. 37–45','issn':'2353-737X','openalex':'W2558010753','archivedPage':'http://www.ejournals.eu/Czasopismo-Techniczne/2016/Budownictwo-Zeszyt-2-B-2016/art/8369/'},
  topics=['scm-flyash','scm-emerging','binder-portland','cross-mechanics','cross-environment-cost'],geo='Poland',lang='en',
  desc='Tests granulated fly ash with 20 % phosphogypsum waste as a cement constituent: cement with 20 % of ground granules met the PN-EN 197-1:2012 strength requirement for class 32.5; mortars had longer setting time than mortar with ash plus gypsum but similar 28-day compressive and flexural strength (abstract-level).',
  access='landing_page_inspected',rights=None,
  evidence='Resolved open lead (2026-11-13: host HTTP 500; Crossref has no record). 2026-11-18: doi.org redirects to the ejournals.eu page (host HTTP 500 today) and Crossref/DataCite have no record; the publisher article page was read in an archived copy (%s) — Dublin Core/citation metadata: title, two authors, issued 2016-12-14, issue Budownictwo Zeszyt 2-B 2016, pp. 37–45, ISSN 2353-737X, DOI 10.4467/2353737XCT.16.156.5767, English abstract, keywords. Paper text not reviewed.'%(WB%'2018-04-19')))]
oldout={}
for i,r in OLD:
    rid=mk(r,'candidate-queue',[i]); x=CAN[i]
    x.update(status='promoted',promotedTo=rid,promotedOn=VD,reviewedOn=VD,reviewPass=PASS,lastCheckedOn=VD); x.pop('openReason',None); oldout[i]=('promoted',rid)
# ---------- new verified records
k2id={}
for r in P['recs']: k2id[r['_key']]=mk(r,'discovery-'+PASS)
oldN=len(CAN); newlead={}; openl=[]
for ld in P['leads']:
    k=ld.pop('_key'); ld['pass']=ld.pop('pass_'); ld.pop('_reject',None)
    if '_open' in ld:
        ld.update(status='rejected',rejectCategory='unverifiable',rejectReason=ld.pop('_open')+'; the OpenAlex landing page could not be inspected (404/403/202 or title not found), so nothing could be verified')
    elif k in k2id: ld.update(status='promoted',promotedTo=k2id[k],promotedOn=VD)
    CAN.append(ld); newlead[k]=len(CAN)-1
i2k={v:k for k,v in k2id.items()}
for f in out[3:]: f['candidateIndex']=[newlead[i2k[f['id']]]]
first,last=out[0]['id'],out[-1]['id']; nfirst=out[3]['id']
tmap={t['id']:t for t in S['topics']}; byid={r['id']:r for r in S['resources']}
for r in S['resources']:
    for t in r['topics']:
        if r['id'] not in tmap[t]['resourceIds']: tmap[t]['resourceIds'].append(r['id'])
for t in S['topics']:
    for i_ in t['resourceIds']:
        if t['id'] not in byid[i_]['topics']: byid[i_]['topics'].append(t['id'])
for r in S['resources'][:NBEFORE]: assert json.dumps(r,sort_keys=True)==before[r['id']],r['id']
n=len(out); nnew=n-3
rejn=sum(1 for c in CAN[oldN:] if c['status']=='rejected')
tc=collections.Counter(t for r in out for t in r['topics'])
acc=collections.Counter(r['access'] for r in out)
langs=collections.Counter(r['language'] for r in out)
chase=[f['id'] for f in out if 'backward citation chase' in f['evidenceNote']]
fwd=[f['id'] for f in out if 'forward citation chase' in f['evidenceNote']]
cur=[f['id'] for f in out if (f['date'] or '').startswith('2026')]
noneng=[f['id'] for f in out if f['language']!='en']
focus=['concrete-mass-rcc','concrete-heavyweight','concrete-cellular','binder-specialty','concrete-shotcrete','binder-white-masonry','binder-well','binder-international','scm-natural','scm-clay','cross-supply-region','cross-failure-repair','cross-construction']
TKX=json.load(open(PD+'takeaways.json'))
TK=dict(TKX)
for tid,txt in TK.items():
    ids=[f['id'] for f in out if tid in f['topics']]
    tmap[tid]['takeaways'].append(txt%('%s–%s, %d records'%(ids[0],ids[-1],len(ids)) if ids else 'none'))
plc=[f['id'] for f in out if any(t in f['topics'] for t in ('standards','dot','carbon','fresh','strength','durability','scm','intl','apps','pavement','mix','field','mass','microcracking'))]
nodoi_ok=sum(1 for f in out if f['doi'] is None)
S['lastUpdated']=VD
S['whatsNew'].insert(0,{'date':'Nov 18','title':'Daily pass: %d verified additions (%s–%s)'%(n,first,last),'detail':'Resumed after the failed Nov 14–17 runs from the Nov 13 state. Resolved the 3 leads left open on Nov 13 (a 2026 Kyrgyz cement-plant carbon-footprint paper — journal page now reachable, its Zenodo DOI is unregistered; and two Czasopismo Techniczne papers read from archived publisher pages) as %s–%s. Discovery added %d verified sources for the next least-covered families — mass concrete/RCC, heavyweight and radiation-shielding concrete, foamed/aerated concrete, expansive/rapid/specialty cements, shotcrete, white cement and masonry/historic mortars, oil-well cement, national cement industries, natural pozzolans and agricultural ashes, metakaolin/calcined clays, cement supply/market/fuels, failure investigation and construction practice — plus %d records from backward and %d from forward citation chases, %d non-English records (Arabic-journal, German, French, Spanish, Portuguese, Hungarian, Croatian, Indonesian, Slovak, Swedish, Vietnamese, Romanian, Ukrainian; English glosses), a Portland-limestone/Type IL backfill (strength, durability, fresh, pavement, microcracking, carbon, DOT, standards) and a Nov 2026 current-awareness sweep (%d records dated 2026). %d new leads were rejected as unverifiable; none left open. Mostly DOI/abstract-level, not full-text reviews.'%(first,out[2]['id'],nnew,len(chase),len(fwd),len(noneng),len(cur),rejn)})
S['changeLog'].append({'date':VD,'entry':'Daily pass 2026-11-18: %d verified additions %s–%s (%s–%s promoted from the 3 previously open leads; %d from new discovery: title.search backfill incl. page-2 re-queries, language-filtered searches, PLC legacy-topic backfill, current-awareness sweep, backward/forward citation chase from existing records in the least-covered topics). %d new leads checked: %d promoted, %d rejected as unverifiable (unregistered DOIs whose landing pages could not be inspected), 0 left open. No corrections to existing records. R1–R2561 preserved (R428 still retired); topic membership union maintained.'%(n,first,last,first,out[2]['id'],nnew,len(P['leads']),nnew,rejn)})
S['gaps'].insert(0,'Daily pass 2026-11-18: additions are registry/catalogue-verified (%d abstract-level, %d DOI metadata only, %d landing pages read, %d catalogue records) — not full-text reviewed. Many Elsevier items have no abstract in Crossref/OpenAlex, so descriptions are bibliographic only. %d no-DOI hits (TRID/HRB reports, CiNii-listed books, CNKI/CQVIP pages, catalogue pages that need JavaScript) could not be inspected and were not added; 7 hits with unregistered DOIs were rejected. ACI portal papers can carry unregistered ACI DOIs (recorded as listedDoi). The Zenodo DOI printed on the Kyrgyz IJESGT article page is unregistered; the two Czasopismo Techniczne papers were read only from archived publisher pages because ejournals.eu returns HTTP 500. No open leads.'%(acc['abstract_metadata'],acc['doi_metadata'],acc['landing_page_inspected'],acc['catalog_metadata'],len(PRNOK)) if False else 'Daily pass 2026-11-18: additions are registry/catalogue-verified (%d abstract-level, %d DOI metadata only, %d landing pages read) — not full-text reviewed. Many Elsevier items have no abstract in Crossref/OpenAlex, so descriptions are bibliographic only. About 60 no-DOI hits (TRID/HRB reports, CiNii-listed books, CNKI/CQVIP pages, catalogue pages needing JavaScript) could not be inspected and were not added; %d hits with unregistered DOIs were rejected as unverifiable. ACI portal papers can carry unregistered ACI DOIs (recorded as listedDoi). The Zenodo DOI printed on the Kyrgyz IJESGT article page is unregistered; the two Czasopismo Techniczne papers were read only from archived publisher pages because ejournals.eu returns HTTP 500. No open leads.'%(acc['abstract_metadata'],acc['doi_metadata'],acc['landing_page_inspected'],rejn))
def wj(path,obj,indent=2):
    tmp=path+'.tmp'; json.dump(obj,open(tmp,'w'),indent=indent,ensure_ascii=False); os.replace(tmp,path)
ids=[r['id'] for r in S['resources']]; assert len(ids)==len(set(ids))
urls=[r['url'].rstrip('/').lower() for r in S['resources']]; dupu=[u for u,c in collections.Counter(urls).items() if c>1]; assert not dupu,dupu
tt=[re.sub(r'\W+',' ',r['title'].lower()).strip() for r in S['resources']]; dupt=[u for u,c in collections.Counter(tt).items() if c>1 and u]; print('dup titles:',dupt[:5])
wj('site-data.json',S); wj('research/resource-notes.json',N)
VER+=out
def wl(path,rows):
    tmp=path+'.tmp'
    with open(tmp,'w') as f:
        for v in rows: f.write(json.dumps(v,ensure_ascii=False)+'\n')
    os.replace(tmp,path)
wl('research/portable/verified-sources.jsonl',VER); wj('research/portable/verified-sources.json',VER,1)
wl('research/portable/candidates.jsonl',CAN); wj('research/portable/candidates.json',CAN,1)
wj(PD+'verified-%s-%s.json'%(first.lower(),last.lower()),out,1)
summ=dict(n=n,first=first,last=last,oldLeads={str(k):v for k,v in oldout.items()},newLeads=len(P['leads']),newPromoted=nnew,newRejected=rejn,open=0,candStatus=dict(collections.Counter(c['status'] for c in CAN)),topics=dict(tc.most_common()),access=dict(acc),types=dict(collections.Counter(r['type'] for r in out)),decades=dict(sorted(collections.Counter(((r['date'] or '')[:3]+'0s') if r['date'] else 'undated' for r in out).items())),languages=dict(langs),citationChaseBackward=len(chase),citationChaseForward=len(fwd),current2026=len(cur),typeILLegacyTopicRecords=len(plc),noDoiLandingRecords=nodoi_ok)
wj(PD+'apply-summary.json',summ,1); print(json.dumps(summ,ensure_ascii=False))
# ---------- ledger
s1=json.load(open(PD+'search-log.json')); s2=json.load(open(PD+'search-log2.json'))
for e in s2: e.setdefault('mode','title.search'); e.setdefault('language',None)
web=['curl: journals.ayu.edu.kz article 6574 (200; DC/citation metadata read); doi.org + DataCite 404 for 10.5281/zenodo.23496439','curl: doi.org 10.4467/2353737XCT.14.077.2527 and .16.156.5767 (redirect to ejournals.eu, HTTP 500), Crossref/DataCite 404, suw.biblos.pk.edu.pl (301 to repozytorium.biblos.pk.edu.pl; no response)','Wayback Machine availability API + id_ snapshots of ejournals.eu article pages 2855 (2019-09-18) and 8369 (2018-04-19)','curl: no-DOI landing pages read — ACI Concrete Abstracts Portal, NRC Publications Archive, Lund University Publications, Redalyc, DYNA (UNAL), Védelem Tudomány (MTAK OJS), University of South Florida / Nebraska digital commons, USP repositories, Indonesian university library catalogues, Iowa publications, CET journal','curl (not inspectable): TRID, CiNii, CNKI/CQVIP, DOAJ 403, ebscohost, ResearchGate']
rec=dict(id=PASS,date=VD,zone='America/Chicago',kind='daily-discovery+lead-verification',focusTopics=focus+['Type IL collection topics via Portland-limestone backfill (strength, durability, fresh, pavement, microcracking, carbon, dot, standards)','non-English literature (new: ar, fa, hr, hu, id, ro, sk, sv, uk, vi; plus pt/es/fr/de re-queried)','backward and forward citation chase from 628 existing DOI records in the least-covered topics'],currentAwareness=True,status='completed-unpublished (publisher to push)',
 repositories=['OpenAlex works API (title.search with period splits and page 2 of earlier-rotation queries; language filter; relevance search for current awareness and PLC topics; referenced_works backward chase; cites: forward chase)','Crossref works API (per-DOI, public pool)','DataCite API','doi.org resolver (HEAD)','Wayback Machine (archived publisher pages)','ACI International Concrete Abstracts Portal','NRC Publications Archive','Lund University Publications','Redalyc / DYNA / MTAK OJS / USP / digital commons / university library catalogues (landing-page reads)'],
 periods='1900–2026 (title.search windows ≤1990/1991–2026, ≤1995/1996–2012, ≤2000/2001–2026, ≤2008/2009–2026; current sweep 2026-08 → 2026-11-18, mostly ≥2026-09)',languages=sorted(langs),
 apiQueries=[dict(e,harvest='harvest1') for e in s1]+[dict(e,harvest='harvest2-page2') for e in s2],webQueries=web,
 citationsFollowed=[dict(direction='backward',tool='OpenAlex referenced_works',seeds='existing DOI-bearing records in the 12 least-covered topics (628 seeds; those dated <2006 expanded)',referencesFound=1196,kept='cited by >=2 seeds or published <1990 (684 kept before dedupe)',promoted=len(chase)),
   dict(direction='forward',tool='OpenAlex cites:',seeds='30 most-cited existing records in those topics',kept='top 8 citers ≤2012 + top 5 citers 2024–2026 per seed',promoted=len(fwd))],
 uniqueApiHits=dict(harvest1=2938,harvest2=2813,newAfterDedupe=2676+len(json.load(open(PD+'new-hits2.json')))),triage='Hits screened by title (listing capped at 24 per focus query-topic, 7 per language/PLC query, 45 current, 110 backward and 45 forward chase hits): 671 listed, 115 excluded on screening (soil stabilisation/geotechnical, dental/biomedical cement, sedimentary geology, dam health monitoring/seismic, generic structural-mechanics failure papers, adsorption/dye removal with ashes, non-concrete social-science "concrete", duplicate titles), 84 no-DOI hits probed on their landing pages (20 read and added; the rest not inspectable), 472 DOI hits verified. See research/pass-2026-11-18/listing.txt and select.py.',
 leadsProcessed=3+len(P['leads']),oldLeadOutcomes={str(k):v for k,v in oldout.items()},verifiedAdded=n,idRange='%s–%s'%(first,last),newLeadsRejected=rejn,openLeadsAfterPass=sum(1 for c in CAN if c['status']=='candidate'),openLeads=[],
 verificationStatus=dict(acc),topicsTouched=dict(tc.most_common()),corrections=[],
 gaps=['Most journal items DOI-level only (Elsevier abstracts absent from Crossref/OpenAlex)','Non-English titles glossed from title/abstract only','~60 no-DOI hits not inspectable (TRID, CiNii, CNKI/CQVIP, JS-only catalogues): e.g. Neville Properties of Concrete editions, Mehta Materials Science of Concrete 1989, Bažant creep books, Powers/Taylor classics','7 unregistered-DOI hits rejected as unverifiable (ACI 10.14359/17303, Iranian AUT/GSJ journal DOIs, Taiwan IJPRT)','Heavyweight/shielding, foamed concrete and mass-concrete topics now have ~70–100 records each but 2024–2026 coverage still thin','Possible correction: R1185 could carry its ACI DOI once registered (unchanged)'],
 nextSteps=['Next rotation head (least-recently backfilled): concrete-lightweight, binder-cac-csa, binder-lc3, binder-magnesium-carbonatable, scm-silica, scm-slag, scm-emerging, binder-blended, concrete-structural, cross-tests-codes, cross-environment-cost','Retry TRID-hosted no-DOI classics via HathiTrust/NTL/Google Books and CiNii via NDL','Forward chase from 2026-11-18 classics (most-cited foamed-concrete, shielding-concrete and RCC papers added today)','More non-English national literature (Czech/Polish theses, Turkish, Korean, Japanese JCI proceedings)','Add 2026 current-awareness queries for RILEM TCs, fib bulletins and agency reports'],
 summary='3 old leads promoted (%s–%s). %d new leads checked the same day: %d promoted, %d rejected (unverifiable), 0 open. %d verified additions %s–%s.'%(first,out[2]['id'],len(P['leads']),nnew,rejn,n,first,last))
L['passes'].append(rec)
qby=collections.defaultdict(list)
MAPT={'pll-pavement':'pavement','pll-strength':'strength','pll-durability':'durability','pll-fresh':'fresh','pll-micro':'microcracking','pll-standards':'standards','pll-dot':'dot','pll-carbon':'carbon','current-2026':None,'citation-chase':None,'citation-chase-fwd':None}
for e in s1+s2:
    t=e['topic']; t=MAPT.get(t,t)
    if t and t.startswith('lang-'): t=None
    if t: qby[t].append(dict(tool='OpenAlex',query=(e['query'] if e.get('mode')=='search' else 'title.search:'+e['query']),period=e.get('period'),language=e.get('language'),hits=e['n'],date=VD,pass_=PASS))
for t in L['topics']:
    st=tmap[t['id']]; t['resourceIds']=list(st['resourceIds']); t['resourceCount']=len(st['resourceIds'])
    add=[r['id'] for r in out if t['id'] in r['topics']]
    if add: t['verifiedAdditions']=t.get('verifiedAdditions',[])+add; t['lastTouched']=VD
    if t['id'] in qby: t['searches']=t.get('searches',[])+[{('pass' if k=='pass_' else k):v for k,v in q.items()} for q in qby[t['id']]]
    if t['id'] in focus:
        t['passStatus']='daily_pass_2026-11-18_backfill'; t['lastDeepPass']=PASS
        t['nextSteps']=['Forward citation chase from 2026-11-18 classics','Look for open institutional/government reports, older proceedings and non-English literature','Avoid repeating 2026-11-13/2026-11-18 title.search queries (see ledger)']
q=L['globalNextQueue']; moved=[x for x in q if x['topicId'] in focus]; L['globalNextQueue']=[x for x in q if x['topicId'] not in focus]+[dict(x,reason='Backfilled in pass-2026-11-18; rotate to end') for x in moved]
L['updated']=VD; L['lastDeepPass']=PASS
L['stats']=dict(topics=59,resourcesAtStart=NBEFORE,resourcesAfterPass=len(S['resources']),verifiedAdded=n,candidatesTotal=len(CAN),candidatesOpen=sum(1 for c in CAN if c['status']=='candidate'),candidatesPromoted=sum(1 for c in CAN if c['status']=='promoted'),candidatesMatchedVerified=sum(1 for c in CAN if c['status']=='matched-verified'),candidatesRejected=sum(1 for c in CAN if c['status']=='rejected'),leadsProcessedThisPass=3+len(P['leads']),previous=L['stats'])
wj('research-ledger.json',L)
# ---------- index.md
md=open('index.md').read().split('\n')
assert md[1].startswith('Last updated: 2026-11-13')
md[1]='Last updated: 2026-11-18 (America/Chicago) — daily pass (3 old leads resolved; %d verified additions). Daily research index; foundational coverage, not exhaustive. Historical records and gaps below are preserved; see expansion notes for current scope.'%n
o=['','## 2026-11-18 — daily pass (old leads resolved + discovery + same-day lead verification)',
'Step 1 — queue: 3 open leads at start (Zenodo-DOI IJESGT carbon-footprint paper; two Czasopismo Techniczne papers). Promoted as %s–%s: the Kyrgyz journal page is reachable today (its DOI remains unregistered); the Polish papers were read from archived publisher pages because ejournals.eu still returns HTTP 500.'%(first,out[2]['id']),
'Step 2 — discovery: OpenAlex title.search queries on the next least-covered families (concrete-mass-rcc, concrete-heavyweight, concrete-cellular, binder-specialty, concrete-shotcrete, binder-white-masonry, binder-well, binder-international, scm-natural, scm-clay, cross-supply-region, cross-failure-repair, cross-construction; page 2 of the earlier queries for deeper rows), language-filtered searches (ar, fa, hr, hu, id, ro, sk, sv, uk, vi new; pt/es/fr/de/ja/zh re-queried), a Portland-limestone backfill for Type IL topics, a Nov 2026 current-awareness sweep, and backward/forward citation chases from existing records in the least-covered topics. %d leads selected from ~5,750 raw API hits (before de-duplication against the index and candidate queue) and verified the same day (Crossref/DataCite per DOI + doi.org; landing pages for items without a registered DOI).'%len(P['leads']),
'- Promoted: %d (%s–%s); rejected: %d (unregistered DOIs, landing pages not inspectable); open: 0.'%(nnew,nfirst,last,rejn),
'- Evidence: abstract-level %d, DOI metadata only %d, landing page read %d, catalogue %d. Nothing full-text reviewed.'%(acc['abstract_metadata'],acc['doi_metadata'],acc['landing_page_inspected'],acc['catalog_metadata']),
'- Citation chase: %d backward, %d forward; non-English: %d (descriptions are English glosses); dated 2026: %d.'%(len(chase),len(fwd),len(noneng),len(cur)),
'- Corrections to existing records: none.','','### New verified resources (2026-11-18)']
for r in out:
    o.append(' | '.join([r['id'],','.join(r['topics']),r['title'],r['publisher'] or 'unknown',r['type'],r['date'] or 'undated',r['url']]))
    au=', '.join(a for a in (r['authors'] or []) if a) if r.get('authors') else 'unknown'
    o.append('  Note: Authors: %s. %s Access: %s. %s%s'%(au,r['description'],r['access'],r['evidenceNote'],(' Edition: '+r['edition']) if r.get('edition') else ''))
o+=['','### Open leads (2026-11-18)','- none']
open('index.md.tmp','w').write('\n'.join(md).rstrip('\n')+'\n'+'\n'.join(o)+'\n'); os.replace('index.md.tmp','index.md')
pg=[[r['id'],r['title'],r['publisher'] or '',r['type'],r['date'] or '',','.join(r['topics']),r['url']] for r in out]
json.dump(dict(rows=pg,news=S['whatsNew'][0],change=S['changeLog'][-1],gap=S['gaps'][0],total=len(S['resources']),takeaways={k:tmap[k]['takeaways'][-1] for k in TK}),open(PD+'page-d1118.json','w'),ensure_ascii=False,indent=0)
print('done',first,last,len(S['resources']))
