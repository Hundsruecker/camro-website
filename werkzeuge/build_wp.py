"""Erzeugt aus dem lokalen Entwurf fertige WordPress-HTML-Blöcke je Seite und Sprache."""
import sys, os, re, json
import tinycss2
from playwright.sync_api import sync_playwright

SITE, OUT, SCRIPTS = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)

URLS = {
    "index": {"de": "https://camro.ro/", "en": "https://camro.ro/en/home/", "ro": "https://camro.ro/ro/acasa/"},
    "gemeinden": {"de": "https://camro.ro/fuer-gemeinden/", "en": "https://camro.ro/en/for-municipalities/", "ro": "https://camro.ro/ro/pentru-primarii/"},
    "kriterien": {"de": "https://camro.ro/kriterien-transparenz/", "en": "https://camro.ro/en/criteria-transparency/", "ro": "https://camro.ro/ro/criterii-transparenta/"},
    "unterstuetzer": {"de": "https://camro.ro/fuer-unterstuetzer/", "en": "https://camro.ro/en/for-supporters/", "ro": "https://camro.ro/ro/pentru-sustinatori/"},
    "projekte": {"de": "https://camro.ro/projekte/", "en": "https://camro.ro/en/projects/", "ro": "https://camro.ro/ro/proiecte/"},
    "kontakt": {"de": "https://camro.ro/kontakt/", "en": "https://camro.ro/en/contact-2/", "ro": "https://camro.ro/ro/contact/"},
    "bedarfserhebung": {"de": "https://camro.ro/bedarfserhebung-2026/", "en": "https://camro.ro/en/needs-assessment-2026/", "ro": "https://camro.ro/ro/evaluarea-nevoilor-2026/"},
}

def split_sel(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([": depth += 1
        if ch in ")]": depth -= 1
        if ch == "," and depth == 0:
            out.append(cur); cur = ""
        else:
            cur += ch
    out.append(cur)
    return [x.strip() for x in out if x.strip()]

P = "#primary #c2"

def pre(sel):
    if sel in (":root", "body", "html"): return P
    if sel.startswith("body "): return P + " " + sel[5:]
    return P + " " + sel

def scope(css):
    out = []
    for r in tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True):
        if r.type == "qualified-rule":
            sel = tinycss2.serialize(r.prelude)
            out.append(",".join(pre(s) for s in split_sel(sel)) + "{" + tinycss2.serialize(r.content).strip() + "}")
        elif r.type == "at-rule" and r.lower_at_keyword == "media":
            out.append("@media " + tinycss2.serialize(r.prelude).strip() + "{" + scope(tinycss2.serialize(r.content)) + "}")
    return "".join(out)

def mini(css):
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};:,>])\s*", r"\1", css)
    return css.replace(";}", "}")

NEUTRAL = (
    # Theme-Teile ausblenden, die die neuen Seiten selbst mitbringen
    "#masthead,#colophon,.site-footer,.entry-header,.ast-breadcrumbs-wrapper,.ast-page-title-bar{display:none!important}"
    "body{background:#F4F6F5!important}"
    # Alle Breiten-Deckel von Astra und vom alten Zusatz-CSS (Abschnitt 24a/25) aufheben
    "#page,#content.site-content,#content .ast-container,#primary,#main,#primary article{max-width:none!important;width:100%!important;margin:0!important;padding:0!important}"
    "#primary .entry-content,#primary .entry-content[data-ast-blocks-layout]{max-width:none!important;width:100%!important;margin:0!important;padding:0!important}"
    "#primary .entry-content>#c2{max-width:none!important;width:100%!important;margin:0!important}"
    # Typografie und Links des alten CSS neutralisieren (zwei IDs schlagen dessen Selektoren)
    "#primary #c2 h1,#primary #c2 h2,#primary #c2 h3,#primary #c2 h4{font-family:inherit;color:inherit;text-transform:none;margin-top:0}"
    "#primary #c2 a{border-bottom:0;color:inherit;text-decoration-line:underline}"
    "#primary #c2 .btn,#primary #c2 .nav a,#primary #c2 .brand,#primary #c2 .jump a,#primary #c2 .lang a,#primary #c2 .foot-area a{text-decoration:none}"
    "#primary #c2 ul,#primary #c2 ol{margin-left:0}#primary #c2 p{margin-bottom:0}#primary #c2 li{margin-bottom:0}"
    "#primary #c2 strong{color:inherit}"
)
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Commissioner:wght@400;500;600;700;800&display=swap" rel="stylesheet">')

