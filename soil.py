import requests
from fastapi import HTTPException
from pyproj import Transformer
from bs4 import BeautifulSoup

def get_soil_data(lat: float, lon: float):
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:25832", always_xy=True)
    x, y = transformer.transform(lon, lat)

    base_url = "https://services.bgr.de/wms/boden/buek200/"
    layer_name = "buek200"
    width = height = 256
    i = j = 128
    info_format = "text/html"

    for bbox_halfsize in [12.5, 25, 50, 100, 200]:
        minx, miny = x - bbox_halfsize, y - bbox_halfsize
        maxx, maxy = x + bbox_halfsize, y + bbox_halfsize

        params = {
            "SERVICE": "WMS",
            "VERSION": "1.3.0",
            "REQUEST": "GetFeatureInfo",
            "CRS": "EPSG:25832",
            "BBOX": f"{minx},{miny},{maxx},{maxy}",
            "WIDTH": str(width),
            "HEIGHT": str(height),
            "I": str(i),
            "J": str(j),
            "LAYERS": layer_name,
            "QUERY_LAYERS": layer_name,
            "INFO_FORMAT": info_format
        }

        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.find_all("tr")
            output = {}
            for row in rows:
                cols = row.find_all("td")
                if len(cols) == 2:
                    key = cols[0].text.strip()
                    value = cols[1].text.strip()
                    output[key] = value
            if output:
                output["quelle"] = f"BGR WMS ({bbox_halfsize} m Radius)"
                return output

        except requests.exceptions.RequestException:
            continue

    raise HTTPException(status_code=404, detail="Keine Bodendaten an dieser Position gefunden.")
