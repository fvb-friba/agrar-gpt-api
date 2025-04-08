from pydantic import BaseModel, Field
from typing import List, Optional

class ClimateRequest(BaseModel):
    easting: float = Field(..., description="Ostwert in EPSG:25832")
    northing: float = Field(..., description="Nordwert in EPSG:25832")
    start_year: Optional[int] = Field(2013, description="Startjahr (z. B. 2013)")
    end_year: Optional[int] = Field(2023, description="Endjahr (z. B. 2023)")

class ClimateDataPoint(BaseModel):
    year: int
    month: int
    temperature: Optional[float]
    precipitation: Optional[float]

class ClimateResponse(BaseModel):
    location: dict
    temperature_mean: Optional[float]
    precipitation_mean: Optional[float]
    data_points: List[ClimateDataPoint]
