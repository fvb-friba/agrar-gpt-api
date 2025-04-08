from fastapi import HTTPException

def get_soil_data(lat: float, lon: float):
    try:
        if 53 <= lat <= 54 and 9 <= lon <= 10:
            return {
                "bodenart": "Lehmiger Sand",
                "ackerzahl": 42,
                "gruenlandzahl": 34,
                "bonitaetsklasse": "mittel",
                "bodenpunkte": 55
            }
        else:
            return {
                "bodenart": "Schluff",
                "ackerzahl": 67,
                "gruenlandzahl": 58,
                "bonitaetsklasse": "gut",
                "bodenpunkte": 72
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
