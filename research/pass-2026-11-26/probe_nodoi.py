"""pass-2026-11-26 (from 2026-11-25; listing-b rows are idx 400+j): probe landing pages of no-DOI shortlisted hits; ok when HTTP 200 and the title's words are present. Pages saved in landing/. https used for http URLs."""
import json,re,subprocess,html,concurrent.futures as cf
keys=json.load(open('listing-keys.json')); kb=json.load(open('listing-b-keys.json')); h=json.load(open('all-hits.json')); NOD=json.load(open('nodoi-idx.json'))
K=lambda i: keys[i] if i<400 else kb[i-400]
SKIP=('trid.trb.org','cnki.net','cqvip.com','ebscohost','researchgate','data.bnf.fr')
def nt(s): return re.sub(r'[^\w]+',' ',html.unescape(s or '').lower()).strip()
def one(i):
  w=h[K(i)]; u=html.unescape((w.get('primary_location') or {}).get('landing_page_url') or '')
  if u.startswith('http://'): u='https://'+u[7:]
  r=dict(idx=i,url=u,title=w['title'])
  if not u or any(x in u for x in SKIP): r['status']='skipped-host'; return r
  f='landing/nodoi-%d.html'%i
  p=subprocess.run(['curl','-sL','-m','35','-A','Mozilla/5.0','-o',f,'-w','%{http_code} %{url_effective}',u],capture_output=True,text=True)
  r['http']=p.stdout
  try: t=nt(re.sub(r'<[^>]+>',' ',re.sub(r'<script.*?</script>|<style.*?</style>','',open(f,errors='ignore').read(),flags=re.S)))
  except Exception: t=''
  words=[x for x in nt(w['title']).split() if len(x)>3 or not x.isascii()][:8]
  r['match']=sum(x in t for x in words)/max(1,len(words)); r['size']=len(t)
  r['status']='ok' if p.stdout.startswith('200') and r['match']>=0.75 and len(t)>300 else 'fail'
  return r
with cf.ThreadPoolExecutor(6) as ex: R=list(ex.map(one,NOD))
json.dump(R,open('probe-nodoi.json','w'),indent=1,ensure_ascii=False)
import collections
print(collections.Counter(r['status'] for r in R))
for r in R: print(r['idx'],r['status'],r.get('http','')[:90],round(r.get('match',0),2),r['title'][:60])
