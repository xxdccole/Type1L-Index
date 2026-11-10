import json,re,os
os.chdir('/workspace/type1l-index'); VD='2026-11-10'; PD='research/pass-2026-11-10/'
S=json.load(open('site-data.json')); L=json.load(open('research-ledger.json'))
B=json.load(open(PD+'build-summary.json')); NEW=json.load(open(PD+'verified-r253-r366.json'))
CAN=[json.loads(l) for l in open('research/portable/candidates.jsonl')]
H=json.load(open(PD+'api-hits.json')); CC=json.load(open(PD+'citation-chase.json')); LOG=json.load(open(PD+'search-log.json'))
FOCUS=['binder-blended','scm-clay','concrete-structural','concrete-hpc','concrete-pavement-pervious','concrete-precast-insitu-print','concrete-circular','concrete-repair-grout-overlay','cross-chemistry','cross-mix','cross-construction','cross-mechanics']
def nd(d): return (d or '').lower().replace('https://doi.org/','').strip()
def norm(t): return re.sub(r'[^a-z0-9]','',(t or '').lower())[:60]
vdois={nd(x.get('doi')) for x in json.load(open('research/portable/verified-sources.json')) if x.get('doi')}
vtitles={norm(r['title'].split(' (')[0]) for r in S['resources']}
promo={nd(d):r['id'] for r in NEW for d in [r.get('doi')] if d and 'Promoted' in r['evidenceNote']}
mv=0
for c in CAN:
    d=nd(c.get('doi'))
    if c['status']=='candidate' and d in promo: c['status']='promoted'; c['promotedTo']=promo[d]; c['promotedOn']=VD
    elif c['status']=='candidate' and d and d in vdois: c['status']='matched-verified'; c['notes']=(c.get('notes') or '')+' matched verified record on '+VD; mv+=1
cd={nd(c.get('doi')) for c in CAN if c.get('doi')}|{norm(c.get('title')) for c in CAN}
KW=re.compile(r'concrete|cement|pozzolan|clay|slag|fly ash|mortar|grout|pavement|hydrat|aggregate|reinforc|prestress|precast|printing|fracture|creep|curing|clinker|binder|metakaolin|rheolog|superplastic|ettringite|uhpc',re.I)
added=[]
def add(topic,title,doi,year,authors,venue,src,query,cited,notes):
    d=nd(doi); t=norm(title)
    if not title or not KW.search(title): return
    if (d and (d in vdois or d in cd)) or t in vtitles or t in cd: return
    cd.add(d or t); cd.add(t)
    added.append(dict(status='candidate',topic=topic,title=title,doi=d or None,year=year,authors=authors or None,venue=venue,url=('https://doi.org/'+d) if d else None,sourceApi=src,query=query,cited_by=cited,notes=notes,addedOn=VD,**{'pass':'pass-2026-11-10-deep3'}))
for k,h in H.items():
    add(h.get('topic'),h.get('title'),h.get('doi'),h.get('year'),h.get('authors'),h.get('venue'),h.get('src','openalex'),h.get('query'),h.get('cited'),'unverified API hit (title/metadata only); not inspected')
for k,c in CC.items():
    for direc in ('forward','backward'):
        for it in c.get(direc,[]):
            add(c['topic'],it[1],it[0],it[2] if len(it)>2 else None,None,None,'openalex-citation-chase','%s of %s'%(direc,k),None,'citation-chase lead (%s); not inspected'%direc)
BLOCK=[('cross-mechanics','Talbot (1907) Tests of reinforced concrete beams — University of Illinois Engineering Experiment Station bulletin','https://www.ideals.illinois.edu/','IDEALS returned HTTP 403 from this network'),
('concrete-structural','Hilsdorf (1970) — University of Illinois report (IDEALS)','https://www.ideals.illinois.edu/','IDEALS returned HTTP 403'),
('concrete-precast-insitu-print','Riding (2007) UT Austin dissertation on early-age concrete temperature','https://repositories.lib.utexas.edu/','UT repository HTTP 403'),
('cross-construction','K. Mather (1980) USACE WES report (ERDC knowledge core)','https://erdc-library.erdc.dren.mil/','ERDC reCAPTCHA blocked automated access'),
('cross-mechanics','TU Delft repository theses (Cornelissen / Walraven era) on concrete fracture/aggregate interlock','https://repository.tudelft.nl/','TU Delft resolver empty response / WebFetch 504'),
('cross-mix','UPenn ScholarlyCommons theses (Meloy; Cellini) on concrete mix topics','https://repository.upenn.edu/','downloads returned tiny/unusable files')]
for t,title,u,why in BLOCK:
    added.append(dict(status='candidate',topic=t,title=title,doi=None,year=None,authors=None,venue=None,url=u,sourceApi='manual',query='historical backfill',cited_by=None,notes='blocked from this network: %s; identity/metadata not confirmed — verify later'%why,addedOn=VD,**{'pass':'pass-2026-11-10-deep3'}))
