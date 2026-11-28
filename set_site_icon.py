#!/usr/bin/env python3
"""Setzt das Website-Symbol (Favicon) von camro.ro auf das neue CAMRO-Zeichen.

Nur Python-Standardbibliothek. Zugangsdaten wie bei update_pages.py:
  CAMRO_WP_USER, CAMRO_WP_APP_PASSWORD

Aufrufe:
  python3 set_site_icon.py              Probelauf: zeigt das aktuelle Website-Symbol, ändert nichts
  python3 set_site_icon.py --apply      lädt medien/camro-website-symbol-512.png hoch und setzt es als Website-Symbol
  python3 set_site_icon.py --restore ID setzt wieder das Symbol mit der Mediathek-ID ID (die alte ID zeigt der Probelauf)
"""
import json, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from update_pages import BASE, UA, auth_header, http, cloudflare

ICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medien", "camro-website-symbol-512.png")


def settings(auth):
    st, txt = http(BASE + "/wp-json/wp/v2/settings", auth=auth)
    if cloudflare(st, txt):
        sys.exit("Cloudflare blockiert den Zugriff. Bitte direkt auf dem Server ausführen.")
    if st != 200:
        sys.exit(f"Einstellungen nicht lesbar (HTTP {st}): {txt[:300]}")
    return json.loads(txt)


def set_icon(auth, media_id):
    st, txt = http(BASE + "/wp-json/wp/v2/settings", method="POST", data={"site_icon": int(media_id)}, auth=auth)
    if st != 200:
        sys.exit(f"Setzen fehlgeschlagen (HTTP {st}): {txt[:300]}")
    print("Website-Symbol gesetzt: Mediathek-ID", json.loads(txt).get("site_icon"))


def upload(auth):
    data = open(ICON, "rb").read()
    req = urllib.request.Request(BASE + "/wp-json/wp/v2/media", data=data, method="POST", headers={
        "User-Agent": UA, "Authorization": auth, "Content-Type": "image/png",
        "Content-Disposition": 'attachment; filename="camro-website-symbol-512.png"'})
    with urllib.request.urlopen(req, timeout=120) as r:
        m = json.loads(r.read().decode("utf-8"))
    print("Hochgeladen: Mediathek-ID", m["id"], m.get("source_url"))
    return m["id"]


if __name__ == "__main__":
    auth = auth_header()
    alt = settings(auth).get("site_icon")
    print("Aktuelles Website-Symbol: Mediathek-ID", alt, "(für --restore notieren)")
    if "--restore" in sys.argv:
        set_icon(auth, sys.argv[sys.argv.index("--restore") + 1])
    elif "--apply" in sys.argv:
        set_icon(auth, upload(auth))
        print("Fertig. Danach im hPanel den Cache leeren; Browser zeigen alte Favicons oft noch eine Weile an.")
    else:
        print("Probelauf – nichts geändert. Zum Ausführen: python3 set_site_icon.py --apply")
