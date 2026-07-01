import pandas as pd

from pricing_ml.features import SppEncoder, engineer_features


def test_engineer_features_computes_expected_columns():
    df = pd.DataFrame(
        {
            "Width_mm": [1000, 2000],
            "Height_mm": [1000, 500],
            "Surface_m2": [1.0, 2.0],
            "Material_price_m2": [50.0, 100.0],
            "Profile_price_unit": [10.0, 20.0],
            "Complexity_factor": [1.0, 1.5],
        }
    )

    result = engineer_features(df)

    assert result["Perimeter_m"].tolist() == [4.0, 5.0]
    assert result["material_cost"].tolist() == [50.0, 200.0]
    assert result["profile_cost"].tolist() == [40.0, 100.0]
    assert result["complexity_material_cost"].tolist() == [50.0, 300.0]


def test_spp_encoder_fits_on_train_only_and_handles_unseen_codes():
    train_spp = pd.Series(["A", "A", "B", "B"])
    train_target = pd.Series([100.0, 120.0, 200.0, 220.0])

    encoder = SppEncoder().fit(train_spp, train_target)

    assert encoder.global_mean_ == 160.0
    assert encoder.table_["A"] == -50.0
    assert encoder.table_["B"] == 50.0

    test_spp = pd.Series(["A", "B", "UNSEEN_CODE"])
    encoded = encoder.transform(test_spp)

    assert encoded.tolist() == [-50.0, 50.0, 0.0]
