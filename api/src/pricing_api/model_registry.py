"""Loads the currently active trained model (latest row in modele_entrainement).

The DB row is fetched on every call (cheap) so a new training run becomes
active immediately; the (larger) joblib artifact itself is cached in memory
per artifact path to avoid re-deserializing it on every request.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import joblib

from .db import get_latest_model_run


@dataclass
class ActiveModel:
    id_entrainement: int
    nom_modele: str
    version: str
    date_entrainement: Any
    r2: float | None
    mae: float | None
    rmse: float | None
    nb_echantillons: int | None
    pipeline: Any
    spp_encoder: Any
    feature_columns: list[str]


@lru_cache(maxsize=4)
def _load_artifact(chemin_artifact: str) -> dict:
    return joblib.load(chemin_artifact)


def load_active_model() -> ActiveModel:
    row = get_latest_model_run()
    if row is None:
        raise RuntimeError(
            "Aucun modele enregistre dans modele_entrainement. "
            "Lancer api/scripts/train_and_register.py d'abord."
        )
    artifact = _load_artifact(row["chemin_artifact"])
    return ActiveModel(
        id_entrainement=row["id_entrainement"],
        nom_modele=row["nom_modele"],
        version=row["version"],
        date_entrainement=row["date_entrainement"],
        r2=row["r2"],
        mae=row["mae"],
        rmse=row["rmse"],
        nb_echantillons=row["nb_echantillons"],
        pipeline=artifact["pipeline"],
        spp_encoder=artifact["spp_encoder"],
        feature_columns=artifact["feature_columns"],
    )
