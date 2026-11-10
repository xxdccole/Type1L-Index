# Lead verification pass — build verified records / rejections from the open candidate queue.
# Run: python3 lv_build.py  (writes plan.json only; apply.py writes the working files)
import json,re,collections
from common import *
from decisions import *
VD='2026-11-10'
X=json.load(open('extra-meta.json'))
CC={'US':'US','GB':'UK','CN':'China','IN':'India','DE':'Germany','FR':'France','CH':'Switzerland','CA':'Canada','AU':'Australia','JP':'Japan','KR':'South Korea','BR':'Brazil','IT':'Italy','ES':'Spain','PT':'Portugal','NL':'Netherlands','BE':'Belgium','SE':'Sweden','NO':'Norway','DK':'Denmark','FI':'Finland','PL':'Poland','CZ':'Czechia','TR':'Turkey','IR':'Iran','SA':'Saudi Arabia','AE':'UAE','EG':'Egypt','ZA':'South Africa','NG':'Nigeria','MY':'Malaysia','SG':'Singapore','TH':'Thailand','VN':'Vietnam','ID':'Indonesia','PK':'Pakistan','BD':'Bangladesh','LK':'Sri Lanka','NZ':'New Zealand','MX':'Mexico','CL':'Chile','CO':'Colombia','AR':'Argentina','PE':'Peru','CU':'Cuba','RU':'Russia','UA':'Ukraine','GR':'Greece','AT':'Austria','IE':'Ireland','IL':'Israel','HK':'Hong Kong','TW':'Taiwan','QA':'Qatar','OM':'Oman','IQ':'Iraq','JO':'Jordan','LB':'Lebanon','MA':'Morocco','DZ':'Algeria','TN':'Tunisia','KE':'Kenya','ET':'Ethiopia','GH':'Ghana','RS':'Serbia','HR':'Croatia','SI':'Slovenia','SK':'Slovakia','HU':'Hungary','RO':'Romania','BG':'Bulgaria','LT':'Lithuania','LV':'Latvia','EE':'Estonia','KZ':'Kazakhstan','PH':'Philippines','NP':'Nepal','KW':'Kuwait','BH':'Bahrain','CY':'Cyprus','IS':'Iceland','LU':'Luxembourg','EC':'Ecuador','VE':'Venezuela','UY':'Uruguay','CM':'Cameroon','TZ':'Tanzania','UG':'Uganda','RW':'Rwanda','ZW':'Zimbabwe','BW':'Botswana','MZ':'Mozambique','SN':'Senegal','CI':"Côte d'Ivoire",'BF':'Burkina Faso','SD':'Sudan','LY':'Libya','SY':'Syria','YE':'Yemen','AF':'Afghanistan','UZ':'Uzbekistan','AZ':'Azerbaijan','GE':'Georgia','AM':'Armenia','BY':'Belarus','MK':'North Macedonia','BA':'Bosnia and Herzegovina','ME':'Montenegro','AL':'Albania','MT':'Malta','MN':'Mongolia','MM':'Myanmar','KH':'Cambodia','LA':'Laos','BN':'Brunei','MO':'Macau','PS':'Palestine','IQ':'Iraq'}
PUB={'Elsevier BV':'Elsevier','Springer Science and Business Media LLC':'Springer','Informa UK Limited':'Taylor & Francis','MDPI AG':'MDPI','Springer International Publishing':'Springer','Frontiers Media SA':'Frontiers','Rilem Publications SARL':'RILEM Publications','Springer Nature Singapore':'Springer','Springer Netherlands':'Springer','Springer Berlin Heidelberg':'Springer','Wiley':'Wiley','American Society of Civil Engineers (ASCE)':'ASCE','Thomas Telford Ltd.':'ICE Publishing','Emerald':'Emerald','IOP Publishing':'IOP Publishing','Hindawi Limited':'Hindawi','American Concrete Institute':'American Concrete Institute','SAGE Publications':'SAGE'}
LIC={'cc-by':'CC BY','cc-by-nc':'CC BY-NC','cc-by-nc-nd':'CC BY-NC-ND','cc-by-sa':'CC BY-SA','cc-by-nc-sa':'CC BY-NC-SA','cc-by-nd':'CC BY-ND','cc0':'CC0','public-domain':'Public domain (US Government work)','other-oa':'Other OA licence'}
TOPICS={t['id'] for t in S['topics']}
RULES=[(r'fly[- ]?ash|coal ash|pulveri[sz]ed fuel ash|\bPFA\b','scm-flyash'),(r'\bslag|GGBF?S','scm-slag'),(r'metakaolin|calcined clay|calcined kaolin','scm-clay'),(r'silica fume|microsilica','scm-silica'),
 (r'limestone (filler|powder|fines)|limestone cement|portland[- ]limestone|\bPLC\b|Type IL','scm-limestone'),(r'geopolymer|alkali[- ]activ|alkali activated','binder-activated'),(r'\bLC3\b|LC³|limestone[- ]calcined[- ]clay','binder-lc3'),
 (r'calcium (sulfo|sulpho)aluminate|\bCSA cement|calcium aluminate|\bCAC\b|aluminous cement|belite[- ]ye','binder-cac-csa'),(r'self[- ]compact|self[- ]consolidat|\bSCC\b','concrete-scc'),
 (r'UHPC|ultra[- ]high[- ]performance|high[- ]strength concrete|high[- ]performance concrete|reactive powder|\bHPC\b|\bUHPFRC','concrete-hpc'),(r'fib(re|er)[- ]reinforced (concrete|cement|mortar|shotcrete)|steel fib|polypropylene fib|glass fib|basalt fib|\bECC\b|engineered cementitious|\bSHCC\b|\bFRC\b|HPFRCC','concrete-fibers'),
 (r'lightweight|expanded clay|pumice aggregate|LWA\b','concrete-lightweight'),(r'recycled (concrete )?aggregate|\bRCA\b|construction and demolition|demolition waste|recycled concrete','concrete-circular'),
 (r'pervious|porous concrete|concrete pavement|rigid pavement|paving|pavement','concrete-pavement-pervious'),(r'shotcrete|sprayed concrete|gunite|gunning','concrete-shotcrete'),(r'3D[- ]print|three[- ]dimensional print|additive manufactur|printable|precast|prefabricat','concrete-precast-insitu-print'),
 (r'foam(ed)? concrete|aerated|cellular concrete|\bAAC\b','concrete-cellular'),(r'mass concrete|roller[- ]compacted|\bRCC\b|\bdams?\b','concrete-mass-rcc'),(r'heavyweight|heavy[- ]weight|radiation shield|gamma|neutron shield|magnetite|barite|hematite','concrete-heavyweight'),
 (r'refractory|castable|polymer concrete|polymer[- ]modified|latex[- ]modified|epoxy mortar','concrete-polymer-refractory'),(r'repair|overlay|grout|retrofit|strengthen|rehabilitat','concrete-repair-grout-overlay'),
 (r'reinforced concrete|prestress|\bbeams?\b|\bcolumns?\b|\bslabs?\b|shear wall|girder|bridge deck|\bbond\b|rebar|reinforcing (bar|steel)','concrete-structural'),
 (r'oil[- ]?well|well cement|cementing|zonal isolation|geothermal well|wellbore','binder-well'),(r'magnesi|\bMgO\b|M-S-H|magnesium silicate hydrate|magnesium phosphate|oxychloride|carbonatable|CO2[- ]cured|carbonation[- ]cur','binder-magnesium-carbonatable'),
 (r'expansive cement|shrinkage[- ]compensat|rapid[- ]harden|rapid[- ]set|expansive agent','binder-specialty'),(r'white (portland )?cement|masonry cement|masonry mortar|stucco|plaster|colou?red (concrete|cement)','binder-white-masonry'),
 (r'natural pozzolan|volcanic|pumice|zeolite|diatom|perlite|tuff','scm-natural'),(r'rice husk|bagasse|biomass ash|palm oil|glass powder|ground glass|waste glass|red mud|bauxite residue|biochar|incinerat|steel slag|copper slag|ceramic waste','scm-emerging'),
 (r'portland cement|ordinary portland|\bOPC\b|clinker','binder-portland'),(r'blended cement|ternary|composite cement|Type I[PST]\b','binder-blended'),(r'exposed aggregate|architectural|decorative|cladding|heritage|historic','concrete-architectural'),
 (r'hydration|C-S-H|calcium silicate hydrate|ettringite|microstructur|thermodynamic|clinker|kiln|phase|pore solution|NMR|XRD|chemistry','cross-chemistry'),
 (r'mix(ture)? (design|proportion)|admixture|superplasticiz|plasticiz|rheolog|workability|aggregate|packing','cross-mix'),(r'curing|placement|formwork|cold weather|hot weather|compaction|pumping|revibrat|construction','cross-construction'),
 (r'strength|shrinkage|creep|crack|fracture|fatigue|elastic|thermal stress|mechanical|flexur|softening|toughness','cross-mechanics'),
 (r'durab|corrosion|chloride|sulfate|sulphate|freez|frost|alkali[- ]silica|\bASR\b|carbonation|service life|seawater|marine|deteriorat|leach|acid','cross-durability'),
 (r'test method|standard|specification|ASTM|\bEN \d|\bISO \d|code|testing','cross-tests-codes'),(r'failure|collapse|case stud|field (performance|evaluation|investigation)|forensic|damage','cross-failure-repair'),
 (r'life[- ]cycle|\bLCA\b|cost|environment|sustainab|eco[- ]friendly|low[- ]carbon|green','cross-environment-cost'),(r'CO2|carbon (emission|footprint|dioxide)|embodied|\bGWP\b|\bEPD\b|decarboni|net[- ]zero|sequestr|mineraliz','cross-environment-cost')]
