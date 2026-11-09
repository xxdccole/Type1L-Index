import json,copy,collections
VD='2026-11-09'
exec(open('research/pass-2026-11-09/new_records.py').read())
S=json.load(open('site-data.json'))
L=json.load(open('research-ledger.json'))
N=json.load(open('research/resource-notes.json'))
start=max(int(r['id'][1:]) for r in S['resources'])+1
assert start==204
recs=[]
for k,r in enumerate(R):
    rid='R%d'%(start+k)
    url=r.get('url') or 'https://doi.org/'+r['doi']
    site={'id':rid,'title':r['title'],'publisher':r['publisher'],'type':r['type'],'date':r['date'],'url':url,'topics':r['topics']}
    S['resources'].append(site)
    full=dict(id=rid,status='verified',title=r['title'],authors=r.get('authors'),publisher=r['publisher'],type=r['type'],date=r['date'],url=url,doi=r.get('doi'),identifiers=r.get('ids') or {},topics=r['topics'],geography=r.get('geo'),language=r.get('lang','en'),description=r['desc'],access=r['access'],evidenceNote=r['evidence'],edition=r.get('edition'),rights=r.get('rights'),version=None,verifiedOn=VD,provenance='deep-pass-2026-11-09',origin=r['origin'],added=VD)
    recs.append(full)
    N[rid]=r['evidence']
# topic membership
tmap={t['id']:t for t in S['topics']}
for f in recs:
    for t in f['topics']:
        if f['id'] not in tmap[t]['resourceIds']: tmap[t]['resourceIds'].append(f['id'])
def ids(t): return [f['id'] for f in recs if t in f['topics']]
def rng(t):
    x=ids(t); return ', '.join(x)
TK={
'binder-portland':"Pass 2 (2026-11-09) historical backfill: NBS Lerch & Bogue 1934 heat of hydration and Flint & Wells 1941 hydrogarnet/sulfate work, Taylor's 1989 Bogue modification, NISTIR 4785 reference-clinker XRD and a 2022 history review ({}). Historic data explain Type II/IV/V logic; current ASTM C150 limits still govern.",
'binder-white-masonry':"Pass 2: NBS Monograph 36 (1961) shows bond strength dominated wall racking/flexure; repair-mortar guidance for traditional masonry, white clinker defects and LBNL albedo data showing white-cement concrete markedly more reflective ({}). Still no current ASTM C91/C1328/C1329 text reviewed.",
'concrete-heavyweight':"Pass 2: gamma and neutron shielding evidence (barite/magnetite/goethite/serpentine HPC; 2021 neutron and 2024 radiation-shielding reviews; ferrophosphorus weighting for well cement) ({}). Lab/review evidence; shielding design requires project-specific nuclear analysis and ACI 349/NRC-type requirements not reviewed.",
'concrete-fibers':"Pass 2: Zollo 1997 30-year FRC overview, steel vs macro-synthetic workability/air study and a GFRC review ({}). ACI 544 documents and EN 14651/ASTM C1609 residual-strength methods remain to be reviewed.",
'concrete-mass-rcc':"Pass 2: 2010 CP Tech Center RCC pavement guide (full PDF), gyratory mix-design procedure and natural-pozzolan RCC scaling study; NBS 1934 heat data also tagged ({}). RCC dam practice (USACE EM 1110-2-2006, USBR) still open; ACI 327 spec expected 2027 per NRMCA report.",
'concrete-polymer-refractory':"Pass 2: 1973 BNL/USBR concrete-polymer topical report, 1988 polymer concrete mechanics, 2020 polymer-modified mortar comparison ({}). Refractory castable practice still thin; ACI 548 documents not re-reviewed.",
'concrete-scc':"Pass 2: Okamura & Ouchi originators' papers (2000 fib; 2003 JACT), UT Austin aggregates-in-SCC research, PCI girder bond/transfer length and a formwork-pressure review ({}). ACI 237R and EN 206 Annex G/EFNARC not yet reviewed.",
'scm-flyash':"Pass 2: Class F durability study, TxDOT 5,500-sample fly ash database and ASR index, ASR-mitigation state-of-art ({}). Harvested/landfilled ash qualification (ASTM C618 updates) and supply data remain gaps.",
'scm-limestone':"Pass 2: carboaluminate (2001), early filler-strength (1977), 2018 review and limestone-cement sulfate microstructure (2003) studies; also CEM II/C-M/CEM VI data ({}). Mostly DOI-level metadata; full texts closed.",
'scm-natural':"Pass 2: Roman concrete volcanic ash (2009) and hot-mixing lime clast mechanism (2023), secondary-mineral effects on pozzolanicity (2008), Trass RCC case ({}). ASTM C618 Class N current-edition review still pending.",
'binder-international':"Pass 2 / current: EN 197-6:2023 RCF cements (preview), Dutch EN 197 overview incl. NEN 8005/CUR 48 rule, Swiss SIA 215/1 (2025) and SN EN 206 ND (2025) paper, Polish CEM II/C-M & CEM VI concrete data ({}). China GB 175 and India IS 269/1489 still not covered by verified sources.",
'concrete-architectural':"Pass 2: TU Delft historic concrete thesis (Dutch surface finishes), bughole image analysis, LBNL concrete albedo study ({}). ACI 303R architectural cast-in-place guidance and CIB/DIN 18217 surface classes not yet reviewed.",
}
for t,txt in TK.items():
    tmap[t]['takeaways'].append(txt.format(rng(t)))
