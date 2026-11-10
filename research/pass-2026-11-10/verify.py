import json,urllib.request,urllib.parse,time
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
res={}
for line in open(__import__('sys').argv[1]):
  t,d=line.split(None,1);d=d.strip()
  r={'topic':t,'doi':d}
  for attempt in range(3):
    try:
      x=json.load(urllib.request.urlopen(urllib.request.Request('https://api.crossref.org/works/'+urllib.parse.quote(d,safe='/'),headers=UA),timeout=30))['message']
      r['crossref']={'title':x.get('title'),'authors':[(a.get('given','')+' '+a.get('family','')).strip() or a.get('name') for a in x.get('author',[])],'publisher':x.get('publisher'),'container':x.get('container-title'),'issued':x.get('issued',{}).get('date-parts'),'type':x.get('type'),'volume':x.get('volume'),'page':x.get('page'),'license':[l.get('URL') for l in x.get('license',[])],'abstract':(x.get('abstract') or '')[:600],'refs':x.get('references-count'),'citedby':x.get('is-referenced-by-count')}
      break
    except Exception as e:
      r['crossrefErr']=str(e); time.sleep(4)
  if 'crossref' not in r:
    try:
      x=json.load(urllib.request.urlopen(urllib.request.Request('https://api.openalex.org/works/doi:'+d+'?mailto=research@example.org',headers=UA),timeout=30))
      r['openalex']={'title':x['title'],'authors':[a['author']['display_name'] for a in x['authorships']],'date':x.get('publication_date'),'venue':((x.get('primary_location') or {}).get('source') or {}).get('display_name'),'oa':x['open_access'],'type':x['type'],'license':(x.get('primary_location') or {}).get('license')}
    except Exception as e: r['openalexErr']=str(e)
  try:
    q=urllib.request.Request('https://doi.org/'+d,headers={'User-Agent':'Mozilla/5.0'},method='GET')
    h=urllib.request.urlopen(q,timeout=30); r['resolved']=h.geturl(); r['http']=h.status
  except Exception as e: r['resolveErr']=str(e)[:120]
  res[d]=r; print(t,d,('crossref' in r) or ('openalex' in r),r.get('http'),r.get('resolved','')[:70],r.get('resolveErr',''),flush=True)
  time.sleep(1.5)
json.dump(res,open(__import__('sys').argv[2],'w'),indent=1)