RULES=[(re.compile(p,re.I),t) for p,t in RULES]
def topics_for(base,title,query=''):
    out=[]
    for b in base:
        if b in TOPICS and b not in out: out.append(b)
    for rx,t in RULES:
        if len(out)>=6: break
        if rx.search(title) and t not in out: out.append(t)
    if not out:
        for rx,t in RULES:
            if rx.search(query) and t not in out: out.append(t); break
    return out or ['cross-chemistry']
REVIEW=re.compile(r'\breview\b|state[- ]of[- ]the[- ]art|\boverview\b|critical assessment|scientometric|meta[- ]analy|bibliometric',re.I)
def typ_of(ct,ot,title):
    m={'journal-article':'Paper','proceedings-article':'Conference paper','book-chapter':'Book chapter','book':'Book','monograph':'Book','edited-book':'Book','reference-book':'Book','report':'Report','dissertation':'Thesis','posted-content':'Preprint','standard':'Standard','dataset':'Dataset','proceedings':'Proceedings','component':'Statistical table','article':'Paper','preprint':'Preprint','book-chapter':'Book chapter','other':'Other'}
    t=m.get(ct) or m.get(ot) or 'Paper'
    if t=='Paper' and REVIEW.search(title): t='Review paper'
    return t
def fmt(parts):
    p=(parts or [[None]])[0]
    if not p or p[0] is None: return None
    return '-'.join([str(p[0])]+['%02d'%x for x in p[1:3]])
