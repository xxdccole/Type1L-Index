"""Probe landing pages of no-DOI shortlisted hits; keep those where HTTP 200 and the title's words are present in the page text. Pages saved in landing/."""
import json,re,subprocess,html,hashlib,concurrent.futures as cf
keys=json.load(open('listing-keys.json')); h={'h1':json.load(open('new-hits.json')),'h2':json.load(open('new-hits2.json'))}
NOD=[96,100,102,103,111,112,116,118,123,155,160,167,170,174,178,179,186,191,193,196,197,198,202,219,281,347,357,395,471,472,473,478,480,482,483,484,488,489,491,492,493,494,495,496,497,498,499,502,512,513,514,515,517,518,520,521,522,528,530,532,534,535,536,537,542,545,546,547,548,549,550,551,560,561,562,564,565,566,577,578,589,594,603,614]
SKIP=('trid.trb.org','ci.nii.ac.jp','cnki.net','cqvip.com','ebscohost','researchgate','data.bnf.fr')
def nt(s): return re.sub(r'[^a-z0-9]+',' ',html.unescape(s or '').lower()).strip()
def one(i):
  s,k=keys[i]; w=h[s][k]; u=(w.get('primary_location') or {}).get('landing_page_url') or ''
  u=html.unescape(u)
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
