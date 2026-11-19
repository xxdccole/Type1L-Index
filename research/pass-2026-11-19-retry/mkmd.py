import json,collections
L=[json.loads(l) for l in open('review-retry.jsonl')]
S=json.load(open('summary.json'))
def md(s): return (s or '').replace('|','\\|').replace('\n',' ')
out=['# Leads to review and retry','',
'Updated November 19, 2026 (America/Chicago). Generated from `research/review-retry.jsonl`.','',
'These leads look real and on-topic: they have a credible title, author, venue, or catalogue or citation hit. But they could not be inspected when they were found, so they are **not index resources** and have no R numbers. Off-topic leads, true duplicates, retractions and non-sources stay `rejected` in `research/candidates.jsonl`.','',
'Topics are suggested groupings for review. The daily run sets final topics when it promotes a lead.','',
'- **Ready to promote** (`retryOutcome: "promotable"`): the 2026-11-19 retry opened a real record (publisher or repository page, a Wayback Machine copy of the record page, a CiNii Research record, or an Open Library catalogue record). The verified metadata is recorded. The next daily run assigns R numbers.',
'- **Still unavailable** (`retryOutcome: "still-unavailable"`): no legitimate route opened a record. The daily run retries these. No paywall bypass and no accounts.','',
f"Totals: {len(L)} leads. {sum(e['retryOutcome']=='promotable' for e in L)} ready to promote, {sum(e['retryOutcome']!='promotable' for e in L)} still unavailable.",'']
for outcome,head in (('promotable','Ready to promote'),('still-unavailable','Still unavailable')):
    rows=[e for e in L if e['retryOutcome']==outcome]
    out+=[f'## {head} ({len(rows)})','']
    g=collections.OrderedDict()
    for e in sorted(rows,key=lambda x:(x['reviewTopicName'] or '~',x['title'].lower())): g.setdefault(e['reviewTopicName'] or 'Unassigned',[]).append(e)
    for t,rs in g.items():
        out+=[f'### {t} ({len(rs)})','']
        for e in rs:
            by='; '.join(x for x in [', '.join(e['authors'][:4]) + (' et al.' if len(e['authors'])>4 else ''), e.get('venue') or '', str(e.get('year') or 'n.d.')] if x)
            ident=[]
            if e.get('doi'): ident.append('DOI '+e['doi'])
            if e.get('openalexId'): ident.append('OpenAlex '+e['openalexId'].split('/')[-1])
            out.append(f"- **{md(e['title'])}**  ")
            out.append(f"  {md(by)}  ")
            if ident: out.append(f"  Identifier: {', '.join(ident)}  ")
            q,_,rest=e['retryReason'].partition('. Previously unavailable: ') if outcome=='promotable' else e['retryReason'].partition('. Unavailable: ')
            out.append(f"  Why it qualifies: {md(q)}.  ")
            if outcome=='promotable':
                un,_,now=rest.partition('. Now inspectable')
                out.append(f"  Why it was unavailable: {md(un)}.  ")
                out.append(f"  Now inspectable: {md(e['accessLevel'])}, [{md(e['bestUrl'][:90])}]({e['bestUrl']})" + (f" (archived from {md(e.get('archivedFrom'))})" if e.get('archivedFrom') else '') + '  ')
                if e.get('verificationNote'): out.append(f"  Check: {md(e['verificationNote'])}  ")
            else:
                un=rest.split('. Retried')[0]
                out.append(f"  Why it is unavailable: {md(un)}.  ")
            links=[f"[lead URL]({e['url']})"] if e.get('url') else []
            out.append(f"  Last tried {e['lastTried']} · {e['attempts']} attempt{'s' if e['attempts']!=1 else ''} · first seen {e['firstSeen']} · {len(e['urlsTried'])} URLs tried" + (' · '+' · '.join(links) if links else ''))
            out.append('')
open('review-retry.md','w').write('\n'.join(out))
print(len(out))
