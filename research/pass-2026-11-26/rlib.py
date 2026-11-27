import json,re,html,unicodedata,subprocess,time,urllib.parse,concurrent.futures as cf,difflib,os,sys
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
def nu(s):
    s=unicodedata.normalize('NFKC',html.unescape(s or '')).lower()
    s=unicodedata.normalize('NFKD',s); s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[\W_]+',' ',s).strip()
def curl(u,f=None,t=35):
    a=['curl','-sL','-m',str(t),'-A',UA,'-w','%{http_code} %{url_effective}','--compressed']
    a+=['-o',f or '/dev/null',u]
    p=subprocess.run(a,capture_output=True,text=True); return p.stdout
def getj(u,t=30):
    p=subprocess.run(['curl','-sL','-m',str(t),'-A','GrokBot-research/1.0',u],capture_output=True,text=True)
    try: return json.loads(p.stdout)
    except Exception: return None
def text_of(f):
    try: t=open(f,errors='ignore').read()
    except Exception: return '',{}
    meta={}
    for m in re.finditer(r'<meta\s+[^>]*?(?:name|property)\s*=\s*"([^"]+)"[^>]*?content\s*=\s*"([^"]*)"',t,re.I):
        k=m.group(1); v=html.unescape(m.group(2)).strip()
        if v and re.match(r'(citation_|dc\.|dcterms\.|og:title|description|publication_date|document_type)',k,re.I):
            meta.setdefault(k,[]).append(v)
    ti=re.findall(r'<title[^>]*>(.*?)</title>',t,re.S|re.I)
    if ti: meta['html_title']=[html.unescape(re.sub(r'\s+',' ',ti[0])).strip()]
    b=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S|re.I)
    b=html.unescape(re.sub(r'<[^>]+>',' ',b))
    return nu(b),meta
def match(title,txt):
    w=[x for x in nu(title).split() if len(x)>3 or (len(x)>=1 and not x.isascii())][:8]
    if not w: w=nu(title).split()[:8]
    if not w: return 0
    return sum(x in txt for x in w)/len(w)
def https(u): return re.sub(r'^http://','https://',u)
def sim(a,b): return difflib.SequenceMatcher(None,nu(a),nu(b)).ratio()
def snippet(txt,title,n=600):
    w=[x for x in nu(title).split() if len(x)>3][:1]
    i=txt.find(w[0]) if w else 0
    return txt[max(0,i):i+n]
SKIPDIRECT=('ebscohost',)
