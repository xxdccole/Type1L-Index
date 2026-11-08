#!/usr/bin/env python3
"""Build the static site from data/site-data.json and data/site-config.json.

Standard library only. Writes:
  index.html, topics/<id>/index.html, sitemap.xml, llms.txt,
  feed.xml (newest resources), feed-daily.xml, feed-weekly.xml (digests)

Usage:
  python3 scripts/build.py                  validate, then build
  python3 scripts/build.py --validate       validate only (exit 1 on errors)
  python3 scripts/build.py --today YYYY-MM-DD   build as if run on that UTC date
  python3 scripts/build.py --indexnow       after a build, ping IndexNow with the site URLs

Digest feeds only contain COMPLETED days and ISO weeks (strictly before today, UTC), so an entry
is never edited after an email service has picked it up. Because of that the build depends on the
date; the workflow in .github/workflows/build.yml rebuilds daily.
"""
import argparse
import collections
import datetime as dt
import html
import json
import re
import shutil
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape as xesc

ROOT = Path(__file__).resolve().parent.parent
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
PARTIAL_DATE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
FULL_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NOTES_PATH = ROOT / "data" / "resource-notes.json"
# Original topic ids. Their takeaways describe Type IL practice and stay labeled that way.
TYPE_IL_TOPICS = frozenset({
    "standards", "dot", "carbon", "fresh", "strength", "durability", "scm",
    "pavement", "apps", "mix", "field", "supply", "intl", "news", "gaps",
    "guides", "microcracking", "mass",
})
TOPIC_AXES = (
    ("type-il", "Type IL collection",
     "Takeaways in this group stay limited to Type IL portland-limestone cement. They are not general rules for every binder or concrete."),
    ("binder", "Cement and binder families",
     "Foundational seeds for binder chemistry. Not a complete catalogue of cements."),
    ("scm", "SCMs and additions",
     "A topic with no sources is a documented coverage gap, not a claim that no literature exists."),
    ("concrete", "Concrete families and applications",
     "Seeded families. Practice for one family does not transfer to the others."),
    ("cross", "Cross-cutting engineering topics",
     "Partial coverage. Catalogue scopes, previews, and project claims are labeled in the source notes."),
)
SCOPE_NOTE = (
    "Type IL collection. These points describe portland-limestone (Type IL) mixtures and exposures already indexed. "
    "They are not general rules for every cement or concrete."
)
SCOPE_NOTE_SHORT = "Type IL collection. These points are not general rules for every cement or concrete."
EVIDENCE_NOTE = (
    "Undated entries have no publication date in the source. A year in a file URL is not used as the date. "
    "Abstracts, previews, catalogue scopes, and manufacturer or project claims are not full-text standards or independent performance proof. "
    "Empty topics are documented gaps. This index is foundational coverage, not an exhaustive catalogue."
)
ISSUES_NOTE = (
    "Points that name Type IL, PLC, or a specific cement type describe that collection. "
    "They are not findings about every cement or concrete."
)


def axis_key(tid):
    if tid in TYPE_IL_TOPICS:
        return "type-il"
    if tid.startswith("binder-"):
        return "binder"
    if tid.startswith("scm-"):
        return "scm"
    if tid.startswith("concrete-"):
        return "concrete"
    if tid.startswith("cross-"):
        return "cross"
    return "other"


def e(value):
    return html.escape("" if value is None else str(value), quote=True)


# ----------------------------------------------------------------------------- load + validate
ADDED_CACHE = ROOT / "added-dates.json"