CAN+=added
with open('research/portable/candidates.jsonl','w') as f:
    for c in CAN: f.write(json.dumps(c,ensure_ascii=False)+'\n')
json.dump(CAN,open('research/portable/candidates.json','w'),indent=1,ensure_ascii=False)
from collections import Counter
cc=Counter(c['status'] for c in CAN); print('candidates',len(CAN),cc,'added',len(added),'matched',mv)
# ledger
n=B['n']; first,last=B['first'],B['last']
cites=["Richard & Cheyrezy 1995 → backward: de Larrard 1989 (R283), de Larrard & Sedran 1994 (R284)",
"RILEM TC 282 clay calcination review (R272) → backward: Sabir 2001 (R264), Fernandez 2011 (R266), Antoni 2012 (R267), Avet 2016 R3 (R268); forward: TC 282 hydration/mixture-design review 2022 (R273), Ben Haha 2023 low-clinker (R260)",
"Buswell 2018 roadmap (R302) → backward: Le 2012 (R300), Roussel 2018 (R301)",
"Hillerborg 1976 (R347) → backward: Modéer 1979 thesis (R365, inspected PDF); forward: Bažant & Oh 1983 crack band (R348)",
"Buck 1977 RCA (R310) → forward: Topçu 2004 (R311)",
"VTRC 26-R52 (R358) → cites ASTM C1897 R3 test (linked to R268); C1897 text not reviewed"]
rec=dict(id='pass-2026-11-10-deep3',date=VD,zone='America/Chicago',focusTopics=FOCUS,currentAwareness=True,status='completed-unpublished (publisher to push)',
repositories=['OpenAlex works API (search, cites:/cited_by:)','Crossref works API (bibliographic search HTTP 429 again; per-DOI lookups succeeded)','DataCite API','doi.org resolver','NIST nvlpubs','FHWA highways.dot.gov','ROSA P / NTL (via WebFetch)','VTRC/VDOT','Lund University portal','ACI previews and news','ANSI Webstore (BSI EN 206-1:2026 preview)','UACEG library (Bulgaria)','Purdue JTRP / Michigan Tech Digital Commons'],
periods='1922–2026 (date-filtered OpenAlex queries for historical topics; ≥2026-01-01 for current sweep)',languages=['en','ja (one source, R351)','bg (one source, R366)'],
apiQueries=LOG,webQueries=[{'tool':'WebSearch/WebFetch','query':q} for q in ['EN 206-1:2026 published CEN','ACI CODE-318-25 release','ACI PRC-522-23 pervious concrete','VTRC 2026 limestone calcined clay cement report','FHWA UHPC structural design HRT-23-077','FHWA UHPC overlay field test','ROSA P zero-maintenance JPCP Darter','Modéer 1979 Lund fracture mechanics thesis','recycled aggregate barriers Bulgaria 2026']],
citationsFollowed=cites,uniqueApiHits=len(H),verifiedAdded=n,idRange='%s–%s'%(first,last),promotedFromCandidates=sorted(promo.values()),candidatesAdded=len(added),candidatesClosedByDedupe=mv,
corrections=['R200 title author attribution "(Avet, Scrivener)" → "(Maraghechi, Avet, Wong, Kazemi-Kamyab, Scrivener)" per Crossref/OpenAlex (verified)','Membership union repaired: %d pre-existing resource↔topic memberships (mostly R178–R203, e.g. R186/R187 in scm-clay) were present on one side only; now both sides'%len(B['repaired'])],
verificationStatus={'open_full_text_inspected':sum(r['access']=='open_full_text_inspected' for r in NEW),'preview_inspected':sum(r['access']=='preview_inspected' for r in NEW),'landing_page_inspected':sum(r['access']=='landing_page_inspected' for r in NEW),'abstract_metadata':sum(r['access']=='abstract_metadata' for r in NEW),'doi_metadata':sum(r['access']=='doi_metadata' for r in NEW)},
gaps=['Normative texts of ACI CODE-318-25, EN 206-1:2026, ACI PRC-522-23 and ASTM C1897 not reviewed (preview/news only)','Abrams 1918 primary text not located in inspectable copy','CRCP design/performance sources not found this pass','Illinois IDEALS and UT repository 403; ERDC reCAPTCHA; TU Delft timeout — historical items logged as candidates','Majority of journal records are DOI/abstract-level only; 1922 Franklin Institute item has no registered authors (unknown)'],
nextSteps=['Next pass: rotate to globalNextQueue head (topics not yet deepened)','Retry blocked repositories (IDEALS, UT, ERDC, TU Delft) from a different network or with user help','Triage the %d new candidate leads for the 12 pass-3 topics'%len(added)],
summary='Verified +%d sources (%s–%s) across 12 queued topics plus 2026 current awareness; %d promoted candidates; %d citation-chase additions; R200 corrected; membership union repaired; %d new unverified candidates queued. Not exhaustive.'%(n,first,last,len(promo),sum(r['origin']=='citation-chase' for r in NEW),len(added)))
L['passes'].append(rec)
tm={t['id']:t for t in S['topics']}
for t in L['topics']:
    st=tm[t['id']]; t['resourceIds']=list(st['resourceIds']); t['resourceCount']=len(st['resourceIds'])
    if t['id'] in FOCUS:
        t['passStatus']='deepened-pass3'; t['lastDeepPass']=VD; t['lastTouched']=VD
        t['searches']+= [dict(q,date=VD,repositories=['OpenAlex','Crossref']) for q in LOG if q['topic']==t['id']]
        t['verifiedAdditions']=list(dict.fromkeys(t['verifiedAdditions']+[r['id'] for r in NEW if t['id'] in r['topics']]))
        t['candidates']=t.get('candidates',[])+[c['title'] for c in added if c['topic']==t['id']][:40]
        t['nextSteps']=['Triage pass-3 candidate leads','Seek full-text/primary documents for DOI-only records']
    elif any(t['id'] in r['topics'] for r in NEW): t['lastTouched']=VD
