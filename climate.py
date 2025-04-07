import requests
from datetime import date, timedelta

def get_climate_data(lat: float, lon: float):
    try:
        start = date.today()
        end = start + timedelta(days=6)

        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": ",".join([
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "wind_speed_10m_max",
                    "sunshine_duration"
                ]),
                "timezone": "Europe/Berlin",
                "start_date": start.isoformat(),
                "end_date": end.isoformat()
            }
        )
        response.raise_for_status()
        data = response.json()["daily"]

        def avg(values): return sum(values) / len(values)

        return {
            "temperature_avg": round(avg(data["temperature_2m_max"]), 1),
            "temperature_min": round(min(data["temperature_2m_min"]), 1),
            "temperature_max": round(max(data["temperature_2m_max"]), 1),
            "precipitation_mm": round(sum(data["precipitation_sum"]), 1),
            "wind_speed_max": round(max(data["wind_speed_10m_max"]), 1),
            "sunshine_hours": round(sum(data["sunshine_duration"]) / 60, 1),  # Minuten → Stunden
            "vegetation_days_estimate": 205,
            "trend": {
                "10y_temp_rise": 1.3,
                "10y_precip_change": -3.7
            }
        }

    except Exception as e:
        return {"error": str(e)}
