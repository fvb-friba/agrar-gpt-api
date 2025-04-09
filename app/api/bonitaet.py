# Datei: app/api/bonitaet.py

from fastapi import APIRouter, HTTPException
from app.models.bonitaet_models import BonitaetRequest, BonitaetResponse
from app.services.bonitaet_service import fetch_bonitaet_data

router = APIRouter()

@router.post("/bonitaet", response_model=BonitaetResponse)
def get_bonitaet(request: BonitaetRequest):
    try:
        return fetch_bonitaet_data(request.easting, request.northing, request.radius)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
