"""pass-2026-11-12 build: verified records (R1624+) + lead decisions -> plan.json. apply.py writes working files.
Derived from research/pass-2026-11-11/build.py (same verification/metadata rules)."""
import json,re,sys,html,collections
B='/workspace/type1l-index/'
VD='2026-11-12'; PASS='pass-2026-11-12'
def clean(t): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',html.unescape(t or ''))).strip()
S=json.load(open(B+'site-data.json'))
TOPICS={t['id'] for t in S['topics']}
src=open('../pass-2026-11-10-leadverify/lv_build.py').read()
blk=src[src.index('CC={'):src.index('# ---------- existing index keys')]
blk=blk.replace("X['countries'].get(d) or []","[]")
exec(blk)
PUB.update({'Beuth Verlag GmbH':'Beuth Verlag (DIN)','Birkhäuser Basel':'Birkhäuser','Springer Berlin Heidelberg':'Springer','FapUNIFESP (SciELO)':'SciELO','Editorial CSIC':'Editorial CSIC','Pontificia Universidad Catolica de Chile':'Pontificia Universidad Católica de Chile','CRC Press':'CRC Press','Thomas Telford Publishing':'ICE Publishing (Thomas Telford)'})
sel=json.load(open('selected.json')); V=json.load(open('doi-verify.json'))
def fixab(a):
    a=clean(a)
    if 'First Name is required' in a or 'Last Name is required' in a or a.lower() in ('not available','resumen','abstract'): return ''
    a=re.sub(r'^(High Resolution Image\s*)?(Download MS PowerPoint Slide\s*)?','',a)
    a=re.sub(r'^(Summary|Abstract|Synopsis|Resumen|RESUMO|Resumo)(?=[A-Z\s])\s*','',a)
    return a
def oa_abs(w):
    ii=w.get('abstract_inverted_index')
    if not ii: return ''
    return ' '.join(x for _,x in sorted((p,x) for x,ps in ii.items() for p in ps))
def oa_geo(w):
    cs=[]
    for a in w.get('authorships',[]):
        for c in (a.get('countries') or [i.get('country_code') for i in a.get('institutions',[])]):
            if c and c not in cs: cs.append(c)
    return ' / '.join(CC.get(c,c) for c in cs[:4]) or None
