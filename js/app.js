"use strict";

const state = {
  q: "",
  topic: "",
  type: "",
  sortKey: "date",
  sortDir: "desc",
};

let data = null;
let topicById = new Map();
let resourceById = new Map();

function h(tag, props, ...kids) {
  const node = document.createElement(tag);
  if (props) {
    for (const [key, value] of Object.entries(props)) {
      if (value == null || value === false) continue;
      if (key === "class") node.className = value;
      else if (key === "text") node.textContent = String(value);
      else node.setAttribute(key, value === true ? "" : String(value));
    }
  }
  appendKids(node, kids);
  return node;
}

function appendKids(node, kids) {
  for (const kid of kids) {
    if (kid == null || kid === false) continue;
    if (Array.isArray(kid)) appendKids(node, kid);
    else node.append(kid);
  }
}

function safeHttpUrl(url) {
  if (typeof url !== "string" || url === "") return null;
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== "https:" && parsed.protocol !== "http:") return null;
  } catch (err) {
    return null;
  }
  return url;
}

function externalLink(url, text) {
  const safe = safeHttpUrl(url);
  if (!safe) return h("span", { text: text || "" });
  const a = h("a", {
    href: safe,
    target: "_blank",
    rel: "noopener",
    class: "res-title",
  });
  a.append(text || safe, h("span", { class: "sr-only", text: " (opens in a new tab)" }));
  return a;
}

function isIsoDate(value) {
  return typeof value === "string" && /^\d{4}(-\d{2}(-\d{2})?)?$/.test(value);
}

