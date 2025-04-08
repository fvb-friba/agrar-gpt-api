from pydantic import BaseModel, Field

class SoilRequest(BaseModel):
    easting: float = Field(..., description="Ostwert in EPSG:25832 (Meter)")
    northing: float = Field(..., description="Nordwert in EPSG:25832 (Meter)")

class SoilResponse(BaseModel):
    bkz: str
    bez: str
    raw_response: str
