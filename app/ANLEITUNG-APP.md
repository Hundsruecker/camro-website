# App-Seiten (app.camro.ro) im neuen CAMRO-Design

Dieser Ordner enthält alles, damit die öffentlichen Seiten der App genauso aussehen wie camro.ro:
gleiche Kopfzeile mit Menü und Sprachschalter (Deutsch / English / Română), gleiche Fußzeile, gleiche Schrift und Farben, volle Breite.

| Datei | Zweck |
|---|---|
| `static/crm/camro-app.css` | Gestaltung (wirkt nur auf Seiten mit `<body class="camro-app">`, das Admin bleibt unberührt) |
| `static/crm/img/camro-favicon-32.png`, `camro-apple-touch-icon-180.png` | Symbole für den Browser-Tab |
| `templates/crm/camro/basis.html` | Grundgerüst, von dem jede öffentliche Seite erbt |
| `templates/crm/camro/_kopf.html`, `_fuss.html` | Kopf- und Fußzeile wie auf camro.ro |
| `vorschau/*.html` | So sehen „Anfrage stellen“ und „Angebot“ danach aus (auch mit Fehlermeldungen) |
| `werkzeuge/vorschau_bauen.py` | Baut die Vorschau neu und prüft dabei die Vorlagen |

## Auftrag für Claude Code (auf dem VPS)

Im Terminal `cd ~/camro-crm && claude` starten und diesen Text einfügen:

```
Bitte passe die öffentlichen Seiten dieser Django-App (app.camro.ro) an das neue Design von camro.ro an.
Vorlage liegt im Repository ~/camro-website (vorher dort "git pull" ausführen), Ordner app/. Lies zuerst app/ANLEITUNG-APP.md.

1. Kopiere app/static/crm/camro-app.css und app/static/crm/img/camro-*.png in das static-Verzeichnis der App
   (dorthin, wo heute static/crm/img/camro_logo.png liegt). Kopiere app/templates/crm/camro/ in das
   Template-Verzeichnis, in dem die crm-Vorlagen liegen, sodass {% extends "crm/camro/basis.html" %} funktioniert.

2. Finde alle öffentlichen Seiten, also alles, was Gemeinden, Unterstützer oder Besucher ohne Admin-Login sehen:
   mindestens /anfrage-stellen/ und /angebot/ samt ihren Danke-/Bestätigungsseiten, außerdem jede weitere Vorlage
   mit dem alten Kopf (Suche nach "sprachumschalter" oder "camro_logo.png" in den Templates), z. B. Antragsformular
   per Link oder Fragebögen. Das Django-Admin bzw. Unfold und Login-Seiten NICHT anfassen.

3. Baue jede dieser Vorlagen so um, dass sie von crm/camro/basis.html erbt:
   - {% block titel %}: der bisherige Seitentitel ohne " – CAMRO"
   - {% block ueberschrift %}: der bisherige Text aus <header><h1>
   - {% block einleitung %}: das bisherige <div class="intro">…</div> unverändert
   - {% block inhalt %}: <section class="app-form"><div class="wrap"> + das bisherige <form>…</form> UNVERÄNDERT + </div></section>.
     Seiten ohne Formular (Danke-Seiten usw.): <section class="app-text"><div class="wrap">…bisheriger Inhalt…</div></section>
   - {% block skripte %}: die bisherigen <script>-Blöcke unverändert
   - Den alten <header>, das Logo-Bild und den alten Inline-<style> entfernen. Seitenspezifische Regeln, die für die
     Funktion nötig sind (z. B. "#neue-gemeinde-felder { display:none; }"), in {% block kopf_extra %} als <style> behalten.
   - Menüpunkt markieren über {% block camro_kopf %}{% include "crm/camro/_kopf.html" with camro_bereich="gemeinden" %}{% endblock %}
     (Anfrage/Antrag von Gemeinden: "gemeinden"; Angebot von Unterstützern: "unterstuetzer").

4. Sprache: basis.html, _kopf.html und _fuss.html brauchen die Variable camro_lang ("de", "en" oder "ro") –
   genau die Sprache, in der die Seite gerade ihre Texte zeigt. Stelle sie über den bestehenden Mechanismus der App bereit
   (z. B. im View-Kontext oder per Context-Processor aus der vorhandenen Sprachlogik). Zeige im Sprachschalter nur die
   Sprachen, die die jeweilige Seite heute schon anbietet (Parameter camro_sprachen, z. B. "de,ro").
   Falls der alte Sprachschalter mehr als "?lang=xx" in seine Links schrieb (z. B. ein Token), übergib dieselben Ziele
   als url_de / url_en / url_ro, damit nichts verloren geht.

5. Nicht ändern: Formularfelder, Feldnamen, IDs, Validierung, Views-Logik, URLs, E-Mail-Versand, Datenbank.

6. Danach ggf. collectstatic ausführen und den App-Dienst neu starten, so wie es in diesem Projekt üblich ist.
   Prüfe jede angepasste Seite in jeder angebotenen Sprache mit einem GET-Aufruf (Status 200, Kopf/Fuß vorhanden,
   <body class="camro-app">). Keine Formulare absenden, damit keine Testdaten in der Datenbank landen.
   Zeige mir am Ende eine Liste der angepassten Seiten mit ihren Adressen.

Zugangsdaten nirgends speichern und nicht ins Repository schreiben.
```

## Vorschau neu bauen

```
pip install django
python3 app/werkzeuge/vorschau_bauen.py
```
