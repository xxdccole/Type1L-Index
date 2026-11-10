import json,subprocess
N=json.load(open('nodoi-meta.json'))
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
from concurrent.futures import ThreadPoolExecutor
def pr(u):
    try:
        o=subprocess.run(['curl','-s','-L','-o','/dev/null','-m','30','-A',UA,'-w','%{http_code} %{url_effective}',u],capture_output=True,text=True,timeout=40).stdout
        c,e=o.split(' ',1); return int(c),e
    except Exception as ex: return None,str(ex)[:60]
def job(t):
    r=N[t]; urls=[]
    for u in [r.get('landing')]+(r.get('locations') or [])+[r.get('probeUrl')]:
        if u and u not in urls: urls.append(u)
    res=[]
    for u in urls[:4]:
        c,e=pr(u); res.append([u,c,e])
        if c==200: break
    r['curlProbe']=res; return t,res
with ThreadPoolExecutor(6) as ex:
    for t,res in ex.map(job,list(N)): print(res[-1][1] if res else None,t[:50],res[-1][0][:80] if res else '')
json.dump(N,open('nodoi-meta.json','w'),indent=1,ensure_ascii=False)
