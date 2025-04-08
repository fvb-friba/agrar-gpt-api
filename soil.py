import requests
from pyproj import Transformer
from bs4 import BeautifulSoup
from fastapi import HTTPException

def get_feature_info_utm(lat, lon, url, layer):
    try:
        # EPSG:4326 → EPSG:25832 (UTM Zone 32N)
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:25832", always_xy=True)
        x, y = transformer.transform(lon, lat)

        bbox_size = 200  # Meter
        minx, miny = x - bbox_size / 2, y - bbox_size / 2
        maxx, maxy = x + bbox_size / 2, y + bbox_size / 2

        params = {
            "SERVICE": "WMS",
            "VERSION": "1.3.0",
            "REQUEST": "GetFeatureInfo",
            "LAYERS": layer,
            "QUERY_LAYERS": layer,
            "CRS": "EPSG:25832",
            "BBOX": f"{minx},{miny},{maxx},{maxy}",
            "WIDTH": 256,
            "HEIGHT": 256,
            "I": 128,
            "J": 128,
            "INFO_FORMAT": "text/html"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.text

    except Exception as e:
        return None

def parse_html_table(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return {}
    result = {}
    for row in table.find_all("tr"):
        cols = row.find_all(["td", "th"])
        if len(cols) >= 2:
            key = cols[0].text.strip().lower()
            val = cols[1].text.strip()
            result[key] = val
    return result

def get_soil_data(lat: float, lon: float):
    if not (47 <= lat <= 55) or not (5 <= lon <= 15):
        raise HTTPException(status_code=400, detail="Koordinaten außerhalb Deutschlands.")

    buek_url = "https://services.bgr.de/wms/boden/buek200/"
    buek_layer = "buek200"

    boeschr_url = "https://services.bgr.de/wms/boden/boeschreibung/"
    boeschr_layer = "boeschreibung"

    buek_info = get_feature_info_utm(lat, lon, buek_url, buek_layer)
    boeschr_info = get_feature_info_utm(lat, lon, boeschr_url, boeschr_layer)

    buek_data = parse_html_table(buek_info) if buek_info else {}
    boeschr_data = parse_html_table(boeschr_info) if boeschr_info else {}

    if not buek_data and not boeschr_data:
        raise HTTPException(status_code=404, detail="Keine Bodendaten an dieser Position gefunden.")

    return {
        "bodenart": buek_data.get("bodenname", "k.A."),
        "textur": buek_data.get("textur", "k.A."),
        "bodenklasse": buek_data.get("bodenklasse", "k.A."),
        "ackerzahl": int(boeschr_data.get("ackerzahl", "0")),
        "gruenlandzahl": int(boeschr_data.get("grünlandzahl", "0")),
        "bodenpunkte": int(boeschr_data.get("bodenpunkte", "0"))
    }
