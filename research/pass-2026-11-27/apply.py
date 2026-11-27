"""pass-2026-11-26 apply (from pass-2026-11-25 apply.py): retry-list promotions + new verified records (R4909+) and lead outcomes into working files (atomic writes).
Run once from the post-2026-11-25 state (backup in research/backups/pre-2026-11-26/). Open queue was empty at start (0 candidates); the open-queue code paths are kept but receive empty lists."""
import json,os,re,collections,copy
os.chdir('/workspace/type1l-index'); VD='2026-11-26'; PASS='pass-2026-11-26'; PD='research/pass-2026-11-26/'
P=json.load(open(PD+'plan.json'))
S=json.load(open('site-data.json')); L=json.load(open('research-ledger.json')); N=json.load(open('research/resource-notes.json'))
VER=[json.loads(l) for l in open('research/portable/verified-sources.jsonl')]
CAN=[json.loads(l) for l in open('research/portable/candidates.jsonl')]
RL=[json.loads(l) for l in open('research/review-retry.jsonl')]
NBEFORE=len(S['resources'])
assert NBEFORE==4907 and S['resources'][-1]['id']=='R4908' and S['lastUpdated']=='2026-11-25','expected pre-pass state'
assert not any(r['id']=='R428' for r in S['resources'])
OPEN=[i for i,c in enumerate(CAN) if c['status']=='candidate']; assert len(OPEN)==0,len(OPEN)
assert sum(1 for c in CAN if c['status']=='retry')==125 and len(RL)==125
before={r['id']:json.dumps(r,sort_keys=True) for r in S['resources']}
out=[]; nxt=4909
def mk(r,origin,cidx=None):
    global nxt
    rid='R%d'%nxt; nxt+=1
    S['resources'].append({'id':rid,'title':r['title'],'publisher':r['publisher'],'type':r['type'],'date':r['date'],'url':r['url'],'topics':list(r['topics'])})
    out.append(dict(id=rid,status='verified',title=r['title'],authors=r.get('authors'),publisher=r['publisher'],type=r['type'],date=r['date'],url=r['url'],doi=r.get('doi'),identifiers=r.get('ids') or {},topics=list(r['topics']),geography=r.get('geo'),language=r.get('lang','en'),description=r['desc'],access=r['access'],evidenceNote=r['evidence'],edition=r.get('edition'),rights=r.get('rights'),version=None,verifiedOn=VD,provenance=PASS,origin=origin,promotedFromCandidate=True,candidateIndex=cidx,added=VD))
    N[rid]=r['evidence']; return rid
# ---------- (1) retry list first
cidx_by_title={}
for i,c in enumerate(CAN):
    if c['status']=='retry': cidx_by_title[c['title']]=i
recs=P['recs']; rr=[r for r in recs if r['_origin'].startswith('retry-list')]; dr=[r for r in recs if not r['_origin'].startswith('retry-list')]
assert len(rr)+len(dr)==len(recs)
oq=P['openQueue']
prom_titles=set()
for r in rr:
    e=r['_retry']; ci=cidx_by_title[e['title']]
    rid=mk(r,'retry-list-'+PASS,[ci]); prom_titles.add(e['title'])
    c=CAN[ci]; c.update(status='promoted',promotedTo=rid,promotedOn=VD,previousStatus='retry',retryResolvedOn=VD,retryResolution=('promoted from the review/retry list (evidence recorded on the %s retry re-confirmed %s)'%(e.get('verifiedOn'),VD)) if e['retryOutcome']=='promotable' else ('promoted from the review/retry list: record opened on the %s retry via %s'%(VD,r['_route'])),lastTried=VD,attempts=(e.get('attempts') or 0)+(0 if e['retryOutcome']=='promotable' else 1))
MATCHED=[]
for x in P.get('matchedRetry',[]):
    ci=cidx_by_title[x['title']]; c=CAN[ci]; e=[e for e in RL if e['title']==x['title']][0]
    c.update(status='matched-verified',matchedTo=x['matchedTo'],matchedOn=VD,previousStatus='retry',retryResolvedOn=VD,retryResolution=x['reason'],lastTried=VD,attempts=(e.get('attempts') or 0)+1)
    prom_titles.add(x['title']); MATCHED.append(dict(title=x['title'],matchedTo=x['matchedTo']))
