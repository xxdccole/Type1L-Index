"""pass-2026-11-20 apply: retry-list promotions + new verified records (R3561+) and lead outcomes into working files (atomic writes). Run once from pre-pass state
(backup in research/backups/pre-2026-11-20/). Derived from research/pass-2026-11-19/apply.py; adds the retry-list step and regenerates research/review-retry.jsonl/.md."""
import json,os,re,collections,copy
os.chdir('/workspace/type1l-index'); VD='2026-11-21'; PASS='pass-2026-11-21'; PD='research/pass-2026-11-21/'
P=json.load(open(PD+'plan.json'))
S=json.load(open('site-data.json')); L=json.load(open('research-ledger.json')); N=json.load(open('research/resource-notes.json'))
VER=[json.loads(l) for l in open('research/portable/verified-sources.jsonl')]
CAN=[json.loads(l) for l in open('research/portable/candidates.jsonl')]
RL=[json.loads(l) for l in open('research/review-retry.jsonl')]
NBEFORE=len(S['resources'])
assert NBEFORE==4044 and S['resources'][-1]['id']=='R4045' and S['lastUpdated']=='2026-11-20','expected pre-pass state'
assert not any(r['id']=='R428' for r in S['resources'])
OPEN=[i for i,c in enumerate(CAN) if c['status']=='candidate']; assert len(OPEN)==5,OPEN
assert sum(1 for c in CAN if c['status']=='retry')==61 and len(RL)==61
before={r['id']:json.dumps(r,sort_keys=True) for r in S['resources']}
out=[]; nxt=4046
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
    e['retryLog']=(e.get('retryLog') or [])+['2026-11-21: '+x for x in lg[-12:]]
    routes='OpenAlex locations, DOI (Crossref/DataCite/doi.org) where listed, direct https re-read, handle.net API targets, Wayback Machine, DOAJ API, DSpace 7 REST, Sikt NVA API, DiVA MODS export, theses.fr API, CiNii Research OpenSearch, Open Library, Crossref bibliographic search, Google Books API, Semantic Scholar'
    s2=[x for x in lg if x.startswith('semanticscholar: hit')]
    base=e['retryReason'].split(' Retried ')[0].split('. Retried ')[0]
    e['retryReason']=base.rstrip('.')+'. Retried 2026-11-19, 2026-11-20 and %s via %s; still no inspectable record (attempt %d).%s'%(VD,routes,e['attempts'],' A Semantic Scholar entry matches the title but is an aggregator record without DOI/landing page, so it is not counted as inspection.' if s2 else '')
    e['retryOutcome']='still-unavailable'
    RLn.append(e)
    ci=cidx_by_title[e['title']]; c=CAN[ci]
    for k in ('lastTried','attempts','urlsTried','retryLog','retryReason','retryOutcome'): c[k]=e[k]
# ---------- (1b) open queue (repo-added leads)
OQROWS=[]
for r in oq:
    ci=[i for i,c in enumerate(CAN) if c['status']=='candidate' and c['title']==r['_cand']][0]
    rid=mk(r,'open-queue-'+PASS,[ci]); c=CAN[ci]; c.update(status='promoted',promotedTo=rid,promotedOn=VD,reviewedOn=VD,reviewPass=PASS); OQROWS.append(rid)
for x in P['openQueueRejected']:
    c=[c for c in CAN if c['status']=='candidate' and c['title']==x['title']][0]; c.update(status='rejected',rejectReason=x['reason'],rejectedOn=VD,reviewedOn=VD,reviewPass=PASS)
assert not [c for c in CAN if c['status']=='candidate']
nprom_oq=len(OQROWS)
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
focus=['standards','dot','carbon','fresh','strength','durability','scm','pavement','apps','mix','field','supply','intl']
TK=json.load(open(PD+'takeaways.json'))
for tid,txt in TK.items():
    ids=[f['id'] for f in out if tid in f['topics']]
    tmap[tid]['takeaways'].append(txt%('%s–%s, %d records'%(ids[0],ids[-1],len(ids)) if ids else 'none'))
