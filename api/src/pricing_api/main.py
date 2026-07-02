"""FastAPI application exposing the industrial article pricing model."""
from __future__ import annotations

import time

from fastapi import Depends, FastAPI, HTTPException

from . import db
from .features import build_feature_row
from .model_registry import load_active_model
from .schemas import CatalogueResponse, ModelInfoResponse, PredictRequest, PredictResponse
from .security import require_api_key

app = FastAPI(
    title="Industrial Pricing API",
    description=(
        "API REST exposant le modele de prediction du prix d'un article "
        "industriel sur-mesure (projet de certification RNCP37827). "
        "L'endpoint /predict necessite une cle API (header X-API-Key)."
    ),
    version="0.1.0",
)


@app.get("/health", tags=["monitoring"])
def health() -> dict:
    return {"status": "ok"}


@app.get("/model/info", response_model=ModelInfoResponse, tags=["model"])
def model_info() -> ModelInfoResponse:
    model = load_active_model()
    return ModelInfoResponse(
        id_entrainement=model.id_entrainement,
        nom_modele=model.nom_modele,
        version=model.version,
        date_entrainement=model.date_entrainement,
        r2=model.r2,
        mae=model.mae,
        rmse=model.rmse,
        nb_echantillons=model.nb_echantillons,
    )


@app.get("/catalogue", response_model=CatalogueResponse, tags=["model"])
def catalogue() -> CatalogueResponse:
    return CatalogueResponse(materiaux=db.list_materiaux(), profiles=db.list_profiles())


@app.post("/predict", response_model=PredictResponse, tags=["prediction"])
def predict(payload: PredictRequest, api_key: str = Depends(require_api_key)) -> PredictResponse:
    start = time.perf_counter()

    model = load_active_model()

    materiau_prix_m2 = db.lookup_materiau_price(payload.materiau)
    if materiau_prix_m2 is None:
        raise HTTPException(status_code=404, detail=f"Materiau inconnu: {payload.materiau!r}")

    profile_prix_unitaire = db.lookup_profile_price(payload.profile)
    if profile_prix_unitaire is None:
        raise HTTPException(status_code=404, detail=f"Profile inconnu: {payload.profile!r}")

    surface_m2 = (payload.largeur_mm / 1000.0) * (payload.hauteur_mm / 1000.0)
    X = build_feature_row(
        largeur_mm=payload.largeur_mm,
        hauteur_mm=payload.hauteur_mm,
        materiau_prix_m2=materiau_prix_m2,
        profile_prix_unitaire=profile_prix_unitaire,
        code_spp=payload.code_spp,
        complexity_factor=payload.complexity_factor,
        logistics_cost=payload.logistics_cost,
        spp_encoder=model.spp_encoder,
    )
    prix_predit = float(model.pipeline.predict(X)[0])

    latence_ms = (time.perf_counter() - start) * 1000

    db.insert_prediction(
        id_entrainement=model.id_entrainement,
        largeur_mm=payload.largeur_mm,
        hauteur_mm=payload.hauteur_mm,
        surface_m2=surface_m2,
        materiau_prix_m2=materiau_prix_m2,
        profile_prix_unitaire=profile_prix_unitaire,
        code_spp=payload.code_spp,
        complexity_factor=payload.complexity_factor,
        logistics_cost=payload.logistics_cost,
        prix_predit=prix_predit,
        latence_ms=latence_ms,
    )

    return PredictResponse(
        prix_predit=round(prix_predit, 2),
        id_entrainement=model.id_entrainement,
        nom_modele=model.nom_modele,
        version=model.version,
        latence_ms=round(latence_ms, 2),
    )
