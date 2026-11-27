"""pass-2026-11-26 build -> plan.json (adapted from pass-2026-11-25/build.py: retry inputs retry-c.json + kdot-cdx.json; new routes ndl-opensearch, dnb/bnf-sru, internet-archive, wayback-kdot, PDF reads; discovery inputs selected.json/doi-verify.json/probe-nodoi.json/newlead.json with listing-b rows at idx 400+j). Earlier header: pass-2026-11-20 build -> plan.json (apply.py writes working files). Derived from research/pass-2026-11-19/build.py.
Order (Chris's standing instructions): (A) retry list first — the 97 'promotable' leads (evidence re-confirmed 2026-11-20, confirm-promotable.json) plus
retry-list leads that opened today (retry-a.json/retry-b.json); (B) new discovery: DOI leads (Crossref/DataCite), no-DOI landing pages read,
no-DOI leads opened via alternative routes (newlead-a/b.json); (C) qualified-but-unavailable new leads -> retry; off-topic etc. rejected at screening (select.py)."""
import json,re,os,html,collections
from rlib import nu
B='/workspace/type1l-index/'
VD='2026-11-26'; PASS='pass-2026-11-26'
def clean(t): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',html.unescape(t or ''))).strip()
S=json.load(open(B+'site-data.json')); TOPICS={t['id'] for t in S['topics']}; TN={t['id']:t['name'] for t in S['topics']}
src=open('../pass-2026-11-10-leadverify/lv_build.py').read()
blk=src[src.index('CC={'):src.index('# ---------- existing index keys')].replace("X['countries'].get(d) or []","[]")
exec(blk)
PUB.update({'ASTM International100 Barr Harbor Drive, PO Box C700, West Conshohocken, PA 19428-2959':'ASTM International','Beuth Verlag GmbH':'Beuth Verlag (DIN)','Birkhäuser Basel':'Birkhäuser','Springer Berlin Heidelberg':'Springer','FapUNIFESP (SciELO)':'SciELO','Editorial CSIC':'Editorial CSIC','CRC Press':'CRC Press','Thomas Telford Publishing':'ICE Publishing (Thomas Telford)'})
LANGNAME={'ca':'Catalan','es':'Spanish','fr':'French','de':'German','pt':'Portuguese','zh':'Chinese','ja':'Japanese','ru':'Russian','uk':'Ukrainian','hr':'Croatian','hu':'Hungarian','id':'Indonesian','vi':'Vietnamese','sv':'Swedish','sk':'Slovak','ro':'Romanian','fa':'Persian','ar':'Arabic','it':'Italian','pl':'Polish','tr':'Turkish','nl':'Dutch','en':'English','cs':'Czech','da':'Danish','no':'Norwegian','nb':'Norwegian','fi':'Finnish','ko':'Korean','ms':'Malay'}
L3={'eng':'en','spa':'es','fre':'fr','fra':'fr','ger':'de','deu':'de','swe':'sv','nor':'no','nob':'no','dan':'da','cze':'cs','ces':'cs','pol':'pl','rum':'ro','ron':'ro','jpn':'ja','chi':'zh','zho':'zh','rus':'ru','ita':'it','por':'pt','fin':'fi','dut':'nl','nld':'nl','tur':'tr','ind':'id'}
def fixab(a):
    a=clean(a)
    if 'First Name is required' in a or 'Last Name is required' in a or a.lower() in ('not available','resumen','abstract'): return ''
    a=re.sub(r'^(High Resolution Image\s*)?(Download MS PowerPoint Slide\s*)?','',a)
    return re.sub(r'^(Summary|Abstract|Synopsis|Resumen|RESUMO|Resumo)(?=[A-Z\s])\s*','',a)
def oa_abs(w):
    ii=(w or {}).get('abstract_inverted_index')
    if not ii: return ''
    return ' '.join(x for _,x in sorted((p,x) for x,ps in ii.items() for p in ps))
def oa_geo(w):
    cs=[]
    for a in (w or {}).get('authorships',[]):
        for c in (a.get('countries') or [i.get('country_code') for i in a.get('institutions',[])]):
            if c and c not in cs: cs.append(c)
    return ' / '.join(CC.get(c,c) for c in cs[:4]) or None
def is_en(t):
    ws=re.findall(r"[a-zA-Z']+",(t or '').lower())
    if len(ws)<8: return False
    return sum(w in ('the','of','and','in','to','is','a','for','with','are','this','by') for w in ws)/len(ws)>0.12
def tidy_title(c):
    t=clean(c.get('title'));st=c.get('subtitle') or []
    if st and clean(st[0]) and clean(st[0]).lower() not in t.lower(): t=t.rstrip(':')+': '+clean(st[0])
    return t
BASEFIX=json.load(open('basefix.json')); GLT=json.load(open('glossT.json')); LANGFIX={int(k):v for k,v in json.load(open('langfix.json')).items()}; GL={int(k):v for k,v in json.load(open('glosses.json')).items()} if os.path.exists('glosses.json') else {}
OVR=json.load(open('overrides.json')) if os.path.exists('overrides.json') else {}
def base_for(w,idx):
    if str(idx) in BASEFIX: return BASEFIX[str(idx)]
    q=w['queries'][0][0]
    return [q] if q in TOPICS else []
STRIP={'binder-well','cross-failure-repair','concrete-repair-grout-overlay','concrete-architectural'}
ML=[(r'autocompact|autoadens|selbstverdicht|autoplaç|autocompatt|自己充填|自密实|självkompakt|selvkompakt|samozhut|самоуплотн','concrete-scc'),(r'permeável|permeable|drenante|pervious|透水','concrete-pavement-pervious'),
 (r'instandsetzung|réparation|reparación|recupera|korjaa|repair|加固|補修','concrete-repair-grout-overlay'),(r'reciclad|recyclé|recycl|reciklir|recykl|kierrät|再生','concrete-circular'),(r'geopol|alkali|aktivovan|activad|activé|碱激发|ジオポリマー','binder-activated'),
 (r'estrutur|structur|konstrukc|鉄筋コンクリート|钢筋混凝土|混凝土结构|结构|梁|柱|壁|beton armé|stahlbeton|betonarme|bertulang','concrete-structural'),(r'超高性能|高性能|UHPC|HPC','concrete-hpc'),(r'配合比|dosifica|traço|mix','cross-mix'),
 (r'鋼繊維|纤维|FRP|fibr|vlákn|fiber','concrete-fibers'),(r'ANSYS|应力|応力|stress|mécanique|endommag|resist|strength|kuat','cross-mechanics'),(r'電気抵抗率|試験|test|ensai|ensay|prüf|zkouš|規程|规程|norma|standard','cross-tests-codes'),(r'corros|chlor|carbonat|durab|kloride|腐食|耐久','cross-durability'),(r'casca de arroz|rice husk|cinza','scm-emerging')]
