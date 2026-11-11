"""Verify each selected lead: Crossref works API per DOI (+DataCite fallback), doi.org registration (HEAD, no redirect); no-DOI items: landing page probe."""
import json,urllib.request,urllib.parse,time,concurrent.futures as cf,subprocess
sel=json.load(open('selected.json'))
UA={'User-Agent':'CementIndexResearch/1.0 (mailto:research@example.org)'}
def get(u):
  for i in range(4):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40))
    except urllib.error.HTTPError as e:
      if e.code==404: return {'_404':True}
      err=e; time.sleep(2*(i+1))
    except Exception as e: err=e; time.sleep(2*(i+1))
  return {'_err':str(err)}
def head(u):
  r=subprocess.run(['curl','-s','-o','/dev/null','-m','25','-w','%{http_code} %{redirect_url}','-I',u],capture_output=True,text=True)
  return r.stdout
def one(k):
  w=sel[k]; out={'key':k}
  doi=(w.get('doi') or '').replace('https://doi.org/','')
  if doi:
    m=get('https://api.crossref.org/works/'+urllib.parse.quote(doi)+'?mailto=research@example.org')
    if 'message' in m:
      x=m['message']
      out['crossref']={'title':(x.get('title') or [None])[0],'subtitle':x.get('subtitle'),'authors':[(a.get('given','')+' '+a.get('family','')).strip() or a.get('name') for a in x.get('author',[])],'issued':(x.get('issued',{}).get('date-parts') or [[None]])[0],'container':(x.get('container-title') or [None])[0],'publisher':x.get('publisher'),'type':x.get('type'),'abstract':x.get('abstract'),'volume':x.get('volume'),'issue':x.get('issue'),'page':x.get('page'),'isbn':x.get('ISBN'),'url':x.get('URL'),'language':x.get('language'),'relation':x.get('relation'),'update-to':x.get('update-to'),'standards-body':x.get('standards-body')}
    else:
      d=get('https://api.datacite.org/dois/'+urllib.parse.quote(doi))
      if 'data' in d:
        a=d['data']['attributes']; out['datacite']={'title':a['titles'][0]['title'] if a.get('titles') else None,'authors':[c.get('name') for c in a.get('creators',[])],'year':a.get('publicationYear'),'publisher':a.get('publisher'),'type':(a.get('types') or {}).get('resourceTypeGeneral')}
      else: out['regErr']=m
    out['doiHead']=head('https://doi.org/'+doi)
  else:
    lp=(w.get('primary_location') or {}).get('landing_page_url')
    out['landing']=lp; out['landingHead']=head(lp) if lp else None
  return out
res={}
with cf.ThreadPoolExecutor(4) as ex:
  for r in ex.map(one,list(sel)): res[r['key']]=r; print(r['key'], 'CR' if 'crossref' in r else ('DC' if 'datacite' in r else r.get('landingHead') or r.get('regErr')),flush=True)
json.dump(res,open('doi-verify.json','w'),indent=1)
