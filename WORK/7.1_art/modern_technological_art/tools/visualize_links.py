#!/usr/bin/env python3
"""
Link visualizer for WEB/7.1_art/modern_technological_art
Run: python3 tools/visualize_links.py
Output: tools/graph.html
"""

import os, re, json
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).parent.parent.parent.parent.parent
SECTION_DIR = BASE / "WEB" / "7.1_art" / "modern_technological_art"
ARTICLES_DIR = SECTION_DIR / "articles"
OUTPUT = Path(__file__).parent / "graph.html"

PORTAL_LABELS = {
    0: "Главная",
    1: "Телекоммуникационное искусство",
    2: "Net.art",
    3: "Медиаактивизм и OSINT",
    4: "Пост-цифровая эпоха",
    5: "Лабораторное искусство",
    6: "Эпоха LLM",
}

PORTAL_COLORS = {
    0: "#F59E0B",
    1: "#06B6D4",
    2: "#3B82F6",
    3: "#F97316",
    4: "#8B5CF6",
    5: "#10B981",
    6: "#EC4899",
}

LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')

# ── helpers ────────────────────────────────────────────────────────────────

def get_portal(stem):
    m = re.match(r'^(\d+)\.', stem)
    return int(m.group(1)) if m else 0

def get_h1(filepath):
    for line in open(filepath, encoding="utf-8"):
        if line.startswith("# "):
            return line[2:].strip()
    return filepath.stem

def short_label(s, n=28):
    return s if len(s) <= n else s[:n-1] + "…"

# ── build graph ────────────────────────────────────────────────────────────

nodes = {}
edges = []
edge_set = set()

def add_node(nid, **kw):
    if nid not in nodes:
        nodes[nid] = {"id": nid, **kw}

def add_edge(src, tgt, etype, label=""):
    key = (src, tgt, etype)
    if key not in edge_set:
        edge_set.add(key)
        edges.append({"source": src, "target": tgt, "type": etype, "label": label[:50]})

# collect article filenames for resolution
article_map = {}   # filename.md -> node_id

# README
add_node("README",
         label="Технологическое искусство: Энциклопедия",
         short="README",
         type="readme",
         portal=0,
         color=PORTAL_COLORS[0],
         file="README.md")
article_map["README.md"] = "README"

# Articles
for f in sorted(ARTICLES_DIR.glob("*.md")):
    portal = get_portal(f.stem)
    title = get_h1(f)
    nid = f.stem
    add_node(nid,
             label=title,
             short=short_label(title),
             type="article",
             portal=portal,
             color=PORTAL_COLORS.get(portal, "#9CA3AF"),
             file=f"articles/{f.name}")
    article_map[f.name] = nid

# ── link extraction ────────────────────────────────────────────────────────

def process_file(filepath, from_id):
    text = open(filepath, encoding="utf-8").read()
    for label, url in LINK_RE.findall(text):
        url = url.strip()

        # skip images
        if url.startswith("../images/") or re.search(r'\.(jpg|png|gif|svg|webp)$', url, re.I):
            continue

        # internal .md link
        if url.endswith(".md") and not url.startswith("http"):
            fname = url.split("/")[-1]
            if fname in article_map:
                tgt = article_map[fname]
                if tgt != from_id:
                    add_edge(from_id, tgt, "internal", label)
            else:
                # link to a file not present in this repo
                broken_id = f"broken:{fname}"
                add_node(broken_id,
                         label=fname,
                         short=short_label(fname),
                         type="broken",
                         portal=-1,
                         color="#EF4444",
                         file=fname)
                add_edge(from_id, broken_id, "broken", label)
            continue

        # external URL
        if url.startswith("http"):
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path_parts = [p for p in parsed.path.split("/") if p]

            if "wikipedia.org" in domain:
                lang = domain.split(".")[0]   # en / ru
                page = path_parts[-1] if path_parts else domain
                nid = f"wiki:{lang}:{page[:40]}"
                display = page.replace("_", " ")
                add_node(nid,
                         label=display,
                         short=short_label(display),
                         type="wiki",
                         lang=lang,
                         domain=domain,
                         url=url,
                         color="#94A3B8" if lang == "en" else "#64748B")
            else:
                nid = f"ext:{domain}"
                add_node(nid,
                         label=domain,
                         short=short_label(domain),
                         type="external",
                         domain=domain,
                         url=url,
                         color="#6B7280")
            add_edge(from_id, nid, "external", label)

# process README
process_file(SECTION_DIR / "README.md", "README")

# process all articles
for f in sorted(ARTICLES_DIR.glob("*.md")):
    process_file(f, f.stem)

# ── compute node stats ─────────────────────────────────────────────────────

in_degree  = {n: 0 for n in nodes}
out_degree = {n: 0 for n in nodes}
for e in edges:
    out_degree[e["source"]] += 1
    in_degree[e["target"]]  += 1

for nid, node in nodes.items():
    node["in"]  = in_degree.get(nid, 0)
    node["out"] = out_degree.get(nid, 0)

# ── assemble graph data ────────────────────────────────────────────────────

