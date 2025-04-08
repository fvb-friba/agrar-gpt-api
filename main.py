from fastapi import FastAPI
from soil import get_soil_data

app = FastAPI()

@app.get("/soil")
def soil(lat: float, lon: float):
    return get_soil_data(lat, lon)
