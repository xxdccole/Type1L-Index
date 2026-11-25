import json,subprocess,re,os,concurrent.futures as cf
from rlib import *
C=[(i,json.loads(l)) for i,l in enumerate(open('../portable/candidates.jsonl'))]
Q=[(i,c) for i,c in C if c['status']=='candidate']
def one(a):
    i,c=a; f='oq/%d.bin'%i
    u=c['url']
    if 'doi.org' in u: u=u
    hc=curl(u,f,t=60)
    kind=('PDF' if os.path.exists(f) and open(f,'rb').read(5)==b'%PDF-' else 'other')
    txt=''; info=''
    if 'PDF' in kind:
        subprocess.run(['pdftotext','-l','3',f,f+'.txt'],capture_output=True)
        txt=open(f+'.txt',errors='ignore').read() if os.path.exists(f+'.txt') else ''
        info=subprocess.run(['pdfinfo',f],capture_output=True,text=True).stdout
        t=nu(txt)
    else:
        t,meta=text_of(f); info=json.dumps(meta)[:800]
    return dict(i=i,title=c['title'],url=u,http=hc[:300],kind=kind,match=match(c['title'],nu(txt) if 'PDF' in kind else t),len=len(t),head=re.sub(r'\s+',' ',txt[:500]) if 'PDF' in kind else t[:400],info=info[:600])
with cf.ThreadPoolExecutor(6) as ex: R=list(ex.map(one,Q))
json.dump(R,open('oq-fetch.json','w'),indent=1)
for r in R: print(r['i'],r['http'][:60].replace('\n',' '),r['kind'][:20],round(r['match'],2),r['len'])
