"""pass-2026-11-19 apply: new verified records (R3048+) and lead outcomes into working files (atomic writes). Run once from pre-pass state.
Derived from research/pass-2026-11-18/apply.py (no open leads at start, so no old-lead block)."""
import json,os,re,collections
os.chdir('/workspace/type1l-index'); VD='2026-11-19'; PASS='pass-2026-11-19'; PD='research/pass-2026-11-19/'
P=json.load(open(PD+'plan.json'))
S=json.load(open('site-data.json')); L=json.load(open('research-ledger.json')); N=json.load(open('research/resource-notes.json'))
VER=[json.loads(l) for l in open('research/portable/verified-sources.jsonl')]
CAN=[json.loads(l) for l in open('research/portable/candidates.jsonl')]
NBEFORE=len(S['resources'])
assert NBEFORE==3046 and S['resources'][-1]['id']=='R3047' and S['lastUpdated']=='2026-11-18','expected pre-pass state'
OPEN=[i for i,c in enumerate(CAN) if c['status']=='candidate']; assert len(OPEN)==0,OPEN
assert not any(r['id']=='R428' for r in S['resources'])
before={r['id']:json.dumps(r,sort_keys=True) for r in S['resources']}
out=[]; nxt=3048
def mk(r,origin,cidx=None):
    global nxt
    rid='R%d'%nxt; nxt+=1
    S['resources'].append({'id':rid,'title':r['title'],'publisher':r['publisher'],'type':r['type'],'date':r['date'],'url':r['url'],'topics':list(r['topics'])})
    out.append(dict(id=rid,status='verified',title=r['title'],authors=r.get('authors'),publisher=r['publisher'],type=r['type'],date=r['date'],url=r['url'],doi=r.get('doi'),identifiers=r.get('ids') or {},topics=list(r['topics']),geography=r.get('geo'),language=r.get('lang','en'),description=r['desc'],access=r['access'],evidenceNote=r['evidence'],edition=r.get('edition'),rights=r.get('rights'),version=None,verifiedOn=VD,provenance=PASS,origin=origin,promotedFromCandidate=True,candidateIndex=cidx,added=VD))
    N[rid]=r['evidence']; return rid
oldout={}
# ---------- new verified records
k2id={}
for r in P['recs']: k2id[r['_key']]=mk(r,'discovery-'+PASS)
oldN=len(CAN); newlead={}; openl=[]
for ld in P['leads']:
    k=ld.pop('_key'); ld['pass']=ld.pop('pass_'); ld.pop('_reject',None)
    if '_open' in ld:
        ld.update(status='rejected',rejectCategory='unverifiable',rejectReason=ld.pop('_open')+('; nothing could be verified' if ld.get('doi') is None else '; the OpenAlex landing page could not be inspected (404/403/202 or title not found), so nothing could be verified'))
    elif k in k2id: ld.update(status='promoted',promotedTo=k2id[k],promotedOn=VD)
    CAN.append(ld); newlead[k]=len(CAN)-1
i2k={v:k for k,v in k2id.items()}
for f in out: f['candidateIndex']=[newlead[i2k[f['id']]]]
first,last=out[0]['id'],out[-1]['id']; nfirst=first
tmap={t['id']:t for t in S['topics']}; byid={r['id']:r for r in S['resources']}
for r in S['resources']:
    for t in r['topics']:
        if r['id'] not in tmap[t]['resourceIds']: tmap[t]['resourceIds'].append(r['id'])
for t in S['topics']:
    for i_ in t['resourceIds']:
        if t['id'] not in byid[i_]['topics']: byid[i_]['topics'].append(t['id'])
