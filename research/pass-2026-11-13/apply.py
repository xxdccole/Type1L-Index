"""pass-2026-11-13 apply: old-lead outcome (R1892) + new verified records R1893+ and lead outcomes into working files (atomic writes). Run once from pre-pass state.
Derived from research/pass-2026-11-12/apply.py and pass-2026-11-11/apply.py (old-lead handling)."""
import json,os,re,collections
os.chdir('/workspace/type1l-index'); VD='2026-11-13'; PASS='pass-2026-11-13'; PD='research/pass-2026-11-13/'
P=json.load(open(PD+'plan.json'))
S=json.load(open('site-data.json')); L=json.load(open('research-ledger.json')); N=json.load(open('research/resource-notes.json'))
VER=[json.loads(l) for l in open('research/portable/verified-sources.jsonl')]
CAN=[json.loads(l) for l in open('research/portable/candidates.jsonl')]
NBEFORE=len(S['resources'])
assert NBEFORE==1890 and S['resources'][-1]['id']=='R1891' and S['lastUpdated']=='2026-11-12','expected pre-pass state'
assert [i for i,c in enumerate(CAN) if c['status']=='candidate']==[1638],'expected 1 open lead'
assert not any(r['id']=='R428' for r in S['resources'])
before={r['id']:json.dumps(r,sort_keys=True) for r in S['resources']}
out=[]; nxt=1892
def mk(r,origin,cidx=None):
    global nxt
    rid='R%d'%nxt; nxt+=1
    S['resources'].append({'id':rid,'title':r['title'],'publisher':r['publisher'],'type':r['type'],'date':r['date'],'url':r['url'],'topics':list(r['topics'])})
    out.append(dict(id=rid,status='verified',title=r['title'],authors=r.get('authors'),publisher=r['publisher'],type=r['type'],date=r['date'],url=r['url'],doi=r.get('doi'),identifiers=r.get('ids') or {},topics=list(r['topics']),geography=r.get('geo'),language=r.get('lang','en'),description=r['desc'],access=r['access'],evidenceNote=r['evidence'],edition=r.get('edition'),rights=r.get('rights'),version=None,verifiedOn=VD,provenance=PASS,origin=origin,promotedFromCandidate=True,candidateIndex=cidx,added=VD))
    N[rid]=r['evidence']; return rid
# ---------- STEP 1: old open lead (candidates[1638])
OLD=(1638,dict(title='水泥混凝土路面板早龄期徐变效应研究 (Early-age creep effects of cement concrete pavement)',authors=['胡昌斌 (HU Chang-bin)','孙增华 (SUN Zeng-hua)','王丽娟 (WANG Li-juan)'],publisher='《工程力学》杂志社 (Engineering Mechanics)',type='Paper',date='2022-03-25',
  url='https://doi.org/10.6052/j.issn.1000-4750.2021.01.0103',doi='10.6052/j.issn.1000-4750.2021.01.0103',ids={'journal':'工程力学 (Engineering Mechanics) 39(4):123–137','issn':'1000-4750','onlineFirst':'2021-04-28','openalex':'W3217108968'},
  topics=['concrete-pavement-pervious','cross-mechanics','pavement'][:2],geo='China',lang='zh',
  desc='Chinese-language paper (English abstract) that builds a 3D simulation of early-age pavement-slab behaviour using a microprestress–solidification creep model with material, structural and environmental inputs; creep acts as relaxation that markedly reduces early-age curling and stress, is comparable in magnitude to temperature-gradient and edge-restraint effects, is strongest in the first 7 days and stabilises after about 60 days; ignoring temperature effects on creep under- or over-estimates it (abstract-level).',
  access='landing_page_inspected',rights='Landing page states CC BY 3.0 (http://creativecommons.org/licenses/by/3.0/).',
  evidence='Resolved open lead (2026-11-12: publisher host HTTP 500, CNKI timeout). 2026-11-13: DOI resolves at doi.org (handle registered 2021-04-28) but has no Crossref record; the https publisher page engineeringmechanics.cn/cn/article/doi/10.6052/j.issn.1000-4750.2021.01.0103 returned 200 and its citation metadata were read (Chinese and English titles, three authors, 工程力学 2022 vol 39 no 4 pp 123–137, online 2021-04-28, keywords, Chinese and English abstracts, CC BY 3.0). OpenAlex lists an older online-first pagination (vol 38, pp 1–15, 2021); the issue pagination from the publisher page is used. Paper text not reviewed.'))
