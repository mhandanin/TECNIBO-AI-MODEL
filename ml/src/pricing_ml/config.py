"""Paths and column-name constants shared across the pricing_ml package."""
from __future__ import annotations

from pathlib import Path

# ml/src/pricing_ml/config.py -> parents[3] is the project root (industrial-pricing-ai/)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "industrial_pricing_dataset_10000_rows.xlsx"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

TARGET_COLUMN = "Article_price"
IQR_FACTOR = 1.5
RANDOM_STATE = 42

NUMERIC_COLUMNS = [
    "Width_mm",
    "Height_mm",
    "Surface_m2",
    "Material_price_m2",
    "Profile_price_unit",
    "Complexity_factor",
    "Logistics_cost",
    "Article_price",
]

RAW_FEATURE_COLUMNS = [
    "Complexity_factor",
    "Logistics_cost",
    "Surface_m2",
    "Material_price_m2",
    "Profile_price_unit",
]

ENGINEERED_FEATURE_COLUMNS = [
    "material_cost",
    "profile_cost",
    "complexity_material_cost",
    "Perimeter_m",
]

FEATURE_COLUMNS = RAW_FEATURE_COLUMNS + ENGINEERED_FEATURE_COLUMNS + ["SPP_price"]
