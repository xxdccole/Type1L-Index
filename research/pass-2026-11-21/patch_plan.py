"""pass-2026-11-21: post-process plan.json. (1) J-GLOBAL retry lead -> promoted via its Crossref DOI (retry-list route); (2) NRC record page metadata fix (Litvan & Meyer 1986);
(3) open-queue leads (repo-added 2026-11-20 reaction-table sources) triaged by hand."""
import json,re
P=json.load(open('plan.json')); RL=[json.loads(l) for l in open('../review-retry.jsonl')]
byt={e['title']:e for e in RL}
VD='2026-11-21'
# (1) J-GLOBAL
jg=byt['高強度真鍮メッキ直鋼繊維の引抜性状に対する超高性能コンクリートの影響']
for r in P['recs']:
    if r.get('doi')=='10.14359/51685792':
        r['lang']='en'; r['_origin']='retry-list-doi-route'; r['_route']='crossref'; r['_retry']=jg
        r['desc']='Paper in ACI Materials Journal 110(4) (2013) on how an ultra-high-performance concrete matrix affects the pullout behaviour of high-strength brass-coated straight steel fibres (title-level; abstract not reviewed).'
        r['evidence']=('Retry-list lead (first seen 2026-11-20 as the J-GLOBAL record "%s", which does not open from the box: HTTP 503). Verified %s: the J-GLOBAL title is the Japanese record of this paper (OpenAlex W3000716741: Wille & Naaman, ACI Materials Journal, 2013); Crossref metadata for DOI 10.14359/51685792 inspected (title, ACI Materials Journal 110(4), 2013; DOI registered, doi.org 302). Authors from OpenAlex because Crossref registers none. Full text not reviewed.'%(jg['title'],VD))
        r['ids']['openalex']='W3000716741'
P['leads']=[l for l in P['leads'] if l.get('_key')!='https://doi.org/10.14359/51685792']
# (2) NRC
for r in P['recs']:
    if r['url'].startswith('https://nrc-publications.canada.ca/fra/voir/objet/?id=bf239155'):
        r.update(title='Carbonation of Granulated Blast Furnace Slag Cement Concrete During Twenty Years of Field Exposure',authors=['G. G. Litvan','A. Meyer'],publisher='National Research Council Canada (NRC Publications Archive; conference paper)',type='Conference paper',date='1986',lang='en',
          desc='Conference paper (Fly Ash, Silica Fume, Slag and Natural Pozzolans in Concrete, 2nd International Conference, Madrid, 1986) on two experimental houses, one in ordinary portland cement concrete and one in granulated-slag cement concrete, cored after 20 years of exposure to measure carbonation (record-page abstract, translated from French).')
        r['ids'].update(archive='NRC Publications Archive (NPARC)',listedDoi='10.14359/10130 (named on the lead; not registered at Crossref/DataCite)')
        r['evidence']=('Retry-list lead (first seen 2026-11-20; DOI 10.14359/10130 named on the lead is not registered). Verified %s: NRC Publications Archive record page read (%s); title, authors (Litvan G.G., Meyer A.), conference (2nd International Conference on Fly Ash, Silica Fume, Slag and Natural Pozzolans in Concrete, 1986, Madrid), subjects and French abstract match. The page header date (2026-11-21) is the site date, not the publication date; 1986 from the record and the lead. Full text not reviewed.'%(VD,r['url']))
        r['topics']=['scm-slag','cross-durability']
for r in P['recs']:
    if r.get('authors'):
        r['authors']=[a for a in r['authors'] if a and a.strip(', ').lower()!='none, none' and a!='None']or None
# (3) open queue: 3 literature leads promoted by hand, 2 reference-data leads rejected
CAN=[json.loads(l) for l in open('../portable/candidates.jsonl')]
OQ=[c for c in CAN if c['status']=='candidate']; assert len(OQ)==5,len(OQ)
def mk(c,**kw):
    d=dict(title=c['title'],authors=c['authors'],ids={},geo=None,lang='en',edition=None,rights=None,_origin='open-queue-pass-2026-11-21',_cand=c['title'],_key='oq:'+c['title'][:30]); d.update(kw); return d
