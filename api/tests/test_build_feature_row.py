import pandas as pd
import pytest
from pricing_ml.config import FEATURE_COLUMNS

from pricing_api.features import build_feature_row


class _FakeSppEncoder:
    def transform(self, spp: pd.Series) -> pd.Series:
        return pd.Series([42.0] * len(spp))


def test_build_feature_row_computes_expected_columns_and_values():
    X = build_feature_row(
        largeur_mm=1000,
        hauteur_mm=1000,
        materiau_prix_m2=50.0,
        profile_prix_unitaire=10.0,
        code_spp="8906",
        complexity_factor=1.0,
        logistics_cost=5.0,
        spp_encoder=_FakeSppEncoder(),
    )

    assert list(X.columns) == FEATURE_COLUMNS
    row = X.iloc[0]
    assert row["Surface_m2"] == pytest.approx(1.0)
    assert row["Perimeter_m"] == pytest.approx(4.0)
    assert row["material_cost"] == pytest.approx(50.0)
    assert row["profile_cost"] == pytest.approx(40.0)
    assert row["complexity_material_cost"] == pytest.approx(50.0)
    assert row["SPP_price"] == pytest.approx(42.0)