i,r=OLD; rid=mk(r,'candidate-queue',[i]); x=CAN[i]
x.update(status='promoted',promotedTo=rid,promotedOn=VD,reviewedOn=VD,reviewPass=PASS,lastCheckedOn=VD); x.pop('openReason',None)
oldout={i:('promoted',rid)}
# ---------- STEP 2: new verified records
k2id={}
for r in P['recs']:
    k2id[r['_key']]=mk(r,'discovery-'+PASS)
oldN=len(CAN); newlead={}; openl=[]
for ld in P['leads']:
    k=ld.pop('_key'); ld['pass']=ld.pop('pass_')
    if '_open' in ld:
        ld['openReason']=ld.pop('_open'); ld['status']='candidate'; ld['lastCheckedOn']=VD; openl.append(ld['title'])
    elif k in k2id: ld.update(status='promoted',promotedTo=k2id[k],promotedOn=VD)
    else:
        cat,reason,dup=P['rejected'][k]; ld.update(status='rejected',rejectCategory=cat,rejectReason=reason,duplicateOf=dup)
    CAN.append(ld); newlead[k]=len(CAN)-1
i2k={v:k for k,v in k2id.items()}
for f in out[1:]: f['candidateIndex']=[newlead[i2k[f['id']]]]
first,last=out[0]['id'],out[-1]['id']; nfirst=out[1]['id']
# ---------- membership union
tmap={t['id']:t for t in S['topics']}; byid={r['id']:r for r in S['resources']}
for r in S['resources']:
    for t in r['topics']:
        if r['id'] not in tmap[t]['resourceIds']: tmap[t]['resourceIds'].append(r['id'])
for t in S['topics']:
    for i_ in t['resourceIds']:
        if t['id'] not in byid[i_]['topics']: byid[i_]['topics'].append(t['id'])
