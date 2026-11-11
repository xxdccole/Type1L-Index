"""pass-2026-11-11 build: verified records (R1477+) + lead decisions -> plan.json. apply.py writes working files."""
import json,re,sys,html,collections
sys.path.insert(0,'../pass-2026-11-10-leadverify')
B='/workspace/type1l-index/'
VD='2026-11-11'; PASS='pass-2026-11-11'
def clean(t): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',html.unescape(t or ''))).strip()
S=json.load(open(B+'site-data.json'))
TOPICS={t['id'] for t in S['topics']}
# reuse the lead-verify taxonomy rules verbatim (copied source block)
src=open('../pass-2026-11-10-leadverify/lv_build.py').read()
blk=src[src.index('CC={'):src.index('# ---------- existing index keys')]
blk=blk.replace("X['countries'].get(d) or []","[]")
exec(blk)
sel=json.load(open('selected.json')); V=json.load(open('doi-verify.json'))
def fixab(a):
    a=clean(a)
    if 'First Name is required' in a or 'Last Name is required' in a: return ''
    a=re.sub(r'^(High Resolution Image\s*)?(Download MS PowerPoint Slide\s*)?','',a)
    a=re.sub(r'^(Summary|Abstract|Synopsis)(?=[A-Z])','',a)
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
BASE={'pll-mix':['scm-limestone','binder-blended'],'current-2026':[]}
# manual topic additions (Type IL collection topics only for genuinely PLC/limestone-cement items) — keyed by (src,idx)
ADD={('harvest2',999):['cross-chemistry'],('harvest2',1003):['cross-chemistry'],('harvest2',1008):['binder-international','intl','cross-chemistry'],
('harvest2',1011):['durability','cross-durability'],('harvest2',1019):['durability','cross-durability'],('harvest2',1022):['strength','durability','intl'],
('harvest2',1023):['strength','durability'],('harvest2',1026):['binder-portland'],('harvest2',1028):['durability','cross-durability'],('harvest2',1035):['scm','carbon','cross-environment-cost'],
('harvest2',1042):['cross-environment-cost'],('harvest2',1061):['durability','binder-portland','scm-natural'],('harvest2',1079):['intl','cross-environment-cost','binder-international'],
('harvest1-current',100):['scm-limestone','binder-blended','scm','scm-slag'],('harvest1-current',102):['scm-limestone','binder-blended','durability','cross-durability'],
('harvest1-current',209):['scm-limestone','binder-blended','concrete-shotcrete'],('harvest1-current',211):['scm-limestone','binder-blended','apps','durability','cross-durability'],
('harvest1-current',215):['scm-limestone','binder-blended','durability','scm'],('harvest1-current',217):['scm-limestone','binder-blended','standards','binder-international','cross-tests-codes'],
('harvest1-current',218):['scm-limestone','binder-blended','scm','scm-clay','scm-flyash'],('harvest1-current',138):['cross-mix','cross-environment-cost'],
('harvest1-current',168):['scm-emerging','cross-tests-codes'],('harvest1-current',307):['concrete-heavyweight'],('harvest1-current',301):['concrete-heavyweight'],
('harvest1-current',295):['concrete-heavyweight'],('harvest1-current',321):['binder-well','scm-flyash','scm-natural'],('harvest1-current',208):['binder-well','binder-lc3'],
('harvest1-current',134):['binder-portland','scm-slag','cross-durability'],('harvest1-current',109):['binder-specialty','scm-slag','cross-durability'],
('harvest1-current',161):['binder-lc3','scm-clay','cross-durability'],('harvest2',661):['concrete-pavement-pervious'],('harvest2',694):['concrete-pavement-pervious'],
('harvest2',590):['cross-mechanics'],('harvest2',635):['mass','cross-construction'],('harvest2',800):['binder-cac-csa'],('harvest2',791):['binder-cac-csa'],('harvest2',823):['binder-cac-csa'],
('harvest2',846):['cross-tests-codes'],('harvest2',788):['cross-durability','concrete-structural'],('harvest2',793):['cross-durability','concrete-structural'],
('harvest2',880):['cross-environment-cost'],('harvest2',881):['cross-environment-cost'],('harvest2',902):['cross-environment-cost'],('harvest2',919):['cross-environment-cost'],
('harvest2',922):['cross-environment-cost','binder-activated'],('harvest2',955):['cross-environment-cost'],('harvest2',971):['cross-environment-cost','scm-flyash'],
('harvest2',903):['cross-mix','cross-environment-cost'],('harvest2',962):['cross-mix'],('harvest2',995):['cross-mix','cross-environment-cost'],
('harvest2',283):['concrete-architectural'],('harvest2',305):['concrete-architectural'],('harvest2',277):['concrete-architectural','concrete-repair-grout-overlay'],
('harvest2',714):['cross-construction'],('harvest2',183):['cross-durability'],('harvest2',184):['cross-durability'],('harvest2',212):['binder-activated'],
('harvest2',1146):['cross-supply-region'],('harvest2',44):['scm-slag'],('harvest2',31):['scm-slag'],('harvest2',33):['scm-slag'],('harvest2',34):['scm-slag'],('harvest2',37):['scm-slag','scm-silica'],('harvest2',56):['scm-slag'],
('harvest2',267):['scm-slag'],('harvest2',51):['cross-environment-cost'],('harvest2',88):['scm-slag','cross-environment-cost'],
('harvest2',178):[],('harvest2',858):['cross-durability','concrete-structural'],('harvest2',866):['cross-durability'],('harvest2',847):['cross-durability'],('harvest2',869):['cross-durability'],('harvest2',855):['cross-durability','cross-mix'],
('harvest2',808):['cross-construction'],('harvest2',1101):['binder-white-masonry'],('harvest2',1084):['concrete-lightweight'],('harvest2',481):['cross-mix']}
# no-DOI items: metadata from the inspected record (manual entry from catalogue/landing pages read 2026-11-11)
ND={
'https://openalex.org/w626239093':dict(title='CEM II- und CEM III/A-Zemente im Betonbau: Nachhaltige Lösungen für das Bauen mit Beton',authors=['P. Bilgeri','K. Droll','A. S. C. Ehrenberg','N. Ehrlich','D. Kuechlin','E. Liebig'],publisher='German cement industry brochure (TRID record; publisher not confirmed — secondary description names VDZ)',type='Book',date='2008',url='https://trid.trb.org/view/938458',ids={'trid':'938458','openalex':'W626239093'},lang='de',access='catalog_metadata',geo='Germany',ev='TRID record 938458 seen via search index (direct TRID fetch timed out 2026-11-11); OpenAlex W626239093 abstract (German) inspected; full text not reviewed. Author list from OpenAlex.'),
'https://openalex.org/w1519848535':dict(title='Mortars, plasters, stuccos, artificial marbles, concretes, Portland cements and compositions (Hodgson, 1912)',authors=['Fred T. Hodgson (ed.)'],publisher='Frederick J. Drake & Co.',type='Book',date='1912',url='https://ci.nii.ac.jp/ncid/BA8570960X',ids={'ncid':'BA8570960X','openalex':'W1519848535'},lang='en',access='catalog_metadata',geo='US',ev='CiNii Books record BA8570960X read 2026-11-11 (full title, "prepared, compiled and edited by Fred T. Hodgson", Frederick J. Drake, c1912; includes a practical treatise on reinforced concretes). Book text not reviewed.',desc='Early-20th-century practical treatise on preparing and using limes, mortars, cements, mastics and compositions in constructive and decorative work, including a treatise on reinforced concrete (catalogue description).'),
'https://openalex.org/w304955481':dict(title='How to Avoid Deficiencies in Portland-Cement Plaster Construction (USACE TR SL-84-10)',authors=['Jacob W. Ribar','John M. Scanlon'],publisher='US Army Engineer Waterways Experiment Station (DTIC ADA144688)',type='Report',date='1984-06',url='http://hdl.handle.net/11681/11202',ids={'dtic':'ADA144688','report':'Technical Report SL-84-10','handle':'11681/11202','hathitrust':'2027/uiug.30112073250133'},lang='en',access='catalog_metadata',geo='US',ev='DTIC OAI record ADA144688 and ERDC handle 11681/11202 identified via search index; DTIC citation page returned 403 to curl 2026-11-11; OpenAlex abstract inspected. Report text not reviewed.'),
'https://openalex.org/w618908713':dict(title='Advances in Autoclaved Aerated Concrete: Proceedings of the 3rd RILEM International Symposium (Zürich, 1992)',authors=['Folker H. Wittmann (ed.)'],publisher='A.A. Balkema',type='Proceedings',date='1992',url='https://catalogue.nla.gov.au/catalog/1110732',ids={'isbn':'9789054100867','openalex':'W618908713'},lang='en',access='catalog_metadata',geo='Switzerland',ev='National Library of Australia catalogue record and publisher (Routledge) listing seen via search index 2026-11-11; OpenAlex abstract (48 papers in seven chapters; 332-reference bibliography) inspected. Proceedings text not reviewed.'),
'https://openalex.org/w639154859':dict(title='Autoclaved Aerated Concrete: CEB Manual of Design and Technology',authors=['Comité Euro-International du Béton (CEB)'],publisher='Construction Press',type='Book',date='1978',url='https://ci.nii.ac.jp/ncid/BA06992924',ids={'ncid':'BA06992924','isbn':'0904406768','lccn':'79300562'},lang='en',access='catalog_metadata',geo='Europe (CEB)',ev='CiNii Books record BA06992924 read 2026-11-11 (Construction Press, Lancaster/New York, 1978; 90 p.; ISBN 0904406768; LCCN 79300562). Book text not reviewed.',desc='CEB design and technology manual for autoclaved aerated concrete (catalogue record; 90 pages with bibliography).'),
'https://openalex.org/w2409006778':dict(title='Controlling Temperatures in Mass Concrete (Gajda & VanGeem, Concrete International 2002)',authors=['John Gajda','Martha G. VanGeem'],publisher='American Concrete Institute (Concrete International)',type='Paper',date='2002',url='https://www.concrete.org/publications/internationalconcreteabstractsportal.aspx?m=details&ID=11125',ids={'aciId':'11125'},lang='en',access='catalog_metadata',geo='US',ev='ACI International Concrete Abstracts Portal record ID 11125 retrieved 2026-11-11 (HTTP 200, title confirmed); article text not reviewed.'),
'https://openalex.org/w631614217':dict(title='ACI 325.10R-95 State-of-the-Art Report on Roller-Compacted Concrete Pavements',authors=['ACI Committee 325 (OpenAlex lists S. D. Tayabji, T. Sherman, O. Keifer, A. Nanni et al.)'],publisher='American Concrete Institute',type='Report',date='1995',url='https://www.concrete.org/publications/internationalconcreteabstractsportal.aspx?id=9760&m=details',ids={'aci':'325.10R-95','trid':'423184'},lang='en',access='catalog_metadata',geo='US',ev='ACI abstracts portal (id 9760) and TRID 423184 identified via search index 2026-11-11 (TRID unreachable directly); OpenAlex abstract inspected. Report text not reviewed.',edition='1995 report (reapproved 2001 per secondary description); later ACI guidance on RCC pavements (ACI 327R-14) exists but is not indexed here.'),
'https://openalex.org/w2241022670':dict(title='The faced symmetrical hardfill dam: a new concept for RCC',authors=['Pierre Londe','Michel Lino'],publisher='International Water Power & Dam Construction',type='Paper',date='1992-02',url='http://pascal-francis.inist.fr/vibad/index.php?action=getRecordDetail&idt=5147422',ids={'pascalFrancis':'5147422','jglobal':'200902013838871948','pages':'19–24'},lang='en',access='catalog_metadata',geo='France',ev='Pascal-Francis record 5147422 and J-GLOBAL record identified via search index 2026-11-11 (J-GLOBAL returned 503 directly). Article text not reviewed.',desc='Introduces the faced symmetrical hardfill dam (FSHD): a symmetrical trapezoidal dam section of low-cement hardfill with an upstream concrete face, proposed as a new RCC concept (bibliographic/secondary description).'),
'https://openalex.org/w2151905550':dict(title='Silica Fume in Shotcrete (Wolsiefer & Morgan, 1993)',authors=['John Wolsiefer Sr.','D. R. Morgan'],publisher='American Concrete Institute (Concrete International)',type='Paper',date='1993-04',url='https://www.concrete.org/publications/internationalconcreteabstractsportal.aspx?id=4088&m=details',ids={'aciId':'4088','pages':'34–39'},lang='en',access='catalog_metadata',geo='US / Canada',ev='ACI abstracts portal record (id 4088) identified via search index 2026-11-11; OpenAlex abstract inspected. A reprint exists on shotcrete.org (2003). Article text not reviewed.'),
'https://openalex.org/w599911318':dict(title='High-Alumina Cements and Concretes (Robson, 1962)',authors=['T. D. Robson'],publisher='Contractors Record',type='Book',date='1962',url='https://ci.nii.ac.jp/ncid/BA16712194',ids={'ncid':'BA16712194'},lang='en',access='catalog_metadata',geo='UK',ev='CiNii Books record BA16712194 read 2026-11-11 (T. D. Robson, Contractors Record, 1962; held by 16 libraries). Book text not reviewed.',desc='Classic mid-century monograph on high-alumina (calcium aluminate) cements and concretes (catalogue record) — background to later HAC conversion/failure investigations.'),
'https://openalex.org/w2167696872':dict(title='Bridges with Premature Concrete Deterioration: Field Observations and Large-Scale Testing (FHWA/TX-02/1857-1)',authors=['A. Boenig','L. Funez','R. E. Klingner','T. J. Fowler'],publisher='University of Texas at Austin, Center for Transportation Research (TxDOT/FHWA)',type='Report',date='2001-10-01',url='https://rosap.ntl.bts.gov/view/dot/40309',ids={'report':'FHWA/TX-02/1857-1','project':'0-1857','rosap':'dot/40309'},lang='en',access='landing_page_inspected',geo='US',ev='ROSA P record dot/40309 read 2026-11-11 (revised edition; creators, report number, ASR/ettringite subject terms, 238 pp.). PDF not reviewed.',desc='TxDOT study using observations of in-service structures and laboratory specimens with premature concrete deterioration (ASR/delayed ettringite), core tests and large-scale tests to predict the capacity of deteriorated elements.'),
'https://openalex.org/w2281470736':dict(title='Case Study of Deterioration of Concrete in Sewerage Environment in an Arabian Gulf Country',authors=['H. Saricimen','Mohammed Maslehuddin'],publisher='Durability of Building Materials (journal)',type='Paper',date='1987',url='http://en.journals.sid.ir/ViewPaper.aspx?ID=111770',ids={'journal':'Durability of Building Materials 5(2):145–154'},lang='en',access='catalog_metadata',geo='Saudi Arabia',ev='SID record seen via search index 2026-11-11 (direct fetch HTTP 500); OpenAlex abstract (French) inspected. Article text not reviewed.',desc='Case study of a hot, humid Arabian Gulf sewage treatment plant: H2S from anaerobic bacteria is oxidised to sulfuric acid by Thiobacilli on moist concrete above the waterline, explaining severe deterioration there (abstract-level).'),
'https://openalex.org/w1996015255':dict(title='Global Warming Impact on the Cement and Aggregates Industries (Davidovits, 1994)',authors=['Joseph Davidovits'],publisher='World Resource Review (author-institute copy, Geopolymer Institute)',type='Paper',date='1994',url='https://www.geopolymer.org/dl/?get=5GWPROCE.pdf',ids={'journal':'World Resource Review 6(2):263–278'},lang='en',access='landing_page_inspected',geo='France',ev='Author-institute PDF (geopolymer.org) first page read 2026-11-11: states publication in World Resource Review 6(2) 263–278, 1994. Mirror of the journal article, not the publisher copy.',desc='Estimates ~1 t CO2 per t of Portland cement and projects cement CO2 growth driven by developing-country demand; argues ecotaxes would sharply raise cement prices, that blending with fly ash/slag gives 25–30% reductions, and promotes geopolymeric cements (author’s position).'),
'https://openalex.org/w3114183003':dict(title='Toward a Sustainable Cement Industry — Substudy 8: Climate Change (Battelle for WBCSD)',authors=['Kenneth Humphreys','Maha Mahasenan'],publisher='World Business Council for Sustainable Development / Battelle Memorial Institute',type='Report',date='2002-03',url='https://osti.gov/etdeweb/biblio/20269589',ids={'etdeweb':'20269589','ref':'CLA-00:090422'},lang='en',access='landing_page_inspected',geo='Switzerland / US',ev='OSTI ETDEWEB record 20269589 read 2026-11-11 (authors, Mar 2002, 61 pages, abstract). Report text not reviewed.',desc='Battelle substudy for the WBCSD Cement Sustainability Initiative: ~40% of cement-related GHG from kiln fuel, ~5% transport, ~5% electricity and ~50% from limestone calcination; favours fly-ash/pozzolan blended cements and discusses advanced options.'),
'https://openalex.org/w2336539488':dict(title='Technical and economical aspects of the use of limestone filler additions in cement (Baron & Douvre, 1987)',authors=['J. Baron','C. Douvre'],publisher='World Cement',type='Paper',date='1987',url='https://ci.nii.ac.jp/naid/80003413799',ids={'journal':'World Cement 18(3):100–104 (per secondary description)','naid':'80003413799'},lang='en',access='catalog_metadata',geo='France',ev='CiNii NAID 80003413799 (returned 202/empty to curl) and KipHub record seen via search index 2026-11-11; OpenAlex abstract (French) inspected. Article text not reviewed.',desc='French study: cements, mortars and concretes with up to 30% limestone addition performed at least as well as conventional cements of the same strength class in durability, workability and strength; 20% limestone cut energy use by ~16–17% (abstract-level).'),
}
DESC_OVR={'https://openalex.org/w626239093':'German-language book on the application properties and ecological benefits of CEM II (Portland-composite) and CEM III/A (blast-furnace) cements in concrete construction, with practice examples (abstract-level).'}
recs=[]; leads=[]
def tidy_title(c):
    t=clean(c.get('title'));st=c.get('subtitle') or []
    if st and clean(st[0]) and clean(st[0]).lower() not in t.lower(): t=t.rstrip(':')+': '+clean(st[0])
    return t
