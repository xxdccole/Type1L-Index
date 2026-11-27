"""Build Private Page edit-ops for the combined 2026-11-26 + 2026-11-27 daily passes (D1126/DAILY1126 then D1127/DAILY1127) against a FRESH ReadCanvas source.
Usage:  python3 make_edit_ops.py FRESH_SOURCE.tsx [OUT_DIR]
FRESH_SOURCE must already contain the Nov 25 changes (D1125 / DAILY1125, the Nov 25 scope line, evidence callout, what's-new row, change-log row and gaps row).
Dry run: research/pass-2026-11-25/page/canvas-2026-11-25-proposed.tsx (the Nov 25 edit as proposed). Without an argument the script prints this text and exits.
Writes OUT_DIR/edit-ops.json (ordered {step, old_string, new_string}; apply in order, each old_string must match exactly once at that point),
OUT_DIR/canvas-2026-11-27-proposed.tsx, OUT_DIR/d1126-block.ts and d1127-block.ts. Fails loudly (SystemExit naming the step and the match count) if any anchor is missing or ambiguous; nothing is written then.
Stage 1 (Nov 26) anchors on the Nov 25 text, stage 2 (Nov 27) anchors on the text stage 1 produced. Data: ../page-d1127.json (days -> per-day news/change/gap/takeaways/summary, rows)."""
import json,re,sys,os
if len(sys.argv)<2: raise SystemExit(__doc__)
HERE=os.path.dirname(os.path.abspath(__file__)); PD=os.path.dirname(HERE)+'/'
src=sys.argv[1]; OUT=(sys.argv[2] if len(sys.argv)>2 else HERE).rstrip('/')+'/'
base=open(src).read(); DAYS=json.load(open(PD+'page-d1127.json'))['days']
def js(s): return json.dumps(s,ensure_ascii=False)
LET='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
def row(r):
    href=r[6]; href='doi:'+href[len('https://doi.org/'):] if href.startswith('https://doi.org/') else href
    return '['+', '.join(js(x) for x in r[:6]+[href])+']'
