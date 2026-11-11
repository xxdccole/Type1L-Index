"""pass-2026-11-11 apply: old-lead outcomes + new verified records R1477+ into working files (atomic writes). Run once from pre-pass state."""
import json,os,re,collections
os.chdir('/workspace/type1l-index'); VD='2026-11-11'; PASS='pass-2026-11-11'; PD='research/pass-2026-11-11/'
P=json.load(open(PD+'plan.json'))
GL={'https://doi.org/10.3151/coj1975.27.5_22':('ja','Japanese-language state-of-the-art report on roller-compacted concrete (RCC) pavements: RCC is described as an extension of soil-cement stabilization, using very stiff, low-water concrete compacted by vibratory rollers for pavement slabs and bases; strong compaction lets the pavement carry wheel loads right after placing (early opening to traffic). Notes active trial construction in Japan and summarizes status and issues. (English gloss of the Japanese abstract.)'),
 'https://doi.org/10.4334/jkci.2026.38.2.191':('ko','Korean-language study analysing industry opinion on establishing a Korean Portland-limestone cement (PLC) standard to cut cement-industry CO2: a survey of 337 cement/concrete experts on the need for a standard, limestone quality (CaCO3 purity, clay content, TOC, fineness), allowable limestone content, strength classes/grading criteria and required physical/chemical properties. (English gloss of the Korean abstract; results not reviewed.)')}
for r in P['recs']:
    if r['_key'] in GL: r['lang'],r['desc']=GL[r['_key']]; r['evidence']+=' Abstract is not in English; description is an English gloss.'