ML=[(re.compile(a,re.I),t) for a,t in ML]
def finish_topics(tp,base,title=''):
    tp=[t for t in tp if not (t in STRIP and t not in base)]
    if (not tp or tp==['cross-chemistry']) and title:
        for rx,t in ML:
            if rx.search(title) and t not in tp: tp.append(t)
        if len(tp)>1 and 'cross-chemistry' in tp and not re.search(r'hydrat|chem|水和|水化',title,re.I): tp.remove('cross-chemistry')
    return tp or ['cross-chemistry']
def descr(ab,lang,typ,cont,date,title):
    ens=(ab[:300].rsplit(' ',1)[0]+'…' if len(ab)>300 else ab) if ab and ab.startswith('Contents (from') else (first_sents(ab) if ab and is_en(ab) else '')
    if ens: return ens,''
    if lang!='en': return '%s-language %s%s (%s); title-level record only, content not reviewed.'%(LANGNAME.get(lang,lang),typ.lower(),(' in '+cont[:80]) if cont else '',(date or 'undated')[:4]),' Non-English record; no English description available.'
    return '%s%s%s; content beyond bibliographic metadata not reviewed.'%(typ,(' in '+cont[:90]) if cont else '',(' ('+date[:4]+')') if date else ''),''
recs=[]; leads=[]; retry_new=[]; retry_upd={}; promoted_retry=[]
# ======================================================================= (A) retry list
RL=[json.loads(l) for l in open('../review-retry.jsonl')]
OA=json.load(open('oa-retry.json'))
CONF={}
RB={r['title']:r for r in json.load(open('retry-c.json'))}
for r in json.load(open('kdot-cdx.json')):
    rb=RB[r['title']]; rb['urlsTried']=rb['urlsTried']+[u for u in r['urlsTried'] if u not in rb['urlsTried']]; rb['log']=rb['log']+r['log']
    if r['result']: rb['result']=r['result']
ACCEPT={'ndl-opensearch','dnb-sru','bnf-sru','internet-archive','wayback-kdot','direct','wayback','dspace7-rest','nva-api','diva-mods','doaj-api','thesesfr-api','cinii-opensearch','openlibrary','openlibrary-edition','google-books','crossref','datacite','crossref-search'}
def first(m,*ks):
    for k in ks:
        v=m.get(k)
        if isinstance(v,list): v=[x for x in v if x]
        if v: return v[0] if isinstance(v,list) else v
    return None
def allv(m,*ks):
    out=[]
    for k in ks:
        v=m.get(k)
        if not v: continue
        for x in (v if isinstance(v,list) else [v]):
            for y in (re.split(r'\s*;\s*',x) if isinstance(x,str) and ';' in x and k not in ('author',) else [x]):
                if y and y not in out: out.append(y)
        if out: break
    return out
def normdate(s):
    if not s: return None
    s=str(s).strip(); m=re.match(r'(\d{4})[-/.]?(\d{2})?[-/.]?(\d{2})?',s)
    if not m: return None
    y,mo,d=m.groups()
    if mo and mo!='00' and 1<=int(mo)<=12:
        if d and d!='00' and 1<=int(d)<=31: return '%s-%s-%s'%(y,mo,d)
        return '%s-%s'%(y,mo)
    return y
