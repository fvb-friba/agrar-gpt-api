# app/services/value_service.py

import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

GENESIS_API_KEY = os.getenv("GENESIS_API_KEY")
GENESIS_API_URL = "https://www-genesis.destatis.de/genesisWS/rest/2020/data/table"
TABLE_CODE = "61521-0020"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def fetch_land_value_by_regionalkey(regionalkey: str, start_year: int, end_year: int) -> dict:
    """
    Holt Daten zur Entwicklung der Kaufpreise landwirtschaftlicher Flächen
    über die GENESIS-Webservice-API nach Regierungsbezirksschlüssel.
    """

    logger.info(f"[GENESIS] Abfrage für Tabelle={TABLE_CODE}, regionalkey={regionalkey}, Jahre={start_year}-{end_year}")

    url = f"{GENESIS_API_URL}/{TABLE_CODE}"

    params = {
        "username": GENESIS_API_KEY,
        "password": "",
        "language": "de",
        "regionalkey": regionalkey,
        "startyear": str(start_year),
        "endyear": str(end_year),
        "format": "json",
        "transpose": "true",
        "compress": "false"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        result = response.json()

        if not result.get("Object"):
            logger.warning("[GENESIS] Leere Rückgabe erhalten.")
            raise ValueError("Keine Daten verfügbar.")

        return {
            "source": "GENESIS Destatis",
            "table": TABLE_CODE,
            "region": regionalkey,
            "years": f"{start_year}-{end_year}",
            "data": result["Object"]
        }

    except Exception as e:
        logger.error(f"[GENESIS] Fehler bei Abruf: {e}")
        raise