def stage(base,tag,date,mon,G,prev,prevtags,prevcount,prevlast,prevdesc,prev_list,prevleads_phrase):
    SUM=G['summary']; rows=G['rows']; n=len(rows); first,last=rows[0][0],rows[-1][0]; total=G['total']
    chunks=[rows[i:i+50] for i in range(0,n,50)]
    blocks=['// D%s_%s (%s–%s)\nD%s.push(\n%s\n);\n'%(tag,LET[ci],ch[0][0],ch[-1][0],tag,',\n'.join(row(r) for r in ch)) for ci,ch in enumerate(chunks)]
    head='// %s daily pass (%s–%s): %d records — %d promoted from the review/retry list (%s), %d from the open queue (empty), %d new discovery records verified the same day (%s). Compact rows: [id,title,publisher,type,date,topicsCSV,href] — "doi:" expands to https://doi.org/.\nconst D%s: string[][] = [];\n'%(date,first,last,n,SUM['retryPromoted'],SUM['retryPromotedRange'],SUM['openQueuePromoted'],SUM['newPromoted'],SUM['discoveryRange'],tag)
    tail='const DAILY%s: Res[] = D%s.map((x) => ({ id: x[0], t: x[1], pub: x[2], type: x[3], date: x[4], topics: x[5] ? x[5].split(",") : [], href: x[6].startsWith("doi:") ? "https://doi.org/" + x[6].slice(4) : x[6] }));\n'%(tag,tag)
    open(OUT+'d%s-block.ts'%tag.lower(),'w').write(head+''.join(blocks)+tail)
    A='const AXIS: AxisTopic[] = ['; ops=[]
    groups=[blocks[i:i+3] for i in range(0,len(blocks),3)]
    for gi,g in enumerate(groups):
        ops.append(dict(step='Insert D%s block part %d/%d before AXIS'%(tag,gi+1,len(groups)),old_string=A,new_string=(head if gi==0 else '')+''.join(g)+(tail if gi==len(groups)-1 else '')+A))
    ops.append(dict(step='RES push (%s)'%tag,old_string='...'+prevtags+');',new_string='...'+prevtags+', ...DAILY%s);'%tag))
    ops.append(dict(step='topic loop (%s)'%tag,old_string='...'+prevtags+']) {',new_string='...'+prevtags+', ...DAILY%s]) {'%tag))
    old_scope=prev['scope_old']
    new_scope='Updated {} {}, 2026 (America/Chicago): {:,} resource records (R1–{}; R428 retired before publication). The {} {} daily pass added {}–{} ({} promoted from the review/retry list, {}; open queue empty; then {} new discovery records verified the same day, {}). '.format('November',date.split('-')[2].lstrip('0'),total,last,mon,date.split('-')[2].lstrip('0'),first,last,SUM['retryPromoted'],SUM['retryPromotedRange'],SUM['newPromoted'],SUM['discoveryRange'])
    # keep the old scope sentence tail after the new one
    ops.append(dict(step='scope line (%s)'%tag,old_string=old_scope,new_string=new_scope+prev['scope_keep']))
    ops.append(dict(step='evidence callout (%s)'%tag,old_string=prev['cb_old'],new_string=prev['cb_new_prefix']+G['cb']))
    ops.append(dict(step='whats new caption (%s)'%tag,old_string='<Section heading="What\'s new" id="new" caption="Last updated %s, 2026 (America/Chicago)">'%prev['cap'],new_string='<Section heading="What\'s new" id="new" caption="Last updated %s %s, 2026 (America/Chicago)">'%(mon,date.split('-')[2].lstrip('0'))))
    wn=G['news']; a=prev['wn_anchor']
    ops.append(dict(step='whats new row (%s)'%tag,old_string=a,new_string='{ lead: %s, title: %s, detail: %s },\n          '%(js(wn['date']),js(wn['title']),js(wn['detail']))+a))
    cl=G['change']; a=prev['cl_anchor']
    ops.append(dict(step='changelog row (%s)'%tag,old_string=a,new_string='[%s, %s],\n          '%(js(cl['date']),js(cl['entry']))+a))
    a=prev['gap_anchor']
    ops.append(dict(step='gaps row (%s)'%tag,old_string=a,new_string='{ title: "Daily pass limits (%s %s)", detail: %s },\n            '%(mon,date.split('-')[2].lstrip('0'),js(G['gap']))+a))
    skipped=[]
    cur0=base
    for o in ops:
        c=cur0.count(o['old_string'])
        if c!=1: raise SystemExit('FAIL at step "%s": old_string matches %d times (need exactly 1).'%(o['step'],c))
        cur0=cur0.replace(o['old_string'],o['new_string'],1)
    for tid in G['takeaways']:
        m=re.search(r'\{key:"%s",[^\n]*?take:"((?:[^"\\]|\\.)*)"\}'%re.escape(tid),cur0)
        if not m: skipped.append(tid); continue
        ids=[r[0] for r in rows if tid in r[5].split(',')]
        if not ids: continue
        oldt=m.group(1)
        ops.append(dict(step='AXIS take %s (%s)'%(tid,tag),old_string='take:"%s"}'%oldt,new_string='take:"%s %s backfill: %d records (%s–%s), DOI/abstract/record-page/catalogue level."}'%(oldt,date[5:].replace('-','/') and mon+' '+date.split('-')[2].lstrip('0'),len(ids),ids[0],ids[-1])))
    cur=base
    for o in ops:
        c=cur.count(o['old_string'])
        if c!=1: raise SystemExit('FAIL at step "%s": old_string matches %d times (need exactly 1).'%(o['step'],c))
        cur=cur.replace(o['old_string'],o['new_string'],1)
    missing=[r[0] for r in rows if ('"%s"'%r[0]) not in cur]
    if missing: raise SystemExit('FAIL: %d new ids missing, e.g. %s'%(len(missing),missing[:3]))
    return cur,ops,skipped
G26=DAYS['2026-11-26']; G27=DAYS['2026-11-27']
# --- stage 1 anchors (Nov 25 text)
P25=dict(scope_old='Updated November 25, 2026 (America/Chicago): 4,907 resource records (R1–R4908; R428 retired before publication). The Nov 25 daily pass added R4583–R4908',scope_keep='The Nov 25 daily pass added R4583–R4908',
  cb_old='the list now holds 125 leads and no leads remain open.',cb_new_prefix='the list then held 125 leads and no leads remained open. ',cap='Nov 25',
  wn_anchor='{ lead: "Nov 25", title: "Daily pass: 326 verified additions (R4583–R4908)',cl_anchor='["2026-11-25", "Daily pass 2026-11-25: 326 verified additions',gap_anchor='{ title: "Daily pass limits (Nov 25)"')