retry_first,retry_last=(out[0]['id'],out[-1]['id']) if out else (None,None)
nretryprom=len(out)
# ---------- remaining retry entries: updated attempt
RLn=[]
for e in RL:
    if e['title'] in prom_titles: continue
    upd=P['retryUpdates'].get(e['title']) or {}
    e=dict(e); e['lastTried']=VD; e['attempts']=(e.get('attempts') or 0)+1
    newu=[u for u in (upd.get('urlsTried') or []) if u not in e['urlsTried']]; e['urlsTried']=e['urlsTried']+newu
    lg=[x for x in (upd.get('log') or [])]
    e['retryLog']=(e.get('retryLog') or [])+[VD+': '+x for x in lg[-12:]]
    routes='OpenAlex locations, DOI (Crossref/DataCite/doi.org) where listed, direct https re-read, handle.net API targets, Wayback Machine, DOAJ API, DSpace 7 REST, Sikt NVA API, DiVA MODS export, theses.fr API, CiNii Research OpenSearch, Open Library, Crossref bibliographic search, Google Books API, Semantic Scholar; on 2026-11-26 also direct re-read with PDF text extraction, Wayback CDX capture lists (incl. other version suffixes of ksdot.gov documents), OpenAlex alternative-version search, J-STAGE search API, NDL Search, DNB and BnF catalogues (SRU), Internet Archive search, DataCite query search and Europe PMC'
    s2=[x for x in lg if x.startswith('semanticscholar: hit')]
    old=e['retryReason']; base=old.split(' Retried ')[0].split('. Retried ')[0]; prev=sorted(set(re.findall(r'2026-\d\d-\d\d',old[len(base):])+re.findall(r'Checked (2026-\d\d-\d\d)',base)))
    base=re.sub(r'\s*Checked 2026-\d\d-\d\d\.?$','',base); ds=prev+[VD]; dtxt=(', '.join(ds[:-1])+' and '+ds[-1]) if len(ds)>1 else ds[0]
    e['retryReason']=base.rstrip('.')+'. Retried %s via %s; still no inspectable record (attempt %d).%s'%(dtxt,routes,e['attempts'],' A Semantic Scholar entry matches the title but is an aggregator record without DOI/landing page, so it is not counted as inspection.' if s2 else '')+(' An aggregator record (%s) matches the title but has no openable record, so it is not counted as inspection.'%'; '.join(upd.get('agg') or []) if upd.get('agg') else '')
    e['retryOutcome']='still-unavailable'
    RLn.append(e)
    ci=cidx_by_title[e['title']]; c=CAN[ci]
    for k in ('lastTried','attempts','urlsTried','retryLog','retryReason','retryOutcome'): c[k]=e[k]
# ---------- (1b) open queue (49 KDOT/Kansas leads queued 2026-11-21): promoted by hand (oq_records.py) or moved to the review list
OQROWS=[]; TN0={t['id']:t['name'] for t in S['topics']}
for r in oq:
    ci=r['_cand_idx']; assert CAN[ci]['status']=='candidate' and CAN[ci]['title']==r['_cand'],ci
    rid=mk(r,'open-queue-'+PASS,[ci]); c=CAN[ci]; c.update(status='promoted',promotedTo=rid,promotedOn=VD,reviewedOn=VD,reviewPass=PASS); OQROWS.append(rid)
for x in P['openQueueRejected']:
    c=[c for c in CAN if c['status']=='candidate' and c['title']==x['title']][0]; c.update(status='rejected',rejectReason=x['reason'],rejectedOn=VD,reviewedOn=VD,reviewPass=PASS)
OQRET=[]
for x in P['openQueueRetry']:
    c=CAN[x['i']]; assert c['status']=='candidate'
    tp='dot'
    c.update(status='retry',reviewTopic=tp,reviewTopicName=TN0[tp],firstSeen=c.get('addedOn') or VD,lastTried=VD,attempts=1,urlsTried=x['urlsTried'],retryLog=[VD+': '+x['why']],
        retryReason='On-topic, real lead (KDOT/Kansas mix-design source queued %s; %s%s). Unavailable: %s. Checked %s.'%(c.get('addedOn') or VD,('named author(s) %s'%', '.join((c.get('authors') or [])[:2])) if c.get('authors') else 'no authors listed',('; dated %s'%c['year']) if c.get('year') else '',x['why'],VD),
        retryOutcome='still-unavailable',bestUrl=c.get('url'),reviewedOn=VD,reviewPass=PASS)
    OQRET.append(dict(c))
