"""Shared pytest fixtures for the pricing_api test suite.

`pricing_api.config` reads DATABASE_URL/API_KEY from the environment (and
`pricing_api.db` opens a SQLAlchemy engine against it) the moment either
module is first imported anywhere in the session. So the environment is
pointed at a disposable "<db>_test" database *before* any `pricing_api`
import happens below -- this way the integration tests (which TRUNCATE
tables) can never touch real local/dev data, and both local runs (reusing
the docker-compose Postgres credentials) and CI (a fresh service container)
go through the same code path.

Creating/engine (SQLAlchemy `create_engine`) is lazy, so importing
`pricing_api.db` here is safe even with no Postgres reachable at all --
only fixtures that actually `.connect()` (used exclusively by the
`integration`-marked tests) require a live database. Pure unit tests never
pull those fixtures in.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_env_file_values = dotenv_values(PROJECT_ROOT / ".env")
_dev_database_url = (
    os.environ.get("DATABASE_URL")
    or _env_file_values.get("DATABASE_URL")
    or "postgresql://pricing_user:change_me_local_dev@localhost:5433/pricing_db"
)


def _with_db_name(url: str, db_name: str) -> str:
    parts = urlsplit(url)
    return urlunsplit(parts._replace(path=f"/{db_name}"))


_TEST_DB_NAME = urlsplit(_dev_database_url).path.lstrip("/") + "_test"
TEST_DATABASE_URL = _with_db_name(_dev_database_url, _TEST_DB_NAME)

# Must happen before any `pricing_api` import below (or in test modules).
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("API_KEY", "test-api-key")

import joblib  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402

from pricing_api.db import engine as api_engine  # noqa: E402
from pricing_api.main import app  # noqa: E402


def _ensure_test_database_exists() -> None:
    admin_engine = create_engine(_with_db_name(_dev_database_url, "postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": _TEST_DB_NAME}
        ).first()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{_TEST_DB_NAME}"'))
    admin_engine.dispose()


def _reset_schema() -> None:
    schema_sql = (PROJECT_ROOT / "db" / "sql" / "001_init_schema.sql").read_text(encoding="utf-8")
    with api_engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        for statement in schema_sql.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))


@pytest.fixture(scope="session")
def test_db_engine():
    _ensure_test_database_exists()
    _reset_schema()
    return api_engine


@pytest.fixture
def seed_catalogue(test_db_engine):
    with test_db_engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE prediction, modele_entrainement, article, materiau, profile "
                "RESTART IDENTITY CASCADE"
            )
        )
        conn.execute(
            text("INSERT INTO materiau (nom, prix_m2) VALUES (:nom, :prix)"),
            {"nom": "Glass_Tempered_8", "prix": 55.0},
        )
        conn.execute(
            text("INSERT INTO profile (nom, prix_unitaire) VALUES (:nom, :prix)"),
            {"nom": "Aluminium_Thermal", "prix": 12.5},
        )
    return {"materiau": ("Glass_Tempered_8", 55.0), "profile": ("Aluminium_Thermal", 12.5)}


@pytest.fixture
def trained_model(test_db_engine, seed_catalogue, tmp_path):
    from pricing_ml.config import FEATURE_COLUMNS
    from pricing_ml.features import SppEncoder, engineer_features
    from pricing_ml.models import get_models

    raw = pd.DataFrame(
        {
            "Width_mm": [1000, 1200, 1500, 900, 2000, 1100],
            "Height_mm": [1000, 1300, 1400, 950, 1800, 1050],
            "Surface_m2": [1.0, 1.56, 2.1, 0.855, 3.6, 1.155],
            "Material_price_m2": [50.0, 55.0, 60.0, 48.0, 70.0, 52.0],
            "Profile_price_unit": [10.0, 11.0, 12.0, 9.5, 15.0, 10.5],
            "Complexity_factor": [1.0, 1.1, 1.05, 0.95, 1.2, 1.0],
            "Logistics_cost": [5.0, 6.0, 7.0, 4.5, 9.0, 5.5],
        }
    )
    target = pd.Series([180.0, 210.0, 260.0, 150.0, 340.0, 190.0])
    spp = pd.Series(["8906", "8906", "1200", "1200", "8906", "1200"])

    engineered = engineer_features(raw)
    encoder = SppEncoder().fit(spp, target)
    engineered["SPP_price"] = encoder.transform(spp)

    pipeline = get_models()["Ridge"]
    pipeline.fit(engineered[FEATURE_COLUMNS], target)

    artifact_path = tmp_path / "ridge_test.joblib"
    joblib.dump(
        {"pipeline": pipeline, "spp_encoder": encoder, "feature_columns": FEATURE_COLUMNS},
        artifact_path,
    )

    with test_db_engine.begin() as conn:
        row = conn.execute(
            text(
                """
                INSERT INTO modele_entrainement (
                    nom_modele, version, hyperparametres, r2, mae, rmse,
                    nb_echantillons, chemin_artifact
                ) VALUES (
                    :nom_modele, :version, :hyperparametres, :r2, :mae, :rmse, :nb, :chemin
                )
                RETURNING id_entrainement
                """
            ),
            {
                "nom_modele": "Ridge",
                "version": "test",
                "hyperparametres": json.dumps({"alpha": 1.0}),
                "r2": 0.99,
                "mae": 1.0,
                "rmse": 1.5,
                "nb": len(raw),
                "chemin": str(artifact_path),
            },
        )
        return row.scalar_one()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def api_key_header():
    return {"X-API-Key": os.environ["API_KEY"]}
