"use strict";
(function () {
  const D = window.RHIZOTOMOS;
  const R = D.results;
  const PE = "experts' reading + Claude's matching (pass E)";
  const PR = "experts' reading + Claude's matching (pass E, repeat run)";
  const PA = "Claude's reading + Claude's matching (pass A)";
  const GE = "experts' reading + everything good";
  const GA = "Claude's reading + everything good";
  const WO = "experts' reading + word overlap";
  const GRADES = ["WEAK", "MODERATE", "STRONG"];
  const REPO = "https://github.com/ashank-crazy/rhizotomos";
  const CAT_OF = {};
  for (const [cat, chars] of Object.entries(D.categories)) for (const c of chars) CAT_OF[c] = cat;
  const app = document.getElementById("app");
  const tip = document.getElementById("tip");

  // -- helpers -------------------------------------------------------------------------------------------------
  function el(tag, attrs, ...kids) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null || v === false) continue;
      if (k === "class") n.className = v;
      else if (k === "text") n.textContent = v;
      else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v === true ? "" : v);
    }
    for (const kid of kids.flat(Infinity)) {
      if (kid == null || kid === false) continue;
      n.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
    }
    return n;
  }
  const pct = (x) => (x == null ? "–" : Math.round(100 * x) + "%");
  const num = (x) => (x == null ? "–" : x.toFixed(2));
  const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
  const fold = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const inFloras = (p) => p.candidates.filter((c) => c.in_floras);

  function bestShare(p, key) {
    // Share of our best-scoring candidates that are also the experts' best (as in evaluate.top_pick).
    const c = inFloras(p);
    if (c.length < 2) return null;
    const top = Math.max(...c.map((x) => x.expert[0]));
    const theirs = new Set(c.filter((x) => x.expert[0] === top).map((x) => x.df_name));
    const best = Math.max(...c.map((x) => x[key][0]));
    const ours = c.filter((x) => x[key][0] === best);
    return ours.filter((x) => theirs.has(x.df_name)).length / ours.length;
  }
  function expertsBest(p) {
    const c = inFloras(p);
    if (!c.length) return [];
    const top = Math.max(...c.map((x) => x.expert[0]));
    return c.filter((x) => x.expert[0] === top).map((x) => x.name);
  }

  // -- tooltip ---------------------------------------------------------------------------------------------------
  function hideTip() { tip.hidden = true; }
  function placeTip(x, y) {
    const pad = 12, w = tip.offsetWidth, h = tip.offsetHeight;
    let left = x + pad, top = y - h - pad;
    if (left + w > innerWidth - 8) left = Math.max(8, x - w - pad);
    if (top < 8) top = y + pad;
    tip.style.left = left + "px";
    tip.style.top = top + "px";
  }
  function attachTip(node, lines) {
    const show = (x, y) => {
      tip.replaceChildren(...lines().filter(Boolean).map(([v, l]) =>
        el("div", { class: "tip-row" }, el("strong", { text: v }), el("span", { text: l }))));
      tip.hidden = false;
      placeTip(x, y);
    };
    node.addEventListener("pointermove", (e) => show(e.clientX, e.clientY));
    node.addEventListener("pointerleave", hideTip);
    node.addEventListener("focus", () => { const r = node.getBoundingClientRect(); show(r.left + 24, r.top); });
    node.addEventListener("blur", hideTip);
  }

  // -- theme -----------------------------------------------------------------------------------------------------
  const themeBtn = document.getElementById("theme");
  const THEMES = ["auto", "light", "dark"];
  let theme = "auto";
  try { theme = localStorage.getItem("rhizotomos-theme") || "auto"; } catch (e) { /* storage blocked */ }
  function applyTheme() {
    if (theme === "auto") delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = theme;
    themeBtn.textContent = "Theme: " + theme;
  }
  themeBtn.addEventListener("click", () => {
    theme = THEMES[(THEMES.indexOf(theme) + 1) % THEMES.length];
    try { localStorage.setItem("rhizotomos-theme", theme); } catch (e) { /* storage blocked */ }
    applyTheme();
  });
  applyTheme();

  // -- router ----------------------------------------------------------------------------------------------------
  function route() {
    const [page, arg] = location.hash.replace(/^#\/?/, "").split("/");
    hideTip();
    app.replaceChildren();
    const nav = page === "validation" || page === "method" ? page : "plants";
    document.querySelectorAll("nav a").forEach((a) => a.classList.toggle("on", a.dataset.page === nav));
    if (page === "plant") renderPlant(decodeURIComponent(arg || ""));
    else if (page === "validation") renderValidation();
    else if (page === "method") renderMethod();
    else renderHome();
    window.scrollTo(0, 0);
  }
  window.addEventListener("hashchange", route);

  // -- home ------------------------------------------------------------------------------------------------------
  function tile(label, value, sub) {
    return el("div", { class: "tile" }, el("p", { class: "label", text: label }), el("p", { class: "value", text: value }),
      el("p", { class: "sub", text: sub }));
  }
  function renderHome() {
    document.title = "Rhizotomos · Which plant did Dioscorides mean?";
    const E = R.verdicts[PE].all, A = R.verdicts[PA].all, M = R.matching["Claude (pass E)"].all, B = R.baselines.all;
    app.append(
      el("section", { class: "hero" },
        el("p", { class: "eyebrow", text: "EthnoHack 2026 · Track 1, traditional knowledge mining" }),
        el("h1", { text: "Which plant did Dioscorides mean?" }),
        el("p", { class: "lede" },
          "In the first century CE, Dioscorides described hundreds of medicinal plants in Greek. Any study that turns one " +
          "of his remedies into a modern lead first has to know which species he meant, and the usual dictionary answers " +
          "are often doubtful. Botanists at Kew and ZHAW (Lardos et al., 2024) built a careful method to decide, and " +
          "applied it by hand to 61 plants. Rhizotomos has an AI model, Claude, repeat each step of that method, and " +
          "checks every step against the experts' own published data."),
        el("p", { class: "lede" }, "Think of a line-up: the ancient description is the witness statement, the candidate " +
          "species are the suspects, and the experts have already solved 61 cases, so the detective can be scored.")),
      el("section", { class: "kpis", "aria-label": "Headline results" },
        tile("Verdicts that agree with the experts", pct(E.agreement),
          `Claude matching the experts' reading to the floras, ${E.candidates} candidates`),
        tile("Same best candidate", pct(E.top_pick),
          `${B.plants_with_choice} plants with a choice · most-cited species: ${pct(B.most_cited_top_pick)}`),
        tile("Statements judged as the experts did", pct(M.agreement),
          `${M.compared} statement pairs · weighted κ ${num(M.kappa_linear)}`),
        tile("End to end, from the Greek", pct(A.agreement),
          `verdict agreement when Claude also reads the Greek · same best candidate ${pct(A.top_pick)}`)),
      el("p", { class: "kpi-note" }, `A second, independent run of the matching gives the same verdict for ` +
        `${pct(R.stability.all.same_grade)} of candidates and the same best candidate for ${pct(R.stability.all.same_best)} ` +
        "of plants. Every figure, with intervals and baselines, is on the ",
        el("a", { href: "#/validation", text: "validation page" }), "."),
      plantIndex());
  }
  function plantIndex() {
    const input = el("input", { type: "search", class: "search", placeholder: "Search Greek, English or Latin names",
      "aria-label": "Search plants" });
    const grid = el("div", { class: "cards" });
    const count = el("p", { class: "count", "aria-live": "polite" });
    const draw = () => {
      const q = fold(input.value.trim());
      const list = D.plants.filter((p) => !q || fold([p.key, p.greek, p.jc, p.chapter, ...p.candidates.map((c) => c.name)]
        .join(" ")).includes(q));
      grid.replaceChildren(...list.map(card));
      count.textContent = `${list.length} of ${D.plants.length} plants, in the order of the book`;
    };
    input.addEventListener("input", draw);
    draw();
    return el("section", { class: "index" },
      el("div", { class: "index-head" }, el("h2", { text: "The 61 plants" }), input, count), grid);
  }
  function agreeLine(share) {
    if (share == null) return el("span", { class: "agree-line muted", text: "Only one candidate to choose from" });
    if (share === 1) return el("span", { class: "agree-line yes", text: "✓ From the Greek, Claude picks the same" });
    if (share === 0) return el("span", { class: "agree-line no", text: "✗ From the Greek, Claude picks another" });
    return el("span", { class: "agree-line", text: "≈ From the Greek, Claude ties it with others" });
  }
  function card(p) {
    const best = expertsBest(p), n = inFloras(p).length;
    return el("a", { class: "card", href: `#/plant/${p.slug}` },
      el("span", { class: "greek", lang: "grc", text: p.greek }),
      el("span", { class: "name", text: cap(p.key) }),
      el("span", { class: "meta", text: `De materia medica ${p.chapter} · ${n} candidate${n === 1 ? "" : "s"} in the floras` }),
      best.length ? el("span", { class: "best" }, "Experts' best: ", el("i", { text: best.join(", ") }))
        : el("span", { class: "best muted", text: "No candidate described in the floras" }),
      agreeLine(bestShare(p, "A")));
  }

  // -- plant page ------------------------------------------------------------------------------------------------
  function gradeCell(v, ref) {
    if (!v) return el("td", { class: "muted", text: "–" });
    const [score, g] = v;
    const kids = [el("span", { class: "score", text: score }), el("span", { class: `grade ${g}`, text: g })];
    if (ref) {
      const same = ref[1] === g;
      kids.push(" ", el("span", { class: same ? "mark yes" : "mark no", "aria-hidden": "true", text: same ? "✓" : "✗" }),
        el("span", { class: "sr", text: same ? "same verdict as the experts" : "different verdict from the experts" }));
    }
    return el("td", { class: "grade-cell" }, kids);
  }
  function callCell(call) {
    return el("td", {}, el("span", { class: `call ${call || "none"}`, text: call || "–" }));
  }
  function matchDetail(p, c) {
    const rowsE = Object.entries(c.calls).map(([ch, v]) =>
      el("tr", { class: v.x && v.E && v.x !== v.E ? "differs" : null },
        el("td", { text: ch }), el("td", { text: p.expert[ch] }), el("td", { text: c.modern[ch] || "–" }),
        callCell(v.x), callCell(v.E)));
    const ours = Object.fromEntries(p.quotes.filter((q) => q.kind === "character").map((q) => [q.char, q.en]));
    const rowsA = D.characters.filter((ch) => ch in c.callsA).map((ch) => [ch, c.callsA[ch]]).map(([ch, call]) => {
      const modern = D.categories[CAT_OF[ch]].filter((k) => c.modern[k]).map((k) => c.modern[k]).join(" · ");
      return el("tr", {}, el("td", { text: ch }), el("td", { text: ours[ch] || "" }), el("td", { text: modern || "–" }),
        callCell(call));
    });
    const table = (head, rows) => el("div", { class: "table-wrap" }, el("table", {},
      el("thead", {}, el("tr", {}, head.map((h) => el("th", { scope: "col", text: h })))), el("tbody", {}, rows)));
    return el("div", { class: "detail-grid" },
      el("div", {},
        el("h4", { text: "The experts' reading against the flora" }),
        el("p", { text: "Each statement the experts read in Dioscorides against the same character in the flora. " +
          "Highlighted rows are where Claude's call differs from the experts'." }),
        rowsE.length ? table(["Character", "Dioscorides (experts)", "Flora", "Experts", "Claude"], rowsE)
          : el("p", { class: "muted", text: "Nothing to compare." })),
      el("div", {},
        el("h4", { text: "Claude's own reading against the flora" }),
        el("p", { text: "Each statement Claude read in the Greek, against what the flora says about the same organ. " +
          "There is no expert call for these." }),
        rowsA.length ? table(["Character", "Dioscorides (Claude)", "Flora, same organ", "Claude"], rowsA)
          : el("p", { class: "muted", text: "Nothing to compare." })));
  }
  function candidatesTable(p) {
    const tbody = el("tbody");
    for (const c of p.candidates) {
      if (!c.in_floras) {
        tbody.append(el("tr", { class: "absent" }, el("td", {}, el("i", { text: c.name })), el("td", { text: c.family || "" }),
          el("td", { class: "num", text: c.cited ?? "" }),
          el("td", { colspan: 3, text: "Not described in Flora of Turkey or Flora of Cyprus, so not scored" })));
        continue;
      }
      const detail = el("tr", { class: "detail", hidden: true }, el("td", { colspan: 6 }, matchDetail(p, c)));
      const btn = el("button", { type: "button", class: "ghost expand", "aria-expanded": "false", text: "Show matches" });
      btn.addEventListener("click", () => {
        const open = detail.hidden;
        detail.hidden = !open;
        btn.setAttribute("aria-expanded", String(open));
        btn.textContent = open ? "Hide matches" : "Show matches";
      });
      tbody.append(el("tr", {},
        el("td", {}, el("i", { text: c.name }), btn), el("td", { text: c.family || "" }),
        el("td", { class: "num", text: c.cited ?? 0 }),
        gradeCell(c.expert), gradeCell(c.E, c.expert), gradeCell(c.A, c.expert)), detail);
    }
    const head = ["Species", "Family", "Times proposed", "Experts", "Claude, experts' reading", "Claude, from the Greek"];
    return el("div", { class: "table-wrap" }, el("table", { class: "cands" },
      el("thead", {}, el("tr", {}, head.map((h, i) => el("th", { scope: "col", class: i === 2 ? "num" : null, text: h })))),
      tbody));
  }
  function greekSection(p) {
    const q = p.quotes;
    const cuts = new Set([0, p.text.length]);
    q.forEach((x) => { if (x.span) { cuts.add(x.span[0]); cuts.add(x.span[1]); } });
    const pts = [...cuts].sort((a, b) => a - b);
    const textEl = el("p", { class: "greek greek-text", lang: "grc" });
    const marks = [], rows = [];
    const setOn = (ids) => {
      const s = new Set(ids);
      marks.forEach((m) => m.classList.toggle("on", m._ids.some((j) => s.has(j))));
      rows.forEach((r) => r.classList.toggle("on", s.has(r._id)));
    };
    for (let i = 0; i < pts.length - 1; i++) {
      const [a, b] = [pts[i], pts[i + 1]];
      const ids = q.map((x, j) => (x.span && x.span[0] <= a && x.span[1] >= b ? j : -1)).filter((j) => j >= 0);
      const s = p.text.slice(a, b);
      if (!ids.length) { textEl.append(s); continue; }
      const cmp = ids.every((j) => q[j].kind === "comparison");
      const m = el("mark", { class: cmp ? "q cmp" : "q", tabindex: "0" }, s);
      m._ids = ids;
      m.addEventListener("pointerenter", () => setOn(ids));
      m.addEventListener("focus", () => setOn(ids));
      m.addEventListener("pointerleave", () => setOn([]));
      m.addEventListener("blur", () => setOn([]));
      attachTip(m, () => ids.map((j) => [q[j].char, q[j].en]));
      marks.push(m);
      textEl.append(m);
    }
    // Readings table: every character either reading fills, in the experts' order, then the comparisons.
    const byChar = {};
    q.forEach((x, j) => { if (x.kind === "character") byChar[x.char] = j; });
    const tbody = el("tbody");
    const addRow = (label, j, expert, isCmp) => {
      const x = j == null ? null : q[j];
      const tr = el("tr", { class: isCmp ? "cmp-row" : null, "data-q": j == null ? null : String(j) },
        el("td", { text: label }),
        el("td", {}, x ? [x.en, el("span", { class: "greek q-greek", lang: "grc", text: x.greek })] : el("span", { class: "muted", text: "–" })),
        el("td", { text: expert || "–", class: expert ? null : "muted" }));
      if (j != null) {
        tr._id = j;
        tr.addEventListener("pointerenter", () => setOn([j]));
        tr.addEventListener("pointerleave", () => setOn([]));
        rows.push(tr);
      }
      tbody.append(tr);
    };
    for (const ch of D.characters) {
      if (ch in byChar || p.expert[ch]) addRow(ch, byChar[ch], p.expert[ch], false);
    }
    const expertCmp = { ...p.expert_comparisons };
    q.forEach((x, j) => {
      if (x.kind !== "comparison") return;
      const organ = x.cat;
      addRow(`Like another plant (${organ})`, j, expertCmp[organ], true);
      delete expertCmp[organ];
    });
    for (const [organ, v] of Object.entries(expertCmp)) addRow(`Like another plant (${organ})`, null, v, true);

    return el("div", { class: "plant-grid" },
      el("div", { class: "text-panel" },
        el("p", { class: "key" },
          el("span", {}, el("i", { style: "background:var(--hl-on)" }), "statement Claude read"),
          el("span", {}, el("i", { style: "background:var(--cmp-on)" }), "comparison with another plant")),
        textEl,
        p.rv.length ? el("details", { class: "rv" }, el("summary", { text: "Other names in the manuscripts (Recensio Vulgaris)" }),
          p.rv.map((s) => el("p", { class: "greek", lang: "grc", text: s }))) : null),
      el("div", { class: "table-wrap" }, el("table", { class: "readings" },
        el("thead", {}, el("tr", {}, ["Character", "Claude's reading of the Greek", "Experts' reading"].map((h) =>
          el("th", { scope: "col", text: h })))), tbody)));
  }
  function renderPlant(slug) {
    const p = D.plants.find((x) => x.slug === slug);
    if (!p) {
      app.append(el("p", { text: "No plant with that name." }), el("a", { href: "#/", text: "See all plants" }));
      return;
    }
    document.title = `${cap(p.key)} · Rhizotomos`;
    const n = inFloras(p).length;
    app.append(...[
      el("a", { class: "back", href: "#/", text: "← All plants" }),
      el("header", { class: "plant-head" },
        el("h1", {}, el("span", { class: "greek", lang: "grc", text: p.greek }), el("span", { class: "translit", text: cap(p.key) })),
        el("p", { class: "meta" }, `De materia medica ${p.chapter} (Wellmann's numbering) · in John the Physician's `,
          el("i", { text: "Therapeutics" }), " (13th century) as ", el("span", { class: "greek", lang: "grc", text: p.jc }))),
      p.seen ? el("p", { class: "note" }, el("strong", { text: "Seen during development. " }),
        `The ${p.seen.join("; ")} for this plant were looked at while the pipeline was being built, so it is left out ` +
        "of the “unseen” figures.") : null,
      el("h2", { text: "Candidate species" }),
      el("p", { class: "section-intro" },
        `Scored with the experts' rule: each organ (leaf, flower, habitat…) gets the average of its match calls, and the ` +
        `score is the number of organs that agree minus those that disagree. STRONG is 5 or more, MODERATE 3 or 4, ` +
        `WEAK 2 or less. “Times proposed” counts earlier identifications in the literature. ` +
        (n ? "Open a candidate to see every match." : "")),
      candidatesTable(p),
      el("h2", { text: "The Greek text and the two readings" }),
      el("p", { class: "section-intro", text: "Every statement Claude took from the chapter carries a quote, and each quote " +
        "was checked by code to occur in the Greek. Point at a highlight or a row to link the two." }),
      greekSection(p)].filter(Boolean));
  }

  // -- validation ------------------------------------------------------------------------------------------------
  function barChart(title, sub, rows) {
    rows = [...rows].sort((a, b) => b.value - a.value);
    const at = (v) => (v * 86).toFixed(2) + "%";
    const ticks = [0, 0.25, 0.5, 0.75, 1];
    const body = el("div", { class: "bars", role: "list" });
    for (const r of rows) {
      const right = Math.max(r.value, r.ci ? r.ci[1] : 0);
      const track = el("div", { class: "track" },
        ticks.map((t) => el("span", { class: t === 0 ? "gl base" : "gl", style: `left:${at(t)}` })),
        el("span", { class: r.claude ? "fill claude" : "fill", style: `width:${at(r.value)}` }),
        r.ci ? el("span", { class: "ci", style: `left:${at(r.ci[0])};width:calc(${at(r.ci[1])} - ${at(r.ci[0])})` }) : null,
        el("span", { class: "val", style: `left:calc(${at(right)} + 6px)`, text: pct(r.value) }));
      const label = `${r.label}: ${pct(r.value)}` + (r.ci ? `, 95% interval ${pct(r.ci[0])} to ${pct(r.ci[1])}` : "");
      const row = el("div", { class: "bar-row", role: "listitem", tabindex: "0", "aria-label": label },
        el("span", { class: "bar-label", text: r.label }), track);
      attachTip(row, () => [[pct(r.value), r.label], r.ci && [`${pct(r.ci[0])} to ${pct(r.ci[1])}`, "95% interval over plants"],
        r.extra]);
      body.append(row);
    }
    const axis = el("div", { class: "bar-row axis-row", "aria-hidden": "true" }, el("span"),
      el("div", { class: "track" }, ticks.map((t) => el("span", { class: "tick", style: `left:${at(t)}`, text: pct(t) }))));
    return el("figure", { class: "chart" },
      el("figcaption", {}, el("h3", { text: title }), el("p", { text: sub })),
      el("p", { class: "legend" },
        el("span", {}, el("i", { style: "background:var(--bar)" }), "Claude"),
        el("span", {}, el("i", { style: "background:var(--bar-base)" }), "baseline"),
        el("span", {}, el("span", { class: "whisker" }), "95% interval")),
      body, axis);
  }
  function heat(title, note, matrix, rowLabels, colLabels, rowName, colName) {
    const max = Math.max(1, ...rowLabels.flatMap((r) => colLabels.map((c) => matrix[r][c])));
    const table = el("table", { class: "heat" },
      el("thead", {}, el("tr", {}, el("th", { scope: "col", text: "" }), colLabels.map((c) => el("th", { scope: "col", text: c })))),
      el("tbody", {}, rowLabels.map((r) => el("tr", {}, el("th", { scope: "row", text: r }), colLabels.map((c) => {
        const n = matrix[r][c];
        const step = n ? Math.min(6, 1 + Math.floor((5 * n) / max)) : 0;
        const td = el("td", { class: "h" + step, tabindex: "0", text: n });
        attachTip(td, () => [[String(n), `${rowName} ${r}, ${colName} ${c}`]]);
        return td;
      })))));
    return el("figure", { class: "heat-fig chart" }, el("figcaption", {}, el("h3", { text: title }), el("p", { text: note })),
      el("div", { class: "table-wrap", style: "border:0" }, table));
  }
  function metricTable() {
    const V = R.verdicts, B = R.baselines;
    const rows = Object.entries(V).map(([name, v]) => {
      const [reading, matching] = name.split(" + ");
      return el("tr", {}, el("td", { text: cap(reading) }), el("td", { text: matching }),
        el("td", { class: "num", text: `${pct(v.all.agreement)} (${pct(v.ci.agreement[0])}–${pct(v.ci.agreement[1])})` }),
        el("td", { class: "num", text: `${num(v.all.kappa_linear)} (${num(v.ci.kappa_linear[0])}–${num(v.ci.kappa_linear[1])})` }),
        el("td", { class: "num", text: num(v.all.spearman) }),
        el("td", { class: "num", text: `${pct(v.all.top_pick)} (${pct(v.ci.top_pick[0])}–${pct(v.ci.top_pick[1])})` }),
        el("td", { class: "num", text: pct(v.unseen.agreement) }), el("td", { class: "num", text: pct(v.unseen.top_pick) }));
    });
    const c = B.ci.most_cited_top_pick;
    rows.push(el("tr", {}, el("td", { text: "–" }), el("td", { text: "species most often proposed in the literature" }),
      el("td", { class: "num", text: "–" }), el("td", { class: "num", text: "–" }), el("td", { class: "num", text: "–" }),
      el("td", { class: "num", text: `${pct(B.all.most_cited_top_pick)} (${pct(c[0])}–${pct(c[1])})` }),
      el("td", { class: "num", text: "–" }), el("td", { class: "num", text: pct(B.unseen.most_cited_top_pick) })));
    rows.push(el("tr", {}, el("td", { text: "–" }), el("td", { text: `always ${B.all.majority_grade}` }),
      el("td", { class: "num", text: pct(B.all.majority_agreement) }), el("td", { class: "num", text: "0" }),
      el("td", { class: "num", text: "–" }), el("td", { class: "num", text: "–" }),
      el("td", { class: "num", text: pct(B.unseen.majority_agreement) }), el("td", { class: "num", text: "–" })));
    rows.push(el("tr", {}, el("td", { text: "–" }), el("td", { text: "random pick" }),
      el("td", { class: "num", text: "–" }), el("td", { class: "num", text: "–" }), el("td", { class: "num", text: "–" }),
      el("td", { class: "num", text: pct(B.all.chance_top_pick) }), el("td", { class: "num", text: "–" }),
      el("td", { class: "num", text: pct(B.unseen.chance_top_pick) })));
    const head = ["Reading", "Matching", "Same verdict", "Weighted κ", "Spearman ρ", "Same best candidate",
      "Same verdict, unseen", "Best candidate, unseen"];
    return el("div", { class: "table-wrap" }, el("table", {},
      el("thead", {}, el("tr", {}, head.map((h, i) => el("th", { scope: "col", class: i > 1 ? "num" : null, text: h })))),
      el("tbody", {}, rows)));
  }
  function renderValidation() {
    document.title = "Validation · Rhizotomos";
    const V = R.verdicts, B = R.baselines.all, M = R.matching, rep = R.replication;
    const cc = R.category_counts, A = R.reading.all, AU = R.reading.unseen;
    const n = V[PE].all.candidates;
    const verdictRows = [
      { label: "Claude matching the experts' reading", value: V[PE].all.agreement, ci: V[PE].ci.agreement, claude: true,
        extra: [num(V[PE].all.kappa_linear), "weighted κ"] },
      { label: "Claude matching the experts' reading, repeat run", value: V[PR].all.agreement, ci: V[PR].ci.agreement, claude: true,
        extra: [num(V[PR].all.kappa_linear), "weighted κ"] },
      { label: "Claude end to end, from the Greek", value: V[PA].all.agreement, ci: V[PA].ci.agreement, claude: true,
        extra: [num(V[PA].all.kappa_linear), "weighted κ"] },
      { label: "Everything “good”, experts' reading", value: V[GE].all.agreement, ci: V[GE].ci.agreement },
      { label: "Everything “good”, Claude's reading", value: V[GA].all.agreement, ci: V[GA].ci.agreement },
      { label: "Word overlap, experts' reading", value: V[WO].all.agreement, ci: V[WO].ci.agreement },
      { label: `Always ${B.majority_grade}`, value: B.majority_agreement },
    ];
    const topRows = [
      { label: "Claude matching the experts' reading", value: V[PE].all.top_pick, ci: V[PE].ci.top_pick, claude: true },
      { label: "Claude matching the experts' reading, repeat run", value: V[PR].all.top_pick, ci: V[PR].ci.top_pick, claude: true },
      { label: "Claude end to end, from the Greek", value: V[PA].all.top_pick, ci: V[PA].ci.top_pick, claude: true },
      { label: "Everything “good”, experts' reading", value: V[GE].all.top_pick, ci: V[GE].ci.top_pick },
      { label: "Everything “good”, Claude's reading", value: V[GA].all.top_pick, ci: V[GA].ci.top_pick },
      { label: "Most often proposed in the literature", value: B.most_cited_top_pick, ci: R.baselines.ci.most_cited_top_pick },
      { label: "Word overlap, experts' reading", value: V[WO].all.top_pick, ci: V[WO].ci.top_pick },
      { label: "Random pick", value: B.chance_top_pick },
    ];
    const M_LABEL = { "Claude (pass E)": "Claude", "Claude (pass E, repeat run)": "Claude, repeat run",
      "all good": "Everything “good”", "word overlap": "Word overlap" };
    const mRows = Object.entries(M).map(([name, m]) => ({
      label: M_LABEL[name] || name, value: m.all.agreement, ci: m.ci.agreement, claude: name.startsWith("Claude"),
      extra: [num(m.all.kappa_linear), "weighted κ"] }));
    const S = R.stability.all, SU = R.stability.unseen;
    const sRow = (label, all, ci, unseen) => el("tr", {}, el("td", { text: label }),
      el("td", { class: "num", text: all + (ci ? ` (${pct(ci[0])}–${pct(ci[1])})` : "") }), el("td", { class: "num", text: unseen }));
    const mE = M["Claude (pass E)"].all;
    app.append(
      el("p", { class: "eyebrow", text: "Validation" }),
      el("h1", { text: "How close does Claude come to the experts?" }),
      el("p", { class: "lede" },
        `The reference is the experts' own botanical verdict for each candidate (Stage 5 of Lardos et al.). Their scoring ` +
        `rule, re-applied in code to their published match calls, reproduces ${rep.agree} of the ${rep.checked} verdicts ` +
        `they published, so every configuration below is scored by that same rule. “Unseen” leaves out the ` +
        `${R.seen_plants.length} plants whose expert data was looked at while the pipeline was being built; the other ` +
        `${R.plants.unseen} were never seen before all calls were made. Intervals are 95% bootstrap intervals over plants.`),
      el("div", { class: "charts" },
        barChart("Same verdict as the experts", `Share of ${n} candidates given the same STRONG, MODERATE or WEAK verdict`, verdictRows),
        barChart("Same best candidate as the experts", `Share of the ${B.plants_with_choice} plants with two or more candidates`, topRows)),
      el("h2", { text: "What the baselines show" }),
      el("ul", { class: "prose" },
        el("li", {}, el("strong", { text: "Calling every statement “good” is a strong baseline. " }),
          "The experts' rule rewards how much the flora says about a candidate, so coverage alone gets " +
          `${pct(V[GE].all.agreement)} of verdicts right. Claude's matching adds ${Math.round(100 * (V[PE].all.agreement - V[GE].all.agreement))} ` +
          `points on the experts' reading and ${Math.round(100 * (V[PA].all.agreement - V[GA].all.agreement))} on its own reading.`),
        el("li", {}, el("strong", { text: "Word overlap fails. " }),
          "Dioscorides and the modern floras describe the same plant in different words (“rough” against “villous”), so " +
          `matching shared words agrees with the experts on ${pct(M["word overlap"].all.agreement)} of statements.`),
        el("li", {}, el("strong", { text: "Reading the Greek is the harder step. " }),
          `End to end, verdict agreement falls from ${pct(V[PE].all.agreement)} to ${pct(V[PA].all.agreement)}. Per candidate, ` +
          `Claude's reading finds ${cc["pass A"].positive.toFixed(2)} organs that agree against the experts' ` +
          `${cc.experts.positive.toFixed(2)}, while disagreeing organs stay about as rare (${cc["pass A"].negative.toFixed(2)} ` +
          `against ${cc.experts.negative.toFixed(2)}). The experts extracted modern descriptions only for the characters in ` +
          "their own reading, so a statement Claude finds anywhere else has nothing to be matched against."),
        el("li", {}, el("strong", { text: "The seen plants did not flatter the results. " }),
          `On the ${R.plants.unseen} unseen plants the figures are ${pct(V[PE].unseen.agreement)} and ` +
          `${pct(V[PA].unseen.agreement)} for verdicts, ${pct(V[PE].unseen.top_pick)} and ${pct(V[PA].unseen.top_pick)} for ` +
          "the best candidate.")),
      el("h2", { text: "All verdict figures" }),
      metricTable(),
      el("div", { class: "heat-grid", style: "margin-top:14px" },
        heat("Verdicts, Claude matching the experts' reading", "Rows: the experts' verdict. Columns: Claude's.",
          V[PE].all.confusion, GRADES, GRADES, "experts", "Claude"),
        heat("Verdicts, Claude end to end", "Rows: the experts' verdict. Columns: Claude's.",
          V[PA].all.confusion, GRADES, GRADES, "experts", "Claude")),
      el("h2", { text: "Single statements" }),
      el("p", { class: "section-intro", text: `Each pair is one statement of the experts' reading against the flora's value ` +
        `for the same character: exactly the ${mE.compared} pairs the experts judged themselves. The experts left ` +
        `${mE.expert_missing} more without a call.` }),
      el("div", { class: "charts" },
        barChart("Same call as the experts", `Share of ${mE.compared} statement pairs called good, partial or no as the experts did`, mRows),
        heat("Calls, Claude against the experts", `Rows: the experts' call. Columns: Claude's. Weighted κ ${num(mE.kappa_linear)}; ` +
          `the two agree on whether a statement fits or contradicts in ${pct(mE.direction_agreement)} of pairs.`,
          mE.confusion, ["no", "partial", "good"], ["no", "partial", "good"], "experts", "Claude")),
      el("h2", { text: "Run to run" }),
      el("p", { class: "section-intro", text: "The matching on the experts' reading was made a second time, in a new " +
        "session, from the same blind batches and without opening the first run's calls. How often do the two runs agree " +
        `with each other? “Unseen” here also leaves out ${R.seen_before_repeat.join(", ")}, seen before the repeat run ` +
        `(${R.plants.unseen_repeat} plants).` }),
      el("div", { class: "table-wrap" }, el("table", {},
        el("thead", {}, el("tr", {}, ["Both runs give", "All", "Unseen"].map((h, i) =>
          el("th", { scope: "col", class: i ? "num" : null, text: h })))),
        el("tbody", {},
          sRow(`the same call (${S.calls} statement pairs)`, pct(S.same_call), S.ci.same_call, pct(SU.same_call)),
          sRow("the same call, weighted κ", num(S.kappa_linear), null, num(SU.kappa_linear)),
          sRow("the same fit or contradiction", pct(S.same_direction), null, pct(SU.same_direction)),
          sRow(`the same verdict (${S.candidates} candidates)`, pct(S.same_grade), S.ci.same_grade, pct(SU.same_grade)),
          sRow("the same verdict, weighted κ", num(S.grade_kappa_linear), null, num(SU.grade_kappa_linear)),
          sRow("the same best candidate", pct(S.same_best), S.ci.same_best, pct(SU.same_best))))),
      el("p", { class: "section-intro", style: "margin-top:10px", text: `Against the experts, the first run gives the ` +
        `same verdict for ${pct(V[PE].all.agreement)} of candidates and the repeat run for ${pct(V[PR].all.agreement)}; ` +
        `the same call for ${pct(M["Claude (pass E)"].all.agreement)} and ${pct(M["Claude (pass E, repeat run)"].all.agreement)} ` +
        `of statements. The reading of the Greek (and so pass A) was made once.` }),
      el("h2", { text: "Reading the Greek" }),
      el("p", { class: "section-intro", text: "Which of the experts' 36 characters, and of the 13 organs they group into, " +
        "Claude's reading fills, against the experts' reading. This measures coverage, not whether the content agrees; " +
        "the end-to-end figures above test the content." }),
      el("div", { class: "table-wrap" }, el("table", {},
        el("thead", {}, el("tr", {}, ["Level", "Claude", "Experts", "Both", "Precision", "Recall", "Recall, unseen"].map((h, i) =>
          el("th", { scope: "col", class: i ? "num" : null, text: h })))),
        el("tbody", {}, ["characters", "categories"].map((lvl) => el("tr", {},
          el("td", { text: lvl === "characters" ? "Characters (36)" : "Organs (13)" }),
          el("td", { class: "num", text: A[lvl].ours }), el("td", { class: "num", text: A[lvl].experts }),
          el("td", { class: "num", text: A[lvl].shared }), el("td", { class: "num", text: pct(A[lvl].precision) }),
          el("td", { class: "num", text: pct(A[lvl].recall) }), el("td", { class: "num", text: pct(AU[lvl].recall) })))))),
      el("p", { class: "section-intro", style: "margin-top:10px" },
        "Most often filled by the experts but not by Claude: " +
        A.characters.missed_most.map(([c, k]) => `${c} (${k})`).join(", ") + ". Most often filled by Claude but not by the experts: " +
        A.characters.added_most.map(([c, k]) => `${c} (${k})`).join(", ") + ". Every Claude statement carries a Greek quote " +
        "that code checked against the chapter: all 699 were found."),
      el("p", { class: "section-intro" }, "The numbers come from ", el("code", { text: "python -m rhizotomos.evaluate" }),
        "; see ", el("a", { href: `${REPO}/blob/main/RESULTS.md`, text: "RESULTS.md" }), " in the repository."));
  }

  // -- method ----------------------------------------------------------------------------------------------------
  function renderMethod() {
    document.title = "Method · Rhizotomos";
    const step = (n, title, text, checked) => el("div", { class: "step" }, el("b", { text: n }), el("strong", { text: title }),
      el("p", { text: text }), el("p", { class: "checked", text: checked }));
    const rep = R.replication;
    app.append(
      el("p", { class: "eyebrow", text: "Method" }),
      el("h1", { text: "How Rhizotomos works" }),
      el("div", { class: "prose" },
        el("p", { class: "lede" }, "Lardos et al. (2024) proposed a systematic way to identify the plants in historical texts " +
          "and tested it on a 13th-century Byzantine pharmacy text, John the Physician's ", el("i", { text: "Therapeutics" }),
          ", whose plants are described in Dioscorides' ", el("i", { text: "De materia medica" }), ". They read each " +
          "description, coded the same characters from modern floras, judged every match, and scored each candidate " +
          "species. Rhizotomos repeats those steps with Claude and scores each against the experts' published data.")),
      el("div", { class: "flow" },
        step("Stage A", "Read the Greek", "Claude reads Wellmann's Greek text of each chapter and sorts what it says " +
          "into the experts' 36 characters (leaf shape, flower colour, habitat…). Every statement carries a Greek quote.",
          "Checked: code finds every quote in the chapter (699 of 699); coverage against the experts' reading."),
        step("Stage B", "Match against the floras", "Each statement is compared with the description of each candidate " +
          "species in Flora of Turkey or Flora of Cyprus, as the experts extracted it, and called good, partial, no or " +
          "absent with the paper's definitions.", "Checked: the same pairs the experts judged, call by call."),
        step("Stage C", "Score the candidates", "The experts' rule turns the calls into a score per candidate: organs " +
          "that agree minus organs that disagree. STRONG is 5 or more, MODERATE 3 or 4, WEAK 2 or less.",
          `Checked: the rule reproduces ${rep.agree} of ${rep.checked} published verdicts; then each Claude configuration is scored.`)),
      el("div", { class: "prose" },
        el("h2", { text: "Two passes keep the stages apart" }),
        el("p", {}, el("strong", { text: "Pass E" }), " gives Claude the experts' own reading and asks only for the match " +
          "calls, which isolates Stage B. ", el("strong", { text: "Pass A" }), " gives Claude its own reading of the Greek, " +
          "which tests the whole pipeline. Pass A was done first, so it never saw the experts' reading. Pass E was later " +
          "made a second time, in a new session, to measure how much the calls vary from run to run."),
        el("h2", { text: "Blind by design" }),
        el("ul", {},
          el("li", { text: "Candidates were shown only as anonymous labels (P07-C2) in a shuffled order. Claude never saw their " +
            "names, the experts' calls or their verdicts while making calls." }),
          el("li", { text: "No expert call or verdict was looked at until both passes were complete. The rules used for the " +
            "calls (prompts/matching.md) were written down before the results were opened." }),
          el("li", {}, `${R.seen_plants.length} plants had some expert data looked at while the code was being built and ` +
            "checked. They are listed in data/llm/contamination.json, and every figure is also given without them.")),
        el("h2", { text: "Limitations" }),
        el("ul", {},
          el("li", { text: "The modern side is the experts' extraction from the floras, which covers only the characters in " +
            "their own reading. Claude's reading is penalised for statements outside them, and Stage B is not tested on " +
            "descriptions Claude would extract itself." }),
          el("li", { text: "One model made every reading and call. Pass E was made twice, in separate sessions: the runs give " +
            `the same call for ${pct(R.stability.all.same_call)} of statements and the same verdict for ` +
            `${pct(R.stability.all.same_grade)} of candidates. The reading of the Greek and pass A were made once, so their ` +
            "variation is not measured. The project had no API budget: the calls were made inside Claude Code sessions and " +
            "are committed, so every number can be reproduced without a model." }),
          el("li", { text: "61 plants and 122 scored candidates is a small benchmark; the intervals are wide." }),
          el("li", { text: "This reproduces the experts' botanical Stage 5 only. Their final identifications also weigh " +
            "medicinal uses and expert review (Stage 6)." }),
          el("li", { text: "These are hypotheses about historical texts. Nothing here is medical advice or a claim that a " +
            "plant is safe or effective." })),
        el("h2", { text: "AI use and what already existed" }),
        el("p", { text: "Claude (Opus 5.5), working in Claude Code, wrote the code, made the readings of the Greek and made " +
          "every match call. Already existing: the Greek text (Wellmann's edition, First1KGreek), the experts' data and " +
          "method (Lardos et al. 2024), and the Python libraries pandas, openpyxl and lxml." }),
        el("h2", { text: "Sources and licences" }),
        el("ul", {},
          el("li", {}, "Lardos A, Patmore K, Allkin R, Lazarou R, Nesbitt M, Scott AC, Zipser B (2024). A systematic " +
            "methodology to assess the identity of plants in historical texts: a case study based on the Byzantine pharmacy " +
            "text John the Physician's Therapeutics. ", el("i", { text: "Journal of Ethnopharmacology" }), " 322: 117622. ",
            el("a", { href: "https://doi.org/10.1016/j.jep.2023.117622", text: "doi:10.1016/j.jep.2023.117622" }),
            ". Article and research data (figshare) CC BY 4.0."),
          el("li", {}, "Dioscorides, ", el("i", { text: "De materia medica" }), ", ed. M. Wellmann (1906–1914), TEI text from ",
            el("a", { href: "https://github.com/OpenGreekAndLatin/First1KGreek", text: "First1KGreek" }), ", CC BY-SA 4.0."),
          el("li", {}, "Code MIT. Source and data: ", el("a", { href: REPO, text: REPO.replace("https://", "") }), "."))));
  }

  route();
})();
