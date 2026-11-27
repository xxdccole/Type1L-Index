"""pass-2026-11-26 supplementary language sweep (title.search, language filter) for languages whose main-harvest query was a prior repeat or returned few hits (it, ru, tr, nl, cs, zh, es, de, fr, ja, pl, vi, sv, hu, ro)."""
import json,urllib.request,urllib.parse,time
S_='s';T='t'
Q=[("lang-it",T,"calcestruzzo riciclato",None,"it"),("lang-it",T,"pavimentazioni in calcestruzzo",None,"it"),("lang-ru",T,"дорожный бетон",None,"ru"),("lang-ru",T,"бетон долговечность",None,"ru"),("lang-tr",T,"beton dayanım",None,"tr"),("lang-nl",T,"betonverharding",None,"nl"),("lang-cs",T,"recyklovaný beton",None,"cs"),("lang-zh",T,"透水混凝土",None,"zh"),("lang-zh",T,"混凝土路面",None,"zh"),("lang-es",T,"hormigón permeable",None,"es"),("lang-de",T,"Betonstraße",None,"de"),("lang-fr",T,"chaussée en béton",None,"fr"),("lang-ja",T,"再生骨材コンクリート",None,"ja"),("lang-pl",T,"beton z kruszywem z recyklingu",None,"pl"),("lang-vi",T,"bê tông cốt liệu tái chế",None,"vi"),("lang-sv",T,"betong",None,"sv"),("lang-hu",T,"beton",None,"hu"),("lang-ro",T,"beton",None,"ro")
]
PR={tuple(x) for x in json.load(open('prior-queries-all.json'))}
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def get(u):
  for i in range(5):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    except Exception as e: err=e; time.sleep(4*(i+1))
  raise err
SEL='id,doi,title,publication_year,publication_date,type,language,cited_by_count,authorships,primary_location,abstract_inverted_index,is_retracted,open_access,biblio'
out={};log=[];sk=[]
for t,mode,q,per,lang in Q:
  if (t,q,per,lang) in PR or (t,'title.search:'+q,per,lang) in PR: sk.append([t,q,per,lang]); continue
  f='title.search:%s,type:article|book-chapter|report|dissertation|book|review|standard,language:%s'%(q,lang)
  p={'filter':f,'per-page':25,'sort':'cited_by_count:desc','select':SEL,'mailto':'research@example.org'}
  ent=dict(topic=t,mode='title.search',query=q,period=per,language=lang,n=0,errors=[])
  try:
    d=get('https://api.openalex.org/works?'+urllib.parse.urlencode(p))
    for w in d['results']:
      k=(w.get('doi') or w['id']).lower()
      if k in out: out[k]['queries'].append([t,q]); continue
      w['queries']=[[t,q]]; out[k]=w; ent['n']+=1
  except Exception as e: ent['errors'].append(str(e))
  log.append(ent); print(q,per,ent['n'],ent['errors'],flush=True)
json.dump(dict(log=log,skippedRepeats=sk),open('search-log-b.json','w'),indent=1); json.dump(out,open('api-hits-b.json','w')); print(len(out))
