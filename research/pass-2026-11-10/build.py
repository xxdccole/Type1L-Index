import json,re,collections,copy,os
os.chdir('/workspace/type1l-index')
VD='2026-11-10'; PD='research/pass-2026-11-10/'
exec(open(PD+'new_records.py').read())
V={**json.load(open(PD+'doi-verify.json')),**json.load(open(PD+'doi-verify2.json'))}
OA=json.load(open(PD+'openalex-detail.json'))
S=json.load(open('site-data.json')); L=json.load(open('research-ledger.json')); N=json.load(open('research/resource-notes.json'))
VER=[json.loads(l) for l in open('research/portable/verified-sources.jsonl')]
CAN=[json.loads(l) for l in open('research/portable/candidates.jsonl')]
assert len(S['resources'])==252
def norm(t): return re.sub(r'[^a-z0-9]','',(t or '').lower())[:60]
ex_urls={r['url'].lower().rstrip('/') for r in S['resources']}
ex_dois={(v.get('doi') or '').lower() for v in VER if v.get('doi')}|{u.split('doi.org/')[1] for u in ex_urls if 'doi.org/' in u}
ex_titles={norm(r['title'].split(' (')[0]) for r in S['resources']}
def fmt(parts):
    p=(parts or [[None]])[0]
    if not p or p[0] is None: return None
    return '-'.join([str(p[0])]+['%02d'%x for x in p[1:]])
PUB={'Elsevier BV':'Elsevier','Springer Science and Business Media LLC':'Springer','Informa UK Limited':'Taylor & Francis','MDPI AG':'MDPI','Springer International Publishing':'Springer','Frontiers Media SA':'Frontiers','Rilem Publications SARL':'RILEM Publications'}
LIC={'cc-by':'CC BY','cc-by-nc':'CC BY-NC','cc-by-nc-nd':'CC BY-NC-ND','public-domain':'Public domain (US Government work)','other-oa':'Other OA licence'}
recs=[]
for doi,(typ,topics,geo,desc,origin,x) in SPEC.items():
    v=V[doi]; c=v.get('crossref') or {}; o=OA.get(doi,{}); oav=v.get('openalex') or {}
    title=(c.get('title') or [None])[0] or oav.get('title')
    title=re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',title)).strip()
    if title.endswith(':'): title=title[:-1]
    authors=[a for a in (c.get('authors') or []) if a] or None
    asrc='Crossref'
    if not authors and o.get('authors'): authors=o['authors']; asrc='OpenAlex'
    if x.get('authorsSource')=='none registered (unknown)': authors=None; asrc='none'
    date=fmt(c.get('issued')) or ((o.get('date') or oav.get('date') or '')[:4] or None)
    if date and len(date)==10 and date.endswith('-01-01') and not c.get('issued'): date=date[:4]
    pub=c.get('publisher'); pub=PUB.get(pub,pub) if pub else None
    cont=(c.get('container') or [None])[0] if c.get('container') else None
    if not pub: pub=oav.get('venue') or 'unknown'
    publisher=pub+(' ('+cont.strip('"')[:80]+')' if cont else '')
    ids={}
    if cont: ids['journal']='%s %s%s'%(cont.strip('"')[:80],c.get('volume') or '',(':'+c['page']) if c.get('page') else '')
    absx=(c.get('abstract') or '') or (o.get('abstract') or '')
    access='abstract_metadata' if len(absx)>80 else 'doi_metadata'
    src='Crossref' if c else 'OpenAlex/DataCite'
    ev='%s metadata%s inspected %s'%(src,' and abstract' if access=='abstract_metadata' else '',VD)
    ev+='; DOI resolved to publisher landing (HTTP 200)' if v.get('http')==200 else '; DOI landing not loaded from this network (resolver/publisher error) — metadata only'
    ev+='; full text not reviewed.'
    if asrc=='OpenAlex': ev+=' Authors taken from OpenAlex because Crossref registers none.'
    if asrc=='none': ev+=' No authors registered (unknown).'
    if x.get('promotedFromCandidate'): ev='Promoted from candidate queue. '+ev
    if origin=='citation-chase': ev+=' Reached by citation chasing (OpenAlex cites/cited_by) in this pass.'
    if x.get('dateNote'): ev+=' '+x['dateNote']+'.'
    lic=o.get('license'); rights=('OpenAlex: '+LIC.get(lic,lic)) if lic else None
    recs.append(dict(title=title,authors=authors,publisher=publisher,type=typ,date=date or 'unknown',url='https://doi.org/'+doi,doi=doi,ids=ids,topics=topics,geo=geo,lang=x.get('lang','en'),desc=desc,access=access,evidence=ev,edition=x.get('edition'),rights=rights,origin=origin,promoted=x.get('promotedFromCandidate',False)))
