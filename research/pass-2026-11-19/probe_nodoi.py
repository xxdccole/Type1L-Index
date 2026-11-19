"""Probe landing pages of no-DOI shortlisted hits; keep those where HTTP 200 and the title's words are present in the page text. Pages saved in landing/."""
import json,re,subprocess,html,hashlib,concurrent.futures as cf
keys=json.load(open('listing-keys.json')); h={'h1':json.load(open('new-hits.json')),'h2':json.load(open('new-hits2.json'))}
NOD=[0, 97, 101, 104, 109, 114, 117, 123, 133, 137, 138, 153, 154, 157, 166, 167, 175, 178, 200, 202, 203, 282, 286, 295, 325, 326, 331, 335, 393, 394, 395, 397, 398, 399, 402, 403, 404, 405, 408, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 428, 430, 432, 433, 435, 437, 439, 441, 442, 443, 447, 450, 452, 457, 458, 459, 460, 461, 462, 463, 464, 466, 467, 468, 469, 470, 472, 484, 485, 488, 491, 492, 493, 495, 501, 504, 511, 512, 513, 515, 516, 521, 526, 527, 528, 529]
SKIP=('trid.trb.org','cnki.net','cqvip.com','ebscohost','researchgate','data.bnf.fr')
def nt(s): return re.sub(r'[^a-z0-9]+',' ',html.unescape(s or '').lower()).strip()
def one(i):
  s,k=keys[i]; w=h[s][k]; u=(w.get('primary_location') or {}).get('landing_page_url') or ''
  u=html.unescape(u)
  if u.startswith('http://'): u='https://'+u[7:]  # box egress returns HTTP 500 for plain-http URLs (2026-11-19); https used instead
  r=dict(idx=i,url=u,title=w['title'])
  if not u or any(x in u for x in SKIP): r['status']='skipped-host'; return r
  f='landing/nodoi-%d.html'%i
  p=subprocess.run(['curl','-sL','-m','35','-A','Mozilla/5.0','-o',f,'-w','%{http_code} %{url_effective}',u],capture_output=True,text=True)
  r['http']=p.stdout
  try: t=nt(re.sub(r'<script.*?</script>|<style.*?</style>','',open(f,errors='ignore').read(),flags=re.S)); t=nt(re.sub(r'<[^>]+>',' ',t)) if False else t
  except Exception: t=''
  words=[x for x in nt(w['title']).split() if len(x)>3][:8]
  r['match']=sum(x in t for x in words)/max(1,len(words)); r['size']=len(t)
  r['status']='ok' if p.stdout.startswith('200') and r['match']>=0.75 else 'fail'
  return r
with cf.ThreadPoolExecutor(6) as ex: R=list(ex.map(one,NOD))
json.dump(R,open('probe-nodoi.json','w'),indent=1)
import collections
print(collections.Counter(r['status'] for r in R))
for r in R: print(r['idx'],r['status'],r.get('http','')[:60],round(r.get('match',0),2))