base_css = open(os.path.join(SITE, "assets/camro.css"), encoding="utf-8").read()
mapjs = open(os.path.join(SCRIPTS, "wpmap.js"), encoding="utf-8").read()

GRAB = r"""(page) => {
  const svg = document.querySelector('svg symbol#camro-mark').closest('svg').outerHTML;
  const hdr = document.getElementById('site-header').cloneNode(true);
  hdr.querySelectorAll('.skip').forEach(a => a.remove());
  hdr.querySelectorAll('.lang button').forEach(b => {
    const a = document.createElement('a'); a.href = 'LANG:' + b.dataset.lang; a.lang = b.lang; a.textContent = b.textContent;
    if (b.getAttribute('aria-pressed') === 'true') a.setAttribute('aria-current', 'true');
    b.replaceWith(a);
  });
  const main = document.getElementById('main').cloneNode(true);
  if (page === 'index') {
    main.querySelector('#grid').id = 'c2-grid'; main.querySelector('#c2-grid').innerHTML = '';
    main.querySelector('#panel').id = 'c2-panel'; main.querySelector('#c2-panel').innerHTML = '';
    const d = main.querySelector('[data-i18n="mapDraft"]'); if (d) d.remove();
  }
  if (page === 'projekte') {
    main.querySelectorAll('section:not(.page-head)').forEach(s => s.remove());
  }
  const foot = document.getElementById('site-footer').innerHTML;
  const styles = [...document.querySelectorAll('head style')].map(s => s.textContent).join('\n');
  return {svg, header: hdr.innerHTML, main: main.innerHTML, footer: foot, styles};
}"""

def fix_links(html, lang):
    def rep(m):
        page, l, h = m.group(1), m.group(2), m.group(3) or ""
        return 'href="' + URLS[page][l] + h + '"'
    html = re.sub(r'href="([a-z]+)\.html\?lang=([a-z]{2})(#[\w-]*)?"', rep, html)
    return html

summary = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for page in URLS:
        for lang in ("de", "en", "ro"):
            pg = b.new_page(viewport={"width": 1280, "height": 900})
            pg.goto(f"file://{SITE}/{page}.html?lang={lang}"); pg.wait_for_timeout(400)
            g = pg.evaluate(GRAB, page)
            pg.close()
            header = g["header"]
            for l in ("de", "en", "ro"):
                header = header.replace(f'href="LANG:{l}"', f'href="{URLS[page][l]}" hreflang="{l}"')
            body = '<div id="c2" lang="' + lang + '">' + g["svg"] + header + '<div id="c2-main">' + g["main"] + '</div>' + g["footer"] + '</div>'
            body = fix_links(body, lang)
            body = body.replace(' data-i18n=', ' data-x=')
            body = re.sub(r' data-(x|base|i18n-aria)="[^"]*"', '', body)
            css = mini(NEUTRAL + scope(base_css + "\n" + g["styles"]))
            parts = [FONTS, "<style>" + css + "</style>", body]
            if page == "index":
                parts.append("<script>" + mapjs + "</script>")
            if page == "projekte":
                # Kopf und Fuß getrennt ablegen; der Mittelteil ist der bestehende Projekt-Block von camro.ro
                mainpart = '<div id="c2-main">' + fix_links(g["main"], lang)
                mainpart = re.sub(r' data-(x|base|i18n|i18n-aria)="[^"]*"', '', mainpart)
                head = FONTS + "<style>" + css + "</style>" + '<div id="c2" lang="' + lang + '">' + g["svg"] + fix_links(header, lang) + mainpart + '<section class="wrap sec" style="padding-top:32px">'
                tail = '</section></div>' + fix_links(g["footer"], lang) + '</div>'
                json.dump({"head": head, "tail": tail}, open(os.path.join(OUT, f"projekte_{lang}.json"), "w", encoding="utf-8"), ensure_ascii=False)
                summary[f"projekte_{lang}"] = len(head) + len(tail)
                continue
            html = "<!-- wp:html -->\n" + "\n".join(parts) + "\n<!-- /wp:html -->"
            open(os.path.join(OUT, f"{page}_{lang}.html"), "w", encoding="utf-8").write(html)
            summary[f"{page}_{lang}"] = len(html)
    b.close()
print(json.dumps(summary, indent=0))
