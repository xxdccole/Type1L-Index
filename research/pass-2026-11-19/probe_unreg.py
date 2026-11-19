"""Probe landing pages of selected hits whose DOI is not registered at doi.org/Crossref/DataCite; keep where HTTP 200 and the title's words are on the page (recorded with listedDoi)."""
import json,re,subprocess,html
sel=json.load(open('selected.json')); V=json.load(open('doi-verify.json'))
def nt(s): return re.sub(r'[^\w]+',' ',html.unescape(s or '').lower()).strip()
R=[]
for k,v in V.items():
  if 'crossref' in v or 'datacite' in v: continue
  w=sel[k]; i=w['_idx']; u=html.unescape((w.get('primary_location') or {}).get('landing_page_url') or '')
  if u.startswith('http://'): u='https://'+u[7:]
  f='landing/unreg-%d.html'%i
  p=subprocess.run(['curl','-sL','-m','35','-A','Mozilla/5.0','-o',f,'-w','%{http_code} %{url_effective}',u],capture_output=True,text=True)
  try: t=nt(re.sub(r'<script.*?</script>|<style.*?</style>','',open(f,errors='ignore').read(),flags=re.S))
  except Exception: t=''
  words=[x for x in nt(w['title']).split() if len(x)>3][:8]; m=sum(x in t for x in words)/max(1,len(words))
  R.append(dict(idx=str(i),key=k,url=p.stdout.split(' ',1)[-1] if p.stdout.startswith('200') else u,title=w['title'],doi=w['doi'],status='ok' if p.stdout.startswith('200') and m>=0.75 else 'fail',http=p.stdout,match=str(m)))
  print(i,R[-1]['status'],p.stdout,m)
json.dump(R,open('probe-unreg.json','w'),indent=1,ensure_ascii=False)
