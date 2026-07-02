from datetime import datetime, timezone

import pytest

from pricing_api import model_registry


@pytest.fixture(autouse=True)
def _clear_artifact_cache():
    model_registry._load_artifact.cache_clear()
    yield
    model_registry._load_artifact.cache_clear()


def _fake_row(**overrides) -> dict:
    row = {
        "id_entrainement": 1,
        "nom_modele": "Ridge",
        "version": "20260101000000",
        "chemin_artifact": "/fake/ridge_v1.joblib",
        "r2": 0.999,
        "mae": 4.0,
        "rmse": 5.0,
        "nb_echantillons": 8000,
        "date_entrainement": datetime.now(timezone.utc),
    }
    row.update(overrides)
    return row


def test_load_active_model_builds_active_model(monkeypatch):
    fake_artifact = {"pipeline": object(), "spp_encoder": object(), "feature_columns": ["a", "b"]}
    load_calls = []

    monkeypatch.setattr(model_registry, "get_latest_model_run", lambda: _fake_row())
    monkeypatch.setattr(
        model_registry.joblib, "load", lambda path: (load_calls.append(path), fake_artifact)[1]
    )

    active = model_registry.load_active_model()

    assert active.id_entrainement == 1
    assert active.nom_modele == "Ridge"
    assert active.pipeline is fake_artifact["pipeline"]
    assert active.spp_encoder is fake_artifact["spp_encoder"]
    assert active.feature_columns == ["a", "b"]
    assert len(load_calls) == 1


def test_load_active_model_caches_artifact_by_path(monkeypatch):
    fake_artifact = {"pipeline": object(), "spp_encoder": object(), "feature_columns": []}
    load_calls = []

    monkeypatch.setattr(model_registry, "get_latest_model_run", lambda: _fake_row())
    monkeypatch.setattr(
        model_registry.joblib, "load", lambda path: (load_calls.append(path), fake_artifact)[1]
    )

    model_registry.load_active_model()
    model_registry.load_active_model()

    assert len(load_calls) == 1


def test_load_active_model_raises_when_no_run_registered(monkeypatch):
    monkeypatch.setattr(model_registry, "get_latest_model_run", lambda: None)

    with pytest.raises(RuntimeError):
        model_registry.load_active_model()
