"""Compare candidate regression models for the Article_price pricing model.

Trains and evaluates several models on a single held-out test set (80/20),
using a proper train-only fit for the SPP target-encoding (unlike the
original discover_formula_v2.py, which encoded SPP on the full dataset
before any split).

Produces:
- reports/figures/06_model_comparison_metrics.png
- reports/figures/07_feature_importance_best_model.png
- reports/figures/08_predicted_vs_actual_best_model.png
- reports/model_comparison.md   (markdown table for the certification report)
- reports/model_comparison.csv

Usage:
    python ml/compare_models.py
"""
from __future__ import annotations

import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNetCV, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from data_prep import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    SppEncoder,
    clean_dataframe,
    engineer_features,
    load_dataset,
)

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")
RANDOM_STATE = 42


def build_dataset() -> tuple[pd.DataFrame, pd.Series]:
    df = load_dataset()
    df = clean_dataframe(df)
    df = engineer_features(df)
    return df, df[TARGET_COLUMN]


def split_and_encode(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=RANDOM_STATE)

    encoder = SppEncoder().fit(train_df["SPP"], train_df[TARGET_COLUMN])
    train_df = train_df.copy()
    test_df = test_df.copy()
    train_df["SPP_price"] = encoder.transform(train_df["SPP"])
    test_df["SPP_price"] = encoder.transform(test_df["SPP"])

    X_train = train_df[FEATURE_COLUMNS]
    X_test = test_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]
    y_test = test_df[TARGET_COLUMN]
    return X_train, X_test, y_train, y_test


def get_models() -> dict:
    return {
        "LinearRegression": make_pipeline(StandardScaler(), LinearRegression()),
        "Ridge": make_pipeline(StandardScaler(), Ridge(alpha=1.0, random_state=RANDOM_STATE)),
        "ElasticNetCV": make_pipeline(
            StandardScaler(),
            ElasticNetCV(
                l1_ratio=[0.1, 0.3, 0.5, 0.7, 0.9, 0.95],
                alphas=100,
                cv=5,
                max_iter=20000,
                n_jobs=-1,
                random_state=RANDOM_STATE,
            ),
        ),
        "RandomForest": RandomForestRegressor(
            n_estimators=300, max_depth=None, n_jobs=-1, random_state=RANDOM_STATE
        ),
        "GradientBoosting": GradientBoostingRegressor(random_state=RANDOM_STATE),
    }


def evaluate_models(X_train, X_test, y_train, y_test) -> pd.DataFrame:
    rows = []
    fitted = {}

    for name, model in get_models().items():
        start = time.perf_counter()
        model.fit(X_train, y_train)
        train_time = time.perf_counter() - start

        y_pred = model.predict(X_test)
        cv_r2 = cross_val_score(model, X_train, y_train, cv=5, scoring="r2", n_jobs=-1)

        rows.append(
            {
                "model": name,
                "r2_test": r2_score(y_test, y_pred),
                "mae_test": mean_absolute_error(y_test, y_pred),
                "rmse_test": root_mean_squared_error(y_test, y_pred),
                "r2_cv_mean": cv_r2.mean(),
                "r2_cv_std": cv_r2.std(),
                "train_time_s": train_time,
            }
        )
        fitted[name] = model
        print(f"{name:18s} R2={rows[-1]['r2_test']:.4f}  MAE={rows[-1]['mae_test']:.2f}  "
              f"RMSE={rows[-1]['rmse_test']:.2f}  CV_R2={cv_r2.mean():.4f}+-{cv_r2.std():.4f}  "
              f"time={train_time:.2f}s")

    results = pd.DataFrame(rows).sort_values("r2_test", ascending=False).reset_index(drop=True)
    return results, fitted


def plot_comparison(results: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    sns.barplot(data=results, x="model", y="r2_test", ax=axes[0], palette="viridis")
    axes[0].set_title("R2 (test set)")
    axes[0].set_ylim(0, 1)
    axes[0].tick_params(axis="x", rotation=30)

    sns.barplot(data=results, x="model", y="mae_test", ax=axes[1], palette="viridis")
    axes[1].set_title("MAE (test set, EUR)")
    axes[1].tick_params(axis="x", rotation=30)

    sns.barplot(data=results, x="model", y="train_time_s", ax=axes[2], palette="viridis")
    axes[2].set_title("Temps d'entrainement (s)")
    axes[2].tick_params(axis="x", rotation=30)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "06_model_comparison_metrics.png", dpi=150)
    plt.close()


def plot_feature_importance(best_name: str, best_model, X_train: pd.DataFrame) -> None:
    plt.figure(figsize=(8, 5))
    if hasattr(best_model, "feature_importances_"):
        importances = pd.Series(best_model.feature_importances_, index=X_train.columns)
        importances.sort_values().plot.barh(color="steelblue")
        plt.title(f"Importance des features - {best_name}")
    elif hasattr(best_model, "named_steps"):
        final_step = list(best_model.named_steps.values())[-1]
        if hasattr(final_step, "coef_"):
            coefs = pd.Series(final_step.coef_, index=X_train.columns)
            coefs.sort_values().plot.barh(color="steelblue")
            plt.title(f"Coefficients standardises - {best_name}")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "07_feature_importance_best_model.png", dpi=150)
    plt.close()


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
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "08_predicted_vs_actual_best_model.png", dpi=150)
    plt.close()


def export_tables(results: pd.DataFrame) -> None:
    results.to_csv(REPORTS_DIR / "model_comparison.csv", index=False)

    lines = ["| Modele | R2 (test) | MAE (test) | RMSE (test) | R2 CV (train, 5-fold) | Temps entrainement (s) |",
             "|---|---|---|---|---|---|"]
    for _, row in results.iterrows():
        lines.append(
            f"| {row['model']} | {row['r2_test']:.4f} | {row['mae_test']:.2f} EUR | "
            f"{row['rmse_test']:.2f} EUR | {row['r2_cv_mean']:.4f} +/- {row['r2_cv_std']:.4f} | "
            f"{row['train_time_s']:.2f} |"
        )
    (REPORTS_DIR / "model_comparison.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    df, _ = build_dataset()
    X_train, X_test, y_train, y_test = split_and_encode(df)

    results, fitted = evaluate_models(X_train, X_test, y_train, y_test)
    export_tables(results)
    plot_comparison(results)

    best_name = results.iloc[0]["model"]
    best_model = fitted[best_name]
    plot_feature_importance(best_name, best_model, X_train)
    plot_predicted_vs_actual(best_name, best_model, X_test, y_test)

    print("\nBest model:", best_name)
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
