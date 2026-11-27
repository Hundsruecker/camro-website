# CAMRO – neue Website auf camro.ro einspielen

Dieses Repository enthält das neue Design von camro.ro in Deutsch, Englisch und Rumänisch.

## Inhalt

| Ordner / Datei | Was |
| --- | --- |
| `blocks/` | Fertige WordPress-Blöcke, je Seite und Sprache eine Datei (Projektseite: Kopf und Fuß, der Projekt-Block selbst bleibt erhalten) |
| `update_pages.py` | Ersetzt die Seiten über die WordPress-Schnittstelle. Erst Probelauf, dann ändern. Sichert jede alte Fassung. |
| `entwurf/` | Der klickbare Entwurf als eigenständige HTML-Seiten, dazu `logo/` mit allen Logo-Dateien |
| `werkzeuge/` | Generator, der aus dem Entwurf die Blöcke baut, und das Skript der Kreiskarte |

Die Kreiskarte auf der Startseite holt ihre Daten live von `https://app.camro.ro/api/karte/`.
Die Projekttabelle auf der Projektseite bleibt technisch unverändert; sie bekommt nur Kopf, Fuß, Schrift und Farben des neuen Designs.

## Was Lika vorher tun muss

1. In WordPress (über hPanel, wie gewohnt) ein **Anwendungspasswort** anlegen:
   Benutzer → Profil → ganz unten „Anwendungspasswörter“ → Name `camro-update` → „Neues Anwendungspasswort hinzufügen“.
   Das angezeigte Passwort kopieren (es wird nur einmal angezeigt).
2. Den eigenen WordPress-Benutzernamen notieren (steht oben auf derselben Profilseite).
3. Beides Claude Code auf dem VPS geben – **nicht** ins Repository schreiben.

## Anweisung für Claude Code (zum Einfügen)

```
Im GitHub-Repository Hundsruecker/camro-website liegt das neue Design für camro.ro.
Bitte:
1. Repository nach ~/camro-website klonen (oder dort git pull).
2. ANLEITUNG.md lesen.
3. Die Zugangsdaten setzen, die ich dir gleich gebe, nur in dieser Shell:
   export CAMRO_WP_USER='<Benutzername>'
   export CAMRO_WP_APP_PASSWORD='<Anwendungspasswort>'
4. Probelauf: python3 update_pages.py
   Zeig mir die Liste (21 Seiten mit Seiten-ID und Titel) und warte auf mein OK.
5. Nach meinem OK zuerst nur die deutsche Kontaktseite ersetzen:
   python3 update_pages.py --apply --only kontakt_de
   Ich schaue sie mir an und gebe OK.
6. Dann alle Seiten: python3 update_pages.py --apply
7. Melde mir das Ergebnis je Seite. Falls Seiten „live noch alt“ sind, sag mir,
   dass ich im hPanel den Cache leeren muss.
Die Zugangsdaten nirgends speichern und nicht ins Repository schreiben.
Den Ordner backup/ nicht committen.
```

## Zurücksetzen

Jeder Lauf legt eine Sicherung in `backup/<Zeitstempel>/` ab. Zurückspielen:

```
python3 update_pages.py --restore backup/<Zeitstempel>
```

Zusätzlich behält WordPress jede alte Fassung als Revision (Seite bearbeiten → Revisionen).

## Wenn Cloudflare blockiert

Das Skript meldet es mit einem klaren Hinweis. Dann in Cloudflare die IP des VPS (76.13.9.75) als erlaubt eintragen
oder den Bot-Schutz für die Dauer des Updates lockern.
