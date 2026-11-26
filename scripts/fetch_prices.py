#!/usr/bin/env python3
"""Refresh API-backed price observations and merge them with curated rows.

Stdlib only. Reads research/prices-curated.json (DOT bid prices, ENR quotes,
and Mineral Commodity Summaries national figures opened by hand). Fetches:

  * BLS public API, https://api.bls.gov/publicAPI/v2/timeseries/data/
  * FRED CSV republishing of the same BLS indexes, annual means for 1990-2016
  * USGS Minerals Yearbook workbooks (cement, crushed stone, construction sand
    and gravel, iron and steel slag)
  * FHWA NHCCI CSV on data.transportation.gov

Writes data/prices.json. Existing observation ids are kept. New rows get the
next P number. A failed download leaves that source out and exits 1 after
writing everything else that succeeded.

  python3 scripts/fetch_prices.py
  python3 scripts/fetch_prices.py --dry-run
"""
import json
import re
import sys
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURATED = ROOT / "research" / "prices-curated.json"
OUT = ROOT / "data" / "prices.json"
UA = "type1l-index-research/1.0 (public data; https://xxdccole.github.io/Type1L-Index/)"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
TODAY = datetime.now(timezone.utc).date().isoformat()

# BLS base dates read from data.bls.gov on 2026-11-26. YYYY00 means the year.
BLS_SERIES = [
    # series id, material, subcategory, geography, level, base
    ("WPU1322", "Cement", "hydraulic", "US", "national", "198200"),
    ("WPU1321", "Aggregates", "construction sand, gravel, and crushed stone", "US", "national", "198200"),
    ("WPU13210120", "Construction sand and gravel", "run of pit or bank", "US", "national", "201112"),
    ("WPU13210122", "Crushed stone", "crushed and broken limestone", "US", "national", "201112"),
    ("WPU132101201", "Construction sand and gravel", "run of pit or bank", "Northeast", "region", "201212"),
    ("WPU132101202", "Construction sand and gravel", "run of pit or bank", "Midwest", "region", "201212"),
    ("WPU132101204", "Construction sand and gravel", "run of pit or bank", "West", "region", "201212"),
    ("WPU133", "Concrete products", "concrete products", "US", "national", "198200"),
    ("WPU1331", "Concrete products", "concrete block and brick", "US", "national", "198200"),
    ("WPU1333", "Ready-mix concrete", "ready-mix concrete", "US", "national", "198200"),
    ("WPU1334", "Concrete products", "precast", "US", "national", "198200"),
    ("WPU1335", "Concrete products", "prestressed", "US", "national", "198200"),
    ("WPU13330101A", "Ready-mix concrete", "ready-mix concrete", "Northeast", "region", "201212"),
    ("WPU13330101B", "Ready-mix concrete", "ready-mix concrete", "Midwest", "region", "201212"),
    ("WPU13330101C", "Ready-mix concrete", "ready-mix concrete", "South", "region", "201212"),
    ("WPU13330101D", "Ready-mix concrete", "ready-mix concrete", "West", "region", "201212"),
    ("WPU139902094", "Aggregates", "treated lightweight aggregate and crushed slag", "US", "national", "201412"),
    ("WPU13990312", "Concrete products", "dry-mixed concrete, mortar, and cement premixes", "US", "national", "201112"),
    ("PCU327310327310", "Cement", "cement manufacturing", "US", "national", "198206"),
    ("PCU327320327320", "Ready-mix concrete", "ready-mix concrete manufacturing", "US", "national", "198106"),
    ("PCU327331327331", "Concrete products", "concrete block and brick manufacturing", "US", "national", "198106"),
    ("PCU327390327390", "Concrete products", "other concrete product manufacturing", "US", "national", "200312"),
    ("PCU212321212321", "Construction sand and gravel", "construction sand and gravel mining", "US", "national", "198206"),
    ("PCU212312212312", "Crushed stone", "crushed and broken limestone mining", "US", "national", "198312"),
]
BLS_TITLES = {
    "WPU1322": "PPI commodity index, cement, hydraulic",
    "WPU1321": "PPI commodity index, construction sand, gravel and crushed stone",
    "WPU13210120": "PPI commodity index, construction sand and gravel",
    "WPU13210122": "PPI commodity index, crushed and broken limestone",
    "WPU132101201": "PPI commodity index, construction sand and gravel, Northeast",
    "WPU132101202": "PPI commodity index, construction sand and gravel, Midwest",
    "WPU132101204": "PPI commodity index, construction sand and gravel, West",
    "WPU133": "PPI commodity index, concrete products",
    "WPU1331": "PPI commodity index, concrete block and brick",
    "WPU1333": "PPI commodity index, ready-mix concrete",
    "WPU1334": "PPI commodity index, precast concrete products",
    "WPU1335": "PPI commodity index, prestressed concrete products",
    "WPU13330101A": "PPI commodity index, ready-mix concrete, Northeast",
    "WPU13330101B": "PPI commodity index, ready-mix concrete, Midwest",
    "WPU13330101C": "PPI commodity index, ready-mix concrete, South",
    "WPU13330101D": "PPI commodity index, ready-mix concrete, West",
    "WPU139902094": "PPI commodity index, treated lightweight aggregate and crushed slag",
    "WPU13990312": "PPI commodity index, dry-mixed concrete materials",
    "PCU327310327310": "PPI industry index, cement manufacturing",
    "PCU327320327320": "PPI industry index, ready-mix concrete manufacturing",
    "PCU327331327331": "PPI industry index, concrete block and brick manufacturing",
    "PCU327390327390": "PPI industry index, other concrete product manufacturing",
    "PCU212321212321": "PPI industry index, construction sand and gravel mining",
    "PCU212312212312": "PPI industry index, crushed and broken limestone mining",
}
# South construction-sand series WPU132101203 returned no observations for 2024-2026
# on 2026-11-26, so it is not requested.
FRED_ANNUAL = ["WPU1322", "WPU1321", "WPU1333", "WPU133", "PCU327310327310", "PCU327320327320"]
USGS = {
    "cement": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/myb1-2023-cemen-ERT.xlsx",
    "stone": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/myb1-2023-stonec-ert.xlsx",
    "sand": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/myb1-2023-sandc-ert.xlsx",
    "slag": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/myb1-2021-fesla-ert.xlsx",
}
NHCCI_URL = "https://data.transportation.gov/api/views/r94d-n4f9/rows.csv?accessType=DOWNLOAD"
STATES = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
    "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
    "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee",
    "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming", "Puerto Rico",
}


