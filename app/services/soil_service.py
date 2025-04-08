import requests
import os
from xml.etree import ElementTree as ET
from app.utils.logger import get_logger

logger = get_logger("soil")

WMS_URL = "https://services.bgr.de/wms/boden/buek200/"
CRS = "EPSG:25832"
INFO_FORMAT = "text/xml"
IMG_SIZE = 256

CAPABILITIES_XML_PATH = os.path.join(os.path.dirname(__file__), "bgr_capabilities.xml")

LAYER_DEFINITIONS = []

def load_layer_definitions(xml_path: str):
    global LAYER_DEFINITIONS
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {'wms': 'http://www.opengis.net/wms'}

    for layer in root.findall(".//wms:Layer/wms:Layer", ns):
        name_elem = layer.find("wms:Name", ns)
        bbox_elem = layer.find("wms:BoundingBox[@CRS='EPSG:25832']", ns)
        if name_elem is not None and bbox_elem is not None:
            bbox = (
                float(bbox_elem.attrib["minx"]),
                float(bbox_elem.attrib["miny"]),
                float(bbox_elem.attrib["maxx"]),
                float(bbox_elem.attrib["maxy"])
            )
            LAYER_DEFINITIONS.append({
                "name": name_elem.text,
                "bbox": bbox
            })
    logger.info(f"{len(LAYER_DEFINITIONS)} Layerdefinitionen geladen.")

def find_layer_by_coords(easting: float, northing: float) -> str:
    for layer in LAYER_DEFINITIONS:
        minx, miny, maxx, maxy = layer["bbox"]
        if minx <= easting <= maxx and miny <= northing <= maxy:
            logger.info(f"Koordinate ({easting}, {northing}) liegt in Layer: {layer['name']}")
            return layer["name"]
    logger.warning(f"Keine Layer-BBOX enthält Koordinate ({easting}, {northing})")
    return None

def fetch_soil_info(easting: float, northing: float) -> dict:
    if not LAYER_DEFINITIONS:
        load_layer_definitions(CAPABILITIES_XML_PATH)

    layer_name = find_layer_by_coords(easting, northing)
    if not layer_name:
        raise ValueError("Kein passender Layer für diese Koordinate gefunden.")

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

        logger.info(f"GetFeatureInfo für Layer '{layer_name}', BBOX: {bbox}")

        params = {
            "SERVICE": "WMS",
            "VERSION": "1.3.0",
            "REQUEST": "GetFeatureInfo",
            "LAYERS": layer_name,
            "QUERY_LAYERS": layer_name,
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

            if "<" in response.text and "Feature" in response.text:
                bkz = extract_xml_attribute(response.text, "BKZ")
                bez = extract_xml_attribute(response.text, "BEZ")
                return {
                    "bkz": bkz,
                    "bez": bez,
                    "raw_response": response.text
                }
            else:
                logger.warning(f"Leere XML-Antwort – neue BBOX. Inhalt: {response.text[:200]}")
                bbox_size *= 2

        except Exception as e:
            logger.error(f"WMS-Anfrage fehlgeschlagen: {str(e)}")

    raise ValueError("Keine gültige Bodeninformation abrufbar.")

def extract_xml_attribute(xml_text: str, key: str) -> str:
    try:
        root = ET.fromstring(xml_text)
        for elem in root.iter():
            if elem.tag.endswith("Attribute") and elem.attrib.get("name") == key:
                return elem.text.strip()
    except ET.ParseError as e:
        logger.error(f"Fehler beim Parsen der XML-Antwort: {e}")
    return "-"
