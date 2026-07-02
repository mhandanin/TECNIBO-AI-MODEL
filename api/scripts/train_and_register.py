#!/usr/bin/env python3
"""Trains the retained model (Ridge, cf. reports/phase1_analysis.md) on the
training data stored in PostgreSQL, evaluates it on a held-out test set,
saves the artifact to api/model_artifacts/ and registers the run in
modele_entrainement.

The evaluation metrics (r2/mae/rmse) come from a model fit on the train
split only (honest, leakage-free estimate). The artifact actually shipped
is then refit on 100% of the available data, for best production accuracy
-- same rationale as the original discover_formula_v2.py script.

Usage:
    python train_and_register.py
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from pricing_ml.config import FEATURE_COLUMNS, RANDOM_STATE, TARGET_COLUMN
from pricing_ml.features import SppEncoder, engineer_features
from pricing_ml.models import get_models
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split
from sqlalchemy import text

from pricing_api.config import DATABASE_URL, MODEL_ARTIFACTS_DIR
from pricing_api.db import engine

MODEL_NAME = "Ridge"


def load_training_data() -> pd.DataFrame:
    query = text(
        """
        SELECT
            a.largeur_mm     AS "Width_mm",
            a.hauteur_mm     AS "Height_mm",
            a.surface_m2     AS "Surface_m2",
            a.code_spp       AS "SPP",
            a.complexity_factor AS "Complexity_factor",
            a.logistics_cost AS "Logistics_cost",
            a.prix_reel      AS "Article_price",
            m.prix_m2        AS "Material_price_m2",
            p.prix_unitaire  AS "Profile_price_unit"
        FROM article a
        JOIN materiau m ON m.id_materiau = a.id_materiau
        JOIN profile p ON p.id_profile = a.id_profile
        """
    )
    with engine.begin() as conn:
        df = pd.read_sql(query, conn)
    return df


def evaluate_on_holdout(df: pd.DataFrame) -> dict:
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=RANDOM_STATE)

    encoder = SppEncoder().fit(train_df["SPP"], train_df[TARGET_COLUMN])
    train_df = train_df.copy()
    test_df = test_df.copy()
    train_df["SPP_price"] = encoder.transform(train_df["SPP"])
    test_df["SPP_price"] = encoder.transform(test_df["SPP"])

    model = get_models()[MODEL_NAME]
    model.fit(train_df[FEATURE_COLUMNS], train_df[TARGET_COLUMN])
    y_pred = model.predict(test_df[FEATURE_COLUMNS])

    return {
        "r2": r2_score(test_df[TARGET_COLUMN], y_pred),
        "mae": mean_absolute_error(test_df[TARGET_COLUMN], y_pred),
        "rmse": root_mean_squared_error(test_df[TARGET_COLUMN], y_pred),
    }


def fit_production_artifact(df: pd.DataFrame):
    encoder = SppEncoder().fit(df["SPP"], df[TARGET_COLUMN])
    df = df.copy()
    df["SPP_price"] = encoder.transform(df["SPP"])

    pipeline = get_models()[MODEL_NAME]
    pipeline.fit(df[FEATURE_COLUMNS], df[TARGET_COLUMN])
    return pipeline, encoder


def register_run(version: str, artifact_path: Path, metrics: dict, nb_echantillons: int) -> int:
    with engine.begin() as conn:
        row = conn.execute(
            text(
                """
                INSERT INTO modele_entrainement (
                    nom_modele, version, hyperparametres, r2, mae, rmse,
                    nb_echantillons, chemin_artifact
                ) VALUES (
                    :nom_modele, :version, :hyperparametres, :r2, :mae, :rmse,
                    :nb_echantillons, :chemin_artifact
                )
                RETURNING id_entrainement
                """
            ),
            {
                "nom_modele": MODEL_NAME,
                "version": version,
                "hyperparametres": json.dumps({"alpha": 1.0, "standardize": True}),
                "r2": metrics["r2"],
                "mae": metrics["mae"],
                "rmse": metrics["rmse"],
                "nb_echantillons": nb_echantillons,
                "chemin_artifact": str(artifact_path),
            },
        )
        return row.scalar_one()


def main() -> None:
    print(f"Connecting to {DATABASE_URL.split('@')[-1]}")
    df = load_training_data()
    df = engineer_features(df)
    print(f"Loaded {len(df)} rows from article/materiau/profile")

    metrics = evaluate_on_holdout(df)
    print(f"Holdout metrics: R2={metrics['r2']:.4f}  MAE={metrics['mae']:.2f}  RMSE={metrics['rmse']:.2f}")

    pipeline, encoder = fit_production_artifact(df)

    MODEL_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    version = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    artifact_path = MODEL_ARTIFACTS_DIR / f"ridge_v{version}.joblib"
    joblib.dump(
        {"pipeline": pipeline, "spp_encoder": encoder, "feature_columns": FEATURE_COLUMNS},
        artifact_path,
    )
    print(f"Saved artifact: {artifact_path}")

    id_entrainement = register_run(version, artifact_path, metrics, len(df))
    print(f"Registered modele_entrainement id={id_entrainement} version={version}")


if __name__ == "__main__":
    main()
