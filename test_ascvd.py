# tests/test_ascvd.py
import math
import pytest

from app.calculators.ascvd import (
    common_terms,
    terms_white_female,
    terms_black_female,
    terms_white_male,
    terms_black_male,
    ascvd_pce_risk,
)


# ------------------------
# common_terms Tests
# ------------------------

def test_common_terms_basic():
    """Test common log-transformed terms are computed correctly."""
    patient = {
        "age": 50,
        "total_cholesterol": 200,
        "hdl": 50,
        "sbp": 120,
        "on_htn_meds": True,
        "smoker": False,
        "diabetes": True,
    }

    terms = common_terms(patient)

    assert math.isclose(terms["ln_age"], math.log(50), rel_tol=1e-6)
    assert math.isclose(terms["ln_age_sq"], math.log(50) ** 2, rel_tol=1e-6)
    assert math.isclose(terms["ln_tc"], math.log(200), rel_tol=1e-6)
    assert math.isclose(terms["ln_hdl"], math.log(50), rel_tol=1e-6)
    assert math.isclose(terms["ln_sbp"], math.log(120), rel_tol=1e-6)
    assert terms["trt"] == 1
    assert terms["smoker"] == 0
    assert terms["diabetes"] == 1


def test_common_terms_no_medication():
    """Test trt=0 when on_htn_meds is False."""
    patient = {
        "age": 60,
        "total_cholesterol": 190,
        "hdl": 45,
        "sbp": 130,
        "on_htn_meds": False,
        "smoker": True,
        "diabetes": False,
    }

    terms = common_terms(patient)
    assert terms["trt"] == 0
    assert terms["smoker"] == 1
    assert terms["diabetes"] == 0


# ------------------------
# Term Builders Tests
# ------------------------

@pytest.mark.parametrize(
    "builder,sex,race",
    [
        (terms_white_female, "female", "white"),
        (terms_black_female, "female", "black"),
        (terms_white_male, "male", "white"),
        (terms_black_male, "male", "black"),
    ],
)
def test_term_builders_output_types(builder, sex, race):
    """Ensure all term builders return numeric values."""
    patient = {
        "age": 55,
        "total_cholesterol": 210,
        "hdl": 55,
        "sbp": 130,
        "on_htn_meds": False,
        "smoker": True,
        "diabetes": False,
    }

    terms = builder(patient)
    for name, value in terms.items():
        assert isinstance(value, (int, float)), f"Term '{name}' is not numeric"


@pytest.mark.parametrize("on_htn_meds", [True, False])
def test_white_female_treated_vs_untreated_bp_fields(on_htn_meds):
    """Ensure correct SBP term is included based on treatment status."""
    patient = {
        "age": 60,
        "total_cholesterol": 200,
        "hdl": 50,
        "sbp": 120,
        "on_htn_meds": on_htn_meds,
        "smoker": False,
        "diabetes": False,
    }

    terms = terms_white_female(patient)

    if on_htn_meds:
        assert "ln_sbp_trt" in terms
        assert "ln_sbp_untrt" not in terms
    else:
        assert "ln_sbp_untrt" in terms
        assert "ln_sbp_trt" not in terms


@pytest.mark.parametrize("on_htn_meds", [True, False])
def test_black_female_includes_age_sbp_interaction(on_htn_meds):
    """Black female model includes interaction term with ln_age * ln_sbp."""
    patient = {
        "age": 60,
        "total_cholesterol": 200,
        "hdl": 50,
        "sbp": 120,
        "on_htn_meds": on_htn_meds,
        "smoker": False,
        "diabetes": False,
    }

    terms = terms_black_female(patient)
    key = "ln_sbp_trt" if on_htn_meds else "ln_sbp_untrt"
    interaction = "ln_age*ln_sbp_trt" if on_htn_meds else "ln_age*ln_sbp_untrt"

    assert key in terms
    assert interaction in terms


# ------------------------
# Final Risk Calculation Tests
# ------------------------

@pytest.mark.parametrize(
    "patient,expected_range",
    [
        (
            {
                "sex": "female",
                "race": "white",
                "age": 60,
                "total_cholesterol": 200,
                "hdl": 50,
                "sbp": 120,
                "on_htn_meds": False,
                "smoker": False,
                "diabetes": False,
            },
            (0.0, 20.0),  # Low-risk white female → low risk
        ),
        (
            {
                "sex": "male",
                "race": "black",
                "age": 55,
                "total_cholesterol": 190,
                "hdl": 45,
                "sbp": 140,
                "on_htn_meds": True,
                "smoker": True,
                "diabetes": True,
            },
            (20.0, 100.0),  # High-risk black male → elevated risk
        ),
    ],
)
def test_ascvd_risk_returns_valid_percentage(patient, expected_range):
    """Ensure risk is a float within [0, 100] and in expected range."""
    risk = ascvd_pce_risk(patient)
    assert isinstance(risk, float)
    assert 0.0 <= risk <= 100.0
    assert expected_range[0] <= risk <= expected_range[1]


def test_ascvd_risk_extreme_age_returns_clamped_values():
    """Very high or low deviation should return clamped 0 or 100."""
    patient = {
        "sex": "male",
        "race": "white",
        "age": 79,
        "total_cholesterol": 400,
        "hdl": 10,
        "sbp": 250,
        "on_htn_meds": True,
        "smoker": True,
        "diabetes": True,
    }

    risk = ascvd_pce_risk(patient)
    assert risk >= 95.0
    assert risk < 100.0  # unless truly infinite


def test_ascvd_risk_invalid_race_raises_error():
    """Race not in ('white', 'black') should raise ValueError."""
    patient = {
        "sex": "female",
        "race": "asian",  # Not supported
        "age": 55,
        "total_cholesterol": 200,
        "hdl": 50,
        "sbp": 120,
        "on_htn_meds": False,
        "smoker": False,
        "diabetes": False,
    }

    with pytest.raises(ValueError, match="Invalid value for 'race' in ASCVD: 'asian'. Must be one of \['black', 'white'\]"):
        ascvd_pce_risk(patient)


def test_ascvd_risk_missing_required_field_raises_error():
    """Missing 'hdl' should trigger validation error."""
    patient = {
        "sex": "female",
        "race": "white",
        "age": 60,
        "total_cholesterol": 200,
        "sbp": 120,
        "on_htn_meds": False,
        "smoker": False,
        "diabetes": False,
        # hdl missing
    }

    with pytest.raises(ValueError, match="Missing required fields"):
        ascvd_pce_risk(patient)


def test_ascvd_risk_invalid_binary_flag_raises_error():
    """Smoker=2 should be rejected."""
    patient = {
        "sex": "male",
        "race": "white",
        "age": 50,
        "total_cholesterol": 200,
        "hdl": 50,
        "sbp": 130,
        "on_htn_meds": 0,
        "smoker": 2,  # Invalid
        "diabetes": 0,
    }

    with pytest.raises(ValueError, match="smoker must be 0 or 1"):
        ascvd_pce_risk(patient)


def test_ascvd_risk_low_hdl_raises_error():
    """HDL=5 is out of valid range."""
    patient = {
        "sex": "female",
        "race": "white",
        "age": 55,
        "total_cholesterol": 200,
        "hdl": 5,  # Too low
        "sbp": 120,
        "on_htn_meds": False,
        "smoker": False,
        "diabetes": False,
    }

    with pytest.raises(ValueError, match="hdl in ASCVD out of range: 5 \(expected between 10 and 150\)"):
        ascvd_pce_risk(patient)