function formatLongDate(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return value;
  const [year, month, day] = value.split("-").map(Number);
  return new Intl.DateTimeFormat("en-US", {
    timeZone: "UTC",
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(Date.UTC(year, month - 1, day)));
}

function timeEl(value, longForm) {
  const time = h("time", { text: longForm ? formatLongDate(value) : value });
  if (isIsoDate(value)) time.dateTime = value;
  return time;
}

function topicName(id) {
  const topic = topicById.get(id);
  return topic ? topic.name : id;
}

function dateValue(value) {
  if (!isIsoDate(value)) return null;
  const [year, month = "0", day = "0"] = value.split("-");
  return Number(year) * 10000 + Number(month) * 100 + Number(day);
}

function compareResources(a, b) {
  if (state.sortKey === "title") {
    const byTitle = a.title.localeCompare(b.title, "en", { sensitivity: "base" });
    const directed = state.sortDir === "asc" ? byTitle : -byTitle;
    if (directed) return directed;
    return a.id.localeCompare(b.id, "en", { numeric: true });
  }
  const av = dateValue(a.date);
  const bv = dateValue(b.date);
  if (av == null && bv == null) {
    return a.title.localeCompare(b.title, "en", { sensitivity: "base" });
  }
  if (av == null) return 1;
  if (bv == null) return -1;
  const diff = state.sortDir === "asc" ? av - bv : bv - av;
  if (diff) return diff;
  return a.title.localeCompare(b.title, "en", { sensitivity: "base" });
}

function haystack(resource) {
  const names = (resource.topics || []).map(topicName).join(" ");
  return [
    resource.id,
    resource.title,
    resource.publisher,
    resource.type,
    resource.date,
    names,
    (resource.topics || []).join(" "),
  ].join("\n").toLowerCase();
}

function matches(resource) {
  if (state.topic && !(resource.topics || []).includes(state.topic)) return false;
  if (state.type && resource.type !== state.type) return false;
  const terms = state.q.toLowerCase().trim().split(/\s+/).filter(Boolean);
  if (!terms.length) return true;
  const hay = haystack(resource);
  return terms.every((term) => hay.includes(term));
}

function showError(message) {
  const status = document.getElementById("status");
  status.hidden = false;
  status.setAttribute("role", "alert");
  status.textContent = message;
  document.getElementById("content").hidden = true;
}

function requireShape(payload) {
  const fields = [
    "title",
    "summary",
    "summaryText",
    "lastUpdated",
    "whatsNew",
    "topics",
    "keyIssues",
    "resources",
    "changeLog",
    "gaps",
  ];
  const missing = fields.filter((key) => !Object.prototype.hasOwnProperty.call(payload, key));
  if (missing.length) {
    throw new Error("data/site-data.json is missing: " + missing.join(", "));
  }
  if (!Array.isArray(payload.topics) || !Array.isArray(payload.resources)) {
    throw new Error("data/site-data.json topics and resources must be arrays.");
  }
}

function fillHeader() {
  document.title = data.title;
  const description = document.getElementById("description");
  if (description) description.setAttribute("content", data.summary);
  document.getElementById("page-title").textContent = data.title;
  document.getElementById("summary").textContent = data.summary;
  document.getElementById("summary-text").textContent = data.summaryText;
  const meta = document.getElementById("meta");
  meta.replaceChildren(
    "Last updated ",
    timeEl(data.lastUpdated, true),
    " · ",
    String(data.topics.length) + " topics",
    " · ",
    String(data.resources.length) + " resources"
  );
  document.getElementById("footer-line").replaceChildren(
    data.title + ". Last updated ",
    timeEl(data.lastUpdated, true),
    "."
  );
}

function fillWhatsNew() {
  const list = document.getElementById("whats-new-list");
  list.replaceChildren();
  for (const item of data.whatsNew) {
    list.append(
      h("article", { class: "news-item" },
        h("p", { class: "news-date", text: item.date || "" }),
        h("div", null,
          h("h3", { text: item.title || "" }),
          item.detail ? h("p", { text: item.detail }) : null
        )
      )
    );
  }
}

function topicChips(ids, linkTopics) {
  const wrap = h("div", { class: "chips" });
  for (const id of ids || []) {
    if (linkTopics) {
      const link = h("a", { class: "chip", href: "#topic-" + id, text: topicName(id) });
      wrap.append(link);
    } else {
      wrap.append(h("span", { class: "chip", text: topicName(id) }));
    }
  }
  return wrap;
}

function fillTopics() {
  const toc = document.getElementById("topic-toc");
  const list = document.getElementById("topic-list");
  const ol = h("ol");
  toc.className = "toc";
  toc.replaceChildren(ol);
  list.replaceChildren();

  for (const topic of data.topics) {
    const anchor = "topic-" + topic.id;
    ol.append(h("li", null, h("a", { href: "#" + anchor, text: topic.name })));

    const article = h("article", { class: "topic", id: anchor, tabindex: "-1" },
      h("h3", { class: "topic-name", text: topic.name })
    );

    if (Array.isArray(topic.takeaways) && topic.takeaways.length) {
      article.append(
        h("ul", { class: "takeaways" },
          topic.takeaways.map((item) => h("li", { text: item }))
        )
      );
    }

    const resources = topic.resourceIds || [];
    if (resources.length) {
      const items = resources.map((id) => {
        const resource = resourceById.get(id);
        if (!resource) return h("li", { text: id });
        const metaBits = [
          h("span", { text: resource.id }),
          h("span", { text: resource.publisher }),
          h("span", { class: "chip", text: resource.type }),
        ];
        if (resource.date) metaBits.push(timeEl(resource.date, false));
        else metaBits.push(h("span", { class: "muted", text: "Undated" }));
        return h("li", null,
          externalLink(resource.url, resource.title),
          h("p", { class: "meta" }, metaBits),
          topicChips(resource.topics, true)
        );
      });
      article.append(
        h("h4", { class: "subhead", text: "Resources" }),
        h("ul", { class: "linked-resources" }, items)
      );
    }

    list.append(article);
  }
}

function fillStringList(id, items) {
  const list = document.getElementById(id);
  list.replaceChildren(...(items || []).map((item) => h("li", { text: item })));
}

function fillLog() {
  const list = document.getElementById("change-log");
  list.replaceChildren();
  for (const item of data.changeLog || []) {
    list.append(
      h("li", null,
        timeEl(item.date, true),
        h("span", { text: item.entry || "" })
      )
    );
  }
}

function fillFilters() {
  const topicSelect = document.getElementById("topic-filter");
  const typeSelect = document.getElementById("type-filter");
  for (const topic of data.topics) {
    topicSelect.append(h("option", { value: topic.id, text: topic.name }));
  }
  const types = [...new Set(data.resources.map((resource) => resource.type).filter(Boolean))];
  types.sort((a, b) => a.localeCompare(b, "en", { sensitivity: "base" }));
  for (const type of types) {
    typeSelect.append(h("option", { value: type, text: type }));
  }
}

function updateSortControls() {
  const sort = document.getElementById("sort");
  sort.value = state.sortKey + "-" + state.sortDir;
  const titleTh = document.getElementById("th-title");
  const dateTh = document.getElementById("th-date");
  const titleInd = document.getElementById("ind-title");
  const dateInd = document.getElementById("ind-date");
  const titleBtn = document.getElementById("sort-title");
  const dateBtn = document.getElementById("sort-date");

  titleTh.setAttribute("aria-sort", state.sortKey === "title" ? (state.sortDir === "asc" ? "ascending" : "descending") : "none");
  dateTh.setAttribute("aria-sort", state.sortKey === "date" ? (state.sortDir === "asc" ? "ascending" : "descending") : "none");
  titleInd.textContent = state.sortKey === "title" ? (state.sortDir === "asc" ? "↑" : "↓") : "";
  dateInd.textContent = state.sortKey === "date" ? (state.sortDir === "asc" ? "↑" : "↓") : "";

  const titleDir = state.sortKey === "title" ? (state.sortDir === "asc" ? ", ascending" : ", descending") : "";
  const dateDir = state.sortKey === "date" ? (state.sortDir === "asc" ? ", ascending" : ", descending") : "";
  titleBtn.setAttribute("aria-label", "Sort by title" + titleDir);
  dateBtn.setAttribute("aria-label", "Sort by date" + dateDir);
}

function renderTable() {
  const body = document.getElementById("resource-body");
  const rows = data.resources.filter(matches).sort(compareResources);
  const total = data.resources.length;
  const count = document.getElementById("resource-count");
  count.textContent = rows.length === total
    ? "Showing " + total + (total === 1 ? " resource" : " resources")
    : "Showing " + rows.length + " of " + total + " resources";

  if (!rows.length) {
    body.replaceChildren(
      h("tr", null, h("td", { class: "empty", colspan: "6", text: "No resources match these filters." }))
    );
  } else {
    body.replaceChildren(...rows.map(renderRow));
  }

  const clear = document.getElementById("clear");
  const active = state.q.trim() !== "" || state.topic !== "" || state.type !== "";
  clear.disabled = !active;
  updateSortControls();
}

function renderRow(resource) {
  const dateCell = h("td", { class: "num" });
  if (resource.date) dateCell.append(timeEl(resource.date, false));
  else dateCell.append(h("span", { class: "muted", text: "Undated" }));

  return h("tr", null,
    h("td", { class: "title-col" }, externalLink(resource.url, resource.title)),
    h("td", { class: "id-col", text: resource.id }),
    h("td", { text: resource.publisher || "" }),
    h("td", null, h("span", { class: "chip", text: resource.type || "" })),
    dateCell,
    h("td", null, topicChips(resource.topics, true))
  );
}

function setSort(key, dir) {
  state.sortKey = key;
  state.sortDir = dir;
  renderTable();
}

function toggleSort(key) {
  if (state.sortKey === key) {
    state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
  } else {
    state.sortKey = key;
    state.sortDir = key === "title" ? "asc" : "desc";
  }
  renderTable();
}

function bind() {
  const form = document.getElementById("resource-filters");
  form.addEventListener("submit", (event) => event.preventDefault());

  document.getElementById("q").addEventListener("input", (event) => {
    state.q = event.target.value;
    renderTable();
  });
  document.getElementById("topic-filter").addEventListener("change", (event) => {
    state.topic = event.target.value;
    renderTable();
  });
  document.getElementById("type-filter").addEventListener("change", (event) => {
    state.type = event.target.value;
    renderTable();
  });
  document.getElementById("sort").addEventListener("change", (event) => {
    const [key, dir] = event.target.value.split("-");
    setSort(key, dir);
  });
  document.getElementById("clear").addEventListener("click", () => {
    state.q = "";
    state.topic = "";
    state.type = "";
    document.getElementById("q").value = "";
    document.getElementById("topic-filter").value = "";
    document.getElementById("type-filter").value = "";
    renderTable();
    document.getElementById("q").focus();
  });
  document.getElementById("sort-title").addEventListener("click", () => toggleSort("title"));
  document.getElementById("sort-date").addEventListener("click", () => toggleSort("date"));

  document.body.addEventListener("click", (event) => {
    const link = event.target.closest("a[href^='#']");
    if (!link) return;
    const id = decodeURIComponent(link.getAttribute("href").slice(1));
    const target = document.getElementById(id);
    if (!target) return;
    window.setTimeout(() => {
      if (target.tabIndex < 0) target.tabIndex = -1;
      target.focus({ preventScroll: true });
    }, 0);
  });
}

function render() {
  topicById = new Map(data.topics.map((topic) => [topic.id, topic]));
  resourceById = new Map(data.resources.map((resource) => [resource.id, resource]));
  fillHeader();
  fillWhatsNew();
  fillTopics();
  fillStringList("issue-list", data.keyIssues);
  fillStringList("gap-list", data.gaps);
  fillLog();
  fillFilters();
  bind();
  renderTable();
  document.getElementById("content").hidden = false;
  document.getElementById("section-nav").hidden = false;
  document.getElementById("status").hidden = true;
}

async function init() {
  try {
    const response = await fetch("data/site-data.json");
    if (!response.ok) {
      throw new Error("Could not load data/site-data.json (" + response.status + "). Serve this folder over HTTP and open the site from that address.");
    }
    const payload = await response.json();
    requireShape(payload);
    data = payload;
    render();
  } catch (err) {
    showError(err && err.message ? err.message : "Could not load data/site-data.json.");
  }
}

init();
