import pandas as pd

from pricing_ml.data import clean_dataframe


def _base_row(**overrides):
    row = {
        "Width_mm": 1000,
        "Height_mm": 1000,
        "Surface_m2": 1.0,
        "Material_price_m2": 50.0,
        "Profile_price_unit": 10.0,
        "Complexity_factor": 1.0,
        "Logistics_cost": 5.0,
        "Article_price": 100.0,
        "SPP": "A",
    }
    row.update(overrides)
    return row


def test_clean_dataframe_drops_non_numeric_rows():
    df = pd.DataFrame(
        [
            _base_row(),
            _base_row(Width_mm="not_a_number"),
        ]
    )

    result = clean_dataframe(df)

    assert len(result) == 1
    assert result.loc[0, "Width_mm"] == 1000


def test_clean_dataframe_drops_non_positive_target_and_dimensions():
    df = pd.DataFrame(
        [
            _base_row(),
            _base_row(Article_price=-10.0),
            _base_row(Width_mm=0),
            _base_row(Height_mm=-1),
        ]
    )

    result = clean_dataframe(df)

    assert len(result) == 1


def test_clean_dataframe_strips_spp_and_casts_to_str():
    df = pd.DataFrame([_base_row(SPP=" 42 ")])

    result = clean_dataframe(df)

    assert result.loc[0, "SPP"] == "42"


def test_clean_dataframe_drop_outliers_removes_extreme_target_values():
    rows = [_base_row(Article_price=price) for price in [95.0, 100.0, 105.0, 98.0, 102.0]]
    rows.append(_base_row(Article_price=100000.0))
    df = pd.DataFrame(rows)

    result = clean_dataframe(df, drop_outliers=True)

    assert 100000.0 not in result["Article_price"].tolist()
    assert len(result) == 5
