#!/usr/bin/env python3
"""
Holt die aktuellen Wassertemperaturen mehrerer Seen und schreibt sie
in die Datei 'wasser.json'. Wird taeglich vom GitHub-Action-Cloud-Job aufgerufen.

Quellen: wassertemperatur.org (basiert auf offiziellen Messungen) und
PEGELONLINE (Messstellen des Bundes, messen ganzjaehrig).
"""

import json
import re
import sys
import urllib.request
from datetime import date

# Die Seen mit ihrer Quelle. Entweder "url" (wassertemperatur.org, dann muss
# "ort" dem Namen im Seitentext entsprechen) oder "pegel" (PEGELONLINE-Messstelle).
SEEN = [
    {"ort": "Schlachtensee",
     "url": "https://www.wassertemperatur.org/berlin/schlachtensee/"},
    # wassertemperatur.org zeigt den Schweriner See nur in der Badesaison,
    # deshalb die ganzjaehrige Messstelle "Schwerin Werderbruecke".
    {"ort": "Schweriner See",
     "pegel": "680d5966-273f-4254-aabe-5d4e00e12a24"},
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


def hole_pegel_temperatur(pegel):
    url = ("https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/"
           + pegel + "/WT/currentmeasurement.json")
    with urllib.request.urlopen(url, timeout=15) as antwort:
        messung = json.load(antwort)   # z.B. {"timestamp": "...", "value": 13.8}
    return float(messung["value"])


def main():
    seen = []
    fehler = []
    for eintrag in SEEN:
        try:
            if "pegel" in eintrag:
                temp = hole_pegel_temperatur(eintrag["pegel"])
            else:
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