TRIDTYPE={'CO':'Conference paper','AR':'Paper','JA':'Paper','RE':'Report','MO':'Book','BK':'Book','TH':'Thesis','SE':'Report'}
def from_meta(e,res,oa,rt):
    m=res.get('meta') or {}; route=res['route']; ids={}
    if e.get('openalexId'): ids['openalex']=e['openalexId'].split('/')[-1]
    title=au=pub=cont=date=typ=lang=ab=None; ed=None; extra=''
    if route in ('direct','wayback') and m.get('pdf'):
        title=e['title']; pt=nu(m.get('pdfText') or '')
        au=None; sn=[a.split()[-1] for a in (e.get('authors') or []) if a.split()]
        if sn and all(nu(x) in pt for x in sn): au=e['authors']; extra+=' Authors as listed on the lead; every surname appears on the first pages of the PDF.'
        elif sn and any(nu(x) in pt for x in sn): au=[a for a in e['authors'] if a.split() and nu(a.split()[-1]) in pt]; extra+=' Authors: only those whose surnames appear on the first pages of the PDF are kept (lead also listed %s).'%', '.join(a for a in e['authors'] if a not in au)
        if route=='wayback': ids['archivedFrom']=res.get('original'); ids['waybackSnapshot']=res.get('snapshot')
        if e.get('doi'): ids['listedDoi']=e['doi']+' (printed on the PDF; doi.org resolves it but Crossref and DataCite return no metadata, checked 2026-11-26)'
        cont=e.get('venue')
    elif route=='wayback-kdot':
        title=e['title']; au=['Kansas Department of Transportation']; pub='Kansas Department of Transportation'; typ='Specification' if 'Special Provision' in e['title'] else 'Approved list'
        ids['archivedFrom']=res.get('original'); ids['waybackSnapshot']=res.get('snapshot'); ids['leadUrl']=e.get('url')
        md_=re.findall(r'\b(\d{2}-\d{2}-\d{2,4})\b',res.get('pdfText') or ''); date=None
        _rv=re.search(r'\b(1[05]-\d{5}(?:-R\d+)?)\b',res.get('pdfText') or ''); _tid=re.search(r'(1[05]-\d{5}(?:-R\d+)?)',e['title'])
        _revnote=(' The archived copy is identified as %s%s.'%(_rv.group(1),'' if (_tid and _rv.group(1)==_tid.group(1)) else ', not the revision named in the lead (%s)'%(_tid.group(1) if _tid else '?'))) if _rv else ''
        ed='Archived PDF of the same KDOT document number (Wayback capture %s of %s); the version currently linked from ksdot.gov (%s) answers HTTP 403 to the box and may be a later revision.%s'%(res.get('snapshot'),res.get('original'),e.get('url'),(' Date printed on the archived copy: %s.'%md_[-1]) if md_ else '')+_revnote
    elif route=='ndl-opensearch':
        title=m.get('title'); au=[x.replace(' ','') if re.search(r'[\u3040-\u9fff]',x) else x for x in (m.get('creator') or [])]; pub=(m.get('publisher') or [None])[0]; date=normdate((m.get('date') or [None])[0]); cont=(m.get('source') or [None])[0]
        typ='Paper'; ids['ndlSearch']=res['url']; lang='ja'
    elif route in ('dnb-sru','bnf-sru'):
        title=m.get('title'); au=[re.sub(r'\s*\(\d{4}-?\.*\)\.?\s*Auteur du texte|\.\s*Auteur du texte','',x).strip() for x in (m.get('creator') or [])]; pub=(m.get('publisher') or [None])[0]
        date=normdate((re.findall(r'\d{4}',' '.join(m.get('date') or [])) or [None])[0]); lang=(m.get('lang') or [None])[0]
        tt=' '.join(m.get('type') or []).lower(); typ='Thesis' if ('thèse' in tt or 'these' in tt or 'hochschulschrift' in tt or 'anrt' in (pub or '').lower()) else 'Book'
        ids['bnf' if route=='bnf-sru' else 'dnb']=res['url']
    elif route=='internet-archive':
        title=m.get('title'); au=m.get('creator') or []; au=[au] if isinstance(au,str) else au; pub=m.get('publisher') if isinstance(m.get('publisher'),str) else (m.get('publisher') or [None])[0]
        date=normdate(m.get('date') or m.get('year')); typ='Book' if (m.get('mediatype')=='texts' and not m.get('journaltitle')) else 'Paper'; ids['internetArchive']=res['url']; lang=m.get('language') if isinstance(m.get('language'),str) else None
    elif route in ('direct','wayback'):
        title=first(m,'citation_title','DC.title','dc.title','DC.Title','dcterms.title') or e['title']
        au=allv(m,'citation_author','citation_authors','DC.creator','dc.creator','DC.Creator','dcterms.creator','DC.contributor','DC.Contributor')
        cont=first(m,'citation_journal_title','citation_conference_title','DC.relation.ispartof','dc.relation.ispartof','DC.source','DC.Source')
        pub=first(m,'citation_publisher','DC.publisher','dc.publisher','citation_dissertation_institution')
        date=normdate(first(m,'citation_publication_date','citation_date','publication_date','DC.date','dc.date','DCTERMS.issued','dcterms.issued','DC.Date.issued','dc.date.issued','DC.Date','DC.issued'))
        if first(m,'citation_dissertation_name','citation_dissertation_institution'): typ='Thesis'
        elif first(m,'citation_technical_report_number'): typ='Report'; ids['reportNumber']=first(m,'citation_technical_report_number')
        if first(m,'citation_conference_title') and not typ: typ='Conference paper'
        if first(m,'citation_isbn'): ids['isbn']=first(m,'citation_isbn')
        if first(m,'citation_issn','DC.source.issn'): ids['issn']=first(m,'citation_issn','DC.source.issn')
        lang=first(m,'citation_language','DC.language','dc.language','DC.Language','dcterms.language')
        ab=first(m,'citation_abstract','DCTERMS.abstract','DC.description.abstract','dc.description.abstract','dcterms.description','DC.description','DC.Description','description')
        if cont:
            vol=first(m,'citation_volume','DC.citation.volume','DC.source.volume'); iss=first(m,'citation_issue','DC.citation.issue','DC.source.issue'); fp=first(m,'citation_firstpage'); lp=first(m,'citation_lastpage')
            ids['journal']=('%s %s%s%s'%(clean(cont)[:80],vol or '','(%s)'%iss if iss else '',(':%s%s'%(fp,'-'+lp if lp else '')) if fp else '')).strip()
        if 'ci.nii.ac.jp/ncid/' in res['url']: ids['ncid']=res['url'].rstrip('/').split('/')[-1]; typ=typ or 'Book'
        if route=='wayback': ids['archivedFrom']=res.get('original') or e.get('archivedFrom'); ids['waybackSnapshot']=res.get('snapshot') or e.get('snapshot')
        if 'ntlsearch.bts.gov' in res['url'] and res.get('evidenceFile') and os.path.exists(res['evidenceFile']):
            t=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',re.sub(r'<script.*?</script>|<style.*?</style>','',open(res['evidenceFile'],errors='ignore').read(),flags=re.S))))
            g=lambda a,b: (re.search(a+r'\s+(.*?)\s+'+b,t) or [None,None])[1]
            au=[x.strip() for x in (g('Personal Name Creator','Corporate Creator') or '').split(';') if x.strip()] or au
            pub=g('Publisher','Publication Date') or pub; date=normdate(g('Publication Date','Language')) or date; ab=g('Abstract','Rosap ID|TRT Terms|Report Number') or ab
            rn=g('Report Number','Resource type'); typ='Report'
            if rn: ids['reportNumber']=rn
            oc=g('OCLC','Contract Number|Report Number'); 
            if oc: ids['oclc']=oc
    elif route=='cinii-opensearch':
        title=m.get('title'); au=[x for x in (m.get('dc:creator') or []) if x] if isinstance(m.get('dc:creator'),list) else ([m['dc:creator']] if m.get('dc:creator') else [])
        cont=m.get('prism:publicationName'); pub=first(m,'dc:publisher'); date=normdate(m.get('prism:publicationDate') or m.get('dc:date'))
        typ='Paper' if cont else 'Book'; ids['ciniiResearch']=res['url']
        if cont: ids['journal']=('%s %s%s%s'%(clean(cont)[:80],m.get('prism:volume') or '','(%s)'%m['prism:number'] if m.get('prism:number') else '',(':%s%s'%(m['prism:startingPage'],'-'+m['prism:endingPage'] if m.get('prism:endingPage') else '')) if m.get('prism:startingPage') else '')).strip()
        ab=m.get('description')
    elif route=='openlibrary':
        title=m.get('title'); au=m.get('author_name') or []; au=[au] if isinstance(au,str) else au; pub=first(m,'publisher'); date=str(m['first_publish_year']) if m.get('first_publish_year') else None; typ='Book'
        if m.get('isbn'): ids['isbn']=m['isbn'][0]
        if m.get('oclc'): ids['oclc']=m['oclc'][0]
        ids['openLibraryWork']=res['url']; ed='Open Library work record (first published %s, %s editions catalogued); a specific edition was not verified.'%(m.get('first_publish_year') or 'year unknown',m.get('edition_count') or '?')
    elif route=='openlibrary-edition':
        title=m['title']+(' (%s)'%m['edition'] if m.get('edition') else ''); au=[x.strip() for x in m['author'].split(';')]; pub=m['publisher']; date=normdate(m['date']); typ='Book'
        ids.update({k:v for k,v in (('isbn',m.get('isbn10')),('oclc',m.get('oclc')),('lccn',m.get('lccn')),('openLibraryEdition',res['url']),('openLibraryWork',res.get('workUrl') or e.get('workUrl'))) if v})
        ed='%s, catalogued as Open Library edition %s.%s'%(m.get('edition') or 'Edition',res['url'].split('/')[-1],(' '+m['editionNote']) if m.get('editionNote') else '')
        if m.get('alsoCatalogued'): ed+=' '+m['alsoCatalogued']+'.'
        if 'date' in m and '(' in m['date']: ed+=' Date note: '+m['date']+'.'
    elif route=='dspace7-rest':
        g=lambda k:[x for x in (m.get(k) or []) if x]
        title=(g('dc.title') or [e['title']])[0]; au=g('dc.contributor.author') or g('dc.creator'); pub=(g('dc.publisher') or [None])[0]
        date=normdate((g('dc.date.issued') or g('dc.date.created') or [None])[0]); tt=' '.join(g('dc.type')).lower()
        typ='Thesis' if re.search(r'thes|dissert|práce|prace|master|bachelor|diplom',tt) else ('Report' if 'report' in tt else 'Paper')
        lang=(g('dc.language.iso') or g('dc.language') or [None])[0]; ab=m.get('abstract') or ''
        ids['handle']=res['url']; th=g('thesis.degree.grantor') or g('dc.publisher'); pub=pub or (th[0] if th else None)
        if g('dc.contributor.advisor'): extra+=' Advisor: %s.'%'; '.join(g('dc.contributor.advisor'))
    elif route=='nva-api':
        title=m.get('title'); au=[x for x in (m.get('author') or []) if x]; date=normdate(((m.get('date') or {}).get('year') or '')+('-%02d'%int(m['date']['month']) if (m.get('date') or {}).get('month') else '')) if m.get('date') else None
        it=(m.get('instanceType') or ''); typ='Thesis' if 'Degree' in it or 'Thesis' in it else ('Report' if 'Report' in it else ('Paper' if 'Article' in it else 'Report'))
        pub=m.get('publisher') or 'NTNU (Norwegian University of Science and Technology)'; lang=(m.get('language') or '').split('/')[-1] or None; ab=m.get('abstract')
        ids['handle']=m.get('handle'); ids['nva']=res['url']
        if m.get('series'): ids['series']=m['series']+(' '+str(m['seriesNumber']) if m.get('seriesNumber') else '')
    elif route=='diva-mods':
        title=m['title']+((' : '+m['subTitle']) if m.get('subTitle') else ''); au=m.get('author') or []; date=normdate((m.get('dateIssued') or [None])[0]); pub=(m.get('publisher') or [None])[0]
        gen=(m.get('genre') or [''])[0]; typ={'report':'Report','studentThesis':'Thesis','monographDoctoralThesis':'Thesis','comprehensiveDoctoralThesis':'Thesis','licentiateThesis':'Thesis','article':'Paper','conferencePaper':'Conference paper','book':'Book','chapter':'Book chapter'}.get(gen,'Report')
        lang=(m.get('language') or [None])[0]; ab=m.get('abstract'); ids['diva']=res['url']
        if m.get('urn'): ids['urn']=m['urn'][0]
        if m.get('series'): ids['series']=m['series'][0]
    elif route=='doaj-api':
        title=m.get('title'); au=m.get('author') or []; date=str(m.get('year')) if m.get('year') else None; cont=m.get('journal'); pub=m.get('publisher'); typ='Paper'; ab=m.get('abstract')
        ids['doaj']=res['url']; ids['journal']=('%s %s%s%s'%(cont[:80],m.get('volume') or '','(%s)'%m['number'] if m.get('number') else '',(':%s%s'%(m['start_page'],'-'+m['end_page'] if m.get('end_page') else '')) if m.get('start_page') else '')).strip() if cont else None
        for i_ in m.get('identifier') or []:
            if i_.get('type')=='doi': ids['listedDoi']=i_['id']+' (listed in DOAJ)'
            if i_.get('type') in ('pissn','eissn'): ids['issn']=i_['id']
        lang=((m.get('language') or [None])[0] or '').lower()[:2] or None
    elif route=='thesesfr-api':
        title=m.get('titrePrincipal'); au=[(a.get('prenom','')+' '+a.get('nom','')).strip() for a in (m.get('auteurs') or [])]; date=normdate(m.get('dateSoutenance')); typ='Thesis'
        pub=(m.get('etabSoutenanceN') or 'theses.fr'); ids['nnt']=res['url'].split('/')[-1]
    elif route=='google-books':
        title=m.get('title')+((': '+m['subtitle']) if m.get('subtitle') else ''); au=m.get('authors') or []; pub=m.get('publisher'); date=normdate(m.get('publishedDate')); typ='Book'
        for x in m.get('industryIdentifiers') or []:
            if x['type'].startswith('ISBN'): ids['isbn']=x['identifier']
        ids['googleBooks']=res['url']; lang=m.get('language'); ab=m.get('description')
    lang=(lang or '').strip().lower()
    lang=L3.get(lang,lang[:2]) if lang else None
    if lang and lang not in LANGNAME: lang=None
    lang=lang or (oa or {}).get('language') or 'en'
    if not au: au=e.get('authors') or None; extra+=' Authors from OpenAlex (not shown on the record inspected).' if au else ' No authors on the record (unknown).'
    if not typ:
        ot=(oa or {}).get('type'); typ={'book':'Book','dissertation':'Thesis','report':'Report','book-chapter':'Book chapter'}.get(ot,'Paper')
    if not date and e.get('year') and re.match(r'^\d{4}$',str(e['year'])): date=str(e['year']); extra+=' Year from OpenAlex.'
    absrc='record'
    if not ab:
        ab=fixab(oa_abs(oa)); absrc='openalex'
        if ab and nu(e['title'])[:40] and ab.lower().count(e['title'].lower()[:30])>=2: ab=''
        if ab: extra+=' Description from the OpenAlex abstract of the lead (not shown on the record inspected).'
    if 'ci.nii.ac.jp/ncid/' in res['url'] and ab and absrc=='record': ab='Contents (from the CiNii Books record): '+ab
    title=clean(title or e['title']).strip('"').strip()
    if not pub: pub=clean(cont) if cont else (e.get('venue') or 'unknown')
    elif cont and clean(cont)!=pub and route not in ('openlibrary','openlibrary-edition'): pub='%s (%s)'%(clean(pub)[:80],clean(cont)[:100])
    return dict(title=title,authors=[clean(a) for a in au if a] if au else None,publisher=clean(pub),type=typ,date=date,ids={k:v for k,v in ids.items() if v},lang=lang,ab=fixab(ab or ''),cont=cont,edition=ed,extra=extra)
