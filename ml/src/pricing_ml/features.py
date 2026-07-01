"""Feature engineering, including the leakage-safe SPP target encoder.

Reworked from the original discover_formula_v2.py exploration script: same
engineered features, but SPP target-encoding is now fit on train data only
(SppEncoder.fit), instead of on the full dataset before any split.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .data import clean_dataframe, load_dataset


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