def recover_added_dates():
    """Days a resource was already indexed, keyed by resource id.

    Digest entries are grouped by that day. `feed.xml` keeps only the 100
    newest, so the full set is stored in added-dates.json once known. The feed
    fills any id the cache does not have yet (the first build after a data
    file that omits `added`).
    """
    found = {}
    if ADDED_CACHE.exists():
        try:
            raw = json.loads(ADDED_CACHE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raw = None
        if isinstance(raw, dict):
            found.update({k: v for k, v in raw.items() if isinstance(v, str) and FULL_DATE.match(v)})
    path = ROOT / "feed.xml"
    if path.exists():
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            root = None
        if root is not None:
            ns = {"a": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("a:entry", ns):
                eid = entry.findtext("a:id", default="", namespaces=ns)
                updated = entry.findtext("a:updated", default="", namespaces=ns)
                match = re.search(r"#r-(R\d+)$", eid or "")
                day = (updated or "")[:10]
                if match and FULL_DATE.match(day) and match.group(1) not in found:
                    found[match.group(1)] = day
    return found


def save_added_dates(resources):
    data = {r["id"]: r["added"] for r in resources if FULL_DATE.match(str(r.get("added") or ""))}
    ADDED_CACHE.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def prepare(d):
    """Fill gaps that would stop the page rendering. Does not rewrite the JSON file.

    `added` drives the digest feeds. "-" and "" are not publication dates, so they
    render as undated. A lowercase type label would split the type filter.

    Topic membership is the union of `resource.topics` and `topic.resourceIds`.
    Preserved records can sit on a newer topic only through `resourceIds`. The join
    is in memory, so those resource objects are not rewritten in the JSON file, and
    both the topic page and the topic filter still find them.
    """
    prior = recover_added_dates()
    by_id = {r.get("id"): r for r in d["resources"]}
    n_date = n_type = n_added = n_tags = 0
    for r in d["resources"]:
        if r.get("date") in ("-", ""):
            r["date"] = None
            n_date += 1
        typ = r.get("type")
        if isinstance(typ, str) and typ[:1].islower():
            r["type"] = typ[:1].upper() + typ[1:]
            n_type += 1
        if not r.get("added"):
            r["added"] = prior.get(r.get("id")) or d.get("lastUpdated")
            n_added += 1
    topics = {t.get("id"): t for t in d["topics"]}
    for t in d["topics"]:
        for rid in list(t.get("resourceIds") or []):
            r = by_id.get(rid)
            if r is not None and t.get("id") not in (r.get("topics") or []):
                r.setdefault("topics", []).append(t["id"])
                n_tags += 1
    for r in d["resources"]:
        for tid in list(r.get("topics") or []):
            t = topics.get(tid)
            if t is not None and r.get("id") not in (t.get("resourceIds") or []):
                t.setdefault("resourceIds", []).append(r["id"])
                n_tags += 1
    if n_date or n_type or n_added or n_tags:
        print(f"render normalize: {n_date} placeholder dates, {n_type} type labels, "
              f"{n_added} missing added dates, {n_tags} topic links")
    return d


def load():
    data = json.loads((ROOT / "data/site-data.json").read_text(encoding="utf-8"))
    cfg = json.loads((ROOT / "data/site-config.json").read_text(encoding="utf-8"))
    prepare(data)
    return data, cfg


def load_notes():
    """Optional per-resource evidence notes. Missing file means there are none."""
    if not NOTES_PATH.exists():
        return {}
    raw = json.loads(NOTES_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return None
    return raw


def validate(d, cfg, notes=None):
    errs = []
    need = ["title", "summary", "summaryText", "lastUpdated", "whatsNew", "topics",
            "keyIssues", "resources", "gaps", "changeLog"]
    for k in need:
        if k not in d:
            errs.append(f"missing top-level field: {k}")
    if errs:
        return errs
    if not FULL_DATE.match(d["lastUpdated"]):
        errs.append(f"lastUpdated is not YYYY-MM-DD: {d['lastUpdated']!r}")
    topics = {}
    for t in d["topics"]:
        if not SLUG.match(t.get("id", "")):
            errs.append(f"topic id is not a lowercase slug: {t.get('id')!r}")
        if t["id"] in topics:
            errs.append(f"duplicate topic id: {t['id']}")
        topics[t["id"]] = t
        if not t.get("name"):
            errs.append(f"topic {t['id']}: empty name")
        ids = t.get("resourceIds")
        if not isinstance(ids, list):
            errs.append(f"topic {t['id']}: resourceIds must be a list")
        elif len(set(ids)) != len(ids):
            errs.append(f"topic {t['id']}: duplicate resourceIds")
        elif not ids and not t.get("takeaways"):
            errs.append(f"topic {t['id']}: an empty topic needs a takeaway stating the coverage gap")
    res = {}
    seen_url, seen_title, types = {}, {}, collections.defaultdict(set)
    for r in d["resources"]:
        rid = r.get("id", "?")
        if rid in res:
            errs.append(f"duplicate resource id: {rid}")
        res[rid] = r
        for k in ("id", "title", "publisher", "type", "url", "topics", "added"):
            if r.get(k) in (None, "", []):
                errs.append(f"{rid}: missing {k}")
        if "date" not in r:
            errs.append(f"{rid}: missing date (use null for undated)")
        elif r["date"] is not None and not PARTIAL_DATE.match(str(r["date"])):
            errs.append(f"{rid}: date must be YYYY, YYYY-MM, YYYY-MM-DD or null, got {r['date']!r}")
        if r.get("added") and (not FULL_DATE.match(r["added"]) or r["added"] > d["lastUpdated"]):
            errs.append(f"{rid}: 'added' must be YYYY-MM-DD and not after lastUpdated, got {r.get('added')!r}")
        if not re.match(r"^https?://[^\s]+$", r.get("url", "")):
            errs.append(f"{rid}: url must be absolute http(s)")
        seen_url.setdefault(r.get("url", "").rstrip("/").lower(), []).append(rid)
        seen_title.setdefault(re.sub(r"\W+", " ", r.get("title", "").lower()).strip(), []).append(rid)
        if r.get("type"):
            types[r["type"].lower()].add(r["type"])
            if r["type"][0] != r["type"][0].upper():
                errs.append(f"{rid}: type should start with a capital letter: {r['type']!r}")
        for tid in r.get("topics", []):
            if tid not in topics:
                errs.append(f"{rid}: unknown topic {tid!r}")
            elif rid not in topics[tid]["resourceIds"]:
                errs.append(f"{rid}: tagged {tid!r} but missing from that topic's resourceIds")
    for t in d["topics"]:
        for rid in t.get("resourceIds", []):
            if rid not in res:
                errs.append(f"topic {t['id']}: unknown resource {rid}")
            elif t["id"] not in res[rid]["topics"]:
                errs.append(f"topic {t['id']} lists {rid}, but {rid} is not tagged {t['id']!r}")
    for k, v in seen_url.items():
        if len(v) > 1:
            errs.append(f"duplicate url in {v}")
    for k, v in seen_title.items():
        if len(v) > 1:
            errs.append(f"duplicate title in {v}")
    for k, v in types.items():
        if len(v) > 1:
            errs.append(f"type labels differ only by case: {sorted(v)}")
    last = None
    for c in d["changeLog"]:
        if not FULL_DATE.match(c.get("date", "")) or not c.get("entry"):
            errs.append(f"bad changeLog entry: {c!r}")
        elif last and c["date"] < last:
            errs.append("changeLog is not in date order")
        last = c.get("date", last)
    if d["changeLog"] and d["changeLog"][-1]["date"] != d["lastUpdated"]:
        errs.append("lastUpdated differs from the last changeLog date")
    for w in d["whatsNew"]:
        if not (w.get("title") and w.get("date")):
            errs.append(f"whatsNew item needs date and title: {w!r}")
    if not cfg["baseUrl"].endswith("/") or not cfg["baseUrl"].startswith("https://"):
        errs.append("config baseUrl must be an https URL ending in /")
    if notes is None:
        errs.append("data/resource-notes.json must be an object of resource id to note")
    else:
        for rid, note in notes.items():
            if rid not in res:
                errs.append(f"resource note for unknown id {rid}")
            elif not isinstance(note, str) or not note.strip():
                errs.append(f"resource note {rid} is empty")
    return errs


# ----------------------------------------------------------------------------- helpers
def long_date(v):
    if not FULL_DATE.match(v):
        return v
    y, m, dd = (int(x) for x in v.split("-"))
    return f"{MONTHS[m - 1]} {dd}, {y}"


def dkey(v):
    if not v or not PARTIAL_DATE.match(str(v)):
        return None
    p = str(v).split("-") + ["0", "0"]
    return int(p[0]) * 10000 + int(p[1]) * 100 + int(p[2])


def rid_num(r):
    return int(re.sub(r"\D", "", r["id"]) or 0)


def sorted_resources(resources):
    """Default order: date, newest first; undated last; ties by title."""
    return sorted(resources, key=lambda r: (dkey(r["date"]) is None, -(dkey(r["date"]) or 0), r["title"].lower()))


def time_el(v, long=False):
    if not v:
        return '<span class="muted">Undated</span>'
    attr = f' datetime="{e(v)}"' if PARTIAL_DATE.match(str(v)) else ""
    return f"<time{attr}>{e(long_date(v) if long else v)}</time>"


def ext_link(r):
    return (f'<a class="res-title" href="{e(r["url"])}" target="_blank" rel="noopener">{e(r["title"])}'
            f'<span class="sr-only"> (opens in a new tab)</span></a>')


def short(text, n=158):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= n:
        return text
    cut = text[:n].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "…"


# ----------------------------------------------------------------------------- page shell
class Site:
    def __init__(self, d, cfg, today, notes=None):
        self.d, self.cfg, self.today = d, cfg, today
        self.notes = notes or {}
        self.base = cfg["baseUrl"]
        self.topics = {t["id"]: t for t in d["topics"]}
        self.res = {r["id"]: r for r in d["resources"]}
        self.name = d["title"]
        self.has_og = (ROOT / "assets/og.png").exists()
        self.first_date = d["changeLog"][0]["date"] if d["changeLog"] else d["lastUpdated"]

    def doc_title(self, specific=None):
        if not specific:
            return self.name
        full = f"{specific} | {self.name}"
        if len(full) <= 90:
            return full
        if len(specific) <= 90:
            return specific
        return short(specific, 89)

    def iter_groups(self):
        buckets = {key: [] for key, _, _ in TOPIC_AXES}
        other = []
        for t in self.d["topics"]:
            key = axis_key(t["id"])
            if key in buckets:
                buckets[key].append(t)
            else:
                other.append(t)
        out = [(key, label, note, buckets[key]) for key, label, note in TOPIC_AXES if buckets[key]]
        if other:
            out.append(("other", "Additional topics", "Topics outside the four axes.", other))
        return out

    def topic_desc(self, t, cnt):
        if t.get("takeaways"):
            return short(t["takeaways"][0])
        if cnt == 0:
            return (
                f"Coverage gap: no dedicated source is indexed yet for {t['name']}. "
                "This records a limit of the index, not a finding that the literature is empty."
            )
        return (
            f"{cnt} sources filed under {t['name']} in the {self.name}. "
            "Foundational coverage, not an exhaustive catalogue."
        )

    def scope_html(self, t, brief=False):
        if t["id"] not in TYPE_IL_TOPICS or not t.get("takeaways"):
            return ""
        return f'<p class="scope-note">{e(SCOPE_NOTE_SHORT if brief else SCOPE_NOTE)}</p>'

    def caveat(self, r):
        note = self.notes.get(r["id"])
        if not note:
            return ""
        return f'<details class="caveat"><summary>Source note</summary><p>{e(note)}</p></details>'

    def topic_options(self):
        parts = []
        for _, label, _, topics in self.iter_groups():
            opts = []
            for t in topics:
                gap = ' data-gap="1"' if not t.get("resourceIds") else ""
                opts.append(f'<option value="{e(t["id"])}"{gap}>{e(t["name"])}</option>')
            parts.append(f'<optgroup label="{e(label)}">{"".join(opts)}</optgroup>')
        return "".join(parts)

    def tlink(self, tid, prefix):
        return f'{prefix}topics/{tid}/'

    def chips(self, tids, prefix):
        out = "".join(f'<a class="chip" href="{e(self.tlink(t, prefix))}">{e(self.topics[t]["name"])}</a>' for t in tids)
        return f'<div class="chips">{out}</div>'

    def head(self, *, title, description, canonical, prefix, jsonld, og_type="website"):
        c = self.cfg
        v = c.get("verification", {})
        metas = []
        if v.get("google"):
            metas.append(f'<meta name="google-site-verification" content="{e(v["google"])}">')
        if v.get("bing"):
            metas.append(f'<meta name="msvalidate.01" content="{e(v["bing"])}">')
        img = ""
        if self.has_og:
            img = (f'<meta property="og:image" content="{e(self.base)}assets/og.png">'
                   '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
                   f'<meta property="og:image:alt" content="{e(self.name)}">'
                   f'<meta name="twitter:image" content="{e(self.base)}assets/og.png">')
        ld = json.dumps(jsonld, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        return f"""<!DOCTYPE html>
<html lang="{e(c.get('language', 'en'))}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical)}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
{chr(10).join(metas)}
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{e(self.name)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="{'summary_large_image' if self.has_og else 'summary'}">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(description)}">
{img}
<link rel="alternate" type="application/atom+xml" title="Daily digest" href="{e(self.base)}feed-daily.xml">
<link rel="alternate" type="application/atom+xml" title="Weekly digest" href="{e(self.base)}feed-weekly.xml">
<link rel="alternate" type="application/atom+xml" title="Newest resources" href="{e(self.base)}feed.xml">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='3' fill='%235c564c'/%3E%3C/svg%3E">
<link rel="stylesheet" href="{prefix}css/styles.css">
<script type="application/ld+json">{ld}</script>
</head>
"""

    def footer(self, prefix):
        d = self.d
        return f"""<footer class="site-footer">
<div class="wrap">
<p>{e(d['title'])}. Last updated {time_el(d['lastUpdated'], True)}.</p>
<p><a href="{prefix}feed-daily.xml">Daily digest feed</a> · <a href="{prefix}feed-weekly.xml">Weekly digest feed</a> · <a href="{prefix}feed.xml">Newest resources feed</a> · <a href="{prefix}data/site-data.json">Data (JSON)</a> · <a href="{prefix}data/resource-notes.json">Source notes (JSON)</a></p>
<p><a href="#top">Back to top</a></p>
</div>
</footer>
"""

    # ------------------------------------------------------------------ subscribe
    def subscribe(self, prefix):
        n = self.cfg.get("newsletter", {})
        form = ""
        if n.get("enabled") and n.get("formAction"):
            fld = e(n.get("frequencyField", "tag"))
            radios = "".join(
                f'<label class="radio"><input type="radio" name="{fld}" value="{e(f["value"])}"{" checked" if i == 0 else ""}> {e(f["label"])}</label>'
                for i, f in enumerate(n.get("frequencies", [])))
            hidden = "".join(f'<input type="hidden" name="{e(k)}" value="{e(v)}">' for k, v in n.get("hiddenFields", {}).items())
            form = f"""<form class="subscribe-form" method="post" action="{e(n['formAction'])}" target="{e(n.get('target', '_blank'))}">
<div class="field grow"><label for="sub-email">Email address</label><input id="sub-email" name="{e(n.get('emailField', 'email'))}" type="email" required autocomplete="email" inputmode="email"></div>
<fieldset class="field"><legend>How often?</legend>{radios}</fieldset>
{hidden}
<div class="field field-action"><button type="submit">Subscribe</button></div>
</form>
<p class="muted note">{e(n.get('note', ''))}</p>"""
        return f"""<section id="subscribe" tabindex="-1" aria-labelledby="subscribe-heading">
<div class="wrap">
<h2 id="subscribe-heading">Get updates</h2>
{('<p class="lede-small">Get new resources by email, as a daily or weekly digest.</p>' + form) if form else ''}
<p>{'Prefer a feed reader? ' if form else 'Follow new additions in a feed reader: '}<a href="{prefix}feed-daily.xml">daily digest</a>, <a href="{prefix}feed-weekly.xml">weekly digest</a>, or <a href="{prefix}feed.xml">every new resource</a> (Atom).</p>
</div>
</section>"""

    # ------------------------------------------------------------------ home
    def resource_row(self, r, prefix):
        topics = " ".join(r["topics"])
        names = " ".join(self.topics[t]["name"] for t in r["topics"])
        note = self.notes.get(r["id"], "")
        hay = "\n".join([r["id"], r["title"], r["publisher"], r["type"], str(r["date"] or ""), names, topics, note]).lower()
        dk = dkey(r["date"])
        return (f'<tr id="r-{e(r["id"])}" data-id="{e(r["id"])}" data-title="{e(r["title"].lower())}" '
                f'data-date="{"" if dk is None else dk}" data-type="{e(r["type"])}" data-topics="{e(topics)}" data-hay="{e(hay)}">'
                f'<td class="title-col">{ext_link(r)}{self.caveat(r)}</td>'
                f'<td class="id-col">{e(r["id"])}</td><td>{e(r["publisher"])}</td>'
                f'<td><span class="chip">{e(r["type"])}</span></td>'
                f'<td class="num">{time_el(r["date"])}</td>'
                f'<td>{self.chips(r["topics"], prefix)}</td></tr>')

    def home(self):
        d, prefix = self.d, ""
        n_res, n_top = len(d["resources"]), len(d["topics"])
        title = self.doc_title()
        desc = d["summary"]
        about = {
            "@type": "Thing",
            "name": "Cement and concrete",
            "description": (
                "Binders, supplementary cementitious materials, concrete families, and engineering practice, "
                "including the preserved Type IL portland-limestone collection."
            ),
        }
        items = [{"@type": "ListItem", "position": i + 1, "name": r["title"], "url": r["url"]}
                 for i, r in enumerate(sorted_resources(d["resources"]))]
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "WebSite", "@id": self.base + "#website", "url": self.base, "name": self.name,
             "description": desc, "inLanguage": self.cfg.get("language", "en")},
            {"@type": "CollectionPage", "@id": self.base + "#page", "url": self.base, "name": self.name,
             "description": desc, "isPartOf": {"@id": self.base + "#website"}, "about": about,
             "datePublished": self.first_date, "dateModified": d["lastUpdated"],
             "inLanguage": self.cfg.get("language", "en"),
             "mainEntity": {"@type": "ItemList", "numberOfItems": n_res, "itemListElement": items}}]}
        head = self.head(title=title, description=desc, canonical=self.base, prefix=prefix, jsonld=ld)

        news = "".join(
            f'<article class="news-item"><p class="news-date">{e(w["date"])}</p><div><h3>{e(w["title"])}</h3>'
            f'{"<p>" + e(w["detail"]) + "</p>" if w.get("detail") else ""}</div></article>' for w in d["whatsNew"])
        toc_parts = []
        card_parts = []
        for key, label, note, topics in self.iter_groups():
            items = "".join(f'<li><a href="#topic-{e(t["id"])}">{e(t["name"])}</a></li>' for t in topics)
            note_html = f'<p class="axis-note">{e(note)}</p>' if note else ""
            toc_parts.append(
                f'<div class="axis"><h3 class="axis-label">{e(label)}</h3>{note_html}<ol>{items}</ol></div>')
            cards = []
            for t in topics:
                tk = ""
                if t.get("takeaways"):
                    tk = self.scope_html(t, brief=True) + '<ul class="takeaways">' + "".join(f"<li>{e(x)}</li>" for x in t["takeaways"]) + "</ul>"
                cnt = len(t.get("resourceIds") or [])
                coll = ' data-collection="type-il"' if t["id"] in TYPE_IL_TOPICS else ""
                if cnt == 0:
                    more = (f'<p class="more"><a href="{e(self.tlink(t["id"], prefix))}">'
                            f'Coverage gap — no dedicated source indexed yet</a></p>')
                else:
                    more = (f'<p class="more"><a href="{e(self.tlink(t["id"], prefix))}">'
                            f'All {cnt} resource{"s" if cnt != 1 else ""} on this topic</a></p>')
                cards.append(
                    f'<article class="topic" id="topic-{e(t["id"])}"{coll} tabindex="-1">'
                    f'<h4 class="topic-name"><a href="{e(self.tlink(t["id"], prefix))}">{e(t["name"])}</a></h4>{tk}'
                    f'{more}</article>')
            card_parts.append(
                f'<section class="axis" id="axis-{e(key)}" aria-labelledby="axis-{e(key)}-label">'
                f'<h3 class="axis-label" id="axis-{e(key)}-label">{e(label)}</h3>{note_html}{"".join(cards)}</section>')
        toc = "".join(toc_parts)
        issues = "".join(f"<li>{e(x)}</li>" for x in d["keyIssues"])
        gaps = "".join(f"<li>{e(x)}</li>" for x in d["gaps"])
        log = "".join(f'<li>{time_el(c["date"], True)}<span>{e(c["entry"])}</span></li>' for c in d["changeLog"])
        topic_opts = self.topic_options()
        type_opts = "".join(f'<option value="{e(x)}">{e(x)}</option>' for x in sorted({r["type"] for r in d["resources"]}, key=str.lower))
        rows = "".join(self.resource_row(r, prefix) for r in sorted_resources(d["resources"]))

        return head + f"""<body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead" id="top">
<div class="wrap">
<h1 id="page-title">{e(d['title'])}</h1>
<p id="summary" class="lede">{e(d['summary'])}</p>
<p id="summary-text" class="overview">{e(d['summaryText'])}</p>
<p id="meta" class="meta-line">Last updated {time_el(d['lastUpdated'], True)} · {n_top} topics · {n_res} resources · <a href="#subscribe">Get updates</a></p>
</div>
</header>
<nav class="site-nav" id="section-nav" aria-label="Sections">
<div class="wrap">
<a href="#whats-new">What's new</a>
<a href="#topics">Topics</a>
<a href="#issues">Key issues</a>
<a href="#resources">Resources</a>
<a href="#gaps">Research gaps</a>
<a href="#changelog">Change log</a>
<a href="#subscribe">Get updates</a>
</div>
</nav>
<main id="main">
<div id="content">
<section id="whats-new" tabindex="-1" aria-labelledby="whats-new-heading"><div class="wrap"><h2 id="whats-new-heading">What's new</h2><div id="whats-new-list">{news}</div></div></section>
<section id="topics" tabindex="-1" aria-labelledby="topics-heading"><div class="wrap"><h2 id="topics-heading">Topics</h2>
<nav id="topic-toc" class="toc" aria-label="Topics">{toc}</nav>
<div id="topic-list">{''.join(card_parts)}</div></div></section>
<section id="issues" tabindex="-1" aria-labelledby="issues-heading"><div class="wrap"><h2 id="issues-heading">Key issues</h2><p class="scope-note">{e(ISSUES_NOTE)}</p><ul id="issue-list" class="plain-list">{issues}</ul></div></section>
<section id="resources" tabindex="-1" aria-labelledby="resources-heading"><div class="wrap">
<h2 id="resources-heading">Resources</h2>
<p id="evidence-note" class="evidence-note">{e(EVIDENCE_NOTE)}</p>
<form id="resource-filters" role="search" aria-label="Filter resources" hidden>
<div class="field grow"><label for="q">Search</label><input id="q" name="q" type="search" placeholder="Search the Cement &amp; Concrete Index" autocomplete="off"></div>
<div class="field"><label for="topic-filter">Topic</label><select id="topic-filter" name="topic"><option value="">All topics</option>{topic_opts}</select></div>
<div class="field"><label for="type-filter">Type</label><select id="type-filter" name="type"><option value="">All types</option>{type_opts}</select></div>
<div class="field"><label for="sort">Sort</label><select id="sort" name="sort"><option value="date-desc">Date, newest</option><option value="date-asc">Date, oldest</option><option value="title-asc">Title, A–Z</option><option value="title-desc">Title, Z–A</option></select></div>
<div class="field field-action"><button type="button" id="clear" disabled>Clear filters</button></div>
</form>
<p id="resource-count" class="count" aria-live="polite">Showing {n_res} resources</p>
<p class="scroll-hint">Scroll sideways to see every column.</p>
<div class="table-scroll" tabindex="0" role="region" aria-label="Resource table, scroll horizontally for more columns">
<table id="resource-table">
<caption class="sr-only">Master list of resources. Sortable by date and title.</caption>
<thead><tr>
<th scope="col" class="title-head" id="th-title" aria-sort="none">Title</th>
<th scope="col">ID</th><th scope="col">Publisher</th><th scope="col">Type</th>
<th scope="col" id="th-date" aria-sort="descending">Date</th>
<th scope="col">Topics</th>
</tr></thead>
<tbody id="resource-body">{rows}<tr id="empty-row" hidden><td class="empty" colspan="6">No resources match these filters.</td></tr></tbody>
</table>
</div>
</div></section>
<section id="gaps" tabindex="-1" aria-labelledby="gaps-heading"><div class="wrap"><h2 id="gaps-heading">Research gaps</h2><ul id="gap-list" class="plain-list">{gaps}</ul></div></section>
<section id="changelog" tabindex="-1" aria-labelledby="changelog-heading"><div class="wrap"><h2 id="changelog-heading">Change log</h2><ol id="change-log" class="log">{log}</ol></div></section>
{self.subscribe(prefix)}
</div>
</main>
{self.footer(prefix)}<script src="js/app.js" defer></script>
</body>
</html>
"""

    # ------------------------------------------------------------------ topic pages
    def topic_page(self, t):
        d, prefix = self.d, "../../"
        url = f"{self.base}topics/{t['id']}/"
        res = [self.res[i] for i in t.get("resourceIds") or []]
        cnt = len(res)
        desc = self.topic_desc(t, cnt)
        title = self.doc_title(t["name"])
        related = []
        for o in d["topics"]:
            if o["id"] != t["id"]:
                shared = len(set(o["resourceIds"]) & set(t["resourceIds"]))
                if shared:
                    related.append((shared, o))
        related = [o for _, o in sorted(related, key=lambda x: (-x[0], x[1]["name"]))[:6]]
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": self.name, "item": self.base},
                {"@type": "ListItem", "position": 2, "name": t["name"], "item": url}]},
            {"@type": "CollectionPage", "@id": url + "#page", "url": url, "name": title, "description": desc,
             "isPartOf": {"@id": self.base + "#website"}, "dateModified": d["lastUpdated"],
             "inLanguage": self.cfg.get("language", "en"),
             "mainEntity": {"@type": "ItemList", "numberOfItems": cnt, "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "name": r["title"], "url": r["url"]} for i, r in enumerate(res)]}}]}
        head = self.head(title=title, description=desc, canonical=url, prefix=prefix, jsonld=ld)
        tk = ""
        if t.get("takeaways"):
            tk = self.scope_html(t) + '<ul class="takeaways">' + "".join(f"<li>{e(x)}</li>" for x in t["takeaways"]) + "</ul>"
        if cnt == 0:
            items = ('<li class="gap-callout">Coverage gap. No dedicated source is indexed for this topic yet. '
                     'This is a limit of the index, not a finding that no literature exists.</li>')
        else:
            items = "".join(
                f'<li id="r-{e(r["id"])}">{ext_link(r)}{self.caveat(r)}<p class="meta"><span>{e(r["id"])}</span><span>{e(r["publisher"])}</span>'
                f'<span class="chip">{e(r["type"])}</span>{time_el(r["date"])}</p>{self.chips(r["topics"], prefix)}</li>'
                for r in sorted_resources(res))
        rel = ""
        if related:
            rel = ('<h2 class="h3like">Related topics</h2><div class="chips">' + "".join(
                f'<a class="chip" href="{e(self.tlink(o["id"], "../../"))}">{e(o["name"])}</a>' for o in related) + "</div>")
        return head + f"""<body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead slim" id="top">
<div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="{prefix}">{e(self.name)}</a> <span aria-hidden="true">›</span> <span>{e(t['name'])}</span></nav>
<h1>{e(t['name'])}</h1>
<p class="meta-line">{'Coverage gap · no dedicated source indexed yet' if cnt == 0 else str(cnt) + (' resource' if cnt == 1 else ' resources')} · Last updated {time_el(d['lastUpdated'], True)}</p>
</div>
</header>
<main id="main"><div id="content">
<section aria-labelledby="takeaways-heading"><div class="wrap">
{('<h2 id="takeaways-heading">Key points</h2>' + tk) if tk else '<h2 id="takeaways-heading" class="sr-only">Key points</h2>'}
<h2 class="h3like">Resources</h2>
<ul class="linked-resources">{items}</ul>
{rel}
<p class="more"><a href="{prefix}#resources">Search and filter all {len(d['resources'])} resources</a> · <a href="{prefix}#subscribe">Get updates by email or feed</a></p>
</div></section>
</div></main>
{self.footer(prefix)}</body>
</html>
"""

    # ------------------------------------------------------------------ sitemap, llms.txt
    def sitemap(self):
        d = self.d
        urls = [(self.base, d["lastUpdated"])]
        for t in d["topics"]:
            added = [self.res[i]["added"] for i in (t.get("resourceIds") or []) if self.res[i].get("added")]
            last = max(added + [d["changeLog"][0]["date"] if d["changeLog"] else d["lastUpdated"]])
            urls.append((f"{self.base}topics/{t['id']}/", last))
        body = "".join(f"<url><loc>{xesc(u)}</loc><lastmod>{m}</lastmod></url>" for u, m in urls)
        return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                + body + "</urlset>\n"), [u for u, _ in urls]

    def llms(self):
        d = self.d
        lines = [f"# {d['title']}", "", f"> {d['summary']}", "", d["summaryText"], "",
                 "Coverage is foundational, not exhaustive. An empty topic is a documented gap, not proof that no literature exists. "
                 "Unknown publication dates stay blank. Topic membership is the union of `topics` on a resource and `resourceIds` on a topic, "
                 "so preserved records can belong to a newer topic through `resourceIds` alone.",
                 "", "## Topics", ""]
        for t in d["topics"]:
            n = len(t.get("resourceIds") or [])
            if n:
                lines.append(f"- [{t['name']}]({self.base}topics/{t['id']}/): {n} resources")
            else:
                lines.append(f"- [{t['name']}]({self.base}topics/{t['id']}/): coverage gap, no dedicated source indexed yet")
        lines += ["", "## Data and feeds", "",
                  f"- [Full index as JSON]({self.base}data/site-data.json)",
                  f"- [Source notes as JSON]({self.base}data/resource-notes.json)",
                  f"- [Daily digest feed]({self.base}feed-daily.xml)",
                  f"- [Weekly digest feed]({self.base}feed-weekly.xml)", ""]
        return "\n".join(lines)

    # ------------------------------------------------------------------ feeds
    def digest_body(self, resources, notes):
        groups = collections.OrderedDict()
        for r in sorted(resources, key=rid_num):
            groups.setdefault(self.topics[r["topics"][0]]["name"], []).append(r)
        out = [f"<p>{len(resources)} new resource{'s' if len(resources) != 1 else ''} in the {e(self.name)}.</p>"]
        for name, rs in groups.items():
            out.append(f"<h3>{e(name)}</h3><ul>")
            for r in rs:
                bits = [r["publisher"], r["type"]] + ([r["date"]] if r["date"] else [])
                out.append(f'<li><a href="{e(r["url"])}">{e(r["title"])}</a> ({e(", ".join(bits))})</li>')
            out.append("</ul>")
        for n in notes:
            out.append(f"<p><em>Index note:</em> {e(n)}</p>")
        out.append(f'<p><a href="{e(self.base)}">Browse the full index</a></p>')
        return "".join(out)

    def atom(self, title, fid, self_url, entries, updated):
        out = ['<?xml version="1.0" encoding="utf-8"?>', '<feed xmlns="http://www.w3.org/2005/Atom">',
               f"<title>{xesc(title)}</title>", f"<id>{xesc(fid)}</id>",
               f'<link rel="self" type="application/atom+xml" href="{xesc(self_url)}"/>',
               f'<link rel="alternate" type="text/html" href="{xesc(self.base)}"/>',
               f"<updated>{updated}</updated>", f"<subtitle>{xesc(self.d['summary'])}</subtitle>"]
        for en in entries:
            out.append(f"<entry><id>{xesc(en['id'])}</id><title>{xesc(en['title'])}</title>"
                       f'<link rel="alternate" type="text/html" href="{xesc(en["link"])}"/>'
                       f"<published>{en['updated']}</published><updated>{en['updated']}</updated>"
                       f'<content type="html">{xesc(en["html"])}</content></entry>')
        out.append("</feed>\n")
        return "\n".join(out)

    def feeds(self):
        d, today = self.d, self.today
        by_day = collections.defaultdict(list)
        for r in d["resources"]:
            by_day[r["added"]].append(r)
        notes_by_day = collections.defaultdict(list)
        for c in d["changeLog"]:
            notes_by_day[c["date"]].append(c["entry"])

        def iso_week_key(day):
            y, w, _ = dt.date.fromisoformat(day).isocalendar()
            return (y, w)

        # daily: completed days with additions
        days = sorted(x for x in by_day if dt.date.fromisoformat(x) < today)
        daily = [{"id": f"tag:type1l-index,{x}:daily", "title": f"{long_date(x)}: {len(by_day[x])} new resource{'s' if len(by_day[x]) != 1 else ''}",
                  "link": self.base, "updated": f"{x}T23:59:59Z",
                  "html": self.digest_body(by_day[x], notes_by_day.get(x, []))} for x in reversed(days)]
        # weekly: completed ISO weeks (Monday..Sunday, week end strictly before today)
        weeks = collections.OrderedDict()
        for x in sorted(by_day):
            weeks.setdefault(iso_week_key(x), []).append(x)
        weekly = []
        for (y, w), xs in reversed(list(weeks.items())):
            monday = dt.date.fromisocalendar(y, w, 1)
            sunday = monday + dt.timedelta(days=6)
            if sunday >= today:
                continue
            rs = [r for x in xs for r in by_day[x]]
            notes = [n for x in xs for n in notes_by_day.get(x, [])]
            weekly.append({"id": f"tag:type1l-index,{y}-W{w:02d}:weekly",
                           "title": f"Week of {long_date(monday.isoformat())}: {len(rs)} new resource{'s' if len(rs) != 1 else ''}",
                           "link": self.base, "updated": f"{sunday.isoformat()}T23:59:59Z",
                           "html": self.digest_body(rs, notes)})
        newest = sorted(d["resources"], key=lambda r: (r["added"], rid_num(r)), reverse=True)[:100]
        latest = [{"id": f"{self.base}#r-{r['id']}", "title": r["title"], "link": f"{self.base}#r-{r['id']}",
                   "updated": f"{r['added']}T00:00:00Z",
                   "html": f'<p><a href="{e(r["url"])}">{e(r["title"])}</a></p><p>{e(r["publisher"])} · {e(r["type"])}'
                           f'{" · " + e(r["date"]) if r["date"] else ""}</p>'} for r in newest]
        stamp = f"{d['lastUpdated']}T00:00:00Z"
        return {
            "feed-daily.xml": self.atom(f"{self.name}: daily digest", self.base + "feed-daily.xml", self.base + "feed-daily.xml", daily, daily[0]["updated"] if daily else stamp),
            "feed-weekly.xml": self.atom(f"{self.name}: weekly digest", self.base + "feed-weekly.xml", self.base + "feed-weekly.xml", weekly, weekly[0]["updated"] if weekly else stamp),
            "feed.xml": self.atom(f"{self.name}: newest resources", self.base + "feed.xml", self.base + "feed.xml", latest, stamp),
        }


# ----------------------------------------------------------------------------- main
def write(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


def indexnow(cfg, urls):
    base = cfg["baseUrl"]
    host = re.match(r"https://([^/]+)/", base).group(1)
    key = cfg["indexNowKey"]
    payload = json.dumps({"host": host, "key": key, "keyLocation": f"{base}{key}.txt", "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=payload,
                                 headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as f:
            print(f"IndexNow: HTTP {f.status} for {len(urls)} URLs")
    except Exception as ex:  # a failed ping must not fail the build
        print(f"IndexNow: not accepted ({ex})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--today")
    ap.add_argument("--indexnow", action="store_true")
    a = ap.parse_args()
    d, cfg = load()
    notes = load_notes()
    errs = validate(d, cfg, notes)
    if errs:
        print("VALIDATION FAILED:")
        for x in errs:
            print("  -", x)
        return 1
    undated = [r["id"] for r in d["resources"] if not r["date"]]
    print(f"valid: {len(d['resources'])} resources, {len(d['topics'])} topics, {len(undated)} undated")
    if a.validate:
        return 0
    today = dt.date.fromisoformat(a.today) if a.today else dt.datetime.now(dt.timezone.utc).date()
    s = Site(d, cfg, today, notes)
    write("index.html", s.home())
    topics_dir = ROOT / "topics"
    if topics_dir.exists():
        for child in topics_dir.iterdir():
            if child.is_dir() and child.name not in s.topics:
                shutil.rmtree(child)
    for t in d["topics"]:
        write(f"topics/{t['id']}/index.html", s.topic_page(t))
    sm, urls = s.sitemap()
    write("sitemap.xml", sm)
    write("llms.txt", s.llms())
    for name, text in s.feeds().items():
        write(name, text)
    save_added_dates(d["resources"])
    write(f"{cfg['indexNowKey']}.txt", cfg["indexNowKey"])
    print(f"built index.html, {len(d['topics'])} topic pages, sitemap.xml, llms.txt, 3 feeds (as of {today})")
    if a.indexnow:
        indexnow(cfg, urls)
    return 0


if __name__ == "__main__":
    sys.exit(main())
