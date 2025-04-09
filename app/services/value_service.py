
import os
import logging
import requests
import csv
from io import StringIO
from typing import Dict, Any

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)


def fetch_land_value_by_regionalkey(regionalkey: str, start_year: int, end_year: int) -> Dict[str, Any]:
    """
    Holt Kaufpreise für landwirtschaftliche Grundstücke anhand eines Regionalschlüssels (Regierungsbezirk).
    Nutzt die GENESIS-API (Tabelle 61521-0020), extrahiert CSV aus JSON-Feld.
    """

    api_url = "https://www-genesis.destatis.de/genesisWS/rest/2020/data/table"
    username = os.getenv("DESTASIS_API_KEY")
    if not username:
        logger.error("API-Key nicht gefunden (Umgebungsvariable 'DESTASIS_API_KEY')")
        raise ValueError("API-Key nicht gesetzt")

    params = {
        "username": username,
        "name": "61521-0020",
        "format": "datencsv",
        "regionalkey": regionalkey,
        "startyear": str(start_year),
        "endyear": str(end_year)
    }

    logger.info(f"Starte GET-Abruf der Kaufpreise von {start_year} bis {end_year} für RBZ {regionalkey}")
    response = requests.get(api_url, params=params)

    if not response.ok:
        logger.error(f"Fehlerhafte Antwort von Destatis API: {response.status_code} - {response.text}")
        raise RuntimeError(f"Destatis API Fehler: {response.status_code}")

    try:
        data = response.json()
        csv_text = data["Object"]["Content"]
        logger.debug("CSV-Inhalt erfolgreich aus JSON extrahiert.")
    except Exception as e:
        logger.exception("Fehler beim Parsen der JSON-Antwort von Destatis.")
        raise RuntimeError("Antwort konnte nicht als JSON interpretiert werden.")

    # Jetzt beginnt echtes CSV-Parsing
    years_data = []
    zeilenzähler = 0

    try:
        csv_reader = csv.reader(StringIO(csv_text), delimiter=';')
        for row in csv_reader:
            zeilenzähler += 1
            if len(row) >= 7:
                logger.debug(f"Zeile {zeilenzähler}: {row[:8]}")
                if "Insgesamt" in row[2] and "Insgesamt" in row[3]:
                    try:
                        year = int(row[0])
                        raw_value = row[6].replace(".", "").replace(",", ".")
                        value = float(raw_value) if raw_value else None
                        years_data.append({"year": year, "value_eur_per_ha": value})
                    except ValueError as ve:
                        logger.warning(f"Fehler beim Parsen der Zeile {zeilenzähler}: {row} – {ve}")
                        continue

        if not years_data:
            raise ValueError("Keine gültigen Zeilen mit 'Insgesamt' gefunden.")

        logger.info(f"Erfolgreich {len(years_data)} Jahre verarbeitet.")
        return {
            "regionalkey": regionalkey,
            "years": years_data
        }

    except Exception as e:
        logger.exception("Fehler beim Parsen der CSV-Daten von Destatis")
        raise RuntimeError(f"Datenverarbeitung fehlgeschlagen: {str(e)}")