for r in S['resources'][:NBEFORE]: assert json.dumps(r,sort_keys=True)==before[r['id']],r['id']
n=len(out); nnew=n-1
rejn=sum(1 for c in CAN[oldN:] if c['status']=='rejected')
tc=collections.Counter(t for r in out for t in r['topics'])
acc=collections.Counter(r['access'] for r in out)
langs=collections.Counter(r['language'] for r in out)
chase=[f['id'] for f in out if 'backward citation chase' in f['evidenceNote']]
fwd=[f['id'] for f in out if 'forward citation chase' in f['evidenceNote']]
cur=[f['id'] for f in out if (f['date'] or '').startswith('2026')]
noneng=[f['id'] for f in out if f['language']!='en']
TK={
'binder-portland':'Nov 13 backfill (DOI/abstract level): Portland clinker and cement classics — Shepherd & Rankin 1911 ternary CaO–Al2O3–SiO2 system, 1960s–70s clinker microscopy (prismatic/interstitial phases, SEM, XRD minor phases), alkalies in cement (Jawed & Skalny 1977), sulfate-resisting cement (Gollop & Taylor 1994/1995), low-heat Portland cement (incl. 2023 review), alite/belite and alite–belite–ye\'elimite cements, early air-entrainment papers (Powers 1954 void spacing, 1946–1959 ACI) (%s).',
'scm-flyash':'Nov 13 backfill: fly-ash reaction and pozzolanicity (Fraay et al. 1989; Marsh & Day 1988; 2019 multiphase model), high-volume fly ash (Bilodeau & Malhotra 2000; Poon et al. 2000; Siddique 2004; Wang & Li 2007 HVFA-ECC), Class C ash (ASR mitigation, abrasion), fly-ash fineness studies, early proportioning papers (1958, 1968, 1976) and an Oct 2026 current sweep (%s).',
'concrete-fibers':'Nov 13 backfill: steel fibre reinforced concrete 1972–1993 (orientation, shear/moment, punching, marine chloride), steel fibre–cement interface studies (1978, 1985), GRC microstructure and durability (1974–2001), hybrid and polypropylene fibres at high temperature, PVA-ECC (Li et al. 2001/2002) and self-healing ECC, basalt fibres and textile-reinforced concrete/mortar incl. RILEM TC 232-TDT (%s).',
'concrete-scc':'Nov 13 backfill: self-compacting concrete design and performance — Su et al. 2001 mix design, Domone 2006 case studies, Khayat 1997/1999 VMA and workability testing, passing ability (J-Ring ASTM C1621 record), rheology with fillers/recycled fines, SCC with fly ash, slag, limestone filler (%s). DOI/abstract level.',
'concrete-architectural':'Nov 13 backfill (bibliographic level): efflorescence in geopolymer binders, iron-oxide and other pigments in concrete, white cement concrete, fair-faced concrete (incl. dark discoloration in JACT 2008), algal fouling of white architectural concrete, and the Hennebique system history in Italy (%s).',
'concrete-polymer-refractory':'Nov 13 backfill: polymer-modified and latex-modified mortar/concrete (Ohama 1987; Kardon 1997 review; SBR latex durability), polymer-impregnated concrete 1971, polymer film formation, refractory castables (Lee et al. 2001 review; ultra-low-cement castable drying, permeability and hydration of bond systems) and corundum fibre-reinforced refractory concrete (Russian) (%s).',
'concrete-pavement-pervious':'Nov 13 backfill: pavement curling and built-in curl (TRR/JTE 1997–2009), dowel-bar load transfer, pervious concrete pore structure, clogging and porosity test (2005–2011), porous concrete strength–porosity, PLC pavement mixes (Florida 2023; 2025 meta-analysis), Iowa PCC deterioration (1996) and the resolved Chinese early-age creep lead (%s).',
'concrete-repair-grout-overlay':'Nov 13 backfill: repair compatibility (Emberson & Mays 1996 property mismatch series), patch-repair macrocell corrosion and sacrificial anodes, cathodic protection reviews (1993–2016), bonded overlays and differential shrinkage (Beushausen & Alexander 2006), cement grouts for rock and repair, magnesium-phosphate rapid-repair mortars and Broomfield\'s Corrosion of Steel in Concrete (book) (%s).',
'concrete-precast-insitu-print':'Nov 13 backfill: early steam-curing papers (Magazine of Concrete Research 1949/1951) and SCM steam curing, precast connections and sandwich panels (ACI/PCI 1966–1995), slipforming, 3D-printed concrete interlayer bond, early-age modelling and printability reviews, injection 3D concrete printing (German, Oct 2026) (%s).',
'concrete-circular':'Nov 13 backfill: recycled-aggregate classics found by citation chase (Nixon 1978 review; Frondistou-Yannas 1977; Malhotra 1976; Hansen & Narud 1983; Hansen & Boegh 1985), 2000s RAC mechanics/ITZ/fine RA studies, C&D waste reviews and CO2 curing of recycled aggregates and blocks (%s).',
'concrete-hpc':'Nov 13 backfill: ACI 1984 state-of-the-art on high-strength concrete, high-temperature behaviour (Khoury 1992; Castillo & Durrani 1990), confinement of HSC columns (Cusson & Paultre 1994), RPC durability (Roux et al. 1996) and mineral admixtures, UHPC tensile/compressive test methods and characterisation, autogenous shrinkage reviews (%s).',
'microcracking':'Nov 13: interfacial-zone and microcracking classics via citation chase — Barnes, Diamond & Dolch 1978 glass-aggregate contact zone and 1979 interfacial-zone micromorphology, Monteiro, Maso & Ollivier 1985 aggregate–mortar interface, steel/mortar interfaces 1979, drying-shrinkage microcracking 1984, submicrocracking 1987 — plus ITZ studies of blended composites and French TEM work on paste–aggregate bond (1975) (%s).',
'scm-limestone':'Nov 13 PLC/limestone backfill: forward citers of Tsivilis 1999 and the 1991 limestone-filled cement papers (De Weerdt et al. 2011 ternary limestone–fly ash; Ipavec et al. 2010 carboaluminates; Lothenbach 2010 thermodynamics; Torres et al. 2003 and Hartshorn et al. 2001 PLC mortars in magnesium sulfate), limestone filler sulfate-attack review (Irassar 2009), CEMHYD3D modelling, rheology/chemical shrinkage with filler, PLC concrete pavements and FE heat-of-hydration with limestone blended cement (%s).',
}
for tid,txt in TK.items():
    ids=[f['id'] for f in out if tid in f['topics']]
    tmap[tid]['takeaways'].append(txt%('%s–%s, %d records'%(ids[0],ids[-1],len(ids)) if ids else 'none'))