def oadate(s):
    if not s: return None
    return s[:4] if s.endswith('-01-01') else s
def first_sents(a,n=300):
    a=clean(a); a=re.sub(r'^(abstract|summary|synopsis)[:.\s]+','',a,flags=re.I)
    if not a or ' -- ' in a or re.match(r'(Department|Faculty|School) of',a) or len(a)<60: return ''
    out=''
    for s in re.split(r'(?<=[a-z0-9\)][.!?])\s+(?=[A-Z])',a):
        if len(out)>=120 and len(out)+len(s)>n: break
        out+=(' ' if out else '')+s
    if len(out)>n+80: out=out[:n].rsplit(' ',1)[0]+'…'
    return out if len(out)>=60 else ''
def geo(d):
    cs=X['countries'].get(d) or []
    return ' / '.join(CC.get(c,c) for c in cs[:4]) or None
def astm_desig(d):
    s=d.split('/',1)[1].upper()
    s=re.sub(r'([A-Z])0+(\d)',r'\1\2',s).replace('_','/')
    return 'ASTM '+s
# ---------- existing index keys
d2id={};t2id={}
for r in S['resources']:
    u=r['url'].lower()
    if 'doi.org/' in u: d2id[u.split('doi.org/')[1].rstrip('/')]=r['id']
    t2id[norm(r['title'].split(' (')[0])]=r['id']