def fetch(url, data=None, headers=None, timeout=90):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def base_label(code):
    year, month = code[:4], code[4:]
    if month == "00":
        return f"{year}=100"
    return f"{year}-{month}=100"


def num(text):
    if text is None:
        return None
    s = str(text).strip().replace(",", "")
    if not s or s in {"W", "w", "--", "-", "NA", "n/a"}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def clean_num(value, digits):
    value = round(float(value), digits)
    if abs(value - round(value)) < 10 ** (-(digits + 2)):
        return int(round(value))
    return value


def place(name):
    name = name.strip()
    while True:
        nxt = re.sub(r"[\s,]*\d+$", "", name).strip(" ,")
        if nxt == name:
            break
        name = nxt
    low = name.lower()
    if low in {"total", "united states", "total or average", "grand total", "u.s. total or average"} or low.startswith("total"):
        return "US", "national", ""
    if low.startswith("importer"):
        return "US importers", "national", ""
    if low == "other":
        return "Other", "region", ""
    if name in STATES:
        return name, "state", name
    return name, "district", ""


def obs(**k):
    k.setdefault("accessed", TODAY)
    k.setdefault("note", "")
    k.setdefault("seriesId", "")
    k.setdefault("state", "")
    k.setdefault("preliminary", False)
    k["value"] = clean_num(k["value"], k.pop("digits", 3))
    return k


def key_of(o):
    return "|".join([
        o.get("publisher") or "",
        o.get("seriesId") or "",
        o.get("period") or "",
        o.get("geography") or "",
        o.get("material") or "",
        o.get("subcategory") or "",
        o.get("kind") or "",
        o.get("currencyOrBase") or "",
        o.get("description") or "",
    ])


