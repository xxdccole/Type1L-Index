# Extra lookups: Crossref approved dates for standards; parent articles of supporting-information components; OpenAlex author-affiliation countries (batched).
import json,urllib.request,urllib.parse,time,re
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def get(u):
    for a in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40))
        except urllib.error.HTTPError as e:
            if e.code==404: return None
            time.sleep(4*(a+1))
        except Exception: time.sleep(4*(a+1))
M=json.load(open('lead-meta.json')); X={'standards':{},'parents':{},'countries':{}}
for d,r in M.items():
    c=r.get('crossref') or {}
    if c.get('type')=='standard':
        m=(get('https://api.crossref.org/works/'+urllib.parse.quote(d,safe='/')) or {}).get('message',{})
        X['standards'][d]={'approved':(m.get('approved') or {}).get('date-parts'),'body':(m.get('standards-body') or {}).get('name'),'resource':(m.get('resource') or {}).get('primary',{}).get('URL'),'authors':[a.get('name') for a in m.get('author',[])]}
        time.sleep(0.4)
    if c.get('type')=='component' and re.search(r'\.s\d{3}$',d):
        p=re.sub(r'\.s\d{3}$','',d)
        if p in X['parents']: continue
        m=(get('https://api.crossref.org/works/'+urllib.parse.quote(p,safe='/')) or {}).get('message')
        if m: X['parents'][p]={'title':m.get('title'),'authors':[(a.get('given','')+' '+a.get('family','')).strip() for a in m.get('author',[])],'publisher':m.get('publisher'),'container':m.get('container-title'),'issued':m.get('issued',{}).get('date-parts'),'type':m.get('type'),'volume':m.get('volume'),'issue':m.get('issue'),'page':m.get('page'),'abstract':(m.get('abstract') or '')[:1500],'license':[l.get('URL') for l in m.get('license',[])]}
        time.sleep(0.4)
dois=list(M)+list(X['parents'])
for i in range(0,len(dois),40):
    ch=[d for d in dois[i:i+40] if '|' not in d and ',' not in d]
    s=get('https://api.openalex.org/works?filter=doi:'+'|'.join(urllib.parse.quote(d,safe='/()') for d in ch)+'&per-page=50&select=doi,authorships,primary_topic&mailto=research@example.org')
    for w in (s or {}).get('results',[]):
        cs=[]
        for a in w.get('authorships',[]):
            for cc in a.get('countries') or []:
                if cc not in cs: cs.append(cc)
        X['countries'][(w.get('doi') or '').replace('https://doi.org/','').lower()]=cs
    time.sleep(0.3)
json.dump(X,open('extra-meta.json','w'),indent=1,ensure_ascii=False)
print(len(X['standards']),len(X['parents']),len(X['countries']))
