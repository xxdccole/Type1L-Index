"""pass-2026-11-27 harvest: OpenAlex title.search backfill for the least-covered topics (binder-specialty, concrete-mass-rcc, binder-well, concrete-heavyweight, concrete-cellular, concrete-shotcrete, binder-white-masonry, binder-cac-csa, binder-lc3, binder-magnesium-carbonatable, scm-clay, binder-blended, concrete-lightweight, scm-natural, binder-international), historical (<=1990) and language sweeps, and current awareness 2026-11-20 -> 2026-11-27. Exact repeats of prior-queries-all.json skipped."""
import json,urllib.request,urllib.parse,time
T='t';S_='s'
Q=[]
def t(tp,*qs):
    for q in qs: Q.append((tp,T,q,None,None))
t('binder-well','oil well cement slurry','geothermal well cement','cement sheath integrity wellbore','well cement CO2 degradation','retarder oil well cement','API Class G cement','cement slurry gas migration','high temperature well cement silica','foamed cement well','cement plug abandonment')
t('binder-specialty','calcium sulfoaluminate cement hydration','rapid setting cement','expansive cement shrinkage compensating','Type K expansive cement','calcium aluminate cement conversion','belite-ye\'elimite cement','magnesium phosphate cement','ultra-rapid hardening cement','Portland cement rapid repair mortar','Roman cement natural cement','Type III high early strength cement','sulfate resistant cement Type V','low heat Portland cement','ettringite expansive additive')
t('binder-magnesium-carbonatable','reactive magnesia cement','magnesium oxychloride cement','magnesium oxysulfate cement','carbonation curing concrete','carbonatable calcium silicate cement','MgO cement hydrated magnesium carbonates','magnesium silicate hydrate cement','CO2 mineralization cement')
t('scm-clay','calcined clay pozzolan','metakaolin concrete','calcined clay limestone cement strength','calcined kaolinite reactivity','calcined clay chloride resistance','activated clay pozzolana','brick powder cement replacement','calcined shale cement','illite smectite calcination cement')
t('concrete-mass-rcc','roller compacted concrete dam','mass concrete thermal cracking','mass concrete temperature control','RCC dam construction','low heat cement mass concrete','Hoover Dam concrete','cemented material dam','concrete dam cooling pipe','hardfill dam')
t('concrete-cellular','foamed concrete','aerated autoclaved concrete','cellular concrete density','foam concrete thermal conductivity','foamed concrete fly ash','lightweight foam concrete shrinkage','autoclaved aerated concrete tobermorite','foam stability cementitious')
t('concrete-heavyweight','heavyweight concrete radiation shielding','barite concrete','magnetite concrete','neutron shielding concrete boron','high density concrete aggregate','nuclear reactor concrete shielding','steel slag heavyweight concrete','gamma radiation shielding cementitious')
t('concrete-shotcrete','shotcrete tunnel lining','wet mix shotcrete','dry-mix shotcrete','accelerator shotcrete','steel fibre reinforced shotcrete','sprayed concrete durability','shotcrete rebound','shotcrete early strength','gunite history')
t('binder-blended','Portland limestone cement Type IL','Portland-composite cement','CEM II limestone cement','ternary blended cement','pozzolanic cement Type IP','slag cement Type IS','portland limestone cement sulfate','interground limestone cement fineness','ASTM C595 blended hydraulic cement','CEM IV pozzolanic cement','composite cements CEM V')
t('binder-white-masonry','white Portland cement','masonry cement','mortar cement','lime mortar historic','masonry mortar bond strength','white cement whiteness','hydraulic lime','lime putty mortar','mortar for brick masonry','stucco plaster cement')
t('binder-cac-csa','high alumina cement','calcium aluminate cement refractory castable','CSA cement low carbon','aluminate cement hydration kinetics','sulfoaluminate belite cement concrete')
t('binder-lc3','LC3 cement','limestone calcined clay cement durability','LC3 concrete field trial')
t('concrete-lightweight','lightweight aggregate concrete structural','expanded clay aggregate concrete','pumice lightweight concrete','sintered fly ash aggregate','internal curing lightweight aggregate','lightweight concrete bridge')
t('scm-natural','volcanic ash cement','natural pozzolan concrete','zeolite cement','pumice pozzolan','diatomaceous earth pozzolan','Roman concrete pozzolan')
t('binder-international','Indian cement industry','cement industry Africa','Chinese cement standard','Brazilian Portland cement','Japanese cement industry history')
# historical
for tp,q,per in [('binder-well','cement for oil wells history',':1975'),('binder-specialty','special cements',':1980'),('concrete-mass-rcc','mass concrete dams',':1960'),('concrete-shotcrete','pneumatically placed mortar',':1975'),('concrete-cellular','aerated concrete',':1975'),('concrete-heavyweight','concrete for radiation shielding',':1975'),('binder-white-masonry','mortar for masonry',':1960'),('scm-clay','pozzolanic clay',':1980'),('binder-magnesium-carbonatable','magnesia cement',':1960'),('binder-blended','blended cements',':1970'),('binder-cac-csa','aluminous cement',':1970')]:
    Q.append((tp,S_,q,per,None))
