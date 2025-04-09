# Datei: app/services/bonitaet_service.py

import logging
import requests
from lxml import etree
from io import BytesIO
from fastapi import HTTPException

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def fetch_bonitaet_data(easting: float, northing: float) -> dict:
    """
    Holt reale Bonitätsdaten (Bodenzahl, Ackerzahl, Klassifizierung etc.) aus dem WFS der LBEG.
    """

    logger.info(f"Starte Bonitätsabfrage für Punkt: Easting={easting}, Northing={northing}")

    wfs_url = "https://nibis.lbeg.de/net3/public/ogcsl.ashx"
    typename = "cls:L849"
    version = "2.0.0"
    srs = "EPSG:25832"
    output_format = "application/gml+xml; version=3.2"
    node_id = "1031"

    # Dynamische Bounding Box (kleiner Puffer)
    buffer = 50
    minx = easting - buffer
    maxx = easting + buffer
    miny = northing - buffer
    maxy = northing + buffer
    bbox = f"{minx},{miny},{maxx},{maxy}"

    params = {
        "SERVICE": "WFS",
        "VERSION": version,
        "REQUEST": "GetFeature",
        "TYPENAMES": typename,
        "SRSNAME": srs,
        "OUTPUTFORMAT": output_format,
        "BBOX": bbox,
        "NODEID": node_id
    }

    try:
        response = requests.get(wfs_url, params=params, timeout=20)
        response.raise_for_status()
        logger.debug(f"WFS-Antwort erhalten ({len(response.content)} Bytes)")

        tree = etree.parse(BytesIO(response.content))
        ns = {
            'gml': 'http://www.opengis.net/gml/3.2',
            'wfs': 'http://www.opengis.net/wfs/2.0',
            'cls': 'http://www.cardogis.com/lbeg'
        }

        features = tree.findall(".//cls:L849", namespaces=ns)
        if not features:
            logger.warning("Keine Bodenschätzungsdaten im Response gefunden.")
            raise HTTPException(status_code=404, detail="Keine Bodenschätzungsdaten im gewählten Bereich.")

        result = []

        for feature in features:
            def extract(tag):
                elem = feature.find(f"cls:{tag}", namespaces=ns)
                return elem.text.strip() if elem is not None and elem.text else None

            entry = {
                "bodenzahl": extract("BODENZ"),
                "ackerzahl": extract("ACKERZ"),
                "kulturart": extract("KLASSENZEICHEN_KLARTEXT"),
                "quelle": "LBEG Niedersachsen – Bodenschätzung",
                "area_qm": extract("AREA"),
                "update": extract("UP_DATE")
            }

            if any(entry.values()):
                result.append(entry)

        if not result:
            logger.warning("Feature gefunden, aber keine verwertbaren Inhalte.")
            raise HTTPException(status_code=404, detail="Bodenschätzungsdaten konnten nicht interpretiert werden.")

        logger.info(f"{len(result)} Bodendatensätze extrahiert.")
        return {"bonitaet": result}

    except requests.exceptions.RequestException as e:
        logger.exception("WFS-Request fehlgeschlagen")
        raise HTTPException(status_code=502, detail=f"WFS-Anfrage fehlgeschlagen: {str(e)}")

    except etree.XMLSyntaxError as e:
        logger.exception("XML-Parsing fehlgeschlagen")
        raise HTTPException(status_code=500, detail=f"GML/XML-Parsing fehlgeschlagen: {str(e)}")

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Unbekannter Fehler bei Bonitätsabfrage")
        raise HTTPException(status_code=500, detail=f"Interner Fehler: {str(e)}")
