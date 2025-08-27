import pytest
from app.calculators.cha2ds2vasc import cha2ds2vasc
from app.validators.patient_input import validate_cha2ds2vasc_input


def test_validate_input_accepts_valid_data():
    valid_data = {
        "chf": 1,
        "hypertension": 0,
        "age_ge_75": False,
        "diabetes": True,
        "stroke": 0,
        "vascular": 1,
        "age_65_74": 0,
        "female": True,
    }
    # Should not raise
    validate_cha2ds2vasc_input(valid_data)


def test_validate_input_rejects_invalid_binary_values():
    invalid_data = {
        "chf": 2,  # invalid: not 0/1
        "hypertension": 0,
        "age_ge_75": 0,
        "diabetes": 0,
        "stroke": 0,
        "vascular": 0,
        "age_65_74": 0,
        "female": 0,
    }
    with pytest.raises(ValueError, match="Field 'chf' must be 0/1 or True/False in CHA2DS2VASc"):
        validate_cha2ds2vasc_input(invalid_data)


def test_validate_input_rejects_non_binary_types():
    invalid_data = {
        "chf": "1",
        "hypertension": 0,
        "age_ge_75": 0,
        "diabetes": 0,
        "stroke": 0,
        "vascular": 0,
        "age_65_74": 0,
        "female": 0,
    }
    with pytest.raises(ValueError, match="Field 'chf' must be 0/1 or True/False in CHA2DS2VASc"):
        validate_cha2ds2vasc_input(invalid_data)


def test_validate_input_rejects_conflicting_age_flags():
    data = {
        "chf": 0,
        "hypertension": 0,
        "age_ge_75": 1,
        "diabetes": 0,
        "stroke": 0,
        "vascular": 0,
        "age_65_74": 1,  # conflict!
        "female": 0,
    }
    with pytest.raises(ValueError, match="cannot both be 1"):
        validate_cha2ds2vasc_input(data)


def test_cha2ds2vasc_all_zero():
    data = {
        "chf": 0,
        "hypertension": 0,
        "age_ge_75": 0,
        "diabetes": 0,
        "stroke": 0,
        "vascular": 0,
        "age_65_74": 0,
        "female": 0,
    }
    assert cha2ds2vasc(data) == 0


def test_cha2ds2vasc_typical_case():
    data = {
        "chf": 1,
        "hypertension": 1,
        "age_ge_75": 0,
        "diabetes": 1,
        "stroke": 0,
        "vascular": 1,
        "age_65_74": 1,
        "female": 0,
    }
    # 1+1+0+1+0+1+1+0 = 5
    assert cha2ds2vasc(data) == 5


def test_cha2ds2vasc_age_over_75_and_female():
    data = {
        "chf": 0,
        "hypertension": 0,
        "age_ge_75": 1,   # 2 points
        "diabetes": 0,
        "stroke": 0,
        "vascular": 0,
        "age_65_74": 0,
        "female": 1,      # 1 point
    }
    assert cha2ds2vasc(data) == 3


def test_cha2ds2vasc_maximum_score():
    data = {
        "chf": 1,           # 1
        "hypertension": 1,  # 1
        "age_ge_75": 1,     # 2 (excludes age_65_74)
        "diabetes": 1,      # 1
        "stroke": 1,        # 2
        "vascular": 1,      # 1
        "age_65_74": 0,     # 0 (mutually exclusive)
        "female": 1,        # 1
    }
    assert cha2ds2vasc(data) == 9