nprom_oq=len(OQROWS); noq_ret=len(OQRET)
# ---------- (2) new discovery records
k2id={}
for r in dr: k2id[r['_key']]=mk(r,'discovery-'+PASS)
oldN=len(CAN); newlead={}; nret=0; newretry=[]; rejn_d=[]
TN={t['id']:t['name'] for t in S['topics']}
for ld in P['leads']:
    k=ld.pop('_key'); ld['pass']=ld.pop('pass_')
    rt=ld.pop('_retry',None)
    if rt:
        ld['status']='retry'; nret+=1
        tp=ld['topic'] if ld['topic'] in TN else ld.pop('_rtopic',None)
        ld.pop('_rtopic',None)
        ld.update(reviewTopic=tp,reviewTopicName=TN.get(tp),firstSeen=VD,lastTried=VD,attempts=1,urlsTried=rt['urlsTried'],retryLog=rt.get('log') or [],
                  retryReason='On-topic, real lead (%s; %s%s). Unavailable: %s. Checked %s.'%(('OpenAlex record, query "%s"'%ld['query']),('named author(s) %s'%', '.join((ld['authors'] or [])[:2])) if ld.get('authors') else 'no authors listed',('; dated %s'%ld['year']) if ld.get('year') else '',rt['why'],VD),
                  retryOutcome='still-unavailable',bestUrl=ld.get('url') or (('https://doi.org/'+ld['doi']) if ld.get('doi') else None))
        newretry.append(ld)
    elif '_dup' in ld: ld.pop('_rtopic',None); ld.update(status='rejected',rejectReason=ld.pop('_dup'),rejectedOn=VD); rejn_d.append(ld['title'])
    elif k in k2id: ld.pop('_rtopic',None); ld.update(status='promoted',promotedTo=k2id[k],promotedOn=VD)
    else: raise SystemExit('lead without outcome: '+ld['title'])
    CAN.append(ld); newlead[k]=len(CAN)-1
i2k={v:k for k,v in k2id.items()}
for f in out:
    if f['id'] in i2k: f['candidateIndex']=[newlead[i2k[f['id']]]]
first,last=out[0]['id'],out[-1]['id']
disc_first=out[nretryprom+nprom_oq]['id'] if len(out)>nretryprom+nprom_oq else None
tmap={t['id']:t for t in S['topics']}; byid={r['id']:r for r in S['resources']}
for r in S['resources']:
    for t in r['topics']:
        if r['id'] not in tmap[t]['resourceIds']: tmap[t]['resourceIds'].append(r['id'])
for t in S['topics']:
    for i_ in t['resourceIds']:
        if t['id'] not in byid[i_]['topics']: byid[i_]['topics'].append(t['id'])
for r in S['resources'][:NBEFORE]: assert json.dumps(r,sort_keys=True)==before[r['id']],r['id']
assert not any(r['id']=='R428' for r in S['resources'])
n=len(out); ndisc=n-nretryprom-nprom_oq
tc=collections.Counter(t for r in out for t in r['topics']); acc=collections.Counter(r['access'] for r in out); langs=collections.Counter(r['language'] for r in out)
chase=[f['id'] for f in out if 'backward citation chase' in f['evidenceNote']]; fwd=[f['id'] for f in out if 'forward citation chase' in f['evidenceNote']]
cur=[f['id'] for f in out if (f['date'] or '').startswith('2026')]; noneng=[f['id'] for f in out if f['language']!='en']
focus=['concrete-architectural','concrete-pavement-pervious','concrete-precast-insitu-print','concrete-circular','concrete-repair-grout-overlay','standards','dot','carbon','fresh','strength','durability','scm','pavement']
TK=json.load(open(PD+'takeaways.json'))
for tid,txt in TK.items():
    ids=[f['id'] for f in out if tid in f['topics']]
    tmap[tid]['takeaways'].append(txt%('%s–%s, %d records'%(ids[0],ids[-1],len(ids)) if ids else 'none'))
