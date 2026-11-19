import json,re,html,unicodedata,collections
B='/workspace/type1l-index/'
def nt(s):
    s=unicodedata.normalize('NFKD',html.unescape(s or '')).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
rows=[json.loads(l) for l in open(B+'research/portable/candidates.jsonl')]
S=json.load(open(B+'site-data.json'))
idx_title=collections.defaultdict(list)
for r in S['resources']: idx_title[nt(r['title'])].append(r['id'])
# also strip subtitles
def tkeys(t):
    n=nt(t); ks={n}
    if ':' in (t or ''): ks.add(nt(t.split(':')[0]))
    return ks
def in_index(t):
    for k in tkeys(t):
        if len(k)>12 and k in idx_title: return idx_title[k]
    return None
pool=collections.OrderedDict()
def add(key,entry):
    if key in pool:
        p=pool[key]; p['sources'].append(entry['sources'][0]); p['seen'].append(entry['firstSeen'])
        p['urlsTried']+= [u for u in entry['urlsTried'] if u not in p['urlsTried']]
        for f in ('authors','venue','year','openalexId','type','language'):
            if not p.get(f) and entry.get(f): p[f]=entry[f]
    else:
        entry['seen']=[entry['firstSeen']]; pool[key]=entry
d=json.load(open('dropped.json'))
for m in d:
    k=m.get('openalexId') or nt(m['title'])
    k=nt(m['title'])
    add(k,dict(title=m['title'],year=m['year'],authors=m['authors'],venue=m['venue'],type=m['type'],language=m['language'],openalexId=m['openalexId'],doi=m['doi'],url=m['url'],alt=m['alt'],topic=m['topic'],firstSeen=m['firstSeen'],urlsTried=[m['url']] if m['url'] else [],sources=[dict(kind='dropped-nodoi',pass_=m['pass_'],listingIdx=m['idx'],probe=m['probe'])]))
for i,r in enumerate(rows):
    if r['status']!='rejected' or r['rejectCategory'] not in ('unverifiable',): continue
    k=nt(r['title'])
    e=dict(title=r['title'],year=r.get('year'),authors=r.get('authors'),venue=r.get('venue'),type=None,language=None,openalexId=r.get('openalexId'),doi=r.get('doi'),url=r.get('url'),alt=[],topic=r['topic'],firstSeen=r.get('addedOn') or r.get('reviewedOn'),urlsTried=[r['url']] if r.get('url') else [],sources=[dict(kind='candidate',candIdx=i,pass_=r.get('reviewPass'),rejectReason=r['rejectReason'])])
    if k in pool:
        p=pool[k]; p['candIdx']=p.get('candIdx',[])+[i]; add(k,e)
        p['doi']=p.get('doi') or e['doi']
    else:
        e['candIdx']=[i]; add(k,e)
for k,p in pool.items():
    p['inIndex']=in_index(p['title'])
    p['seen']=sorted(set(p['seen'])); p['firstSeen']=p['seen'][0]
    p['priorAttempts']=len({s['pass_'] for s in p['sources']})
json.dump(list(pool.values()),open('pool.json','w'),ensure_ascii=False,indent=1)
print(len(pool), 'with cand',sum(1 for p in pool.values() if p.get('candIdx')), 'multi-cand',sum(1 for p in pool.values() if len(p.get('candIdx',[]))>1))
for p in pool.values():
    if p['inIndex']: print('INDEX',p['inIndex'],p['title'][:80],p.get('candIdx'))
