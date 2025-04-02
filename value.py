import csv
import requests
from fastapi import HTTPException

# Simplifizierte statische Kaufpreisdaten als Beispiel
# In einem Live-System würde hier ein Abruf von Destatis erfolgen
KAUFPREISE = {
    "Dithmarschen": {
        "2022": 34567,
        "2021": 33320,
        "2020": 31900
    },
    "01051": {  # Schlüssel für Dithmarschen
        "2022": 34567,
        "2021": 33320,
        "2020": 31900
    }
}

def get_land_value(landkreis: str):
    data = KAUFPREISE.get(landkreis)
    if not data:
        raise HTTPException(status_code=404, detail="Keine Kaufpreisdaten für diesen Landkreis gefunden.")
    return {
        "landkreis": landkreis,
        "preise_eur_ha": data
    }
