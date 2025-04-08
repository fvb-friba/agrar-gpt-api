from fastapi import FastAPI
from soil import get_soil_data
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS aktivieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/soil")
def soil(lat: float, lon: float):
    return get_soil_data(lat, lon)