# languages
for tp,q,l in [('lang-de','Spezialzement','de'),('lang-de','Leichtbeton','de'),('lang-fr','béton projeté','fr'),('lang-fr','ciment alumineux','fr'),('lang-es','cemento sulfoaluminato','es'),('lang-es','hormigón celular','es'),('lang-pt','concreto massa','pt'),('lang-pt','cimento de poço de petróleo','pt'),('lang-ru','тампонажный цемент','ru'),('lang-ru','пенобетон','ru'),('lang-zh','硫铝酸盐水泥','zh'),('lang-zh','油井水泥','zh'),('lang-zh','煅烧黏土水泥','zh'),('lang-ja','吹付けコンクリート','ja'),('lang-ja','マスコンクリート','ja'),('lang-it','calcestruzzo alleggerito','it'),('lang-tr','köpük beton','tr'),('lang-pl','cement glinoglinowy','pl'),('lang-id','beton busa','id'),('lang-vi','bê tông bọt','vi'),('lang-ko','숏크리트','ko')]:
    Q.append((tp,T,q,None,l))
# current awareness
for q,per in [('concrete','2026-11-20:'),('cement','2026-11-20:'),('mortar','2026-11-20:'),('shotcrete','2026-10-15:'),('foamed concrete','2026-10-15:'),('calcined clay','2026-10-15:'),('oil well cement','2026-09-01:'),('magnesium cement','2026-10-01:'),('sulfoaluminate','2026-10-01:'),('mass concrete','2026-10-15:'),('radiation shielding concrete','2026-10-01:'),('limestone cement','2026-11-10:'),('alkali-activated','2026-11-20:'),('low-carbon cement','2026-11-20:')]:
    Q.append(('current-2026',S_,q,per,None))
PR={tuple(x) for x in json.load(open('prior-queries-all.json'))}
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def get(u):
  for i in range(5):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    except Exception as e: err=e; time.sleep(4*(i+1))
  raise err
SEL='id,doi,title,publication_year,publication_date,type,language,cited_by_count,authorships,primary_location,abstract_inverted_index,is_retracted,open_access,biblio,referenced_works'
TY='type:article|book-chapter|report|dissertation|book|review|standard'
out={};log=[];sk=[]
for tp,mode,q,per,lang in Q:
  if (tp,q,per,lang) in PR or (tp,'title.search:'+q,per,lang) in PR: sk.append([tp,q,per,lang]); continue
  if mode==T: f='title.search:%s,%s'%(q,TY)
  else:
    f='title_and_abstract.search:%s,%s'%(q,TY)
  if per:
    a,b=per.split(':'); 
    if a: f+=',from_publication_date:'+a
    if b: f+=',to_publication_date:'+(b+'-12-31' if len(b)==4 else b)
  if lang: f+=',language:'+lang
  p={'filter':f,'per-page':25,'sort':'cited_by_count:desc' if tp!='current-2026' else 'publication_date:desc','select':SEL,'mailto':'research@example.org'}
  ent=dict(topic=tp,mode='title.search' if mode==T else 'title_and_abstract.search',query=q,period=per,language=lang,n=0,errors=[])
  try:
    d=get('https://api.openalex.org/works?'+urllib.parse.urlencode(p)); ent['returned']=len(d['results'])
    for w in d['results']:
      k=(w.get('doi') or w['id']).lower()
      if k in out: out[k]['queries'].append([tp,q]); continue
      w['queries']=[[tp,q]]; out[k]=w; ent['n']+=1
  except Exception as e: ent['errors'].append(str(e))
  log.append(ent); print(tp,q,per,ent['n'],ent['errors'],flush=True); time.sleep(0.25)
json.dump(dict(log=log,skippedRepeats=sk),open('search-log.json','w'),indent=1); json.dump(out,open('api-hits.json','w')); print('total',len(out),'skipped',len(sk))
