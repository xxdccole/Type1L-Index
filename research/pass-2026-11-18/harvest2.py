"""pass-2026-11-18 harvest 2: (a) page-2 of the topical title.search queries of harvest.py (deeper rows 26-50 for the same query, so no shallow repeats);
(b) backward chase from existing DOI records (<2006) in the least-covered topics (refs cited by >=2 seeds or published <1990);
(c) forward chase (cites:) from the most-cited existing DOI records in those topics (top citers <=2012 and 2024-2026)."""
import json,urllib.request,urllib.parse,time,collections,re
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def get(u):
  err=None
  for i in range(5):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    except Exception as e: err=e; time.sleep(5*(i+1))
  raise err
SEL='id,doi,title,publication_year,publication_date,type,language,cited_by_count,authorships,primary_location,abstract_inverted_index,is_retracted,open_access,biblio'
LOG=json.load(open('search-log.json'))
out={};log=[]
def add(w,q):
  k=(w.get('doi') or w['id']).lower()
  if k in out: out[k]['queries'].append(q); return 0
  w['queries']=[q]; out[k]=w; return 1
# (a) page 2
for e in LOG:
  if e['mode']!='title.search' or e['topic'].startswith(('lang-','current')) or e['n']<15: continue
  f='title.search:%s,type:article|book-chapter|report|dissertation|book|review|standard'%e['query']
  if e['period']:
    a,b=e['period'].split(':')
    if a: f+=',from_publication_date:%s-01-01'%a
    if b: f+=',to_publication_date:%s-12-31'%b
  p={'filter':f,'per-page':25,'page':2,'sort':'cited_by_count:desc','select':SEL,'mailto':'research@example.org'}
  try:
    d=get('https://api.openalex.org/works?'+urllib.parse.urlencode(p)); n=sum(add(w,[e['topic'],e['query']+' [p2]']) for w in d['results'])
    log.append(dict(topic=e['topic'],query=e['query']+' [page 2]',period=e['period'],n=n)); print('p2',e['topic'],e['query'],n,flush=True)
  except Exception as ex: print('ERR',e['query'],ex,flush=True)
  time.sleep(0.4)
# (b)/(c) seeds
S=json.load(open('../../site-data.json')); vs={}
for l in open('../portable/verified-sources.jsonl'):
  v=json.loads(l); vs[v['id']]=v
FOCUS={'concrete-mass-rcc','concrete-heavyweight','concrete-cellular','binder-specialty','concrete-shotcrete','binder-white-masonry','binder-well','binder-international','scm-natural','scm-clay','cross-supply-region','cross-failure-repair'}
seeds=[]
for r in S['resources']:
  if not FOCUS & set(r['topics']): continue
  m=re.search(r'10\.\d{4,9}/[^\s?#]+',r.get('url') or '')
  if m: seeds.append((r['id'],m.group(0).lower().rstrip('/.'),(r.get('date') or '')[:4]))
print('seeds',len(seeds),flush=True)
oa={}
for i in range(0,len(seeds),40):
  chunk=seeds[i:i+40]
  f='doi:'+'|'.join('https://doi.org/'+d for _,d,_ in chunk)
  try:
    d=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':f,'per-page':50,'select':'id,doi,publication_year,cited_by_count,referenced_works','mailto':'research@example.org'}))
  except Exception as ex: print('seed err',ex); continue
  for w in d['results']: oa[(w['doi'] or '').replace('https://doi.org/','').lower()]=w
  time.sleep(0.5)
sid={d:rid for rid,d,_ in seeds}
refs=collections.defaultdict(list)
for d,w in oa.items():
  if (w.get('publication_year') or 9999)<2006:
    for r in w.get('referenced_works') or []: refs[r.split('/')[-1]].append(sid.get(d,d))
print('refs',len(refs),flush=True)
ids=list(refs); got={}
for i in range(0,len(ids),50):
  try: d=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'openalex:'+'|'.join(ids[i:i+50]),'per-page':50,'select':SEL,'mailto':'research@example.org'}))
  except Exception as ex: print('ref err',ex); continue
  for w in d['results']: got[w['id'].split('/')[-1]]=w
  time.sleep(0.5)
kb=0
for wid,w in got.items():
  cs=refs[wid]
  if len(set(cs))>=2 or (w.get('publication_year') or 9999)<1990:
    kb+=add(w,['citation-chase','refs of '+','.join(sorted(set(cs))[:6])])
print('backward',kb,flush=True)
top=sorted(oa.values(),key=lambda w:-(w.get('cited_by_count') or 0))[:30]
kf=0
for w in top:
  wid=w['id'].split('/')[-1]; sd=sid.get((w['doi'] or '').replace('https://doi.org/','').lower())
  for lab,extra,srt in (('old','to_publication_date:2012-12-31','cited_by_count:desc'),('new','from_publication_date:2024-01-01','cited_by_count:desc')):
    try:
      d=get('https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'cites:%s,%s,type:article|book-chapter|report|dissertation|book|review'%(wid,extra),'per-page':8 if lab=='old' else 5,'sort':srt,'select':SEL,'mailto':'research@example.org'}))
      kf+=sum(add(x,['citation-chase-fwd','cites '+str(sd)]) for x in d['results'])
    except Exception as ex: print('fwd err',ex)
    time.sleep(0.4)
print('forward',kf,flush=True)
json.dump(log,open('search-log2.json','w'),indent=1); json.dump(out,open('api-hits2.json','w')); print(len(out))