S=json.load(open('site-data.json')); L=json.load(open('research-ledger.json')); N=json.load(open('research/resource-notes.json'))
VER=[json.loads(l) for l in open('research/portable/verified-sources.jsonl')]
CAN=[json.loads(l) for l in open('research/portable/candidates.jsonl')]
assert len(S['resources'])==1475 and S['resources'][-1]['id']=='R1476' and S['lastUpdated']=='2026-11-10','expected pre-pass state'
before={r['id']:json.dumps(r,sort_keys=True) for r in S['resources']}
# ---------- STEP 1: the 4 open leads
OLD=[
 (1013,dict(title='Theory and Experiments on the Mechanical Behaviour of Cracks in Plain and Reinforced Concrete Subjected to Shear Loading',authors=['J. C. Walraven','H. W. Reinhardt'],publisher='Delft University of Technology (HERON)',type='Paper',date='1981',url='http://resolver.tudelft.nl/uuid:3d68bd1a-465d-4590-b33c-7ede99bbc251',doi=None,ids={'journal':'HERON 26(1A):1–68','openalex':'W2146241768','tudelftUuid':'3d68bd1a-465d-4590-b33c-7ede99bbc251'},topics=['concrete-structural','cross-mechanics','concrete-lightweight'],geo='Netherlands',lang='en',
   desc='Experiments on precracked shear specimens and a theoretical model for shear transfer across cracks by aggregate interlock and reinforcement dowel action; variables included bar type, concrete strength (13–60 N/mm²), gravel vs lightweight concrete, grading, maximum aggregate size (16/32 mm) and initial crack width.',
   access='catalog_metadata',evidence='Resolved open lead (TU Delft timeout on 2026-11-10). 2026-11-11: TU Delft repository record content (journal article, 1981, authors, "Source: HERON, 26 (1A), 1981") read via search-index copy — direct fetch still timed out (WebFetch 504); OpenAlex W2146241768 abstract text inspected; pages 1–68 from the PCI Journal 2016 reference list. PDF not reviewed.')),
 (1247,dict(title='Densified Cement/Ultra-Fine Particle-Based Materials (Bache, 1981)',authors=['H. H. Bache'],publisher='Aalborg Portland, Cement- og Betonlaboratoriet (CBL Report 40)',type='Conference paper',date='1981',url='https://www.osti.gov/etdeweb/biblio/10168064',doi=None,ids={'report':'CBL-40; CONF-8106349-1','isbn':'87-89132-00-9','ntis':'DE93500154','etdeweb':'10168064','conference':'2nd International Conference on Superplasticizers in Concrete, Ottawa, 10–12 June 1981'},topics=['concrete-hpc','scm-silica','cross-mix','concrete-fibers'],geo='Denmark',lang='en',
   desc='Founding DSP paper: binders of densely packed cement with ultra-fine particles in the interstices, made workable at w/(c+fines) 0.13–0.18 with large superplasticizer doses, giving 120–270 MPa and high durability; discusses packing principles, dispersants and composites adding tensile strength/ductility (e.g. fibres).',
   access='landing_page_inspected',evidence='Resolved open lead (CiNii 500 on 2026-11-10). 2026-11-11: OSTI ETDEWEB record 10168064 read (abstract, author, 1981, report CBL-40, ISBN, conference, 35 p.); NTIS record DE93500154 seen via search index. Paper text not reviewed.')),
 (1264,dict(title='Aggregates from Waste Materials (Gutt, 1972)',authors=['W. Gutt'],publisher='Chemistry and Industry (journal)',type='Paper',date='1972',url='https://trid.trb.org/view/106168',doi=None,ids={'journal':'Chemistry and Industry, no. 11 (1972), pp. 439–447 (per Buck 1976 reference list)','trid':'106168'},topics=['concrete-circular','cross-mix'],geo='UK',lang='en',
   desc='Article by W. Gutt (UK Building Research Establishment) on producing aggregates from waste materials; cited by Buck (1976) in the US Army WES recycled-concrete-aggregate review. Metadata-level record — content not reviewed.',
   access='catalog_metadata',evidence='Resolved open lead (TRID 503 on 2026-11-10). 2026-11-11: TRID record 106168 (title, W. Gutt, 1972-08-01) seen via search index — direct TRID fetch timed out; bibliographic details from the reference list of ERDC MP C-76-2 (Buck 1976, PDF text via search index) and the Royal Society 1974 "Aggregates in Britain" reference list. Month differs between sources (June vs Aug 1972), so only the year is given. Article text not reviewed.')),
]
NIB=1263
k2id={}; out=[]; nxt=1477
def mk(r,origin,cidx=None):
    global nxt
    rid='R%d'%nxt; nxt+=1
    S['resources'].append({'id':rid,'title':r['title'],'publisher':r['publisher'],'type':r['type'],'date':r['date'],'url':r['url'],'topics':list(r['topics'])})
    full=dict(id=rid,status='verified',title=r['title'],authors=r.get('authors'),publisher=r['publisher'],type=r['type'],date=r['date'],url=r['url'],doi=r.get('doi'),identifiers=r.get('ids') or {},topics=list(r['topics']),geography=r.get('geo'),language=r.get('lang','en'),description=r['desc'],access=r['access'],evidenceNote=r['evidence'],edition=r.get('edition'),rights=r.get('rights'),version=None,verifiedOn=VD,provenance=PASS,origin=origin,promotedFromCandidate=True,candidateIndex=cidx,added=VD)
    out.append(full); N[rid]=r['evidence']; return rid
oldout={}
for i,r in OLD:
    rid=mk(r,'candidate-queue',[i]); x=CAN[i]; assert x['status']=='candidate'
    x.update(status='promoted',promotedTo=rid,promotedOn=VD,reviewedOn=VD,reviewPass=PASS); x.pop('openReason',None); x['lastCheckedOn']=VD; oldout[i]=('promoted',rid)
x=CAN[NIB]; assert x['status']=='candidate'
x.update(status='rejected',rejectCategory='off-topic',rejectReason='off-topic: identity confirmed 2026-11-11 (A. A. B. Musannif, BRE Current Paper CP 83/74, Sept 1974; TRID 22439 and BRE archive listing via search index) — it describes a quiet concrete-breaking attachment for hydraulic excavators (equipment/noise), not concrete materials, recycling performance or engineering behaviour.',reviewedOn=VD,reviewPass=PASS,lastCheckedOn=VD); x.pop('openReason',None); oldout[NIB]=('rejected','off-topic')
# ---------- STEP 2: new verified records
oldN=len(CAN)
for r in P['recs']:
    rid=mk(r,'discovery-'+PASS,None); k2id[r['_key']]=rid
    out[-1]['candidateIndex']=None
