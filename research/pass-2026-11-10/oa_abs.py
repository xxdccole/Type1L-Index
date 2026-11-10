import json,urllib.request,time
d=json.load(open('doi-verify.json'))
out={}
for k in list(d)+['10.1617/s11527-018-1255-3']:
  try:
    x=json.load(urllib.request.urlopen('https://api.openalex.org/works/doi:'+k+'?mailto=research@example.org',timeout=30))
    inv=x.get('abstract_inverted_index') or {}
    pos=sorted((p,w) for w,ps in inv.items() for p in ps)
    out[k]=dict(abstract=' '.join(w for p,w in pos)[:900],authors=[a['author']['display_name'] for a in x['authorships']],date=x.get('publication_date'),oa=x.get('open_access'),license=(x.get('primary_location') or {}).get('license'),type=x.get('type'),lang=x.get('language'),refs=len(x.get('referenced_works') or []),cited=x.get('cited_by_count'))
  except Exception as e: out[k]={'err':str(e)}
  time.sleep(0.3)
json.dump(out,open('openalex-detail.json','w'),indent=1,ensure_ascii=False)
