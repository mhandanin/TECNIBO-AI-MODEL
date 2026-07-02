"""API key authentication (header X-API-Key).

Simple shared-secret scheme, appropriate for a demo/certification project.
The key is declared as a FastAPI security scheme so it appears in the
OpenAPI docs (/docs) with the padlock icon and can be tested from there.
"""
from __future__ import annotations

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from .config import API_KEY

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(key: str | None = Security(_api_key_header)) -> str:
    if not API_KEY:
        raise RuntimeError("API_KEY is not configured on the server (.env)")
    if key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key (header X-API-Key)",
        )
    return key
