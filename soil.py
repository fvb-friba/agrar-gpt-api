import requests
from fastapi import HTTPException
from bs4 import BeautifulSoup

def get_wms_featureinfo(url, lat, lon, layer, info_format="text/html"):
    try:
        params = {
            "SERVICE": "WMS",
            "VERSION": "1.3.0",
            "REQUEST": "GetFeatureInfo",
            "LAYERS": layer,
            "QUERY_LAYERS": layer,
            "CRS": "EPSG:4326",
            "BBOX": f"{lat-0.005},{lon-0.005},{lat+0.005},{lon+0.005}",
            "WIDTH": 101,
            "HEIGHT": 101,
            "I": 50,
            "J": 50,
            "INFO_FORMAT": info_format
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

    # BÜK200 (Bodenart, Textur)
    buek_url = "https://services.bgr.de/wms/boden/buek200/"
    buek_layer = "buek200"
    buek_info = get_wms_featureinfo(buek_url, lat, lon, buek_layer)
    buek_data = parse_html_table(buek_info) if buek_info else {}

    # BODEN-DÜS (Bonität)
    boden_url = "https://services.bgr.de/wms/boden/boeschreibung/"
    boden_layer = "boeschreibung"
    boden_info = get_wms_featureinfo(boden_url, lat, lon, boden_layer)
    boden_data = parse_html_table(boden_info) if boden_info else {}

    if not buek_data and not boden_data:
        raise HTTPException(status_code=404, detail="Keine Bodendaten an dieser Position gefunden.")

    return {
        "bodenart": buek_data.get("bodenname", "k.A."),
        "textur": buek_data.get("textur", "k.A."),
        "bodenklasse": buek_data.get("bodenklasse", "k.A."),
        "ackerzahl": int(boden_data.get("ackerzahl", "0")),
        "gruenlandzahl": int(boden_data.get("grünlandzahl", "0")),
        "bodenpunkte": int(boden_data.get("bodenpunkte", "0"))
    }
