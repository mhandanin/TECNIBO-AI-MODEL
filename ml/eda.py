"""Exploratory data analysis for the industrial pricing dataset.

Generates PNG figures under reports/figures/ for use in the certification
report (RNCP37827, bloc E2 - comprehension/preparation des donnees).

Usage:
    python ml/eda.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from data_prep import (
    ENGINEERED_FEATURE_COLUMNS,
    RAW_FEATURE_COLUMNS,
    TARGET_COLUMN,
    engineer_features,
    load_dataset,
)

FIGURES_DIR = Path(__file__).resolve().parent.parent / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


def savefig(name: str) -> None:
    path = FIGURES_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"saved {path}")


def missing_and_outlier_summary(df: pd.DataFrame) -> None:
    print("Shape:", df.shape)
    print("\nMissing values per column:")
    print(df.isna().sum())

    numeric_cols = df.select_dtypes("number").columns
    print("\nOutlier count per numeric column (IQR rule, k=1.5):")
    for col in numeric_cols:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_out = ((df[col] < lower) | (df[col] > upper)).sum()
        print(f"  {col:26s}: {n_out}")


def plot_target_distribution(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    sns.histplot(df[TARGET_COLUMN], bins=60, kde=True, ax=axes[0])
    axes[0].set_title("Distribution de Article_price")
    sns.boxplot(x=df[TARGET_COLUMN], ax=axes[1])
    axes[1].set_title("Boxplot Article_price (detection outliers)")
    savefig("01_target_distribution.png")


def plot_feature_distributions(df: pd.DataFrame) -> None:
    cols = RAW_FEATURE_COLUMNS + ["Width_mm", "Height_mm"]
    n = len(cols)
    ncols = 3
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 3.4 * nrows))
    axes = axes.flatten()
    for ax, col in zip(axes, cols):
        sns.histplot(df[col], bins=40, kde=True, ax=ax, color="steelblue")
        ax.set_title(col)
    for ax in axes[len(cols):]:
        ax.axis("off")
    savefig("02_feature_distributions.png")


def plot_correlation_heatmap(df: pd.DataFrame) -> None:
    numeric_cols = RAW_FEATURE_COLUMNS + ENGINEERED_FEATURE_COLUMNS + [TARGET_COLUMN]
    corr = df[numeric_cols].corr()
    plt.figure(figsize=(9, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, vmin=-1, vmax=1)
    plt.title("Correlation entre features (brutes + engineerees) et Article_price")
    savefig("03_correlation_heatmap.png")


def plot_target_vs_top_features(df: pd.DataFrame) -> None:
    features = ["material_cost", "Surface_m2", "profile_cost", "Complexity_factor"]
    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    for ax, feat in zip(axes.flatten(), features):
        sns.scatterplot(x=df[feat], y=df[TARGET_COLUMN], ax=ax, alpha=0.25, s=12)
        ax.set_title(f"Article_price vs {feat}")
    savefig("04_target_vs_top_features.png")


def plot_spp_effect(df: pd.DataFrame) -> None:
    spp_means = df.groupby("SPP")[TARGET_COLUMN].mean().sort_values()
    plt.figure(figsize=(10, 4))
    plt.plot(range(len(spp_means)), spp_means.values, ".", alpha=0.5)
    plt.axhline(df[TARGET_COLUMN].mean(), color="red", linestyle="--", label="Moyenne globale")
    plt.title(f"Prix moyen par code SPP ({df['SPP'].nunique()} codes distincts / {len(df)} lignes)")
    plt.xlabel("Codes SPP (tries par prix moyen)")
    plt.ylabel("Article_price moyen")
    plt.legend()
    savefig("05_spp_effect.png")


def main() -> None:
    df = load_dataset()
    df["SPP"] = df["SPP"].astype(str).str.strip()
    df = engineer_features(df)

    missing_and_outlier_summary(df)
    plot_target_distribution(df)
    plot_feature_distributions(df)
    plot_correlation_heatmap(df)
    plot_target_vs_top_features(df)
    plot_spp_effect(df)


if __name__ == "__main__":
    main()