rejn=len(rejn_d); nrej_oq=len(P['openQueueRejected']); nodoi=sum(1 for f in out if f['doi'] is None)
nleads=len(P['leads']); nleadprom=ndisc; assert nleads==nleadprom+nret+rejn
S['lastUpdated']=VD
ROUTES_TXT='Wayback/direct record pages, CiNii Books, the Crossref DOI record and the NRC Publications Archive'
S['whatsNew'].insert(0,{'date':'Nov 21','title':'Daily pass: %d verified additions (%s–%s), %d from the review list and %d from the open queue'%(n,first,last,nretryprom,nprom_oq),'detail':'Retry list first: all 61 leads retried; %d promoted (%s–%s) — Litvan & Meyer on 20-year carbonation of slag-cement concrete (NRC Publications Archive record), the Refractory castable engineering book (CiNii Books) and Wille & Naaman 2013 on UHPC and brass-coated steel-fibre pullout (via its Crossref DOI, previously a J-GLOBAL lead). %d leads stay on the review list (%d carried over, %d new). Open queue: the 5 reaction-table source leads added to the repository on Nov 20 were checked — %d promoted (%s), %d reference-data pages rejected as not literature sources. Discovery then added %d verified sources for the rotation head — standards, DOT specifications, carbon, fresh properties, strength, durability, SCMs, pavements, applications, mix design, field practice, supply and international — with %d records from backward and %d from forward citation chases, %d non-English records (English glosses) and %d dated 2026. Mostly DOI/abstract or record-page level, not full-text reviews. Review list: https://xxdccole.github.io/Type1L-Index/review/'%(nretryprom,retry_first,retry_last,len(RLn)+nret,len(RLn),nret,nprom_oq,', '.join(OQROWS),nrej_oq,ndisc,len(chase),len(fwd),len(noneng),len(cur))})
S['changeLog'].append({'date':VD,'entry':'Daily pass 2026-11-21: %d verified additions %s–%s. Retry list first: 61 leads retried, %d promoted (%s–%s), %d still unavailable (lastTried 2026-11-21, attempts +1). Open queue: 5 repo-added leads (reactions table sources) — %d promoted (%s), %d rejected as reference-data pages. Discovery: %d new leads checked — %d promoted (%s–%s), %d qualified-but-unavailable added to the review list, 0 rejected after screening (11 hits excluded at screening as off-topic), 0 left open. No corrections to existing records. R1–R4045 preserved (R428 still retired); topic membership union maintained; reactions table, calculator and site pages untouched.'%(n,first,last,nretryprom,retry_first,retry_last,len(RLn),nprom_oq,', '.join(OQROWS),nrej_oq,nleads,nleadprom,disc_first,last,nret)})
S['gaps'].insert(0,'Daily pass 2026-11-21: additions are registry/catalogue/record-page verified (%d abstract-level, %d DOI metadata only, %d record pages read incl. Wayback copies, %d library catalogue records, %d public PDFs opened) — not full-text reviewed. %d qualified leads remain on the review list (research/review-retry.md; https://xxdccole.github.io/Type1L-Index/review/): mainly CNKI/CQVIP Chinese articles, TRID/ROSA records with no readable copy, Theseus (Cloudflare challenge), J-GLOBAL (HTTP 503), yadda/BazTech, ResearchGate-only items and unregistered ACI DOIs (10.14359/17603, 17608, 6418). Seven no-DOI hits were opened only through Open Library/CiNii catalogue records. The legacy Type IL topics (standards, dot, carbon, fresh, strength, durability, scm, pavement, apps, mix, field, supply, intl) were backfilled with general cement/concrete sources; PLC/Type IL-specific literature there is still thin.'%(acc['abstract_metadata'],acc['doi_metadata'],acc['landing_page_inspected'],acc['catalog_metadata'],acc['public_pdf_or_page'],len(RLn)+nret))
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
RLall=RLn+newretry
for x in newretry:
    for k in ('sourceApi','query','cited_by','notes','addedOn','reviewedOn','reviewPass','pass','topic'): pass
