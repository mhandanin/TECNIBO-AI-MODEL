"""Pydantic request/response models."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    largeur_mm: int = Field(gt=0, le=10000, description="Largeur de l'article, en mm")
    hauteur_mm: int = Field(gt=0, le=10000, description="Hauteur de l'article, en mm")
    materiau: str = Field(description="Nom du materiau, ex: Glass_Tempered_8 (voir GET /catalogue)")
    profile: str = Field(description="Nom du profile, ex: Aluminium_Thermal (voir GET /catalogue)")
    code_spp: str = Field(description="Code de finition/couleur (SPP)")
    complexity_factor: float = Field(gt=0, description="Facteur de complexite de fabrication")
    logistics_cost: float = Field(ge=0, description="Cout logistique estime, en EUR")


class PredictResponse(BaseModel):
    prix_predit: float
    id_entrainement: int
    nom_modele: str
    version: str
    latence_ms: float


class ModelInfoResponse(BaseModel):
    id_entrainement: int
    nom_modele: str
    version: str
    date_entrainement: datetime
    r2: Optional[float]
    mae: Optional[float]
    rmse: Optional[float]
    nb_echantillons: Optional[int]


class CatalogueResponse(BaseModel):
    materiaux: list[str]
    profiles: list[str]
