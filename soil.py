import requests
from fastapi import HTTPException
from pyproj import Transformer
from xml.etree import ElementTree

def get_soil_data(lat: float, lon: float):
    # Umwandlung WGS84 → ETRS89 / UTM32 (EPSG:25832)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:25832", always_xy=True)
    x, y = transformer.transform(lon, lat)

    bbox_size = 25  # 25m Suchradius
    minx, miny = x - bbox_size, y - bbox_size
    maxx, maxy = x + bbox_size, y + bbox_size

    url = "https://sg.geodatenzentrum.de/wfs_inspire_boden"
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeNames": "de.bgr.boden.bodeneinheit",
        "srsName": "EPSG:25832",
        "bbox": f"{minx},{miny},{maxx},{maxy},EPSG:25832"
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()

        root = ElementTree.fromstring(r.content)
        ns = {"gml": "http://www.opengis.net/gml/3.2"}
        feature_members = root.findall(".//gml:featureMember", ns)

        if not feature_members:
            return {
                "soil_unit": None,
                "parent_material": None,
                "land_use": None,
                "quelle": "INSPIRE Soil WFS (keine Daten verfügbar)"
            }

        # Einfachste Extraktion: Beschreibung als Text
        description = feature_members[0].find(".//{*}beschreibung")
        material = feature_members[0].find(".//{*}ausgangsmaterial")
        landuse = feature_members[0].find(".//{*}nutzung")

        return {
            "soil_unit": description.text if description is not None else None,
            "parent_material": material.text if material is not None else None,
            "land_use": landuse.text if landuse is not None else None,
            "quelle": "INSPIRE Soil WFS"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