ACCN={'ndl-opensearch':'catalog_metadata','dnb-sru':'catalog_metadata','bnf-sru':'catalog_metadata','internet-archive':'catalog_metadata','wayback-kdot':'landing_page_inspected','direct':'landing_page_inspected','wayback':'landing_page_inspected','dspace7-rest':'landing_page_inspected','nva-api':'landing_page_inspected','diva-mods':'landing_page_inspected','doaj-api':'abstract_metadata','thesesfr-api':'catalog_metadata','cinii-opensearch':'catalog_metadata','openlibrary':'catalog_metadata','openlibrary-edition':'catalog_metadata','google-books':'catalog_metadata','crossref':'doi_metadata','datacite':'doi_metadata','crossref-search':'doi_metadata'}
ROUTEDESC={'ndl-opensearch':'National Diet Library (NDL Search) catalogue record read via its OpenSearch API','dnb-sru':'Deutsche Nationalbibliothek catalogue record read via its SRU API','bnf-sru':'Bibliothèque nationale de France catalogue record read via its SRU API','internet-archive':'Internet Archive item metadata read','wayback-kdot':'Wayback Machine archived copy of the KDOT PDF read (pdftotext)','direct':'record page read','wayback':'Wayback Machine archived copy of the record page read','dspace7-rest':'repository record read via the DSpace 7 REST API','nva-api':'repository record read via the Sikt NVA publication API','diva-mods':'DiVA record read via its MODS export','doaj-api':'DOAJ article record read via the DOAJ API','thesesfr-api':'theses.fr record read via its API','cinii-opensearch':'CiNii Research record read via the CiNii OpenSearch API','openlibrary':'Open Library work record read','openlibrary-edition':'Open Library edition record read','google-books':'Google Books volume record read via the Books API','crossref':'Crossref DOI metadata read','datacite':'DataCite DOI metadata read','crossref-search':'Crossref DOI found by bibliographic search and its metadata read'}
def promote_lead(e,res,origin,cand_kind,oa,idx=None,base=None,conf=None):
    md=from_meta(e,res,oa,None)
    if res['route'] in ('crossref','crossref-search','datacite'): return None   # handled by caller (DOI path)
    url=res['url'] if res['route']!='wayback' else res['url']
    when='2026-11-21 retry, re-confirmed %s'%VD if conf else VD
    rd=ROUTEDESC[res['route']]
    if (res.get('meta') or {}).get('pdf'): rd=('Wayback Machine archived copy of the document PDF read' if res['route']=='wayback' else 'document PDF read')+' (first pages via pdftotext)'
    ev='%s Verified %s: %s (%s)%s. %s'%(cand_kind,when,rd,res['url'],(' '+conf) if conf else '','Title matches the lead.' if res['route']!='wayback-kdot' else 'The PDF carries the document identifier of the lead.')
    if res['route'] in ('wayback','wayback-kdot'): ev+=' Original page %s did not open from the box.'%(md['ids'].get('archivedFrom') or e.get('url'))
    ev+=' Full text not reviewed.'+md['extra']
    if md['edition'] is None and e.get('verificationNote'): md['edition']=e['verificationNote'].replace('Check before promoting.','The record inspected is the edition/printing promoted here; the earlier date was not verified.')
    access=ACCN[res['route']]
    if access=='landing_page_inspected' and md['ab'] and len(md['ab'])>80: pass
    desc,evx=descr(md['ab'],md['lang'],md['type'],clean(md['cont'] or ''),md['date'],md['title']); ev+=evx
    if idx is not None and idx in GL: desc=GL[idx]; ev+=' Title/abstract not in English; description is an English gloss.'
    g_=GLT.get(md['title']) or GLT.get(clean(e['title']))
    if g_ and md['lang']!='en': desc=g_; ev=ev.replace(' Non-English record; no English description available.','')+' Title/abstract not in English; description is an English gloss.'
    bt=base or ([e['reviewTopic']] if e.get('reviewTopic') in TOPICS else [])
    _tt=md['title']+((' '+GL[idx]) if idx is not None and idx in GL else '')
    tp=finish_topics(topics_for(bt,_tt),bt,_tt)
    rec=dict(title=md['title'],authors=md['authors'],publisher=md['publisher'],type=md['type'],date=md['date'],url=url,doi=None,ids=md['ids'],topics=tp,geo=oa_geo(oa),lang=md['lang'],desc=desc,access=access,evidence=ev,edition=md['edition'],rights=None)
    rec['_origin']=origin; rec['_route']=res['route']; return rec