for v in VER:
    if v.get('doi'): d2id[v['doi'].lower()]=v['id']
STD_EXIST={'ASTM C845':'R179','ASTM C1600':'R180','ASTM C1866':'R185'}
# ---------- per-lead plan
plan={}   # idx -> dict(action, ...)
recs={}   # key -> record (promote)
def add_rec(key,rec,idx):
    if key in recs:
        r=recs[key]
        for t in rec['topics']:
            if t not in r['topics'] and len(r['topics'])<7: r['topics'].append(t)
        r['leadIdx'].append(idx); plan[idx]=dict(action='dup-merge',key=key)
    else:
        rec['leadIdx']=[idx]; recs[key]=rec; plan[idx]=dict(action='promote',key=key)
std_groups=collections.defaultdict(list)
for i,x in enumerate(CAN):
    if x['status']!='candidate': continue
    d=(x.get('doi') or '').lower()
    base=[x['topic']] if x['topic']!='current-2026' else CURRENT_Q.get(x.get('query'),[])
    if i in REJECT_IDX: plan[i]=dict(action='reject',reason=REJECT_IDX[i]); continue
    if i in MANUAL_DUP: plan[i]=dict(action='manualdup',targets=MANUAL_DUP[i]); continue
    if not d:
        o=ND.get(x['title'],{}); ov=NODOI.get(i,{})
        if 'open' in ov: plan[i]=dict(action='open',reason=ov['open']); continue
        if not ov and not o.get('found'): plan[i]=dict(action='open',reason='no DOI and no OpenAlex/repository record found'); continue
        ab=clean(o.get('abstract')); land=ov.get('landing')
        if land is None:
            cp=[p for p in (o.get('curlProbe') or []) if p[1]==200]
            land=200 if cp else 'not reachable'
        url=ov.get('url') or ([p[2] for p in (o.get('curlProbe') or []) if p[1]==200] or [None])[0] or o.get('landing')
        ok=(land==200 or str(land).startswith('200')) or len(ab)>=200
        if not ok or not url: plan[i]=dict(action='open',reason='landing %s and no usable abstract'%land); continue
        title=ov.get('title') or clean(o.get('title') or x['title'])
        title=title.replace('â','—')
        typ=ov.get('type') or typ_of(None,o.get('type'),title)
        access=ov.get('access') or ('abstract_metadata' if len(ab)>=200 else 'catalog_metadata')
        lt='landing page HTTP 200 on %s (page content not reviewed)'%VD if (land==200) else 'landing page %s on %s'%(land,VD)
        ev=ov.get('ev') or ('Promoted from candidate queue. OpenAlex record (%s)%s inspected %s; %s; full text not reviewed.'%(o.get('id','').split('/')[-1],' and abstract' if access=='abstract_metadata' else '',VD,lt))
        if not ev.startswith('Promoted') : ev='Promoted from candidate queue. '+ev
        desc=ov.get('desc') or (first_sents(ab) if ab else '%s (%s) listed in %s; content beyond bibliographic metadata not reviewed.'%(typ,(o.get('date') or '')[:4] or 'undated',o.get('venue') or 'a repository'))
        pub=ov.get('publisher') or o.get('publisher') or o.get('venue') or 'unknown'
        if o.get('venue') and o.get('venue') not in pub and not ov.get('publisher'): pub=pub+' ('+o['venue'][:80]+')' if o.get('publisher') else pub
        rec=dict(title=title,authors=ov.get('authors') or o.get('authors') or None,publisher=pub,type=typ,date=ov.get('date') or oadate(o.get('date')),url=url,doi=None,ids=dict(ov.get('ids') or {},openalex=(o.get('id') or '').split('/')[-1] or None),topics=topics_for(ov.get('topics') or base,title,x.get('query','')),geo=None,lang=(o.get('lang') or 'en'),desc=desc,access=access,evidence=ev,edition=ov.get('edition'),rights=None)
        rec['ids']={k:v for k,v in rec['ids'].items() if v}
        add_rec('url:'+url.lower(),rec,i); continue
    # ---- DOI leads
    r=M.get(d,{}); c=r.get('crossref') or {}; o=r.get('openalex') or {}; dc=r.get('datacite') or {}
    if d in d2id: plan[i]=dict(action='reject',reason='duplicate of %s (same DOI)'%d2id[d]); continue
    if o.get('retracted'): plan[i]=dict(action='reject',reason='retracted per OpenAlex'); continue
    if c.get('type')=='component' and re.search(r'\.s\d{3}$',d):
        p=re.sub(r'\.s\d{3}$','',d)
        if p in COMPONENT_PARENT_OFFTOPIC: plan[i]=dict(action='reject',reason=COMPONENT_PARENT_OFFTOPIC[p]); continue
        if p in d2id: plan[i]=dict(action='reject',reason='supporting-information file; parent article is already %s'%d2id[p]); continue
        pm=X['parents'].get(p)
        if not pm: plan[i]=dict(action='open',reason='supporting-information file; parent article metadata not retrieved'); continue
        title=clean(pm['title'][0]); cont=clean((pm.get('container') or [''])[0])
        pub=PUB.get(pm.get('publisher'),pm.get('publisher'))
        ab=clean(pm.get('abstract'))
        access='abstract_metadata' if len(ab)>80 else 'doi_metadata'
        ev='Promoted from candidate queue. Lead was a supporting-information file (%s); resolved to its parent article via Crossref metadata%s inspected %s; full text not reviewed.'%(d,' and abstract' if ab else '',VD)
        rec=dict(title=title,authors=[a for a in pm['authors'] if a] or None,publisher=pub+(' ('+cont+')' if cont else ''),type='Paper',date=fmt(pm.get('issued')),url='https://doi.org/'+p,doi=p,ids={'journal':'%s %s%s'%(cont,pm.get('volume') or '',(':'+pm['page']) if pm.get('page') else '')},topics=topics_for(base,title),geo=geo(p),lang='en',desc=first_sents(ab) or 'Paper in %s; content beyond bibliographic metadata not reviewed.'%cont,access=access,evidence=ev,edition=None,rights=None)
        add_rec('doi:'+p,rec,i); continue
    if c.get('type') in ('grant',) or (c and not (c.get('title') or [''])[0] and not o.get('title')):
        plan[i]=dict(action='reject',reason='not a substantive source (no title / grant record)'); continue
    title=vt(d)
    if not title: plan[i]=dict(action='open',reason='no title in any registry record'); continue
    tid=t2id.get(norm(title))
    if tid: plan[i]=dict(action='reject',reason='duplicate of %s (same title)'%tid); continue
    if c.get('type')=='standard':
        std_groups[(c.get('publisher'),norm(title))].append((i,d)); continue
    # bibliographic
    authors=[a for a in (c.get('authors') or []) if a] or None; asrc='Crossref'
    if not authors and o.get('authors'): authors=o['authors']; asrc='OpenAlex'
    if not authors and dc.get('authors'): authors=dc['authors']; asrc='DataCite'
    date=fmt(c.get('issued')) or oadate(o.get('date')) or (str(dc.get('year')) if dc.get('year') else None)
    pub=c.get('publisher') or dc.get('publisher') or o.get('publisher'); pub=PUB.get(pub,pub) if pub else None
    conts=[clean(z) for z in (c.get('container') or [])]
    cont=' — '.join(conts[:2]) if conts else (o.get('venue') if not c else None)
    if not pub: pub=o.get('venue') or 'unknown'
    publisher=pub+(' ('+cont[:100]+')' if cont and cont!=pub else '')
    ids={}
    if conts: ids['journal']=('%s %s%s'%(conts[0][:80],c.get('volume') or '',(':'+c['page']) if c.get('page') else '')).strip()
    if c.get('isbn'): ids['isbn']=c['isbn'][0]
    ab=abstract(d)
    access='abstract_metadata' if len(ab)>80 else 'doi_metadata'
    src='Crossref' if c else ('DataCite' if dc else 'OpenAlex')
    ev='Promoted from candidate queue. %s metadata%s inspected %s'%(src,' and abstract' if access=='abstract_metadata' else '',VD)
    st=r.get('doiStatus')
    if st in (301,302): ev+='; DOI registered (doi.org redirect to %s)'%((r.get('doiLocation') or '').split('/')[2] if (r.get('doiLocation') or '').count('/')>=2 else 'publisher')
    elif st==404: ev+='; DOI NOT registered at doi.org (404)'
    ev+='; full text not reviewed.'
    if asrc!='Crossref' and src=='Crossref': ev+=' Authors from %s because Crossref registers none.'%asrc
    if not authors: ev+=' No authors registered (unknown).'
    url='https://doi.org/'+d
    if st==404:
        land=o.get('landing')
        if not land: plan[i]=dict(action='open',reason='DOI not registered (doi.org 404) and no alternative landing page'); continue
        url=land; ev+=' Canonical URL is the OpenAlex landing page because the listed DOI does not resolve.'
    lic=o.get('license'); rights=('OpenAlex: '+LIC.get(lic,lic)) if lic else None
    typ=typ_of(c.get('type'),o.get('type'),title)
    if dc and not c and (dc.get('type') or '').lower()=='dissertation': typ='Thesis'
    desc=first_sents(ab) or '%s%s%s; content beyond bibliographic metadata not reviewed.'%(typ,(' in '+cont[:90]) if cont else '',(' ('+date[:4]+')') if date else '')
    ed=None
    rel=c.get('relation') or {}
    if rel.get('is-preprint-of'): ed='Preprint; published version: '+', '.join(z.get('id') for z in rel['is-preprint-of'])
    if c.get('update-to'): ed='Update notice for '+', '.join(z.get('DOI','') for z in c['update-to'])
    rec=dict(title=title,authors=authors,publisher=publisher,type=typ,date=date,url=url,doi=d if st!=404 else None,ids=dict(ids,**({'listedDoiUnregistered':d} if st==404 else {})),topics=topics_for(base,title,x.get('query','')),geo=geo(d),lang=o.get('lang') or 'en',desc=desc,access=access,evidence=ev,edition=ed,rights=rights)
    add_rec('doi:'+d if st!=404 else 'url:'+url.lower(),rec,i)
