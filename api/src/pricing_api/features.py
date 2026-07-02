"""Builds the model feature vector for a single prediction request.

Reuses pricing_ml.features.engineer_features so the API computes the exact
same formulas (material_cost, profile_cost, Perimeter_m, ...) as the
training pipeline, instead of duplicating them.
"""
from __future__ import annotations

import pandas as pd
from pricing_ml.config import FEATURE_COLUMNS
from pricing_ml.features import engineer_features


def build_feature_row(
    largeur_mm: int,
    hauteur_mm: int,
    materiau_prix_m2: float,
    profile_prix_unitaire: float,
    code_spp: str,
    complexity_factor: float,
    logistics_cost: float,
    spp_encoder,
) -> pd.DataFrame:
    surface_m2 = (largeur_mm / 1000.0) * (hauteur_mm / 1000.0)

    raw = pd.DataFrame(
        [
            {
                "Width_mm": largeur_mm,
                "Height_mm": hauteur_mm,
                "Surface_m2": surface_m2,
                "Material_price_m2": materiau_prix_m2,
                "Profile_price_unit": profile_prix_unitaire,
                "Complexity_factor": complexity_factor,
                "Logistics_cost": logistics_cost,
            }
        ]
    )
    engineered = engineer_features(raw)
    engineered["SPP_price"] = spp_encoder.transform(pd.Series([code_spp]))
    return engineered[FEATURE_COLUMNS]
