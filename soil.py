import requests
from bs4 import BeautifulSoup
from pyproj import Transformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("soil")

def get_soil_data(lat: float, lon: float):
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:25832", always_xy=True)
    x, y = transformer.transform(lon, lat)

    radii = [12.5, 25, 50, 100, 200]
    for radius in radii:
        minx = x - radius
        miny = y - radius
        maxx = x + radius
        maxy = y + radius

        bbox = f"{minx},{miny},{maxx},{maxy},EPSG:25832"
        url = (
            "https://services.bgr.de/wms/boden/buek200/"
            "?service=WMS&version=1.3.0&request=GetFeatureInfo"
            f"&CRS=EPSG:25832&BBOX={minx},{miny},{maxx},{maxy}"
            f"&WIDTH=256&HEIGHT=256&I=128&J=128&INFO_FORMAT=text/html"
            f"&LAYERS=buek200&QUERY_LAYERS=buek200"
        )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, features="xml")

            logger.info(f"BBOX Radius: {radius} m")
            logger.info(f"HTML-Antwort (Ausschnitt):\n{response.text[:400]}")

            text = soup.get_text(strip=True)
            if text and "ServiceException" not in text:
                return {
                    "text": text,
                    "quelle": f"BGR WMS ({radius} m Radius)"
                }
        except Exception as e:
            logger.error(f"Fehler bei Radius {radius}: {e}")
            continue

    return {
        "detail": "Keine Bodendaten an dieser Position gefunden."
    }