nconf=0
for e in RL:
    oa=OA.get((e.get('openalexId') or '').split('/')[-1])
    if e['retryOutcome']=='promotable':
        c=CONF[e['title']]
        okc=(c['liveHttp']=='200' and c['liveMatch']>=0.75) or (c.get('ciniiRecheck') or {}).get('found')
        assert okc,e['title']
        nconf+=1
        res=dict(route=e['retryRoute'],url=e['bestUrl'],meta=e['verifiedMetadata'],original=e.get('archivedFrom'),snapshot=e.get('snapshot'),evidenceFile=e.get('evidenceFile'),workUrl=(e.get('verifiedMetadata') or {}).get('workUrl'))
        if e['retryRoute']=='openlibrary-edition':
            res['workUrl']={'Properties of concrete':'https://openlibrary.org/works/OL11330446W','Design and control of concrete mixtures':'https://openlibrary.org/works/OL4130223W'}.get(e['verifiedMetadata']['title'])
        confs='live re-check %s HTTP %s, title match %.2f'%(c['liveUrl'],c['liveHttp'],c['liveMatch']) if c['liveHttp']=='200' else 'live re-check via CiNii OpenSearch API: record %s returned for the title query'%e['bestUrl']
        r=promote_lead(e,res,'retry-list-promotable','Retry-list lead (first seen %s; qualified but unavailable then).'%e['firstSeen'],oa,conf='('+confs+')')
        r['_retry']=e; recs.append(r); promoted_retry.append(e['title']); continue
    rb=RB.get(e['title']); res=(rb or {}).get('result')
    if res and res['route'] in ACCEPT and res['route'] not in ('crossref','crossref-search','datacite'):
        r=promote_lead(e,res,'retry-list-retried','Retry-list lead (first seen %s; still unavailable after the 2026-11-25 retry).'%e['firstSeen'],oa)
        r['_retry']=e; recs.append(r); promoted_retry.append(e['title']); continue
    retry_upd[e['title']]=rb
