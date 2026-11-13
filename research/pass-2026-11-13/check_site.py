#!/usr/bin/env python3
"""Integrity check of the built site (standard library only).

Checks every generated HTML page for: one <h1>, unique ids, canonical URL matching its path,
local links/scripts/styles that resolve (including #fragments), JSON-LD that parses, and a title
and description. Also parses sitemap.xml and the feeds, and checks that sitemap URLs map to files.
Exit code 1 on any problem.
"""
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag, urlparse

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "data/site-config.json").read_text(encoding="utf-8"))
BASE = CFG["baseUrl"]
errors = []


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.dupes, self.links, self.h1 = set(), [], [], 0
        self.canonical = self.description = None
        self.jsonld, self._ld, self._title, self.title = [], False, False, ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "link" and a.get("href") and a.get("rel") == "stylesheet":
            self.links.append(a["href"])
        if tag == "script" and a.get("src"):
            self.links.append(a["src"])
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if tag == "meta" and a.get("name") == "description":
            self.description = a.get("content")
        if tag == "script" and a.get("type") == "application/ld+json":
            self._ld = True
            self.jsonld.append("")
        if tag == "title":
            self._title = True

    def handle_endtag(self, tag):
        if tag == "script":
            self._ld = False
        if tag == "title":
            self._title = False

    def handle_data(self, data):
        if self._ld:
            self.jsonld[-1] += data
        if self._title:
            self.title += data


def parse(path):
    p = Page()
    text = path.read_text(encoding="utf-8")
    ids = re.findall(r'\sid="([^"]+)"', text)
    p.dupes = sorted({i for i in ids if ids.count(i) > 1})
    p.feed(text)
    return p


pages = {}
for f in sorted([ROOT / "index.html"] + list((ROOT / "topics").glob("*/index.html"))):
    pages[f] = parse(f)

for f, p in pages.items():
    rel = f.relative_to(ROOT).as_posix()
    where = rel
    if p.h1 != 1:
        errors.append(f"{where}: expected exactly one h1, found {p.h1}")
    if p.dupes:
        errors.append(f"{where}: duplicate ids {p.dupes}")
    url_path = "" if rel == "index.html" else rel[: -len("index.html")]
    if p.canonical != BASE + url_path:
        errors.append(f"{where}: canonical {p.canonical!r} != {BASE + url_path!r}")
    if not p.title.strip() or len(p.title) > 90:
        errors.append(f"{where}: missing or very long <title> ({len(p.title)} chars)")
    if not p.description or len(p.description) < 40:
        errors.append(f"{where}: missing or short meta description")
    for blob in p.jsonld:
        try:
            json.loads(blob)
        except ValueError as ex:
            errors.append(f"{where}: JSON-LD does not parse ({ex})")
    for href in p.links:
        if href.startswith(("http://", "https://", "mailto:", "data:")):
            continue
        target, frag = urldefrag(href)
        base = f.parent
        dest = (base / unquote(target)).resolve() if target else f
        if dest.is_dir():
            dest = dest / "index.html"
        if not dest.exists():
            errors.append(f"{where}: broken local link {href!r}")
            continue
        if frag and dest.suffix == ".html":
            tp = pages.get(dest) or parse(dest)
            if frag not in tp.ids:
                errors.append(f"{where}: {href!r} points to a missing anchor")

# sitemap and feeds
ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "a": "http://www.w3.org/2005/Atom"}
try:
    sm = ET.parse(ROOT / "sitemap.xml").getroot()
    for loc in sm.findall("s:url/s:loc", ns):
        u = loc.text
        if not u.startswith(BASE):
            errors.append(f"sitemap: {u} is outside baseUrl")
            continue
        path = ROOT / (u[len(BASE):] or "index.html")
        if path.is_dir():
            path = path / "index.html"
        if not path.exists():
            errors.append(f"sitemap: {u} has no file")
    n_sm = len(sm.findall("s:url", ns))
    if n_sm != len(pages):
        errors.append(f"sitemap lists {n_sm} URLs but the site has {len(pages)} pages")
except Exception as ex:
    errors.append(f"sitemap.xml: {ex}")
for name in ("feed.xml", "feed-daily.xml", "feed-weekly.xml"):
    try:
        feed = ET.parse(ROOT / name).getroot()
        ids = [x.text for x in feed.findall("a:entry/a:id", ns)]
        if len(ids) != len(set(ids)):
            errors.append(f"{name}: duplicate entry ids")
        print(f"{name}: {len(ids)} entries")
    except Exception as ex:
        errors.append(f"{name}: {ex}")

# Data, membership, dates, and scope. Counts and topic filters are rendered from the JSON.
data = json.loads((ROOT / "data/site-data.json").read_text(encoding="utf-8"))
notes_path = ROOT / "data/resource-notes.json"
notes = json.loads(notes_path.read_text(encoding="utf-8")) if notes_path.exists() else {}
home_html = (ROOT / "index.html").read_text(encoding="utf-8")
n_res, n_top = len(data["resources"]), len(data["topics"])
if f"{n_top} topics" not in home_html or f"{n_res} resources" not in home_html:
    errors.append("home page counts are not derived from site-data.json")
_home_title = re.search(r"<title>(.*?)</title>", home_html, re.S)
if _home_title and "Portland-Limestone Cement (PLC)" in _home_title.group(1):
    errors.append("home page still uses the Type IL-only document title")
if "not an exhaustive catalogue" not in home_html:
    errors.append("home page is missing the non-exhaustive coverage note")
if 'placeholder="Search the Cement &amp; Concrete Index"' not in home_html:
    errors.append("search placeholder was not broadened to the Cement & Concrete Index")
listed = {}
for t in data["topics"]:
    for rid in t.get("resourceIds") or []:
        listed.setdefault(rid, set()).add(t["id"])
