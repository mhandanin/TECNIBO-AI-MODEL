"""Train/test split, model evaluation and comparison-table export."""
from __future__ import annotations

import time

import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import cross_val_score, train_test_split

from .config import FEATURE_COLUMNS, RANDOM_STATE, REPORTS_DIR, TARGET_COLUMN
from .data import clean_dataframe, load_dataset
from .features import SppEncoder, engineer_features
from .models import get_models


def build_dataset() -> pd.DataFrame:
    df = load_dataset()
    df = clean_dataframe(df)
    df = engineer_features(df)
    return df


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


def evaluate_models(X_train, X_test, y_train, y_test) -> tuple[pd.DataFrame, dict]:
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
        print(
            f"{name:18s} R2={rows[-1]['r2_test']:.4f}  MAE={rows[-1]['mae_test']:.2f}  "
            f"RMSE={rows[-1]['rmse_test']:.2f}  CV_R2={cv_r2.mean():.4f}+-{cv_r2.std():.4f}  "
            f"time={train_time:.2f}s"
        )

    results = pd.DataFrame(rows).sort_values("r2_test", ascending=False).reset_index(drop=True)
    return results, fitted


def export_tables(results: pd.DataFrame) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(REPORTS_DIR / "model_comparison.csv", index=False)

    lines = [
        "| Modele | R2 (test) | MAE (test) | RMSE (test) | R2 CV (train, 5-fold) | Temps entrainement (s) |",
        "|---|---|---|---|---|---|",
    ]
    for _, row in results.iterrows():
        lines.append(
            f"| {row['model']} | {row['r2_test']:.4f} | {row['mae_test']:.2f} EUR | "
            f"{row['rmse_test']:.2f} EUR | {row['r2_cv_mean']:.4f} +/- {row['r2_cv_std']:.4f} | "
            f"{row['train_time_s']:.2f} |"
        )
    (REPORTS_DIR / "model_comparison.md").write_text("\n".join(lines), encoding="utf-8")
