"use strict";

/*
 * Progressive enhancement only. The page is complete HTML without this file
 * (scripts/build.py renders it). This adds search, filters, sorting and
 * shareable filter links (?q=...&topic=...&type=...&sort=...) to the resource table.
 */
(function () {
  var form = document.getElementById("resource-filters");
  var body = document.getElementById("resource-body");
  if (!form || !body) return;

  var rows = Array.prototype.slice.call(body.querySelectorAll("tr[data-id]"));
  var emptyRow = document.getElementById("empty-row");
  var qInput = document.getElementById("q");
  var topicSel = document.getElementById("topic-filter");
  var typeSel = document.getElementById("type-filter");
  var sortSel = document.getElementById("sort");
  var clearBtn = document.getElementById("clear");
  var countEl = document.getElementById("resource-count");
  var titleTh = document.getElementById("th-title");
  var dateTh = document.getElementById("th-date");
  var total = rows.length;
  var state = { q: "", topic: "", type: "", sortKey: "date", sortDir: "desc" };

  rows.forEach(function (row) {
    var date = row.getAttribute("data-date");
    row._k = {
      id: row.getAttribute("data-id"),
      title: row.getAttribute("data-title"),
      date: date === "" ? null : Number(date),
      type: row.getAttribute("data-type"),
      topics: (row.getAttribute("data-topics") || "").split(" "),
      hay: row.getAttribute("data-hay") || ""
    };
  });

  function collate(a, b) {
    return a.localeCompare(b, "en", { sensitivity: "base" });
  }

  function compare(a, b) {
    var x = a._k, y = b._k;
    if (state.sortKey === "title") {
      var t = collate(x.title, y.title);
      if (t) return state.sortDir === "asc" ? t : -t;
      return collate(x.id, y.id);
    }
    if (x.date == null && y.date == null) return collate(x.title, y.title);
    if (x.date == null) return 1;
    if (y.date == null) return -1;
    var diff = state.sortDir === "asc" ? x.date - y.date : y.date - x.date;
    return diff || collate(x.title, y.title);
  }

  function matches(row) {
    var k = row._k;
    if (state.topic && k.topics.indexOf(state.topic) === -1) return false;
    if (state.type && k.type !== state.type) return false;
    var terms = state.q.toLowerCase().trim().split(/\s+/).filter(Boolean);
    for (var i = 0; i < terms.length; i++) {
      if (k.hay.indexOf(terms[i]) === -1) return false;
    }
    return true;
  }

  function makeSortButton(th, key, label) {
    var btn = document.createElement("button");
    btn.type = "button";
    var ind = document.createElement("span");
    ind.setAttribute("aria-hidden", "true");
    btn.append(label + " ", ind);
    th.replaceChildren(btn);
    btn.addEventListener("click", function () {
      if (state.sortKey === key) {
        state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
      } else {
        state.sortKey = key;
        state.sortDir = key === "title" ? "asc" : "desc";
      }
      render();
    });
    return { btn: btn, ind: ind };
  }

  var titleCtl = makeSortButton(titleTh, "title", "Title");
  var dateCtl = makeSortButton(dateTh, "date", "Date");

  function updateSortUi() {
    sortSel.value = state.sortKey + "-" + state.sortDir;
    [[titleTh, titleCtl, "title", "Sort by title"], [dateTh, dateCtl, "date", "Sort by date"]].forEach(function (c) {
      var active = state.sortKey === c[2];
      var word = state.sortDir === "asc" ? "ascending" : "descending";
      c[0].setAttribute("aria-sort", active ? word : "none");
      c[1].ind.textContent = active ? (state.sortDir === "asc" ? "↑" : "↓") : "";
      c[1].btn.setAttribute("aria-label", c[3] + (active ? ", " + word : ""));
    });
  }

  function syncUrl() {
    var p = new URLSearchParams();
    if (state.q.trim()) p.set("q", state.q.trim());
    if (state.topic) p.set("topic", state.topic);
    if (state.type) p.set("type", state.type);
    if (state.sortKey !== "date" || state.sortDir !== "desc") p.set("sort", state.sortKey + "-" + state.sortDir);
    var qs = p.toString();
    try {
      history.replaceState(null, "", location.pathname + (qs ? "?" + qs : "") + location.hash);
    } catch (err) { /* file:// or sandboxed frame: ignore */ }
  }

  function render() {
    var shown = rows.filter(matches).sort(compare);
    var show = new Set(shown);
    var frag = document.createDocumentFragment();
    shown.forEach(function (row) { row.hidden = false; frag.appendChild(row); });
    rows.forEach(function (row) { if (!show.has(row)) { row.hidden = true; frag.appendChild(row); } });
    body.insertBefore(frag, emptyRow);
    emptyRow.hidden = shown.length !== 0;
    countEl.textContent = shown.length === total
      ? "Showing " + total + (total === 1 ? " resource" : " resources")
      : "Showing " + shown.length + " of " + total + " resources";
    clearBtn.disabled = !(state.q.trim() || state.topic || state.type);
    updateSortUi();
    syncUrl();
  }

  qInput.addEventListener("input", function (ev) { state.q = ev.target.value; render(); });
  topicSel.addEventListener("change", function (ev) { state.topic = ev.target.value; render(); });
  typeSel.addEventListener("change", function (ev) { state.type = ev.target.value; render(); });
  sortSel.addEventListener("change", function (ev) {
    var parts = ev.target.value.split("-");
    state.sortKey = parts[0];
    state.sortDir = parts[1];
    render();
  });
  clearBtn.addEventListener("click", function () {
    state.q = state.topic = state.type = "";
    qInput.value = topicSel.value = typeSel.value = "";
    render();
    qInput.focus();
  });
  form.addEventListener("submit", function (ev) { ev.preventDefault(); });

  // initial state from the URL (shareable links)
  var params = new URLSearchParams(location.search);
  var optionValues = function (sel) {
    return Array.prototype.map.call(sel.options, function (o) { return o.value; });
  };
  if (params.get("q")) { state.q = params.get("q"); qInput.value = state.q; }
  if (params.get("topic") && optionValues(topicSel).indexOf(params.get("topic")) > -1) {
    state.topic = params.get("topic"); topicSel.value = state.topic;
  }
  if (params.get("type") && optionValues(typeSel).indexOf(params.get("type")) > -1) {
    state.type = params.get("type"); typeSel.value = state.type;
  }
  if (/^(date|title)-(asc|desc)$/.test(params.get("sort") || "")) {
    var s = params.get("sort").split("-");
    state.sortKey = s[0]; state.sortDir = s[1];
  }

  form.hidden = false;
  render();

  // keep keyboard focus on the target of in-page links
  document.body.addEventListener("click", function (event) {
    var link = event.target.closest("a[href^='#']");
    if (!link) return;
    var target = document.getElementById(decodeURIComponent(link.getAttribute("href").slice(1)));
    if (!target) return;
    window.setTimeout(function () {
      if (target.tabIndex < 0) target.tabIndex = -1;
      target.focus({ preventScroll: true });
    }, 0);
  });
})();
