import requests
import csv
from io import StringIO
from urllib.parse import quote
from fastapi import HTTPException

# GENESIS API-Zugangsdaten
USERNAME = quote("f.vonbraunschweig@friba-investment.com")
PASSWORD = "49efaedd2eb84800a34f4bca2045ea71"
BASE_URL = "https://www-genesis.destatis.de/genesisWS/rest/2020/data/tablefile"

def get_land_value(landkreis: str):
    try:
        params = {
            "username": USERNAME,
            "password": PASSWORD,
            "name": "61111-0001",
            "format": "csv",
            "area": "all",
            "compress": "false"
        }
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()

        content = response.content.decode("utf-8", errors="replace")
        reader = csv.reader(StringIO(content), delimiter=';')

        result = {}
        for row in reader:
            if len(row) < 3:
                continue
            if landkreis.lower() in row[0].lower():
                try:
                    jahr = row[1].strip()
                    preis = float(row[2].replace(",", "."))
                    result[jahr] = preis
                except:
                    continue

        if not result:
            raise HTTPException(status_code=404, detail="Keine Kaufpreisdaten gefunden.")

        return {
            "landkreis": landkreis,
            "preise_eur_ha": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
