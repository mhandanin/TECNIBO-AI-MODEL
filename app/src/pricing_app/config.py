"""Configuration for the pricing web client."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# app/src/pricing_app/config.py -> parents[2] is app/, parents[3] is the project root
APP_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")

PRICING_API_BASE_URL = os.environ.get("PRICING_API_BASE_URL", "http://127.0.0.1:8000")
API_KEY = os.environ.get("API_KEY", "")