# new leads -> candidates with outcomes
newlead={}
for ld in P['leads']:
    k=ld.pop('_key'); ld['pass']=ld.pop('pass_')
    if k in k2id: ld.update(status='promoted',promotedTo=k2id[k],promotedOn=VD)
    else:
        cat,reason,dup=P['rejected'][k]
        if dup.startswith('(this pass'):
            dup=k2id['https://doi.org/10.3403/00047536']; reason=reason.replace('promoted in this pass','promoted in this pass as '+dup)
        ld.update(status='rejected',rejectCategory=cat,rejectReason=reason,duplicateOf=dup)
    CAN.append(ld); newlead[k]=len(CAN)-1
for f in out:
    if f['origin'].startswith('discovery'):
        k=[kk for kk,v in k2id.items() if v==f['id']][0]; f['candidateIndex']=[newlead[k]]
first,last=out[0]['id'],out[-1]['id']
# ---------- membership union
tmap={t['id']:t for t in S['topics']}; byid={r['id']:r for r in S['resources']}
for r in S['resources']:
    for t in r['topics']:
        if r['id'] not in tmap[t]['resourceIds']: tmap[t]['resourceIds'].append(r['id'])
for t in S['topics']:
    for i in t['resourceIds']:
        if t['id'] not in byid[i]['topics']: byid[i]['topics'].append(t['id'])
for r in S['resources'][:1475]: assert json.dumps(r,sort_keys=True)==before[r['id']],r['id']
n=len(out); nnew=n-3
tc=collections.Counter(t for r in out for t in r['topics'])
acc=collections.Counter(r['access'] for r in out)
rejn=sum(1 for c in CAN[oldN:] if c['status']=='rejected')
# ---------- narrative
S['lastUpdated']=VD
S['whatsNew'].insert(0,{'date':'Nov 11','title':'Daily pass: %d verified additions; old lead queue cleared'%n,'detail':'Resolved the 4 leads left open on Nov 10 (Walraven & Reinhardt 1981 HERON shear-crack study, Bache 1981 DSP paper and Gutt 1972 aggregates-from-waste promoted; the 1974 BRE "Nibbler" demolition-equipment note rejected as off-topic). Discovery added %d verified sources (%s–%s overall range) focused on the thinnest topics — cellular/foamed and autoclaved aerated concrete, heavyweight/radiation-shielding concrete, mass concrete and RCC, oil-well/geothermal cements, expansive/rapid-hardening cements, lime/cement mortars and plaster, CEM II/III blast-furnace cements, shotcrete, natural pozzolans, failures/forensic case studies and cement-industry supply/emissions — plus a Portland-limestone cement backfill and a Sept–Nov 2026 current-awareness sweep (incl. ASTM C1697-26 and C926-26 catalogue records). %d new leads rejected as duplicates/superseded editions. Mostly DOI/abstract-level, not full-text reviews.'%(nnew,first,last,rejn)})
S['changeLog'].append({'date':VD,'entry':'Daily pass 2026-11-11: %d verified additions %s–%s (3 promoted from the 4 previously open leads; %d from new discovery). Nibbler lead rejected (off-topic). %d newly found leads rejected (duplicate/superseded editions of R178, R828, R111 and an older BSI edition). No open leads remain. R1–R1476 preserved; topic membership union maintained.'%(n,first,last,nnew,rejn)})
S['gaps'].insert(0,'Daily pass 2026-11-11: candidate queue is empty (0 open). New additions are registry/catalogue-verified (%d abstract-level, %d DOI metadata only, %d catalogue records, %d landing pages read) — not full-text reviewed. Citation chasing was not done this pass; thin topics remain cross-supply-region (regional cement/aggregate market data beyond emissions papers), RCC dam construction practice reports (USACE/USBR), and non-English national cement standards (JIS, GB, IS) — Japanese/Chinese standards bodies not reachable via Crossref.'%(acc['abstract_metadata'],acc['doi_metadata'],acc['catalog_metadata'],acc['landing_page_inspected']))
def wj(path,obj,indent=2):
    tmp=path+'.tmp'; json.dump(obj,open(tmp,'w'),indent=indent,ensure_ascii=False); os.replace(tmp,path)