for r in S['resources'][:NBEFORE]: assert json.dumps(r,sort_keys=True)==before[r['id']],r['id']
n=len(out); nnew=n
rejn=sum(1 for c in CAN[oldN:] if c['status']=='rejected')
tc=collections.Counter(t for r in out for t in r['topics'])
acc=collections.Counter(r['access'] for r in out)
langs=collections.Counter(r['language'] for r in out)
chase=[f['id'] for f in out if 'backward citation chase' in f['evidenceNote']]
fwd=[f['id'] for f in out if 'forward citation chase' in f['evidenceNote']]
cur=[f['id'] for f in out if (f['date'] or '').startswith('2026')]
noneng=[f['id'] for f in out if f['language']!='en']
focus=['concrete-lightweight','binder-cac-csa','binder-lc3','binder-magnesium-carbonatable','scm-silica','scm-slag','scm-emerging','binder-blended','concrete-structural','cross-tests-codes','cross-environment-cost']
TKX=json.load(open(PD+'takeaways.json'))
TK=dict(TKX)
for tid,txt in TK.items():
    ids=[f['id'] for f in out if tid in f['topics']]
    tmap[tid]['takeaways'].append(txt%('%s–%s, %d records'%(ids[0],ids[-1],len(ids)) if ids else 'none'))
