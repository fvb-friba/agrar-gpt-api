from pydantic import BaseModel, Field
from typing import List, Optional

class ValueRequest(BaseModel):
    regionalschluessel: Optional[str] = Field(None, description="AGS-Regionalschlüssel (z. B. 05315 für Duisburg)")
    easting: Optional[float] = Field(None, description="Easting in EPSG:25832")
    northing: Optional[float] = Field(None, description="Northing in EPSG:25832")

class ValueYearData(BaseModel):
    year: int
    avg_price_eur_per_ha: float
    num_cases: Optional[int]

class ValueResponse(BaseModel):
    region: str
    ags: str
    unit: str
    years: List[ValueYearData]