ids=[r['id'] for r in S['resources']]; assert len(ids)==len(set(ids))
urls=[r['url'].rstrip('/').lower() for r in S['resources']]; dupu=[u for u,c in collections.Counter(urls).items() if c>1]; assert not dupu,dupu
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
summ=dict(n=n,first=first,last=last,oldLeads={str(k):v for k,v in oldout.items()},newLeads=len(P['leads']),newPromoted=nnew,newRejected=rejn,candStatus=dict(collections.Counter(c['status'] for c in CAN)),topics=dict(tc.most_common()),access=dict(acc),types=dict(collections.Counter(r['type'] for r in out)),decades=dict(sorted(collections.Counter(((r['date'] or '')[:3]+'0s') if r['date'] else 'undated' for r in out).items())),languages=dict(collections.Counter(r['language'] for r in out)))
wj(PD+'apply-summary.json',summ,1); print(json.dumps(summ,ensure_ascii=False))
# ---------- ledger
s1=json.load(open(PD+'search-log.json')); s2=json.load(open(PD+'search-log2.json'))
focus=['cross-supply-region','concrete-mass-rcc','concrete-cellular','concrete-heavyweight','cross-failure-repair','binder-specialty','binder-white-masonry','binder-international','binder-well','scm-natural','concrete-shotcrete','scm-limestone']
web=['WebSearch/WebFetch: Walraven Reinhardt 1981 HERON (TU Delft)','WebSearch/WebFetch: Bache 1981 densified cement (OSTI ETDEWEB)','WebSearch: Nibbler concrete breaking 1974 (TRID/BRE)','WebSearch: Aggregates from waste materials 1972 (TRID/ERDC)','WebSearch: ACI 223R-10 / PRC-223-21','WebSearch: Ribar Scanlon 1984 plaster (DTIC/ERDC)','WebSearch: Londe Lino 1992 FSHD','WebSearch: Wittmann 1992 AAC proceedings','WebSearch: Morgan Wolsiefer silica fume shotcrete','WebSearch: Saricimen 1987 sewerage','WebSearch/WebFetch: Toward a Sustainable Cement Industry substudy 8 (OSTI)','WebSearch: Baron Douvre 1987 limestone filler','WebSearch: ACI 325.10R-95','WebSearch: CEM II/CEM III/A Zemente 2008 (TRID)','WebSearch: ACI PRC-223-21','curl: CiNii Books BA8570960X, BA21028963, BA06992924, BA16712194; ACI abstracts portal 11125; geopolymer.org Davidovits 1994 PDF','WebFetch: ROSA P dot/40309']
rec=dict(id=PASS,date=VD,zone='America/Chicago',kind='daily-discovery+lead-verification',focusTopics=focus+['Type IL collection topics via Portland-limestone cement backfill (durability, strength, scm, intl, carbon, standards, apps)'],currentAwareness=True,status='completed-unpublished (publisher to push)',
 repositories=['OpenAlex works API (fulltext search sorted by citations / relevance; title.search filter with period splits)','Crossref works API (per-DOI; no bibliographic search used)','DataCite API (Zenodo, UVA Libra)','doi.org resolver (HEAD)','OSTI ETDEWEB','ROSA P / NTL','CiNii Books','ACI International Concrete Abstracts Portal','TRID (unreachable directly; records via search index)','TU Delft repository (unreachable directly; record via search index)','DTIC/ERDC (403; via search index)','National Library of Australia catalogue (via search index)','Pascal-Francis (via search index)','Geopolymer Institute author copy'],
 periods='1912–2026 (title.search queries split into pre-2000/2000s/post-2005 windows; current sweep 2026-01 → 2026-11-11, mostly ≥2026-06)',languages=sorted(summ['languages']),
 apiQueries=[dict(e,harvest='harvest1') for e in s1]+[dict(e,harvest='harvest2-titlesearch') for e in s2],webQueries=web,
 citationsFollowed=[],citationNote='No backward/forward citation chase this pass (time spent on title.search backfill and no-DOI verification). Buck (1976) and PCI Journal reference lists were used only to confirm old-lead bibliographic details.',
 uniqueApiHits=dict(harvest1=904,harvest2=1209,newAfterDedupe=840+1154),triage='Hits were screened by title/abstract; %d selected as leads (all verified this pass). Screened-out hits (off-topic noise from citation-sorted search, near-duplicate modern studies, dental/medical "cement", energy-market "aggregators") were not queued as leads — see research/pass-2026-11-11/triage.json.'%len(P['leads']),
 leadsProcessed=4+len(P['leads']),oldLeadOutcomes={str(k):v for k,v in oldout.items()},verifiedAdded=n,idRange='%s–%s'%(first,last),newLeadsRejected=rejn,openLeadsAfterPass=sum(1 for c in CAN if c['status']=='candidate'),
 verificationStatus=dict(acc),topicsTouched=dict(tc.most_common()),corrections=[],
 gaps=['No citation chasing this pass','Most journal items DOI-level only (Elsevier abstracts absent from OpenAlex/Crossref)','ACI committee-report designations inferred from title/venue/year not confirmed (e.g. Roller Compacted Mass Concrete 1988; Preplaced Aggregate Concrete guide 1992)','BSI ordinary/rapid-hardening Portland cement record lacks designation and edition year in Crossref','TRID, TU Delft, DTIC, J-GLOBAL, SID unreachable directly'],
 nextSteps=['Next rotation head: cross-durability, cross-tests-codes, cross-environment-cost, standards, dot, carbon, fresh, strength (legacy Type IL topics need PLC-specific sources)','Citation chase from today\'s historical seeds (Robson 1962 HAC, ACI 325.10R-95, Callan 1953 shielding, Valore 1954 cellular concretes, Bache 1981)','Seek USACE/USBR RCC dam manuals and EM 1110-2 series via legal open repositories','Search regional cement market/supply data (USGS Mineral Commodity Summaries editions, CEMBUREAU, GCCA) for cross-supply-region'],
 summary='Old queue cleared (3 promoted, 1 rejected). %d new leads found and all verified the same day: %d promoted, %d rejected. %d verified additions %s–%s.'%(len(P['leads']),nnew,rejn,n,first,last))
