"""Integration tests: exercise the FastAPI app against a real (disposable)
Postgres database (see conftest.py). Requires a reachable Postgres server.
"""
from __future__ import annotations

from sqlalchemy import text

import pytest

pytestmark = pytest.mark.integration


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_catalogue_lists_seeded_materiaux_and_profiles(client, seed_catalogue):
    resp = client.get("/catalogue")
    assert resp.status_code == 200
    assert resp.json() == {
        "materiaux": ["Glass_Tempered_8"],
        "profiles": ["Aluminium_Thermal"],
    }


def test_model_info_returns_active_model_metadata(client, trained_model):
    resp = client.get("/model/info")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id_entrainement"] == trained_model
    assert body["nom_modele"] == "Ridge"


def test_predict_without_api_key_is_rejected(client, trained_model, seed_catalogue):
    resp = client.post(
        "/predict",
        json={
            "largeur_mm": 1000,
            "hauteur_mm": 1000,
            "materiau": "Glass_Tempered_8",
            "profile": "Aluminium_Thermal",
            "code_spp": "8906",
            "complexity_factor": 1.0,
            "logistics_cost": 5.0,
        },
    )
    assert resp.status_code == 401


def test_predict_with_wrong_api_key_is_rejected(client, trained_model, seed_catalogue):
    resp = client.post(
        "/predict",
        headers={"X-API-Key": "wrong-key"},
        json={
            "largeur_mm": 1000,
            "hauteur_mm": 1000,
            "materiau": "Glass_Tempered_8",
            "profile": "Aluminium_Thermal",
            "code_spp": "8906",
            "complexity_factor": 1.0,
            "logistics_cost": 5.0,
        },
    )
    assert resp.status_code == 401


def test_predict_unknown_materiau_returns_404(client, trained_model, seed_catalogue, api_key_header):
    resp = client.post(
        "/predict",
        headers=api_key_header,
        json={
            "largeur_mm": 1000,
            "hauteur_mm": 1000,
            "materiau": "Unknown_Material",
            "profile": "Aluminium_Thermal",
            "code_spp": "8906",
            "complexity_factor": 1.0,
            "logistics_cost": 5.0,
        },
    )
    assert resp.status_code == 404


def test_predict_unknown_profile_returns_404(client, trained_model, seed_catalogue, api_key_header):
    resp = client.post(
        "/predict",
        headers=api_key_header,
        json={
            "largeur_mm": 1000,
            "hauteur_mm": 1000,
            "materiau": "Glass_Tempered_8",
            "profile": "Unknown_Profile",
            "code_spp": "8906",
            "complexity_factor": 1.0,
            "logistics_cost": 5.0,
        },
    )
    assert resp.status_code == 404


def test_predict_invalid_payload_returns_422(client, trained_model, seed_catalogue, api_key_header):
    resp = client.post(
        "/predict",
        headers=api_key_header,
        json={
            "largeur_mm": 0,
            "hauteur_mm": 1000,
            "materiau": "Glass_Tempered_8",
            "profile": "Aluminium_Thermal",
            "code_spp": "8906",
            "complexity_factor": 1.0,
            "logistics_cost": 5.0,
        },
    )
    assert resp.status_code == 422


def test_predict_happy_path_returns_price_and_logs_prediction(
    client, trained_model, seed_catalogue, api_key_header, test_db_engine
):
    resp = client.post(
        "/predict",
        headers=api_key_header,
        json={
            "largeur_mm": 1360,
            "hauteur_mm": 1794,
            "materiau": "Glass_Tempered_8",
            "profile": "Aluminium_Thermal",
            "code_spp": "8906",
            "complexity_factor": 1.094923,
            "logistics_cost": 16.13,
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["id_entrainement"] == trained_model
    assert body["nom_modele"] == "Ridge"
    assert isinstance(body["prix_predit"], float)

    with test_db_engine.begin() as conn:
        count = conn.execute(text("SELECT count(*) FROM prediction")).scalar_one()
    assert count == 1
