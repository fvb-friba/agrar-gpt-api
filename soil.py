import requests
import geopandas as gpd
from fastapi import HTTPException
from pyproj import Transformer
from shapely.geometry import Point
from zipfile import ZipFile
from io import BytesIO
import os

SHAPEFILE_URL = "https://download.bgr.de/bgr/Boden/BUEK3000/shp/buek3000_v21.zip"
SHAPEFILE_DIR = "buek3000_shapefile"

def download_and_extract_shapefile():
    if not os.path.exists(SHAPEFILE_DIR):
        print("🔽 Lade BÜK3000 Shapefile...")
        r = requests.get(SHAPEFILE_URL)
        r.raise_for_status()
        with ZipFile(BytesIO(r.content)) as zip_ref:
            zip_ref.extractall(SHAPEFILE_DIR)
        print("✅ Shapefile entpackt.")

def get_soil_data(lat: float, lon: float):
    download_and_extract_shapefile()

    shp_path = None
    for file in os.listdir(SHAPEFILE_DIR):
        if file.endswith(".shp"):
            shp_path = os.path.join(SHAPEFILE_DIR, file)
            break
    if not shp_path:
        raise HTTPException(status_code=500, detail="Shapefile nicht gefunden.")

    gdf = gpd.read_file(shp_path)
    transformer = Transformer.from_crs("EPSG:4326", gdf.crs.to_string(), always_xy=True)
    x, y = transformer.transform(lon, lat)
    point = Point(x, y)

    match = gdf[gdf.geometry.contains(point)]
    if match.empty:
        return {"detail": "Keine Bodendaten für diese Koordinate gefunden."}

    row = match.iloc[0]
    return {
        "bodenname": row.get("BODENNAME", None),
        "beschreibung": row.get("BESCHREIBU", None),
        "leitboden": row.get("LEITBODEN", None),
        "begleitbo": row.get("BEGLEITBO", None),
        "ausgangsmaterial": row.get("AUSGANGSMA", None),
        "quelle": "BÜK3000 (Shapefile BGR)"
    }