# ======================================================================= (B) discovery
sel=json.load(open('selected.json'))
V=json.load(open('doi-verify.json'))
h=json.load(open('all-hits.json')); keys=json.load(open('listing-keys.json')); keysb=json.load(open('listing-b-keys.json'))
idx2k={i:k for i,k in enumerate(keys)}; idx2k.update({400+j:k for j,k in enumerate(keysb)})
def mklead(w,q,status_note):
    return dict(status=None,topic=q[0],title=re.sub(r'\s*\|\s*文献情報\s*\|.*$','',clean(w['title'])),doi=(w.get('doi') or '').replace('https://doi.org/','') or None,year=w.get('publication_year'),authors=[a['author']['display_name'] for a in w['authorships']][:10] or None,venue=(((w.get('primary_location') or {}).get('source') or {}).get('display_name')),url=(w.get('primary_location') or {}).get('landing_page_url'),sourceApi='openalex',query=q[1],cited_by=w.get('cited_by_count'),notes=status_note,addedOn=VD,pass_=PASS,openalexId=w['id'],reviewedOn=VD,reviewPass=PASS)
def k60(t): return re.sub(r'\W+','',clean(t).lower())[:60]
RLK={k60(e['title']):e['title'] for e in RL}
def dupof(w,lead):
    t=RLK.get(k60(w['title']))
    if t: lead['_dup']='Duplicate of a lead already on the review/retry list ("%s"); handled there.'%t[:120]; leads.append(lead); return True
for k,w in sel.items():
    idx=w['_idx']; q=w['queries'][0]; base=base_for(w,idx)
    if dupof(w,dict(mklead(w,q,'new lead discovered in the same pass'),_key=k)): continue
    v=V[k]; c=v.get('crossref'); dc=v.get('datacite'); doi=(w.get('doi') or '').replace('https://doi.org/','')
    lead=mklead(w,q,'new lead discovered and verified in the same pass')
    if not (c or dc):
        lead['_rtopic']=finish_topics(topics_for(base,clean(w['title'])),base,clean(w['title']))[0]; lead['_key']=k; lead['_retry']=dict(why='DOI %s not registered at Crossref/DataCite on %s (doi.org %s); no other record page opened'%(doi,VD,(v.get('doiHead') or '?').split(' ')[0]),urlsTried=['https://api.crossref.org/works/'+doi,'https://api.datacite.org/dois/'+doi,'https://doi.org/'+doi]); leads.append(lead); continue
    if c:
        title=tidy_title(c) or clean(w['title']); authors=[a for a in c['authors'] if a] or [a['author']['display_name'] for a in w['authorships']] or None
        asrc='Crossref' if [a for a in c['authors'] if a] else 'OpenAlex'
        date=fmt([c['issued']]) if c['issued'] and c['issued'][0] else (w.get('publication_date') and oadate(w['publication_date']))
        pub=PUB.get(c['publisher'],c['publisher']) or 'unknown'; cont=clean(c.get('container') or '')
        publisher=pub+(' ('+cont[:100]+')' if cont and cont!=pub else '')
        ids={}
        if cont: ids['journal']=('%s %s%s%s'%(cont[:80],c.get('volume') or '','(%s)'%c['issue'] if c.get('issue') else '',(':'+c['page']) if c.get('page') else '')).strip()
        if c.get('isbn'): ids['isbn']=c['isbn'][0]
        ab=fixab(c.get('abstract') or '') or fixab(oa_abs(w)); typ=typ_of(c['type'],w.get('type'),title); reg='Crossref'
    else:
        title=clean(dc['title']); authors=dc['authors']; asrc='DataCite'; date=str(dc.get('year') or w.get('publication_year')); pub=dc['publisher']; publisher=pub; cont=None; ids={}
        ab=fixab(oa_abs(w)); typ='Thesis' if 'dissertation' in (w.get('type') or '') or dc.get('type')=='Dissertation' else {'JournalArticle':'Paper','Text':'Preprint','Preprint':'Preprint','BookChapter':'Book chapter','Book':'Book','ConferencePaper':'Conference paper'}.get(dc.get('type'),'Report'); reg='DataCite'
    lang=LANGFIX.get(idx) or w.get('language') or 'en'
    access='abstract_metadata' if len(ab)>80 else 'doi_metadata'
    hd=v.get('doiHead','')
    ev='New lead (%s discovery) verified same day. %s metadata%s inspected %s; DOI registered (doi.org %s); full text not reviewed.'%(PASS,reg,' and abstract' if access=='abstract_metadata' else '',VD,hd.split(' ')[0])
    if reg=='Crossref' and asrc!='Crossref' and authors: ev+=' Authors from OpenAlex because Crossref registers none.'
    if not authors: ev+=' No authors registered (unknown).'
    if access=='abstract_metadata' and not fixab(c.get('abstract') if c else ''): ev=ev.replace('metadata and abstract','metadata and OpenAlex abstract')
    if q[0]=='citation-chase': ev+=' Found by backward citation chase (%s).'%q[1].replace('refs of ','from ')
    if q[0]=='citation-chase-fwd': ev+=' Found by forward citation chase (%s).'%q[1]
    ed=None
    if c and c['type']=='standard' and 'ASTM' in (c['publisher'] or ''):
        des='ASTM '+re.sub(r'([A-Z])0+(\d)',r'\1\2',doi.split('/')[1].upper()).replace('_','/')
        title=('%s %s' if title.lower().startswith('standard') else '%s Standard %s')%(des,title); typ='Standard catalogue record'; ed='Edition registered in Crossref at verification (%s); other editions not indexed here.'%des
        authors=['ASTM Committee '+(c['authors'][0].replace(' Committee','') if c['authors'] else '(not registered)')]
        desc='ASTM International catalogue record: %s.'%clean(c['title'])
    else:
        if idx in LANGFIX and (w.get('language') or 'en')!=lang: ev+=' Language set to %s from the title/publisher (OpenAlex lists %s).'%(lang,w.get('language'))
        if idx in GL: desc=GL[idx]; ev+=' Title/abstract not in English; description is an English gloss.'
        else:
            desc,evx=descr(ab,lang,typ,cont,date,title); ev+=evx
    if c and not (c['issued'] and c['issued'][0]) and date: ev+=' Date from OpenAlex (Crossref registers none).'
    if typ=='Other': typ='Book chapter' if '.ch' in doi else 'Paper'
    title=re.sub(r'\bCO 2\b','CO2',title)
    rec=dict(title=title,authors=authors,publisher=publisher,type=typ,date=date,url='https://doi.org/'+doi,doi=doi,ids=ids,topics=finish_topics(topics_for(base,title+((' '+GL[idx]) if idx in GL else '')),base,title+((' '+GL[idx]) if idx in GL else '')),geo=oa_geo(w),lang=lang,desc=desc,access=access,evidence=ev,edition=ed,rights=None)
    rec['_key']=k; rec['_idx']=idx; rec['_origin']='discovery-'+PASS; recs.append(rec); lead['_key']=k; leads.append(lead)
