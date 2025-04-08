import requests
from datetime import date, timedelta

def get_climate_data(lat: float, lon: float):
    try:
        # === 7-Tage-Vorhersage ===
        start = date.today()
        end = start + timedelta(days=6)

        forecast_response = requests.get(
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
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()["daily"]

        def avg(values): return sum(values) / len(values)

        temperature_avg = round(avg(forecast_data["temperature_2m_max"]), 1)
        temperature_min = round(min(forecast_data["temperature_2m_min"]), 1)
        temperature_max = round(max(forecast_data["temperature_2m_max"]), 1)
        precipitation_mm = round(sum(forecast_data["precipitation_sum"]), 1)
        wind_speed_max = round(max(forecast_data["wind_speed_10m_max"]), 1)
        sunshine_hours = round(sum(forecast_data["sunshine_duration"]) / 60, 1)

        # === Trenddaten + Vegetationsperiode (Reanalysis) ===
        archive_response = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude": lat,
                "longitude": lon,
                "start_date": "2014-01-01",
                "end_date": "2023-12-31",
                "daily": "temperature_2m_max,precipitation_sum,temperature_2m_mean",
                "timezone": "Europe/Berlin"
            }
        )
        archive_response.raise_for_status()
        archive_data = archive_response.json()["daily"]

        # Trenddaten (wie bisher)
        years = [int(d.split("-")[0]) for d in archive_data["time"]]
        year_data = {}
        for i, year in enumerate(years):
            if year not in year_data:
                year_data[year] = {"temps": [], "precs": []}
            year_data[year]["temps"].append(archive_data["temperature_2m_max"][i])
            year_data[year]["precs"].append(archive_data["precipitation_sum"][i])

        year_avgs = {}
        for y, vals in year_data.items():
            year_avgs[y] = {
                "temp": sum(vals["temps"]) / len(vals["temps"]),
                "prec": sum(vals["precs"])
            }

        years_sorted = sorted(year_avgs.keys())
        temp_trend = year_avgs[years_sorted[-1]]["temp"] - year_avgs[years_sorted[0]]["temp"]
        prec_trend = ((year_avgs[years_sorted[-1]]["prec"] / year_avgs[years_sorted[0]]["prec"]) - 1) * 100

        # Vegetationsperiode (2023)
        veg_start = None
        veg_end = None
        mean_temps = [
            (i, t) for i, (d, t) in enumerate(zip(archive_data["time"], archive_data["temperature_2m_mean"]))
            if d.startswith("2023")
        ]
        for i in range(len(mean_temps) - 5):
            # Start: 5 aufeinanderfolgende Tage mit ≥ 5 °C
            if all(mean_temps[j][1] >= 5 for j in range(i, i + 5)):
                veg_start = i
                break
        for i in range(len(mean_temps) - 1, 4, -1):
            if all(mean_temps[j][1] < 5 for j in range(i - 4, i + 1)):
                veg_end = i
                break
        if veg_start is not None and veg_end is not None and veg_end > veg_start:
            vegetation_days = veg_end - veg_start
        else:
            vegetation_days = 205  # fallback

        return {
            "temperature_avg": temperature_avg,
            "temperature_min": temperature_min,
            "temperature_max": temperature_max,
            "precipitation_mm": precipitation_mm,
            "wind_speed_max": wind_speed_max,
            "sunshine_hours": sunshine_hours,
            "vegetation_days_estimate": vegetation_days,
            "trend": {
                "10y_temp_rise": round(temp_trend, 2),
                "10y_precip_change": round(prec_trend, 1)
            }
        }

    except Exception as e:
        return {"error": str(e)}
