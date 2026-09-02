#!/usr/bin/env python3
"""
Holt die aktuelle Wassertemperatur des Schlachtensees und schreibt sie
in die Datei 'wasser.json'. Wird taeglich vom GitHub-Action-Cloud-Job aufgerufen.

Quelle: wassertemperatur.org (LAGeSO-basierte Werte).
"""

import json
import re
import sys
import urllib.request
from datetime import date

QUELLE = "https://www.wassertemperatur.org/berlin/schlachtensee/"


def hole_temperatur():
    kopf = {"User-Agent": "Mozilla/5.0 (Wetter-Projekt)"}
    anfrage = urllib.request.Request(QUELLE, headers=kopf)
    with urllib.request.urlopen(anfrage, timeout=15) as antwort:
        html = antwort.read().decode("utf-8", errors="replace")

    # Sucht z.B.:  Schlachtensee: <span style="color:red">21 °C</span>
    treffer = re.search(
        r"Schlachtensee:\s*<span[^>]*>\s*(\d+(?:[.,]\d+)?)\s*°", html
    )
    if not treffer:
        raise ValueError("Wassertemperatur nicht im Seitentext gefunden.")

    return float(treffer.group(1).replace(",", "."))


def main():
    temperatur = hole_temperatur()
    daten = {
        "ort": "Schlachtensee",
        "temperatur": temperatur,
        "stand": date.today().isoformat(),  # z.B. "2026-09-02"
        "quelle": QUELLE,
    }
    with open("wasser.json", "w", encoding="utf-8") as datei:
        json.dump(daten, datei, ensure_ascii=False, indent=2)
    print("Geschrieben:", daten)


if __name__ == "__main__":
    try:
        main()
    except Exception as fehler:
        print("Fehler:", fehler, file=sys.stderr)
        sys.exit(1)