graph_data = {
    "nodes": list(nodes.values()),
    "links": edges,
    "portals": [{"id": k, "label": v, "color": PORTAL_COLORS[k]}
                for k, v in PORTAL_LABELS.items()],
}

# ── HTML template ──────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Граф ссылок — Технологическое искусство</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0f1117; color: #e2e8f0; font-family: 'Inter', system-ui, sans-serif;
         display: flex; height: 100vh; overflow: hidden; }

  /* ── sidebar ── */
  #sidebar { width: 280px; min-width: 280px; background: #1a1d2e; display: flex;
             flex-direction: column; border-right: 1px solid #2d3348; z-index: 10; }
  #sidebar h1 { font-size: 13px; font-weight: 700; padding: 16px; color: #94a3b8;
                text-transform: uppercase; letter-spacing: .08em; border-bottom: 1px solid #2d3348; }

  .section { padding: 12px 16px; border-bottom: 1px solid #2d3348; }
  .section h2 { font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase;
                letter-spacing: .07em; margin-bottom: 8px; }

  /* search */
  #search { width: 100%; background: #252840; border: 1px solid #3a3f5c; border-radius: 6px;
            padding: 7px 10px; font-size: 13px; color: #e2e8f0; outline: none; }
  #search::placeholder { color: #475569; }
  #search:focus { border-color: #6366f1; }

  /* toggles */
  .toggle-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
                cursor: pointer; user-select: none; font-size: 13px; }
  .toggle-row input { accent-color: #6366f1; cursor: pointer; }
  .dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

  /* portal list */
  .portal-item { display: flex; align-items: center; gap: 8px; padding: 4px 0;
                 cursor: pointer; font-size: 12px; color: #94a3b8; }
  .portal-item.active { color: #e2e8f0; }
  .portal-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

  /* info panel */
  #info { flex: 1; overflow-y: auto; padding: 12px 16px; }
  #info-title { font-size: 14px; font-weight: 600; margin-bottom: 8px; color: #f1f5f9; }
  #info-body { font-size: 12px; color: #94a3b8; line-height: 1.6; }
  #info-body .stat { margin-top: 4px; }
  #info-body .chip { display: inline-block; background: #252840; border-radius: 4px;
                     padding: 2px 7px; margin: 2px 2px 0 0; font-size: 11px; color: #64748b; }

  /* stats bar */
  #stats { padding: 10px 16px; font-size: 11px; color: #475569;
           border-top: 1px solid #2d3348; }

  /* ── canvas ── */
  #canvas { flex: 1; position: relative; }
  svg { width: 100%; height: 100%; }

  .link { stroke-opacity: 0.55; fill: none; }
  .link.internal { stroke: #6366f1; stroke-width: 1.5px; }
  .link.external  { stroke: #475569; stroke-width: 1px; stroke-dasharray: 4 3; }
  .link.wiki      { stroke: #374151; stroke-width: 1px; stroke-dasharray: 3 3; }
  .link.broken    { stroke: #ef4444; stroke-width: 1px; stroke-dasharray: 2 4; }

  .link.highlighted  { stroke-opacity: 1   !important; stroke-width: 2.5px !important; }
  .link.bg-dimmed    { stroke-opacity: 0   !important; pointer-events: none; }
  .link.path-link    { stroke: #22c55e !important; stroke-opacity: 1 !important;
                       stroke-width: 3px  !important; stroke-dasharray: none !important; }

  .node circle { cursor: pointer; stroke-width: 1.5px; }
  .node text   { pointer-events: none; font-size: 11px; fill: #cbd5e1;
                 text-shadow: 0 1px 3px #0f1117, 0 0 8px #0f1117; }

  /* ── animations ── */
  @keyframes readme-pulse {
    0%   { stroke-width: 2px;  stroke-opacity: 0.7; r: 22; }
    50%  { stroke-width: 6px;  stroke-opacity: 1;   r: 25; }
    100% { stroke-width: 2px;  stroke-opacity: 0.7; r: 22; }
  }
  .node.readme-node circle { animation: readme-pulse 3s ease-in-out infinite; }

  @keyframes edge-flow {
    from { stroke-dashoffset: 24; }
    to   { stroke-dashoffset: 0; }
  }
  .link.internal.flow-on {
    stroke-dasharray: 8 4 !important;
    stroke-opacity: 0.8 !important;
    animation: edge-flow 1.4s linear infinite;
  }

  #btn-orbit {
    width: 100%; padding: 7px; background: #252840; border: 1px solid #3a3f5c;
    border-radius: 6px; color: #94a3b8; font-size: 12px; cursor: pointer;
    text-align: left; margin-bottom: 8px;
  }
  #btn-orbit.active { border-color: #06B6D4; color: #06B6D4; }

  .node.dimmed circle { opacity: 0.12; }
  .node.dimmed text   { opacity: 0.08; }
  .node.highlighted  circle { stroke: #fff    !important; stroke-width: 2.5px; }
  .node.path-source  circle { stroke: #22c55e !important; stroke-width: 3.5px; fill: #22c55e33 !important; }
  .node.path-target  circle { stroke: #f59e0b !important; stroke-width: 3.5px; fill: #f59e0b33 !important; }
  .node.path-mid     circle { stroke: #fff    !important; stroke-width: 2px; }

  /* tooltip */
  #tooltip { position: absolute; background: #1e2235; border: 1px solid #3a3f5c;
             border-radius: 8px; padding: 10px 13px; pointer-events: none;
             font-size: 12px; max-width: 260px; line-height: 1.5;
             box-shadow: 0 8px 24px rgba(0,0,0,.5); opacity: 0; transition: opacity .1s; z-index: 100; }
  #tooltip strong { color: #f1f5f9; display: block; margin-bottom: 4px; }
  #tooltip span { color: #64748b; font-size: 11px; }
</style>
</head>
<body>

<div id="sidebar">
  <h1>Граф ссылок</h1>

  <div class="section">
    <h2>Поиск</h2>
    <input id="search" type="text" placeholder="Название статьи или домен…">
  </div>

  <div class="section">
    <h2>Показать</h2>
    <label class="toggle-row"><input type="checkbox" id="tog-internal" checked>
      <span class="dot" style="background:#6366f1"></span> Внутренние ссылки</label>
    <label class="toggle-row"><input type="checkbox" id="tog-external">
      <span class="dot" style="background:#475569"></span> Внешние (Wikipedia, сайты)</label>
    <label class="toggle-row"><input type="checkbox" id="tog-broken">
      <span class="dot" style="background:#ef4444"></span> Ссылки вне репо</label>
    <label class="toggle-row"><input type="checkbox" id="tog-labels" checked>
      <span class="dot" style="background:#94a3b8"></span> Подписи узлов</label>
  </div>

  <div class="section">
    <h2>Путь A → B</h2>
    <div id="path-status" style="font-size:12px;color:#475569;margin-bottom:8px">Режим выключен</div>
    <button id="btn-path"
      style="width:100%;padding:7px;background:#252840;border:1px solid #3a3f5c;border-radius:6px;
             color:#94a3b8;font-size:12px;cursor:pointer;text-align:left">
      ⬡ Включить режим пути
    </button>
    <label class="toggle-row" style="margin-top:8px">
      <input type="checkbox" id="tog-readme-path">
      <span class="dot" style="background:#F59E0B"></span> Через README
    </label>
  </div>

  <div class="section">
    <h2>Анимация</h2>
    <button id="btn-orbit">⟳ Орбитальное вращение</button>
    <label class="toggle-row">
      <input type="checkbox" id="tog-flow">
      <span class="dot" style="background:#6366f1"></span> Поток по рёбрам
    </label>
  </div>

  <div class="section" id="portal-filters">
    <h2>Порталы</h2>
    <!-- filled by JS -->
  </div>

  <div id="info">
    <div id="info-title" style="color:#475569">Нажмите на узел</div>
    <div id="info-body"></div>
  </div>

  <div id="stats"></div>
</div>

<div id="canvas">
  <svg id="svg"></svg>
  <div id="tooltip"></div>
</div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const DATA = GRAPH_DATA_PLACEHOLDER;

// ── setup ──────────────────────────────────────────────────────────────────
const svg = d3.select("#svg");
const container = svg.append("g");
const tooltip = document.getElementById("tooltip");
const infoTitle = document.getElementById("info-title");
const infoBody  = document.getElementById("info-body");

// arrow markers
["internal","external","wiki","broken"].forEach(t => {
  const color = t === "internal" ? "#6366f1" : t === "broken" ? "#ef4444" : "#374151";
  svg.append("defs").append("marker")
    .attr("id", `arrow-${t}`)
    .attr("viewBox", "0 -4 8 8")
    .attr("refX", 18).attr("refY", 0)
    .attr("markerWidth", 6).attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path").attr("d","M0,-4L8,0L0,4").attr("fill", color).attr("opacity", 0.7);
});

// zoom
const zoom = d3.zoom().scaleExtent([0.1, 8]).on("zoom", e => container.attr("transform", e.transform));
svg.call(zoom);

// ── radial + sector layout ──────────────────────────────────────────────────
// Ring 0 (center):  README
// Ring 1 (r≈260):   articles directly linked from README  → grouped by portal sector
// Ring 2 (r≈490):   articles 2nd-level                   → same portal sectors
// Ring 3 (r≈740):   external / wiki / broken             → free radial
const RING_R = { 0: 0, 1: 260, 2: 490, 3: 740 };

// Portal angular sectors: 6 portals arranged in hexagon, portal 1 at top, clockwise
const PORTAL_ANGLE = {
  1: -Math.PI / 2,        // top (270°)
  2: -Math.PI / 6,        // top-right (330°)
  3:  Math.PI / 6,        // right (30°)
  4:  Math.PI / 2,        // bottom (90°)
  5:  5 * Math.PI / 6,    // bottom-left (150°)
  6: -5 * Math.PI / 6,    // top-left (210°)
};

// BFS from README over internal links to assign ring depth per article
function computeRingDepths() {
  const depths = { README: 0 };
  const queue = ["README"];
  const adj = {};
  DATA.nodes.forEach(n => { adj[n.id] = []; });
  DATA.links.forEach(l => {
    if (l.type !== "internal") return;
    const sid = l.source.id || l.source;
    const tid = l.target.id || l.target;
    adj[sid].push(tid);
    adj[tid].push(sid);
  });
  while (queue.length) {
    const cur = queue.shift();
    for (const nb of (adj[cur] || [])) {
      if (!(nb in depths)) { depths[nb] = depths[cur] + 1; queue.push(nb); }
    }
  }
  return depths;
}
const ringDepths = computeRingDepths();

function nodeRing(d) {
  if (d.type === "readme") return 0;
  if (d.type === "article") return (ringDepths[d.id] ?? 99) <= 1 ? 1 : 2;
  return 3;
}

// Compute target (x, y) for each node given canvas center (cx, cy)
function computeTargets(cx, cy) {
  DATA.nodes.forEach(n => {
    if (n.type === "readme") {
      n._tx = cx; n._ty = cy;
    } else if (n.type === "article") {
      const r     = RING_R[nodeRing(n)];
      const angle = PORTAL_ANGLE[n.portal] ?? 0;
      n._tx = cx + Math.cos(angle) * r;
      n._ty = cy + Math.sin(angle) * r;
    } else {
      // external/wiki/broken: angular target not needed, radial force handles them
      n._tx = cx; n._ty = cy;
    }
  });
}

// ── state ──────────────────────────────────────────────────────────────────
let showInternal = true;
let showExternal = false;
let showBroken   = false;
let showLabels   = true;
let activePorts  = new Set([-1, 0, 1, 2, 3, 4, 5, 6]);
let searchTerm   = "";
let selectedNode = null;
let pathMode        = false;
let pathSource      = null;
let pathAllowReadme = false;

// ── portal filter UI ───────────────────────────────────────────────────────
const pfDiv = document.getElementById("portal-filters");
DATA.portals.forEach(p => {
  const el = document.createElement("div");
  el.className = "portal-item active";
  el.dataset.portal = p.id;
  el.innerHTML = `<span class="portal-dot" style="background:${p.color}"></span>${p.label}`;
  el.addEventListener("click", () => {
    const pid = +el.dataset.portal;
    if (activePorts.has(pid)) { activePorts.delete(pid); el.classList.remove("active"); }
    else { activePorts.add(pid); el.classList.add("active"); }
    restart();
  });
  pfDiv.appendChild(el);
});

// ── helpers ────────────────────────────────────────────────────────────────
function nodeRadius(d) {
  if (d.type === "readme") return 22;
  if (d.type === "article") return 10 + d.in * 1.2;
  if (d.type === "wiki")    return 6  + d.in * 0.8;
  return 7;
}

function nodeStroke(d) {
  if (d.type === "readme")  return "#F59E0B";
  if (d.type === "article") return d.color;
  if (d.type === "wiki")    return d.color;
  return "#6B7280";
}

function nodeFill(d) {
  const c = nodeStroke(d);
  return c + "33";  // transparent fill
}

function isVisible(d) {
  if (d.type === "article" || d.type === "readme") {
    if (!activePorts.has(d.portal)) return false;
  }
  if ((d.type === "wiki" || d.type === "external") && !showExternal) return false;
  if (d.type === "broken" && !showBroken) return false;
  return true;
}

function linkVisible(l) {
  if (!isVisible(nodeById[l.source.id || l.source])) return false;
  if (!isVisible(nodeById[l.target.id || l.target])) return false;
  if (l.type === "internal" && !showInternal) return false;
  if ((l.type === "external" || l.type === "wiki") && !showExternal) return false;
  if (l.type === "broken" && !showBroken) return false;
  return true;
}

const nodeById = Object.fromEntries(DATA.nodes.map(n => [n.id, n]));

// ── simulation ─────────────────────────────────────────────────────────────
const simulation = d3.forceSimulation()
  .force("link", d3.forceLink().id(d => d.id).distance(d =>
      d.type === "internal" ? 130 : 160).strength(0.12))
  .force("charge", d3.forceManyBody().strength(d =>
      d.type === "article" || d.type === "readme" ? -450 : -60))
  .force("center", d3.forceCenter())
  .force("collide", d3.forceCollide().radius(d => nodeRadius(d) + 16).strength(0.85))
  // portal-sector force: pull articles/readme to their (angle × ring) target position
  .force("sector-x", d3.forceX(d => d._tx ?? 0).strength(d =>
      d.type === "readme" ? 0.9 : d.type === "article" ? 0.1 : 0))
  .force("sector-y", d3.forceY(d => d._ty ?? 0).strength(d =>
      d.type === "readme" ? 0.9 : d.type === "article" ? 0.1 : 0))
  // radial force only for external/wiki/broken (keeps them in outer ring)
  .force("radial", d3.forceRadial(RING_R[3], 0, 0).strength(d =>
      (d.type === "wiki" || d.type === "external" || d.type === "broken") ? 0.4 : 0))
  .velocityDecay(0.62)
  .alphaDecay(0.025);

// ── render ─────────────────────────────────────────────────────────────────
let linkSel, nodeSel;

function restart() {
  const visNodes = DATA.nodes.filter(isVisible);
  const visIds   = new Set(visNodes.map(n => n.id));
  const visLinks = DATA.links.filter(l => {
    const sid = l.source.id || l.source;
    const tid = l.target.id || l.target;
    return visIds.has(sid) && visIds.has(tid) && linkVisible(l);
  });

  // seed initial positions near each node's sector target
  visNodes.forEach(n => {
    if (n.x == null) {
      n.x = (n._tx ?? 0) + (Math.random() - 0.5) * 60;
      n.y = (n._ty ?? 0) + (Math.random() - 0.5) * 60;
    }
  });

  // links
  linkSel = container.selectAll(".link")
    .data(visLinks, d => `${d.source.id||d.source}-${d.target.id||d.target}-${d.type}`)
    .join(
      enter => enter.append("line")
        .attr("class", d => `link ${d.type}`)
        .attr("marker-end", d => `url(#arrow-${d.type})`),
      update => update.attr("class", d => `link ${d.type}`)
        .attr("marker-end", d => `url(#arrow-${d.type})`),
      exit => exit.remove()
    );

  // nodes
  nodeSel = container.selectAll(".node")
    .data(visNodes, d => d.id)
    .join(
      enter => {
        const g = enter.append("g").attr("class", d => `node${d.type === "readme" ? " readme-node" : ""}`).call(
          d3.drag()
            .on("start", dragstart)
            .on("drag",  dragged)
            .on("end",   dragend));

        g.append("circle")
          .attr("r", nodeRadius)
          .attr("fill", nodeFill)
          .attr("stroke", nodeStroke)
          .on("click", (e, d) => { e.stopPropagation(); selectNode(d); })
          .on("mouseenter", (e, d) => showTooltip(e, d))
          .on("mousemove",  (e)    => moveTooltip(e))
          .on("mouseleave", ()     => hideTooltip());

        g.append("text")
          .attr("dx", d => nodeRadius(d) + 4)
          .attr("dy", "0.35em")
          .text(d => d.short)
          .style("display", showLabels ? null : "none");

        return g;
      },
      update => {
        update.select("circle")
          .attr("r", nodeRadius)
          .attr("fill", nodeFill)
          .attr("stroke", nodeStroke);
        update.select("text")
          .attr("dx", d => nodeRadius(d) + 4)
          .text(d => d.short)
          .style("display", showLabels ? null : "none");
        return update;
      },
      exit => exit.remove()
    );

  simulation.nodes(visNodes);
  simulation.force("link").links(visLinks);
  simulation.alpha(0.3).restart();
  updateStats(visNodes, visLinks);
}

simulation.on("tick", () => {
  if (linkSel) linkSel
    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  if (nodeSel) nodeSel
    .attr("transform", d => `translate(${d.x},${d.y})`);
});

// ── drag ───────────────────────────────────────────────────────────────────
function dragstart(e, d) {
  if (!e.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x; d.fy = d.y;
}
function dragged(e, d)  { d.fx = e.x; d.fy = e.y; }
function dragend(e, d)  {
  if (!e.active) simulation.alphaTarget(0);
  d.fx = null; d.fy = null;
}

// ── selection & highlight ──────────────────────────────────────────────────
svg.on("click", () => {
  selectedNode = null;
  if (!pathMode) { clearHighlight(); clearInfo(); }
  else { pathSource = null; clearHighlight(); clearInfo(); pathStatus.textContent = "Нажмите на первую статью (A)"; }
});

function selectNode(d) {
  if (pathMode) { handlePathClick(d); return; }
  selectedNode = d;
  highlightNeighbors(d);
  showInfo(d);
}

function highlightNeighbors(d) {
  if (!nodeSel || !linkSel) return;
  const neighbors = new Set([d.id]);
  linkSel.each(l => {
    const sid = l.source.id || l.source;
    const tid = l.target.id || l.target;
    if (sid === d.id) neighbors.add(tid);
    if (tid === d.id) neighbors.add(sid);
  });
  nodeSel.classed("dimmed",      n => !neighbors.has(n.id))
         .classed("highlighted", n => n.id === d.id);
  // only direct edges visible; all others invisible
  linkSel
    .classed("highlighted", l => {
      const sid = l.source.id || l.source;
      const tid = l.target.id || l.target;
      return sid === d.id || tid === d.id;
    })
    .classed("bg-dimmed", l => {
      const sid = l.source.id || l.source;
      const tid = l.target.id || l.target;
      return sid !== d.id && tid !== d.id;
    });
}

function clearHighlight() {
  if (nodeSel) nodeSel
    .classed("dimmed",      false)
    .classed("highlighted", false)
    .classed("path-source", false)
    .classed("path-target", false)
    .classed("path-mid",    false);
  if (linkSel) linkSel
    .classed("highlighted", false)
    .classed("bg-dimmed",   false)
    .classed("path-link",   false);
}

// ── BFS pathfinding ─────────────────────────────────────────────────────────
// excludeSet: set of node IDs to skip as intermediate nodes (not src/tgt)
function bfs(srcId, tgtId, excludeSet = new Set()) {
  const adj = {};
  DATA.nodes.forEach(n => { adj[n.id] = []; });
  // only traverse link types that are currently rendered (match visibility flags)
  DATA.links.forEach(l => {
    if ((l.type === "external" || l.type === "wiki") && !showExternal) return;
    if (l.type === "broken" && !showBroken) return;
    if (l.type === "internal" && !showInternal) return;
    const sid = l.source.id || l.source;
    const tid = l.target.id || l.target;
    adj[sid].push({ to: tid, link: l });
    adj[tid].push({ to: sid, link: l }); // undirected for pathfinding
  });

  const prev = { [srcId]: null };
  const prevLink = {};
  const queue = [srcId];
  while (queue.length) {
    const cur = queue.shift();
    if (cur === tgtId) break;
    for (const { to, link } of (adj[cur] || [])) {
      if (!(to in prev) && (to === tgtId || !excludeSet.has(to))) {
        prev[to] = cur;
        prevLink[to] = link;
        queue.push(to);
      }
    }
  }
  if (!(tgtId in prev)) return null;

  const pathNodes = [];
  const pathLinks = new Set();
  let cur = tgtId;
  while (cur !== srcId) {
    pathNodes.push(cur);
    pathLinks.add(prevLink[cur]);
    cur = prev[cur];
  }
  pathNodes.push(srcId);
  return { nodes: new Set(pathNodes), links: pathLinks, ordered: [...pathNodes].reverse() };
}

// ── path mode ───────────────────────────────────────────────────────────────
const pathStatus = document.getElementById("path-status");
const btnPath    = document.getElementById("btn-path");

btnPath.addEventListener("click", () => {
  pathMode = !pathMode;
  pathSource = null;
  clearHighlight();
  clearInfo();
  if (pathMode) {
    btnPath.textContent = "✕ Выйти из режима пути";
    btnPath.style.borderColor = "#22c55e";
    btnPath.style.color = "#22c55e";
    pathStatus.textContent = "Нажмите на первую статью (A)";
    pathStatus.style.color = "#22c55e";
  } else {
    btnPath.textContent = "⬡ Включить режим пути";
    btnPath.style.borderColor = "#3a3f5c";
    btnPath.style.color = "#94a3b8";
    pathStatus.textContent = "Режим выключен";
    pathStatus.style.color = "#475569";
  }
});

function handlePathClick(d) {
  if (!pathSource) {
    pathSource = d;
    clearHighlight();
    nodeSel.classed("path-source", n => n.id === d.id);
    pathStatus.textContent = `A: ${d.short} — нажмите на B`;
    infoTitle.textContent = `Путь из: ${d.short}`;
    infoTitle.style.color = "#22c55e";
    infoBody.innerHTML = `<div class="stat" style="color:#64748b">Нажмите на вторую статью</div>`;
  } else if (d.id === pathSource.id) {
    pathSource = null;
    clearHighlight(); clearInfo();
    pathStatus.textContent = "Нажмите на первую статью (A)";
  } else {
    const excludeSet = pathAllowReadme ? new Set() : new Set(["README"]);
    let result = bfs(pathSource.id, d.id, excludeSet);
    let viaReadme = false;
    if (!result && !pathAllowReadme) {
      // fallback: try with README
      result = bfs(pathSource.id, d.id, new Set());
      viaReadme = !!result;
    }
    clearHighlight();
    if (result) {
      nodeSel
        .classed("dimmed",      n => !result.nodes.has(n.id))
        .classed("path-source", n => n.id === pathSource.id)
        .classed("path-target", n => n.id === d.id)
        .classed("path-mid",    n => result.nodes.has(n.id) && n.id !== pathSource.id && n.id !== d.id);
      linkSel
        .classed("path-link",  l => result.links.has(l))
        .classed("bg-dimmed",  l => !result.links.has(l));
      const steps = result.nodes.size - 1;
      const viaNote = viaReadme ? " (через README)" : "";
      infoTitle.textContent = `Путь найден: ${steps} ${steps === 1 ? "шаг" : steps < 5 ? "шага" : "шагов"}${viaNote}`;
      infoTitle.style.color = viaReadme ? "#f59e0b" : "#22c55e";
      infoBody.innerHTML = result.ordered.map(id => {
        const n = nodeById[id];
        const bullet = id === pathSource.id ? "🟢" : id === d.id ? "🟡" : "⚪";
        return `<div class="stat">${bullet} <span class="chip" style="border-left:3px solid ${n?.color||"#333"}">${n?.short||id}</span></div>`;
      }).join("");
      pathStatus.textContent = `${result.ordered.length} узлов в пути`;
    } else {
      infoTitle.textContent = "Путь не найден";
      infoTitle.style.color = "#ef4444";
      infoBody.innerHTML = `<div class="stat" style="color:#64748b">Нет пути между статьями по внутренним ссылкам</div>`;
      pathStatus.textContent = "Нет пути — выберите другие статьи";
    }
    pathSource = null;
    pathStatus.style.color = "#475569";
  }
}

// ── info panel ─────────────────────────────────────────────────────────────
function showInfo(d) {
  infoTitle.textContent = d.label;
  infoTitle.style.color = d.color || "#f1f5f9";

  const outLinks = DATA.links.filter(l => (l.source.id||l.source) === d.id);
  const inLinks  = DATA.links.filter(l => (l.target.id||l.target) === d.id);

  let html = "";
  if (d.type === "article" || d.type === "readme") {
    html += `<div class="stat">📄 <b>Файл:</b> ${d.file || "—"}</div>`;
    html += `<div class="stat">🔗 Входящих: <b>${d.in}</b> / Исходящих: <b>${d.out}</b></div>`;
    if (d.portal >= 0) {
      const pname = DATA.portals.find(p => p.id === d.portal)?.label || "";
      html += `<div class="stat">🗂 <b>${pname}</b></div>`;
    }
  } else if (d.type === "wiki" || d.type === "external") {
    html += `<div class="stat">🌐 <a href="${d.url||"#"}" target="_blank" style="color:#6366f1">${d.url||d.domain}</a></div>`;
    html += `<div class="stat">Упоминается: <b>${d.in}</b> раз</div>`;
  }

  // list out-links
  if (outLinks.length) {
    html += `<div class="stat" style="margin-top:8px;color:#475569;font-size:11px">ССЫЛКИ ОТСЮДА (${outLinks.length})</div>`;
    outLinks.slice(0, 8).forEach(l => {
      const tid = l.target.id || l.target;
      const tn = nodeById[tid];
      const name = tn ? tn.short : tid;
      html += `<span class="chip" style="border-left:3px solid ${tn?.color||'#333'}">${name}</span>`;
    });
    if (outLinks.length > 8) html += `<span class="chip">+${outLinks.length - 8} ещё</span>`;
  }

  // list in-links
  if (inLinks.length) {
    html += `<div class="stat" style="margin-top:8px;color:#475569;font-size:11px">ССЫЛКИ СЮДА (${inLinks.length})</div>`;
    inLinks.slice(0, 8).forEach(l => {
      const sid = l.source.id || l.source;
      const sn = nodeById[sid];
      const name = sn ? sn.short : sid;
      html += `<span class="chip" style="border-left:3px solid ${sn?.color||'#333'}">${name}</span>`;
    });
    if (inLinks.length > 8) html += `<span class="chip">+${inLinks.length - 8} ещё</span>`;
  }

  infoBody.innerHTML = html;
}

function clearInfo() {
  infoTitle.textContent = "Нажмите на узел";
  infoTitle.style.color = "#475569";
  infoBody.innerHTML = "";
}

// ── tooltip ────────────────────────────────────────────────────────────────
function showTooltip(e, d) {
  tooltip.style.opacity = "1";
  tooltip.innerHTML = `<strong>${d.label}</strong>
    <span>${d.type === "article" ? "Статья · Портал " + d.portal :
           d.type === "wiki"     ? "Wikipedia · " + (d.lang === "en" ? "EN" : "RU") :
           d.type === "external" ? "Внешний ресурс" :
           d.type === "readme"   ? "Главная страница" : d.type}
    </span>
    <span style="margin-top:4px;display:block">→ ${d.out}  ← ${d.in}</span>`;
  moveTooltip(e);
}
function moveTooltip(e) {
  const r = document.getElementById("canvas").getBoundingClientRect();
  let x = e.clientX - r.left + 14, y = e.clientY - r.top + 14;
  if (x + 270 > r.width)  x -= 280;
  if (y + 90  > r.height) y -= 100;
  tooltip.style.left = x + "px";
  tooltip.style.top  = y + "px";
}
function hideTooltip() { tooltip.style.opacity = "0"; }

// ── search ─────────────────────────────────────────────────────────────────
document.getElementById("search").addEventListener("input", e => {
  searchTerm = e.target.value.toLowerCase().trim();
  if (!nodeSel) return;
  if (!searchTerm) { clearHighlight(); return; }
  const match = new Set();
  DATA.nodes.forEach(n => {
    if ((n.label||"").toLowerCase().includes(searchTerm) ||
        (n.domain||"").toLowerCase().includes(searchTerm)) {
      match.add(n.id);
    }
  });
  const neighbors = new Set(match);
  DATA.links.forEach(l => {
    const sid = l.source.id||l.source, tid = l.target.id||l.target;
    if (match.has(sid)) neighbors.add(tid);
    if (match.has(tid)) neighbors.add(sid);
  });
  nodeSel.classed("dimmed",      n => !neighbors.has(n.id))
         .classed("highlighted", n => match.has(n.id));
  linkSel.classed("highlighted", l => {
    return match.has(l.source.id||l.source) || match.has(l.target.id||l.target);
  });
});

// ── toggle controls ────────────────────────────────────────────────────────
document.getElementById("tog-internal"   ).addEventListener("change", e => { showInternal = e.target.checked; restart(); });
document.getElementById("tog-external"   ).addEventListener("change", e => { showExternal = e.target.checked; restart(); });
document.getElementById("tog-broken"     ).addEventListener("change", e => { showBroken   = e.target.checked; restart(); });
document.getElementById("tog-readme-path").addEventListener("change", e => { pathAllowReadme = e.target.checked; });
document.getElementById("tog-labels"     ).addEventListener("change", e => {
  showLabels = e.target.checked;
  if (nodeSel) nodeSel.select("text").style("display", showLabels ? null : "none");
});

// ── orbital animation ──────────────────────────────────────────────────────
let orbitActive = false;
let orbitAngle1 = 0;   // ring 1 offset (clockwise)
let orbitAngle2 = 0;   // ring 2 offset (counter-clockwise)
let orbitLast   = null;
let orbitRAF    = null;
let flowEdges   = false;

function orbitStep(ts) {
  if (!orbitActive) return;
  if (orbitLast == null) orbitLast = ts;
  const dt = Math.min(ts - orbitLast, 50);
  orbitLast = ts;

  orbitAngle1 += 0.00014 * dt;   // ~45 s per revolution
  orbitAngle2 -= 0.00008 * dt;   // ~78 s, opposite direction

  const { width, height } = document.getElementById("canvas").getBoundingClientRect();
  const cx = width / 2, cy = height / 2;

  DATA.nodes.forEach(n => {
    if (n.type !== "article") return;
    const ring = nodeRing(n);
    const base = PORTAL_ANGLE[n.portal] ?? 0;
    const off  = ring === 1 ? orbitAngle1 : orbitAngle2;
    const r    = RING_R[ring];
    n._tx = cx + Math.cos(base + off) * r;
    n._ty = cy + Math.sin(base + off) * r;
  });

  simulation.force("sector-x").x(d => d._tx ?? cx);
  simulation.force("sector-y").y(d => d._ty ?? cy);
  if (simulation.alpha() < 0.08) simulation.alpha(0.08).restart();

  orbitRAF = requestAnimationFrame(orbitStep);
}

document.getElementById("btn-orbit").addEventListener("click", () => {
  orbitActive = !orbitActive;
  const btn = document.getElementById("btn-orbit");
  if (orbitActive) {
    btn.textContent = "⏹ Остановить вращение";
    btn.classList.add("active");
    orbitLast = null;
    orbitRAF = requestAnimationFrame(orbitStep);
  } else {
    btn.textContent = "⟳ Орбитальное вращение";
    btn.classList.remove("active");
    if (orbitRAF) { cancelAnimationFrame(orbitRAF); orbitRAF = null; }
    // snap back to original sector positions
    const { width, height } = document.getElementById("canvas").getBoundingClientRect();
    computeTargets(width / 2, height / 2);
    simulation.force("sector-x").x(d => d._tx ?? width / 2);
    simulation.force("sector-y").y(d => d._ty ?? height / 2);
    simulation.alpha(0.3).restart();
  }
});

document.getElementById("tog-flow").addEventListener("change", e => {
  flowEdges = e.target.checked;
  if (linkSel) linkSel.classed("flow-on", l => flowEdges && l.type === "internal");
});

// ── stats bar ──────────────────────────────────────────────────────────────
function updateStats(nodes, links) {
  const articles  = nodes.filter(n => n.type === "article" || n.type === "readme").length;
  const wikis     = nodes.filter(n => n.type === "wiki").length;
  const externals = nodes.filter(n => n.type === "external").length;
  document.getElementById("stats").textContent =
    `${articles} статей · ${wikis} вики · ${externals} сайтов · ${links.length} связей`;
}

// ── center on resize ───────────────────────────────────────────────────────
function recenter() {
  const { width, height } = document.getElementById("canvas").getBoundingClientRect();
  const cx = width / 2, cy = height / 2;
  simulation.force("center", d3.forceCenter(cx, cy));
  computeTargets(cx, cy);
  simulation.force("sector-x").x(d => d._tx ?? cx);
  simulation.force("sector-y").y(d => d._ty ?? cy);
  simulation.force("radial").x(cx).y(cy);
  // pin README to canvas center
  const rn = DATA.nodes.find(n => n.id === "README");
  if (rn) { rn.fx = cx; rn.fy = cy; }
  svg.attr("viewBox", `0 0 ${width} ${height}`);
  simulation.alpha(0.3).restart();
}
window.addEventListener("resize", recenter);

// ── init ───────────────────────────────────────────────────────────────────
recenter();
restart();
</script>
</body>
</html>
"""

# ── inject data & write ────────────────────────────────────────────────────

json_str = json.dumps(graph_data, ensure_ascii=False, separators=(",", ":"))
html_out = HTML.replace("GRAPH_DATA_PLACEHOLDER", json_str)

os.makedirs(OUTPUT.parent, exist_ok=True)
OUTPUT.write_text(html_out, encoding="utf-8")

# ── summary ────────────────────────────────────────────────────────────────

arts    = [n for n in nodes.values() if n["type"] == "article"]
wikis   = [n for n in nodes.values() if n["type"] == "wiki"]
exts    = [n for n in nodes.values() if n["type"] == "external"]
brokens = [n for n in nodes.values() if n["type"] == "broken"]

print(f"✓  Граф сгенерирован: {OUTPUT}")
print(f"   Узлы: {len(arts)} статей, {len(wikis)} Wikipedia, {len(exts)} сайтов, {len(brokens)} вне репо")
print(f"   Рёбра: {len(edges)} связей")
if brokens:
    print(f"   Ссылки вне репо:")
    for b in brokens:
        print(f"      - {b['label']}")
print(f"\n   Открой в браузере: open {OUTPUT}")