rejn=len(rejn_d); nrej_oq=len(P['openQueueRejected']); nodoi=sum(1 for f in out if f['doi'] is None)
nleads=len(P['leads']); nleadprom=ndisc; assert nleads==nleadprom+nret+rejn
S['lastUpdated']=VD
nrl_start=125; rtitles='; '.join('%s "%s"'%(f['id'],f['title'][:90]) for f in out[:nretryprom])
FOCN='architectural concrete, concrete and pervious pavements, precast/3D-printed concrete, recycled/circular concrete, repair/overlays/grouts, standards, state DOT practice, carbon, fresh properties, strength, durability, SCMs and pavement'
NT=json.load(open(PD+'notes.json')); RNOTE=NT['retry']; NEXCL=9; NLIST=315+54
S['whatsNew'].insert(0,{'date':'Nov 26','title':'Daily pass: %d verified additions (%s–%s), %d from the review list'%(n,first,last,nretryprom),'detail':'Retry list first: all %d leads retried by new routes (PDF text extraction, Wayback capture lists incl. older ksdot.gov document versions, OpenAlex alternative versions, J-STAGE, NDL, DNB/BnF catalogues, Internet Archive); %d promoted (%s–%s): %s. %d leads stay on the review list (%d carried over, %d new from discovery). The open queue was empty. Discovery (OpenAlex backfill of %s, 15 language-filtered sweeps, citation chases and a current-awareness sweep of new publications through Nov 26) added %d verified sources, with %d records from backward and %d from forward citation chases, %d non-English records (English title glosses) and %d dated 2026. Mostly DOI/abstract or record-page level, not full-text reviews. Review list: https://xxdccole.github.io/Type1L-Index/review/'%(nrl_start,nretryprom,retry_first,retry_last,RNOTE,len(RLn)+nret,len(RLn),nret,FOCN,ndisc,len(chase),len(fwd),len(noneng),len(cur))})
S['changeLog'].append({'date':VD,'entry':'Daily pass 2026-11-26: %d verified additions %s–%s. Retry list first: %d leads retried, %d promoted (%s–%s), %d still unavailable (lastTried 2026-11-26, attempts +1). Open queue: empty at start. Discovery: %d new leads checked — %d promoted (%s–%s), %d qualified-but-unavailable added to the review list, %d rejected (%s), %d hits excluded at screening as off-topic, 0 left open. No corrections to existing records. R1–R4908 preserved (R428 still retired); topic membership union maintained; reactions table, calculator, prices and DOT QPL pages untouched.'%(n,first,last,nrl_start,nretryprom,retry_first,retry_last,len(RLn),nleads,nleadprom,disc_first,last,nret,rejn,('duplicate of R4298 / superseded BSI undated and series records' if rejn else 'none'),NEXCL)})
S['gaps'].insert(0,'Daily pass 2026-11-26: additions are registry/catalogue/record-page verified (%d abstract-level, %d DOI metadata only, %d record pages or PDFs read incl. Wayback copies, %d library catalogue records) — not full-text reviewed. Four KDOT special provisions were read from archived copies only; the versions currently linked from ksdot.gov answer HTTP 403, so later revisions may differ. %d qualified leads remain on the review list (research/review-retry.md; https://xxdccole.github.io/Type1L-Index/review/): mainly the KDOT PQL documents and remaining special provisions (no archive copy), TRID-only records, CNKI/CQVIP and J-GLOBAL records, Polish BazTech records, theses behind unreachable repositories and unregistered DOIs. Non-English additions carry title-level English glosses only. The Type IL/PLC-specific KDOT sources (PQL 5.1, SP 15-20001) remain unread.'%(acc['abstract_metadata'],acc['doi_metadata'],acc['landing_page_inspected'],acc['catalog_metadata'],len(RLn)+nret))
def wj(path,obj,indent=2):
    tmp=path+'.tmp'; json.dump(obj,open(tmp,'w'),indent=indent,ensure_ascii=False); os.replace(tmp,path)
