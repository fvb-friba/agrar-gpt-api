import requests
import os
from typing import Optional, List
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger("value")

GENESIS_USERNAME = os.getenv("GENESIS_USERNAME")
GENESIS_API_KEY = os.getenv("GENESIS_API_KEY")

if not GENESIS_USERNAME or not GENESIS_API_KEY:
    logger.error("GENESIS Zugangsdaten fehlen – Umgebungsvariablen prüfen.")
    raise EnvironmentError("GENESIS API-Zugang nicht gesetzt")

GENESIS_BASE_URL = "https://www-genesis.destatis.de/genesisWS/rest/2020/data"
TABLE_CODE = "61241-01-01-4-B"  # Kaufwerte landw. Grundstücke

def fetch_value_data(ags: str) -> dict:
    end_year = datetime.now().year
    start_year = end_year - 9

    logger.info(f"Frage GENESIS für AGS={ags}, Zeitraum {start_year}-{end_year} ab")

    params = {
        "username": GENESIS_USERNAME,
        "password": GENESIS_API_KEY,
        "name": TABLE_CODE,
        "bereich": "allgemein",
        "format": "json",
        "startjahr": str(start_year),
        "endjahr": str(end_year),
        "regionalschluessel": ags,
        "language": "de"
    }
    
    url = f"{GENESIS_BASE_URL}/value"
    
    print(f"GENESIS Request URL: {url}")
    print(f"GENESIS Params: {params}")

    try:
        response = requests.get(url, params=params, timeout=15)
        print(f"GENESIS Response Text: {response.text[:500]}")
        response.raise_for_status()
        data = response.json()
        logger.info(f"GENESIS Rückgabe OK – {len(data.get('Object', []))} Einträge")

        items = []
        for obj in data.get("Object", []):
            try:
                jahr = int(obj["Jahr"])
                wert = float(obj["Inhalt"])
                einheit = obj["Einheit"]
                items.append({
                    "year": jahr,
                    "avg_price_eur_per_ha": round(wert, 2),
                    "unit": einheit,
                    "num_cases": None  # Optional: separate Tabelle nötig
                })
            except Exception as parse_err:
                logger.warning(f"Konnte Wert nicht parsen: {parse_err}")

        if not items:
            raise ValueError("Keine gültigen Daten empfangen")

        return {
            "region": obj.get("1 REGION", ags),
            "ags": ags,
            "unit": items[0]["unit"] if items else "EUR/ha",
            "years": items
        }

    except Exception as e:
        logger.error(f"GENESIS API Fehler: {e}")
        raise ValueError("Fehler beim Abrufen der Kaufpreise")

# 🧭 AGS über Koordinaten (vereinfacht)
def resolve_ags_from_coords(easting: float, northing: float) -> Optional[str]:
    logger.info(f"Simulierter AGS-Lookup für Koordinate: {easting}, {northing}")
    # 👉 Später ersetzen durch echten Geo-Service
    return "05315"  # Beispiel: Duisburg