# R40 correction (date refinement)
for r in S['resources']:
    if r['id']=='R40' and r['date']=='2026':
        r['date']='2026-08-01'
N['R40']=(N.get('R40','')+' ' if N.get('R40') else '')+'2026-11-09: date refined to 2026-08-01 (ASTM store, Accuris and NBS publication index all show C595/C595M-26 published 2026-08-01, superseding C595/C595M-25).'
N['R97']=(N.get('R97','')+' ' if N.get('R97') else '')+'2026-11-09: same article now registered with DOI 10.70909/aca.2026.sn3370 (ACA SN3370, Crossref issued 2026-11-06). Not added as a separate resource (same work).'
S['lastUpdated']=VD
S['whatsNew'].insert(0,{'date':'Nov 9','title':'Deep research pass 2 + 2026 current-awareness sweep','detail':'Added 49 verified sources R204–R252: 12 rotated topics (Portland I–V history, white/masonry, heavyweight/shielding, fibers, RCC, polymer, SCC, fly ash, limestone, natural pozzolans, international CEM, architectural), 2026 standards/committee news (ACI Fall 2026 committee status, ACI CODE-323-24 preview, EN 197-6, Swiss SIA 215/1 paper, Dutch EN 197 explainer, blended-cement dataset) and 4 promoted candidates. R40 date refined; R97 DOI noted. Not exhaustive.'})
S['changeLog'].append({'date':VD,'entry':'Deep research pass 2: current-awareness sweep plus historical backfill of 12 least-covered queued topics; appended 49 verified records R204–R252 (45 new from pass-2 searches, 4 promoted from candidate queue). Corrected R40 date to 2026-08-01. R1–R203 otherwise preserved.'})
S['gaps'].insert(0,'Pass 2 (2026-11-09) is a second batch, not complete coverage. Many pass-2 records are DOI/abstract-level (closed full text); access level is recorded per record in research/portable/verified-sources.jsonl. Still open: China GB 175 / India IS standards, ACI 544/237R/303R/207 texts, USACE/USBR RCC dam manuals, ASTM C91/C270/C618 current-edition reviews, refractory castables practice.')
S['keyIssues'].append('2026 standards movement: ASTM C595-26 (published 2026-08-01) adds Type IC and changes Type IL sulfate testing; ACI 332-26 residential code tentatively Nov 2026; ACI 301 revision expected 2027; ACI 323 next edition and ACI 201 PLC durability report in development (NRMCA Fall 2026 convention report, R204). Verify adoption status before specifying.')
# membership sanity
allids={r['id'] for r in S['resources']}
for t in S['topics']:
    assert all(i in allids for i in t['resourceIds'])
    t.pop('resourceCount',None) if 'resourceCount' in t else None
json.dump(S,open('site-data.json','w'),indent=2,ensure_ascii=False)
json.dump(N,open('research/resource-notes.json','w'),indent=2,ensure_ascii=False)
with open('research/portable/verified-sources.jsonl','a') as f:
    for x in recs: f.write(json.dumps(x,ensure_ascii=False)+'\n')
allv=[json.loads(l) for l in open('research/portable/verified-sources.jsonl')]
json.dump(allv,open('research/portable/verified-sources.json','w'),indent=1,ensure_ascii=False)
json.dump(recs,open('research/pass-2026-11-09/verified-r204-r252.json','w'),indent=1,ensure_ascii=False)
print(len(S['resources']),recs[0]['id'],recs[-1]['id'])