PLC=['scm-limestone','binder-blended']
# topic overrides by listing index (replace the query topic as base; RULES then add up to 6)
T={
573:['cross-tests-codes','binder-international','concrete-structural','cross-durability'],576:['cross-durability','cross-chemistry'],578:['cross-chemistry','binder-portland','binder-white-masonry'],579:['cross-chemistry','binder-white-masonry'],
584:['binder-activated'],587:['cross-environment-cost','cross-supply-region'],589:['cross-chemistry','cross-tests-codes'],590:['binder-activated','scm-flyash'],595:['scm-natural','cross-durability'],596:['concrete-circular','cross-mix'],597:['cross-tests-codes','cross-durability'],
599:['cross-mix'],600:['cross-mechanics'],602:['cross-mechanics','cross-tests-codes'],604:['cross-mechanics'],605:['binder-portland','cross-chemistry'],607:['binder-portland','cross-chemistry'],611:['scm-limestone','cross-chemistry','microcracking'],
617:['concrete-polymer-refractory','cross-mechanics'],619:['scm-emerging'],621:['scm-natural','scm-clay','cross-tests-codes'],623:['binder-activated','cross-environment-cost','binder-international'],629:['cross-mix','concrete-hpc'],638:['concrete-circular','concrete-pavement-pervious','cross-mix'],
641:['cross-environment-cost'],643:['cross-environment-cost','concrete-circular','cross-durability'],644:['cross-environment-cost','binder-international'],
650:PLC+['durability','scm','cross-durability'],654:PLC+['scm-natural'],655:['binder-lc3','scm-clay','scm-limestone'],659:PLC+['cross-chemistry'],660:PLC+['standards','binder-international','cross-tests-codes'],
661:PLC+['durability','cross-durability'],663:PLC+['strength','durability'],669:['binder-lc3','scm-clay','scm-limestone','standards','cross-tests-codes'],671:PLC+['dot','durability','strength'],672:PLC+['dot','durability','cross-durability'],674:PLC+['scm-slag','durability','cross-durability'],
676:PLC+['scm-slag','cross-chemistry','strength'],677:PLC+['strength'],679:PLC+['scm-slag','strength'],680:PLC+['strength','durability','cross-tests-codes'],681:['binder-blended','scm-natural','cross-chemistry'],
107:['cross-chemistry','binder-portland'],111:['binder-portland','cross-chemistry','cross-mechanics'],112:['cross-chemistry','binder-portland','binder-blended'],113:['cross-durability','cross-tests-codes'],115:['cross-durability','cross-chemistry'],117:['cross-chemistry','cross-durability'],
118:['binder-portland','cross-chemistry','scm-limestone'],129:PLC+['cross-chemistry'],130:PLC+['cross-chemistry'],131:PLC+['cross-chemistry'],133:['concrete-structural','cross-tests-codes'],134:['cross-durability','cross-chemistry'],140:['binder-white-masonry','cross-chemistry'],
143:['cross-durability','durability','scm-limestone'],145:PLC+['strength'],146:PLC+['strength','cross-chemistry'],150:['cross-tests-codes','cross-durability'],152:['concrete-structural','cross-tests-codes'],157:['cross-mechanics'],162:['scm-flyash','binder-blended'],164:['cross-chemistry','cross-tests-codes'],
194:['binder-white-masonry','cross-durability','cross-failure-repair'],197:['cross-durability','cross-tests-codes'],204:['scm-natural','cross-tests-codes'],212:PLC+['cross-chemistry'],222:['cross-durability','durability','scm-limestone'],230:PLC+['durability'],233:PLC+['fresh','cross-mix'],
240:['cross-durability','cross-tests-codes'],256:['scm-natural','cross-tests-codes'],258:PLC+['binder-portland'],262:['cross-durability','cross-tests-codes'],270:PLC+['cross-mechanics'],315:PLC+['strength','cross-construction'],323:['concrete-cellular','concrete-precast-insitu-print'],332:['concrete-lightweight','concrete-cellular','concrete-precast-insitu-print'],
499:['cross-tests-codes','cross-mechanics'],
531:['binder-cac-csa','cross-chemistry'],532:['binder-magnesium-carbonatable','cross-environment-cost'],544:['concrete-lightweight','cross-mechanics'],546:['cross-durability','cross-environment-cost','concrete-structural'],552:['binder-blended','cross-tests-codes','cross-environment-cost'],553:['scm-emerging','binder-activated','binder-blended'],
554:['cross-environment-cost','cross-supply-region','binder-blended'],556:['cross-tests-codes','cross-chemistry'],557:['scm-limestone','cross-tests-codes','binder-blended'],565:['scm-limestone','binder-blended','cross-chemistry'],
}
GLOSS={
573:'German national application standard for concrete in concrete, reinforced and prestressed concrete structures: specification, properties, production and conformity — application rules for DIN EN 206-1 (catalogue description; text not reviewed).',
576:'German-language monograph on the durability of concrete by J. Stark and B. Wicht (Birkhäuser, 2001). Bibliographic record only; content not reviewed.',
578:'German-language book by J. Stark and B. Wicht on cement and lime, written to explain how cement is produced and used (English gloss of the opening of the publisher abstract; content not reviewed).',
579:'Chapter "Zement, Kalk, Gips" (cement, lime, gypsum) in Ferdinand Fischer\'s "Chemisch-technologisches Rechnen" (Springer, 1920). Bibliographic record only; content not reviewed.',
584:'Spanish-language review of the alkaline activation of aluminosilicates (alkali-activated cements and geopolymers) as a lower-CO2 alternative to Portland cement (abstract-level gloss).',
587:'Spanish-language study that uses life cycle assessment and IPCC guidelines to quantify embodied energy and CO2 emissions of cement manufacture in Ecuador, as local data for decision-makers and producers (abstract-level gloss).',
589:'Spanish-language reference table of infrared absorption frequencies and spectra of compounds relevant to cement chemistry (Materiales de Construcción, 1981). Bibliographic record only.',
590:'Spanish-language paper on the technological properties of alkali-activated aluminosilicate binders, especially mortars and concretes of alkali-activated fly ash without Portland cement, depending on the activator type after prior thermal curing (abstract-level gloss).',
595:'Spanish-language (Chile) experimental study of how natural pozzolan content affects the porosity and pore interconnectivity of concrete over time (abstract-level gloss).',
596:'Spanish doctoral thesis (Universidad Politécnica de Madrid) on recycled aggregate for structural concrete, intended to support technical regulation called for by Spain\'s 2001–2006 national construction-and-demolition waste plan (abstract-level gloss).',
597:'Spanish-language paper on electrical resistivity as a non-destructive control parameter for concrete and its durability — an indicator of setting, mechanical strength and degree of saturation (abstract-level gloss).',
599:'French-language paper introducing the "concrete-equivalent mortar" (MBE) method as a tool to help formulate admixed concretes (title-level gloss; content not reviewed).',
600:'French-language paper "Le béton numérique" (numerical concrete) on computer simulation of concrete structure (title-level gloss; content not reviewed).',
602:'French-language text (Materials and Structures, 1985) on determining the fracture energy of mortars and concretes by three-point bending of notched beams (title-level gloss; content not reviewed).',
604:'French-language paper on the drying of concrete: analysis and modelling (title-level gloss; content not reviewed).',
605:'French-language paper on how Portland cement composition influences its hydration in the presence of zinc (title-level gloss; content not reviewed).',
607:'French-language study of the retarding effect of zinc on the hydration of Portland cement paste (title-level gloss; content not reviewed).',
611:'French-language study of the formation of calcium monocarboaluminate hydrate in contact with a limestone aggregate in Portland cement paste (title-level gloss; content not reviewed).',
617:'Japanese-language paper (English abstract) on a polymer cement concrete made with a polypropylene emulsion, reporting several properties targeted by polymer modification such as flexural and tensile strength, drying shrinkage and permeability (abstract-level).',
619:'Portuguese-language (Brazil) study of sugarcane bagasse ash as a partial replacement for Portland cement in mortar, as an outlet for a residue expected to grow with fuel-alcohol production (abstract-level gloss).',
621:'Portuguese-language (Brazil) study, part I, of the pozzolanic activity of mineral additions for Portland cement using the lime pozzolanic activity index, XRD and other methods, discussing Brazilian standard tests (NBR 15895 modified Chapelle; NBR 5751) (abstract-level gloss).',
623:'Portuguese-language comparative life cycle assessment (Umberto software) of geopolymer concretes versus concretes made with Brazilian composite Portland cement CP II (abstract-level gloss).',
629:'Portuguese-language review of particle dispersion and packing concepts for producing special (high-performance) concretes (abstract-level gloss).',
638:'Chinese-language review (English abstract) of the properties of recycled concrete aggregate and the strength and durability-related performance of cement-stabilized semi-rigid base materials containing RCA for Chinese highways (abstract-level).',
}
EDN={
573:'2008-08 edition; withdrawn and replaced by DIN 1045-2:2023-08 (DIN Media catalogue entries for both editions seen via search index 2026-11-12).',
112:'Crossref edited-book record dated 1998 (ISBN 9780750662567). The 1970 3rd edition is indexed as R1461 and 2019 5th-edition chapters as R483, R974 and R1072; editor not registered in Crossref.',
107:'Crossref book record dated 1997 (Thomas Telford; ISBNs 9780727725929, 9780727739452); edition statement not registered in Crossref.',
133:'Historical 1947 edition of the ACI 318 building code (journal printing); superseded by later editions (current edition announced as ACI CODE-318-25, R356).',
152:'Historical ACI 318-71 code (journal printing, 1972); superseded by later editions (current edition announced as ACI CODE-318-25, R356).',
282:'1994 ACI Materials Journal printing of the ACI 232.1R committee report; later revisions of ACI 232.1R are not indexed here.',
429:'RILEM TC 176-IDC recommendation as published in Materials and Structures 2004 (committee designation not registered in Crossref).',
111:'Part of the multi-part 1946–47 ACI Journal series by Powers and Brownyard; this record is the issue registered under doi 10.14359/15302.',
}
ND={
617:dict(title='Some Properties of A Polymer Cement Concrete (ポリプロピレン系混合剤を用いたコンクリートの諸性質)',authors=['Shigemasa Hasaba','Mitsunori Kawamura','Toru Koizumi','Saemon Sukeda'],publisher='Faculty of Technology, Kanazawa University (Memoirs of the Faculty of Technology Kanazawa University)',type='Paper',date='1978-03-25',url='https://doi.org/10.24517/00011725',doi='10.24517/00011725',ids={'journal':'Memoirs of the Faculty of Technology Kanazawa University 11(2):35–43','ncid':'AN00044309','jalc':'10.24517/00011725'},lang='ja',access='catalog_metadata',geo='Japan',ev='JaLC DOI registry record 10.24517/00011725 read 2026-11-12 (titles ja/en, four authors, Kanazawa Univ. Faculty of Technology, 1978-03-25, vol 11 no 2 pp 35–43, VoR PDF in institutional repository); doi.org resolves (302) but Crossref has no record; repository landing page returned 503. OpenAlex English abstract inspected. Paper text not reviewed.'),
638:dict(title='含混凝土再生骨料水泥稳定基层性能综述 (A Review of Performance of Cement-Stabilized Base Materials Containing Recycled Concrete Aggregate)',authors=['宋承哲 (SONG Chengzhe)','李家全 (LI Jiaquan)','孔靖勋 (KONG Jingxun)','周长俊','安星'],publisher='中外公路杂志社 (Journal of China & Foreign Highway)',type='Review paper',date='2025',url='https://doi.org/10.14048/j.issn.1671-2579.2025.01.011',doi='10.14048/j.issn.1671-2579.2025.01.011',ids={'journal':'中外公路 (Journal of China & Foreign Highway) 2025(1)','chinadoi':'10.14048/j.issn.1671-2579.2025.01.011'},lang='zh',access='catalog_metadata',geo='China',ev='ChinaDOI resolution record read 2026-11-12 (title, five authors, 中外公路, 2025, registered 2025-05-06; links to zwgl.csust.edu.cn and CNKI); Crossref has no record. OpenAlex English abstract inspected. Paper text not reviewed. Romanised names for the last two authors are not registered (unknown).'),
499:dict(title='Estimation of Concrete Strength by Combined Nondestructive Testing Method',authors=['Yasuo Tanigawa','Kenji Baba','Hiroshi Mori'],publisher='American Concrete Institute (SP-82: In Situ/Nondestructive Testing of Concrete)',type='Conference paper',date='1984-09-01',url='https://www.concrete.org/publications/internationalconcreteabstractsportal.aspx?id=6549&m=details',doi=None,ids={'aciId':'6549','symposium':'ACI SP-82, pp. 57–76','listedDoi':'10.14359/6549 (listed by ACI; doi.org returned 404 on 2026-11-12)'},lang='en',access='landing_page_inspected',geo='Japan',ev='ACI International Concrete Abstracts Portal record id 6549 read 2026-11-12 (title, authors, SP vol 82, pp 57–76, 1984-09-01, abstract). The DOI listed there (10.14359/6549) is not registered at doi.org/Crossref (404). Paper text not reviewed.',desc='Develops practical expressions for estimating concrete compressive strength by combining rebound number with ultrasonic pulse velocity, examining water-cement ratio, coarse-aggregate size and volume fraction, curing and age, and applies them to strength distribution in a column and an existing building (abstract-level).'),
}
recs=[]; leads=[]
def tidy_title(c):
    t=clean(c.get('title'));st=c.get('subtitle') or []
    if st and clean(st[0]) and clean(st[0]).lower() not in t.lower(): t=t.rstrip(':')+': '+clean(st[0])
    return t
