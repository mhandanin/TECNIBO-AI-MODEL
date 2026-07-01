"""Loading and cleaning of the raw pricing dataset."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import DATA_PATH, IQR_FACTOR, NUMERIC_COLUMNS, TARGET_COLUMN


def load_dataset(path: Path | str = DATA_PATH) -> pd.DataFrame:
    return pd.read_excel(path, engine="openpyxl")


def clean_dataframe(df: pd.DataFrame, drop_outliers: bool = False) -> pd.DataFrame:
    """Coerce numeric columns, drop invalid rows, optionally filter target outliers (IQR)."""
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
        lower, upper = q1 - IQR_FACTOR * iqr, q3 + IQR_FACTOR * iqr
        df = df[(df[TARGET_COLUMN] >= lower) & (df[TARGET_COLUMN] <= upper)].copy()

    df["SPP"] = df["SPP"].astype(str).str.strip()
    return df.reset_index(drop=True)


def print_missing_and_outlier_summary(df: pd.DataFrame) -> None:
    """Print a quick data-quality summary (shape, missing values, IQR outlier counts)."""
    print("Shape:", df.shape)
    print("\nMissing values per column:")
    print(df.isna().sum())

    numeric_cols = df.select_dtypes("number").columns
    print("\nOutlier count per numeric column (IQR rule, k=1.5):")
    for col in numeric_cols:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - IQR_FACTOR * iqr, q3 + IQR_FACTOR * iqr
        n_out = ((df[col] < lower) | (df[col] > upper)).sum()
        print(f"  {col:26s}: {n_out}")
