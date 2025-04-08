from fastapi import FastAPI
from app.api import soil

app = FastAPI()
app.include_router(soil.router)