for w in WEB:
    r=dict(w); r.setdefault('doi',None); r.setdefault('lang','en'); r.setdefault('edition',None); r.setdefault('rights',None); r['promoted']=False
    recs.append(r)
# dedupe
seen=set(); final=[]; dups=[]
for r in recs:
    k=(r.get('doi') or '').lower(); u=r['url'].lower().rstrip('/'); t=norm(r['title'].split(' (')[0])
    if (k and k in ex_dois) or u in ex_urls or t in ex_titles or (k or u) in seen: dups.append(r['title']); continue
    seen.add(k or u); final.append(r)
print('dups',dups)
tids={t['id'] for t in S['topics']}
for r in final:
    bad=[t for t in r['topics'] if t not in tids]; assert not bad,(r['title'],bad)
start=253; out=[]
for i,r in enumerate(final):
    rid='R%d'%(start+i)
    S['resources'].append({'id':rid,'title':r['title'],'publisher':r['publisher'],'type':r['type'],'date':r['date'],'url':r['url'],'topics':r['topics']})
    full=dict(id=rid,status='verified',title=r['title'],authors=r.get('authors'),publisher=r['publisher'],type=r['type'],date=r['date'],url=r['url'],doi=r.get('doi'),identifiers=r.get('ids') or {},topics=r['topics'],geography=r.get('geo'),language=r.get('lang','en'),description=r['desc'],access=r['access'],evidenceNote=r['evidence'],edition=r.get('edition'),rights=r.get('rights'),version=None,verifiedOn=VD,provenance='deep-pass-2026-11-10',origin=r['origin'],added=VD)
    out.append(full); N[rid]=r['evidence']
byid={r['id']:r for r in S['resources']}
# correction R200 (verified via Crossref/OpenAlex: first author Maraghechi)
r200=byid['R200']; old=r200['title']
r200['title']='Performance of Limestone Calcined Clay Cement (LC3) with various kaolinite contents with respect to chloride transport (Maraghechi, Avet, Wong, Kazemi-Kamyab, Scrivener)'
N['R200']=(N.get('R200','')+' ' if N.get('R200') else '')+'2026-11-10: title author attribution corrected from "(Avet, Scrivener)" to full author list; Crossref/OpenAlex list Hamed Maraghechi as first author with François Avet, Hong Seong Wong, Hadi Kazemi-Kamyab and Karen L. Scrivener (Materials and Structures 51, 2018).'
for v in VER:
    if v['id']=='R200':
        v['title']=r200['title']; v.setdefault('corrections',[]).append({'date':VD,'field':'title/authors','from':old,'note':'author attribution corrected per Crossref/OpenAlex'})
        v['authors']=['Hamed Maraghechi','François Avet','Hong Seong Wong','Hadi Kazemi-Kamyab','Karen L. Scrivener']
# membership union over all resources
tmap={t['id']:t for t in S['topics']}; repaired=[]
for r in S['resources']:
    for t in r['topics']:
        if r['id'] not in tmap[t]['resourceIds']:
            tmap[t]['resourceIds'].append(r['id'])
            if int(r['id'][1:])<253: repaired.append((t,r['id']))
for t in S['topics']:
    for i in t['resourceIds']:
        if t['id'] not in byid[i]['topics']: byid[i]['topics'].append(t['id']); repaired.append((t['id'],i,'resource-side'))