wl('research/review-retry.jsonl',sorted(RLall,key=lambda x:(x.get('reviewTopicName') or '~',x['title'].lower())))
summ=dict(newRejectedDup=rejn,n=n,first=first,last=last,retryPromoted=nretryprom,retryPromotedRange='%s–%s'%(retry_first,retry_last),retryReconfirmed=sum(1 for r in rr if r['_retry']['retryOutcome']=='promotable'),retryOpenedToday=sum(1 for r in rr if r['_retry']['retryOutcome']!='promotable'),retryStill=len(RLn),retryNew=nret,retryTotal=len(RLall),newLeads=nleads,newPromoted=nleadprom,discoveryRange='%s–%s'%(disc_first,last),open=0,candStatus=dict(collections.Counter(c['status'] for c in CAN)),topics=dict(tc.most_common()),access=dict(acc),types=dict(collections.Counter(r['type'] for r in out)),decades=dict(sorted(collections.Counter(((r['date'] or '')[:3]+'0s') if r['date'] else 'undated' for r in out).items())),languages=dict(langs),citationChaseBackward=len(chase),citationChaseForward=len(fwd),current2026=len(cur),noDoiRecords=nodoi,total=len(S['resources']))
wj(PD+'apply-summary.json',summ,1); print(json.dumps(summ,ensure_ascii=False))
# ---------- ledger
SL=json.load(open(PD+'search-log.json'))
web=['Retry list (61 leads): retried via OpenAlex locations, DOI (Crossref/DataCite/doi.org), direct https, handle.net API, Wayback, DOAJ API, DSpace 7 REST, Sikt NVA API, DiVA MODS, theses.fr API, CiNii OpenSearch, Open Library, Crossref bibliographic search, Google Books API, Semantic Scholar (aggregator hits recorded, not counted as inspection); J-GLOBAL lead resolved through OpenAlex W3000716741 -> Crossref DOI 10.14359/51685792','Open queue (5 repo-added leads): Crossref DOI records, NIST nvlpubs/tsapps PDFs; MDPI page answered 403','No-DOI discovery hits: landing pages over https; failures re-tried via Wayback copies, CiNii OpenSearch, Open Library','Not openable: CNKI/CQVIP, Theseus, J-GLOBAL (503), TRID/ROSA records without Wayback copies, ResearchGate']
rec=dict(id=PASS,date=VD,zone='America/Chicago',kind='daily-retry-list+open-queue+discovery+lead-verification',focusTopics=focus+['retry list first (research/review-retry.jsonl, 61 leads)','open queue: 5 repo-added reaction-table source leads','historical searches (specifications for portland cement, consistency tests, strength investigations, durability exposure tests, concrete roads, mix proportioning bulletins, construction practice, reinforced concrete textbooks)','non-English literature (es, pt, de, fr, ja, zh, ko, id, tr language-filtered title queries)','backward chase from %d existing DOI records in the 13 focus topics and forward chase from the 25 most-cited of them plus the 10 most-cited Nov 20 additions'%SL['chase']['seeds']],currentAwareness=True,status='completed-unpublished (publisher to push)',
 repositories=['OpenAlex works API (title.search sorted by citations; relevance search for history and current awareness; language filter; referenced_works backward chase; cites: forward chase)','Crossref works API (per DOI and bibliographic search)','DataCite API','doi.org resolver','Wayback Machine availability API + raw snapshots','CiNii Books / CiNii Research OpenSearch','Open Library','Google Books API','DOAJ API','DSpace 7 REST','Sikt NVA API','DiVA MODS export','Semantic Scholar Graph API','NRC Publications Archive, TU Delft repository, NIST publications, ACI abstracts portal, Dialnet/regional journal sites'],
 periods='1926–2026 (title.search all years; history searches ≤1950/≤1960/≤1970; current sweep 2026-10-01 → 2026-11-21)',languages=sorted(langs),
 apiQueries=SL['log'],skippedRepeatQueries=SL['skippedRepeats'],webQueries=web,
 citationsFollowed=[dict(direction='backward',tool='OpenAlex referenced_works',seeds='existing DOI-bearing records in the 13 focus topics (%d seeds, %d found in OpenAlex; those dated <2006 expanded)'%(SL['chase']['seeds'],SL['chase']['seedsInOpenAlex']),referencesFound=SL['chase']['refs'],kept='cited by >=2 seeds or published <1990 (%d kept before dedupe; listing capped at 70)'%SL['chase']['backwardKept'],promoted=len(chase)),
   dict(direction='forward',tool='OpenAlex cites:',seeds='25 most-cited focus records + 10 most-cited Nov 20 additions: '+', '.join(x for x in SL['chase']['forwardSeeds'] if x),kept='top 6 citers ≤2010 + top 4 citers 2025–2026 per seed (%d kept; listing capped at 30)'%SL['chase']['forwardKept'],promoted=len(fwd))],
 triage='273 rows listed (per-topic cap 8; 6 per language; 30 current; 70 backward and 30 forward chase) plus the J-GLOBAL/Crossref lead; 11 excluded at screening (road-surface aggregate geology x2, drainage of pavements, a general pavement-design textbook, statue AR case study, rock-mass geothermal heat transfer, dolostone cap geology, wood-stove design, green supply-chain/PAH-soil/cap-and-tax items); see research/pass-2026-11-21/listing.txt and select.py.',
 leadsProcessed=nleads,retryList=dict(start=61,promoted=nretryprom,stillUnavailable=len(RLn),newlyAdded=nret,total=len(RLall)),openQueue=dict(start=5,promoted=OQROWS,rejected=[x['title'] for x in P['openQueueRejected']]),verifiedAdded=n,idRange='%s–%s'%(first,last),openLeadsAfterPass=sum(1 for c in CAN if c['status']=='candidate'),openLeads=[],
 verificationStatus=dict(acc),topicsTouched=dict(tc.most_common()),corrections=[],
 gaps=['Most journal items DOI-level only (Elsevier abstracts absent from Crossref/OpenAlex)','Non-English titles glossed from title/abstract only','%d leads on the review list: CNKI/CQVIP articles, TRID/ROSA records without readable copies, Theseus (Cloudflare), J-GLOBAL (503), yadda/BazTech, ResearchGate-only, unregistered ACI DOIs'%len(RLall),'PLC/Type IL-specific coverage in the legacy topics (standards, dot, carbon, fresh, strength, durability, scm, pavement, apps, mix, field, supply, intl) remains thin; additions are mostly general cement/concrete literature','Bentz et al. 2009 (Concrete International) has no DOI found'],
 nextSteps=['Next rotation head (least-recently backfilled): see globalNextQueue head','Retry the review list again (CNKI/CQVIP via open mirrors; TRID via Wayback as snapshots appear; Theseus via finna.fi records)','Query PLC/Type IL terms inside TRID/NTL/state-DOT report repositories rather than OpenAlex title.search','Forward chase from Nov 21 additions'],
 summary='Retry list first: %d promoted (%s–%s), %d still unavailable, %d new. Open queue: %d promoted, %d rejected. %d new leads checked the same day: %d promoted, %d to the review list, 0 rejected after screening, 0 open. %d verified additions %s–%s.'%(nretryprom,retry_first,retry_last,len(RLn),nret,nprom_oq,nrej_oq,nleads,nleadprom,nret,n,first,last))