def wl(path,rows):
    tmp=path+'.tmp'
    with open(tmp,'w') as f:
        for v in rows: f.write(json.dumps(v,ensure_ascii=False)+'\n')
    os.replace(tmp,path)
ids=[r['id'] for r in S['resources']]; assert len(ids)==len(set(ids))
urls=[r['url'].rstrip('/').lower() for r in S['resources']]; dupu=[u for u,c in collections.Counter(urls).items() if c>1]; assert not dupu,dupu
tt=[re.sub(r'\W+',' ',r['title'].lower()).strip() for r in S['resources']]; dupt=[u for u,c in collections.Counter(tt).items() if c>1 and u]; print('dup titles:',dupt[:5])
# retry lead URL must not equal an index URL
rset=set(urls)
for c in CAN:
    if c['status']=='retry': assert (c.get('url') or '').rstrip('/').lower() not in rset,c['url']
wj('site-data.json',S); wj('research/resource-notes.json',N)
VER+=out
wl('research/portable/verified-sources.jsonl',VER); wj('research/portable/verified-sources.json',VER,1)
wl('research/portable/candidates.jsonl',CAN); wj('research/portable/candidates.json',CAN,1)
wj(PD+'verified-%s-%s.json'%(first.lower(),last.lower()),out,1)
# ---------- review list
RLall=RLn+OQRET+newretry
for x in newretry:
    for k in ('sourceApi','query','cited_by','notes','addedOn','reviewedOn','reviewPass','pass','topic'): pass
wl('research/review-retry.jsonl',sorted(RLall,key=lambda x:(x.get('reviewTopicName') or '~',x['title'].lower())))
summ=dict(newRejectedDup=rejn,n=n,first=first,last=last,retryPromoted=nretryprom,retryPromotedRange='%s–%s'%(retry_first,retry_last),retryReconfirmed=sum(1 for r in rr if r['_retry']['retryOutcome']=='promotable'),retryOpenedToday=sum(1 for r in rr if r['_retry']['retryOutcome']!='promotable'),retryStill=len(RLn),retryNew=nret+noq_ret,retryNewDiscovery=nret,retryNewOpenQueue=noq_ret,openQueuePromoted=nprom_oq,retryTotal=len(RLall),newLeads=nleads,newPromoted=nleadprom,discoveryRange='%s–%s'%(disc_first,last),open=0,candStatus=dict(collections.Counter(c['status'] for c in CAN)),topics=dict(tc.most_common()),access=dict(acc),types=dict(collections.Counter(r['type'] for r in out)),decades=dict(sorted(collections.Counter(((r['date'] or '')[:3]+'0s') if r['date'] else 'undated' for r in out).items())),languages=dict(langs),citationChaseBackward=len(chase),citationChaseForward=len(fwd),current2026=len(cur),noDoiRecords=nodoi,total=len(S['resources']))
wj(PD+'apply-summary.json',summ,1); print(json.dumps(summ,ensure_ascii=False))
# ---------- ledger
SL=json.load(open(PD+'search-log.json')); SLC=json.load(open(PD+'search-log-b.json'))
for e_ in SL['log']: e_.setdefault('runDate',VD)
for e_ in SLC['log']: e_['runDate']=VD
SL['log']=SL['log']+SLC['log']; SL['skippedRepeats']=SL['skippedRepeats']+SLC['skippedRepeats']
PQ=json.load(open(PD+'prior-queries-all.json')); PQs={tuple(x) for x in PQ}
for e_ in SL['log']:
    k=[e_['topic'],e_['query'],e_.get('period'),e_.get('language')]
    if tuple(k) not in PQs: PQ.append(k); PQs.add(tuple(k))
