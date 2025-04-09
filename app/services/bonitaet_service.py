
import geopandas as gpd
from shapely.geometry import Point
from pyproj import CRS, Transformer
from app.utils.logger import get_logger

logger = get_logger("bonitaet")

# WFS-Zugang zu Niedersachsen – Priorität 1
NDS_WFS_URL = (
    "https://www.geobasisdaten.niedersachsen.de/geobasisdaten"
    "/geodienste/afis_bodenschaetzung_wfs"
    "?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature"
    "&TYPENAMES=afis:BZB_Flaeche"
    "&outputFormat=application/json"
)

CRS_25832 = CRS.from_epsg(25832)
CRS_4326 = CRS.from_epsg(4326)
transformer = Transformer.from_crs(CRS_25832, CRS_4326, always_xy=True)

def fetch_bonitaet_data(easting: float, northing: float) -> dict:
    logger.info(f"Starte Bonitätsabfrage für Koordinate (E:{easting}, N:{northing})")

    # Umwandlung in WGS84 für WFS-Kompatibilität (falls nötig)
    lon, lat = transformer.transform(easting, northing)
    point = Point(easting, northing)
    logger.debug(f"Koordinatentransformation WGS84: ({lat}, {lon})")

    try:
        gdf = gpd.read_file(NDS_WFS_URL, bbox=(lon - 0.001, lat - 0.001, lon + 0.001, lat + 0.001))
        gdf = gdf.to_crs(epsg=25832)
        logger.info(f"{len(gdf)} Bonitätsflächen geladen.")

        match = gdf[gdf.contains(point)]
        if match.empty:
            raise ValueError("Kein Bodenschätzungswert an dieser Stelle verfügbar.")

        row = match.iloc[0]
        return {
            "bodenzahl": row.get("BODENZ", None),
            "ackerzahl": row.get("ACKERZ", None),
            "ertragsmesszahl": row.get("EMZ", None),
            "kulturart": row.get("KULTURART", None),
            "quelle": "BZB Niedersachsen WFS"
        }

    except Exception as e:
        logger.exception("Fehler beim Abruf der Bonitätsdaten.")
        raise RuntimeError(f"WFS-Zugriff oder Datenverarbeitung fehlgeschlagen: {str(e)}")