S26=G26['summary']
G26['cb']=('On Nov 26 the review/retry list was worked first by new routes: %d of its 125 leads were promoted (%s; opened via PDF text extraction, Wayback copies including four KDOT special provisions archived under older ksdot.gov document versions, archived TRID records, an OSTI ETDEWEB record, BnF and NDL catalogue records) and %d stay on it after another retry; the open queue was empty; %d new leads were checked the same day (%d promoted %s, %d qualified but unavailable added to the review list, %d rejected: a duplicate of R4298 and two superseded BSI undated/series records); the list now holds %d leads and no leads remain open.'%(S26["retryPromoted"],S26["retryPromotedRange"],S26["retryStill"],S26["newLeads"],S26["newPromoted"],S26["discoveryRange"],S26["retryNewDiscovery"],S26["newRejectedDup"],S26["retryTotal"]))
cur1,ops1,sk1=stage(base,'1126','2026-11-26','Nov',G26,P25,'DAILY1122, ...DAILY1125',0,0,0,0,0)
# --- stage 2 anchors (text produced by stage 1)
r26=G26['rows']; sc26='Updated November 26, 2026 (America/Chicago): {:,} resource records (R1–{}; R428 retired before publication). The Nov 26 daily pass added {}–{} ({} promoted from the review/retry list, {}; open queue empty; then {} new discovery records verified the same day, {}). '.format(G26['total'],r26[-1][0],r26[0][0],r26[-1][0],S26['retryPromoted'],S26['retryPromotedRange'],S26['newPromoted'],S26['discoveryRange'])
S27=G27['summary']
P26=dict(scope_old=sc26+'The Nov 25 daily pass added R4583–R4908',scope_keep='The Nov 25 daily pass added R4583–R4908',
  cb_old='the list now holds %d leads and no leads remain open.'%S26['retryTotal'],cb_new_prefix='the list then held %d leads and no leads remained open. '%S26['retryTotal'],cap='Nov 26',
  wn_anchor='{ lead: "Nov 26", title: %s'%js(G26['news']['title'])[:-1],cl_anchor='[%s, %s'%(js(G26['change']['date']),js(G26['change']['entry'])[:60]),gap_anchor='{ title: "Daily pass limits (Nov 26)"')
# the Nov 27 scope sentence must keep the Nov 26 sentence, so scope_keep = Nov 26 sentence + Nov 25 tail
P26['scope_keep']=sc26.replace('Updated November 26, 2026 (America/Chicago): {:,} resource records (R1–{}; R428 retired before publication). '.format(G26['total'],r26[-1][0]),'')+'The Nov 25 daily pass added R4583–R4908'
P26['scope_keep']='The Nov 26 daily pass added'+P26['scope_keep'][len('The Nov 26 daily pass added'):]
G27['cb']=('On Nov 27 the review/retry list was worked first again: %d of its %d leads were promoted (%s; opened via Wayback copies of repository records and PDFs, three archived TRID records and direct record pages) and %d stay on it after another retry; the open queue was empty; %d new leads were checked the same day (%d promoted %s, %d qualified but unavailable added to the review list, %d rejected as off-topic asphalt-concrete or piezoelectric-sensor items); the list now holds %d leads and no leads remain open.'%(S27["retryPromoted"],S26["retryTotal"],S27["retryPromotedRange"],S27["retryStill"],S27["newLeads"],S27["newPromoted"],S27["discoveryRange"],S27["retryNewDiscovery"],S27["newRejectedDup"],S27["retryTotal"]))
cur2,ops2,sk2=stage(cur1,'1127','2026-11-27','Nov',G27,P26,'DAILY1122, ...DAILY1125, ...DAILY1126',0,0,0,0,0)
ops=ops1+ops2
open(OUT+'canvas-2026-11-27-proposed.tsx','w').write(cur2); json.dump(ops,open(OUT+'edit-ops.json','w'),ensure_ascii=False,indent=1)
print(src,'->',len(ops),'ops (%d + %d); max new_string'%(len(ops1),len(ops2)),max(len(o['new_string'].encode()) for o in ops),'bytes; skipped takes',sk1,sk2)