RJT=('%d rejected as duplicates of leads already on the review list'%rejn) if rejn else '0 rejected after screening'
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
        t['passStatus']='daily_pass_2026-11-21_backfill'; t['lastDeepPass']=PASS
        t['nextSteps']=['Forward citation chase from 2026-11-21 additions','Look for open institutional/government reports, older proceedings and non-English literature','Avoid repeating 2026-11-12 to 2026-11-21 title.search queries (see ledger)']
q=L['globalNextQueue']; moved=[x for x in q if x['topicId'] in focus]; L['globalNextQueue']=[x for x in q if x['topicId'] not in focus]+[dict(x,reason='Backfilled in pass-2026-11-21; rotate to end') for x in moved]
nexthead=[x['topicId'] for x in L['globalNextQueue'][:13]]; rec['nextSteps'][0]='Next rotation head (least-recently backfilled): '+', '.join(nexthead); rec['nextRotationHead']=nexthead
L['updated']=VD; L['lastDeepPass']=PASS
L['stats']=dict(topics=59,resourcesAtStart=NBEFORE,resourcesAfterPass=len(S['resources']),verifiedAdded=n,candidatesTotal=len(CAN),candidatesOpen=sum(1 for c in CAN if c['status']=='candidate'),candidatesPromoted=sum(1 for c in CAN if c['status']=='promoted'),candidatesMatchedVerified=sum(1 for c in CAN if c['status']=='matched-verified'),candidatesRejected=sum(1 for c in CAN if c['status']=='rejected'),candidatesRetry=sum(1 for c in CAN if c['status']=='retry'),leadsProcessedThisPass=nleads,retryListPromotedThisPass=nretryprom,previous=L['stats'])
wj('research-ledger.json',L)
# ---------- index.md
md=open('index.md').read().split('\n')
assert md[1].startswith('Last updated: 2026-11-20')
md[1]='Last updated: 2026-11-21 (America/Chicago) — daily pass (%d verified additions: %d from the review list, %d from the open queue; no open leads). Daily research index; foundational coverage, not exhaustive. Historical records and gaps below are preserved; see expansion notes for current scope.'%(n,nretryprom,nprom_oq)
o=['','## 2026-11-21 — daily pass (retry list first, then open queue, discovery + same-day lead verification)',
'Step 1 — retry list (research/review-retry.jsonl, 61 leads at start): %d promoted (%s–%s): the NRC Publications Archive record of Litvan & Meyer (20-year carbonation of slag-cement concrete), the CiNii Books record of Refractory castable engineering, and Wille & Naaman 2013 (UHPC / brass-coated steel fibre pullout, ACI Mater. J., DOI 10.14359/51685792 verified in Crossref; was a J-GLOBAL lead). %d remain (lastTried 2026-11-21, attempts +1, URLs appended).'%(nretryprom,retry_first,retry_last,len(RLn)),
'Step 2 — open queue (5 leads appended to research/candidates.jsonl by the 2026-11-20 reactions-table commit): %d promoted (%s: NIST CEMHYD3D manual, Bentz et al. limestone-fillers article, Leon & Chen slag mass-concrete paper); %d rejected (NIST Chemistry WebBook CO2 entry and IUPAC CIAAW atomic weights are reference-data pages, not literature; they stay cited in research/reactions.md).'%(nprom_oq,', '.join(OQROWS),nrej_oq),
'Step 3 — discovery: OpenAlex title.search on the rotation head (standards, dot, carbon, fresh, strength, durability, scm, pavement, apps, mix, field, supply, intl) with new terms (repeats skipped), historical searches, language-filtered searches, a current-awareness sweep to 2026-11-21, backward/forward citation chases. %d leads checked the same day.'%nleads,
'- Promoted: %d (%s–%s); qualified but unavailable → review list: %d; rejected after screening: 0 (11 excluded at screening); open: 0.'%(nleadprom,disc_first,last,nret),
'- Evidence (all %d additions): abstract-level %d, DOI metadata only %d, record page read %d, catalogue %d, public PDF opened %d. Nothing full-text reviewed.'%(n,acc['abstract_metadata'],acc['doi_metadata'],acc['landing_page_inspected'],acc['catalog_metadata'],acc['public_pdf_or_page']),
'- Citation chase: %d backward, %d forward; non-English: %d (descriptions are English glosses where available); dated 2026: %d.'%(len(chase),len(fwd),len(noneng),len(cur)),
'- Review list now %d leads (research/review-retry.md; https://xxdccole.github.io/Type1L-Index/review/).'%len(RLall),
'- Corrections to existing records: none.','','### New verified resources (2026-11-21)']
for r in out:
    o.append(' | '.join([r['id'],','.join(r['topics']),r['title'],r['publisher'] or 'unknown',r['type'],r['date'] or 'undated',r['url']]))
    au=', '.join(a for a in (r['authors'] or []) if a) if r.get('authors') else 'unknown'
    o.append('  Note: Authors: %s. %s Access: %s. %s%s'%(au,r['description'],r['access'],r['evidenceNote'],(' Edition: '+r['edition']) if r.get('edition') else ''))
o+=['','### Open leads (2026-11-21)','- none','','### Added to the review list (2026-11-21)']+['- %s (%s) — %s'%(x['title'],x.get('year') or 'n.d.',x['retryReason'].split('Unavailable: ')[-1]) for x in newretry]
open('index.md.tmp','w').write('\n'.join(md).rstrip('\n')+'\n'+'\n'.join(o)+'\n'); os.replace('index.md.tmp','index.md')
pg=[[r['id'],r['title'],r['publisher'] or '',r['type'],r['date'] or '',','.join(r['topics']),r['url']] for r in out]
json.dump(dict(rows=pg,news=S['whatsNew'][0],change=S['changeLog'][-1],gap=S['gaps'][0],total=len(S['resources']),summary=summ,takeaways={k:tmap[k]['takeaways'][-1] for k in TK}),open(PD+'page-d1121.json','w'),ensure_ascii=False,indent=0)
print('done',first,last,len(S['resources']))
