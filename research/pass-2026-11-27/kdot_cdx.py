"""pass-2026-11-26: KDOT PQL / special-provision documents (ksdot.gov answers 403 to the box). Wayback CDX query per document number
(any version suffix, filter on the document path), sequential with back-off; newest 200 captures fetched raw and read with pdftotext.
Accepted only if the PDF text carries the document's own identifier (special-provision number or 'PQL <n>' / list title)."""
import json,re,subprocess,time,urllib.parse,os
L=[json.loads(l) for l in open('../review-retry.jsonl')]
K=[e for e in L if 'ksdot.gov' in (e.get('url') or '')]
def cdx(d):
    u='https://web.archive.org/cdx/search/cdx?url=www.ksdot.gov/home/showpublisheddocument/%s/&matchType=prefix&output=json&filter=statuscode:200&filter=original:.*/showpublisheddocument/%s/.*'%(d,d)
    for i in range(4):
        p=subprocess.run(['curl','-s','-m','90',u],capture_output=True,text=True)
        try: return u,json.loads(p.stdout)[1:]
        except Exception: time.sleep(20*(i+1))
    return u,None
out=[]
for e in K:
    d=re.search(r'showpublisheddocument/(\d+)/',e['url']).group(1)
    u,rows=cdx(d); log=['wayback cdx document %s (any version): %s captures'%(d,'no response' if rows is None else len(rows))]; tried=[u]; res=None
    t=e['title']; m=re.search(r'Special Provision\s+([\d-]+(?:-R\d+)?)',t); key=None
    if m: key=re.escape(m.group(1).split('-R')[0])
    else:
        mp=re.search(r'PQL\s*([\d.]+)',t); key=None
    for row in sorted(rows or [],key=lambda r:r[1],reverse=True)[:3]:
        ts,orig=row[1],row[2]; raw='https://web.archive.org/web/%sid_/%s'%(ts,orig); f='ev/kdot-%s-%s.pdf'%(d,ts)
        p=subprocess.run(['curl','-s','-m','120','-o',f,'-w','%{http_code}',raw],capture_output=True,text=True); tried.append(raw)
        txt=subprocess.run(['pdftotext','-l','3',f,'-'],capture_output=True,text=True).stdout if os.path.exists(f) else ''
        if m: okk=bool(re.search(key,txt))
        else:
            words=[w for w in re.findall(r'[A-Za-z]{4,}',t.split('–',1)[-1])]
            okk=bool(re.search(r'PQL|[Pp]requalified|PREQUALIFIED',txt)) and sum(w.lower() in txt.lower() for w in words)>=max(1,len(words)-1)
        log.append('wayback raw %s -> %s, pdf text %d chars, identifier %s'%(raw,p.stdout,len(txt),'found' if okk else 'not found'))
        if p.stdout=='200' and okk:
            res=dict(route='wayback-kdot',url='https://web.archive.org/web/%s/%s'%(ts,orig),original=orig,snapshot=ts,evidenceFile=f,pdfText=txt[:4000]); break
        elif os.path.exists(f): os.remove(f)
        time.sleep(5)
    out.append(dict(title=t,result=res,log=log,urlsTried=tried)); print('OK' if res else '--',t[:70],log,flush=True)
    json.dump(out,open('kdot-cdx.json','w'),ensure_ascii=False,indent=1); time.sleep(8)
