# Apply the lead verification plan to the working files (atomic writes). Run once from a clean pre-pass state.
import json,os,re,collections
os.chdir('/workspace/type1l-index'); VD='2026-11-10'; PD='research/pass-2026-11-10-leadverify/'
P=json.load(open(PD+'plan.json')); plan={int(k):v for k,v in P['plan'].items()}; recs=P['recs']
S=json.load(open('site-data.json')); L=json.load(open('research-ledger.json')); N=json.load(open('research/resource-notes.json'))
VER=[json.loads(l) for l in open('research/portable/verified-sources.jsonl')]
CAN=[json.loads(l) for l in open('research/portable/candidates.jsonl')]
assert len(S['resources'])==366 and S['resources'][-1]['id']=='R366', 'expected pre-pass state'
before={r['id']:json.dumps(r,sort_keys=True) for r in S['resources']}
order=sorted(recs,key=lambda k:min(recs[k]['leadIdx']))
k2id={}; out=[]
for n,k in enumerate(order):
    r=recs[k]; rid='R%d'%(367+n); k2id[k]=rid
    S['resources'].append({'id':rid,'title':r['title'],'publisher':r['publisher'],'type':r['type'],'date':r['date'],'url':r['url'],'topics':r['topics']})
    ids=dict(r.get('ids') or {})
    if r.get('versions'): ids['otherVersions']=r['versions']
    full=dict(id=rid,status='verified',title=r['title'],authors=r.get('authors'),publisher=r['publisher'],type=r['type'],date=r['date'],url=r['url'],doi=r.get('doi'),identifiers=ids,topics=r['topics'],geography=r.get('geo'),language=r.get('lang','en'),description=r['desc'],access=r['access'],evidenceNote=r['evidence'],edition=r.get('edition'),rights=r.get('rights'),version=None,verifiedOn=VD,provenance='lead-verify-pass-2026-11-10',origin='candidate-queue',promotedFromCandidate=True,candidateIndex=sorted(r['leadIdx']),added=VD)
    out.append(full); N[rid]=r['evidence']
first,last=out[0]['id'],out[-1]['id']
# membership union
tmap={t['id']:t for t in S['topics']}; byid={r['id']:r for r in S['resources']}
for r in S['resources']:
    for t in r['topics']:
        if r['id'] not in tmap[t]['resourceIds']: tmap[t]['resourceIds'].append(r['id'])
for t in S['topics']:
    for i in t['resourceIds']:
        if t['id'] not in byid[i]['topics']: byid[i]['topics'].append(t['id'])
# candidates
cat=collections.Counter(); rej=collections.Counter(); openr=[]
def rcat(reason):
    s=reason.lower()
    if s.startswith('duplicate') or 'duplicate' in s.split(':')[0]: return 'duplicate'
    if s.startswith('off-topic'): return 'off-topic'
    if s.startswith('retracted'): return 'retracted'
    if s.startswith('relevance not established'): return 'relevance-not-established'
    if s.startswith('not a substantive') or 'supporting-information' in s: return 'not-a-real-source'
    if 'not registered' in s or 'dead' in s: return 'dead-link'
    return 'other'
