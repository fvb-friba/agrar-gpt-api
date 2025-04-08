from pydantic import BaseModel, Field

class SoilRequest(BaseModel):
    easting: float = Field(..., description="Ostwert in EPSG:25832 (Meter)")
    northing: float = Field(..., description="Nordwert in EPSG:25832 (Meter)")

class SoilResponse(BaseModel):
    legende: str
    legendentext: str
    profil_url: str
    raw_response: str