json.dump(PQ,open(PD+'prior-queries-all.json','w'),ensure_ascii=False)
web=['Retry list (%d leads): direct re-read with PDF text extraction (pdftotext), Wayback CDX capture lists (filtered by document path; older ksdot.gov version suffixes), OpenAlex alternative-version search then Crossref/DataCite/location fetch, J-STAGE search API, NDL Search OpenSearch, DNB and BnF SRU catalogues, Internet Archive advanced search, DataCite query, Europe PMC (aggregator only, not counted as inspection)'%nrl_start,'No-DOI discovery hits: landing pages over https; failures re-tried via CiNii Research OpenSearch, Open Library, Wayback copies and BnF SRU','Not openable: ksdot.gov documents (403), TRID direct (no response), CNKI/CQVIP, J-GLOBAL, HathiTrust/CORE (403), WorldCat (client-side only), Library of Congress (timeouts/403), UGent biblio (bot redirect)']
rec=dict(id=PASS,date=VD,zone='America/Chicago',kind='daily-retry-list+discovery+lead-verification',focusTopics=focus+['retry list first (research/review-retry.jsonl, %d leads)'%nrl_start,'historical searches (13 searches with ≤1940–≤1985 period filters)','non-English literature (it, ru, tr, nl, cs, zh, es, de, fr, ja, pl, vi, sv, hu, ro language-filtered queries)','backward chase from %d existing DOI records in the 13 focus topics and forward chase from the 25 most-cited of them plus the 10 most-cited Nov 25 additions'%SL['chase']['seeds'],'current-awareness sweep (8 queries, publication dates from 2026-11-01/10/15/25 to 2026-11-26)'],currentAwareness=True,status='completed-unpublished (publisher to push)',
 note='All harvest queries, lead verification and retries ran on 2026-11-26 (America/Chicago). KDOT special provisions were read from archived Wayback copies of the same ksdot.gov document numbers (older version suffixes); edition caveats recorded.',
 repositories=['OpenAlex works API (title.search sorted by citations; relevance search for history and current awareness; language filter; referenced_works backward chase; cites: forward chase)','Crossref works API (per DOI and bibliographic search)','DataCite API','doi.org resolver','Wayback Machine CDX API + raw snapshots','CiNii Research OpenSearch','J-STAGE search API','NDL Search OpenSearch','DNB SRU','BnF SRU','Internet Archive advanced search/metadata','Open Library','Europe PMC (aggregator only)','OSTI ETDEWEB','TRID (archived record pages)','ACI abstracts portal','institutional repositories and journal sites (direct or Wayback)'],
 periods='1900–2026 (title.search all years; history searches ≤1940/≤1950/≤1960/≤1975/≤1980/≤1985; current sweeps with publication-date floors 2026-11-01/10/15/25, run 2026-11-26)',languages=sorted(langs),
 apiQueries=SL['log'],skippedRepeatQueries=SL['skippedRepeats'],webQueries=web,
 citationsFollowed=[dict(direction='backward',tool='OpenAlex referenced_works',seeds='existing DOI-bearing records in the 13 focus topics (%d seeds, %d found in OpenAlex; those dated <2006 expanded)'%(SL['chase']['seeds'],SL['chase']['seedsInOpenAlex']),referencesFound=SL['chase']['refs'],kept='cited by >=2 seeds or published <1990 (%d kept before dedupe; listing capped at 70)'%SL['chase']['backwardKept'],promoted=len(chase)),
   dict(direction='forward',tool='OpenAlex cites:',seeds='25 most-cited focus records + 10 most-cited Nov 25 additions (R4583–R4908): '+', '.join(x for x in SL['chase']['forwardSeeds'] if x),kept='top 6 citers ≤2010 + top 4 citers 2025–2026 per seed (%d kept; listing capped at 30)'%SL['chase']['forwardKept'],promoted=len(fwd))],
 triage='%d rows listed (315 from topic, history, current and chase searches with per-topic cap 10 and 40 current; 54 from the language sweep); 9 excluded at screening (reasons in select.py docstring); 275 DOI rows verified at Crossref/DataCite/doi.org and 85 no-DOI rows probed (landing page, then CiNii OpenSearch, Open Library, Wayback, BnF); see listing.txt, listing-b.txt, select.py in research/pass-2026-11-26/.'%NLIST,
 leadsProcessed=nleads,retryList=dict(start=nrl_start,promoted=nretryprom,promotedIds=[f['id'] for f in out[:nretryprom]],matchedToExisting=MATCHED,stillUnavailable=len(RLn),newlyAdded=nret,newFromDiscovery=nret,newFromOpenQueue=0,total=len(RLn)+nret),openQueue=dict(start=0,promoted=[],movedToRetry=0,rejected=[]),verifiedAdded=n,idRange='%s–%s'%(first,last),openLeadsAfterPass=sum(1 for c in CAN if c['status']=='candidate'),openLeads=[],
 verificationStatus=dict(acc),topicsTouched=dict(tc.most_common()),corrections=[],
 gaps=['Most journal items DOI-level only (Elsevier abstracts absent from Crossref/OpenAlex)','Non-English titles glossed from the title only','%d leads on the review list: KDOT PQL and remaining special-provision documents (403, no archive copy), TRID-only records, CNKI/CQVIP/J-GLOBAL articles, BazTech, theses on unreachable repositories, unregistered DOIs'%(len(RLn)+nret),'PLC/Type IL-specific coverage in KDOT specifications (PQL 5.1, SP 15-20001) still unread'],
 nextSteps=['Next rotation head (least-recently backfilled): see globalNextQueue head','Retry the review list again (KDOT PQL documents and SP 15-04003/15-11004/15-20001 via Wayback CDX if captures appear; TRID via Wayback; CNKI/CQVIP; BazTech)','Query PLC/Type IL terms inside TRID/NTL/state-DOT report repositories rather than OpenAlex title.search','Forward chase from Nov 26 additions','Check whether current KDOT special-provision revisions differ from the archived copies once ksdot.gov is reachable'],
 summary='Retry list first: %d promoted (%s–%s), %d still unavailable, %d new from discovery. Open queue: empty. %d new leads checked the same day: %d promoted, %d to the review list, 0 rejected after screening, 0 open. %d verified additions %s–%s.'%(nretryprom,retry_first,retry_last,len(RLn),nret,nleads,nleadprom,nret,n,first,last))
