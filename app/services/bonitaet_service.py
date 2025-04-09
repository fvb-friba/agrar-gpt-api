# Datei: app/services/bonitaet_service.py

import logging
import requests
from lxml import etree
from io import BytesIO

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def fetch_bonitaet_data(easting: float, northing: float) -> dict:
    """
    Holt reale Bonitätsdaten (z. B. Bodenzahl, BZB) für die übergebenen Koordinaten
    aus dem INSPIRE-konformen WFS-Dienst der LBEG (Niedersachsen).
    """

    logger.info(f"Starte Bonitätsabfrage für Punkt: Easting={easting}, Northing={northing}")

    wfs_url = "https://nibis.lbeg.de/net3/public/ogcsl.ashx"
    typename = "cls:L849"  # Bodenschätzung (Landwirtschaft)
    version = "2.0.0"
    srs = "EPSG:25832"
    output_format = "text/xml; subtype=gml/3.2"

    # Puffer um den Punkt
    buffer = 100
    minx = easting - buffer
    maxx = easting + buffer
    miny = northing - buffer
    maxy = northing + buffer

    bbox = f"{minx},{miny},{maxx},{maxy},{srs}"

    params = {
        "SERVICE": "WFS",
        "VERSION": version,
        "REQUEST": "GetFeature",
        "TYPENAMES": typename,
        "SRSNAME": srs,
        "outputFormat": output_format,
        "BBOX": bbox
    }

    try:
        response = requests.get(wfs_url, params=params)
        response.raise_for_status()
        logger.debug(f"WFS-Antwort erhalten ({len(response.content)} Bytes)")

        # GML parsen
        tree = etree.parse(BytesIO(response.content))
        ns = {
            'gml': 'http://www.opengis.net/gml/3.2',
            'lbeg': 'http://www.lbeg.de/soil'
        }

        features = tree.findall(".//gml:featureMember", namespaces=ns)
        if not features:
            logger.warning("Keine Bodenschätzungsdaten im Response gefunden.")
            return {"message": "Keine Bodenschätzungsdaten im gewählten Bereich."}

        result = []
        for feature in features:
            data = {}
            for elem in feature.iter():
                tag_clean = etree.QName(elem.tag).localname
                if elem.text and elem.text.strip():
                    data[tag_clean] = elem.text.strip()
            if data:
                result.append(data)

        logger.info(f"{len(result)} Bodendatensätze extrahiert.")
        return {"bonitaet": result}

    except Exception as e:
        logger.exception(f"WFS-Zugriff oder Parsing fehlgeschlagen: {str(e)}")
        return {"error": f"WFS-Zugriff oder Parsing fehlgeschlagen: {str(e)}"}
