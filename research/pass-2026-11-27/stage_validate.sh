#!/bin/bash
# pass-2026-11-27: combined Nov 26 + Nov 27 bundle (fresh clone of main + working files)
set -e
W=/workspace/type1l-index; V=/tmp/t1l-v27; P=/workspace/publish-1127
EXC="--exclude=api-hits*.json --exclude=new-hits*.json --exclude=selected*.json --exclude=landing --exclude=ev --exclude=dedupe-dup*.json --exclude=oa-retry.json --exclude=__pycache__ --exclude=plan.json --exclude=page/canvas-* --exclude=oq --exclude=retry-b-p*.json --exclude=all-hits.json --exclude=kdot-cdx-partial.json --exclude=*.log --exclude=retry-c-p*.json --exclude=retry-c-raw.json --exclude=page/out-* --exclude=page/fresh-*"
rm -rf $V; git clone -q https://github.com/xxdccole/Type1L-Index $V
cd $V && git log --oneline | head -1
cp $W/site-data.json $V/data/site-data.json
cp $W/research/resource-notes.json $V/data/resource-notes.json
cp $W/index.md $V/research/index.md
cp $W/research-ledger.json $V/research/research-ledger.json
cp $W/research/portable/candidates.jsonl $W/research/portable/verified-sources.jsonl $V/research/
cp $W/research/review-retry.jsonl $W/research/review-retry.md $V/research/
cp $W/research/DAILY-2026-11-27-HANDOFF.md $V/research/
for D in pass-2026-11-26 pass-2026-11-27; do
  rm -rf $V/research/$D; mkdir -p $V/research/$D
  (cd $W/research/$D && tar cf - $EXC .) | (cd $V/research/$D && tar xf -)
done
cd $V && python3 scripts/build.py --validate && python3 scripts/build.py && python3 scripts/check_site.py
rm -rf $P; mkdir -p $P/stage/data $P/stage/research
cp $V/data/site-data.json $V/data/resource-notes.json $P/stage/data/
for f in index.md research-ledger.json candidates.jsonl verified-sources.jsonl review-retry.md review-retry.jsonl DAILY-2026-11-27-HANDOFF.md; do cp $V/research/$f $P/stage/research/; done
cp -r $V/research/pass-2026-11-26 $V/research/pass-2026-11-27 $P/stage/research/
cd $P && tar czf publish-2026-11-27.tar.gz stage && sha256sum publish-2026-11-27.tar.gz | tee publish-2026-11-27.tar.gz.sha256 && du -sh publish-2026-11-27.tar.gz
