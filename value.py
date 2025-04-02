import requests
import csv
from io import StringIO
from fastapi import HTTPException

def get_land_value(landkreis: str):
    try:
        # Quelle: https://www-genesis.destatis.de/genesis/online
        # Wir verwenden Tabelle 61111-01-01-4 (flächenspez. Kaufwerte, je Bundesland)
        url = "https://www-genesis.destatis.de/genesis/downloads/00/tables/61111-01-01-4.csv"
        response = requests.get(url)
        response.raise_for_status()

        content = response.content.decode("utf-8")
        csv_reader = csv.reader(StringIO(content), delimiter=";")

        result = {}
        for row in csv_reader:
            if landkreis.lower() in row[0].lower():
                try:
                    jahr = row[1].strip()
                    preis = float(row[2].strip().replace(",", "."))
                    result[jahr] = preis
                except:
                    continue

        if not result:
            raise HTTPException(status_code=404, detail="Keine echten Daten gefunden.")

        return {
            "landkreis": landkreis,
            "preise_eur_ha": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
