"""pass-2026-11-13 build: verified records (R1893+; R1892 = resolved old lead) + lead decisions -> plan.json. apply.py writes working files.
Derived from research/pass-2026-11-12/build.py (same verification/metadata rules)."""
import json,re,sys,html,collections
B='/workspace/type1l-index/'
VD='2026-11-13'; PASS='pass-2026-11-13'
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
AE=['binder-portland','cross-durability','cross-mix']
T={0:AE,1:AE+['cross-tests-codes'],2:AE,3:AE+['cross-mechanics'],4:AE+['cross-mechanics'],5:AE,6:AE,
14:['scm-flyash','binder-blended','cross-mechanics'],15:['scm-flyash','binder-blended','cross-durability'],22:PLC+['binder-portland','cross-chemistry'],25:['binder-portland','scm-silica'],27:['binder-portland','concrete-mass-rcc','cross-mechanics'],
84:['microcracking','cross-chemistry'],94:['microcracking','cross-chemistry','cross-mix'],106:['microcracking','cross-chemistry'],126:['microcracking','concrete-structural','cross-chemistry'],146:['microcracking','cross-mechanics'],201:['microcracking','cross-mechanics'],
297:PLC+['scm-flyash','scm','cross-chemistry'],312:PLC+['cross-chemistry'],315:PLC+['scm-flyash','scm'],324:['scm-limestone','binder-portland','cross-chemistry'],325:PLC+['durability','cross-durability'],338:PLC+['durability','cross-durability'],
339:['scm-limestone','binder-blended'],343:['scm-limestone','cross-mechanics'],345:['scm-limestone','cross-durability'],347:['binder-lc3','scm-clay','scm-limestone','cross-durability'],
357:['binder-activated','concrete-architectural','cross-durability'],358:['binder-activated','scm-natural','concrete-architectural'],361:['binder-activated','concrete-architectural','cross-durability'],
367:['cross-durability','cross-tests-codes'],368:['cross-durability'],371:['concrete-architectural','cross-durability'],
839:['concrete-hpc','concrete-structural','cross-mechanics'],843:['concrete-repair-grout-overlay','concrete-structural','cross-durability'],844:['binder-lc3','scm-clay','cross-mechanics','cross-construction'],846:['scm-emerging','cross-mix'],
851:['binder-lc3','cross-durability'],853:['scm-slag','concrete-mass-rcc','cross-chemistry'],854:PLC+['strength','durability','mass'],855:['binder-portland','concrete-mass-rcc','cross-chemistry'],856:PLC+['mass','concrete-mass-rcc','cross-mechanics'],857:['binder-portland','scm-flyash','scm-limestone','mass','concrete-mass-rcc'],
858:['microcracking','binder-blended','cross-chemistry'],863:['microcracking','scm-emerging'],864:['concrete-precast-insitu-print','scm-clay','scm-limestone'],
865:['concrete-fibers','scm-limestone','scm-slag'],867:['cross-environment-cost','binder-portland','concrete-circular'],868:['binder-lc3','cross-environment-cost'],869:['binder-portland','cross-chemistry'],870:['cross-mix','cross-environment-cost'],871:['binder-lc3','scm-clay','scm-limestone','cross-chemistry'],
872:['concrete-pavement-pervious','cross-environment-cost'],873:['concrete-pavement-pervious','cross-mix'],874:PLC+['pavement','apps','durability','strength'],875:['concrete-pavement-pervious','cross-mix'],876:PLC+['pavement','mix','concrete-pavement-pervious'],877:['concrete-pavement-pervious','cross-durability','cross-failure-repair'],
879:PLC+['strength','durability','cross-construction'],880:PLC+['strength','durability','fresh'],881:['binder-portland','scm-slag','cross-chemistry'],886:PLC+['durability','cross-durability'],887:['concrete-scc','scm-limestone','scm-flyash'],888:['binder-cac-csa','scm-limestone'],889:PLC+['cross-chemistry'],890:['scm-limestone','cross-mix','fresh'],891:['concrete-scc','scm-limestone','cross-mix'],892:['scm-limestone','cross-mechanics','cross-chemistry'],
79:['cross-durability','cross-chemistry'],89:['concrete-circular','cross-mechanics'],138:['binder-activated','cross-chemistry','concrete-architectural'],230:['cross-mix','cross-durability','cross-chemistry'],246:['concrete-lightweight','cross-durability'],770:['concrete-structural','concrete-architectural','cross-supply-region'],
163:['cross-durability','concrete-structural'],184:['cross-durability','cross-mix'],229:['concrete-mass-rcc','cross-mechanics'],238:['binder-portland','concrete-structural','cross-chemistry'],260:['scm-slag','binder-activated'],821:['concrete-polymer-refractory','concrete-fibers'],
189:['cross-durability','cross-chemistry'],248:['cross-durability','concrete-structural'],251:['cross-durability','cross-mix'],704:['concrete-precast-insitu-print'],727:['binder-cac-csa','cross-chemistry'],750:['cross-chemistry'],754:['binder-international','cross-durability','cross-tests-codes'],755:['cross-durability','binder-international'],
756:['scm-emerging','concrete-polymer-refractory'],758:['scm-emerging','cross-durability'],759:['scm-emerging','scm-silica'],760:['scm-emerging','cross-mix'],761:['concrete-fibers','binder-white-masonry'],762:['concrete-circular','concrete-fibers','binder-white-masonry'],
763:['cross-durability','cross-chemistry'],765:['scm-slag','cross-chemistry'],766:['cross-chemistry','microcracking'],768:['cross-durability','cross-chemistry'],769:['microcracking','cross-chemistry'],795:['concrete-hpc','cross-construction'],
817:['scm-emerging','scm-flyash'],820:['concrete-cellular','scm-flyash'],823:['concrete-circular','cross-mix'],826:['concrete-hpc','concrete-fibers','concrete-structural'],828:['concrete-fibers','cross-mechanics'],829:['concrete-lightweight','cross-mix'],
}
GLOSS={
189:'German-language paper (Cement and Concrete Research, 1975) on concrete deterioration by sulfate (SO3) attack with formation of thaumasite and woodfordite (title-level gloss; content not reviewed).',
248:'Paper in Materiales de Construcción (1961) on the durability of reinforced concrete in seawater; no abstract registered (title-level; content not reviewed; text language not confirmed).',
251:'French-language paper (Canadian Journal of Civil Engineering, 1977) on alkali reactivity of Potsdam sandstone aggregate in old concrete structures in the Beauharnois–Valleyfield area south-west of Montreal, linking observed disintegration to alkali–silica reaction (English abstract).',
704:'German-language paper (Beton- und Stahlbetonbau, Oct 2026) on injection 3D concrete printing (I3DCP), which places concrete along arbitrary spatial trajectories inside a supporting medium so that material-saving, force-flow-following geometries can be built without formwork (abstract-level gloss).',
727:'Paper (Universum: Chemistry & Biology, Nov 2026; Uzbekistan) on developing the composition of a CAC 35 alumina-cement clinker from local raw materials; registered abstract is a Russian-language fragment (title-level gloss; content not reviewed).',
750:'German-language review (Angewandte Chemie, 2014) of formation mechanisms of inorganic nanoparticles and nanostructures in precipitation reactions, using calcium carbonate as the main example and discussing cement and polymers from an industrial viewpoint (abstract-level gloss).',
754:'German standard DIN 1164-10:2013-03, "Special cement — Part 10: Composition, requirements and conformity evaluation for cement with low effective alkali content" (low-alkali NA cements for ASR prevention). Catalogue record only; normative text not reviewed.',
755:'Chapter "Zement" (cement) in the German-language book "Dauerhaftigkeit von Beton" (Springer, 2013). Bibliographic record only; content not reviewed.',
756:'Spanish-language study of how crushed waste glass used as aggregate affects the properties and high-temperature behaviour of cement mortars (abstract-level gloss).',
758:'Spanish-language paper (English abstract) on spent fluid catalytic cracking catalyst (sFCC) as an SCM in Portland-cement mortars and their resistance to sulfuric, acetic and hydrochloric acid compared with other additions (abstract-level).',
759:'Spanish-language study (English abstract) of laboratory sol-gel nano-silica from sugarcane bagasse added to cement mortars (Type N and HS cements), reporting workability, compressive strength and hydrophobicity (abstract-level).',
760:'Spanish-language review (Revista ALCONPAT, 2022) of marble powder used to replace cement, sand or fine aggregate in concrete, mortar and bricks; concludes replacement up to about 15 % is possible without loss of compressive strength, depending on the material replaced (abstract-level gloss).',
761:'Spanish-language (Ecuador) study of synthetic polypropylene fibres and paraffin-treated natural cabuya fibres on the water permeability of cement–sand and cement–lime–sand masonry mortars (UNE-EN 12390-8 penetration and capillary absorption tests) (abstract-level gloss).',
762:'Spanish doctoral thesis (Universidad Politécnica de Madrid) on the physical, mechanical and thermal behaviour of cement mortars with mineral fibres recovered from construction and demolition waste (abstract-level gloss).',
763:'French-language paper (International Journal of Heat and Mass Transfer, 1991) on deriving a random pore network to model moisture sorption and migration in a cement mortar (title-level gloss; content not reviewed).',
765:'French-language paper (Cement and Concrete Research, 1989) comparing how porosity evolves in slag-cement mortars and Portland-cement mortars (title-level gloss; content not reviewed).',
766:'French-language paper (Materials and Structures, 1985) on the orientation of portlandite in Portland-cement mortars and concretes and the influence of the nature and surface state of the crystallisation substrate (title-level gloss; content not reviewed).',
768:'French-language paper (Materials and Structures, 1996) on global modelling of physico-chemical interactions, governed by non-linear isotherms, between chloride ions and Portland-cement mortar (title-level gloss; content not reviewed).',
769:'French-language paper (Cement and Concrete Research, 1975) reporting direct transmission-electron-microscope observation of the cement paste–aggregate bond in calcite and quartz mortars (title-level gloss; content not reviewed).',
770:'Italian-language monograph (AITEC, Milan, 1990) by R. Nelva and B. Signorelli on the arrival and evolution of reinforced concrete in Italy through the Hennebique system (catalogue-level gloss; book not reviewed).',
795:'Korean-language paper (English abstract) on pumping C60/C80 high-performance concrete to 500–575 m in a super-tall building, relating measured pumping pressure and output to fresh properties, temperature rise and slump-flow loss (abstract-level).',
817:'Paper (Polish journal, English abstract) comparing two biomass-combustion fly ashes (coconut shell and sunflower) in cement and standard mortars, as a way to use landfilled ash (abstract-level).',
820:'Russian-language paper (Kazakhstan, 2022) on autoclaved cellular (aerated) concrete made with Ekibastuz GRES-2 fly ash and a complex aluminium-containing additive, reporting strength, density and frost resistance (abstract-level gloss).',
821:'Russian-language paper (Novye Ogneupory / New Refractories), part 6 of a series on heat-resistant corundum concrete reinforced with alumina fibres formed in the matrix during firing; the fibres redistribute stress, reduce shrinkage and raise heat resistance and load-bearing capacity (English abstract).',
823:'Turkish-language study of whether marble block waste from the Afyonkarahisar region meets TS 706 EN 12620+A1 requirements for concrete aggregate (physical, chemical and ageing tests) (abstract-level gloss).',
826:'Turkish-language experimental study of reinforced concrete beams with ultra-high-performance fibre-reinforced concrete (hybrid micro and hooked macro steel fibres), covering ductility, capacity, flexural stiffness, failure and cracking (abstract-level gloss).',
828:'Turkish-language study of how fibre additions affect the impact resistance of concrete, motivated by protective/defence structures (abstract-level gloss).',
829:'Turkish-language paper estimating, with an artificial neural network trained on published data, the lightweight-aggregate content needed to reach a target strength in lightweight concrete, as a practical mix-design aid (abstract-level gloss).',
}
EDN={754:'2013-03 edition (designation from Crossref title); status (current/withdrawn) not checked.',
645:'Crossref book record dated 1997 (Taylor & Francis); later editions (2007, 2023) exist but are not indexed here.'}
DINDATE={754:'2013-03'}; DINAUTH={}
ACI='https://www.concrete.org/publications/internationalconcreteabstractsportal.aspx?id=%s&m=details'
def aci(i,title,authors,sp,pages,date,desc,geo='USA'):
    return dict(title=title,authors=authors,publisher='American Concrete Institute (%s)'%sp,type='Conference paper',date=date,url=ACI%i,doi=None,ids={'aciId':str(i),'symposium':'%s, pp. %s'%(sp,pages),'listedDoi':'10.14359/%s (listed by ACI; doi.org returned 404 on 2026-11-13)'%i},lang='en',access='landing_page_inspected',geo=geo,
        ev='ACI International Concrete Abstracts Portal record id %s read 2026-11-13 (title, authors, %s pp. %s, date, abstract). The DOI listed there (10.14359/%s) is not registered at doi.org/Crossref (404). Found by backward citation chase from 2026-11-12 seeds. Paper text not reviewed.'%(i,sp,pages,i),desc=desc)
