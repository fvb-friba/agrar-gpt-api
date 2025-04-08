# app/api/value.py

from fastapi import APIRouter, HTTPException, Query
from app.services.value_service import fetch_land_value_by_regionalkey

router = APIRouter()

@router.get("/value")
def get_land_value_data(
    regionalkey: str = Query(..., description="Dreistelliger Schlüssel des Regierungsbezirks (z. B. '051')"),
    start_year: int = Query(2013, ge=2000, le=2099),
    end_year: int = Query(2023, ge=2000, le=2099)
):
    """
    API-Endpunkt für landwirtschaftliche Kaufpreise auf Regierungsbezirksebene.
    """
    try:
        return fetch_land_value_by_regionalkey(regionalkey, start_year, end_year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
