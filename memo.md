# memo.md — Sitzungs-Tagebuch (Wetter-Web)

Fortlaufendes Protokoll unserer Arbeitssitzungen. **Neueste Sitzung oben.**
Zweck: Damit wir in einer neuen Sitzung nahtlos weitermachen, ohne dass etwas verloren geht.

> Für Claude: Diese Datei zu Beginn jeder Sitzung lesen. Am Ende jeder Sitzung
> oben einen neuen Eintrag im gleichen Format ergänzen (Datum, Gemacht, Stand, Nächste Ideen).

---

## 2026-09-02 — Projekt von Grund auf gebaut

**Gemacht (in dieser Reihenfolge):**
- Von den Grundlagen gestartet (Bash, Git vs. GitHub, lokal vs. Cloud erklärt).
- Wetter-Programm in Python gebaut: `wetter.py` (Terminal) + `wetter_gui.py` (Fenster).
  Als eigenständige Mac-App verpackt (PyInstaller). Liegt separat unter `~/wetter/`.
  Wichtig gelernt: Apples System-Python 3.9 hat kaputtes Tk 8.5 (schwarzes Fenster) →
  Homebrew `python-tk@3.14` (Tk 9) genutzt.
- Web-Version gebaut (`index.html`): schön, plattformübergreifend.
- Über Git zu GitHub hochgeladen und via **GitHub Pages** live gestellt.
- Kurzlink erstellt (TinyURL) — wirkt aber „dubios"; besser die klare Adresse teilen.
- 5-Tage-Vorhersage mit Regenwahrscheinlichkeit ergänzt.
- Seewassertemperatur ergänzt (Schlachtensee, dann Schweriner See) — via täglichem
  GitHub-Action-Cronjob (`update_wasser.py` → `wasser.json`), weil es keine CORS-API gibt.
- Städte ergänzt: Potsdam, Berlin, Schwerin, Bad Schmiedeberg, Alanya (Türkei).
- Alanya-Meerwasser: live über Open-Meteo Marine-API (CORS-fähig, kein Cronjob nötig).
- Projekt lokal gesichert nach `~/Desktop/Projekte/Wetter-Web/` (einzige Arbeitskopie;
  loses `~/wetter-web` wurde entfernt). GitHub bleibt Cloud-Backup.
- `CLAUDE.md` per `init` erstellt; diese `memo.md` als Sitzungs-Tagebuch eingeführt.

**Stand:** Fertig, live, gesichert, dokumentiert. Sauberer Stopp-Punkt.

**Live:** https://chrisdefy.github.io/wetter-web/ · Kurzlink: https://tinyurl.com/29wtdq2s

**Nächste Ideen / offen:**
- Eigene Wunsch-Domain (z. B. `wetter.<name>.de`) mit GitHub Pages verbinden
  (~5–15 €/Jahr; macht den Link seriöser). Beim nächsten Mal gern zusammen einrichten.
- Weitere Städte/Seen jederzeit leicht ergänzbar (siehe CLAUDE.md).
- Der Nutzer hat weitere, andere Projekte, die er starten möchte.
