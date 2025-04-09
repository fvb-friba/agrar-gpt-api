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
    Holt reale Bonitätsdaten aus dem WFS-Dienst der LBEG Niedersachsen.
    Vergrößert die BBOX dynamisch, falls keine Daten gefunden werden.
    """
    wfs_url = "https://nibis.lbeg.de/net3/public/ogcsl.ashx"
    typename = "cls:L849"
    version = "2.0.0"
    srs = "EPSG:25832"
    output_format = "text/xml; subtype=gml/3.2"

    # Dynamischer Buffer: starte bei 100 m, verdopple bis max 1000 m
    buffer_sizes = [100, 200, 400, 800, 1600]

    for buffer in buffer_sizes:
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
            logger.info(f"Versuche BBOX mit Buffer {buffer} m: {bbox}")
            response = requests.get(wfs_url, params=params)
            response.raise_for_status()

            tree = etree.parse(BytesIO(response.content))
            ns = {
                'gml': 'http://www.opengis.net/gml/3.2',
                'lbeg': 'http://www.lbeg.de/soil'
            }

            features = tree.findall(".//gml:featureMember", namespaces=ns)
            logger.debug(f"BBOX {buffer} m → {len(features)} featureMember")

            if not features:
                continue  # vergrößere Buffer

            result = []
            for feature in features:
                fachobjekt = feature.find(".//lbeg:L849", namespaces=ns)
                data = {}
                if fachobjekt is not None:
                    for elem in fachobjekt.iter():
                        tag_clean = etree.QName(elem.tag).localname
                        if elem.text and elem.text.strip():
                            data[tag_clean] = elem.text.strip()
                    if data:
                        result.append(data)

            if not result:
                logger.warning("Features gefunden, aber keine verwertbaren Inhalte.")
                continue

            logger.info(f"{len(result)} Bonitäts-Objekte extrahiert.")
            return {"bonitaet": result}

        except requests.exceptions.RequestException as e:
            logger.exception("WFS-Request fehlgeschlagen")
            raise HTTPException(status_code=502, detail=f"WFS-Anfrage fehlgeschlagen: {str(e)}")

        except etree.XMLSyntaxError as e:
            logger.exception("GML/XML-Parsing fehlgeschlagen")
            raise HTTPException(status_code=500, detail=f"GML/XML-Parsing fehlgeschlagen: {str(e)}")

        except Exception as e:
            logger.exception("Allgemeiner Fehler bei Bonitätsabfrage")
            raise HTTPException(status_code=500, detail=f"Interner Fehler: {str(e)}")

    raise HTTPException(status_code=404, detail="Keine Bodenschätzungsdaten im gewählten Bereich.")