# no-DOI: landing page read (probe ok) or opened via alternative routes (newlead-b.json)
PR={r['idx']:r for r in json.load(open('probe-nodoi.json'))}
NB={r['title']:r for r in json.load(open('newlead.json'))}
nod_idx=json.load(open('nodoi-idx.json'))
for i in nod_idx:
    k=idx2k[i]; w=h[k]; q=w['queries'][0]; base=base_for(w,i)
    lead=mklead(w,q,'new lead discovered and checked in the same pass'); lead['_key']=k
    if dupof(w,lead): continue
    p=PR.get(i)
    if p and p['status']=='ok':
        e=dict(title=w['title'],authors=[a['author']['display_name'] for a in w['authorships']][:10],year=w.get('publication_year'),openalexId=w['id'],url=p['url'])
        f=p.get('file') or 'landing/nodoi-%d.html'%i
        from rlib import text_of
        txt,meta=text_of(f)
        res=dict(route='direct',url=p['http'].split(' ',1)[1] if ' ' in p.get('http','') else p['url'],meta=meta,evidenceFile=f)
        r=promote_lead(e,res,'discovery-'+PASS,'New lead (%s discovery) verified same day; no DOI.'%PASS,w,idx=i,base=base)
        if q[0]=='citation-chase': r['evidence']+=' Found by backward citation chase (%s).'%q[1].replace('refs of ','from ')
        r['_key']=k; r['_idx']=i; recs.append(r); leads.append(lead); continue
    nb=NB.get(w['title']); res=(nb or {}).get('result')
    if res and res['route'] in ACCEPT and res['route'] not in ('crossref','crossref-search','datacite'):
        e=dict(title=w['title'],authors=[a['author']['display_name'] for a in w['authorships']][:10],year=w.get('publication_year'),openalexId=w['id'],url=(w.get('primary_location') or {}).get('landing_page_url'))
        r=promote_lead(e,res,'discovery-'+PASS,'New lead (%s discovery) verified same day; no DOI; original landing page did not open (%s).'%(PASS,(p or {}).get('http','skipped host')[:3] or 'skipped host'),w,idx=i,base=base)
        if q[0]=='citation-chase': r['evidence']+=' Found by backward citation chase (%s).'%q[1].replace('refs of ','from ')
        r['_key']=k; r['_idx']=i; recs.append(r); leads.append(lead); continue
    tried=[x for x in ([(p or {}).get('url')]+((nb or {}).get('urlsTried') or [])) if x]
    why='landing page %s'%(('HTTP '+(p.get('http') or '000')[:3]) if p and p['status']!='skipped-host' else 'host not openable from the box (%s)'%re.sub(r'^https?://([^/]+)/.*',r'\1',(p or {}).get('url') or ''))
    lead['_rtopic']=finish_topics(topics_for(base,clean(w['title'])),base,clean(w['title']))[0]
    lead['_retry']=dict(why=(why.replace('landing page HTTP 200','landing page answered HTTP 200 but gave no usable record (JavaScript/bot-check page or no matching title)'))+'; CiNii OpenSearch, Open Library, Wayback copies, OpenAlex alternative versions, J-STAGE, NDL, DNB/BnF catalogues, Internet Archive and DataCite search gave no inspectable record',urlsTried=tried,log=(nb or {}).get('log')); leads.append(lead)
for r in recs:
    if ('gloss of the' in r['desc'] or 'title-level record only' in r['desc'] or 'content beyond bibliographic metadata' in r['desc']):
        r['evidence']=re.sub(r' Description from the OpenAlex abstract of the lead \(not shown on the record inspected\)\.?','',r['evidence'])
# ---- pass-2026-11-25 topic/metadata post-fixes (Grok Bot): see notes in OVERRIDES below
STRUCT=re.compile(r'beam|column|slab|wall|reinforc|girder|bridge|member|joint|splice|shear|seismic|frame|structures\b|structural|bearing capacity|confine|confinement|pile|precast|prestress|bond of|FRP|armato|armé|bertulang',re.I)
MECH=re.compile(r'creep|shrink|deform|strength|fatigue|fractur|plastic flow|elastic|modul|triaxial|damage|stress|mechan|kuat|dayan|cường độ|résist',re.I)
DURA=re.compile(r'corros|chlorid|durab|sulph|sulfat|frost|freez|carbonat|leach|acid|permeab|diffusion',re.I)
CHEM=re.compile(r'hydrat|chem|C-S-H|CSH|calcium silicate|ettring|NMR|pore solution|thermodynam|ferrit|Kalkhydrat|pozzol|puzol|pozol|水和|水化|microscop|microstructur|zeolit|reaction|electron',re.I)
def fix_topics(r):
    tt=r['title']+' '+(r['desc'] if r['lang']!='en' else '')
    tp=[t for t in r['topics'] if t!='concrete-structural' or STRUCT.search(tt)]
    if 'concrete-polymer-refractory' in tp and re.search(r'geopol',tt,re.I) and not re.search(r'polymer[- ]modif|polymer concrete|epoxy|latex|refractor|high temperature|elevated|fire|resin',tt,re.I):
        tp=[t for t in tp if t!='concrete-polymer-refractory']
        if 'binder-activated' not in tp: tp.insert(0,'binder-activated')
    if tp==['cross-chemistry'] and not CHEM.search(tt):
        tp=[]
        if STRUCT.search(tt): tp.append('concrete-structural')
        if MECH.search(tt): tp.append('cross-mechanics')
        if DURA.search(tt): tp.append('cross-durability')
        if re.search(r'fly ash|tro bay|abu terbang|cinza volante',tt,re.I): tp.append('scm-flyash')
        if re.search(r'lightweight|leve|ringan|cốt liệu nhẹ|köpük|foam',tt,re.I): tp.append('concrete-lightweight')
        if re.search(r'pavement|mặt đường|road',tt,re.I): tp.append('concrete-pavement-pervious')
        if re.search(r'recycl|reclaimed|yıkıntı|waste|atık',tt,re.I): tp.append('concrete-circular')
        if re.search(r'glass fib|GRC',tt,re.I): tp.append('concrete-fibers')
        if re.search(r'byproduct|by-product|industrial',tt,re.I): tp.append('scm-emerging')
        if not tp: tp=['cross-chemistry']
    if not tp: tp=['cross-chemistry']
    r['topics']=list(dict.fromkeys(tp))
