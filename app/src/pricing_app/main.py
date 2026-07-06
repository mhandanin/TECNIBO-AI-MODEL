"""Minimal web client for the industrial pricing API.

Serves a single HTML form and proxies calls to the pricing API server-side,
so the API key never reaches the browser (it would otherwise be visible in
the page source / network tab of any client-side JS calling the API
directly).
"""
from __future__ import annotations

from pathlib import Path

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import API_KEY, PRICING_API_BASE_URL

app = FastAPI(title="Industrial Pricing : Client")

_PACKAGE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(_PACKAGE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(_PACKAGE_DIR / "static")), name="static")


def _pricing_api_request(method: str, path: str, **kwargs) -> httpx.Response:
    """Thin wrapper around the pricing API call, isolated so tests can mock it."""
    with httpx.Client(base_url=PRICING_API_BASE_URL, timeout=10.0) as http_client:
        return http_client.request(method, path, **kwargs)


def _relay(resp: httpx.Response) -> Response:
    return JSONResponse(content=resp.json(), status_code=resp.status_code)


@app.get("/", response_class=Response)
def index(request: Request) -> Response:
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/catalogue")
def catalogue() -> Response:
    resp = _pricing_api_request("GET", "/catalogue")
    return _relay(resp)


@app.post("/api/predict")
async def predict(request: Request) -> Response:
    payload = await request.json()
    resp = _pricing_api_request(
        "POST",
        "/predict",
        json=payload,
        headers={"X-API-Key": API_KEY},
    )
    return _relay(resp)