# ---------- standards: one record per document, latest dated edition; others rejected as superseded/duplicate versions
for (pubr,tn),items in std_groups.items():
    def appr(d):
        s=X['standards'].get(d,{}); a=fmt(s.get('approved'))
        return a or ''
    items=sorted(items,key=lambda z:(appr(z[1]),z[1]))
    best_i,best_d=items[-1]
    c=M[best_d]['crossref']; title=vt(best_d); s=X['standards'].get(best_d,{})
    x=CAN[best_i]; base=[x['topic']]
    if pubr=='ASTM International':
        des=astm_desig(best_d); root=re.match(r'ASTM [A-Z]+\d+',des).group(0)
        if root in STD_EXIST:
            for i,d in items: plan[i]=dict(action='reject',reason='duplicate-version of %s (%s; %s indexed as the current edition)'%(STD_EXIST[root],astm_desig(d),STD_EXIST[root]))
            continue
        ftitle='%s %s'%(des,title if title.lower().startswith('standard') else 'Standard '+title)
        if not appr(best_d): # undated pointer only
            dated=[z for z in items if appr(z[1])]
        prior=[astm_desig(d) for i,d in items[:-1]]
        ed='Latest edition registered in Crossref for this designation (approved %s). Earlier editions in the lead queue: %s — superseded.'%(appr(best_d) or 'date not registered',', '.join(prior) or 'none')
        publisher='ASTM International'; authors=[a for a in s.get('authors',[]) if a] or ['ASTM Committee (not registered)']
    else:
        ftitle=title if pubr!='BSI British Standards' else 'BSI: '+title
        ed=None; publisher=pubr; authors=[s.get('body')] if s.get('body') else None
        prior=[d for i,d in items[:-1]]
        if prior: ed='Other BSI DOIs with the same title (earlier-dated or undated records, treated as versions): '+', '.join(prior)
    date=appr(best_d) or None
    ev='Promoted from candidate queue. Crossref standard record (title, standards body, %sresolver URL) inspected %s; DOI registered; normative text not reviewed (paywalled).'%('approval date, ' if date else '',VD)
    if pubr=='BSI British Standards': ev+=' Crossref gives no BS/EN designation for this record (BSI document %s); designation unknown.'%best_d.split('/')[1]
    desc='%s catalogue record: %s.'%(publisher,title)+(' Edition approved %s.'%date if date else '')
    rec=dict(title=ftitle,authors=authors,publisher=publisher,type='Standard catalogue record',date=date,url='https://doi.org/'+best_d,doi=best_d,ids={'standardsBody':s.get('body') or pubr,'resolver':s.get('resource')},topics=topics_for(base+['cross-tests-codes'],title),geo=None,lang='de' if 'DIN' in (pubr or '') else 'en',desc=desc,access='doi_metadata',evidence=ev,edition=ed,rights=None)
    if pubr=='BSI British Standards' and 'calcium aluminate cement' in title.lower():
        for i,d in items: plan[i]=dict(action='reject',reason='duplicate-version of R181 (title matches EN 14647 Calcium aluminate cement; BSI national record of the same EN)')
        continue
    key='doi:'+best_d
    rec['leadIdx']=[best_i]; recs[key]=rec; plan[best_i]=dict(action='promote',key=key)
    for i,d in items[:-1]: plan[i]=dict(action='std-superseded',key=key,doi=d)
