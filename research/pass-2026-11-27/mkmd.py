"""Regenerate research/review-retry.md from research/review-retry.jsonl (format of the 2026-11-19 file; adapted from research/pass-2026-11-19-retry/mkmd.py)."""
import json,collections,sys
B='/workspace/type1l-index/research/'
L=[json.loads(l) for l in open(B+'review-retry.jsonl')]
S=json.load(open(B+'pass-2026-11-27/apply-summary.json'))
def md(s): return (s or '').replace('|','\\|').replace('\n',' ')
out=['# Leads to review and retry','',
'Updated November 27, 2026 (America/Chicago). Generated from `research/review-retry.jsonl`.','',
'These leads look real and on-topic: they have a credible title, author, venue, or catalogue or citation hit. But they could not be inspected when they were found, so they are **not index resources** and have no R numbers. Off-topic leads, true duplicates, retractions and non-sources stay `rejected` in `research/candidates.jsonl`.','',
'Topics are suggested groupings for review. The daily run sets final topics when it promotes a lead.','',
'- **Ready to promote** (`retryOutcome: "promotable"`): a retry opened a real record and the verified metadata is recorded. The next daily run assigns R numbers.',
'- **Still unavailable** (`retryOutcome: "still-unavailable"`): no legitimate route opened a record. The daily run retries these. No paywall bypass and no accounts.','',
f"Promoted from this list on 2026-11-27: {S['retryPromoted']} leads ({S['retryPromotedRange']}; opened on today's retry: Wayback copies of repository records and PDFs, three archived TRID records, a DergiPark page, an EPN repository record and an ACI abstracts-portal page). They left the list and are index resources now.",'',
f"Totals: {len(L)} leads. {sum(e['retryOutcome']=='promotable' for e in L)} ready to promote, {sum(e['retryOutcome']!='promotable' for e in L)} still unavailable ({S['retryStill']} carried over and retried again on 2026-11-27, {S['retryNew']} added on 2026-11-27 from discovery).",'']
for outcome,head in (('promotable','Ready to promote'),('still-unavailable','Still unavailable')):
    rows=[e for e in L if e['retryOutcome']==outcome]
    out+=[f'## {head} ({len(rows)})','']
    g=collections.OrderedDict()
    for e in sorted(rows,key=lambda x:(x.get('reviewTopicName') or '~',x['title'].lower())): g.setdefault(e.get('reviewTopicName') or 'Unassigned',[]).append(e)
    for t,rs in g.items():
        out+=[f'### {t} ({len(rs)})','']
        for e in rs:
            au=e.get('authors') or []
            by='; '.join(x for x in [', '.join(au[:4]) + (' et al.' if len(au)>4 else ''), e.get('venue') or '', str(e.get('year') or 'n.d.')] if x)
            ident=[]
            if e.get('doi'): ident.append('DOI '+e['doi'])
            if e.get('openalexId'): ident.append('OpenAlex '+e['openalexId'].split('/')[-1])
            out.append(f"- **{md(e['title'])}**  ")
            out.append(f"  {md(by)}  ")
            if ident: out.append(f"  Identifier: {', '.join(ident)}  ")
            q,_,rest=e['retryReason'].partition('. Unavailable: ')
            out.append(f"  Why it qualifies: {md(q)}.  ")
            un=rest.split('. Retried')[0].split('. Checked')[0]
            out.append(f"  Why it is unavailable: {md(un)}.  ")
            links=[f"[lead URL]({e['url']})"] if e.get('url') else []
            out.append(f"  Last tried {e['lastTried']} · {e['attempts']} attempt{'s' if e['attempts']!=1 else ''} · first seen {e['firstSeen']} · {len(e['urlsTried'])} URLs tried" + (' · '+' · '.join(links) if links else ''))
            out.append('')
open(B+'review-retry.md','w').write('\n'.join(out))
print(len(out),len(L))
