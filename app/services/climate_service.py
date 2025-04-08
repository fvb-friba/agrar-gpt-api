import requests
from pyproj import Transformer
from app.utils.logger import get_logger

logger = get_logger("climate")

def convert_epsg25832_to_wgs84(easting: float, northing: float) -> tuple:
    transformer = Transformer.from_crs("epsg:25832", "epsg:4326", always_xy=True)
    lon, lat = transformer.transform(easting, northing)
    return lat, lon

def fetch_climate_data(easting: float, northing: float, start_year: int, end_year: int) -> dict:
    lat, lon = convert_epsg25832_to_wgs84(easting, northing)
    logger.info(f"Abfrage für Koordinaten EPSG:25832 → WGS84 ({lat}, {lon})")

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": f"{start_year}-01-01",
        "end_date": f"{end_year}-12-31",
        "daily": ["temperature_2m_mean", "precipitation_sum"],
        "timezone": "Europe/Berlin"
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        temps = daily.get("temperature_2m_mean", [])
        precs = daily.get("precipitation_sum", [])

        # Daten pro Monat zusammenfassen
        monthly_data = {}
        for i, date in enumerate(dates):
            year, month, *_ = map(int, date.split("-"))
            key = (year, month)
            t = temps[i]
            p = precs[i]
            if key not in monthly_data:
                monthly_data[key] = {"t": [], "p": []}
            if t is not None:
                monthly_data[key]["t"].append(t)
            if p is not None:
                monthly_data[key]["p"].append(p)

        data_points = []
        for (y, m), vals in monthly_data.items():
            data_points.append({
                "year": y,
                "month": m,
                "temperature": sum(vals["t"]) / len(vals["t"]) if vals["t"] else None,
                "precipitation": sum(vals["p"]) if vals["p"] else None
            })

        t_all = [dp["temperature"] for dp in data_points if dp["temperature"] is not None]
        p_all = [dp["precipitation"] for dp in data_points if dp["precipitation"] is not None]

        return {
            "location": {"lat": lat, "lon": lon},
            "temperature_mean": round(sum(t_all) / len(t_all), 2) if t_all else None,
            "precipitation_mean": round(sum(p_all) / len(p_all), 2) if p_all else None,
            "data_points": data_points
        }

    except Exception as e:
        logger.error(f"Klimadaten konnten nicht abgerufen werden: {str(e)}")
        raise
