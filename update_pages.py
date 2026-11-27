#!/usr/bin/env python3
"""Ersetzt die Seiten von camro.ro durch das neue Design (DE/EN/RO).

Nur Python-Standardbibliothek. Zugangsdaten kommen aus Umgebungsvariablen:
  CAMRO_WP_USER          WordPress-Benutzername
  CAMRO_WP_APP_PASSWORD  WordPress-Anwendungspasswort (Benutzer > Profil > Anwendungspasswörter)

Aufrufe:
  python3 update_pages.py                 Probelauf: findet die Seiten, sichert den aktuellen Inhalt, ändert nichts
  python3 update_pages.py --apply         ersetzt alle Seiten
  python3 update_pages.py --apply --only index_de   nur eine Seite (Kennung siehe Probelauf)
  python3 update_pages.py --restore backup/<Zeitstempel>   spielt eine Sicherung zurück
"""
import base64, json, os, re, sys, time, urllib.request, urllib.error

BASE = "https://camro.ro"
HERE = os.path.dirname(os.path.abspath(__file__))
BLOCKS = os.path.join(HERE, "blocks")
UA = "Mozilla/5.0 (camro-update)"

PAGES = {
    "index":           {"de": "/", "en": "/en/home/", "ro": "/ro/acasa/"},
    "gemeinden":       {"de": "/fuer-gemeinden/", "en": "/en/for-municipalities/", "ro": "/ro/pentru-primarii/"},
    "kriterien":       {"de": "/kriterien-transparenz/", "en": "/en/criteria-transparency/", "ro": "/ro/criterii-transparenta/"},
    "unterstuetzer":   {"de": "/fuer-unterstuetzer/", "en": "/en/for-supporters/", "ro": "/ro/pentru-sustinatori/"},
    "projekte":        {"de": "/projekte/", "en": "/en/projects/", "ro": "/ro/proiecte/"},
    "kontakt":         {"de": "/kontakt/", "en": "/en/contact-2/", "ro": "/ro/contact/"},
    "bedarfserhebung": {"de": "/bedarfserhebung-2026/", "en": "/en/needs-assessment-2026/", "ro": "/ro/evaluarea-nevoilor-2026/"},
}
START, END = "<!--c2-proj-start-->", "<!--c2-proj-end-->"


def auth_header():
    u, p = os.environ.get("CAMRO_WP_USER"), os.environ.get("CAMRO_WP_APP_PASSWORD")
    if not u or not p:
        sys.exit("Fehlt: CAMRO_WP_USER und CAMRO_WP_APP_PASSWORD als Umgebungsvariablen setzen.")
    return "Basic " + base64.b64encode(f"{u}:{p.replace(' ', '')}".encode()).decode()


def http(url, method="GET", data=None, auth=None):
    headers = {"User-Agent": UA, "Accept": "application/json, text/html"}
    if auth:
        headers["Authorization"] = auth
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def cloudflare(status, text):
    return status in (403, 503) and ("cf-chl" in text or "Just a moment" in text or "cloudflare" in text.lower())


def page_id(path):
    st, html = http(BASE + path + ("&" if "?" in path else "?") + "nocache=" + str(int(time.time())))
    if cloudflare(st, html):
        sys.exit(f"Cloudflare blockiert den Abruf von {path} (HTTP {st}). Bitte in Cloudflare die IP des VPS freigeben oder den Bot-Schutz kurz lockern.")
    m = re.search(r"page-id-(\d+)", html)
    if not m:
        sys.exit(f"Seiten-ID für {path} nicht gefunden (HTTP {st}).")
    return int(m.group(1))


def get_raw(pid, auth):
    st, txt = http(f"{BASE}/wp-json/wp/v2/pages/{pid}?context=edit", auth=auth)
    if st != 200:
        sys.exit(f"Lesen von Seite {pid} fehlgeschlagen (HTTP {st}): {txt[:300]}")
    j = json.loads(txt)
    return j["content"]["raw"], j["title"]["raw"]


def projekte_content(raw, lang):
    if START in raw and END in raw:
        orig = raw.split(START, 1)[1].split(END, 1)[0]
    else:
        orig = re.sub(r"<!--\s*/?wp:[^>]*-->", "", raw).strip()
    parts = json.load(open(os.path.join(BLOCKS, f"projekte_{lang}.json"), encoding="utf-8"))
    return "<!-- wp:html -->\n" + parts["head"] + START + orig + END + parts["tail"] + "\n<!-- /wp:html -->"


def new_content(key, lang, raw):
    if key == "projekte":
        return projekte_content(raw, lang)
    return open(os.path.join(BLOCKS, f"{key}_{lang}.html"), encoding="utf-8").read()


def main():
    args = sys.argv[1:]
    auth = auth_header()

    if "--restore" in args:
        folder = args[args.index("--restore") + 1]
        for f in sorted(os.listdir(folder)):
            m = re.match(r"(.+)_(\d+)\.html$", f)
            if not m:
                continue
            pid = int(m.group(2))
            st, txt = http(f"{BASE}/wp-json/wp/v2/pages/{pid}", "POST", {"content": open(os.path.join(folder, f), encoding="utf-8").read()}, auth)
            print(f"{m.group(1):24} Seite {pid}: {'zurückgespielt' if st == 200 else 'FEHLER HTTP ' + str(st)}")
        return

    apply = "--apply" in args
    only = args[args.index("--only") + 1] if "--only" in args else None
    stamp = time.strftime("%Y%m%d-%H%M%S")
    bdir = os.path.join(HERE, "backup", stamp)
    os.makedirs(bdir, exist_ok=True)

    print(("ÄNDERN" if apply else "PROBELAUF (es wird nichts geändert)") + f" – Sicherung in {bdir}\n")
    ok = True
    for key, langs in PAGES.items():
        for lang, path in langs.items():
            ident = f"{key}_{lang}"
            if only and ident != only:
                continue
            pid = page_id(path)
            raw, title = get_raw(pid, auth)
            open(os.path.join(bdir, f"{ident}_{pid}.html"), "w", encoding="utf-8").write(raw)
            new = new_content(key, lang, raw)
            line = f"{ident:24} Seite {pid:<6} „{title}“  alt {len(raw):>6} Zeichen → neu {len(new):>6}"
            if not apply:
                print(line)
                continue
            st, txt = http(f"{BASE}/wp-json/wp/v2/pages/{pid}", "POST", {"content": new}, auth)
            if st != 200:
                ok = False
                print(line + f"  FEHLER HTTP {st}: {txt[:200]}")
                continue
            st2, live = http(BASE + path + "?nocache=" + str(int(time.time())))
            seen = 'id="c2"' in live
            print(line + ("  ersetzt, live sichtbar" if seen else "  ersetzt, live noch alt (Cache leeren)"))
            time.sleep(1)
    print("\nFertig." if ok else "\nMit Fehlern beendet. Sicherung liegt in " + bdir)


if __name__ == "__main__":
    main()
