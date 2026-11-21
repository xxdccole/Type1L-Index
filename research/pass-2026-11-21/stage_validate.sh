#!/bin/bash
set -e
W=/workspace/type1l-index; V=/tmp/t1l-v21; P=/workspace/publish-1121
rm -rf $V; git clone -q https://github.com/xxdccole/Type1L-Index $V
cd $V && git log --oneline | head -1
cp $W/site-data.json $V/data/site-data.json
cp $W/research/resource-notes.json $V/data/resource-notes.json
cp $W/index.md $V/research/index.md
cp $W/research-ledger.json $V/research/research-ledger.json
cp $W/research/portable/candidates.jsonl $W/research/portable/verified-sources.jsonl $V/research/
cp $W/research/review-retry.jsonl $W/research/review-retry.md $V/research/
cp $W/research/DAILY-2026-11-21-HANDOFF.md $V/research/
rm -rf $V/research/pass-2026-11-21; mkdir -p $V/research/pass-2026-11-21
(cd $W/research/pass-2026-11-21 && tar cf - --exclude='api-hits*.json' --exclude='new-hits*.json' --exclude='selected*.json' --exclude='landing' --exclude='ev' --exclude='dedupe-dup.json' --exclude='oa-retry.json' --exclude='__pycache__' --exclude='plan.json' --exclude='page/canvas-*' .) | (cd $V/research/pass-2026-11-21 && tar xf -)
cd $V && python3 scripts/build.py --validate && python3 scripts/build.py && python3 scripts/check_site.py
rm -rf $P; mkdir -p $P/stage/data $P/stage/research
cp $V/data/site-data.json $V/data/resource-notes.json $P/stage/data/
for f in index.md research-ledger.json candidates.jsonl verified-sources.jsonl review-retry.md review-retry.jsonl DAILY-2026-11-21-HANDOFF.md; do cp $V/research/$f $P/stage/research/; done
cp -r $V/research/pass-2026-11-21 $P/stage/research/
cd $P && tar czf publish-2026-11-21.tar.gz stage && sha256sum publish-2026-11-21.tar.gz | tee publish-2026-11-21.tar.gz.sha256 && du -sh publish-2026-11-21.tar.gz
