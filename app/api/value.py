from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from app.services.value_service import fetch_land_value_by_regionalkey

router = APIRouter()

@router.get("/value")
def get_land_value(
    regionalkey: str = Query(..., min_length=3, max_length=3, description="3-stelliger Regionalschlüssel laut Destatis"),
    start_year: int = Query(None, description="Startjahr (optional, Standard: aktuelles Jahr - 10)"),
    end_year: int = Query(None, description="Endjahr (optional, Standard: aktuelles Jahr)")
):
    """
    Liefert die durchschnittlichen Kaufwerte landwirtschaftlicher Flächen
    für einen Regierungsbezirk anhand des Regionalschlüssels.
    """

    try:
        current_year = datetime.now().year
        start = start_year if start_year else current_year - 10
        end = end_year if end_year else current_year

        return fetch_land_value_by_regionalkey(regionalkey, start, end)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
