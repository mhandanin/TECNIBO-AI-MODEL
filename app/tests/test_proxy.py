import httpx
import pytest
from fastapi.testclient import TestClient

from pricing_app import main


@pytest.fixture
def client():
    return TestClient(main.app)


def test_index_serves_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_catalogue_relays_success(client, monkeypatch):
    fake_response = httpx.Response(
        200, json={"materiaux": ["Glass_Tempered_8"], "profiles": ["Aluminium_Thermal"]}
    )
    monkeypatch.setattr(main, "_pricing_api_request", lambda method, path, **kw: fake_response)

    resp = client.get("/api/catalogue")

    assert resp.status_code == 200
    assert resp.json() == {"materiaux": ["Glass_Tempered_8"], "profiles": ["Aluminium_Thermal"]}


def test_predict_forwards_body_and_api_key(client, monkeypatch):
    monkeypatch.setattr(main, "API_KEY", "test-secret-key")
    captured = {}

    def fake_request(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["kwargs"] = kwargs
        return httpx.Response(
            200,
            json={
                "prix_predit": 181.8,
                "id_entrainement": 1,
                "nom_modele": "Ridge",
                "version": "20260702144144",
                "latence_ms": 10.4,
            },
        )

    monkeypatch.setattr(main, "_pricing_api_request", fake_request)

    payload = {
        "largeur_mm": 1360,
        "hauteur_mm": 1794,
        "materiau": "Glass_Tempered_8",
        "profile": "Aluminium_Thermal",
        "code_spp": "8906",
        "complexity_factor": 1.094923,
        "logistics_cost": 16.13,
    }
    resp = client.post("/api/predict", json=payload)

    assert resp.status_code == 200
    assert resp.json()["prix_predit"] == 181.8
    assert captured["method"] == "POST"
    assert captured["path"] == "/predict"
    assert captured["kwargs"]["json"] == payload
    assert captured["kwargs"]["headers"]["X-API-Key"] == "test-secret-key"


def test_predict_relays_error_status_and_detail(client, monkeypatch):
    fake_response = httpx.Response(404, json={"detail": "Materiau inconnu: 'Unknown'"})
    monkeypatch.setattr(main, "_pricing_api_request", lambda method, path, **kw: fake_response)

    resp = client.post(
        "/api/predict",
        json={
            "largeur_mm": 1000,
            "hauteur_mm": 1000,
            "materiau": "Unknown",
            "profile": "Aluminium_Thermal",
            "code_spp": "8906",
            "complexity_factor": 1.0,
            "logistics_cost": 10.0,
        },
    )

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Materiau inconnu: 'Unknown'"
