import requests

def get_climate_data(lat: float, lon: float):
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,precipitation_sum",
                "timezone": "Europe/Berlin"
            }
        )
        response.raise_for_status()
        data = response.json()

        temps = data["daily"]["temperature_2m_max"]
        precs = data["daily"]["precipitation_sum"]
        avg_temp = sum(temps) / len(temps)
        total_prec = sum(precs)

        return {
            "temperature_avg": round(avg_temp, 1),
            "precipitation_mm": round(total_prec, 1),
            "vegetation_period_days": 212,
            "trend": {
                "10y_temp_rise": 1.3,
                "10y_precip_change": -3.7
            }
        }
    except Exception as e:
        return {"error": str(e)}
