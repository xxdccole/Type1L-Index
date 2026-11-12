import json,re,collections
h1=json.load(open('new-hits.json')); h2=json.load(open('new-hits2.json'))
gen=re.compile(r'cement|concrete|mortar|clinker|pozzol|geopolym|alkali.activ|shotcrete|grout|binder|masonry|slag|silica fume|fly ash|aggregate|Zement|Beton|ciment|béton|cemento|hormig|cimento|concreto|ettringit|kiln|calcined|metakaolin|magnesi|ash',re.I)
bad=re.compile(r'dental|tooth|teeth|bone cement|endodont|root canal|orthop|arthroplast|vertebro|glass ionomer|pulp|implant|surgical|clinical',re.I)
rows=[]
for src,h in (('h1',h1),('h2',h2)):
  for k,w in h.items():
    ti=w.get('title') or ''
    if not gen.search(ti) or bad.search(ti) or w.get('is_retracted'): continue
    if w.get('type') in ('paratext','erratum','editorial','letter'): continue
    rows.append((w['queries'][0][0]+'::'+w['queries'][0][1] if w['queries'][0][0] not in ('current-2026','citation-chase') else w['queries'][0][0],-(w.get('cited_by_count') or 0),src,k,w))
rows.sort(key=lambda r:(r[0],r[1]))
cap=collections.Counter(); keys=[]
with open('listing.txt','w') as f:
  for t,nc,src,k,w in rows:
    lim=40 if t in('current-2026',) else 7
    if t=='citation-chase': lim=400
    if cap[t]>=lim: continue
    cap[t]+=1
    i=len(keys); keys.append([src,k])
    ab='A' if w.get('abstract_inverted_index') else '-'
    pl=((w.get('primary_location') or {}).get('source') or {}).get('display_name') or ''
    f.write(f"{i}|{t}|{w.get('publication_year')}|{-nc}|{w.get('type')}|{ab}|{(w.get('language') or '')}|{w['title'][:130]}|{pl[:40]}|{'doi' if w.get('doi') else 'nodoi'}\n")
json.dump(keys,open('listing-keys.json','w'))
print(len(rows),len(keys),cap)