plc=[f['id'] for f in out if any(t in f['topics'] for t in ('standards','dot','carbon','fresh','strength','durability','scm','intl','apps','pavement','mix','field','mass','microcracking'))]
# ---------- narrative
S['lastUpdated']=VD
S['whatsNew'].insert(0,{'date':'Nov 13','title':'Daily pass: %d verified additions (%s–%s)'%(n,first,last),'detail':'Resolved the one lead left open on Nov 12 (Chinese Engineering Mechanics paper on early-age creep of concrete pavement slabs, %s; publisher page reachable today). Discovery added %d verified sources focused on the next least-searched families — Portland clinker/cement classics and air entrainment, fly ash, fibre-reinforced concrete and ECC, self-compacting concrete, architectural/white/pigmented concrete, polymer-modified and refractory concrete, pavements and pervious concrete, repair/overlays/grouts and cathodic protection, precast/steam curing/3D printing, recycled-aggregate concrete and high-strength/UHPC — plus %d records from a backward citation chase and %d from a forward citation chase of Nov 12 seeds, %d non-English records (German, French, Spanish, Italian, Russian, Turkish, Polish, Korean, Chinese; English glosses), a Portland-limestone backfill for the Type IL topics (pavement, mix, mass, microcracking) and an Oct–Nov 2026 current-awareness sweep (%d records dated 2026). %d new leads rejected as duplicates; 3 left open (hosts unreachable or DOI unregistered). Mostly DOI/abstract-level, not full-text reviews.'%(first,nnew,len(chase),len(fwd),len(noneng),len(cur),rejn)})
S['changeLog'].append({'date':VD,'entry':'Daily pass 2026-11-13: %d verified additions %s–%s (%s promoted from the 1 previously open lead; %d from new discovery: title.search backfill with period splits, language-filtered searches in new languages, PLC legacy-topic backfill, current-awareness sweep, backward and forward citation chase from 2026-11-12 seeds). %d new leads found: %d promoted, %d rejected as duplicates (R1185 conference paper, two chapter-level records of a book indexed instead, one duplicate journal printing), %d left open. No corrections to existing records. R1–R1891 preserved (R428 still retired); topic membership union maintained.'%(n,first,last,first,nnew,len(P['leads']),nnew,rejn,len(openl))})
S['gaps'].insert(0,'Daily pass 2026-11-13: additions are registry/catalogue-verified (%d abstract-level, %d DOI metadata only, %d catalogue records, %d landing pages read) — not full-text reviewed. Many Elsevier items have no abstract in Crossref/OpenAlex, so descriptions are bibliographic only. ~45 no-DOI classics surfaced by the citation chase (TRID/HRB reports, CiNii-listed books such as Bažant\'s creep monographs and Mehta\'s Materials Science of Concrete, Czech/Belgian theses incl. the 1950s Purdocement alkali-activated slag study) could not be inspected today (TRID 503, CiNii/JS-only pages) and were not added. ACI symposium papers carry ACI DOIs that are not registered at doi.org. 3 leads open (Kraków Technical Transactions DOIs without Crossref metadata; one Zenodo DOI unregistered).'%(acc['abstract_metadata'],acc['doi_metadata'],acc['catalog_metadata'],acc['landing_page_inspected']))
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
summ=dict(n=n,first=first,last=last,oldLeads={str(k):v for k,v in oldout.items()},newLeads=len(P['leads']),newPromoted=nnew,newRejected=rejn,open=openl,candStatus=dict(collections.Counter(c['status'] for c in CAN)),topics=dict(tc.most_common()),access=dict(acc),types=dict(collections.Counter(r['type'] for r in out)),decades=dict(sorted(collections.Counter(((r['date'] or '')[:3]+'0s') if r['date'] else 'undated' for r in out).items())),languages=dict(langs),citationChaseBackward=len(chase),citationChaseForward=len(fwd),current2026=len(cur),typeILLegacyTopicRecords=len(plc))
wj(PD+'apply-summary.json',summ,1); print(json.dumps(summ,ensure_ascii=False))
# ---------- ledger
s1=json.load(open(PD+'search-log.json')); s2=json.load(open(PD+'search-log2.json'))
focus=['binder-portland','scm-flyash','concrete-fibers','concrete-scc','concrete-architectural','concrete-polymer-refractory','concrete-pavement-pervious','concrete-repair-grout-overlay','concrete-precast-insitu-print','concrete-circular','concrete-hpc']
web=['curl: engineeringmechanics.cn https landing page (200; citation metadata) and doi.org handle API for 10.6052/j.issn.1000-4750.2021.01.0103','curl: ACI International Concrete Abstracts Portal ids 17530, 17535, 17327, 17620, 6739, 9140, 2380','curl: NRC Publications Archive (Ramachandran 1976)','curl: Lund University Publications 1292206','curl: REAL-EOD 14262 (Biczók 1967)','curl: IRIS Politecnico di Torino 11583/1393757','curl: newogneup.elpub.ru article 25','curl: doi.org RA lookup for 10.4467; ejournals.eu and suw.biblos.pk.edu.pl (HTTP 500)','curl: journals.ayu.edu.kz (HTTP 500)','curl: no-DOI landing pages — TRID (503), pubsindex.trb.org/CiNii/EPFL/NCSU (500), CiNii CRID (202), DSpace 7/Primo (JS-only), ROSA P (403)']
rec=dict(id=PASS,date=VD,zone='America/Chicago',kind='daily-discovery+lead-verification',focusTopics=focus+['Type IL collection topics via Portland-limestone / limestone-filler backfill (pavement, mix, field, mass, microcracking, apps, strength, durability, fresh, scm)','non-English literature (new: it, nl, ru, pl, cs, tr, ko; plus de/fr/es/ja with new terms/periods)','backward and forward citation chase from 2026-11-12 seeds'],currentAwareness=True,status='completed-unpublished (publisher to push)',
 repositories=['OpenAlex works API (title.search with period splits; language filter; relevance search for current awareness and PLC topics; referenced_works backward chase; cites: forward chase)','Crossref works API (per-DOI)','DataCite API (Magazine of Civil Engineering, Zenodo, UT Austin)','doi.org resolver (HEAD; handle API; RA lookup)','ACI International Concrete Abstracts Portal','NRC Publications Archive (Canada)','Lund University Publications','REAL-EOD (Hungarian Academy of Sciences Library)','IRIS Politecnico di Torino','Novye Ogneupory journal site (elpub)','engineeringmechanics.cn (publisher page)'],
 periods='1895–2026 (title.search windows ≤1975/≤1980/≤1985/≤1990/≤1995/≤2000/≤2005/≤2012, 1986–2000/1990–2005/1991–2010/1996–2010/2001–2015/2006–2015/2011–2026; current sweep 2026-08 → 2026-11-12, mostly ≥2026-09; forward chase ≤2010 and 2024–2026)',languages=sorted(langs),
 apiQueries=[dict(e,harvest='harvest1') for e in s1]+[dict(e,harvest='harvest2-citation-chase') for e in s2],webQueries=web,
 citationsFollowed=[dict(direction='backward',tool='OpenAlex referenced_works',seeds='120 records from pass-2026-11-12 dated <2000 with OpenAlex IDs',referencesFound=570,kept='cited by >=2 seeds or published <1990 (442 kept before dedupe)',promoted=len(chase)),
   dict(direction='forward',tool='OpenAlex cites:',seeds='R1634 Davidovits 1991, R1713 Mayfield 1988, R1744 Diamond 1975, R1747 Papadakis 1991, R1686 Tsivilis 1999, R1704 limestone-filled cements 1991',kept='top 12 citers ≤2010 + top 6 citers 2024–2026 per seed by citation count',promoted=len(fwd))],
 uniqueApiHits=dict(harvest1=2384,harvest2=528,newAfterDedupe=2244+470),triage='Hits screened by title (listing capped at 7 per query, 40 current, all backward-chase and forward-chase hits): 725 picked, 49 no-DOI picks dropped because their catalogue/landing pages could not be inspected today, 676 leads verified this pass. Screened out: book reviews, discussions, FRP-only structural papers, machining, geology "limestone cement", medical "Zement", finance, soil-only, ML-prediction papers in minor venues, a Figshare mirror. See research/pass-2026-11-13/listing.txt and select.py.',
 leadsProcessed=1+len(P['leads']),oldLeadOutcomes={str(k):v for k,v in oldout.items()},verifiedAdded=n,idRange='%s–%s'%(first,last),newLeadsRejected=rejn,openLeadsAfterPass=sum(1 for c in CAN if c['status']=='candidate'),openLeads=[dict(title=c['title'],reason=c['openReason']) for c in CAN if c['status']=='candidate'],
 verificationStatus=dict(acc),topicsTouched=dict(tc.most_common()),corrections=[],
 gaps=['Most journal items DOI-level only (Elsevier abstracts absent from Crossref/OpenAlex)','Non-English titles glossed from title/abstract only','~45 no-DOI chase classics not inspectable today (TRID 503; CiNii; JS-only DSpace/Primo) — e.g. Powers 1949 air requirement (HRB), Mehta 1986/1989 Materials Science of Concrete, Bažant 1982/1988 creep books, Purdocement 1950s AAS (UGent), Kansas/ROSA P DOT reports','ACI symposium/journal DOIs (10.14359/…) unregistered; ACI portal used','Possible correction: R1185 (TRID record of the 1987 ASTM C1012 paper) could carry its ACI DOI 10.14359/… once registered','3 open leads (2 Kraków Technical Transactions DOIs without Crossref metadata, 1 Zenodo DOI unregistered)'],
 nextSteps=['Next rotation head: binder-specialty, binder-white-masonry, binder-well, binder-international, scm-natural, scm-clay, concrete-shotcrete, concrete-heavyweight, concrete-cellular, concrete-mass-rcc, cross-construction (least-recently backfilled)','Retry TRID-hosted no-DOI classics via an alternative route (TRID search index / HathiTrust / NTL) and CiNii books via NDL/WorldCat','Retry 3 open leads (ejournals.eu, Zenodo)','Forward citation chase from today\'s classics (Powers 1954 void spacing, Fraay 1989, Li PVA-ECC 2001, Okamura SCC)','More non-English national literature (Czech/Slovak theses, Italian/Dutch journals, Russian/Chinese standards catalogues)'],
 summary='1 old lead promoted (%s). %d new leads found and verified the same day: %d promoted, %d rejected (duplicates), %d open. %d verified additions %s–%s.'%(first,len(P['leads']),nnew,rejn,len(openl),n,first,last))