for k,w in sel.items():
    src=w['_src']; idx=w['_idx']; q=w['queries'][0]
    base=BASE.get(q[0],[q[0]])
    v=V[k]; c=v.get('crossref'); dc=v.get('datacite')
    lead=dict(status=None,topic=q[0],title=clean(w['title']),doi=(w.get('doi') or '').replace('https://doi.org/','') or None,year=w.get('publication_year'),authors=[a['author']['display_name'] for a in w['authorships']][:10] or None,venue=(((w.get('primary_location') or {}).get('source') or {}).get('display_name')),url=(w.get('primary_location') or {}).get('landing_page_url'),sourceApi='openalex',query=q[1],cited_by=w.get('cited_by_count'),notes='new lead discovered and verified in the same pass',addedOn=VD,pass_=PASS,openalexId=w['id'],reviewedOn=VD,reviewPass=PASS)
    if k in ND:
        m=ND[k]; title=m['title']
        ab=fixab(oa_abs(w))
        desc=DESC_OVR.get(k) or m.get('desc') or first_sents(ab) or '%s (%s); content beyond the catalogue record not reviewed.'%(m['type'],m['date'])
        rec=dict(title=title,authors=m['authors'],publisher=m['publisher'],type=m['type'],date=m['date'],url=m['url'],doi=None,ids=m['ids'],topics=topics_for(base+ADD.get((src,idx),[]),title),geo=m.get('geo'),lang=m['lang'],desc=desc,access=m['access'],evidence='New lead (pass-2026-11-11 discovery) verified same day. '+m['ev'],edition=m.get('edition'),rights=None)
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
        elif not dc:
            rec=dict(title=clean(w['title']),authors=None,publisher=None,type=None,date=str(w.get('publication_year')),url=None,doi=None,ids={},topics=[q[0]],geo=None,lang='en',desc='',access=None,evidence='',edition=None,rights=None)
            rec['_key']=k; rec['_src']=src; rec['_idx']=idx; rec['_topic']=q[0]; recs.append(rec); lead['_key']=k; leads.append(lead); continue
        else:
            title=clean(dc['title']); authors=dc['authors']; asrc='DataCite'; date=w.get('publication_date'); pub=dc['publisher']; publisher=pub; cont=None; ids={}
            ab=fixab(oa_abs(w)); typ='Thesis' if 'dissertation' in (w.get('type') or '') else 'Report'; reg='DataCite'
        access='abstract_metadata' if len(ab)>80 else 'doi_metadata'
        hd=v.get('doiHead','')
        ev='New lead (pass-2026-11-11 discovery) verified same day. %s metadata%s inspected %s; DOI registered (doi.org %s); full text not reviewed.'%(reg,' and abstract' if access=='abstract_metadata' else '',VD,hd.split(' ')[0])
        if reg=='Crossref' and asrc!='Crossref' and authors: ev+=' Authors from OpenAlex because Crossref registers none.'
        if not authors: ev+=' No authors registered (unknown).'
        if access=='abstract_metadata' and not clean(c.get('abstract') if c else ''): ev=ev.replace('metadata and abstract','metadata and OpenAlex abstract')
        ed=None
        if c and c['type']=='standard':
            des='ASTM '+re.sub(r'([A-Z])0+(\d)',r'\1\2',doi.split('/')[1].upper()) if 'ASTM' in (c['publisher'] or '') else None
            if des:
                title='%s Standard %s'%(des,title); typ='Standard catalogue record'; ed='Latest edition registered in Crossref at verification (%s); earlier editions not indexed.'%des
                authors=['ASTM Committee '+(c['authors'][0].replace(' Committee','') if c['authors'] else '(not registered)')]
            else:
                title='BSI: '+title; typ='Standard catalogue record'; authors=None
                ev+=' Crossref gives no BS designation for this BSI record (document %s); designation and edition year unknown in Crossref (OpenAlex dates it %s).'%(doi.split('/')[1],w.get('publication_year'))
            desc='%s catalogue record: %s.'%('ASTM International' if des else 'BSI',clean(c['title']))
        else:
            desc=first_sents(ab) or '%s%s%s; content beyond bibliographic metadata not reviewed.'%(typ,(' in '+cont[:90]) if cont else '',(' ('+date[:4]+')') if date else '')
        if c and not (c['issued'] and c['issued'][0]) and date: ev+=' Date from OpenAlex (Crossref registers none).'
        if typ=='Other': typ='Book chapter' if '.ch' in doi else 'Paper'
        title=re.sub(r'\bCO 2\b','CO2',title)
        rec=dict(title=title,authors=authors,publisher=publisher,type=typ,date=date,url='https://doi.org/'+doi,doi=doi,ids=ids,topics=topics_for(base+ADD.get((src,idx),[]),title),geo=oa_geo(w),lang=w.get('language') or 'en',desc=desc,access=access,evidence=ev,edition=ed,rights=None)
    rec['_key']=k; rec['_src']=src; rec['_idx']=idx; rec['_topic']=q[0]
    recs.append(rec); lead['_key']=k; leads.append(lead)
