import pytest
from fastapi import HTTPException

from pricing_api import security


def test_missing_key_raises_401(monkeypatch):
    monkeypatch.setattr(security, "API_KEY", "expected-key")

    with pytest.raises(HTTPException) as exc_info:
        security.require_api_key(None)

    assert exc_info.value.status_code == 401


def test_wrong_key_raises_401(monkeypatch):
    monkeypatch.setattr(security, "API_KEY", "expected-key")

    with pytest.raises(HTTPException) as exc_info:
        security.require_api_key("wrong-key")

    assert exc_info.value.status_code == 401


def test_correct_key_is_accepted(monkeypatch):
    monkeypatch.setattr(security, "API_KEY", "expected-key")

    result = security.require_api_key("expected-key")

    assert result == "expected-key"


def test_unconfigured_api_key_raises_runtime_error(monkeypatch):
    monkeypatch.setattr(security, "API_KEY", "")

    with pytest.raises(RuntimeError):
        security.require_api_key("anything")