RJT=('%d rejected (duplicate of R4298; BSI undated and series records superseded by dated parts)'%rejn) if rejn else '0 rejected after screening'
rec['summary']=rec['summary'].replace('0 rejected after screening',RJT); rec['duplicatesRejected']=rejn_d
L['passes'].append(rec)
qby=collections.defaultdict(list)
for e_ in SL['log']:
    t=e_['topic']
    if t.startswith(('lang-','current')): continue
    qby[t].append(dict(tool='OpenAlex',query=(e_['query'] if e_['mode']=='search' else 'title.search:'+e_['query']),period=e_.get('period'),language=e_.get('language'),hits=e_['n'],date=VD,pass_=PASS))
for t in L['topics']:
    st=tmap[t['id']]; t['resourceIds']=list(st['resourceIds']); t['resourceCount']=len(st['resourceIds'])
    add=[r['id'] for r in out if t['id'] in r['topics']]
    if add: t['verifiedAdditions']=t.get('verifiedAdditions',[])+add; t['lastTouched']=VD
    if t['id'] in qby: t['searches']=t.get('searches',[])+[{('pass' if k=='pass_' else k):v for k,v in q.items()} for q in qby[t['id']]]
    if t['id'] in focus:
        t['passStatus']='daily_pass_2026-11-26_backfill'; t['lastDeepPass']=PASS
        t['nextSteps']=['Forward citation chase from 2026-11-26 additions','Look for open institutional/government reports, older proceedings and non-English literature','Avoid repeating 2026-11-12 to 2026-11-26 title.search queries (see ledger)']
