/* Material price table: filter, sort, and small trend charts. The table is in the HTML. */
(function () {
  "use strict";
  var table = document.getElementById("price-table");
  if (!table) return;
  var rows = Array.prototype.slice.call(table.tBodies[0].rows);
  var visible = document.getElementById("price-visible");
  var filters = {
    material: document.getElementById("f-material"),
    kind: document.getElementById("f-kind"),
    level: document.getElementById("f-level"),
    year: document.getElementById("f-year"),
    q: document.getElementById("f-q")
  };

  function apply() {
    var material = filters.material.value;
    var kind = filters.kind.value;
    var level = filters.level.value;
    var year = filters.year.value;
    var q = (filters.q.value || "").trim().toLowerCase();
    var n = 0;
    for (var i = 0; i < rows.length; i++) {
      var r = rows[i];
      var show = (!material || r.getAttribute("data-material") === material) &&
        (!kind || r.getAttribute("data-kind") === kind) &&
        (!level || r.getAttribute("data-level") === level) &&
        (!year || r.getAttribute("data-year") === year) &&
        (!q || (r.getAttribute("data-hay") || "").indexOf(q) !== -1);
      r.hidden = !show;
      if (show) n++;
    }
    if (visible) visible.textContent = n + " shown";
  }

  Object.keys(filters).forEach(function (k) {
    if (!filters[k]) return;
    filters[k].addEventListener("input", apply);
    filters[k].addEventListener("change", apply);
  });

  var sortKey = "period";
  var sortDir = 1;
  function cellValue(row, key) {
    if (key === "value") return parseFloat(row.getAttribute("data-value"));
    if (key === "period") return row.getAttribute("data-period") || "";
    var idx = { material: 0, geography: 2, kind: 5, source: 6 }[key];
    return (row.cells[idx].textContent || "").toLowerCase();
  }
  Array.prototype.forEach.call(table.tHead.rows[0].cells, function (th) {
    var key = th.getAttribute("data-sort");
    if (!key) return;
    th.tabIndex = 0;
    th.style.cursor = "pointer";
    function go() {
      if (sortKey === key) sortDir = -sortDir;
      else { sortKey = key; sortDir = key === "period" || key === "value" ? 1 : 1; }
      rows.sort(function (a, b) {
        var av = cellValue(a, key), bv = cellValue(b, key);
        if (av < bv) return -sortDir;
        if (av > bv) return sortDir;
        return 0;
      });
      var body = table.tBodies[0];
      for (var i = 0; i < rows.length; i++) body.appendChild(rows[i]);
    }
    th.addEventListener("click", go);
    th.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); go(); } });
  });

  var specNode = document.getElementById("price-charts");
  var host = document.getElementById("chart-host");
  if (specNode && host) {
    var specs = JSON.parse(specNode.textContent);
    specs.forEach(function (spec) {
      host.appendChild(chart(spec));
    });
  }

  function chart(spec) {
    var wrap = document.createElement("figure");
    wrap.className = "price-chart";
    var cap = document.createElement("figcaption");
    cap.textContent = spec.title + " (" + spec.unit + ")";
    var w = 640, h = 180, pad = 28;
    var pts = spec.points || [];
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", spec.title);
    if (pts.length >= 2) {
      var min = pts[0].v, max = pts[0].v;
      for (var i = 1; i < pts.length; i++) {
        if (pts[i].v < min) min = pts[i].v;
        if (pts[i].v > max) max = pts[i].v;
      }
      if (min === max) { min -= 1; max += 1; }
      var d = "";
      for (var j = 0; j < pts.length; j++) {
        var x = pad + (w - pad * 2) * (j / (pts.length - 1));
        var y = pad + (h - pad * 2) * (1 - (pts[j].v - min) / (max - min));
        d += (j ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1);
      }
      var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", d);
      path.setAttribute("fill", "none");
      path.setAttribute("stroke", "currentColor");
      path.setAttribute("stroke-width", "1.5");
      svg.appendChild(path);
      var label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", pad);
      label.setAttribute("y", 14);
      label.setAttribute("font-size", "12");
      label.textContent = pts[0].p + " – " + pts[pts.length - 1].p + " · " + min + " to " + max;
      svg.appendChild(label);
    }
    wrap.appendChild(svg);
    wrap.appendChild(cap);
    return wrap;
  }

  apply();
})();
