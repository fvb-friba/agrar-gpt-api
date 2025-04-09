
import geopandas as gpd
from shapely.geometry import Point
from pyproj import CRS
from app.utils.logger import get_logger

logger = get_logger("bonitaet")

# WFS mit GML-Ausgabe und URL-encoded Formatparameter
NDS_WFS_GML_URL = (
    "https://nibis.lbeg.de/net3/public/ogcsl.ashx"
    "?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature"
    "&TYPENAMES=cls:L849"
    "&SRSNAME=EPSG:25832"
    "&outputFormat=text/xml;%20subtype=gml/3.2"
)

def fetch_bonitaet_data(easting: float, northing: float) -> dict:
    logger.info(f"Starte Bonitätsabfrage für (E:{easting}, N:{northing}) [EPSG:25832]")
    point = Point(easting, northing)

    try:
        # Umkreis für WFS-BBOX (Meter)
        buffer = 100
        bbox = (easting - buffer, northing - buffer, easting + buffer, northing + buffer)

        # GML laden mit geopandas + fiona
        gdf = gpd.read_file(NDS_WFS_GML_URL, bbox=bbox, driver="GML")
        gdf = gdf.set_crs(epsg=25832, allow_override=True)
        logger.info(f"{len(gdf)} Bonitätsflächen empfangen.")

        match = gdf[gdf.contains(point)]
        if match.empty:
            raise ValueError("Kein Bodenschätzungswert an dieser Stelle verfügbar.")

        row = match.iloc[0]
        return {
            "bodenzahl": row.get("BODENZ", None),
            "ackerzahl": row.get("ACKERZ", None),
            "ertragsmesszahl": row.get("EMZ", None),
            "kulturart": row.get("KULTURART", None),
            "quelle": "LBeg Niedersachsen – WFS cls:L849 (GML)"
        }

    except Exception as e:
        logger.exception("Fehler beim Abruf der Bonitätsdaten.")
        raise RuntimeError(f"WFS-Zugriff oder Datenverarbeitung fehlgeschlagen: {str(e)}")