plc=[f['id'] for f in out if any(t in f['topics'] for t in ('standards','dot','carbon','fresh','strength','durability','scm','intl','apps','pavement','mix','field','mass','microcracking'))]
nodoi_ok=sum(1 for f in out if f['doi'] is None)
S['lastUpdated']=VD
S['whatsNew'].insert(0,{'date':'Nov 19','title':'Daily pass: %d verified additions (%s–%s)'%(n,first,last),'detail':'No leads were open at the start. Discovery added %d verified sources for the next least-covered families — lightweight-aggregate concrete (perlite, EPS, plastic-waste aggregates), calcium sulfoaluminate and calcium aluminate cements, LC3/low-grade calcined clays, CO2-cured and magnesium (phosphate, oxysulfate, reactive MgO) binders, silica fume and nano-silica, GGBS/steel/copper slags, emerging SCMs (waste glass, biochar, sludge ash, marble/brick powders, gangue, phosphogypsum), blended cements, structural concrete (confinement, bond, shear, punching, creep/shrinkage models, precast), test methods and codes (ACI 318, Eurocode 2, ASTM C143) and cement-industry decarbonisation/recycled aggregates — plus %d records from backward and %d from forward citation chases, %d non-English records (Czech, Danish, Dutch, French, German, Indonesian, Italian, Korean, Portuguese, Russian, Spanish, Turkish; English glosses), Type IL legacy-topic backfill (mix, supply, international, applications, field, strength, durability), DOT/university reports and theses, CiNii Books catalogue records for classic textbooks, and a Nov 2026 current-awareness sweep (%d records dated 2026). %d new leads were rejected as unverifiable; none left open. Mostly DOI/abstract-level, not full-text reviews.'%(nnew,len(chase),len(fwd),len(noneng),len(cur),rejn)})
S['changeLog'].append({'date':VD,'entry':'Daily pass 2026-11-19: %d verified additions %s–%s (all from new discovery: title.search backfill with period splits and page-2 re-queries, historical/government/standards searches, language-filtered searches, PLC legacy-topic backfill, current-awareness sweep, backward/forward citation chase from existing records in the focus topics and from the most-cited Nov 18 additions). %d new leads checked: %d promoted, %d rejected as unverifiable, 0 left open. No corrections to existing records. R1–R3047 preserved (R428 still retired); topic membership union maintained.'%(n,first,last,len(P['leads']),nnew,rejn)})
S['gaps'].insert(0,'Daily pass 2026-11-19: additions are registry/catalogue-verified (%d abstract-level, %d DOI metadata only, %d landing pages read, %d library catalogue records) — not full-text reviewed. Many Elsevier items have no abstract in Crossref/OpenAlex, so descriptions are bibliographic only. %d of 95 no-DOI hits were inspectable and added (incl. 8 CiNii Books catalogue records); the other 67 were rejected as unverifiable and logged in the candidate queue (TRID timeouts, CiNii article/CNKI/CQVIP/ResearchGate pages, ROSA P/Theseus/yadda/DOAJ pages returning 403, JS-only repositories and PDFs) — e.g. Neville Properties of Concrete (4th ed.), PCA Design and Control of Concrete Mixtures, the Concrete Admixtures Handbook, the FHWA UHPC state-of-the-art report and several creep/shrinkage books remain gaps. Plain-http landing URLs failed from the box and were read over https. Two hits whose DOIs are unregistered (Russian MCE, Turkish Teknik Dergi) were added from their article pages with the DOI recorded as listedDoi. No open leads.'%(acc['abstract_metadata'],acc['doi_metadata'],acc['landing_page_inspected'],acc['catalog_metadata'],nodoi_ok-2))
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
web=['curl (https): CiNii Books (ci.nii.ac.jp/ncid) catalogue records read — 8 books; no-DOI landing pages read — Docta Complutense, ReP USP, Lund University Publications, DTU Orbit, Aalborg University portal, Politecnico di Milano IRIS, University of Bergamo Aisberg, DBpia, KCI, DergiPark, AVESIS, KU ScholarWorks, University of Washington ResearchWorks, University of Toronto TSpace, TU Delft Repository','curl: article pages for unregistered DOIs 10.18720/mce.75.4 (engstroy.spbstu.ru) and 10.18400/td.12199 (DergiPark Teknik Dergi), citation metadata read','curl (not inspectable): TRID (timeout), CiNii article pages (cir.nii.ac.jp HTTP 202), CNKI/CQVIP, ResearchGate (skipped hosts); ROSA P (NTL), Theseus, yadda/BazTech, DOAJ, Illinois IDEALS, UT Austin repositories (HTTP 403); Czech DSpace, Tampere Trepo, NVA (sikt.no), DiVA, RWTH pages (title not found / JS-only); PDFs not parsed','Box egress note: plain-http URLs returned HTTP 500 (proxy); https retried']
rec=dict(id=PASS,date=VD,zone='America/Chicago',kind='daily-discovery+lead-verification',focusTopics=focus+['historical/government/standards sweep (Bureau of Reclamation, National Bureau of Standards, Highway Research Board, FHWA, early cement specifications, blended-cement theses)','Type IL collection topics via Portland-limestone backfill (mix, supply, intl, apps, field, strength, durability)','non-English literature (new: cs, da, fi, it, ko, nl, no, pl, ru, tr with new terms; pt/es/de/fr/zh/ja re-queried with new terms)','backward and forward citation chase from %d existing DOI records in the 11 focus topics plus forward chase from the 10 most-cited Nov 18 additions'%1240],currentAwareness=True,status='completed-unpublished (publisher to push)',
 repositories=['OpenAlex works API (title.search with period splits and page 2 of this pass\'s queries; language filter; relevance search for current awareness, history and PLC topics; referenced_works backward chase; cites: forward chase)','Crossref works API (per-DOI, public pool)','DataCite API','doi.org resolver (HEAD)','University/national repositories (Lund, DTU Orbit, Aalborg, Polimi IRIS, Bergamo Aisberg, KU ScholarWorks, UW ResearchWorks, U Toronto TSpace, TU Delft)','Korean DBpia/KCI, Turkish DergiPark/AVESIS, Russian MCE journal pages'],
 periods='1909–2026 (title.search windows ≤1980/≤1990/1991–2026, ≤1995/1996–2026, ≤2000/2001–2026, ≤2005/2006–2026, ≤2010, 2016–2026, 2023–2026; history searches ≤1960/≤1970/≤1975/≤1980; current sweep 2026-09-15 → 2026-11-19)',languages=sorted(langs),
 apiQueries=[dict(e,harvest='harvest1') for e in s1]+[dict(e,harvest='harvest2-page2') for e in s2],webQueries=web,
 citationsFollowed=[dict(direction='backward',tool='OpenAlex referenced_works',seeds='existing DOI-bearing records in the 11 focus topics (1,240 seeds; those dated <2006 expanded)',referencesFound=2929,kept='cited by >=2 seeds or published <1990 (1,710 kept before dedupe)',promoted=len(chase)),
   dict(direction='forward',tool='OpenAlex cites:',seeds='30 most-cited existing records in those topics + 10 most-cited Nov 18 additions (R2635–R2721, R2984)',kept='top 8 citers ≤2012 + top 5 citers 2024–2026 per seed',promoted=len(fwd))],
 uniqueApiHits=dict(harvest1=3483,harvest2=4263,newAfterDedupe=3198+len(json.load(open(PD+'new-hits2.json')))),triage='Hits screened by title (listing capped at 24 per focus query-topic, 7 per language/PLC query, 45 current, 110 backward and 45 forward chase hits): 618 listed, 38 excluded on screening (dental/resin cements, zeolite synthesis/NMR, soil stabilisation/subgrade/earth bricks/soil-cement piles, mine backfill, asphalt, seismic code-comparison/fragility building analyses, sociology/politics/history uses of cement/beton, a bare journal-title record, a reproducibility survey, an image-processing paper), 95 no-DOI hits probed on their landing pages (28 read and added, incl. 8 CiNii Books catalogue records; 67 not inspectable, logged as rejected leads), 485 DOI hits verified (476 Crossref, 7 DataCite, 2 unregistered DOIs whose article pages were read). See research/pass-2026-11-19/listing.txt and select.py.',
 leadsProcessed=len(P['leads']),oldLeadOutcomes={},verifiedAdded=n,idRange='%s–%s'%(first,last),newLeadsRejected=rejn,openLeadsAfterPass=sum(1 for c in CAN if c['status']=='candidate'),openLeads=[],
 verificationStatus=dict(acc),topicsTouched=dict(tc.most_common()),corrections=[],
 gaps=['Most journal items DOI-level only (Elsevier abstracts absent from Crossref/OpenAlex)','Non-English titles glossed from title/abstract only','67 no-DOI hits not inspectable and rejected (TRID timeouts; CiNii article pages (cir.nii.ac.jp 202), CNKI/CQVIP, ResearchGate skipped; ROSA P, Theseus, yadda/BazTech, DOAJ, IDEALS, UT repositories 403; JS-only DSpace/NVA/DiVA; PDFs): e.g. Neville Properties of Concrete 4th ed., Design and Control of Concrete Mixtures, Concrete Admixtures Handbook, two creep/shrinkage books (Creep of plain and structural concrete, 1983; Creep and shrinkage in concrete structures, 1982), FHWA UHPC state-of-the-art report (ROSA P 403), Finnish/Polish/Norwegian theses and papers','Lightweight-aggregate title.search hits drifted toward recycled/waste fine aggregates (kept, re-tagged by title keywords)','"composite cement" queries mostly returned fibre/nano cement composites (kept, re-tagged)','Seismic code-comparison (Turkish) and fragility papers left out as structural-engineering rather than materials literature','Possible correction: R1185 could carry its ACI DOI once registered (unchanged)'],
 nextSteps=['Next rotation head (least-recently backfilled): cross-mix, cross-chemistry, cross-mechanics, scm-limestone, binder-activated, cross-durability, concrete-architectural, concrete-scc, concrete-polymer-refractory, concrete-circular, concrete-pavement-pervious, concrete-repair-grout-overlay, concrete-precast-insitu-print','Retry ROSA P / Theseus / yadda pages that returned 403 (FHWA UHPC report, Finnish and Polish theses) via alternative mirrors or OAI-PMH','Forward chase from 2026-11-19 classics (Mander confined-concrete model, B3 creep model, CSA/LC3 reviews)','Type IL legacy topics still thin: mix, gaps, supply, news, intl — continue PLC-specific backfill','Add 2026 current-awareness queries for RILEM TCs, fib bulletins and agency reports'],
 summary='No open leads at start. %d new leads checked the same day: %d promoted, %d rejected (unverifiable), 0 open. %d verified additions %s–%s.'%(len(P['leads']),nnew,rejn,n,first,last))
