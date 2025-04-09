# Datei: app/models/bonitaet_models.py

from pydantic import BaseModel
from typing import Optional, List


class BonitaetRequest(BaseModel):
    easting: float
    northing: float
    radius: Optional[float] = 50  # optionaler Suchpuffer, default bleibt wie bisher


class BonitaetFeature(BaseModel):
    bodenzahl: Optional[int]
    ackerzahl: Optional[int]
    kulturart: Optional[str]
    area_qm: Optional[float]
    update: Optional[str]
    quelle: str


class BonitaetResponse(BaseModel):
    bonitaet: List[BonitaetFeature]