L['passes'].append(rec)
tm={t['id']:t for t in S['topics']}
qby=collections.defaultdict(list)
for e in s1+s2:
    t=e['topic']; t={'pll-mix':'scm-limestone','current-2026':None}.get(t,t)
    if t: qby[t].append(dict(tool='OpenAlex',query=e.get('query') or ('title.search:'+e.get('titleSearch','')),period=e.get('period') or e.get('to') ,hits=e['n'],date=VD,pass_=PASS))
for t in L['topics']:
    st=tm[t['id']]; t['resourceIds']=list(st['resourceIds']); t['resourceCount']=len(st['resourceIds'])
    add=[r['id'] for r in out if t['id'] in r['topics']]
    if add:
        t['verifiedAdditions']=t.get('verifiedAdditions',[])+add; t['lastTouched']=VD
    if t['id'] in qby:
        t['searches']=t.get('searches',[])+[{('pass' if k=='pass_' else k):v for k,v in q.items()} for q in qby[t['id']]]
    if t['id'] in focus:
        t['passStatus']='daily_pass_2026-11-11_backfill'; t['lastDeepPass']=PASS
        t['nextSteps']=['Citation chase from 2026-11-11 seeds','Look for open institutional/government reports and older proceedings','Avoid repeating 2026-11-11 title.search queries (see ledger)']
