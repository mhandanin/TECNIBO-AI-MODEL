"""Unit test for the readiness probe failure path (no real DB needed)."""
from __future__ import annotations

from fastapi.testclient import TestClient

from pricing_api import db, main


def test_health_ready_returns_503_when_db_unreachable(monkeypatch):
    def _broken_connect():
        raise ConnectionError("could not connect to server")

    monkeypatch.setattr(db.engine, "connect", _broken_connect)

    client = TestClient(main.app)
    resp = client.get("/health/ready")

    assert resp.status_code == 503
    assert resp.json()["status"] == "unavailable"
