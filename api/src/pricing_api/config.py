"""Configuration and paths for the pricing API."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# api/src/pricing_api/config.py -> parents[2] is api/, parents[3] is the project root
API_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.environ["DATABASE_URL"]
API_KEY = os.environ.get("API_KEY", "")
MODEL_ARTIFACTS_DIR = API_DIR / "model_artifacts"
