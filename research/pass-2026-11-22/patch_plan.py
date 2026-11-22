"""pass-2026-11-22: post-process plan.json. (1) fix the 3 retry-list promotions (topics, description, language, DOI note); (2) topic inference for fallback-only discovery records;
(3) description/evidence tidy-ups; (4) open-queue records (oq-records.json) and open-queue leads moved to the review list (oq-retry.json)."""
import json,re
P=json.load(open('plan.json')); VD='2026-11-22'
for r in P['recs']:
    if 'concrete.org/publications/internationalconcreteabstractsportal' in r['url'] and r['_origin']=='retry-list-retried':
        if 'i=17603' in r['url']:
            r['desc']='ACI Special Publication 47 (1975) chapter by T.C. Powers on the mechanism of freezing and thawing damage in concrete: the author discusses how the theories advanced over more than 40 years have evolved (record abstract cut off on the page).'
            r['ids']['listedDoi']='10.14359/17603 (named on the lead and on the ACI page; not registered at Crossref/DataCite)'
        else:
            r['desc']='ACI Special Publication 47 (1975) chapter by F.P. Browne and P.D. Cady reporting three experiments on the two primary deicer scaling mechanisms in concrete, the first being a hydraulic pressure mechanism (record abstract cut off on the page).'
        r['topics']=['durability','cross-durability']
        r['evidence']=r['evidence'].replace('Title matches the lead.','Title matches the lead; the ACI abstract portal had not opened for this item on earlier retries (the DOI named on the lead is not registered at Crossref/DataCite). Authors, series (Special Publication 47) and pages from the page metadata.')
    if r['url'].startswith('https://radial.e-journal.unbitago.ac.id'):
        r['lang']='id'; r['topics']=['scm-flyash','cross-mechanics']
        r['desc']='Indonesian-language paper (RADIAL 8(1), 2020) on the compressive strength of 45 MPa high-strength concrete with fly ash as a partial cement replacement.'
        r['evidence']=r['evidence'].replace('Title matches the lead.','Title matches the lead. Title/abstract not in English; description is an English gloss.')
RULES=[(r'massenbeton|mass concrete|concretes? massa|大体积|大掺量|massive concrete','mass'),(r'flugasche|fly ash|粉煤灰|cinza volante','scm-flyash'),(r'fibr|serat|faser|纤维|繊維','concrete-fibers'),(r'hormigón armado|reinforced concrete|béton armé|calcestruzzo armato|cemento armato|stahlbeton|鉄筋','concrete-structural'),(r'fisurac|crack|ひび割れ|fissur|\bRiss','microcracking'),(r'argamassa|mortar|mortero|mortier|masonry|alvenaria|mauerwerk','binder-white-masonry'),(r'metakaol|metacaol','scm-clay'),(r'proiettato|shotcrete|sprayed','concrete-shotcrete'),(r'geopol|alkali.activ','binder-activated'),(r'sulfoalum|\bCSA\b','binder-cac-csa'),(r'radiation|shield|heavyweight','concrete-heavyweight'),(r'ultra.hautes|ultra.high|UHPC|high.performance|high.strength|高性能|mutu tinggi','concrete-hpc'),(r'roller.compact','concrete-mass-rcc'),(r'calcined clay|brick|halloysite|kaolin','scm-clay')]
for r in P['recs']:
    if r['topics']==['cross-chemistry'] or r['topics']==['cross-mechanics']:
        add=[t for rx,t in RULES if re.search(rx,r['title'],re.I)]
        if add: r['topics']=add[:3]+([r['topics'][0]] if r['topics']==['cross-mechanics'] else [])
    # tidy descriptions cut off by the page meta
    if r['desc'] and r['desc'][-1] not in '.)…' and r['_origin'] and r['access']=='landing_page_inspected' and 'language' not in r['desc'][:40]:
        r['desc']='%s in %s (%s); the record page abstract is cut off, so content beyond bibliographic metadata is not reviewed.'%(r['type'],((r['ids'] or {}).get('journal') or r['publisher'])[:90],(r['date'] or 'undated')[:4])
    def fx(m):
        c=m.group(1)
        return 'original landing page did not open (%s)'%{'ski':'host not openable from the box','200':'HTTP 200 but the title was not found on the page','202':'HTTP 202, no content','000':'no response','403':'HTTP 403','404':'HTTP 404','500':'HTTP 500','503':'HTTP 503','418':'HTTP 418'}.get(c,'HTTP '+c)
    r['evidence']=re.sub(r'original landing page did not open \((\w+)\)',fx,r['evidence'])
# keep leads in sync (a lead whose record was dropped would raise in apply.py)
# open queue
OQR=json.load(open('oq-records.json'))
oq=[]
for x in OQR:
    d=dict(title=x['title'],authors=x['authors'],publisher=x['publisher'],type=x['type'],date=x['date'],url=x['url'],doi=x['doi'],ids=x['ids'],topics=x['topics'],geo=None,lang='en',desc=x['desc'],access=x['access'],evidence=x['evidence'],edition=None,rights=None,_origin='open-queue-pass-2026-11-22',_cand=x['title'],_cand_idx=x['i'],_key='oq:'+str(x['i']),_route=x['route'])
    oq.append(d)
TITLES={'Hardened Concrete Properties Workbook 2026 (KDOT certified inspector training)':'Hardened Concrete Properties Workbook (Certified Inspector Training Program)','Portland-Limestone Cement after 10 Years in the Field (MAP Brief Oct 2018)':'Portland-Limestone Cement after 10 Years in the Field (MAP Brief, October 2018)','KDOT OFQ – KDOT Official Quality Status by Quarry (test history app)':'Official Quality Status by Quarry (OFQ), Kansas Department of Transportation','High Dosage Type-C Fly Ash and Limestone in Sand-Gravel Concrete (TRR, 1996)':'High Dosage Type-C Fly Ash and Limestone in Sand-Gravel Concrete','Nebraska Aggregate Reactivity Evaluation Phase I–II':"Nebraska's Aggregates Reactivity Evaluation – Phase I–II",'Investigation of Optimize Graded Concrete for Oklahoma – Phase I':'Investigation of Optimized Graded Concrete for Oklahoma – Phase I'}
for d in oq: d['title']=TITLES.get(d['title'],d['title'])
P['openQueue']=oq; P['openQueueRejected']=[]; P['openQueueRetry']=json.load(open('oq-retry.json'))
json.dump(P,open('plan.json','w'),indent=1,ensure_ascii=False,default=str)
print(len(P['recs']),len(P['leads']),len(oq),len(P['openQueueRetry']))
