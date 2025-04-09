
import geopandas as gpd
from urllib.parse import urlencode

def fetch_bonitaet_data(bbox: tuple) -> gpd.GeoDataFrame:
    base_url = "https://nibis.lbeg.de/net3/public/ogcsl.ashx"

    # Beispielhafte Layerauswahl – in der Praxis dynamisch bestimmbar
    layer_name = "cls:L849"

    # Umrechnung der Bounding Box in String
    bbox_str = ",".join(map(str, bbox))

    # Korrekte URL-Parameter
    params = {
        "SERVICE": "WFS",
        "VERSION": "2.0.0",
        "REQUEST": "GetFeature",
        "TYPENAMES": layer_name,
        "SRSNAME": "EPSG:25832",
        "outputFormat": "text/xml;subtype=gml/3.2",  # ✅ Wichtig: kein Leerzeichen!
        "BBOX": f"{bbox_str},EPSG:25832"
    }

    # URL bauen
    url = f"{base_url}?{urlencode(params)}"

    # Laden der Daten
    gdf = gpd.read_file(url)

    return gdf
