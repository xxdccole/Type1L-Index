#!/usr/bin/env python3
"""Integrity check of the built site (standard library only).

Checks every generated HTML page for: one <h1>, unique ids, canonical URL matching its path,
local links/scripts/styles that resolve (including #fragments), JSON-LD that parses, and a title
and description. Also parses sitemap.xml and the feeds, and checks that sitemap URLs map to files.
Exit code 1 on any problem.
"""
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

print(f"checked {len(pages)} pages")
if errors:
    print("PROBLEMS:")
    for x in errors:
        print("  -", x)
    sys.exit(1)
print("site check passed")