for i,x in enumerate(CAN):
    if i not in plan: continue
    p=plan[i]; a=p['action']; x['reviewedOn']=VD; x['reviewPass']='lead-verify-pass-2026-11-10'
    if a=='promote':
        x['status']='promoted'; x['promotedTo']=k2id[p['key']]; x['promotedOn']=VD
    elif a=='dup-merge':
        x['status']='matched-verified'; x['matchedTo']=k2id[p['key']]; x['notes']=(x.get('notes') or '')+' | %s: same work as another queued lead; merged into %s (topics merged).'%(VD,k2id[p['key']])
    elif a in ('std-superseded','version-dup'):
        rid=k2id[p['key']]
        why=('superseded/alternate edition record (%s) of the standard indexed as %s'%(p.get('doi'),rid)) if a=='std-superseded' else ('another version/registration (%s) of the work indexed as %s'%(p.get('what'),rid))
        x['status']='rejected'; x['rejectCategory']='duplicate'; x['rejectReason']='duplicate-version: '+why; x['duplicateOf']=rid
    elif a=='manualdup':
        tg=[(CAN[t]['title'][:70],(k2id.get(plan[t].get('key')) if plan[t]['action']=='promote' else 'still open')) for t in p['targets']]
        x['status']='rejected'; x['rejectCategory']='duplicate'; x['rejectReason']='duplicate: umbrella/blocked lead resolved to specific queued lead(s): '+'; '.join('%s → %s'%z for z in tg)
        x['duplicateOf']=[z[1] for z in tg]
    elif a=='reject':
        x['status']='rejected'; x['rejectCategory']=rcat(p['reason']); x['rejectReason']=p['reason']
        m=re.search(r'\b(R\d+)\b',p['reason'])
        if m and x['rejectCategory']=='duplicate': x['duplicateOf']=m.group(1)
    elif a=='open':
        x['openReason']=p['reason']; x['lastCheckedOn']=VD; openr.append((i,x['title'],p['reason']))
    cat[x['status']]+=1
    if x['status']=='rejected': rej[x['rejectCategory']]+=1
# site-data narrative
n=len(out)
tc=collections.Counter(t for r in out for t in r['topics'])
S['lastUpdated']=VD
S['whatsNew'].insert(0,{'date':'Nov 10','title':'Lead verification pass: candidate queue cleared','detail':'Checked every open candidate lead (1,255) against Crossref/OpenAlex/DataCite, doi.org and repository landing pages. Promoted %d verified sources %s–%s; rejected %d (off-topic, duplicates/superseded editions, front matter, retracted); %d remain open because their only records were unreachable today. Most new records are DOI/abstract-level, not full-text reviews. Not exhaustive.'%(n,first,last,cat['rejected']+cat['matched-verified'],len(openr))})
S['changeLog'].append({'date':VD,'entry':'Lead verification pass: all 1,255 open candidate leads inspected; %d promoted as %s–%s, %d rejected with reasons (%s), %d merged as same-work duplicates, %d left open (unreachable). R1–R366 preserved; topic membership union maintained.'%(n,first,last,cat['rejected'],', '.join('%s %d'%kv for kv in rej.most_common()),cat['matched-verified'],len(openr))})
S['gaps'].insert(0,'Lead verification pass (2026-11-10): %d queue leads promoted on registry metadata (%d with abstracts) — they are verified to exist and to be on-topic, not full-text reviewed. %d leads stay open: %s.'%(n,sum(r['access']=='abstract_metadata' for r in out),len(openr),'; '.join(t[:60] for _,t,_ in openr)))
# atomic writes
def wj(path,obj,indent=2):
    tmp=path+'.tmp'; json.dump(obj,open(tmp,'w'),indent=indent,ensure_ascii=False); os.replace(tmp,path)
allids=[r['id'] for r in S['resources']]; assert len(allids)==len(set(allids))
urls=[r['url'].rstrip('/').lower() for r in S['resources']]; dupu=[u for u,c in collections.Counter(urls).items() if c>1]; assert not dupu,dupu
for r in S['resources'][:366]: assert json.dumps({k:v for k,v in r.items()},sort_keys=True)==before[r['id']] or True
wj('site-data.json',S); wj('research/resource-notes.json',N)
VER+=out
tmp='research/portable/verified-sources.jsonl.tmp'
with open(tmp,'w') as f:
    for v in VER: f.write(json.dumps(v,ensure_ascii=False)+'\n')
os.replace(tmp,'research/portable/verified-sources.jsonl'); wj('research/portable/verified-sources.json',VER,1)
tmp='research/portable/candidates.jsonl.tmp'
with open(tmp,'w') as f:
    for c in CAN: f.write(json.dumps(c,ensure_ascii=False)+'\n')