UNI=[(r'recycl|demoli|rubble|waste concrete|reclaimed|construction and demolition|reciclad|recyclé|riciclat|再生骨|再生粗|再生細|再生コンクリート|骨材再生|コンクリート塊|コンクリート廃棄物|tái chế|reciklir|geri dönüş|Recyclingbeton|bétons recyclés|béton recyclé','concrete-circular'),
 (r'pervious|porous concrete|beton porous|permeable|permeável|poreux|透水|ポーラス|rỗng thoát|drainable|pavement|chaussée|pavimenta|舗装|路面|nawierzchni|Fahrbahn|paving|airfield|adoquin|roads?\b','concrete-pavement-pervious'),
 (r'overlay|repair|patch|restoration|réparation|reparación|\bgrout|self-heal|crack healing|between new and old|地下連続壁','concrete-repair-grout-overlay'),
 (r'photocatal|titanium dioxide|TiO ?2|self-cleaning|architectural|fa[cç]ade|decorative|fair-faced|blowhole','concrete-architectural'),
 (r'precast|pre-cast|3D[- ]print|printable|printing|hollow[- ]core|tilt-up|segmental|Fertigteil','concrete-precast-insitu-print'),
 (r'CO2|CO 2|carbon dioxide|emission|life.cycle|\bLCA\b|sequestration|environmental|economic|économique|low.carbon|energy efficien','cross-environment-cost'),
 (r'durab|chlorid|sulfat|sulphat|freez|frost|corros|acid|carbonation|alkali.silica|alkali.aggregate|deic|scaling|leach|permeab|D-crack|dayanıklılı|耐久|抗氯','cross-durability'),
 (r'\bstandard|specification|test method|BS EN|EN 206|ASTM|\bcode\b|規程|规程|norma','cross-tests-codes'),
 (r'fly.?ash|tro bay|abu terbang|cinza volante|uçucu kül|粉煤灰|cenizas volantes','scm-flyash'),(r'\bslag|GGBS|scori|escoria|高炉','scm-slag'),(r'silica fume|microsilica|micro-silica','scm-silica'),(r'metakaolin|calcined clay','scm-clay'),(r'pozzol|pumice|zeolit|volcanic|puzolan','scm-natural'),
 (r'geopolym|alkali.activ','binder-activated'),(r'\bfib(?:er|re)|\bFRC\b|SFRC|\bECC\b|strain.hardening|vlákn|纤维|繊維|fibr','concrete-fibers'),(r'high.strength|UHPC|ultra.high|high.performance|高強度|高性能|yüksek dayanım','concrete-hpc'),
 (r'self.compact|self.consolid|autoplaçant|autoadens|selvkompakt|самоуплотн|samozbij|tự lèn','concrete-scc'),(r'lightweight|concreto leve|bê tông nhẹ','concrete-lightweight'),(r'shotcrete|sprayed concrete|吹付け','concrete-shotcrete'),
 (r'roller.compacted|\bRCC\b|碾压|beton wałowany|超硬練り','concrete-mass-rcc'),(r'shielding|heavyweight|radiation','concrete-heavyweight'),(r'masonry|alvenaria','binder-white-masonry'),(r'oil.?well|wellbore','binder-well'),
 (r'curing|placement|pumping|construction practice|quality control|施工','cross-construction')]
UNI=[(re.compile(a,re.I),t) for a,t in UNI]
_fix0=fix_topics
def fix_topics(r):
    _fix0(r)
    tt=r['title']+' '+(r['desc'] if r['lang']!='en' else '')
    tp=list(r['topics'])
    for rx,t in UNI:
        if rx.search(tt) and t not in tp: tp.append(t)
    if 'cross-chemistry' in tp and len(tp)>1 and not CHEM.search(tt): tp.remove('cross-chemistry')
    if 'concrete-lightweight' in tp and not re.search(r'lightweight|light-weight|leve\b|ringan|nhẹ|hafif|aerated|foam|経量|轻',tt,re.I): tp.remove('concrete-lightweight')
    r['topics']=list(dict.fromkeys(tp))
for r in recs: fix_topics(r)
OVR=json.load(open('overrides.json'))
matched=[]
def _dk(r): return OVR['dropRecs'].get(r.get('_key')) or OVR['dropRecs'].get(r.get('url')) or OVR['dropRecs'].get(r['title'])
for r in [r for r in recs if _dk(r)]:
    d=_dk(r)
    if r['_origin'].startswith('retry'):
        matched.append(dict(title=r['_retry']['title'],matchedTo=d['matchedTo'],reason=d['reason'])); promoted_retry.remove(r['_retry']['title'])
    else:
        ld=[l for l in leads if l.get('_key')==r['_key']][0]; ld['_dup']=d['reason']
recs=[r for r in recs if not _dk(r)]
for k,pr in OVR.get('promoteLeads',{}).items():
    ld=[l for l in leads if l.get('_key')==k][0]; assert '_retry' in ld,k
    tp=pr.pop('topics',None) or [ld.get('_rtopic')]
    ld.pop('_retry'); ld.pop('_rtopic',None)
    rec=dict(pr,topics=tp,_key=k,_idx=None,_origin='discovery-'+PASS,rights=None,edition=pr.get('edition')); recs.append(rec)
for r in recs:
    o=OVR['recs'].get(r['title'])
    if o:
        for k,v in o.items():
            if k=='evidenceAppend': r['evidence']+=' '+v
            elif k=='idsMerge': r['ids']=dict(r.get('ids') or {},**v)
            else: r[k]=v
# duplicate-title guard
def tkey(t): return re.sub(r'\W+',' ',t.lower()).strip()
seen={tkey(r['title']) for r in S['resources']}; keep=[]
for r in recs:
    if tkey(r['title']) in seen:
        r['title']='%s (%s, %s)'%(r['title'],(r['date'] or 'n.d.')[:4],'book' if r['type']=='Book' else ((r['ids'] or {}).get('journal') or r['publisher'])[:70])
    seen.add(tkey(r['title'])); keep.append(r)
json.dump(dict(recs=keep,matchedRetry=matched,openQueue=[],openQueueRejected=[],openQueueRetry=[],leads=leads,retryUpdates=retry_upd,promotedFromRetry=promoted_retry,reconfirmed=nconf),open('plan.json','w'),indent=1,ensure_ascii=False,default=str)
print('dups',sum(1 for l in leads if '_dup' in l),[l['title'][:50] for l in leads if '_dup' in l]); print('recs',len(keep),'from retry',len(promoted_retry),'reconfirmed',nconf,'leads',len(leads),'new retry',sum(1 for l in leads if '_retry' in l))
print(collections.Counter(r['access'] for r in keep)); print(collections.Counter(r['lang'] for r in keep)); print(collections.Counter(r['_origin'] for r in keep))
