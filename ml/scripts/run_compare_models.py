#!/usr/bin/env python3
"""Model comparison entrypoint.

Trains and evaluates 5 candidate models on a held-out test set, exports the
comparison table (reports/model_comparison.{csv,md}) and the corresponding
figures (reports/figures/06..08).

Usage:
    python scripts/run_compare_models.py
"""
from pricing_ml.evaluate import build_dataset, evaluate_models, export_tables, split_and_encode
from pricing_ml.plots import plot_comparison, plot_feature_importance, plot_predicted_vs_actual


def main() -> None:
    df = build_dataset()
    X_train, X_test, y_train, y_test = split_and_encode(df)

    results, fitted = evaluate_models(X_train, X_test, y_train, y_test)
    export_tables(results)
    plot_comparison(results)

    best_name = results.iloc[0]["model"]
    best_model = fitted[best_name]
    plot_feature_importance(best_name, best_model, X_train.columns)
    plot_predicted_vs_actual(best_name, best_model, X_test, y_test)

    print("\nBest model:", best_name)
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