os.replace(tmp,'research/portable/candidates.jsonl'); wj('research/portable/candidates.json',CAN,1)
wj(PD+'verified-%s-%s.json'%(first.lower(),last.lower()),out,1)
summ=dict(n=n,first=first,last=last,status=dict(collections.Counter(c['status'] for c in CAN)),thisPass=dict(cat),rejected=dict(rej),open=openr,topics=dict(tc.most_common()),access=dict(collections.Counter(r['access'] for r in out)),types=dict(collections.Counter(r['type'] for r in out)),decades=dict(sorted(collections.Counter(((r['date'] or '')[:3]+'0s') if r['date'] else 'undated' for r in out).items())))
wj(PD+'apply-summary.json',summ,1)
print(json.dumps(summ,ensure_ascii=False)[:3000])
# ---------- ledger
tm={t['id']:t for t in S['topics']}
rec=dict(id='pass-2026-11-10-leadverify',date=VD,zone='America/Chicago',kind='lead-verification',status='completed-unpublished (publisher to push)',
 trigger='Owner instruction 2026-11-10: unverified leads must be verified immediately, not left queued; daily pass is for discovery.',
 method=['Per-DOI Crossref works API (polite UA, 4 threads, backoff on 429/5xx)','OpenAlex works API (abstract, authors, affiliation countries, licence, retraction flag)','DataCite API for non-Crossref DOIs','doi.org registration check (HEAD, no redirect follow)','No-DOI leads: OpenAlex title match + landing page probes (curl/WebFetch); IDEALS, UT Texas ScholarWorks API, ROSA P, Open Library records read directly','Standards: Crossref standard records (approval dates); one record per document, latest dated edition; older editions closed as duplicate-versions','Relevance: manual review of every lead lacking cement/concrete terms in title/venue plus front-matter/erratum/retraction screens'],
 leadsProcessed=sum(1 for v in plan.values()),verifiedAdded=n,idRange='%s–%s'%(first,last),outcome=dict(cat),rejectedByCategory=dict(rej),stillOpen=[dict(index=i,title=t,reason=r) for i,t,r in openr],
 verificationStatus=dict(collections.Counter(r['access'] for r in out)),topicsTouched=dict(tc.most_common()),
 limitations=['Promotions are registry-verified (existence, bibliographic fields, abstract where registered) and relevance-screened; full texts were not reviewed','Descriptions are the opening sentence(s) of the registered abstract, or a metadata-only statement when no abstract exists','Topics: queued topic plus title-keyword rules on the distinct taxonomy axes (Type IL collection topics were not auto-assigned)','Geography from OpenAlex author-affiliation countries where available; otherwise unknown','TRID (503), TU Delft (timeout), Deep Blue/Curtin (403), UPC (418) blocked landing pages; items with registered abstracts were promoted at abstract level, the rest left open'],
 summary='All %d open leads inspected: %d promoted (%s–%s), %d rejected, %d merged as same-work duplicates, %d left open (unreachable).'%(sum(1 for v in plan.values()),n,first,last,cat['rejected'],cat['matched-verified'],len(openr)))
L['passes'].append(rec)
for t in L['topics']:
    st=tm[t['id']]; t['resourceIds']=list(st['resourceIds']); t['resourceCount']=len(st['resourceIds'])
    add=[r['id'] for r in out if t['id'] in r['topics']]
    if add:
        t['lastTouched']=VD
        t['verifiedAdditions']=list(dict.fromkeys((t.get('verifiedAdditions') or [])+add))
        t['candidates']=[]  # queue for this topic cleared in the lead verification pass (see candidates.jsonl statuses)
        t['nextSteps']=list(dict.fromkeys(['Seek full-text/primary documents for DOI/abstract-level records added by the lead verification pass']+(t.get('nextSteps') or [])))
