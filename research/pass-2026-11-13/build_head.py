"""pass-2026-11-13 build: verified records (R1893+; R1892 = resolved old lead) + lead decisions -> plan.json. apply.py writes working files.
Derived from research/pass-2026-11-12/build.py (same verification/metadata rules)."""
import json,re,sys,html,collections
B='/workspace/type1l-index/'
VD='2026-11-13'; PASS='pass-2026-11-13'
def clean(t): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',html.unescape(t or ''))).strip()
S=json.load(open(B+'site-data.json'))
TOPICS={t['id'] for t in S['topics']}
src=open('../pass-2026-11-10-leadverify/lv_build.py').read()
blk=src[src.index('CC={'):src.index('# ---------- existing index keys')]
blk=blk.replace("X['countries'].get(d) or []","[]")
exec(blk)
PUB.update({'Beuth Verlag GmbH':'Beuth Verlag (DIN)','Birkhäuser Basel':'Birkhäuser','Springer Berlin Heidelberg':'Springer','FapUNIFESP (SciELO)':'SciELO','Editorial CSIC':'Editorial CSIC','Pontificia Universidad Catolica de Chile':'Pontificia Universidad Católica de Chile','CRC Press':'CRC Press','Thomas Telford Publishing':'ICE Publishing (Thomas Telford)'})
sel=json.load(open('selected.json')); V=json.load(open('doi-verify.json'))
def fixab(a):
    a=clean(a)
    if 'First Name is required' in a or 'Last Name is required' in a or a.lower() in ('not available','resumen','abstract'): return ''
    a=re.sub(r'^(High Resolution Image\s*)?(Download MS PowerPoint Slide\s*)?','',a)
    a=re.sub(r'^(Summary|Abstract|Synopsis|Resumen|RESUMO|Resumo)(?=[A-Z\s])\s*','',a)
    return a
def oa_abs(w):
    ii=w.get('abstract_inverted_index')
    if not ii: return ''
    return ' '.join(x for _,x in sorted((p,x) for x,ps in ii.items() for p in ps))
def oa_geo(w):
    cs=[]
    for a in w.get('authorships',[]):
        for c in (a.get('countries') or [i.get('country_code') for i in a.get('institutions',[])]):
            if c and c not in cs: cs.append(c)
    return ' / '.join(CC.get(c,c) for c in cs[:4]) or None
PLC=['scm-limestone','binder-blended']