q=L['globalNextQueue']; L['globalNextQueue']=[x for x in q if x['topicId'] not in FOCUS]+[x for x in q if x['topicId'] in FOCUS]
for x in L['globalNextQueue']:
    if x['topicId'] in FOCUS: x['reason']='deepened in pass 3 (2026-11-10); revisit after remaining topics'
prev=L['stats']; deepened={t['id'] for t in L['topics'] if str(t.get('passStatus','')).startswith('deepened')}
L['stats']=dict(topics=59,resourcesAtStart=252,resourcesAfterPass=len(S['resources']),verifiedAdded=n,uniqueApiHits=len(H),candidatesTotal=len(CAN),candidatesOpen=cc['candidate'],candidatesPromoted=cc['promoted'],candidatesMatchedVerified=cc['matched-verified'],topicsDeepenedPass3=12,topicsDeepenedTotal=len(deepened),topicsQueuedNotYetDeepened=59-len(deepened),membershipRepairs=len(B['repaired']),previous=prev)
L['updated']=VD
json.dump(L,open('research-ledger.json','w'),indent=2,ensure_ascii=False)
print(L['stats'] | {'previous':None}, [x['topicId'] for x in L['globalNextQueue'][:12]])
# index.md
md=open('index.md').read().split('\n')
md[1]='Last updated: 2026-11-10 (America/Chicago) — deep research pass 3 + 2026 current-awareness sweep. Daily research index; foundational coverage, not exhaustive. Historical records and gaps below are preserved; see expansion notes for current scope.'
md='\n'.join(md).rstrip('\n')
md=md.replace('(Avet, Scrivener)','(Maraghechi, Avet, Wong, Kazemi-Kamyab, Scrivener)')
byid={r['id']:r for r in S['resources']}
o=['','## 2026-11-10 — deep research pass 3 + current-awareness sweep','Deepened topics (queue order): '+', '.join(FOCUS)+'.',
'%d verified records %s–%s appended (OpenAlex/DOI/web searches incl. 2026 current awareness; %d promoted from the candidate queue: %s; citation chasing followed). R1–R252 preserved. Not exhaustive; %d unverified candidate leads remain in research/portable/candidates.jsonl.'%(n,first,last,len(promo),', '.join(sorted(promo.values())),cc['candidate']),
'Corrections: R200 title author attribution corrected to (Maraghechi, Avet, Wong, Kazemi-Kamyab, Scrivener) per Crossref/OpenAlex. Topic membership union repaired for %d pre-existing resource↔topic links (one-sided before).'%len(B['repaired']),
'','### Current awareness (2026)',
'- EN 206-1:2026 (CEN, March 2026; R355 preview): EN 206 split into Parts 1–3, superseding EN 206:2013+A2:2021; adds CO2-emission classes. National adoption by Sept 2026.',
'- ACI CODE-318-25 released Jan 2025 (R356, release news; code text not reviewed). ACI PRC-522-23 pervious concrete report supersedes 522R-10 (R357 preview).',
'- VTRC 26-R52 (June 2026, R358): VDOT evaluation of LC3 to address fly ash shortage; uses ASTM C1897 R3 reactivity. 2026 journal items: R274, R292, R293, R298, R299, R309, R318, R325, R366.',
'','### New verified resources']
for r in NEW:
    o.append(' | '.join([r['id'],','.join(r['topics']),r['title'],r['publisher'],r['type'],r['date'],r['url']]))
    au=', '.join(r['authors']) if r.get('authors') else 'unknown'
    o.append('  Note: Authors: %s. %s Access: %s. %s%s'%(au,r['description'],r['access'],r['evidenceNote'],(' Rights: '+r['rights']+'.') if r.get('rights') else ''))
o+=['','### Pass 3 takeaways by topic']+['- %s: %s'%(t,tm[t]['takeaways'][-1]) for t in FOCUS]+['','### Pass 3 gaps']+['- '+g for g in rec['gaps']]+['- Crossref bibliographic search rate-limited (HTTP 429) again; OpenAlex search plus per-DOI Crossref/DataCite verification used.','']
open('index.md','w').write(md+'\n'+'\n'.join(o))
