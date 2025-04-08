import requests
from app.utils.logger import get_logger

logger = get_logger("soil")

WMS_URL = "https://services.bgr.de/wms/boden/buek200/"
LAYER_NAME = "buek200"
CRS = "EPSG:25832"
INFO_FORMAT = "text/plain"
IMG_SIZE = 256

def fetch_soil_info(easting: float, northing: float) -> dict:
    bbox_size = 500
    retries = 3

    for attempt in range(retries):
        half = bbox_size / 2
        bbox = (
            easting - half,
            northing - half,
            easting + half,
            northing + half
        )

        logger.info(f"GetFeatureInfo für Koordinaten: ({easting}, {northing}), Versuch {attempt+1}, BBOX: {bbox}")

        params = {
            "SERVICE": "WMS",
            "VERSION": "1.3.0",
            "REQUEST": "GetFeatureInfo",
            "LAYERS": LAYER_NAME,
            "QUERY_LAYERS": LAYER_NAME,
            "CRS": CRS,
            "BBOX": ",".join(map(str, bbox)),
            "WIDTH": IMG_SIZE,
            "HEIGHT": IMG_SIZE,
            "INFO_FORMAT": INFO_FORMAT,
            "I": IMG_SIZE // 2,
            "J": IMG_SIZE // 2
        }

        try:
            response = requests.get(WMS_URL, params=params, timeout=10)
            response.raise_for_status()

            if "Feature" in response.text and "BKZ" in response.text:
                bkz = extract_attribute(response.text, "BKZ")
                bez = extract_attribute(response.text, "BEZ")
                return {
                    "bkz": bkz,
                    "bez": bez,
                    "raw_response": response.text
                }
            else:
                logger.warning(f"Leere oder ungültige Antwort, nächste Vergrößerung. Inhalt: {response.text[:200]}")
                bbox_size *= 2

        except Exception as e:
            logger.error(f"Fehler bei WMS-Anfrage: {str(e)}")

    raise ValueError("Keine gültige Bodeninformation abrufbar.")

def extract_attribute(text: str, key: str) -> str:
    for line in text.splitlines():
        if key in line:
            return line.split("=")[-1].strip()
    return "-"