# ---------------------------------------------------------------- BLS and FRED
def fetch_bls():
    meta = {s[0]: s for s in BLS_SERIES}
    payload = json.dumps({
        "seriesid": [s[0] for s in BLS_SERIES],
        "startyear": "2017",
        "endyear": "2026",
    }).encode()
    raw = json.loads(fetch(
        "https://api.bls.gov/publicAPI/v2/timeseries/data/",
        data=payload,
        headers={"Content-Type": "application/json"},
    ))
    if raw.get("status") != "REQUEST_SUCCEEDED":
        raise RuntimeError(f"BLS API status {raw.get('status')}: {raw.get('message')}")
    rows = []
    for series in raw.get("Results", {}).get("series", []):
        sid = series.get("seriesID")
        spec = meta.get(sid)
        if not spec or not series.get("data"):
            continue
        _, material, sub, geo, level, base = spec
        for pt in series["data"]:
            if not str(pt.get("period", "")).startswith("M"):
                continue
            value = num(pt.get("value"))
            if value is None:
                continue
            month = int(pt["period"][1:])
            period = f"{pt['year']}-{month:02d}"
            prelim = any((f or {}).get("code") == "P" for f in pt.get("footnotes") or [])
            note = "Not seasonally adjusted. An index, not a dollar price."
            if prelim:
                note += " Preliminary. BLS may revise it."
            rows.append(obs(
                material=material, subcategory=sub,
                description=BLS_TITLES[sid],
                value=value, digits=3, unit="index", currencyOrBase=base_label(base),
                kind="index", period=period, geography=geo, geographyLevel=level,
                sourceTitle=BLS_TITLES[sid],
                publisher="U.S. Bureau of Labor Statistics",
                url=f"https://data.bls.gov/timeseries/{sid}",
                accessLevel="public API",
                note=note, seriesId=sid, preliminary=prelim,
            ))
    if len(rows) < 100:
        raise RuntimeError(f"BLS returned only {len(rows)} monthly points")
    return rows


def fetch_fred_annual():
    """Annual means of BLS indexes as republished by FRED, for years before the BLS pull."""
    meta = {s[0]: s for s in BLS_SERIES}
    rows = []
    for sid in FRED_ANNUAL:
        _, material, sub, geo, level, base = meta[sid]
        text = fetch(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}").decode("utf-8")
        by_year = defaultdict(list)
        for line in text.splitlines()[1:]:
            if "," not in line:
                continue
            day, val = line.split(",", 1)
            value = num(val)
            if value is None or len(day) < 7:
                continue
            year = int(day[:4])
            if 1990 <= year <= 2016:
                by_year[year].append(value)
        for year, vals in sorted(by_year.items()):
            rows.append(obs(
                material=material, subcategory=sub,
                description=BLS_TITLES[sid] + f", unweighted mean of {len(vals)} monthly values",
                value=sum(vals) / len(vals), digits=3, unit="index",
                currencyOrBase=base_label(base), kind="index", period=str(year),
                geography=geo, geographyLevel=level,
                sourceTitle=BLS_TITLES[sid] + " (FRED reprint of the BLS series)",
                publisher="Federal Reserve Bank of St. Louis",
                url=f"https://fred.stlouisfed.org/series/{sid}",
                accessLevel="public CSV download",
                note="FRED republishes the BLS producer price index. This row is the unweighted mean of the monthly values FRED published for that year, for years before the monthly rows taken from the BLS API. Not a dollar price.",
                seriesId=sid + "-FRED-ANNUAL",
            ))
    return rows


