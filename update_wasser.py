#!/usr/bin/env python3
"""
Holt die aktuellen Wassertemperaturen mehrerer Seen und schreibt sie
in die Datei 'wasser.json'. Wird taeglich vom GitHub-Action-Cloud-Job aufgerufen.

Quellen: wassertemperatur.org (basiert auf offiziellen Messungen),
PEGELONLINE (Messstellen des Bundes, messen ganzjaehrig) und der serbische
Wetterdienst RHMZ (hidmet.gov.rs, ein Tageswert je Messstelle).
"""

import json
import re
import sys
import urllib.request
from datetime import date

# Die Gewaesser mit ihrer Quelle. Entweder "url" (wassertemperatur.org, dann muss
# "ort" dem Namen im Seitentext entsprechen), "pegel" (PEGELONLINE-Messstelle)
# oder "rhmz" (Nummer der Messstelle beim serbischen Wetterdienst).
SEEN = [
    {"ort": "Schlachtensee",
     "url": "https://www.wassertemperatur.org/berlin/schlachtensee/"},
    # wassertemperatur.org zeigt den Schweriner See nur in der Badesaison,
    # deshalb die ganzjaehrige Messstelle "Schwerin Werderbruecke".
    {"ort": "Schweriner See",
     "pegel": "680d5966-273f-4254-aabe-5d4e00e12a24"},
    # Messstelle "Beograd" an der Save, 0,9 km vor der Muendung in die Donau.
    {"ort": "Save Belgrad", "rhmz": "45099"},
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


def hole_rhmz_temperatur(nummer):
    url = ("https://www.hidmet.gov.rs/eng/hidrologija/izvestajne/prognoza.php?hm_id="
           + nummer)
    kopf = {"User-Agent": "Mozilla/5.0 (Wetter-Projekt)"}
    anfrage = urllib.request.Request(url, headers=kopf)
    with urllib.request.urlopen(anfrage, timeout=20) as antwort:
        html = antwort.read().decode("utf-8", errors="replace")

    # Sucht z.B.:  alt="Water temperature u profilu" />&nbsp;18.6
    temp = re.search(r'alt="Water temperature[^"]*"\s*/?>\s*(?:&nbsp;)?\s*(-?\d+(?:[.,]\d+)?)', html)
    # und das Datum des Tageswerts:  Date:&nbsp;TUESDAY,&nbsp;13.10.2026.
    tag = re.search(r"Date:(?:&nbsp;|\s)*[A-Z]+,(?:&nbsp;|\s)*(\d{1,2})\.(\d{1,2})\.(\d{4})", html)
    if not temp or not tag:
        raise ValueError(f"Wassertemperatur fuer Messstelle {nummer} nicht gefunden.")
    t, m, j = (int(x) for x in tag.groups())
    return float(temp.group(1).replace(",", ".")), date(j, m, t).isoformat()


def main():
    seen = []
    fehler = []
    for eintrag in SEEN:
        try:
            datum = None   # nur gesetzt, wenn der Wert nicht von heute ist
            if "pegel" in eintrag:
                temp = hole_pegel_temperatur(eintrag["pegel"])
            elif "rhmz" in eintrag:
                temp, datum = hole_rhmz_temperatur(eintrag["rhmz"])
            else:
                temp = hole_temperatur(eintrag["ort"], eintrag["url"])
            see = {"ort": eintrag["ort"], "temperatur": temp}
            if datum:
                see["datum"] = datum
            seen.append(see)
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