OPEN={635:'blocked: DOI 10.6052/j.issn.1000-4750.2021.01.0103 resolves at doi.org but is registered with neither Crossref nor JaLC; publisher site engineeringmechanics.cn returned HTTP 500 to curl and timed out to WebFetch, CNKI link timed out (2026-11-12). Retry next pass.'}
for k,w in sel.items():
    src_=w['_src']; idx=w['_idx']; q=w['queries'][0]
    base=T.get(idx) or ([q[0]] if q[0] in TOPICS else [])
    v=V[k]; c=v.get('crossref'); dc=v.get('datacite')
    lead=dict(status=None,topic=q[0],title=clean(w['title']),doi=(w.get('doi') or '').replace('https://doi.org/','') or None,year=w.get('publication_year'),authors=[a['author']['display_name'] for a in w['authorships']][:10] or None,venue=(((w.get('primary_location') or {}).get('source') or {}).get('display_name')),url=(w.get('primary_location') or {}).get('landing_page_url'),sourceApi='openalex',query=q[1],cited_by=w.get('cited_by_count'),notes='new lead discovered and verified in the same pass',addedOn=VD,pass_=PASS,openalexId=w['id'],reviewedOn=VD,reviewPass=PASS)
    if q[0]=='citation-chase': lead['citedBySeeds']=w.get('_citedBySeeds')
    if idx in OPEN:
        lead['_key']=k; lead['_open']=OPEN[idx]; leads.append(lead); continue
    if idx in ND:
        m=ND[idx]; title=m['title']
        ab=fixab(oa_abs(w))
        desc=GLOSS.get(idx) or m.get('desc') or first_sents(ab)
        rec=dict(title=title,authors=m['authors'],publisher=m['publisher'],type=m['type'],date=m['date'],url=m['url'],doi=m.get('doi'),ids=m['ids'],topics=topics_for(base,clean(w['title'])),geo=m.get('geo'),lang=m['lang'],desc=desc,access=m['access'],evidence='New lead (pass-2026-11-12 discovery) verified same day. '+m['ev'],edition=EDN.get(idx),rights=None)
    else:
        doi=lead['doi']
        if c:
            title=tidy_title(c); authors=[a for a in c['authors'] if a] or [a['author']['display_name'] for a in w['authorships']] or None
            asrc='Crossref' if [a for a in c['authors'] if a] else 'OpenAlex'
            date=fmt([c['issued']]) if c['issued'] and c['issued'][0] else (w.get('publication_date') and oadate(w['publication_date']))
            pub=PUB.get(c['publisher'],c['publisher']); cont=clean(c.get('container') or '')
            publisher=pub+(' ('+cont[:100]+')' if cont and cont!=pub else '')
            ids={}
            if cont: ids['journal']=('%s %s%s%s'%(cont[:80],c.get('volume') or '','(%s)'%c['issue'] if c.get('issue') else '',(':'+c['page']) if c.get('page') else '')).strip()
            if c.get('isbn'): ids['isbn']=c['isbn'][0]
            ab=fixab(c.get('abstract') or '') or fixab(oa_abs(w))
            typ=typ_of(c['type'],w.get('type'),title)
            reg='Crossref'
        else:
            title=clean(dc['title']); authors=dc['authors']; asrc='DataCite'; date=str(dc.get('year') or w.get('publication_year')); pub=dc['publisher']; publisher=pub; cont=None; ids={}
            ab=fixab(oa_abs(w)); typ='Thesis' if 'dissertation' in (w.get('type') or '') or dc.get('type')=='Dissertation' else 'Report'; reg='DataCite'
        access='abstract_metadata' if len(ab)>80 else 'doi_metadata'
        hd=v.get('doiHead','')
        ev='New lead (pass-2026-11-12 discovery) verified same day. %s metadata%s inspected %s; DOI registered (doi.org %s); full text not reviewed.'%(reg,' and abstract' if access=='abstract_metadata' else '',VD,hd.split(' ')[0])
        if reg=='Crossref' and asrc!='Crossref' and authors: ev+=' Authors from OpenAlex because Crossref registers none.'
        if not authors: ev+=' No authors registered (unknown).'
        if access=='abstract_metadata' and not fixab(c.get('abstract') if c else ''): ev=ev.replace('metadata and abstract','metadata and OpenAlex abstract')
        if q[0]=='citation-chase': ev+=' Found by backward citation chase from %s.'%', '.join(w.get('_citedBySeeds') or [])
        ed=EDN.get(idx)
        if c and c['type']=='standard' and 'ASTM' in (c['publisher'] or ''):
            des='ASTM '+re.sub(r'([A-Z])0+(\d)',r'\1\2',doi.split('/')[1].upper())
            title='%s Standard %s'%(des,title); typ='Standard catalogue record'; ed=ed or 'Latest edition registered in Crossref at verification (%s); earlier editions not indexed.'%des
            authors=['ASTM Committee '+(c['authors'][0].replace(' Committee','') if c['authors'] else '(not registered)')]
            desc='ASTM International catalogue record: %s.'%clean(c['title'])
        elif c and c['type']=='standard' and 'Beuth' in (c['publisher'] or ''):
            typ='Standard catalogue record'; authors=['DIN (NA 005-07-02 AA Betontechnik, per DIN Media catalogue)']; date='2008-08'
            ev+=' Crossref registers no issued date; edition date 2008-08 is part of the designation.'
            desc=GLOSS[idx]
        else:
            desc=GLOSS.get(idx) or first_sents(ab) or '%s%s%s; content beyond bibliographic metadata not reviewed.'%(typ,(' in '+cont[:90]) if cont else '',(' ('+date[:4]+')') if date else '')
        if c and not (c['issued'] and c['issued'][0]) and date and 'Beuth' not in (c['publisher'] or ''): ev+=' Date from OpenAlex (Crossref registers none).'
        if typ=='Other': typ='Book chapter' if '.ch' in doi else 'Paper'
        if idx==429: typ='Test method recommendation (RILEM)'
        title=re.sub(r'\bCO 2\b','CO2',title)
        lang=w.get('language') or 'en'
        if idx in GLOSS and lang!='en': ev+=' Title/abstract not in English; description is an English gloss.'
        rec=dict(title=title,authors=authors,publisher=publisher,type=typ,date=date,url='https://doi.org/'+doi,doi=doi,ids=ids,topics=topics_for(base,title),geo=oa_geo(w),lang=lang,desc=desc,access=access,evidence=ev,edition=ed,rights=None)
    rec['_key']=k; rec['_src']=src_; rec['_idx']=idx; rec['_topic']=q[0]
    recs.append(rec); lead['_key']=k; leads.append(lead)

