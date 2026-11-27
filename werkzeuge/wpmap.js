(function () {
  "use strict";
  var grid = document.getElementById("c2-grid"), panel = document.getElementById("c2-panel");
  if (!grid || !panel) return;
  var API = "https://app.camro.ro/api/karte/";
  var lang = /^\/ro\//.test(location.pathname) ? "ro" : /^\/en\//.test(location.pathname) ? "en" : "de";
  var PROJ = { de: "https://camro.ro/projekte/", en: "https://camro.ro/en/projects/", ro: "https://camro.ro/ro/proiecte/" }[lang];
  var T = {
    de: { keine: "Noch keine Projekte aus diesem Kreis.", keinKreis: "Noch keinen Kreis ausgewählt",
      hauptstadt: "București ist eine eigenständige Gemeinde mit Sonderstatus und kein Kreis im klassischen Sinn.", offen: "noch offen",
      st: { active: "Aktive Kooperation", trial: "Probephase", none: "Noch kein Eintrag", special: "București (Sonderstatus)" } },
    en: { keine: "No projects from this county yet.", keinKreis: "No county selected",
      hauptstadt: "București is a separate municipality with special status, not a county.", offen: "still open",
      st: { active: "Active cooperation", trial: "Probationary period", none: "No entry yet", special: "București (special status)" } },
    ro: { keine: "Încă niciun proiect din acest județ.", keinKreis: "Niciun județ selectat",
      hauptstadt: "București este o unitate separată cu statut special, nu un județ.", offen: "încă neacoperit",
      st: { active: "Cooperare activă", trial: "Perioadă de probă", none: "Încă nicio înregistrare", special: "București (statut special)" } }
  }[lang];
  /* Kürzel, Name, Spalte, Zeile; Bucuresti heißt in der Schnittstelle "BI" */
  var C = [["SM","Satu Mare",2,0],["MM","Maramureș",3,0],["SV","Suceava",4,0],["BT","Botoșani",5,0],
    ["BH","Bihor",1,1],["SJ","Sălaj",2,1],["BN","Bistrița-Năsăud",3,1],["NT","Neamț",4,1],["IS","Iași",5,1],
    ["AR","Arad",1,2],["CJ","Cluj",2,2],["MS","Mureș",3,2],["HR","Harghita",4,2],["BC","Bacău",5,2],["VS","Vaslui",6,2],
    ["TM","Timiș",0,3],["HD","Hunedoara",1,3],["AB","Alba",2,3],["SB","Sibiu",3,3],["BV","Brașov",4,3],["CV","Covasna",5,3],["VN","Vrancea",6,3],["GL","Galați",7,3],
    ["CS","Caraș-Severin",1,4],["GJ","Gorj",2,4],["VL","Vâlcea",3,4],["AG","Argeș",4,4],["PH","Prahova",5,4],["BZ","Buzău",6,4],["BR","Brăila",7,4],["TL","Tulcea",8,4],
    ["MH","Mehedinți",1,5],["DJ","Dolj",2,5],["OT","Olt",3,5],["DB","Dâmbovița",4,5],["IF","Ilfov",5,5],["IL","Ialomița",6,5],["CT","Constanța",7,5],
    ["TR","Teleorman",3,6],["GR","Giurgiu",4,6],["B","București",5,6],["CL","Călărași",6,6]];
  var DATA = {}, sel = null, hover = null;
  function key(code) { return code === "B" ? "BI" : code; }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function status(code) {
    if (code === "B") return "special";
    var d = DATA[key(code)] || {};
    if (d.status === "active") return "active";
    if (d.status === "trial") return "trial";
    if (d.status === "capital") return "special";
    return (d.projekte && d.projekte.length) ? "active" : "none";
  }
  function betrag(n) { return n == null || isNaN(n) ? "" : Number(n).toLocaleString(lang === "de" ? "de-DE" : lang === "ro" ? "ro-RO" : "en-GB") + " RON"; }
  function draw() {
    grid.innerHTML = C.map(function (c) {
      var s = status(c[0]);
      return '<button type="button" class="tile s-' + s + '" data-code="' + c[0] + '" style="grid-column:' + (c[2] + 1) + ';grid-row:' + (c[3] + 1) + '" aria-pressed="' + (c[0] === sel) + '" aria-label="' + esc(c[1] + ": " + T.st[s]) + '" title="' + esc(c[1]) + '">' + c[0] + '</button>';
    }).join("");
  }
  function show() {
    var code = hover || sel;
    if (!code) { panel.innerHTML = '<p class="status">' + esc(T.keinKreis) + '</p>'; return; }
    var c = C.filter(function (x) { return x[0] === code; })[0], s = status(code), d = DATA[key(code)] || {}, list = d.projekte || [];
    var h = '<div><span class="code">' + c[0] + '</span><span class="name">' + esc(d.name || c[1]) + '</span></div><p class="status">' + esc(T.st[s]) + '</p>';
    if (code === "B") h += '<p class="empty">' + esc(T.hauptstadt) + '</p>';
    else if (!list.length) h += '<p class="empty">' + esc(T.keine) + '</p>';
    else h += '<ul>' + list.map(function (p) {
      var amount = p.betragRon != null ? ' · ' + esc(betrag(p.betragRon)) + (p.prozentOffen ? ', ' + Math.round(p.prozentOffen) + ' % ' + esc(T.offen) : "") : "";
      return '<li><a href="' + PROJ + '#projekt-' + esc(p.id) + '"><b>' + esc(p.gemeinde) + '</b></a> ' + esc(p.need || "") + amount + '</li>';
    }).join("") + '</ul>';
    panel.innerHTML = h;
  }
  grid.addEventListener("click", function (e) {
    var b = e.target.closest(".tile"); if (!b) return;
    sel = b.getAttribute("data-code");
    grid.querySelectorAll(".tile").forEach(function (x) { x.setAttribute("aria-pressed", x === b); });
    show();
  });
  ["mouseover", "focusin"].forEach(function (ev) { grid.addEventListener(ev, function (e) { var b = e.target.closest(".tile"); if (b) { hover = b.getAttribute("data-code"); show(); } }); });
  ["mouseleave", "focusout"].forEach(function (ev) { grid.addEventListener(ev, function () { hover = null; show(); }); });
  draw(); show();
  fetch(API + "?lang=" + lang, { headers: { Accept: "application/json" } })
    .then(function (r) { return r.ok ? r.json() : {}; })
    .then(function (d) {
      DATA = d || {};
      if (!sel) { for (var i = 0; i < C.length; i++) { var k = DATA[key(C[i][0])]; if (k && k.projekte && k.projekte.length) { sel = C[i][0]; break; } } }
      draw(); show();
    })
    .catch(function () { draw(); show(); });
})();
