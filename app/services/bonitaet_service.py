
import fiona
import geopandas as gpd
from shapely.geometry import Point, shape
from pyproj import CRS
from app.utils.logger import get_logger

logger = get_logger("bonitaet")

# URL mit korrekt kodiertem GML-Ausgabeformat
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
        buffer = 100
        bbox = (easting - buffer, northing - buffer, easting + buffer, northing + buffer)
        bbox_str = ",".join(map(str, bbox))
        query_url = NDS_WFS_GML_URL + f"&BBOX={bbox_str},EPSG:25832"

        # Direkter Zugriff via Fiona (nicht pyogrio)
        with fiona.open(query_url, driver="GML") as src:
            features = [f for f in src]

        if not features:
            raise ValueError("Keine Bonitätsfläche im Zielbereich gefunden.")

        gdf = gpd.GeoDataFrame.from_features(features, crs=25832)
        match = gdf[gdf.contains(point)]

        if match.empty:
            raise ValueError("Punkt liegt außerhalb aller Bonitätsflächen.")

        row = match.iloc[0]
        return {
            "bodenzahl": row.get("BODENZ", None),
            "ackerzahl": row.get("ACKERZ", None),
            "ertragsmesszahl": row.get("EMZ", None),
            "kulturart": row.get("KULTURART", None),
            "quelle": "LBeg Niedersachsen – WFS cls:L849 (Fiona-GML)"
        }

    except Exception as e:
        logger.exception("Fehler beim Abruf der Bonitätsdaten.")
        raise RuntimeError(f"WFS-Zugriff oder Datenverarbeitung fehlgeschlagen: {str(e)}")
