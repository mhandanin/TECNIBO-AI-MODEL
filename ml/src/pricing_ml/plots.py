"""All matplotlib/seaborn figure generation, saved under reports/figures/."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .config import ENGINEERED_FEATURE_COLUMNS, FIGURES_DIR, RAW_FEATURE_COLUMNS, TARGET_COLUMN

sns.set_theme(style="whitegrid")


def _savefig(name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"saved {path}")


# --- EDA figures --------------------------------------------------------

def plot_target_distribution(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    sns.histplot(df[TARGET_COLUMN], bins=60, kde=True, ax=axes[0])
    axes[0].set_title("Distribution de Article_price")
    sns.boxplot(x=df[TARGET_COLUMN], ax=axes[1])
    axes[1].set_title("Boxplot Article_price (detection outliers)")
    _savefig("01_target_distribution.png")


def plot_feature_distributions(df: pd.DataFrame) -> None:
    cols = RAW_FEATURE_COLUMNS + ["Width_mm", "Height_mm"]
    ncols = 3
    nrows = (len(cols) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 3.4 * nrows))
    axes = axes.flatten()
    for ax, col in zip(axes, cols):
        sns.histplot(df[col], bins=40, kde=True, ax=ax, color="steelblue")
        ax.set_title(col)
    for ax in axes[len(cols):]:
        ax.axis("off")
    _savefig("02_feature_distributions.png")


def plot_correlation_heatmap(df: pd.DataFrame) -> None:
    numeric_cols = RAW_FEATURE_COLUMNS + ENGINEERED_FEATURE_COLUMNS + [TARGET_COLUMN]
    corr = df[numeric_cols].corr()
    plt.figure(figsize=(9, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, vmin=-1, vmax=1)
    plt.title("Correlation entre features (brutes + engineerees) et Article_price")
    _savefig("03_correlation_heatmap.png")


def plot_target_vs_top_features(df: pd.DataFrame) -> None:
    features = ["material_cost", "Surface_m2", "profile_cost", "Complexity_factor"]
    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    for ax, feat in zip(axes.flatten(), features):
        sns.scatterplot(x=df[feat], y=df[TARGET_COLUMN], ax=ax, alpha=0.25, s=12)
        ax.set_title(f"Article_price vs {feat}")
    _savefig("04_target_vs_top_features.png")


def plot_spp_effect(df: pd.DataFrame) -> None:
    spp_means = df.groupby("SPP")[TARGET_COLUMN].mean().sort_values()
    plt.figure(figsize=(10, 4))
    plt.plot(range(len(spp_means)), spp_means.values, ".", alpha=0.5)
    plt.axhline(df[TARGET_COLUMN].mean(), color="red", linestyle="--", label="Moyenne globale")
    plt.title(f"Prix moyen par code SPP ({df['SPP'].nunique()} codes distincts / {len(df)} lignes)")
    plt.xlabel("Codes SPP (tries par prix moyen)")
    plt.ylabel("Article_price moyen")
    plt.legend()
    _savefig("05_spp_effect.png")


# --- Model comparison figures -------------------------------------------

def plot_comparison(results: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    sns.barplot(data=results, x="model", y="r2_test", hue="model", legend=False, ax=axes[0], palette="viridis")
    axes[0].set_title("R2 (test set)")
    axes[0].set_ylim(0, 1)
    axes[0].tick_params(axis="x", rotation=30)

    sns.barplot(data=results, x="model", y="mae_test", hue="model", legend=False, ax=axes[1], palette="viridis")
    axes[1].set_title("MAE (test set, EUR)")
    axes[1].tick_params(axis="x", rotation=30)

    sns.barplot(data=results, x="model", y="train_time_s", hue="model", legend=False, ax=axes[2], palette="viridis")
    axes[2].set_title("Temps d'entrainement (s)")
    axes[2].tick_params(axis="x", rotation=30)

    _savefig("06_model_comparison_metrics.png")


def plot_feature_importance(best_name: str, best_model, feature_names) -> None:
    plt.figure(figsize=(8, 5))
    if hasattr(best_model, "feature_importances_"):
        importances = pd.Series(best_model.feature_importances_, index=feature_names)
        importances.sort_values().plot.barh(color="steelblue")
        plt.title(f"Importance des features - {best_name}")
    elif hasattr(best_model, "named_steps"):
        final_step = list(best_model.named_steps.values())[-1]
        if hasattr(final_step, "coef_"):
            coefs = pd.Series(final_step.coef_, index=feature_names)
            coefs.sort_values().plot.barh(color="steelblue")
            plt.title(f"Coefficients standardises - {best_name}")
    _savefig("07_feature_importance_best_model.png")


def plot_predicted_vs_actual(best_name: str, best_model, X_test, y_test) -> None:
    y_pred = best_model.predict(X_test)
    plt.figure(figsize=(6, 6))
    plt.scatter(y_test, y_pred, alpha=0.3, s=12)
    lims = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
    plt.plot(lims, lims, "r--", label="Prediction parfaite")
    plt.xlabel("Article_price reel")
    plt.ylabel("Article_price predit")
    plt.title(f"Predit vs reel - {best_name}")
    plt.legend()
    _savefig("08_predicted_vs_actual_best_model.png")