q=L['globalNextQueue']; moved=[x for x in q if x['topicId'] in focus]; L['globalNextQueue']=[x for x in q if x['topicId'] not in focus]+[dict(x,reason='Backfilled in pass-2026-11-26; rotate to end') for x in moved]
nexthead=[x['topicId'] for x in L['globalNextQueue'][:13]]; rec['nextSteps'][0]='Next rotation head (least-recently backfilled): '+', '.join(nexthead); rec['nextRotationHead']=nexthead
L['updated']=VD; L['lastDeepPass']=PASS
L['stats']=dict(topics=59,resourcesAtStart=NBEFORE,resourcesAfterPass=len(S['resources']),verifiedAdded=n,candidatesTotal=len(CAN),candidatesOpen=sum(1 for c in CAN if c['status']=='candidate'),candidatesPromoted=sum(1 for c in CAN if c['status']=='promoted'),candidatesMatchedVerified=sum(1 for c in CAN if c['status']=='matched-verified'),candidatesRejected=sum(1 for c in CAN if c['status']=='rejected'),candidatesRetry=sum(1 for c in CAN if c['status']=='retry'),leadsProcessedThisPass=nleads,retryListPromotedThisPass=nretryprom,previous=L['stats'])
wj('research-ledger.json',L)
# ---------- index.md
md=open('index.md').read().split('\n')
assert md[1].startswith('Last updated: 2026-11-25')
md[1]='Last updated: 2026-11-26 (America/Chicago) — daily pass (%d verified additions: %d from the review list; open queue empty; no open leads). Daily research index; foundational coverage, not exhaustive. Historical records and gaps below are preserved; see expansion notes for current scope.'%(n,nretryprom)
o=['','## 2026-11-26 — daily pass (retry list first, open queue empty, discovery + same-day lead verification)',
'Step 1 — retry list (research/review-retry.jsonl, %d leads at start): %d promoted (%s–%s): %s. %d remain (lastTried 2026-11-26, attempts +1, URLs appended).'%(nrl_start,nretryprom,retry_first,retry_last,rtitles,len(RLn)),
'- Matched to an existing record instead of promoted: %s.'%('; '.join('"%s" → %s'%(m['title'],m['matchedTo']) for m in MATCHED) or 'none'),
'Step 2 — open queue: 0 open candidates at start; nothing to process.',
'Step 3 — discovery: OpenAlex title.search on the rotation head (%s) with new terms (repeats skipped), historical searches, language-filtered searches, backward/forward citation chases, and a current-awareness sweep of publications dated 2026-11-01 to 2026-11-26. %d leads checked the same day.'%(', '.join(focus),nleads),
'- Promoted: %d (%s–%s); qualified but unavailable → review list: %d; rejected: %d%s; excluded at screening: %d; open: 0.'%(nleadprom,disc_first,last,nret,rejn,(' (duplicate of R4298; BSI undated/series records superseded by dated parts)' if rejn else ''),NEXCL),
'- Evidence (all %d additions): abstract-level %d, DOI metadata only %d, record page read %d, catalogue %d. Nothing full-text reviewed.'%(n,acc['abstract_metadata'],acc['doi_metadata'],acc['landing_page_inspected'],acc['catalog_metadata']),
'- Citation chase: %d backward, %d forward; non-English: %d (descriptions are English title glosses); dated 2026: %d.'%(len(chase),len(fwd),len(noneng),len(cur)),
'- Review list now %d leads (research/review-retry.md; https://xxdccole.github.io/Type1L-Index/review/).'%len(RLall),
'- Corrections to existing records: none.','','### New verified resources (2026-11-26)']
for r in out:
    o.append(' | '.join([r['id'],','.join(r['topics']),r['title'],r['publisher'] or 'unknown',r['type'],r['date'] or 'undated',r['url']]))
    au=', '.join(a for a in (r['authors'] or []) if a) if r.get('authors') else 'unknown'
    o.append('  Note: Authors: %s. %s Access: %s. %s%s'%(au,r['description'],r['access'],r['evidenceNote'],(' Edition: '+r['edition']) if r.get('edition') else ''))
o+=['','### Open leads (2026-11-26)','- none','','### Added to the review list (2026-11-26)']+['- %s (%s) — %s'%(x['title'],x.get('year') or 'n.d.',x['retryReason'].split('Unavailable: ')[-1]) for x in OQRET+newretry]
open('index.md.tmp','w').write('\n'.join(md).rstrip('\n')+'\n'+'\n'.join(o)+'\n'); os.replace('index.md.tmp','index.md')
pg=[[r['id'],r['title'],r['publisher'] or '',r['type'],r['date'] or '',','.join(r['topics']),r['url']] for r in out]
json.dump(dict(rows=pg,news=S['whatsNew'][0],change=S['changeLog'][-1],gap=S['gaps'][0],total=len(S['resources']),summary=summ,takeaways={k:tmap[k]['takeaways'][-1] for k in TK}),open(PD+'page-d1126.json','w'),ensure_ascii=False,indent=0)
print('done',first,last,len(S['resources']))
