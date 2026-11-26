/* DOT qualified-product list: filter by material category and by state or agency text. */
(function () {
  "use strict";
  var cat = document.getElementById("qpl-cat");
  var q = document.getElementById("qpl-q");
  var visible = document.getElementById("qpl-visible");
  var groups = Array.prototype.slice.call(document.querySelectorAll("[data-qpl-state]"));
  if (!cat || !groups.length) return;

  function apply() {
    var want = cat.value;
    var text = (q.value || "").trim().toLowerCase();
    var n = 0;
    groups.forEach(function (group) {
      var rows = group.querySelectorAll("tbody tr");
      var any = false;
      for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var show = (!want || row.getAttribute("data-cat") === want) &&
          (!text || (row.getAttribute("data-hay") || "").indexOf(text) !== -1);
        row.hidden = !show;
        if (show) { any = true; n++; }
      }
      group.hidden = !any;
    });
    if (visible) visible.textContent = n + " lists shown";
  }

  cat.addEventListener("change", apply);
  q.addEventListener("input", apply);
  apply();
})();
