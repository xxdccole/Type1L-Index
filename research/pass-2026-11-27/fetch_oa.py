"""Fetch OpenAlex work records (type, language, authorships/countries, abstract) for all retry-list leads (pass-2026-11-26: 125), used for type/language/geography when promoting."""
import json,urllib.request,urllib.parse,time
L=[json.loads(l) for l in open('../review-retry.jsonl')]
ids=[x['openalexId'].split('/')[-1] for x in L if x.get('openalexId')]
out={}
for i in range(0,len(ids),50):
    u='https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'openalex:'+'|'.join(ids[i:i+50]),'per-page':50,'select':'id,doi,title,publication_year,publication_date,type,language,authorships,primary_location,abstract_inverted_index,biblio','mailto':'research@example.org'})
    d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'CementIndexResearch/1.0'}),timeout=60))
    for w in d['results']: out[w['id'].split('/')[-1]]=w
    time.sleep(0.5)
json.dump(out,open('oa-retry.json','w'),ensure_ascii=False); print(len(ids),len(out))
