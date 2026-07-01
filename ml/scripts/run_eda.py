#!/usr/bin/env python3
"""Exploratory data analysis entrypoint.

Generates PNG figures under reports/figures/ for the certification report.

Usage:
    python scripts/run_eda.py
"""
from pricing_ml.data import load_dataset, print_missing_and_outlier_summary
from pricing_ml.features import engineer_features
from pricing_ml.plots import (
    plot_correlation_heatmap,
    plot_feature_distributions,
    plot_spp_effect,
    plot_target_distribution,
    plot_target_vs_top_features,
)


def main() -> None:
    df = load_dataset()
    df["SPP"] = df["SPP"].astype(str).str.strip()
    df = engineer_features(df)

    print_missing_and_outlier_summary(df)
    plot_target_distribution(df)
    plot_feature_distributions(df)
    plot_correlation_heatmap(df)
    plot_target_vs_top_features(df)
    plot_spp_effect(df)


if __name__ == "__main__":
    main()