L['passes'].append(rec)
qby=collections.defaultdict(list)
MAPT={'pll-pavement':'pavement','pll-strength':'strength','pll-durability':'durability','pll-fresh':'fresh','pll-micro':'microcracking','pll-standards':'standards','pll-dot':'dot','pll-carbon':'carbon','pll-mix':'mix','pll-supply':'supply','pll-intl':'intl','pll-apps':'apps','pll-field':'field','current-2026':None,'citation-chase':None,'citation-chase-fwd':None}
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
        t['passStatus']='daily_pass_2026-11-19_backfill'; t['lastDeepPass']=PASS
        t['nextSteps']=['Forward citation chase from 2026-11-19 classics','Look for open institutional/government reports, older proceedings and non-English literature','Avoid repeating 2026-11-12/2026-11-19 title.search queries (see ledger)']
q=L['globalNextQueue']; moved=[x for x in q if x['topicId'] in focus]; L['globalNextQueue']=[x for x in q if x['topicId'] not in focus]+[dict(x,reason='Backfilled in pass-2026-11-19; rotate to end') for x in moved]
L['updated']=VD; L['lastDeepPass']=PASS
L['stats']=dict(topics=59,resourcesAtStart=NBEFORE,resourcesAfterPass=len(S['resources']),verifiedAdded=n,candidatesTotal=len(CAN),candidatesOpen=sum(1 for c in CAN if c['status']=='candidate'),candidatesPromoted=sum(1 for c in CAN if c['status']=='promoted'),candidatesMatchedVerified=sum(1 for c in CAN if c['status']=='matched-verified'),candidatesRejected=sum(1 for c in CAN if c['status']=='rejected'),leadsProcessedThisPass=len(P['leads']),previous=L['stats'])
wj('research-ledger.json',L)
# ---------- index.md
md=open('index.md').read().split('\n')
assert md[1].startswith('Last updated: 2026-11-18')
md[1]='Last updated: 2026-11-19 (America/Chicago) — daily pass (%d verified additions; no open leads). Daily research index; foundational coverage, not exhaustive. Historical records and gaps below are preserved; see expansion notes for current scope.'%n
o=['','## 2026-11-19 — daily pass (discovery + same-day lead verification)',
'Step 1 — queue: 0 open leads at start (statuses promoted/rejected/matched-verified only); nothing to resolve.',
'Step 2 — discovery: OpenAlex title.search queries on the next least-covered families (concrete-lightweight, binder-cac-csa, binder-lc3, binder-magnesium-carbonatable, scm-silica, scm-slag, scm-emerging, binder-blended, concrete-structural, cross-tests-codes, cross-environment-cost; period splits and page 2 for deeper rows), historical/government/standards searches (Bureau of Reclamation, NBS, HRB, FHWA, early cement specifications, theses), language-filtered searches with new terms (cs, da, fi, it, ko, nl, no, pl, ru, tr; pt/es/de/fr/zh/ja), a Portland-limestone backfill for Type IL topics (mix, supply, intl, apps, field, strength, durability), a Nov 2026 current-awareness sweep, and backward/forward citation chases from existing records in the focus topics and the most-cited Nov 18 additions. %d leads selected from ~7,750 raw API hits (before de-duplication against the index and candidate queue) and verified the same day (Crossref/DataCite per DOI + doi.org; landing pages for items without a registered DOI).'%len(P['leads']),
'- Promoted: %d (%s–%s); rejected: %d (no-DOI hits whose landing/catalogue pages could not be inspected); open: 0.'%(nnew,nfirst,last,rejn),
'- Evidence: abstract-level %d, DOI metadata only %d, landing page read %d, catalogue %d. Nothing full-text reviewed.'%(acc['abstract_metadata'],acc['doi_metadata'],acc['landing_page_inspected'],acc['catalog_metadata']),
'- Citation chase: %d backward, %d forward; non-English: %d (descriptions are English glosses); dated 2026: %d.'%(len(chase),len(fwd),len(noneng),len(cur)),
'- Corrections to existing records: none.','','### New verified resources (2026-11-19)']
for r in out:
    o.append(' | '.join([r['id'],','.join(r['topics']),r['title'],r['publisher'] or 'unknown',r['type'],r['date'] or 'undated',r['url']]))
    au=', '.join(a for a in (r['authors'] or []) if a) if r.get('authors') else 'unknown'
    o.append('  Note: Authors: %s. %s Access: %s. %s%s'%(au,r['description'],r['access'],r['evidenceNote'],(' Edition: '+r['edition']) if r.get('edition') else ''))
o+=['','### Open leads (2026-11-19)','- none']
open('index.md.tmp','w').write('\n'.join(md).rstrip('\n')+'\n'+'\n'.join(o)+'\n'); os.replace('index.md.tmp','index.md')
pg=[[r['id'],r['title'],r['publisher'] or '',r['type'],r['date'] or '',','.join(r['topics']),r['url']] for r in out]
json.dump(dict(rows=pg,news=S['whatsNew'][0],change=S['changeLog'][-1],gap=S['gaps'][0],total=len(S['resources']),takeaways={k:tmap[k]['takeaways'][-1] for k in TK}),open(PD+'page-d1119.json','w'),ensure_ascii=False,indent=0)
print('done',first,last,len(S['resources']))
