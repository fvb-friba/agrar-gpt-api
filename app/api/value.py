from fastapi import APIRouter, HTTPException
from app.models.value_models import ValueRequest, ValueResponse, ValueYearData
# NEU – keine Modell-Imports notwendig
from fastapi import APIRouter, HTTPException, Query
from app.services.value_service import fetch_land_value_by_regionalkey


router = APIRouter()

@router.post("/value", response_model=ValueResponse)
def get_value_data(request: ValueRequest):
    ags = request.regionalschluessel

    if not ags:
        if request.easting is None or request.northing is None:
            raise HTTPException(status_code=400, detail="Easting/Northing oder Regionalschlüssel erforderlich.")
        ags = resolve_ags_from_coords(request.easting, request.northing)
        if not ags:
            raise HTTPException(status_code=404, detail="Kein Regionalschlüssel ermittelbar.")

    try:
        result = fetch_value_data(ags)
        result["years"] = [ValueYearData(**entry) for entry in result["years"]]
        return ValueResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
