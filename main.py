from fastapi import FastAPI
from climate import get_climate_data
from value import get_land_value

app = FastAPI()

@app.get("/climate")
def climate(lat: float, lon: float):
    return get_climate_data(lat, lon)

@app.get("/value")
def value(landkreis: str):
    return get_land_value(landkreis)
