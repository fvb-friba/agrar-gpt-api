def get_climate_data(lat: float, lon: float):
    # Beispielhafte, statisch simulierte DWD-Daten
    return {
        "temperature_avg": 9.3,
        "precipitation_mm": 735,
        "vegetation_period_days": 212,
        "trend": {
            "10y_temp_rise": 1.4,
            "10y_precip_change": -3.2
        }
    }
