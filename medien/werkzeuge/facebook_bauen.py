"""Erzeugt Facebook-Profilbild und -Titelbild für CAMRO aus den Logo-Dateien (Playwright)."""
import os, re
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(H)
INK, PAPER, STONE, RAPS, WHITE = "#1B2440", "#F4F6F5", "#E1E6E3", "#E2B33C", "#FFFFFF"
sym = open(os.path.join(H, "camro-app-symbol.svg"), encoding="utf-8").read()
# Kacheln des Bildzeichens (ohne den abgerundeten Hintergrund)
tiles = re.findall(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="[\d.]+" rx="([\d.]+)" fill="(#[0-9A-Fa-f]+)"', sym)
xs = [float(t[0]) for t in tiles]; ys = [float(t[1]) for t in tiles]; w = float(tiles[0][2])
X0, Y0, X1, Y1 = min(xs), min(ys), max(xs) + w, max(ys) + w

def mark(size, tile, accent):
    """Bildzeichen als SVG, auf Breite `size` skaliert; tile/accent = Farben."""
    s = size / (X1 - X0); hgt = (Y1 - Y0) * s
    r = "".join(f'<rect x="{(float(x)-X0)*s:.2f}" y="{(float(y)-Y0)*s:.2f}" width="{float(ww)*s:.2f}" height="{float(ww)*s:.2f}" rx="{float(rx)*s:.2f}" fill="{accent if f.upper()==RAPS else tile}"/>'
                for x, y, ww, rx, f in tiles)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{size:.0f}" height="{hgt:.0f}" viewBox="0 0 {size:.2f} {hgt:.2f}">{r}</svg>'

def logo(name, width):
    s = open(os.path.join(H, name), encoding="utf-8").read()
    s = re.sub(r'<title>.*?</title>', '', s)
    return re.sub(r'width="921" height="260"', f'width="{width}" height="{width*260/921:.0f}"', s, count=1)

page = lambda w, h, bg, body: f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:{bg}}}.c{{position:absolute}}svg{{display:block}}</style></head><body>{body}</body></html>'

# Profilbild 1080x1080: Facebook schneidet kreisrund zu, das Zeichen bleibt deutlich im Kreis
P = 1080; mw = 760
m = mark(mw, WHITE, RAPS); mh = (Y1 - Y0) * mw / (X1 - X0)
profil = page(P, P, INK, f'<div class="c" style="left:{(P-mw)/2:.0f}px;top:{(P-mh)/2:.0f}px">{m}</div>')

# Titelbild 1702x630 (doppelte Auflösung von 851x315). Auf dem Handy bleibt nur die Mitte (~1120 px breit) sichtbar,
# darum steht das Logo mittig und das große Zeichen nur als Schmuck am rechten Rand.
W, Hh = 1702, 630; lw = 860; lh = lw * 260 / 921
big = 900; bh = (Y1 - Y0) * big / (X1 - X0)
def cover(bg, logofile, tile, accent):
    deco = f'<div class="c" style="left:{W-big*0.42:.0f}px;top:{(Hh-bh)/2+40:.0f}px">{mark(big, tile, accent)}</div>'
    deco2 = f'<div class="c" style="left:{-big*0.62:.0f}px;top:{(Hh-bh)/2-150:.0f}px">{mark(big, tile, tile)}</div>'
    return page(W, Hh, bg, deco + deco2 + f'<div class="c" style="left:{(W-lw)/2:.0f}px;top:{(Hh-lh)/2-10:.0f}px">{logo(logofile, lw)}</div>')

jobs = {"facebook-profilbild.png": (P, P, profil),
        "facebook-titelbild-hell.png": (W, Hh, cover(PAPER, "camro-logo.svg", STONE, "#EBD9A6")),
        "facebook-titelbild-dunkel.png": (W, Hh, cover(INK, "camro-logo-dunkel.svg", "#26305A", "#5A4E33"))}
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, (w_, h_, html) in jobs.items():
        pg = b.new_page(viewport={"width": w_, "height": h_})
        pg.set_content(html); pg.screenshot(path=os.path.join(OUT, name)); pg.close()
        print(name, w_, h_)
    b.close()