# ---------- within-queue title duplicates (versions): keep best type
pref={'Paper':0,'Review paper':0,'Standard catalogue record':0,'Book':1,'Report':1,'Thesis':1,'Book chapter':2,'Conference paper':2,'Proceedings':2,'Preprint':5,'Other':6,'Dataset':4}
bytitle=collections.defaultdict(list)
for k,r in recs.items(): bytitle[norm(r['title'])].append(k)
for tn,ks in bytitle.items():
    if len(ks)<2: continue
    if len(tn)<25: continue
    yrs={(recs[k].get('date') or '')[:4] for k in ks}
    if len(yrs)>1 and not any(recs[k]['type']=='Preprint' for k in ks): continue
    ks=sorted(ks,key=lambda k:(pref.get(recs[k]['type'],3),-(len(recs[k]['desc'])),k))
    keep=recs[ks[0]]
    for k in ks[1:]:
        r=recs.pop(k)
        for t in r['topics']:
            if t not in keep['topics'] and len(keep['topics'])<7: keep['topics'].append(t)
        keep.setdefault('versions',[]).append(r.get('doi') or r['url'])
        for idx in r['leadIdx']: plan[idx]=dict(action='version-dup',key=ks[0],what=r.get('doi') or r['url'])
# ---------- front matter / generic chapter titles
for k in list(recs):
    r=recs[k]
    if re.match(r'^(copyright|front ?matter|back ?matter|index|title page|contents)$',r['title'].strip(),re.I):
        recs.pop(k)
        for idx in r['leadIdx']: plan[idx]=dict(action='reject',reason='not a substantive source (front-matter "%s" page of a book)'%r['title'])
        continue
    if r['type']=='Book chapter' and len(r['title'])<36:
        cont=r['publisher'].split('(',1)[1].rstrip(')') if '(' in r['publisher'] else ''
        if cont: r['title']='%s — in %s'%(r['title'],cont.split(' — ')[-1])
    r['publisher']=re.sub(r'(ASTM International).*',r'\1',r['publisher']) if r['publisher'].startswith('ASTM International') else r['publisher']
    if r['type']=='Other' and '.ch' in (r.get('doi') or ''): r['type']='Book chapter'
# ---------- title uniqueness against index + among new (validator rejects duplicate titles)
def tkey(t): return re.sub(r'\W+',' ',t.lower()).strip()
seen={tkey(r['title']) for r in S['resources']}
for k,r in recs.items():
    if tkey(r['title']) in seen:
        extra=', '.join(z for z in [(r.get('date') or '')[:4],(r['ids'].get('journal') or r['publisher'])[:60]] if z)
        r['title']='%s (%s)'%(r['title'],extra)
        if tkey(r['title']) in seen: r['title']+=' [%s]'%(r.get('doi') or r['url'])
    seen.add(tkey(r['title']))
json.dump({'plan':{str(k):v for k,v in plan.items()},'recs':recs},open('plan.json','w'),indent=1,ensure_ascii=False)
print(collections.Counter(v['action'] for v in plan.values()),len(recs))
