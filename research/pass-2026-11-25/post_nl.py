"""pass-2026-11-25: replace the Amazon retail-page hit for "Euro-Cements" (newlead-a direct route) with the Open Library work record (search API read 2026-11-25), a library-catalogue source."""
import json
R=json.load(open('newlead-b.json')); d=[x for x in json.load(open('ev/eurocements-ol-search.json'))['docs'] if x['key']=='/works/OL34035644W'][0]
for r in R:
    if r['title'].startswith('Euro-Cements'):
        r['urlsTried'].append('https://openlibrary.org/search.json?title=Euro-Cements')
        r['log'].append('Amazon retail page not used as evidence; Open Library work OL34035644W read instead')
        r['result']=dict(route='openlibrary',url='https://openlibrary.org'+d['key'],match=1.0,meta=dict(title=d.get('title'),author_name=d.get('author_name'),first_publish_year=d.get('first_publish_year'),publisher=(d.get('publisher') or [])[:5],isbn=(d.get('isbn') or [])[:3],edition_count=d.get('edition_count'),oclc=(d.get('oclc') or [])[:3]))
        print('patched',r['result'])
json.dump(R,open('newlead-b.json','w'),ensure_ascii=False,indent=1)