q=L['globalNextQueue']; moved=[x for x in q if x['topicId'] in focus]; L['globalNextQueue']=[x for x in q if x['topicId'] not in focus]+[dict(x,reason='Backfilled in pass-2026-11-11; rotate to end') for x in moved]
L['updated']=VD; L['lastDeepPass']=PASS
L['stats']=dict(topics=59,resourcesAtStart=1475,resourcesAfterPass=len(S['resources']),verifiedAdded=n,candidatesTotal=len(CAN),candidatesOpen=sum(1 for c in CAN if c['status']=='candidate'),candidatesPromoted=sum(1 for c in CAN if c['status']=='promoted'),candidatesMatchedVerified=sum(1 for c in CAN if c['status']=='matched-verified'),candidatesRejected=sum(1 for c in CAN if c['status']=='rejected'),leadsProcessedThisPass=4+len(P['leads']),previous=L['stats'])
wj('research-ledger.json',L)
# ---------- index.md
md=open('index.md').read().split('\n')
assert md[1].startswith('Last updated: 2026-11-10')
md[1]='Last updated: 2026-11-11 (America/Chicago) — daily pass (old lead queue cleared; %d verified additions). Daily research index; foundational coverage, not exhaustive. Historical records and gaps below are preserved; see expansion notes for current scope.'%n
o=['','## 2026-11-11 — daily pass (lead queue + discovery)',
'Step 1 — the 4 leads left open on 2026-11-10: Walraven & Reinhardt 1981 → R1477; Bache 1981 → R1478; Gutt 1972 → R1479 (all catalogue/record-level); "The Nibbler" (BRE CP 83/74, 1974) → rejected, off-topic (demolition equipment). No open leads remain.',
'Step 2 — discovery: OpenAlex full-text and title.search queries (period-split) on the least-covered topics plus a Portland-limestone cement backfill and a Sept–Nov 2026 current-awareness sweep; %d leads selected from ~2,000 de-duplicated hits and all verified the same day (Crossref/DataCite per DOI + doi.org; catalogue/landing pages for no-DOI items).'%len(P['leads']),
'- Promoted: %d (%s–%s); rejected: %d (duplicate/superseded editions: ACI 223R-10 → R178; RILEM AAC 1993 Spon edition → R828; ACI 207.2R-90 journal printing → R111; older BSI ordinary/rapid-hardening Portland cement record → kept newer record).'%(nnew,out[3]['id'],last,rejn),
'- Evidence: abstract-level %d, DOI metadata only %d, catalogue record %d, landing page read %d. Nothing full-text reviewed.'%(acc['abstract_metadata'],acc['doi_metadata'],acc['catalog_metadata'],acc['landing_page_inspected']),
'- Blocked/limited hosts: TRID and TU Delft (timeouts), DTIC (403), J-GLOBAL (503), SID (500); their records were read through the search index and labelled as such.',
'- Not done: citation chasing (next pass).','','### New verified resources (2026-11-11)']
for r in out:
    o.append(' | '.join([r['id'],','.join(r['topics']),r['title'],r['publisher'],r['type'],r['date'] or 'undated',r['url']]))
    au=', '.join(a for a in (r['authors'] or []) if a) if r.get('authors') else 'unknown'
    o.append('  Note: Authors: %s. %s Access: %s. %s%s'%(au,r['description'],r['access'],r['evidenceNote'],(' Edition: '+r['edition']) if r.get('edition') else ''))
o+=['','### Rejected leads (2026-11-11)']
for x in CAN:
    if x.get('reviewPass')==PASS and x['status']=='rejected': o.append('- [rejected] %s — %s'%(x['title'][:110],x['rejectReason']))
open('index.md.tmp','w').write('\n'.join(md).rstrip('\n')+'\n'+'\n'.join(o)+'\n'); os.replace('index.md.tmp','index.md')
# ---------- Page chunk data
pg=[[r['id'],r['title'],r['publisher'],r['type'],r['date'] or '',','.join(r['topics']),r['url']] for r in out]
json.dump(dict(rows=pg,news=S['whatsNew'][0],change=S['changeLog'][-1],gap=S['gaps'][0],total=len(S['resources'])),open(PD+'page-d1111.json','w'),ensure_ascii=False,indent=0)
print('done',first,last,len(S['resources']))