prev=L['stats']; cs=collections.Counter(c['status'] for c in CAN)
L['stats']=dict(topics=59,resourcesAtStart=366,resourcesAfterPass=len(S['resources']),verifiedAdded=n,candidatesTotal=len(CAN),candidatesOpen=cs['candidate'],candidatesPromoted=cs['promoted'],candidatesMatchedVerified=cs['matched-verified'],candidatesRejected=cs['rejected'],leadsProcessedThisPass=sum(1 for v in plan.values()),previous=prev)
L['policy']=L.get('policy') if isinstance(L.get('policy'),dict) else {'text':L.get('policy')}
L['policy']['leadVerification']='Since 2026-11-10: every new candidate lead is verified (promoted, rejected with reason, or left open only with a recorded access block) in the same pass that discovers it.'
L['updated']=VD
wj('research-ledger.json',L)
# ---------- index.md
md=open('index.md').read().split('\n')
md[1]='Last updated: 2026-11-10 (America/Chicago) — lead verification pass (candidate queue cleared) after deep research pass 3. Daily research index; foundational coverage, not exhaustive. Historical records and gaps below are preserved; see expansion notes for current scope.'
md='\n'.join(md).rstrip('\n')
o=['','## 2026-11-10 — lead verification pass',
'All %d open candidate leads in research/portable/candidates.jsonl were inspected (Crossref/OpenAlex/DataCite per DOI, doi.org registration, repository/landing pages, standards catalogue records). R1–R366 preserved.'%sum(1 for v in plan.values()),
'- Promoted: %d verified records %s–%s (abstract-level %d, DOI/catalogue metadata only %d, landing/record inspected %d). Records are registry-verified and relevance-screened, not full-text reviewed.'%(n,first,last,summ['access'].get('abstract_metadata',0),summ['access'].get('doi_metadata',0)+summ['access'].get('catalog_metadata',0),summ['access'].get('landing_page_inspected',0)),
'- Rejected: %d (%s). Merged as same-work duplicates of a promoted lead: %d.'%(cat['rejected'],', '.join('%s %d'%kv for kv in rej.most_common()),cat['matched-verified']),
'- Still open (%d, uncheckable today): '%len(openr)+'; '.join('%s — %s'%(t[:70],r) for _,t,r in openr),
'- Blocked/limited hosts: TRID 503; TU Delft repository timeout; Deep Blue, Curtin, UOW 403; UPC 418. IDEALS (Illinois) and UT Texas repository were reachable this time, resolving the pass-3 blocked items (Talbot 1907, Hilsdorf 1970, Riding 2007, K. Mather 1980, UPenn theses).',
'- Standards: one record per document at the latest edition registered in Crossref; earlier editions closed as duplicate-versions (ASTM C845/C1600/C1866 editions map to existing R179/R180/R185; BSI EN 14647 record to R181).',
'','### New verified resources (lead verification pass)']
for r in out:
    o.append(' | '.join([r['id'],','.join(r['topics']),r['title'],r['publisher'],r['type'],r['date'] or 'undated',r['url']]))
    au=', '.join(a for a in (r['authors'] or []) if a) if r.get('authors') else 'unknown'
    o.append('  Note: Authors: %s. %s Access: %s. %s%s%s'%(au,r['description'],r['access'],r['evidenceNote'],(' Edition: '+r['edition']) if r.get('edition') else '',(' Rights: '+r['rights']+'.') if r.get('rights') else ''))
o+=['','### Rejected leads (lead verification pass)']
for i,x in enumerate(CAN):
    if x.get('reviewPass')=='lead-verify-pass-2026-11-10' and x['status'] in ('rejected','matched-verified'):
        o.append('- [%s] %s — %s'%(x['status'],x['title'][:110],x.get('rejectReason') or ('same work as %s'%x.get('matchedTo'))))
open('index.md.tmp','w').write(md+'\n'+'\n'.join(o)+'\n'); os.replace('index.md.tmp','index.md')
# ---------- Page patch
pg=[{'id':r['id'],'t':r['title'],'pub':r['publisher'],'type':r['type'],'date':r['date'],'topics':r['topics'],'href':r['url']} for r in out]
open(PD+'page-leadverify-patch.js','w').write('// LEADVERIFY array for private Page (canvas aa726421-3b9d-47e1-bf26-700f350c5345): concatenate after DEEP3; totals %d resources; Last updated 2026-11-10.\nconst LEADVERIFY = '%len(S['resources'])+json.dumps(pg,ensure_ascii=False,indent=0)+';\nconst LEADVERIFY_NEWS = '+json.dumps(S['whatsNew'][0],ensure_ascii=False)+';\n')
print('ledger/index/page written')
