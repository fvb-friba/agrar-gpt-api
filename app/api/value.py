from fastapi import APIRouter, HTTPException, Query
from app.services.value_service import fetch_land_value_by_regionalkey

router = APIRouter()

@router.get("/value")
def get_land_value(regionalkey: str = Query(..., min_length=3, max_length=3, description="3-stelliger Regionalschlüssel laut Destatis")):
    """
    Liefert die durchschnittlichen Kaufwerte landwirtschaftlicher Flächen
    basierend auf dem 3-stelligen Regionalschlüssel (Regierungsbezirk).
    """
    try:
        return fetch_land_value_by_regionalkey(regionalkey)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