# ---- decisions: rejections after inspection (duplicates / superseded editions)
REJ={
 'https://openalex.org/w2292350902':('duplicate','duplicate-version: ACI 223R-10 is the superseded 2010 edition of the guide indexed as R178 (ACI PRC-223-21; superseded 2024-12-26 per Intertek/ACI store "historical").','R178'),
 'https://openalex.org/w564518750':('duplicate','duplicate-version: original 1993 E&FN Spon edition (CiNii BA21028963) of the RILEM recommended practice already indexed as R828 (CRC 2004 digital reissue, doi 10.1201/9781482271195).','R828'),
}
for r in recs:
    if r['doi']=='10.14359/9657' or (r['title'].startswith('Effect of Restraint, Volume Change, and Reinforcement on Cracking of Mass Concrete')):
        REJ[r['_key']]=('duplicate','duplicate-version: 1990 ACI Materials Journal publication of the ACI Committee 207 report on restraint/volume-change cracking of mass concrete, superseded by ACI 207.2R-07 indexed as R111 (title/venue/year match; designation not registered in Crossref).','R111')
    if r['doi']=='10.3403/30304851':
        REJ[r['_key']]=('duplicate','duplicate-version: BSI "Portland cement ordinary and rapid hardening" (OpenAlex 1947) treated as an earlier edition of the BSI ordinary and rapid-hardening Portland cement specification promoted in this pass (10.3403/00047536, OpenAlex 1978); Crossref gives no designation for either.','(this pass: 10.3403/00047536)')
# title uniqueness
def tkey(t): return re.sub(r'\W+',' ',t.lower()).strip()
seen={tkey(r['title']) for r in S['resources']}
keep=[r for r in recs if r['_key'] not in REJ]
for r in keep:
    if tkey(r['title']) in seen:
        r['title']='%s (%s, %s)'%(r['title'],(r['date'] or '')[:4],(r['ids'].get('journal') or r['publisher'])[:50])
    seen.add(tkey(r['title']))
json.dump(dict(recs=keep,rejected={k:list(v) for k,v in REJ.items()},leads=leads),open('plan.json','w'),indent=1,ensure_ascii=False)
print(len(recs),len(keep),len(REJ))
print(collections.Counter(r['access'] for r in keep)); print(collections.Counter(t for r in keep for t in r['topics']).most_common())
