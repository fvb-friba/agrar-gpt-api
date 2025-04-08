from fastapi import FastAPI
from app.api import soil, climate

app = FastAPI()

app.include_router(soil.router)
app.include_router(climate.router)