ND={
163:aci(17530,'Mechanisms of Corrosion of Steel in Concrete',['George J. Verbeck'],'SP-49: Corrosion of Metals in Association with Concrete','21–38','1975','Interpretative summary of the design, concrete-quality and environmental factors that govern corrosion of steel in concrete and resulting structural performance (cover, permeability, w/c, chlorides, cracking, cathodic protection) (abstract-level).'),
184:aci(17535,'Corrosion Inhibitors for Reinforced Concrete',['D. F. Griffin'],'SP-49: Corrosion of Metals in Association with Concrete','95–102','1975','Early review of corrosion-inhibiting admixtures for reinforced concrete: theory, inhibitor types and a method for evaluating them; notes that investigations to date were laboratory-only (abstract-level).'),
229:aci(17327,'Studies of Creep in Mass Concrete',['Milos Polivka','David Pirtz','Robert F. Adams'],'SP-6: Symposium on Mass Concrete','257–286','1963','University of California study of the creep characteristics of mass concrete, used to determine stress from strain measurements and the sustained modulus of elasticity for designing mass concrete structures (abstract-level).'),
238:aci(17620,'A Brief History of Lime, Cement, Concrete, and Reinforced Concrete',['Jasper O. Draffin'],'SP-52: A Selection of Historic American Papers on Concrete 1876–1926','3–39','1976','Historical survey of lime, cements, concrete and reinforced concrete from antiquity onward, reprinted in ACI\'s collection of historic American concrete papers (abstract-level; reprint date given, original publication date not shown on the record).'),
260:aci(6739,'Activation of Blast Furnace Slag by Some Inorganic Materials',['J. Metso','E. Kajaus'],'SP-79: Fly Ash, Silica Fume, Slag and Other Mineral By-Products in Concrete','1059–1074','1983-05','Activation of merwinite–gehlenite granulated and pelletised blast-furnace slag with clinker, Ca(OH)2, gypsum, NaOH, sodium silicate, sodium carbonate, fly ash and phosphogypsum; NaOH and several NaOH combinations were good activators (abstract-level).','Finland'),
89:dict(title='Strength of Recycled Concrete Made From Crushed Concrete Coarse Aggregate',authors=['Torben C. Hansen','Henrik Narud'],publisher='American Concrete Institute (Concrete International)',type='Paper',date='1983-01',url='https://www.concrete.org/publications/internationalconcreteabstractsportal/m/details/id/9140',doi=None,ids={'aciId':'9140','journal':'Concrete International 5(1):79–83'},lang='en',access='landing_page_inspected',geo='Denmark',
   ev='ACI International Concrete Abstracts Portal record id 9140 read 2026-11-13 (title, authors, Concrete International 5(1):79–83, Jan 1983, abstract); no DOI registered. Found by backward citation chase from 2026-11-12 seeds. Paper text not reviewed.',desc='Compressive strength of concrete made with recycled coarse aggregate as a function of the strength of the original concrete, plus fresh properties, crusher-product gradings, recycled-aggregate properties and attached old mortar by size fraction (abstract-level).'),
138:dict(title='Ancient and Modern Concretes: What is the Real Difference?',authors=['Joseph Davidovits'],publisher='American Concrete Institute (Concrete International)',type='Paper',date='1987-12',url='https://www.concrete.org/publications/internationalconcreteabstractsportal/m/details/id/2380',doi=None,ids={'aciId':'2380','journal':'Concrete International 9(12):23–28'},lang='en',access='landing_page_inspected',geo='France',
   ev='ACI International Concrete Abstracts Portal record id 2380 read 2026-11-13 (title, author, Concrete International 9(12):23–28, Dec 1987, abstract); no DOI registered. Found by backward citation chase. The claim that ancient materials are geopolymeric is the author\'s argument, not established here. Paper text not reviewed.',desc='Davidovits argues that the durability of some ancient mortars and concretes reflects geopolymeric chemistry that could be replicated for modern use (author\'s thesis; abstract-level).'),
79:dict(title='Concrete corrosion and concrete protection',authors=['Imre Biczók'],publisher='Akadémiai Kiadó, Budapest',type='Book',date='1967',url='https://real-eod.mtak.hu/14262/',doi=None,ids={'realEod':'14262','mtaPrimo':'alma990005369500209321'},lang='en',access='catalog_metadata',geo='Hungary',
   ev='REAL-EOD (Library of the Hungarian Academy of Sciences) repository record 14262 read 2026-11-13 (title, I. Biczók, Akadémiai Kiadó, Budapest, 1967, English, book, scanned PDF linked); edition statement not given on the record. Found by backward citation chase. Book not reviewed.',desc='English-language monograph by I. Biczók (Akadémiai Kiadó, 1967) on concrete corrosion and concrete protection (catalogue-level; content not reviewed).',edition='1967 edition per REAL-EOD record; other editions/translations not checked.'),
230:dict(title='Calcium chloride in concrete: science and technology',authors=['V. S. Ramachandran'],publisher='Applied Science Publishers',type='Book',date='1976',url='https://nrc-publications.canada.ca/eng/view/object/?id=28b55500-66f8-44ec-96ae-417beb3a4956',doi=None,ids={'isbn':'9780853346821','nrcNumber':'NRC-IRC-3202','nparc':'20331082'},lang='en',access='catalog_metadata',geo='Canada',
   ev='NRC Publications Archive record read 2026-11-13 (V. S. Ramachandran, NRC Canada; Applied Science Publishers, 1976; 216 pages; ISBN 9780853346821; subject admixtures). Found by backward citation chase. Book not reviewed.',desc='Monograph by V. S. Ramachandran (National Research Council Canada) on the science and technology of calcium chloride in concrete; catalogued under admixtures (catalogue-level; content not reviewed).'),
246:dict(title='Frost resistance of concrete with porous aggregate',authors=['Göran Fagerlund'],publisher='Cement- och betonginstitutet (CBI), Stockholm',type='Report',date='1978',url='https://lup.lub.lu.se/search/publication/1292206',doi=None,ids={'series':'CBI forskning (1978)','issn':'0346-6906','lupRecord':'1292206'},lang='en',access='catalog_metadata',geo='Sweden',
   ev='Lund University Publications record 1292206 read 2026-11-13 (citation metadata: title, G. Fagerlund, 1978, CBI Stockholm, CBI forskning, ISSN 0346-6906, report, English). Found by backward citation chase. Report not reviewed.',desc='Swedish Cement and Concrete Research Institute report by G. Fagerlund on the frost resistance of concrete made with porous (lightweight) aggregate (catalogue-level; content not reviewed).'),
770:dict(title='Avvento ed evoluzione del calcestruzzo armato in Italia: il Sistema Hennebique',authors=['Riccardo Nelva','B. Signorelli'],publisher='AITEC, Milano',type='Book',date='1990',url='https://iris.polito.it/handle/11583/1393757',doi=None,ids={'handle':'11583/1393757'},lang='it',access='catalog_metadata',geo='Italy',
   ev='Politecnico di Torino IRIS record read 2026-11-13 (citation metadata: title, Nelva R. and Signorelli B., 1990, AITEC, Milano, monograph, ~200 pages). Book not reviewed.'),
821:dict(title='Heat-resistant corundum concrete reinforced by aluminum oxide fibers synthesized in the matrix while burning. Part 6: thermal and mechanical properties (Термостойкий корундовый бетон…)',authors=['V. N. Sokov','S. D. Sokova','V. V. Sokov'],publisher='Novye Ogneupory (New Refractories)',type='Paper',date='2016-06-28',url='https://newogneup.elpub.ru/jour/article/view/25',doi=None,ids={'journal':'Новые огнеупоры (Novye Ogneupory) no. 2, pp. 39–40','issn':'1683-4518','listedDoi':'10.17073/1683-4518-2015-2-39-40 (listed on the journal page; doi.org returned 404 on 2026-11-13)'},lang='ru',access='landing_page_inspected',geo='Russia',
   ev='Journal landing page (newogneup.elpub.ru) read 2026-11-13: Russian title, English title and abstract, three authors, issue 2, pp. 39–40, issued 2016-06-28. The DOI shown (10.17073/1683-4518-2015-2-39-40, which implies a 2015 issue) is not registered (doi.org 404); the year is therefore given as on the page. Paper text not reviewed.'),
}
OPEN={718:'blocked: DOI 10.5281/zenodo.23496439 (listed by OpenAlex) returned 404 at doi.org, Crossref and DataCite on 2026-11-13, and the journal page journals.ayu.edu.kz returned HTTP 500. Retry next pass; reject if the DOI stays unregistered and the page is unreachable.',
816:'blocked: DOI 10.4467/2353737XCT.14.077.2527 resolves at doi.org (Crossref prefix) but Crossref returns no record; ejournals.eu returned HTTP 500 and the Kraków repository PDF timed out on 2026-11-13. Retry next pass.',
818:'blocked: DOI 10.4467/2353737XCT.16.156.5767 resolves at doi.org (Crossref prefix) but Crossref returns no record; ejournals.eu and suw.biblos.pk.edu.pl returned HTTP 500 on 2026-11-13. Retry next pass.'}
recs=[]; leads=[]
def tidy_title(c):
    t=clean(c.get('title'));st=c.get('subtitle') or []
    if st and clean(st[0]) and clean(st[0]).lower() not in t.lower(): t=t.rstrip(':')+': '+clean(st[0])
    return t
