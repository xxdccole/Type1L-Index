"""pass-2026-11-12 apply: new verified records R1624+ and lead outcomes into working files (atomic writes). Run once from pre-pass state."""
import json,os,re,collections
os.chdir('/workspace/type1l-index'); VD='2026-11-12'; PASS='pass-2026-11-12'; PD='research/pass-2026-11-12/'
P=json.load(open(PD+'plan.json'))
S=json.load(open('site-data.json')); L=json.load(open('research-ledger.json')); N=json.load(open('research/resource-notes.json'))
VER=[json.loads(l) for l in open('research/portable/verified-sources.jsonl')]
CAN=[json.loads(l) for l in open('research/portable/candidates.jsonl')]
assert len(S['resources'])==1622 and S['resources'][-1]['id']=='R1623' and S['lastUpdated']=='2026-11-11','expected pre-pass state'
assert not any(c['status']=='candidate' for c in CAN),'queue not empty'
assert not any(r['id']=='R428' for r in S['resources'])
before={r['id']:json.dumps(r,sort_keys=True) for r in S['resources']}
k2id={}; out=[]; nxt=1624
for r in P['recs']:
    rid='R%d'%nxt; nxt+=1
    S['resources'].append({'id':rid,'title':r['title'],'publisher':r['publisher'],'type':r['type'],'date':r['date'],'url':r['url'],'topics':list(r['topics'])})
    out.append(dict(id=rid,status='verified',title=r['title'],authors=r.get('authors'),publisher=r['publisher'],type=r['type'],date=r['date'],url=r['url'],doi=r.get('doi'),identifiers=r.get('ids') or {},topics=list(r['topics']),geography=r.get('geo'),language=r.get('lang','en'),description=r['desc'],access=r['access'],evidenceNote=r['evidence'],edition=r.get('edition'),rights=r.get('rights'),version=None,verifiedOn=VD,provenance=PASS,origin='discovery-'+PASS,promotedFromCandidate=True,candidateIndex=None,added=VD))
    N[rid]=r['evidence']; k2id[r['_key']]=rid
oldN=len(CAN); newlead={}; openl=[]
for ld in P['leads']:
    k=ld.pop('_key'); ld['pass']=ld.pop('pass_')
    if '_open' in ld:
        ld['openReason']=ld.pop('_open'); ld['status']='candidate'; ld['lastCheckedOn']=VD; openl.append(ld['title'])
    elif k in k2id: ld.update(status='promoted',promotedTo=k2id[k],promotedOn=VD)
    else:
        cat,reason,dup=P['rejected'][k]; ld.update(status='rejected',rejectCategory=cat,rejectReason=reason,duplicateOf=dup)
    CAN.append(ld); newlead[k]=len(CAN)-1
for f in out:
    k=[kk for kk,v in k2id.items() if v==f['id']][0]; f['candidateIndex']=[newlead[k]]
first,last=out[0]['id'],out[-1]['id']; byrid={f['id']:f for f in out}
# ---------- membership union
tmap={t['id']:t for t in S['topics']}; byid={r['id']:r for r in S['resources']}
for r in S['resources']:
    for t in r['topics']:
        if r['id'] not in tmap[t]['resourceIds']: tmap[t]['resourceIds'].append(r['id'])
for t in S['topics']:
    for i in t['resourceIds']:
        if t['id'] not in byid[i]['topics']: byid[i]['topics'].append(t['id'])