# ---------------------------------------------------------------- USGS workbooks
def xlsx_sheets(blob):
    z = zipfile.ZipFile(BytesIO(blob))
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", NS):
            ss.append("".join(t.text or "" for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
    sheets = {}
    for s in wb.findall("m:sheets/m:sheet", NS):
        target = rid[s.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]]
        if not target.startswith("xl/"):
            target = "xl/" + target.lstrip("/")
        sheets[s.attrib["name"]] = target

    def cells(name):
        root = ET.fromstring(z.read(sheets[name]))
        table = {}
        for c in root.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"):
            ref = c.attrib.get("r")
            if not ref:
                continue
            t = c.attrib.get("t")
            v = c.find("m:v", NS)
            if t == "s" and v is not None and v.text:
                val = ss[int(v.text)]
            elif v is not None:
                val = v.text or ""
            else:
                val = ""
            table[ref] = val
        return table

    return cells


def col_row(ref):
    col = "".join(ch for ch in ref if ch.isalpha())
    row = int("".join(ch for ch in ref if ch.isdigit()))
    return col, row


def rows_by_label(cells):
    """Map column A text to {col: value} for that row."""
    found = {}
    for ref, val in cells.items():
        col, row = col_row(ref)
        if col == "A" and val:
            found[val] = {}
    # second pass
    wanted_rows = {}
    for ref, val in cells.items():
        col, row = col_row(ref)
        if col == "A" and val:
            wanted_rows[row] = val
    out = {label: {} for label in wanted_rows.values()}
    for ref, val in cells.items():
        col, row = col_row(ref)
        if row in wanted_rows:
            out[wanted_rows[row]][col] = val
    return out


def state_unit_rows(cells, years, material, subcategory, source, url, note):
    """years is {year: column letter of the printed unit value}."""
    rows = []
    labels = {}
    for ref, val in cells.items():
        col, row = col_row(ref)
        if col == "A" and val and row >= 8:
            labels[row] = val.strip()
    for row, label in sorted(labels.items()):
        if label.lower().startswith("state") or label.lower().startswith("table"):
            continue
        geo, level, state = place(label)
        extra = ""
        if geo == "Other":
            extra = " The source groups some states as Other and does not publish a separate unit value for each of them."
        for year, col in years.items():
            value = num(cells.get(f"{col}{row}"))
            if value is None:
                continue
            rows.append(obs(
                material=material, subcategory=subcategory,
                description=f"Printed unit value, {year}.",
                value=value, digits=2, unit="USD per metric ton", currencyOrBase="USD",
                kind="unit value", period=str(year), geography=geo, geographyLevel=level, state=state,
                sourceTitle=source, publisher="U.S. Geological Survey", url=url,
                accessLevel="public workbook",
                note=note + extra, seriesId=f"USGS-{material[:4].upper()}-{year}",
            ))
    return rows


def fetch_usgs():
    rows = []
    cement = xlsx_sheets(fetch(USGS["cement"]))
    stone = xlsx_sheets(fetch(USGS["stone"]))
    sand = xlsx_sheets(fetch(USGS["sand"]))
    slag = xlsx_sheets(fetch(USGS["slag"]))
    note = ("Mine-gate or mill-gate unit value printed by USGS. Not a delivered price and not a bid price. "
            "Withheld state totals (W) are omitted. A trailing footnote digit in the source label is not part of the place name.")
    rows.extend(state_unit_rows(
        cement("T11"), {2022: "G", 2023: "N"}, "Cement", "portland and blended, by shipping district",
        "Minerals Yearbook 2023, Cement, Table 11, portland and blended cement shipped by district",
        USGS["cement"], note + " Districts follow the reporting mills, not necessarily the state where the cement was sold.",
    ))
    rows.extend(state_unit_rows(
        stone("T4"), {2022: "G", 2023: "M"}, "Crushed stone", "sold or used by producers",
        "Minerals Yearbook 2023, Crushed Stone, Table 4, by state and territory",
        USGS["stone"], note,
    ))
    rows.extend(state_unit_rows(
        sand("T3"), {2022: "G", 2023: "M"}, "Construction sand and gravel", "sold or used by producers",
        "Minerals Yearbook 2023, Construction Sand and Gravel, Table 3, by state",
        USGS["sand"], note,
    ))
    # National cement average value, 2019-2020, from yearbook Table 1. Later years are the MCS rows.
    t1 = rows_by_label(cement("T1"))
    avg = None
    for label, cols in t1.items():
        if label.startswith("Average value"):
            avg = cols
            break
    if avg:
        # Header years sit on the row above the quantity block. Read D/F/H/J/L if those are the year cells.
        # Confirmed layout on the 2023 workbook: 2019 in D, then every other column.
        year_cols = [("2019", "D"), ("2020", "F"), ("2021", "H"), ("2022", "J"), ("2023", "L")]
        for year, col in year_cols:
            if year >= "2021":
                continue  # MCS curated rows cover 2021-2025
            value = num(avg.get(col))
            if value is None:
                continue
            rows.append(obs(
                material="Cement", subcategory="portland, blended, and masonry",
                description="Average value of shipments from mills and terminals.",
                value=value, digits=2, unit="USD per metric ton", currencyOrBase="USD",
                kind="unit value", period=year, geography="US", geographyLevel="national",
                sourceTitle="Minerals Yearbook 2023, Cement, Table 1, salient statistics",
                publisher="U.S. Geological Survey", url=USGS["cement"],
                accessLevel="public workbook",
                note="Mill shipment average value. 2021-2025 of the same series are stored from Mineral Commodity Summaries 2026.",
                seriesId="USGS-CEMENT-AVG",
            ))
    # Slag unit values calculated from printed quantity and value. The yearbook does not print a unit-value column.
    s1 = rows_by_label(slag("T1"))
    pairs = [
        ("Air-cooled", "air-cooled blast-furnace slag"),
        ("Granulated", "granulated blast-furnace slag"),
        ("Steel furnace slag", "steel furnace slag"),
    ]
    year_cols = [("2017", "C"), ("2018", "E"), ("2019", "G"), ("2020", "I"), ("2021", "K")]
    # Quantity block is the first occurrence of each label; value block is the second.
    # rows_by_label keeps only the last column-A label, so air-cooled quantity is overwritten by value.
    # Read by scanning column A order instead.
    ordered = []
    for ref, val in slag("T1").items():
        col, row = col_row(ref)
        if col == "A" and val:
            ordered.append((row, val.strip(), {}))
    ordered.sort()
    grid = {row: bucket for row, _, bucket in ordered}
    for ref, val in slag("T1").items():
        col, row = col_row(ref)
        if row in grid:
            grid[row][col] = val
    labels_in_order = [(row, label) for row, label, _ in ordered]
    # Split at the Value:e row.
    value_at = next(i for i, (_, label) in enumerate(labels_in_order) if label.startswith("Value"))
    qty = {label: grid[row] for row, label in labels_in_order[:value_at]}
    valmap = {label: grid[row] for row, label in labels_in_order[value_at:]}
    for label, sub in pairs:
        for year, col in year_cols:
            q = num((qty.get(label) or {}).get(col))
            v = num((valmap.get(label) or {}).get(col))
            if not q or v is None:
                continue
            rows.append(obs(
                material="Slag", subcategory=sub,
                description=f"Unit value calculated from printed sales quantity and value, {year}. Both were estimated by USGS.",
                value=v / q, digits=2, unit="USD per metric ton", currencyOrBase="USD",
                kind="unit value", period=year, geography="US", geographyLevel="national",
                sourceTitle="Minerals Yearbook 2021, Iron and Steel Slag, Table 1",
                publisher="U.S. Geological Survey", url=USGS["slag"],
                accessLevel="public workbook",
                note="Calculated here as value divided by quantity. The table prints thousand metric tons and thousand dollars, so the ratio is dollars per metric ton. USGS marks the sales figures estimated. This is not a printed unit-value cell. Granulated slag is the feedstock for slag cement; the table does not price ground granulated slag separately.",
                seriesId="USGS-SLAG-CALC-" + sub.split()[0].upper(),
            ))
    return rows


def fetch_nhcci():
    text = fetch(NHCCI_URL).decode("utf-8")
    lines = text.splitlines()
    header = lines[0].split(",")
    qi, ii = header.index("quarter"), header.index("NHCCI")
    rows = []
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) <= ii or not parts[qi]:
            continue
        value = num(parts[ii])
        if value is None:
            continue
        q = parts[qi].strip()  # "2003 Q1"
        year, quarter = q.split()
        period = f"{year}-{quarter}"
        rows.append(obs(
            material="Highway construction", subcategory="NHCCI",
            description="National Highway Construction Cost Index.",
            value=value, digits=6, unit="index", currencyOrBase="2003-Q1=1",
            kind="index", period=period, geography="US", geographyLevel="national",
            sourceTitle="National Highway Construction Cost Index",
            publisher="Federal Highway Administration",
            url="https://data.transportation.gov/Highway-Statistics/NHCCI/r94d-n4f9",
            accessLevel="public CSV download",
            note="Bid-price index for highway construction, not a material price. In this file, 2003 Q1 equals 1. Component contribution columns are percent contributions to the index change and are not stored.",
            seriesId="NHCCI",
        ))
    if len(rows) < 20:
        raise RuntimeError("NHCCI file had too few quarters")
    return rows