L['passes'].append(rec)
qby=collections.defaultdict(list)
MAPT={'pll-pavement':'pavement','pll-mix':'mix','pll-field':'field','pll-mass':'mass','pll-micro':'microcracking','pll-apps':'apps','pll-ttl':'scm-limestone','current-2026':None,'citation-chase':None,'citation-chase-fwd':None}
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
        t['passStatus']='daily_pass_2026-11-13_backfill'; t['lastDeepPass']=PASS
        t['nextSteps']=['Forward citation chase from 2026-11-13 classics','Look for open institutional/government reports, older proceedings and non-English literature','Avoid repeating 2026-11-13 title.search queries (see ledger)']
q=L['globalNextQueue']; moved=[x for x in q if x['topicId'] in focus]; L['globalNextQueue']=[x for x in q if x['topicId'] not in focus]+[dict(x,reason='Backfilled in pass-2026-11-13; rotate to end') for x in moved]
L['updated']=VD; L['lastDeepPass']=PASS
L['stats']=dict(topics=59,resourcesAtStart=NBEFORE,resourcesAfterPass=len(S['resources']),verifiedAdded=n,candidatesTotal=len(CAN),candidatesOpen=sum(1 for c in CAN if c['status']=='candidate'),candidatesPromoted=sum(1 for c in CAN if c['status']=='promoted'),candidatesMatchedVerified=sum(1 for c in CAN if c['status']=='matched-verified'),candidatesRejected=sum(1 for c in CAN if c['status']=='rejected'),leadsProcessedThisPass=1+len(P['leads']),previous=L['stats'])
wj('research-ledger.json',L)
# ---------- index.md
md=open('index.md').read().split('\n')
assert md[1].startswith('Last updated: 2026-11-12')
md[1]='Last updated: 2026-11-13 (America/Chicago) — daily pass (1 old lead resolved; %d verified additions). Daily research index; foundational coverage, not exhaustive. Historical records and gaps below are preserved; see expansion notes for current scope.'%n
o=['','## 2026-11-13 — daily pass (old lead resolved + discovery + same-day lead verification)',
'Step 1 — queue: 1 open lead at start (Engineering Mechanics 10.6052/j.issn.1000-4750.2021.01.0103). Publisher page reachable over https today; promoted as %s.'%first,
'Step 2 — discovery: OpenAlex title.search queries (period-split) on the next least-searched families (binder-portland, scm-flyash, concrete-fibers, concrete-scc, concrete-architectural, concrete-polymer-refractory, concrete-pavement-pervious, concrete-repair-grout-overlay, concrete-precast-insitu-print, concrete-circular, concrete-hpc), language-filtered searches (it, nl, ru, pl, cs, tr, ko new; de/fr/es/ja with new terms), a Portland-limestone/limestone-filler backfill for Type IL topics (pavement, mix, field, mass, microcracking, apps), an Aug–Nov 2026 current-awareness sweep, a backward citation chase (OpenAlex referenced_works) from 120 pre-2000 seeds added on 2026-11-12 and a forward chase (OpenAlex cites:) from six classics. %d leads selected from ~2,700 de-duplicated hits and verified the same day (Crossref/DataCite per DOI + doi.org; ACI portal, NRC, Lund, REAL-EOD, IRIS and journal pages for items without a registered DOI).'%len(P['leads']),
'- Promoted: %d (%s–%s); rejected: %d (duplicates: R1185 conference paper; two chapter-level records of Broomfield\'s Corrosion of Steel in Concrete, book indexed instead; Hansson 1995 duplicate printing in Metall. Mater. Trans. B); open: %d.'%(nnew,nfirst,last,rejn,len(openl)),
'- Evidence: abstract-level %d, DOI metadata only %d, catalogue/registry record %d, landing page read %d. Nothing full-text reviewed.'%(acc['abstract_metadata'],acc['doi_metadata'],acc['catalog_metadata'],acc['landing_page_inspected']),
'- Citation chase: %d backward, %d forward; non-English: %d (descriptions are English glosses); dated 2026: %d.'%(len(chase),len(fwd),len(noneng),len(cur)),
'- Corrections to existing records: none.','','### New verified resources (2026-11-13)']
for r in out:
    o.append(' | '.join([r['id'],','.join(r['topics']),r['title'],r['publisher'] or 'unknown',r['type'],r['date'] or 'undated',r['url']]))
    au=', '.join(a for a in (r['authors'] or []) if a) if r.get('authors') else 'unknown'
    o.append('  Note: Authors: %s. %s Access: %s. %s%s'%(au,r['description'],r['access'],r['evidenceNote'],(' Edition: '+r['edition']) if r.get('edition') else ''))
o+=['','### Open leads (2026-11-13)']+['- [open] %s — %s'%(c['title'][:110],c['openReason']) for c in CAN if c['status']=='candidate']
open('index.md.tmp','w').write('\n'.join(md).rstrip('\n')+'\n'+'\n'.join(o)+'\n'); os.replace('index.md.tmp','index.md')
# ---------- Page chunk data
pg=[[r['id'],r['title'],r['publisher'] or '',r['type'],r['date'] or '',','.join(r['topics']),r['url']] for r in out]
json.dump(dict(rows=pg,news=S['whatsNew'][0],change=S['changeLog'][-1],gap=S['gaps'][0],total=len(S['resources']),takeaways={k:tmap[k]['takeaways'][-1] for k in TK}),open(PD+'page-d1113.json','w'),ensure_ascii=False,indent=0)
print('done',first,last,len(S['resources']))