for r in S['resources'][:1622]: assert json.dumps(r,sort_keys=True)==before[r['id']],r['id']
n=len(out)
tc=collections.Counter(t for r in out for t in r['topics'])
acc=collections.Counter(r['access'] for r in out)
langs=collections.Counter(r['language'] for r in out)
chase=[f['id'] for f in out if 'backward citation chase' in f['evidenceNote']]
cur=[f['id'] for f in out if (f['date'] or '').startswith('2026')]
noneng=[f['id'] for f in out if f['language']!='en']
def ids_where(pred): return [f['id'] for f in out if pred(f)]
def rng(ids): return ', '.join(ids[:12])+(' …' if len(ids)>12 else '')
# ---------- topic takeaways (pointers to today's additions; evidence level stated)
TK={
'binder-cac-csa':'Nov 12 backfill (catalogue/abstract level): classic CSA/CAC chemistry — Mehta & Klein 1965 ettringite from anhydrous calcium sulfoaluminate, Sharp et al. 1999 “low-energy cements, special cements or what?”, Glasser & Zhang 2001/2002 CSA-belite matrices and <24 h hydration, Scrivener et al. 1999 CAC high-performance concretes — plus six Jul–Sep 2026 Advances in Cement Research CSA papers (%s).',
'binder-activated':'Nov 12 backfill: founding geopolymer papers (Davidovits 1989, 1991), Wang & Scrivener 1994/1995 alkali-activated slag, Palomo/Fernández-Jiménez fly-ash activation series, Duxson et al. 2006 state of the art, RILEM TC 247-DTA round robins on durability testing of alkali-activated concretes (%s). DOI/abstract level.',
'binder-magnesium-carbonatable':'Nov 12 backfill: Sorel/magnesium oxychloride cement (Tooper & Cartz 1966 Nature; Ball 1977; Deng 2003; Li & Chau 2007), magnesium phosphate rapid repair (Seehra et al. 1993), carbonation curing of precast and a 2026 MOC review (%s). DOI/abstract level.',
'scm-silica':'Nov 12 backfill: early condensed-silica-fume literature (Page & Vennesland 1983 pore solution/chloride binding; Mehta & Gjørv 1982; Huang & Feldman 1985; Malhotra et al. 1988 book; Bentur & Cohen 1987 ITZ; Hooton 1993 durability) plus rice husk ash and nano-silica studies (%s).',
'scm-emerging':'Nov 12 backfill: steel/ladle slag cementitious properties (Shi 2002, 2004), red mud in clinker and special cements, MSWI ash in cement and clinker, palm oil fuel ash and sugarcane bagasse ash (incl. a 2009 Brazilian Portuguese-language study) (%s). DOI/abstract level.',
'concrete-lightweight':'Nov 12 backfill: Shideler 1957 ACI structural LWAC, Zhang & Gjørv 1991 LWA for high-strength concrete, internal curing with pre-wetted LWA (Bentur et al. 2001; Zhutovsky et al. 2002; Cusson & Hoogeveen 2008; Castro et al. 2011), pumice and sintered fly-ash aggregates, ACI 1968 low-density precast units guide (%s).',
'cross-durability':'Nov 12 backfill of mechanism classics (DOI/abstract level): ASR (Diamond 1975; Chatterji 1979; Hobbs 1988 book; Swamy & Al-Asali 1988; Fournier & Bérubé 2000), DEF (Scrivener & Taylor 1993; Diamond 1996; Taylor et al. 2001), carbonation models (Papadakis 1991/2000), chloride transport (Page et al. 1981; Andrade 1993; Thomas & Bamforth 1999), sulfate/thaumasite (Mehta 1983; Cohen & Mather 1991; Crammond 1985/1995) and RILEM CDF/CIF frost tests (%s).',
'cross-tests-codes':'Nov 12 backfill: test-method history — ASTM C1012 development (Patzias 1991), Mehta & Gjørv 1974 sulfate test, RCPT/resistivity (Shi 2004; Wee et al. 2000; Andrade 2011 in Spanish), maturity method, UPV standards comparison (Komloš et al. 1996), Malhotra & Carino NDT handbook (2003), RILEM round robins; historical ACI 318-47 and 318-71 code printings and DIN 1045-2:2008 (superseded by DIN 1045-2:2023-08) (%s).',
'cross-environment-cost':'Nov 12 backfill: cement-kiln emissions with alternative fuels, carbon-capture integration (Ca-looping), embodied-carbon of concrete (Purnell & Black 2012; Anderson & Moncaster 2020 EPD analysis), LCA reviews (Van den Heede & De Belie 2012), prospective LCA of European cement and Ecuador/Brazil LCA studies (%s). DOI/abstract level.',
'scm-limestone':'Nov 12 PLC/limestone backfill: 1988–1991 ASTM/CRC “carbonate additions” literature (Mayfield 1988; Livesey 1991; Barker & Cory 1991; Adams & Race 1990; Bédard & Bergeron 1990; Neto & Campiteli 1990), Gutteridge & Dalziel 1990 filler-cement papers, Tsivilis 1999 and Vuk 2001 PLC parameters, Purdue 2013 and Caltrans 2021 PLC reports, and Nov 2026 limestone/gypsum content determination (%s).',
}
TOPICFOCUS={'binder-cac-csa','binder-activated','binder-magnesium-carbonatable','scm-silica','scm-emerging','concrete-lightweight','cross-durability','cross-tests-codes','cross-environment-cost','scm-limestone'}
for tid,txt in TK.items():
    ids=[f['id'] for f in out if tid in f['topics']]
    tmap[tid]['takeaways'].append(txt%('%s–%s, %d records'%(ids[0],ids[-1],len(ids)) if ids else 'none'))
