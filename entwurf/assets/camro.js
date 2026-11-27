/* CAMRO – gemeinsames Skript (Entwurf)
   Kopf- und Fußzeile, Sprachwahl DE/EN/RO, Kachelkarte der Kreise, Balkendiagramme.
   Jede Seite meldet ihre eigenen Texte mit CAMRO.page({de:{…},en:{…},ro:{…}}, render) an. */
window.CAMRO = (function () {
  "use strict";

  var LANGS = [["de", "Deutsch"], ["en", "English"], ["ro", "Română"]];

  var COMMON = {
    de: {
      skip: "Zum Inhalt springen", navLabel: "Hauptnavigation", langLabel: "Sprache",
      nav: ["Start", "Für Gemeinden", "Kriterien & Transparenz", "Für Unterstützer", "Projekte", "Kontakt"],
      st: { active: "Aktive Kooperation", trial: "Probephase", none: "Noch kein Eintrag", special: "București (Sonderstatus)" },
      panelLabel: "Gemeldete Gemeinden", panelEmpty: "Aus diesem Kreis ist noch keine Gemeinde gemeldet.",
      aboutHead: "Über uns", footAbout: "CAMRO ist eine unabhängige Kooperationsplattform für kommunalen Tierschutz in Rumänien.",
      infoHead: "Informationen", legalHead: "Rechtliches", imprint: "Impressum", privacy: "Datenschutz",
      contactHead: "Kontakt", footProject: "CAMRO ist ein Projekt der Hundsrücker Tierschutz gUG"
    },
    en: {
      skip: "Skip to content", navLabel: "Main navigation", langLabel: "Language",
      nav: ["Home", "For municipalities", "Criteria & Transparency", "For supporters", "Projects", "Contact"],
      st: { active: "Active cooperation", trial: "Probationary period", none: "No entry yet", special: "București (special status)" },
      panelLabel: "Registered municipalities", panelEmpty: "No municipality from this county has registered yet.",
      aboutHead: "About us", footAbout: "CAMRO is an independent cooperation platform for municipal animal welfare in Romania.",
      infoHead: "Information", legalHead: "Legal", imprint: "Imprint", privacy: "Privacy",
      contactHead: "Contact", footProject: "CAMRO is a project of Hundsrücker Tierschutz gUG"
    },
    ro: {
      skip: "Salt la conținut", navLabel: "Navigare principală", langLabel: "Limba",
      nav: ["Acasă", "Pentru primării", "Criterii & Transparență", "Pentru susținători", "Proiecte", "Contact"],
      st: { active: "Cooperare activă", trial: "Perioadă de probă", none: "Încă nicio înregistrare", special: "București (statut special)" },
      panelLabel: "Primării înregistrate", panelEmpty: "Din acest județ nu s-a înregistrat încă nicio primărie.",
      aboutHead: "Despre noi", footAbout: "CAMRO este o platformă independentă de cooperare pentru protecția animalelor la nivel municipal în România.",
      infoHead: "Informații", legalHead: "Juridic", imprint: "Impressum", privacy: "Protecția datelor",
      contactHead: "Contact", footProject: "CAMRO este un proiect al Hundsrücker Tierschutz gUG"
    }
  };

  var PAGES = ["index.html", "gemeinden.html", "kriterien.html", "unterstuetzer.html", "projekte.html", "kontakt.html"];

  /* Kreise: Kürzel, Name, Spalte, Zeile der Kachelkarte (9 x 7) */
  var COUNTIES = [
    ["SM","Satu Mare",2,0],["MM","Maramureș",3,0],["SV","Suceava",4,0],["BT","Botoșani",5,0],
    ["BH","Bihor",1,1],["SJ","Sălaj",2,1],["BN","Bistrița-Năsăud",3,1],["NT","Neamț",4,1],["IS","Iași",5,1],
    ["AR","Arad",1,2],["CJ","Cluj",2,2],["MS","Mureș",3,2],["HR","Harghita",4,2],["BC","Bacău",5,2],["VS","Vaslui",6,2],
    ["TM","Timiș",0,3],["HD","Hunedoara",1,3],["AB","Alba",2,3],["SB","Sibiu",3,3],["BV","Brașov",4,3],["CV","Covasna",5,3],["VN","Vrancea",6,3],["GL","Galați",7,3],
    ["CS","Caraș-Severin",1,4],["GJ","Gorj",2,4],["VL","Vâlcea",3,4],["AG","Argeș",4,4],["PH","Prahova",5,4],["BZ","Buzău",6,4],["BR","Brăila",7,4],["TL","Tulcea",8,4],
    ["MH","Mehedinți",1,5],["DJ","Dolj",2,5],["OT","Olt",3,5],["DB","Dâmbovița",4,5],["IF","Ilfov",5,5],["IL","Ialomița",6,5],["CT","Constanța",7,5],
    ["TR","Teleorman",3,6],["GR","Giurgiu",4,6],["B","București",5,6],["CL","Călărași",6,6]
  ];

  /* BEISPIELWERTE für den Entwurf. Auf der Live-Seite durch die JSON-Antwort des CAMRO-CRM ersetzen. */
  var STATUS = { PH: { s: "trial", places: ["Breaza", "Bărcănești"] }, B: { s: "special", places: [] } };

  var lang = (function () {
    var q = new URLSearchParams(location.search).get("lang");
    if (q && COMMON[q]) return q;
    try { var s = localStorage.getItem("camro-lang"); if (s && COMMON[s]) return s; } catch (e) {}
    return "de";
  })();

  var pageDict = { de: {}, en: {}, ro: {} };
  var hooks = [];

  function esc(s) { var d = document.createElement("div"); d.textContent = s == null ? "" : String(s); return d.innerHTML; }
  function t(key) { var p = pageDict[lang] || {}; return key in p ? p[key] : COMMON[lang][key]; }
  function info(code) { return STATUS[code] || { s: "none", places: [] }; }
  function county(code) { for (var i = 0; i < COUNTIES.length; i++) if (COUNTIES[i][0] === code) return COUNTIES[i]; return null; }
  function link(file, hash) { return file + "?lang=" + lang + (hash || ""); }
  function fmt(n) { return new Intl.NumberFormat(lang === "en" ? "en-GB" : lang === "ro" ? "ro-RO" : "de-DE").format(n); }

  function markSymbol() {
    if (document.getElementById("camro-mark")) return;
    var r = "";
    COUNTIES.forEach(function (c) {
      if (c[0] === "PH") return;
      r += '<rect x="' + (c[2] + .09) + '" y="' + (c[3] + .09) + '" width=".82" height=".82" rx=".14"/>';
    });
    var div = document.createElement("div");
    div.innerHTML = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="camro-mark" viewBox="0 0 9 7"><g fill="currentColor">' + r +
      '</g><rect x="5.09" y="4.09" width=".82" height=".82" rx=".14" fill="#E2B33C"/></symbol></svg>';
    document.body.insertBefore(div.firstChild, document.body.firstChild);
  }

  function brand(tag) {
    return '<' + tag + ' class="brand"' + (tag === "a" ? ' href="' + link("index.html") + '" aria-label="CAMRO"' : "") + '>' +
      '<svg width="40" height="31" aria-hidden="true"><use href="#camro-mark"/></svg><b>CAMRO</b></' + tag + '>';
  }

  function renderHeader() {
    var el = document.getElementById("site-header"); if (!el) return;
    var c = COMMON[lang], cur = document.body.getAttribute("data-page");
    var nav = PAGES.map(function (p, i) {
      return '<a href="' + link(p) + '"' + (p === cur ? ' aria-current="page"' : "") + '>' + esc(c.nav[i]) + '</a>';
    }).join("");
    var sw = LANGS.map(function (l) {
      return '<button type="button" lang="' + l[0] + '" data-lang="' + l[0] + '" aria-pressed="' + (l[0] === lang) + '">' + l[1] + '</button>';
    }).join("");
    el.innerHTML = '<a class="skip" href="#main">' + esc(c.skip) + '</a><header class="head"><div class="wrap">' + brand("a") +
      '<nav class="nav" aria-label="' + esc(c.navLabel) + '">' + nav + '</nav>' +
      '<div class="lang" role="group" aria-label="' + esc(c.langLabel) + '">' + sw + '</div></div></header>';
    el.querySelectorAll("[data-lang]").forEach(function (b) {
      b.addEventListener("click", function () { setLang(b.getAttribute("data-lang")); });
    });
  }

  function renderFooter() {
    var el = document.getElementById("site-footer"); if (!el) return;
    var c = COMMON[lang];
    el.innerHTML = '<footer class="foot-area"><div class="wrap foot">' +
      '<div class="foot-brand">' + brand("span") + '<h2 style="margin-top:20px">' + esc(c.aboutHead) + '</h2><p style="margin-top:0">' + esc(c.footAbout) + '</p></div>' +
      '<nav aria-label="' + esc(c.infoHead) + '"><h2>' + esc(c.infoHead) + '</h2><ul>' +
        PAGES.map(function (p, i) { return '<li><a href="' + link(p) + '">' + esc(c.nav[i]) + '</a></li>'; }).join("") + '</ul></nav>' +
      '<nav aria-label="' + esc(c.legalHead) + '"><h2>' + esc(c.legalHead) + '</h2><ul>' +
        '<li><a href="https://camro.ro/impressum/">' + esc(c.imprint) + '</a></li>' +
        '<li><a href="https://camro.ro/datenschutz/">' + esc(c.privacy) + '</a></li></ul></nav>' +
      '<address><h2>' + esc(c.contactHead) + '</h2><p>' + esc(c.footProject) + '</p><p>Europaallee 33, 67657 Kaiserslautern</p>' +
        '<p><a href="tel:+4917681081042">+49 176 810 810 42</a></p><p><a href="mailto:kontakt@hundsruecker.de">kontakt@hundsruecker.de</a></p></address>' +
      '</div><div class="wrap bottom"><span>© 2026 CAMRO</span><a href="https://www.facebook.com/profile.php?id=61585799586972">Facebook</a></div></footer>';
  }

  function applyText() {
    document.querySelectorAll("[data-i18n]").forEach(function (el) { el.textContent = t(el.getAttribute("data-i18n")); });
    document.querySelectorAll("[data-i18n-html]").forEach(function (el) { el.innerHTML = t(el.getAttribute("data-i18n-html")); });
    document.querySelectorAll("[data-i18n-aria]").forEach(function (el) { el.setAttribute("aria-label", t(el.getAttribute("data-i18n-aria"))); });
    /* interne Links: Sprache mitgeben */
    document.querySelectorAll("main a[href]").forEach(function (a) {
      var base = a.getAttribute("data-base");
      if (!base) {
        var h = a.getAttribute("href");
        if (!/^[a-z-]+\.html/.test(h)) return;
        base = h.split("?")[0]; a.setAttribute("data-base", base);
      }
      var parts = base.split("#");
      a.setAttribute("href", link(parts[0], parts[1] ? "#" + parts[1] : ""));
    });
  }

  function render() {
    document.documentElement.lang = lang;
    var title = t("pageTitle"); if (title) document.title = title + " – CAMRO";
    renderHeader(); renderFooter(); applyText();
    hooks.forEach(function (fn) { fn(lang, t); });
  }

  function setLang(l) {
    lang = l;
    try { localStorage.setItem("camro-lang", l); } catch (e) {}
    try { var u = new URL(location.href); u.searchParams.set("lang", l); history.replaceState(null, "", u); } catch (e) {}
    render();
  }

  /* Kachelkarte. opts: { selected, onPick(code), allowNone } – liefert {render, select} */
  function tileMap(gridEl, opts) {
    opts = opts || {};
    var sel = opts.selected || null;
    function draw() {
      gridEl.innerHTML = COUNTIES.map(function (c) {
        var d = info(c[0]);
        return '<button type="button" class="tile s-' + d.s + '" data-code="' + c[0] + '" style="grid-column:' + (c[2] + 1) + ';grid-row:' + (c[3] + 1) + '"' +
          ' aria-pressed="' + (c[0] === sel) + '" aria-label="' + esc(c[1] + ": " + COMMON[lang].st[d.s]) + '" title="' + esc(c[1]) + '">' + c[0] + '</button>';
      }).join("");
    }
    gridEl.addEventListener("click", function (e) {
      var b = e.target.closest(".tile"); if (!b) return;
      var code = b.getAttribute("data-code");
      sel = (opts.allowNone && sel === code) ? null : code;
      gridEl.querySelectorAll(".tile").forEach(function (x) { x.setAttribute("aria-pressed", x.getAttribute("data-code") === sel); });
      if (opts.onPick) opts.onPick(sel);
    });
    if (opts.onHover) {
      ["mouseover", "focusin"].forEach(function (ev) {
        gridEl.addEventListener(ev, function (e) { var b = e.target.closest(".tile"); if (b) opts.onHover(b.getAttribute("data-code")); });
      });
      ["mouseleave", "focusout"].forEach(function (ev) { gridEl.addEventListener(ev, function () { opts.onHover(null); }); });
    }
    return { render: draw, select: function (c) { sel = c; draw(); }, get selected() { return sel; } };
  }

  function legend(el) {
    var st = COMMON[lang].st;
    el.innerHTML = ["active", "trial", "none", "special"].map(function (k) {
      return '<li><span class="sw s-' + k + '" aria-hidden="true"></span>' + esc(st[k]) + '</li>';
    }).join("");
  }

  function panel(el, code) {
    var c = county(code); if (!c) { el.innerHTML = ""; return; }
    var d = info(code), cm = COMMON[lang];
    var h = '<div><span class="code">' + c[0] + '</span><span class="name">' + esc(c[1]) + '</span></div><p class="status">' + esc(cm.st[d.s]) + '</p>';
    if (d.places.length) h += '<p class="lbl">' + esc(cm.panelLabel) + '</p><ul>' + d.places.map(function (p) { return '<li>' + esc(p) + '</li>'; }).join("") + '</ul>';
    else if (d.s !== "special") h += '<p class="empty">' + esc(cm.panelEmpty) + '</p>';
    el.innerHTML = h;
  }

  /* Balkenliste. items: [[Beschriftung, Wert], …]; opts: {max, hi: Index, suffix, decimals} */
  function bars(el, items, opts) {
    opts = opts || {};
    var max = opts.max || Math.max.apply(null, items.map(function (i) { return i[1]; }));
    el.innerHTML = items.map(function (it, i) {
      var v = it[1], w = Math.max(0, Math.min(100, v / max * 100));
      var shown = opts.decimals ? v.toLocaleString(lang === "en" ? "en-GB" : lang === "ro" ? "ro-RO" : "de-DE", { minimumFractionDigits: opts.decimals, maximumFractionDigits: opts.decimals }) : fmt(v);
      return '<li><span class="lab">' + esc(it[0]) + '</span><span class="track" aria-hidden="true"><span class="fill' + (opts.hi === i ? " hi" : "") + '" style="width:' + w.toFixed(1) + '%"></span></span>' +
        '<span class="val">' + shown + (opts.suffix || "") + '</span></li>';
    }).join("");
  }

  function page(dict, hook) {
    ["de", "en", "ro"].forEach(function (l) { pageDict[l] = dict[l] || {}; });
    if (hook) hooks.push(hook);
  }

  document.addEventListener("DOMContentLoaded", function () { markSymbol(); render(); });

  return {
    page: page, esc: esc, t: t, fmt: fmt, link: link, tileMap: tileMap, legend: legend, panel: panel, bars: bars,
    counties: COUNTIES, county: county, info: info,
    get lang() { return lang; }
  };
})();
