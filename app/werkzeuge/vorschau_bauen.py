"""Rendert die App-Vorlagen mit Django zu statischen Vorschau-Seiten in app/vorschau/ (prüft dabei auch die Vorlagen-Syntax)."""
import os, django
from django.conf import settings
H = os.path.dirname(os.path.abspath(__file__)); APP = os.path.dirname(H)
settings.configure(STATIC_URL="/static/", INSTALLED_APPS=["django.contrib.staticfiles"],
    TEMPLATES=[{"BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [os.path.join(APP, "templates"), os.path.join(H, "vorlagen")]}])
django.setup()
from django.template.loader import render_to_string
seiten = [("anfrage.html", "anfrage-stellen", {}), ("anfrage.html", "anfrage-stellen-fehler", {"fehler": True}),
          ("angebot.html", "angebot", {}), ("angebot.html", "angebot-fehler", {"fehler": True})]
for vorlage, name, ctx in seiten:
    for lang in ("de",):
        html = render_to_string(vorlage, {"camro_lang": lang, **ctx})
        html = html.replace('"/static/', '"../static/')
        open(os.path.join(APP, "vorschau", f"{name}.html"), "w", encoding="utf-8").write(html)
        print(name, lang, len(html))
