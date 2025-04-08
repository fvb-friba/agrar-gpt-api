import requests
from fastapi import HTTPException
from bs4 import BeautifulSoup

def get_buek200_info(lat: float, lon: float):
    # Nutze EPSG:4326 direkt im WMS-Aufruf
    bbox_size = 0.01
    minx, miny = lon - bbox_size / 2, lat - bbox_size / 2
    maxx, maxy = lon + bbox_size / 2, lat + bbox_size / 2

    url = "https://services.bgr.de/wms/boden/buek200/"
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetFeatureInfo",
        "LAYERS": "buek200",
        "QUERY_LAYERS": "buek200",
        "CRS": "EPSG:4326",
        "BBOX": f"{minx},{miny},{maxx},{maxy}",
        "WIDTH": 256,
        "HEIGHT": 256,
        "I": 128,
        "J": 128,
        "INFO_FORMAT": "text/html"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table")
        if not table:
            raise ValueError("Keine Tabelle gefunden.")
        result = {}
        for row in table.find_all("tr"):
            cols = row.find_all(["td", "th"])
            if len(cols) >= 2:
                key = cols[0].text.strip().lower()
                val = cols[1].text.strip()
                result[key] = val
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail="Keine Bodendaten an dieser Position gefunden.")

def get_soil_data(lat: float, lon: float):
    if not (47 <= lat <= 55 and 5 <= lon <= 15):
        raise HTTPException(status_code=400, detail="Koordinaten außerhalb Deutschlands.")
    info = get_buek200_info(lat, lon)
    return {
        "bodenart": info.get("bodenname", "unbekannt"),
        "textur": info.get("textur", "unbekannt"),
        "bodenklasse": info.get("bodenklasse", "unbekannt"),
        "quelle": "BÜK200 (BGR WMS)"
    }
