import json,urllib.parse,re,os,concurrent.futures as cf
from rlib import *
R=json.load(open('oq-fetch.json'))
B=[r for r in R if r['http'][:3] in ('403','000')]
def one(r):
    u=r['url']; out=dict(i=r['i'],title=r['title'],url=u)
    av=getj('https://archive.org/wayback/available?url='+urllib.parse.quote(re.sub(r'^https?://','',u),safe=''),t=40)
    s=((av or {}).get('archived_snapshots') or {}).get('closest'); out['wb']=s
    if s:
        ts=s['timestamp']; raw=https(s['url']).replace('/web/'+ts+'/','/web/'+ts+'id_/'); f='oq/%d.wb'%r['i']
        hc=curl(raw,f,t=60); out['raw']=raw; out['http']=hc[:3]
        if open(f,'rb').read(5)==b'%PDF-':
            subprocess.run(['pdftotext','-l','3',f,f+'.txt'],capture_output=True); txt=open(f+'.txt',errors='ignore').read(); out['kind']='PDF'; out['head']=re.sub(r'\s+',' ',txt[:500]); out['match']=match(r['title'],nu(txt)); out['info']=subprocess.run(['pdfinfo',f],capture_output=True,text=True).stdout[:500]
        else:
            t,meta=text_of(f); out['kind']='html'; out['match']=match(r['title'],t); out['head']=t[:400]; out['meta']=meta
    return out
import subprocess
with cf.ThreadPoolExecutor(6) as ex: O=list(ex.map(one,B))
json.dump(O,open('oq-wb.json','w'),indent=1)
for o in O: print(o['i'],bool(o['wb']),o.get('http'),o.get('kind'),round(o.get('match',0),2))