plc=[f['id'] for f in out if any(t in f['topics'] for t in ('standards','dot','carbon','fresh','strength','durability','scm','intl','apps'))]
# ---------- narrative
S['lastUpdated']=VD
S['whatsNew'].insert(0,{'date':'Nov 12','title':'Daily pass: %d verified additions (%s–%s)'%(n,first,last),'detail':'Queue was empty at start. Discovery added %d verified sources focused on the next least-covered rotation topics — durability mechanisms (ASR, DEF, carbonation, chloride, sulfate/thaumasite, frost), testing/specification history, environment/LCA and kiln emissions, calcium aluminate/sulfoaluminate, alkali-activated/geopolymer, magnesium and carbonatable binders, silica fume/rice husk ash/nano-silica, emerging SCMs (steel slag, red mud, MSWI ash, POFA, bagasse ash), slag and lightweight aggregate concrete — plus %d records found by a backward citation chase from Nov 11 historical seeds, %d non-English records (German, Spanish, French, Portuguese, Japanese, Chinese; English glosses), a Portland-limestone/carbonate-additions backfill and a Jul–Nov 2026 current-awareness sweep (%d records dated 2026). One lead left open (Chinese journal host unreachable). Mostly DOI/abstract-level, not full-text reviews.'%(n,len(chase),len(noneng),len(cur))})
S['changeLog'].append({'date':VD,'entry':'Daily pass 2026-11-12: %d verified additions %s–%s, all from new discovery (title.search backfill with period splits, language-filtered searches, PLC backfill, current-awareness sweep, and backward citation chase from 2026-11-11 seeds). %d new leads found: %d promoted, 0 rejected, %d left open (host unreachable). No corrections to existing records. R1–R1623 preserved (R428 still retired); topic membership union maintained.'%(n,first,last,len(P['leads']),n,len(openl))})
S['gaps'].insert(0,'Daily pass 2026-11-12: additions are registry/catalogue-verified (%d abstract-level, %d DOI metadata only, %d catalogue records, %d landing pages read) — not full-text reviewed. Many Elsevier journal items have no abstract in Crossref/OpenAlex, so descriptions are bibliographic only. Non-English coverage is still thin (German/French/Spanish/Portuguese journal and standards literature, JIS/GB/IS national standards); Chinese journals registered only with ChinaDOI/CNKI are hard to verify (1 lead open). Historical ACI committee reports in ACI journals carry no committee designation in Crossref. Legacy Type IL topics (standards, dot, carbon, fresh) still need PLC-specific DOT specifications and EPD sources.'%(acc['abstract_metadata'],acc['doi_metadata'],acc['catalog_metadata'],acc['landing_page_inspected']))
def wj(path,obj,indent=2):
    tmp=path+'.tmp'; json.dump(obj,open(tmp,'w'),indent=indent,ensure_ascii=False); os.replace(tmp,path)
