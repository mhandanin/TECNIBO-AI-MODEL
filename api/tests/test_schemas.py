import pytest
from pydantic import ValidationError
from pricing_api.schemas import PredictRequest

VALID = dict(
    largeur_mm=1000,
    hauteur_mm=1000,
    materiau="Glass_Tempered_8",
    profile="Aluminium_Thermal",
    code_spp="8906",
    complexity_factor=1.0,
    logistics_cost=10.0,
)


def test_valid_payload_is_accepted():
    req = PredictRequest(**VALID)
    assert req.largeur_mm == 1000


@pytest.mark.parametrize("field,value", [("largeur_mm", 0), ("largeur_mm", -1), ("largeur_mm", 10001)])
def test_largeur_mm_out_of_bounds_rejected(field, value):
    with pytest.raises(ValidationError):
        PredictRequest(**{**VALID, field: value})


@pytest.mark.parametrize("field,value", [("hauteur_mm", 0), ("hauteur_mm", -1), ("hauteur_mm", 10001)])
def test_hauteur_mm_out_of_bounds_rejected(field, value):
    with pytest.raises(ValidationError):
        PredictRequest(**{**VALID, field: value})


def test_complexity_factor_must_be_positive():
    with pytest.raises(ValidationError):
        PredictRequest(**{**VALID, "complexity_factor": 0})


def test_logistics_cost_allows_zero_but_not_negative():
    PredictRequest(**{**VALID, "logistics_cost": 0})
    with pytest.raises(ValidationError):
        PredictRequest(**{**VALID, "logistics_cost": -0.01})


def test_boundary_values_are_accepted():
    req = PredictRequest(**{**VALID, "largeur_mm": 10000, "hauteur_mm": 10000})
    assert req.largeur_mm == 10000