for k,w in sel.items():
    src_=w['_src']; idx=w['_idx']; q=w['queries'][0]
    base=T.get(idx) or ([q[0]] if q[0] in TOPICS else [])
    v=V[k]; c=v.get('crossref'); dc=v.get('datacite')
    lead=dict(status=None,topic=q[0],title=clean(w['title']),doi=(w.get('doi') or '').replace('https://doi.org/','') or None,year=w.get('publication_year'),authors=[a['author']['display_name'] for a in w['authorships']][:10] or None,venue=(((w.get('primary_location') or {}).get('source') or {}).get('display_name')),url=(w.get('primary_location') or {}).get('landing_page_url'),sourceApi='openalex',query=q[1],cited_by=w.get('cited_by_count'),notes='new lead discovered and verified in the same pass',addedOn=VD,pass_=PASS,openalexId=w['id'],reviewedOn=VD,reviewPass=PASS)
    if q[0]=='citation-chase': lead['citedBySeeds']=w.get('_citedBySeeds')
    if q[0]=='citation-chase-fwd': lead['citesSeed']=w.get('_citesSeed')
    if idx in OPEN:
        lead['_key']=k; lead['_open']=OPEN[idx]; leads.append(lead); continue
    if idx in ND:
        m=ND[idx]; title=m['title']
        ab=fixab(oa_abs(w))
        desc=GLOSS.get(idx) or m.get('desc') or first_sents(ab)
        rec=dict(title=title,authors=m['authors'],publisher=m['publisher'],type=m['type'],date=m['date'],url=m['url'],doi=m.get('doi'),ids=m['ids'],topics=topics_for(base,clean(w['title'])),geo=m.get('geo'),lang=m['lang'],desc=desc,access=m['access'],evidence='New lead (pass-2026-11-13 discovery) verified same day. '+m['ev'],edition=EDN.get(idx),rights=None)
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
        ev='New lead (pass-2026-11-13 discovery) verified same day. %s metadata%s inspected %s; DOI registered (doi.org %s); full text not reviewed.'%(reg,' and abstract' if access=='abstract_metadata' else '',VD,hd.split(' ')[0])
        if reg=='Crossref' and asrc!='Crossref' and authors: ev+=' Authors from OpenAlex because Crossref registers none.'
        if not authors: ev+=' No authors registered (unknown).'
        if access=='abstract_metadata' and not fixab(c.get('abstract') if c else ''): ev=ev.replace('metadata and abstract','metadata and OpenAlex abstract')
        if q[0]=='citation-chase': ev+=' Found by backward citation chase from %s.'%', '.join(w.get('_citedBySeeds') or [])
        if q[0]=='citation-chase-fwd': ev+=' Found by forward citation chase (cites %s).'%w.get('_citesSeed')
        ed=EDN.get(idx)
        if c and c['type']=='standard' and 'ASTM' in (c['publisher'] or ''):
            des='ASTM '+re.sub(r'([A-Z])0+(\d)',r'\1\2',doi.split('/')[1].upper())
            title='%s Standard %s'%(des,title); typ='Standard catalogue record'; ed=ed or 'Latest edition registered in Crossref at verification (%s); earlier editions not indexed.'%des
            authors=['ASTM Committee '+(c['authors'][0].replace(' Committee','') if c['authors'] else '(not registered)')]
            desc='ASTM International catalogue record: %s.'%clean(c['title'])
        elif c and c['type']=='standard' and 'Beuth' in (c['publisher'] or ''):
            typ='Standard catalogue record'; authors=DINAUTH.get(idx,['DIN (committee not registered in Crossref)']); date=DINDATE[idx]
            ev+=' Crossref registers no issued date; edition date %s is part of the designation.'%DINDATE[idx]
            desc=GLOSS[idx]
        else:
            desc=GLOSS.get(idx) or first_sents(ab) or '%s%s%s; content beyond bibliographic metadata not reviewed.'%(typ,(' in '+cont[:90]) if cont else '',(' ('+date[:4]+')') if date else '')
        if c and not (c['issued'] and c['issued'][0]) and date and 'Beuth' not in (c['publisher'] or ''): ev+=' Date from OpenAlex (Crossref registers none).'
        if typ=='Other': typ='Book chapter' if '.ch' in doi else 'Paper'
        title=re.sub(r'\bCO 2\b','CO2',title)
        lang=w.get('language') or 'en'
        if idx in GLOSS and lang!='en': ev+=' Title/abstract not in English; description is an English gloss.'
        rec=dict(title=title,authors=authors,publisher=publisher,type=typ,date=date,url='https://doi.org/'+doi,doi=doi,ids=ids,topics=topics_for(base,title),geo=oa_geo(w),lang=lang,desc=desc,access=access,evidence=ev,edition=ed,rights=None)
    rec['_key']=k; rec['_src']=src_; rec['_idx']=idx; rec['_topic']=q[0]
    recs.append(rec); lead['_key']=k; leads.append(lead)