ids=[r['id'] for r in S['resources']]; assert len(ids)==len(set(ids))
urls=[r['url'].rstrip('/').lower() for r in S['resources']]; dupu=[u for u,c in collections.Counter(urls).items() if c>1]; assert not dupu,dupu
tt=[re.sub(r'\W+',' ',r['title'].lower()).strip() for r in S['resources']]; dupt=[u for u,c in collections.Counter(tt).items() if c>1 and u]; print('dup titles (pre-existing ok?):',dupt[:5])
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
summ=dict(n=n,first=first,last=last,newLeads=len(P['leads']),newPromoted=n,newRejected=0,open=openl,candStatus=dict(collections.Counter(c['status'] for c in CAN)),topics=dict(tc.most_common()),access=dict(acc),types=dict(collections.Counter(r['type'] for r in out)),decades=dict(sorted(collections.Counter(((r['date'] or '')[:3]+'0s') if r['date'] else 'undated' for r in out).items())),languages=dict(langs),citationChase=len(chase),current2026=len(cur),plcLegacyTopicRecords=len(plc))
wj(PD+'apply-summary.json',summ,1); print(json.dumps(summ,ensure_ascii=False))
# ---------- ledger
s1=json.load(open(PD+'search-log.json')); s2=json.load(open(PD+'search-log2.json'))
focus=['cross-durability','cross-tests-codes','cross-environment-cost','binder-cac-csa','binder-activated','binder-magnesium-carbonatable','scm-silica','scm-emerging','scm-slag','concrete-lightweight','binder-lc3']
web=['WebSearch: DIN 1045-2:2008-08 supersession (DIN Media / technischebaubestimmungen.de via search index)','WebSearch: Tanigawa Baba Mori 1984 ACI SP-82 (ACI abstracts portal)','curl: ACI International Concrete Abstracts Portal id 6549','curl: JaLC API 10.24517/00011725','curl: ChinaDOI resolver 10.14048/j.issn.1671-2579.2025.01.011 and 10.6052/j.issn.1000-4750.2021.01.0103','curl/WebFetch: engineeringmechanics.cn (HTTP 500 / timeout)','curl: kanazawa-u.repo.nii.ac.jp (503)']
rec=dict(id=PASS,date=VD,zone='America/Chicago',kind='daily-discovery+lead-verification',focusTopics=focus+['Type IL collection topics via Portland-limestone / carbonate-additions backfill (standards, dot, durability, strength, fresh, scm)','non-English literature (de, es, fr, pt, ja, zh)','citation chase from 2026-11-11 seeds'],currentAwareness=True,status='completed-unpublished (publisher to push)',
 repositories=['OpenAlex works API (title.search filter with period splits; language filter; relevance search for current awareness; referenced_works for backward citation chase)','Crossref works API (per-DOI)','DataCite API (EPFL thesis)','JaLC API','ChinaDOI resolver','doi.org resolver (HEAD)','ACI International Concrete Abstracts Portal','DIN Media catalogue (via search index)'],
 periods='1916–2026 (title.search split into pre-1985/≤1990/≤1995/≤2000/≤2005/≤2010/≤2012 and 1986–2005/1991–2010/1996–2015 windows; current sweep 2026-01 → 2026-11-12, mostly ≥2026-07)',languages=sorted(langs),
 apiQueries=[dict(e,harvest='harvest1') for e in s1]+[dict(e,harvest='harvest2-retry+citation-chase') for e in s2],webQueries=web,
 citationsFollowed=[dict(direction='backward',tool='OpenAlex referenced_works',seeds='79 records from pass-2026-11-11 dated <2005 with OpenAlex IDs',referencesFound=632,kept='cited by >=2 seeds or published <1995',promoted=len(chase))],
 uniqueApiHits=dict(harvest1=1882,harvest2=493,newAfterDedupe=1822+450),triage='Hits were screened by title (listing capped at 7 per query, 40 current, all citation-chase); 269 selected as leads and verified this pass. Screened out: book reviews, dental/medical/biology "cement", dye-adsorption uses of rice husk ash, soil-only stabilisation, finance and literature items, near-duplicate modern studies, no-DOI items not verifiable today. See research/pass-2026-11-12/listing.txt and select.py.',
 leadsProcessed=len(P['leads']),verifiedAdded=n,idRange='%s–%s'%(first,last),newLeadsRejected=0,openLeadsAfterPass=sum(1 for c in CAN if c['status']=='candidate'),openLeads=[dict(title=c['title'],reason=c['openReason']) for c in CAN if c['status']=='candidate'],
 verificationStatus=dict(acc),topicsTouched=dict(tc.most_common()),corrections=[],
 gaps=['Most journal items DOI-level only (Elsevier abstracts absent from Crossref/OpenAlex)','Non-English titles glossed from title/abstract only','Historical ACI committee reports/codes in ACI journals have no committee designation or author in Crossref','Chinese journal DOI 10.6052/j.issn.1000-4750.2021.01.0103 unverifiable today (publisher 500, CNKI timeout)','Book-level classics (Neville, Powers 1968 book, PCA Design and Control 1991) surfaced by the chase but had no DOI/registry record; not added'],
 nextSteps=['Next rotation head: standards, dot, carbon, fresh, strength, durability, scm, pavement (legacy Type IL topics need PLC-specific DOT specs/EPDs)','Forward citation chase (OpenAlex cites:) from today\'s classic seeds (Papadakis 1991, Diamond 1975, Mayfield 1988, Davidovits 1991)','Catalogue-level verification for no-DOI classics (Neville Properties of Concrete editions; PCA Design and Control editions; Powers 1949 non-evaporable water bulletin)','Retry engineeringmechanics.cn lead','More non-English national literature (JIS/GB/IS standards catalogues; Materiales de Construcción; Beton- und Stahlbetonbau)'],
 summary='Queue empty at start. %d new leads found and verified the same day: %d promoted, 0 rejected, %d open (host unreachable). %d verified additions %s–%s.'%(len(P['leads']),n,len(openl),n,first,last))
L['passes'].append(rec)
qby=collections.defaultdict(list)
MAPT={'pll-std':'scm-limestone','pll-dot':'scm-limestone','pll-carbon':'cross-environment-cost','pll-fresh':'scm-limestone','pll-strength':'scm-limestone','current-2026':None,'citation-chase':None}
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
        t['passStatus']='daily_pass_2026-11-12_backfill'; t['lastDeepPass']=PASS
        t['nextSteps']=['Forward citation chase from 2026-11-12 classics','Look for open institutional/government reports, older proceedings and non-English literature','Avoid repeating 2026-11-12 title.search queries (see ledger)']
