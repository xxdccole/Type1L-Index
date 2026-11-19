import json,html,re
B='/workspace/type1l-index/research/'
def work(p,i):
    keys=json.load(open(B+p+'/listing-keys.json'))
    h={'h1':json.load(open(B+p+'/new-hits.json')),'h2':json.load(open(B+p+'/new-hits2.json'))}
    s,k=keys[i]; w=h[s][k]
    lines=open(B+p+'/listing.txt').read().splitlines()
    ln=[l for l in lines if l.split('|')[0]==str(i)]
    topic=ln[0].split('|')[1] if ln else None
    return w,topic,k
def meta(w):
    pl=w.get('primary_location') or {}
    src=(pl.get('source') or {})
    return dict(title=html.unescape(w.get('title') or w.get('display_name') or ''),year=w.get('publication_year'),
      authors=[a['author']['display_name'] for a in (w.get('authorships') or [])][:12],
      venue=src.get('display_name'),type=w.get('type'),language=w.get('language'),
      openalexId=w.get('id'),doi=w.get('doi'),url=html.unescape(pl.get('landing_page_url') or ''),
      pdf=pl.get('pdf_url'),cited_by=w.get('cited_by_count'),
      alt=[html.unescape(l.get('landing_page_url') or '') for l in (w.get('locations') or []) if l.get('landing_page_url')])
out=[]
# Nov 13 dropped
import importlib
D13=[46, 55, 56, 58, 61, 68, 69, 74, 85, 118, 132, 139, 166, 171, 187, 192, 197, 198, 199, 204, 208, 215, 222, 223, 226, 228, 239, 243, 256, 257, 261, 268, 269, 271, 273, 274, 275, 276, 277, 283, 286, 287, 290, 292, 740, 742, 804, 840, 845]
for i in D13:
    w,t,k=work('pass-2026-11-13',i); m=meta(w); m.update(topic=t,firstSeen='2026-11-13',pass_='pass-2026-11-13',idx=i,origin='dropped-nodoi',probe='not inspectable on 2026-11-13 (TRID 503, CiNii 202/500, JS-only DSpace/Primo, ROSA P 403)')
    out.append(m)
for r in json.load(open(B+'pass-2026-11-18/probe-nodoi.json')):
    if r['status']=='ok': continue
    w,t,k=work('pass-2026-11-18',r['idx']); m=meta(w); m.update(topic=t,firstSeen='2026-11-18',pass_='pass-2026-11-18',idx=r['idx'],origin='dropped-nodoi',probe=r['status']+' '+(r.get('http') or '')+(' match=%s'%r.get('match') if 'match' in r else ''))
    out.append(m)
json.dump(out,open('dropped.json','w'),ensure_ascii=False,indent=1)
print(len(out))
for m in out: print(m['firstSeen'],m['topic'],m['year'],'|',m['title'][:80],'|',m['venue'],'|',m['type'],'|',m['url'][:70])
