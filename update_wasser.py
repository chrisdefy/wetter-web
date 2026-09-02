#!/usr/bin/env python3
"""
Holt die aktuellen Wassertemperaturen mehrerer Seen und schreibt sie
in die Datei 'wasser.json'. Wird taeglich vom GitHub-Action-Cloud-Job aufgerufen.

Quelle: wassertemperatur.org (basiert auf offiziellen Messungen).
"""

import json
import re
import sys
import urllib.request
from datetime import date

# Die Seen mit ihrer Quelle. "ort" muss dem Namen im Seitentext entsprechen.
SEEN = [
    {"ort": "Schlachtensee",
     "url": "https://www.wassertemperatur.org/berlin/schlachtensee/"},
    {"ort": "Schweriner See",
     "url": "https://www.wassertemperatur.org/schweriner-see/"},
]


def hole_temperatur(ort, url):
    kopf = {"User-Agent": "Mozilla/5.0 (Wetter-Projekt)"}
    anfrage = urllib.request.Request(url, headers=kopf)
    with urllib.request.urlopen(anfrage, timeout=15) as antwort:
        html = antwort.read().decode("utf-8", errors="replace")

    # Sucht z.B.:  Schlachtensee: <span style="color:red">21 °C</span>
    treffer = re.search(
        re.escape(ort) + r":\s*<span[^>]*>\s*(\d+(?:[.,]\d+)?)\s*°", html
    )
    if not treffer:
        raise ValueError(f"Wassertemperatur fuer '{ort}' nicht gefunden.")

    return float(treffer.group(1).replace(",", "."))


def main():
    seen = []
    fehler = []
    for eintrag in SEEN:
        try:
            temp = hole_temperatur(eintrag["ort"], eintrag["url"])
            seen.append({"ort": eintrag["ort"], "temperatur": temp})
        except Exception as e:
            fehler.append(f"{eintrag['ort']}: {e}")

    if not seen:
        # Nur abbrechen, wenn KEIN einziger See geklappt hat.
        raise RuntimeError("Kein See konnte gelesen werden. " + "; ".join(fehler))

    daten = {"stand": date.today().isoformat(), "seen": seen}
    with open("wasser.json", "w", encoding="utf-8") as datei:
        json.dump(daten, datei, ensure_ascii=False, indent=2)
    print("Geschrieben:", daten)
    if fehler:
        print("Warnung (einzelne Seen fehlten):", "; ".join(fehler), file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except Exception as fehler:
        print("Fehler:", fehler, file=sys.stderr)
        sys.exit(1)
