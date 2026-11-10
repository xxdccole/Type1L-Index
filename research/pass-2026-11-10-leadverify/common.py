import json,re,html
B='/workspace/type1l-index/'
def norm(t): return re.sub(r'[^a-z0-9]','',html.unescape(t or '').lower())[:60]
def clean(t): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',html.unescape(t or ''))).strip()
M=json.load(open(B+'research/pass-2026-11-10-leadverify/lead-meta.json'))
ND=json.load(open(B+'research/pass-2026-11-10-leadverify/nodoi-meta.json'))
CAN=[json.loads(l) for l in open(B+'research/portable/candidates.jsonl')]
S=json.load(open(B+'site-data.json'))
VER=[json.loads(l) for l in open(B+'research/portable/verified-sources.jsonl')]
def vt(d):
    r=M.get(d,{}); c=r.get('crossref') or {}; o=r.get('openalex') or {}; dc=r.get('datacite') or {}
    t=(c.get('title') or [None])[0] or o.get('title') or (dc.get('title') or [None])[0]
    st=(c.get('subtitle') or [None])
    st=st[0] if st else None
    t=clean(t)
    if st and clean(st) and clean(st).lower() not in t.lower(): t=t.rstrip(':')+': '+clean(st)
    return t
def abstract(d):
    r=M.get(d,{}); return clean((r.get('crossref') or {}).get('abstract') or (r.get('openalex') or {}).get('abstract') or (r.get('datacite') or {}).get('abstract') or '')
def venue(d):
    r=M.get(d,{}); c=r.get('crossref') or {}
    return clean((c.get('container') or [None])[0] if c.get('container') else ((r.get('openalex') or {}).get('venue') or ''))
STRONG=re.compile(r'cement|concrete|mortar|clinker|pozzolan|geopolymer|alkali[- ]activat|\bslag|fly ash|metakaolin|calcined clay|silica fume|grout|shotcrete|gunite|c-s-h|calcium silicate hydrate|ettringite|uhpc|\becc\b|engineered cementitious|binder|portland|hydraulic lime|lime mortar|aggregate|rebar|reinforced|prestress|precast|pavement|masonry|well cementing|zonal isolation|cementing|kiln|carbonat|thaumasite|hydration|admixture|superplasticiz|aerated|foam concrete|rcc|roller[- ]compacted|pervious|fibre|fiber',re.I)