TYPE_IL_TOPICS = {
    "standards", "dot", "carbon", "fresh", "strength", "durability", "scm",
    "pavement", "apps", "mix", "field", "supply", "intl", "news", "gaps",
    "guides", "microcracking", "mass",
}
for r in data["resources"]:
    rid = r["id"]
    row = re.search(rf'<tr id="r-{re.escape(rid)}"[^>]*\sdata-topics="([^"]*)"', home_html)
    if row is None:
        errors.append(f"home table is missing {rid}")
        continue
    if html.escape(r["url"], quote=True) not in home_html:
        errors.append(f"home page is missing the URL for {rid}")
    expected = set(r.get("topics") or []) | listed.get(rid, set())
    got = set(filter(None, row.group(1).split(" ")))
    if got != expected:
        errors.append(f"{rid}: topic filter tags {sorted(got)} != union {sorted(expected)}")
    if r.get("date") in (None, "", "-"):
        chunk = re.search(rf'<tr id="r-{re.escape(rid)}".*?</tr>', home_html, re.S)
        if chunk is None or "Undated" not in chunk.group(0) or "<time" in chunk.group(0):
            errors.append(f"{rid}: unknown date was not left undated")
    note = notes.get(rid)
    if note and html.escape(note, quote=True) not in home_html:
        errors.append(f"{rid}: source note is missing from the home page")
by_topic = {}
for r in data["resources"]:
    for tid in r.get("topics") or []:
        by_topic.setdefault(tid, set()).add(r["id"])
for t in data["topics"]:
    page = (ROOT / "topics" / t["id"] / "index.html").read_text(encoding="utf-8")
    ids = set(t.get("resourceIds") or []) | by_topic.get(t["id"], set())
    if not ids:
        if "Coverage gap" not in page or "not a finding that no literature exists" not in page:
            errors.append(f"topic {t['id']}: empty membership is not shown as a coverage gap")
        if "0 resource" in page:
            errors.append(f"topic {t['id']}: empty membership is shown as zero resources")
    for rid in ids:
        if f'id="r-{rid}"' not in page:
            errors.append(f"topic {t['id']}: missing resource {rid}")
    if t["id"] in TYPE_IL_TOPICS and t.get("takeaways") and "Type IL collection" not in page:
        errors.append(f"topic {t['id']}: Type IL takeaways are not scoped")
if "Type IL collection" not in home_html:
    errors.append("home page does not label the Type IL collection")

# Provenance sidecars. Candidates are an unverified queue and are not index resources.
for i in range(140, 178):
    if f"R{i}" not in notes or not str(notes.get(f"R{i}") or "").strip():
        errors.append(f"earlier source note R{i} was dropped")
verified_path = ROOT / "research" / "verified-sources.jsonl"
candidate_path = ROOT / "research" / "candidates.jsonl"
ledger_path = ROOT / "research" / "research-ledger.json"
resource_urls = {r.get("url", "").rstrip("/").lower() for r in data["resources"]}
resource_ids = {r["id"] for r in data["resources"]}
if not verified_path.exists():
    errors.append("research/verified-sources.jsonl is missing")
else:
    for line in verified_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        rid = item.get("id")
        if item.get("status") != "verified" or rid not in resource_ids:
            errors.append(f"verified sidecar {rid} is not an indexed resource")
        elif notes.get(rid) != item.get("evidenceNote"):
            errors.append(f"{rid}: source note does not match verified-sources evidenceNote")
if not candidate_path.exists():
    errors.append("research/candidates.jsonl is missing")
else:
    n_candidates = 0
    for line in candidate_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        n_candidates += 1
        status = item.get("status")
        url = (item.get("url") or "").rstrip("/").lower()
        # Open leads stay unverified. Closed lines record a promotion or a dedupe
        # and are not counted as index resources.
        if status == "candidate":
            if url and url in resource_urls:
                errors.append(f"unverified candidate URL is also an index resource: {item.get('url')}")
        elif status == "promoted":
            dest = item.get("promotedTo")
            if dest not in resource_ids:
                errors.append(f"promoted queue line does not point at an indexed resource: {dest!r}")
        elif status == "matched-verified":
            dest = item.get("matchedTo")
            if dest not in resource_ids:
                errors.append(f"matched-verified queue line does not point at an indexed resource: {dest!r}")
        elif status == "rejected":
            # Closed after inspection; must say why. A duplicate may point at the indexed record.
            if not str(item.get("rejectReason") or "").strip():
                errors.append(f"rejected queue line has no rejectReason: {item.get('title')!r}")
            dup = item.get("duplicateOf")
            for d in ([dup] if isinstance(dup, str) else (dup or [])):
                if d != "still open" and d not in resource_ids:
                    errors.append(f"rejected queue line points at an unknown resource: {d!r}")
        else:
            errors.append(f"candidate queue contains an unknown status: {status!r}")
    if n_candidates and str(n_candidates) in home_html and f"{n_candidates} resources" in home_html:
        errors.append("home page resource count matches the unverified candidate queue")
if not ledger_path.exists():
    errors.append("research/research-ledger.json is missing")
else:
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger_topics = ledger.get("topics") or []
    if len(ledger_topics) != len(data["topics"]):
        errors.append(f"research ledger has {len(ledger_topics)} topics, site data has {len(data['topics'])}")
    finished = [t.get("id") for t in ledger_topics if t.get("coverageStatus") in ("complete", "exhaustive", "finished")]
    if finished:
        errors.append(f"research ledger marks topics finished: {finished}")

print(f"checked {len(pages)} pages")
if errors:
    print("PROBLEMS:")
    for x in errors:
        print("  -", x)
    sys.exit(1)
print("site check passed")