# ---- post-fixes after manual QA of plan-review.txt (2026-11-12)
STRIP_UNLESS_BASE={'binder-well','cross-failure-repair','concrete-repair-grout-overlay'}
DROP={159:['cross-environment-cost'],401:['cross-environment-cost'],74:['cross-durability'],86:['cross-durability']}
for r in recs:
    i=r['_idx']; base=T.get(i) or []
    r['topics']=[t for t in r['topics'] if not (t in STRIP_UNLESS_BASE and t not in base and t!=r['_topic'])]
    r['topics']=[t for t in r['topics'] if t not in DROP.get(i,[])]
    if r['publisher'] and r['publisher'].startswith('ASTM International100 Barr Harbor'): r['publisher']='ASTM International'+(r['publisher'].split(')',1)[0].split('(',1)[1:] and ' ('+r['publisher'].split('(',1)[1] if '(' in r['publisher'] else '')
    if i==44: r['desc']='Paper in Inorganic Chemistry (1993) on characterising calcium aluminate phases in cements by 27Al MAS NMR spectroscopy (title-level; content beyond bibliographic metadata not reviewed).'; r['access']='doi_metadata'; r['evidence']=r['evidence'].replace(' and OpenAlex abstract','').replace('metadata and abstract','metadata')
    if i==107: r['authors']=['H. F. W. Taylor']; r['evidence']+=' Author taken from the publisher book description in the registered abstract (Crossref and OpenAlex register no author).'
    if i==754: r['authors']=['P. B. Bamforth']; r['evidence']+=' OpenAlex lists "BS 1881" as a second author; that is a parsing artefact (a British Standard), so only P. B. Bamforth is given.'
    if i in (129,130): r['title']='Filler cement: The effect of the secondary component on the hydration of Portland cement (%s)'%r['ids']['journal']
REJ={}
def tkey(t): return re.sub(r'\W+',' ',t.lower()).strip()
seen={tkey(r['title']) for r in S['resources']}
keep=[r for r in recs if r['_key'] not in REJ]
for r in keep:
    if tkey(r['title']) in seen:
        r['title']='%s (%s, %s)'%(r['title'],(r['date'] or '')[:4],(r['ids'].get('journal') or r['publisher'])[:70])
    seen.add(tkey(r['title']))
json.dump(dict(recs=keep,rejected={k:list(v) for k,v in REJ.items()},leads=leads),open('plan.json','w'),indent=1,ensure_ascii=False)
print(len(recs),len(keep),len(REJ),len(leads))
print(collections.Counter(r['access'] for r in keep)); print(collections.Counter(t for r in keep for t in r['topics']).most_common())
