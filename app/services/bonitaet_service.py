
import logging
import requests
from typing import Optional
from app.models.bonitaet_models import BonitaetResponse

logger = logging.getLogger(__name__)

def fetch_bonitaet_data(easting: float, northing: float) -> Optional[BonitaetResponse]:
    logger.info(f"Fetching Bonitaet data for: {easting=}, {northing=}")

    wfs_url = (
        "https://nibis.lbeg.de/net3/public/ogcsl.ashx?"
        "SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature"
        "&TYPENAMES=cls:L849"
        "&SRSNAME=EPSG:25832"
        "&outputFormat=text/xml; subtype=gml/3.2"
        f"&BBOX={easting-100},{northing-100},{easting+100},{northing+100},EPSG:25832"
    )

    try:
        response = requests.get(wfs_url)
        response.raise_for_status()
        
        if len(response.content) == 0:
            logger.warning("Empty WFS response")
            return None

        # Hier Beispiel-Parsing mit Dummy-Werten – bitte ersetzen mit echtem XML/GML-Parsing
        logger.info("Parsing response content")
        return BonitaetResponse(
            bodenzahl=72,
            naehrstoffstufe="II",
            bodenart="Lehm",
            nutzungsgrenze="Acker"
        )

    except Exception as e:
        logger.error(f"WFS-Zugriff oder Datenverarbeitung fehlgeschlagen: {e}")
        return None
