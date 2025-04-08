import uvicorn
from fastapi import FastAPI
from climate import get_climate_data
from value import get_value_data
from soil import get_soil_data

app = FastAPI()

@app.get("/climate")
def climate(lat: float, lon: float):
    return get_climate_data(lat, lon)

@app.get("/value")
def value(blid: str):
    return get_value_data(blid)

@app.get("/soil")
def soil(lat: float, lon: float):
    return get_soil_data(lat, lon)
