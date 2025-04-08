import os
import logging
from typing import Dict, Any
import requests

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def fetch_land_value_by_regionalkey(regionalkey: str, start_year: int, end_year: int) -> Dict[str, Any]:
    """
    Holt Kaufpreise für landwirtschaftliche Grundstücke anhand eines Regionalschlüssels (Regierungsbezirk).
    Nutzt die GENESIS-API (Tabelle 61521-0020).
    """

    api_url = "https://www-genesis.destatis.de/genesisWS/rest/2020/data/table"
    username = os.getenv("DESTASIS_API_KEY")  # Hier wird der API-Key als Benutzername genutzt
    if not username:
        logger.error("API-Key nicht gefunden (Umgebungsvariable 'DESTASIS_API_KEY')")
        raise ValueError("API-Key nicht gesetzt")

    params = {
        "username": username,
        "password": "",  # bei Verwendung des Tokens als Benutzername leer lassen
        "name": "61521-0020",
        "area": "",  # leer lassen, wenn 'regionalkey' verwendet wird
        "regionalkey": regionalkey,
        "startyear": str(start_year),
        "endyear": str(end_year),
        "format": "json"
    }

    logger.info(f"Starte Abruf der Kaufpreise von {start_year} bis {end_year} für RBZ {regionalkey}")
    response = requests.get(api_url, params=params)

    if not response.ok:
        logger.error(f"Fehlerhafte Antwort von Destatis API: {response.status_code} - {response.text}")
        raise RuntimeError(f"Destatis API Fehler: {response.status_code}")

    data = response.json()
    logger.debug(f"Rohdaten von Destatis: {data}")

    try:
        values = data["Object"]["Content"]["Value"]
        years_data = []

        for entry in values:
            year = int(entry["year"])
            value = float(entry["value"].replace(",", ".")) if entry["value"] else None
            years_data.append({"year": year, "value_eur_per_m2": value})

        return {
            "regionalkey": regionalkey,
            "years": years_data
        }

    except (KeyError, ValueError) as e:
        logger.exception("Fehler beim Parsen der Destatis-Daten")
        raise RuntimeError(f"Datenverarbeitung fehlgeschlagen: {str(e)}")
