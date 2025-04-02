from fastapi import FastAPI
from climate import get_climate_data

app = FastAPI()

@app.get("/climate")
def climate(lat: float, lon: float):
    return get_climate_data(lat, lon)