def merge(fresh):
    existing = []
    if OUT.exists():
        existing = json.loads(OUT.read_text(encoding="utf-8"))
        if isinstance(existing, dict):
            existing = existing.get("observations") or []
    by_key = {}
    max_id = 0
    for old in existing:
        by_key[key_of(old)] = old
        m = re.fullmatch(r"P(\d+)", old.get("id") or "")
        if m:
            max_id = max(max_id, int(m.group(1)))
    merged = []
    seen = set()
    for row in fresh:
        k = key_of(row)
        if k in seen:
            continue
        seen.add(k)
        old = by_key.get(k)
        if old:
            row["id"] = old["id"]
        else:
            max_id += 1
            row["id"] = f"P{max_id}"
        merged.append(row)
    merged.sort(key=lambda r: (r["material"], r["geography"], r["period"], r["id"]))
    # Reassign first-run ids in sorted order when there was no previous file,
    # so a clean build is deterministic. Preserve ids once the file exists.
    if not existing:
        for i, row in enumerate(merged, start=1):
            row["id"] = f"P{i}"
    return merged


def main():
    dry = "--dry-run" in sys.argv
    errors = []
    fresh = json.loads(CURATED.read_text(encoding="utf-8"))
    for name, fn in (("BLS", fetch_bls), ("FRED", fetch_fred_annual), ("USGS", fetch_usgs), ("NHCCI", fetch_nhcci)):
        try:
            got = fn()
            print(f"{name}: {len(got)} observations")
            fresh.extend(got)
        except Exception as ex:
            errors.append(f"{name}: {type(ex).__name__}: {ex}")
            print(f"{name} FAILED: {ex}", file=sys.stderr)
    merged = merge(fresh)
    print(f"total {len(merged)} observations")
    if dry:
        return 1 if errors else 0
    OUT.write_text(json.dumps(merged, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
