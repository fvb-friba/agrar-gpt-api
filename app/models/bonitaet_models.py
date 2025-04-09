
from pydantic import BaseModel
from typing import Optional

class BonitaetRequest(BaseModel):
    easting: float
    northing: float

class BonitaetResponse(BaseModel):
    bodenzahl: Optional[float]
    ackerzahl: Optional[float]
    ertragsmesszahl: Optional[float]
    kulturart: Optional[str]
    quelle: str
