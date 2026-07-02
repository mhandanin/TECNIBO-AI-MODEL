import pandas as pd

from pricing_ml.config import FEATURE_COLUMNS
from pricing_ml.evaluate import split_and_encode
from pricing_ml.features import engineer_features


def _synthetic_dataset(n=10) -> pd.DataFrame:
    raw = pd.DataFrame(
        {
            "Width_mm": [1000 + 10 * i for i in range(n)],
            "Height_mm": [800 + 5 * i for i in range(n)],
            "Surface_m2": [1.0 + 0.1 * i for i in range(n)],
            "Material_price_m2": [50.0 + i for i in range(n)],
            "Profile_price_unit": [10.0 + i for i in range(n)],
            "Complexity_factor": [1.0 + 0.05 * i for i in range(n)],
            "Logistics_cost": [5.0 + i for i in range(n)],
        }
    )
    df = engineer_features(raw)
    df["SPP"] = [f"SPP_{i % 3}" for i in range(n)]
    df["Article_price"] = [100.0 + 10 * i for i in range(n)]
    return df


def test_split_and_encode_returns_expected_shapes_and_columns():
    df = _synthetic_dataset(n=10)

    X_train, X_test, y_train, y_test = split_and_encode(df)

    assert len(X_train) + len(X_test) == len(df)
    assert len(X_train) == len(y_train)
    assert len(X_test) == len(y_test)
    assert list(X_train.columns) == FEATURE_COLUMNS
    assert list(X_test.columns) == FEATURE_COLUMNS
    assert not set(X_train.index) & set(X_test.index)


def test_split_and_encode_spp_price_has_no_missing_values():
    df = _synthetic_dataset(n=10)

    X_train, X_test, _, _ = split_and_encode(df)

    assert X_train["SPP_price"].isna().sum() == 0
    assert X_test["SPP_price"].isna().sum() == 0