print('membership repairs (pre-existing):',len(repaired),repaired[:40])
def ids(t): return ', '.join(f['id'] for f in out if t in f['topics'])
TK={
'binder-blended':"Pass 3 (2026-11-10): NBS 1976 energy case for blended cements, early ternary-blend durability/strength papers (1997–2007), SCM reactivity review (2019), CO2-reduction techniques (2016), low-clinker systems (2023), RILEM pore-solution/pore-structure and TC 282 mixture-design reviews ({}). Mostly DOI/abstract-level; US C595 Type IP/IS/IT history beyond R37/R39/R40 still thin.",
'scm-clay':"Pass 3: metakaolin foundations (Wild 1996; Frías 2000; Boddy 2001; Sabir 2001 review; Greek kaolins 2004), clay-mineral pozzolanicity (2011), metakaolin+limestone (2012), R3 test development (2016) and RILEM TC 267/TC 282 reviews, LC3 factors, 2026 clinker×clay mineralogy study and VDOT VTRC 26-R52 field-agency evaluation of LC3/LC2 vs fly ash ({}). ASTM C1897 text itself not reviewed.",
'concrete-structural':"Pass 3: Hennebique history and system weaknesses, invention-of-RC chapter, Bažant–Kazemi shear size effect (1991), bar bond/deformation and corrosion-bond studies, PCI 1975 prestress-loss recommendations, PCI 1982 precast connections, ACI CODE-318-25 release, FHWA UHPC structural design framework and 2026 UHPC section shapes ({}). ACI 318-25 code text not reviewed.",
'concrete-hpc':"Pass 3: de Larrard ultrafine particles (1989) and packing optimization (1994), Richard & Cheyrezy RPC (1995), NIST HPC curing/maturity/fire workshop reports (1992–1999), Aïtcin durability review, USACE very-high-strength concrete, FHWA UHPC design framework, resistivity TechBrief and overlay reports, 2026 PCI/ACI UHPC bridge papers ({}).",
'concrete-pavement-pervious':"Pass 3: FHWA 1977 zero-maintenance JPCP design manual, Purdue 1985 pumping analysis, pervious mix-design/property papers (2010–2014), ACI PRC-522-23 preview (supersedes 522R-10), 2026 permeability-model and paver frost-durability studies ({}). CRCP-specific sources still not found in this pass.",
'concrete-precast-insitu-print':"Pass 3: 3DCP roadmap (2018), printing mix design (2012), rheological requirements (2018), interlayer adhesion (2019), Digital Concrete (2019) and extrusion review (2020); precast heat-curing DEF lab and Brewer Stadium field case; direct electric curing thesis; PCI connections and prestress-loss reports; 2026 3DCP shrinkage ({}).",
'concrete-circular':"Pass 3: Buck 1977 recycled concrete aggregate and forward-cited follow-ups, C&DW aggregate classification, RCA enhancement review, two-stage mixing, fine RCA durability, global cement carbonation uptake (2016), SCM-carbonation review, 2026 rammed RCA concrete and Bulgarian national-annex barrier analysis; EN 206-1:2026 adds CO2 classes ({}).",
'concrete-repair-grout-overlay':"Pass 3: FHWA first US UHPC overlay field test (2017), UHPC P&R design guide (2022), corrosion-control materials (2000), UHPC overlay thesis, zeolite VMA grouts, grout and new-old bond reviews, pavement repair materials, corrosion challenges (Angst 2018), 2026 UHPC rehabilitation review ({}).",
'cross-chemistry':"Pass 3: 1963 early hydration of cement types, NBS 1966 aluminoferrite hydrates, TEA/C3A (1973), Helmuth fresh-paste rheology (1980), CSA hydration modelling, C-S-H composition review, blended pore solution/structure, Cemdata18 ({}).",
'cross-mix':"Pass 3: PCE architecture/adsorption (2007–2008), rheology and thixotropy reviews, computational mix optimization (2018), Purdue low-paste paving optimization (2012), Buck RCA, de Larrard packing ({}). Abrams (1918) w/c law primary text still not located in an inspectable digitized copy.",
'cross-construction':"Pass 3: 1922 cold-weather cooling study, NBS 1976 construction safety, maturity-method papers (1983, 1990, NIST 1992), HPC curing, formwork and cold-weather reviews (2023), pervious compaction energy (2026) ({}).",
'cross-mechanics':"Pass 3: Hillerborg 1976 fictitious crack model, Modéer 1979 Lund thesis, Bažant–Oh crack band (1983), van Mier multiaxial softening thesis (1984), Brincker 1989, Wittmann 1983, Bažant–Li creep-model comparison (2008), C-S-H nanoscale creep, concrete at elevated temperature ({}).",
}
for t,txt in TK.items(): tmap[t]['takeaways'].append(txt.format(ids(t)))
# fixed takeaways for standards
tmap['standards']['takeaways'].append("EN 206-1:2026 (CEN, March 2026; R%s) splits EN 206 into Parts 1–3, superseding EN 206:2013+A2:2021, and adds CO2-emission classes and binder terminology; national adoption due by Sept 2026."%[f['id'] for f in out if f['title'].startswith('EN 206-1')][0][1:])
n=len(out); first=out[0]['id']; last=out[-1]['id']
S['lastUpdated']=VD
S['whatsNew'].insert(0,{'date':'Nov 10','title':'Deep research pass 3 + 2026 current-awareness sweep','detail':'Added %d verified sources %s–%s: historical/foundational backfill for blended binders, calcined clays, structural, HPC/UHPC, pavement/pervious, precast/printing, circular/RCA, repair/grout/overlay, chemistry, mix design, construction and mechanics; 2026 items incl. EN 206-1:2026, VTRC 26-R52 LC3 report, PCI/ACI UHPC bridge papers. Corrected R200 author attribution; repaired topic membership for pre-existing records. Not exhaustive.'%(n,first,last)})
S['changeLog'].append({'date':VD,'entry':'Deep research pass 3: appended %d verified records %s–%s (12 queued topics + current awareness; 3 promoted from the candidate queue, 13 via citation chasing). Corrected R200 title author attribution. Repaired topic.resourceIds/resource.topics union for %d pre-existing memberships. R1–R252 otherwise preserved.'%(n,first,last,len(repaired))})
S['gaps'].insert(0,'Pass 3 (2026-11-10) is a third batch, not complete coverage. Most journal records are DOI/abstract-level; ACI 318-25, EN 206-1:2026, ACI PRC-522-23 and ASTM C1897 normative texts not reviewed. Still open: Abrams 1918 primary text, CRCP design/performance sources, Talbot 1907 and other Illinois/Texas repository items (403 from this network), USACE ERDC Mather reports (reCAPTCHA), TU Delft repository (timeout).')
S['keyIssues'].append('EN 206 restructured in 2026: EN 206-1:2026 (performance, FPC), EN 206-2:2026 (conformity/certification) and EN 206-3:2026 (geotechnical) supersede EN 206:2013+A2:2021, with new CO2-emission classes; national annexes (e.g., Bulgaria BDS EN 206/NA RCA limits) still govern local use.')
allids=[r['id'] for r in S['resources']]; assert len(allids)==len(set(allids))
urls=[r['url'] for r in S['resources'] if r['url']]; assert len(urls)==len(set(urls)),[u for u,c in collections.Counter(urls).items() if c>1]
json.dump(S,open('site-data.json','w'),indent=2,ensure_ascii=False)
json.dump(N,open('research/resource-notes.json','w'),indent=2,ensure_ascii=False)
VER+=out
with open('research/portable/verified-sources.jsonl','w') as f:
    for x in VER: f.write(json.dumps(x,ensure_ascii=False)+'\n')
json.dump(VER,open('research/portable/verified-sources.json','w'),indent=1,ensure_ascii=False)
json.dump(out,open(PD+'verified-%s-%s.json'%(first.lower(),last.lower()),'w'),indent=1,ensure_ascii=False)
json.dump({'n':n,'first':first,'last':last,'repaired':repaired,'dups':dups,'promoted':[f['doi'] for f,r in zip(out,final) if r.get('promoted')]},open(PD+'build-summary.json','w'),indent=1,ensure_ascii=False)
print(n,first,last,len(S['resources']))