oq=[]
for c in OQ:
    if c['reactionsKey']=='NEW-BENTZ-2005':
        oq.append(mk(c,publisher='National Institute of Standards and Technology (NISTIR 7232)',type='Report',date='2005-06',url='https://doi.org/10.6028/NIST.IR.7232',doi='10.6028/NIST.IR.7232',ids={'reportNumber':'NISTIR 7232','inspectedPdf':'https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7232.pdf'},
          topics=['cross-chemistry','scm-limestone','cross-mechanics'][:2],desc='NIST user manual and program listings for version 3.0 of CEMHYD3D, the 3-D cement hydration and microstructure model; adds limestone/inert-filler effects, preliminary slag reactions and pore-solution prediction, with example applications.',
          access='public_pdf_or_page',evidence='Open-queue lead (added to candidates.jsonl 2026-11-20 with the reactions table; source for data/reactions.json). Verified 2026-11-21: Crossref metadata for DOI 10.6028/NIST.IR.7232 (NISTIR 7232, 2005, author D. P. Bentz; DOI registered) and the NIST public PDF (nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7232.pdf, HTTP 200) opened; title page and abstract (June 2005) read. Remaining text/appendices not reviewed today.'))
    elif c['reactionsKey']=='NEW-BENTZ-2009':
        oq.append(mk(c,publisher='American Concrete Institute (Concrete International 31(11))',type='Paper',date='2009',url='https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=901137',doi=None,ids={'journal':'Concrete International 31(11):41-46'},
          topics=['scm-limestone','cross-mix'],desc="Concrete International article that uses Powers' model to show why limestone powder can replace cement in low water-cement-ratio mixtures (unhydrated cement acts as filler), with worked porosity and w/c results (part 1).",
          access='public_pdf_or_page',evidence='Open-queue lead (added 2026-11-20 with the reactions table). Verified 2026-11-21: NIST-hosted PDF (tsapps.nist.gov/publication/get_pdf.cfm?pub_id=901137, HTTP 200, application/pdf) opened; title, authors (Bentz, Irassar, Bucher, Weiss) and opening text read. No DOI found (Crossref bibliographic search returned none), so DOI is unknown. Year and issue (2009, 31(11):41-46) are from the lead; the PDF page read does not show them. Remaining text not reviewed.'))
    elif c['reactionsKey']=='NEW-LEON-CHEN-2021':
        oq.append(mk(c,publisher='MDPI (CivilEng)',type='Paper',date='2021-03-17',url='https://doi.org/10.3390/civileng2010014',doi='10.3390/civileng2010014',ids={'journal':'CivilEng 2(1):254-270'},
          topics=['concrete-mass-rcc','scm-slag'],desc='Open-access CivilEng paper on thermal analysis of mass concrete containing ground granulated blast-furnace slag.',
          access='doi_metadata',evidence='Open-queue lead (added 2026-11-20 with the reactions table; secondary citation there). Verified 2026-11-21: Crossref metadata for DOI 10.3390/civileng2010014 inspected (CivilEng 2(1):254-270, 17 March 2021, authors Leon and Chen; DOI registered). The MDPI article page answered HTTP 403 to the box today, so the page was not re-read. Full text not reviewed.'))
P['openQueue']=oq
P['openQueueRejected']=[dict(title=c['title'],reason=('Reference-data page (NIST Chemistry WebBook thermochemistry entry for CO2, SRD 69), opened and used only for a constant in the reactions table; not a cement/concrete literature source, so not added to the index (the citation stays in research/reactions.md and data/reactions.json).' if c['reactionsKey']=='NEW-NIST-WEBBOOK-CO2' else 'Reference-data page (IUPAC CIAAW abridged standard atomic weights), opened and used only to derive molar masses in the reactions table; not a cement/concrete literature source, so not added to the index (the citation stays in research/reactions.md and data/reactions.json).')) for c in OQ if c['reactionsKey'] in ('NEW-NIST-WEBBOOK-CO2','NEW-CIAAW')]
json.dump(P,open('plan.json','w'),indent=1,ensure_ascii=False,default=str)
print(len(P['recs']),len(P['leads']),len(oq),len(P['openQueueRejected']))