q=L['globalNextQueue']; moved=[x for x in q if x['topicId'] in focus]; L['globalNextQueue']=[x for x in q if x['topicId'] not in focus]+[dict(x,reason='Backfilled in pass-2026-11-12; rotate to end') for x in moved]
L['updated']=VD; L['lastDeepPass']=PASS
L['stats']=dict(topics=59,resourcesAtStart=1622,resourcesAfterPass=len(S['resources']),verifiedAdded=n,candidatesTotal=len(CAN),candidatesOpen=sum(1 for c in CAN if c['status']=='candidate'),candidatesPromoted=sum(1 for c in CAN if c['status']=='promoted'),candidatesMatchedVerified=sum(1 for c in CAN if c['status']=='matched-verified'),candidatesRejected=sum(1 for c in CAN if c['status']=='rejected'),leadsProcessedThisPass=len(P['leads']),previous=L['stats'])
wj('research-ledger.json',L)
# ---------- index.md
md=open('index.md').read().split('\n')
assert md[1].startswith('Last updated: 2026-11-11')
md[1]='Last updated: 2026-11-12 (America/Chicago) — daily pass (%d verified additions). Daily research index; foundational coverage, not exhaustive. Historical records and gaps below are preserved; see expansion notes for current scope.'%n
o=['','## 2026-11-12 — daily pass (discovery + same-day lead verification)',
'Step 1 — queue: 0 open leads at start (nothing to resolve).',
'Step 2 — discovery: OpenAlex title.search queries (period-split) on the next least-covered rotation topics (cross-durability, cross-tests-codes, cross-environment-cost, binder-cac-csa, binder-activated, binder-magnesium-carbonatable, scm-silica, scm-emerging, scm-slag, concrete-lightweight, binder-lc3), language-filtered searches (de, fr, es, pt, ja, zh), a Portland-limestone/carbonate-additions backfill, a Jul–Nov 2026 current-awareness sweep and a backward citation chase (OpenAlex referenced_works) from 79 pre-2005 seeds added on 2026-11-11. %d leads selected from ~2,270 de-duplicated hits and verified the same day (Crossref/DataCite/JaLC/ChinaDOI per DOI + doi.org; ACI portal for one item whose listed DOI is unregistered).'%len(P['leads']),
'- Promoted: %d (%s–%s); rejected: 0; open: %d (%s).'%(n,first,last,len(openl),'; '.join(c['title'][:80]+' — '+c['openReason'][:160] for c in CAN if c['status']=='candidate')),
'- Evidence: abstract-level %d, DOI metadata only %d, catalogue/registry record %d, landing page read %d. Nothing full-text reviewed.'%(acc['abstract_metadata'],acc['doi_metadata'],acc['catalog_metadata'],acc['landing_page_inspected']),
'- Citation chase: %d records; non-English: %d (descriptions are English glosses); dated 2026: %d.'%(len(chase),len(noneng),len(cur)),
'- Corrections to existing records: none.','','### New verified resources (2026-11-12)']
for r in out:
    o.append(' | '.join([r['id'],','.join(r['topics']),r['title'],r['publisher'] or 'unknown',r['type'],r['date'] or 'undated',r['url']]))
    au=', '.join(a for a in (r['authors'] or []) if a) if r.get('authors') else 'unknown'
    o.append('  Note: Authors: %s. %s Access: %s. %s%s'%(au,r['description'],r['access'],r['evidenceNote'],(' Edition: '+r['edition']) if r.get('edition') else ''))
o+=['','### Open leads (2026-11-12)']+['- [open] %s — %s'%(c['title'][:110],c['openReason']) for c in CAN if c['status']=='candidate']
open('index.md.tmp','w').write('\n'.join(md).rstrip('\n')+'\n'+'\n'.join(o)+'\n'); os.replace('index.md.tmp','index.md')
# ---------- Page chunk data
pg=[[r['id'],r['title'],r['publisher'] or '',r['type'],r['date'] or '',','.join(r['topics']),r['url']] for r in out]
json.dump(dict(rows=pg,news=S['whatsNew'][0],change=S['changeLog'][-1],gap=S['gaps'][0],total=len(S['resources']),takeaways={k:tmap[k]['takeaways'][-1] for k in TK}),open(PD+'page-d1112.json','w'),ensure_ascii=False,indent=0)
print('done',first,last,len(S['resources']))
