from fastapi import APIRouter, HTTPException
from app.models.climate_models import ClimateRequest, ClimateResponse, ClimateDataPoint
from app.services.climate_service import fetch_climate_data

router = APIRouter()

@router.post("/climate", response_model=ClimateResponse)
def get_climate(request: ClimateRequest):
    try:
        result = fetch_climate_data(
            easting=request.easting,
            northing=request.northing,
            start_year=request.start_year,
            end_year=request.end_year
        )
        result["data_points"] = [ClimateDataPoint(**dp) for dp in result["data_points"]]
        return ClimateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