# ---- post-fixes after manual QA of plan-review.txt (2026-11-13)
STRIP_UNLESS_BASE={'binder-well','cross-failure-repair','concrete-repair-grout-overlay','concrete-architectural'}
DROP={39:['binder-magnesium-carbonatable'],288:['binder-magnesium-carbonatable'],325:['binder-magnesium-carbonatable'],338:['binder-magnesium-carbonatable'],578:['binder-magnesium-carbonatable','concrete-structural'],108:['cross-durability'],114:['cross-durability'],119:['cross-durability'],548:['concrete-structural']}
ADD={135:['cross-durability'],153:['cross-durability']}
LANGFIX={110:'en',784:'en',706:'en',251:'fr'}
for r in recs:
    i=r['_idx']; base=T.get(i) or []
    r['topics']=[t for t in r['topics'] if not (t in STRIP_UNLESS_BASE and t not in base and t!=r['_topic'])]
    if i in LANGFIX: r['lang']=LANGFIX[i]
    r['topics']=[t for t in r['topics'] if t not in DROP.get(i,[])]+[t for t in ADD.get(i,[]) if t not in r['topics']]
    if i==707: r['type']='Paper'; r['evidence']+=' DataCite registers resource type "Text"; it is a Magazine of Civil Engineering journal article, so type is given as Paper.'
    if i==720: r['type']='Repository deposit (Zenodo)'; r['evidence']+=' Zenodo self-deposit; peer-review status unknown.'
    if i==706: r['type']='Book'
    if i==332: r['evidence']+=' Crossref links a preprint (has-preprint); this is the published version.'
    if i==330: r['evidence']+=' The same paper was also printed in Metallurgical and Materials Transactions B 26:417–437 (10.1007/BF02653859); only the Transactions A record is indexed.'
REJ={206:('duplicate','duplicate: same Katharine and Bryant Mather conference paper (ASTM C 1012 sulfate resistance, 1987) already indexed as R1185 (TRID record); this is its ACI DOI record','R1185'),
48:('duplicate','chapter-level record ("Corrosion of steel in concrete", chapter 2 of an ebook edition of Broomfield\'s Corrosion of Steel in Concrete) with no authors registered; the book-level record is indexed instead',None),
129:('duplicate','chapter-level record ("Corrosion of steel in concrete", chapter 2 of the 1996/1997 Spon edition of Broomfield\'s Corrosion of Steel in Concrete); the book-level record (same pass) is indexed instead',None),
335:('duplicate','duplicate publication: the same Hansson (1995) paper printed in Metallurgical and Materials Transactions B; the Transactions A record (same pass) is indexed',None)}
K2I={r['_key']:r['_idx'] for r in recs}
REJ={k:REJ[i] for k,i in K2I.items() if i in REJ}
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
