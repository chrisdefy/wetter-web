# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Was das ist

Eine statische Wetter-Webseite (eine einzige `index.html`, kein Build-Schritt), die für mehrere Städte das aktuelle Wetter + 5-Tage-Vorhersage mit Regenwahrscheinlichkeit anzeigt, dazu Seewassertemperaturen (deutsche Seen) und die Meerwassertemperatur (Alanya). Deployt über GitHub Pages, live unter https://chrisdefy.github.io/wetter-web/ (Repo `chrisdefy/wetter-web`, Branch `main`, Root-Ordner).

Der Nutzer ist Programmier-Einsteiger und kommuniziert auf Deutsch — Erklärungen einfach und schrittweise halten.

**Wo wir stehen:** `memo.md` ist das fortlaufende Sitzungs-Tagebuch. Lies es zu Beginn jeder Sitzung (neueste Einträge oben), um dort weiterzumachen, wo zuletzt aufgehört wurde — und ergänze am Ende der Sitzung einen neuen datierten Eintrag.

## Häufige Befehle

- **Lokal ansehen:** `python3 -m http.server 8765`, dann http://localhost:8765/ öffnen.
  Wichtig: **nicht** die Datei per Doppelklick (`file://`) öffnen — dann blockiert der Browser das Laden von `wasser.json` (CORS bei lokalen Dateien).
- **See-Updater testen:** `python3 update_wasser.py` (schreibt `wasser.json` neu).
- **Deployen:** `git push origin main` → GitHub Pages veröffentlicht automatisch (~1 Min). Danach ggf. Browser-Cache beachten (`cache-control: max-age=600`, also bis zu 10 Min; hart neu laden oder privates Fenster).
- **See-Job manuell auslösen:** `gh workflow run wasser.yml`, Status: `gh run list --workflow=wasser.yml --limit 1`.

Kein Build, keine Tests, kein Linter.

## Architektur — der zentrale Punkt

Datenquellen unterscheiden sich danach, ob sie **im Browser** (CORS-fähig) abrufbar sind:

1. **Live im Browser** (client-seitig in `index.html`, kein Server nötig):
   - Wetter + 5-Tage-Vorhersage: Open-Meteo `api.open-meteo.com` (pro Stadt in `STAEDTE`).
   - Meerwasser Alanya: Open-Meteo Marine `marine-api.open-meteo.com` (`sea_surface_temperature`, Punkt `MEER_ALANYA` leicht im Wasser).

2. **Nicht im Browser abrufbar → über einen Umweg** (deutsche Seen):
   Für Seewassertemperaturen gibt es keine CORS-fähige API. Deshalb liest ein täglicher GitHub-Action-Cronjob (`.github/workflows/wasser.yml`) die Werte server-seitig über `update_wasser.py` (scrapt wassertemperatur.org) und committet sie in `wasser.json`. Die Seite lädt diese Datei **same-origin** (kein CORS-Problem) in `ladeWasser()`.

## Änderungen — die üblichen Stellen

- **Stadt hinzufügen:** Eintrag `{ name, lat, lon }` im `STAEDTE`-Array in `index.html`. Sonst nichts nötig — Wetter und Vorhersage kommen automatisch.
- **See hinzufügen:** Eintrag `{ ort, url }` in der `SEEN`-Liste in `update_wasser.py`. `ort` **muss** exakt dem Namen entsprechen, wie er im Seitentext der Quelle vor der Temperatur steht (die Regex sucht `"<ort>: <span ...>NN °"`). Die Seite zeigt alle Einträge aus `wasser.json` automatisch an.
- **Meer-Standort ändern:** `MEER_ALANYA` in `index.html`. Der Punkt muss über Wasser liegen, sonst liefert die Marine-API `null`.

## Fallstricke

- `update_wasser.py` scrapt fremdes HTML — bricht das Muster bei einer Seitenänderung der Quelle, schlägt der Wert fehl; die Kachel zeigt dann einfach nichts (Rest der Seite läuft weiter). Das Skript bricht nur ab, wenn **kein** See gelesen werden konnte.
- Der Action-Job committet nur, wenn sich `wasser.json` geändert hat (sonst „nichts zu tun").
