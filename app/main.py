from fastapi import FastAPI
from app.api import soil, climate, value, bonitaet

app = FastAPI()

app.include_router(soil.router)
app.include_router(climate.router)
app.include_router(value.router)
app.include_router(bonitaet.router)
