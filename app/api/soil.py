from fastapi import APIRouter, HTTPException
from app.models.soil_models import SoilRequest, SoilResponse
from app.services.soil_service import fetch_soil_info

router = APIRouter()

@router.post("/soil", response_model=SoilResponse)
def get_soil_data(request: SoilRequest):
    try:
        result = fetch_soil_info(request.easting, request.northing)
        return SoilResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
