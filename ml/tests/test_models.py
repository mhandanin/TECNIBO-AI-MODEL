from sklearn.linear_model import Ridge

from pricing_ml.models import get_models


def test_get_models_returns_expected_candidates():
    models = get_models()

    assert set(models) == {
        "LinearRegression",
        "Ridge",
        "ElasticNetCV",
        "RandomForest",
        "GradientBoosting",
    }
    for model in models.values():
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")


def test_ridge_uses_alpha_one():
    ridge_step = get_models()["Ridge"].named_steps["ridge"]

    assert isinstance(ridge_step, Ridge)
    assert ridge_step.alpha == 1.0
