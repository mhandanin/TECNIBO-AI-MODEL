"""Shared data loading / cleaning / feature engineering for the pricing model.

Reworked from the original discover_formula_v2.py exploration script:
- same cleaning rules and engineered features
- SPP target-encoding is now fit on train data only (SppEncoder), to avoid
  the leakage of the original script (which encoded on the full dataset
  before any split).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

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

TARGET_COLUMN = "Article_price"
IQR_FACTOR = 1.5

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "industrial_pricing_dataset_10000_rows.xlsx"


def load_dataset(path: Path | str = DEFAULT_DATA_PATH) -> pd.DataFrame:
    return pd.read_excel(path, engine="openpyxl")


def clean_dataframe(df: pd.DataFrame, drop_outliers: bool = False) -> pd.DataFrame:
    df = df.copy()
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna().copy()
    df = df[df[TARGET_COLUMN] > 0].copy()
    df = df[(df["Width_mm"] > 0) & (df["Height_mm"] > 0)].copy()

    if drop_outliers:
        q1 = df[TARGET_COLUMN].quantile(0.25)
        q3 = df[TARGET_COLUMN].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - IQR_FACTOR * iqr
        upper = q3 + IQR_FACTOR * iqr
        df = df[(df[TARGET_COLUMN] >= lower) & (df[TARGET_COLUMN] <= upper)].copy()

    df["SPP"] = df["SPP"].astype(str).str.strip()
    return df.reset_index(drop=True)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Perimeter_m"] = 2 * (df["Width_mm"] + df["Height_mm"]) / 1000
    df["material_cost"] = df["Surface_m2"] * df["Material_price_m2"]
    df["profile_cost"] = df["Perimeter_m"] * df["Profile_price_unit"]
    df["complexity_material_cost"] = df["material_cost"] * df["Complexity_factor"]
    return df


@dataclass
class SppEncoder:
    """Target-mean encoding for the SPP code, fit on train data only."""

    global_mean_: float = 0.0
    table_: dict = field(default_factory=dict)

    def fit(self, spp: pd.Series, target: pd.Series) -> "SppEncoder":
        self.global_mean_ = float(target.mean())
        means = target.groupby(spp).mean()
        self.table_ = (means - self.global_mean_).to_dict()
        return self

    def transform(self, spp: pd.Series) -> pd.Series:
        return spp.map(self.table_).fillna(0.0)

    def fit_transform(self, spp: pd.Series, target: pd.Series) -> pd.Series:
        self.fit(spp, target)
        return self.transform(spp)


def load_clean_engineered(drop_outliers: bool = False) -> pd.DataFrame:
    df = load_dataset()
    df = clean_dataframe(df, drop_outliers=drop_outliers)
    df = engineer_features(df)
    return df
