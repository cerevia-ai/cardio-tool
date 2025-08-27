# tests/test_patient_input.py
import pytest
from app.validators.patient_input import (
    validate_ascvd_input,
    validate_bp_input,
    validate_cha2ds2vasc_input,
    validate_ecg_rhythm_input,
    validate_ecg_12lead_input,
)


# ========================
# ASCVD INPUT VALIDATION
# ========================

def test_validate_ascvd_input_valid():
    """Test valid input passes validation."""
    patient = {
        'age': 60,
        'sex': 'Male',
        'race': 'White',
        'total_cholesterol': 200,
        'hdl': 50,
        'sbp': 120,
        'on_htn_meds': False,
        'smoker': False,
        'diabetes': False
    }
    assert validate_ascvd_input(patient) is None  # No exception = pass


def test_validate_ascvd_input_missing_fields():
    """Test missing required fields raises ValueError."""
    patient = {'age': 60, 'sex': 'Male'}
    with pytest.raises(ValueError, match="Missing required fields"):
        validate_ascvd_input(patient)


def test_validate_ascvd_input_age_out_of_range():
    """Test age <40 or >79 raises error."""
    patient = {
        'age': 35,
        'sex': 'Male',
        'race': 'White',
        'total_cholesterol': 200,
        'hdl': 50,
        'sbp': 120,
        'on_htn_meds': False,
        'smoker': False,
        'diabetes': False
    }
    with pytest.raises(ValueError, match=r"age in ASCVD out of range: 35 \(expected between 40 and 79\)"):
        validate_ascvd_input(patient)

    patient['age'] = 80
    with pytest.raises(ValueError, match="age in ASCVD out of range: 80 \(expected between 40 and 79\)"):
        validate_ascvd_input(patient)


def test_validate_ascvd_input_invalid_sex():
    """Test invalid sex raises error."""
    patient = {
        'age': 60,
        'sex': 'Other',
        'race': 'White',
        'total_cholesterol': 200,
        'hdl': 50,
        'sbp': 120,
        'on_htn_meds': False,
        'smoker': False,
        'diabetes': False
    }
    with pytest.raises(ValueError, match="Invalid value for 'sex'"):
        validate_ascvd_input(patient)


def test_validate_ascvd_input_invalid_race():
    """Test invalid race raises error."""
    patient = {
        'age': 60,
        'sex': 'Male',
        'race': 'Asian',
        'total_cholesterol': 200,
        'hdl': 50,
        'sbp': 120,
        'on_htn_meds': False,
        'smoker': False,
        'diabetes': False
    }
    with pytest.raises(ValueError, match="Invalid value for 'race'"):
        validate_ascvd_input(patient)


def test_validate_ascvd_input_invalid_cholesterol():
    """Test cholesterol out of range."""
    patient = {
        'age': 60,
        'sex': 'Male',
        'race': 'White',
        'total_cholesterol': 50,
        'hdl': 50,
        'sbp': 120,
        'on_htn_meds': False,
        'smoker': False,
        'diabetes': False
    }
    with pytest.raises(ValueError, match="total_cholesterol in ASCVD out of range: 50 \(expected between 100 and 400\)"):
        validate_ascvd_input(patient)

    patient['total_cholesterol'] = 600
    with pytest.raises(ValueError, match="total_cholesterol in ASCVD out of range: 600 \(expected between 100 and 400\)"):
        validate_ascvd_input(patient)


def test_validate_ascvd_input_invalid_bp():
    """Test systolic BP out of range."""
    patient = {
        'age': 60,
        'sex': 'Male',
        'race': 'White',
        'total_cholesterol': 200,
        'hdl': 50,
        'sbp': 20,
        'on_htn_meds': False,
        'smoker': False,
        'diabetes': False
    }
    with pytest.raises(ValueError, match="sbp in ASCVD out of range: 20 \(expected between 70 and 250\)"):
        validate_ascvd_input(patient)

    patient['sbp'] = 260
    with pytest.raises(ValueError, match="sbp in ASCVD out of range: 260 \(expected between 70 and 250\)"):
        validate_ascvd_input(patient)


def test_validate_ascvd_input_invalid_binary_flags():
    """Test smoker, diabetes, on_htn_meds must be bool or 0/1."""
    patient = {
        'age': 60,
        'sex': 'Male',
        'race': 'White',
        'total_cholesterol': 200,
        'hdl': 50,
        'sbp': 120,
        'on_htn_meds': "yes",
        'smoker': False,
        'diabetes': False
    }
    with pytest.raises(ValueError, match="on_htn_meds must be 0 or 1"):
        validate_ascvd_input(patient)

    patient['on_htn_meds'] = 2
    with pytest.raises(ValueError, match="on_htn_meds must be 0 or 1"):
        validate_ascvd_input(patient)


# ========================
# BP CATEGORY VALIDATION
# ========================

def test_validate_bp_input_valid():
    """Test valid BP values."""
    assert validate_bp_input(120, 80) is None


def test_validate_bp_input_invalid_sbp():
    """Test systolic BP out of range."""
    with pytest.raises(ValueError, match="sbp \(60\) must be greater than dbp \(80\)"):
        validate_bp_input(60, 80)

    with pytest.raises(ValueError, match="sbp must be between 50 and 250, but got 300"):
        validate_bp_input(300, 80)


def test_validate_bp_input_invalid_dbp():
    """Test diastolic BP out of range."""
    with pytest.raises(ValueError, match="dbp must be between 40 and 150, but got 30"):
        validate_bp_input(120, 30)

    with pytest.raises(ValueError, match="dbp must be between 40 and 150, but got 200"):
        validate_bp_input(120, 200)


def test_validate_bp_input_sbp_leq_dbp():
    """Test systolic must be > diastolic."""
    with pytest.raises(ValueError, match="sbp \(120\) must be greater than dbp \(120\)"):
        validate_bp_input(120, 120)

    with pytest.raises(ValueError, match="sbp \(80\) must be greater than dbp \(90\)"):
        validate_bp_input(80, 90)


# ========================
# CHA₂DS₂-VASc VALIDATION
# ========================

def test_validate_cha2ds2vasc_input_valid():
    """Test valid CHA₂DS₂-VASc input."""
    data = {
        'chf': 0,
        'hypertension': 1,
        'age_ge_75': 0,
        'diabetes': 1,
        'stroke': 0,
        'vascular': 1,
        'age_65_74': 1,
        'female': 0
    }
    assert validate_cha2ds2vasc_input(data) is None


def test_validate_cha2ds2vasc_input_missing_fields():
    """Test missing required fields."""
    data = {'chf': 0}
    with pytest.raises(ValueError, match="Missing required fields"):
        validate_cha2ds2vasc_input(data)


def test_validate_cha2ds2vasc_input_invalid_binary():
    """Test all fields must be 0/1 or True/False."""
    data = {
        'chf': 0,
        'hypertension': 1,
        'age_ge_75': 0,
        'diabetes': 1,
        'stroke': 0,
        'vascular': 1,
        'age_65_74': 1,
        'female': "yes"
    }
    with pytest.raises(ValueError, match="must be 0/1 or True/False"):
        validate_cha2ds2vasc_input(data)

    data['female'] = 2
    with pytest.raises(ValueError, match="must be 0/1 or True/False"):
        validate_cha2ds2vasc_input(data)


# ========================
# ECG RHYTHM VALIDATION
# ========================

def test_validate_ecg_rhythm_input_valid():
    """Test valid ECG rhythm input."""
    data = {
        'rate': 75,
        'regular': True,
        'p_waves_present': True
    }
    assert validate_ecg_rhythm_input(data) is None


def test_validate_ecg_rhythm_input_invalid_rate():
    """Test heart rate out of range."""
    data = {'rate': 10, 'regular': True, 'p_waves_present': True}
    with pytest.raises(ValueError, match=r"out of range: 10 \(expected between 20 and 250\)"):
        validate_ecg_rhythm_input(data)

    data['rate'] = 300
    with pytest.raises(ValueError, match=r"out of range: 300 \(expected between 20 and 250\)"):
        validate_ecg_rhythm_input(data)


def test_validate_ecg_rhythm_input_invalid_types():
    """Test regular and p_waves_present must be bool or 0/1."""
    data = {'rate': 75, 'regular': "yes", 'p_waves_present': True}
    with pytest.raises(ValueError, match="regular must be boolean or 0/1"):
        validate_ecg_rhythm_input(data)

    data['regular'] = True
    data['p_waves_present'] = "no"
    with pytest.raises(ValueError, match="p_waves_present must be boolean or 0/1"):
        validate_ecg_rhythm_input(data)


# ========================
# ECG 12-LEAD VALIDATION
# ========================

def test_validate_ecg_12lead_input_valid():
    """Test valid 12-lead input."""
    data = {
        'qt_interval_ms': 400,
        'rr_interval_ms': 800,
        'pr_interval_ms': 160,
        'st_elevation': False,
        'lvh_criteria_met': False,
        'pathological_q_waves': False,
        't_wave_inversion': False
    }
    assert validate_ecg_12lead_input(data) is None


def test_validate_ecg_12lead_input_optional_ranges():
    """Test optional fields are validated if present."""
    data = {'qt_interval_ms': 200}
    with pytest.raises(ValueError, match="qt_interval_ms in 12-lead ECG out of range: 200 \(expected between 300 and 700\)"):
        validate_ecg_12lead_input(data)

    data['qt_interval_ms'] = 800
    with pytest.raises(ValueError, match="qt_interval_ms in 12-lead ECG out of range: 800 \(expected between 300 and 700\)"):
        validate_ecg_12lead_input(data)

    data = {'rr_interval_ms': 200}
    with pytest.raises(ValueError, match="rr_interval_ms in 12-lead ECG out of range: 200 \(expected between 300 and 1200\)"):
        validate_ecg_12lead_input(data)

    data['rr_interval_ms'] = 1500
    with pytest.raises(ValueError, match="rr_interval_ms in 12-lead ECG out of range: 1500 \(expected between 300 and 1200\)"):
        validate_ecg_12lead_input(data)

    data = {'pr_interval_ms': 100}
    with pytest.raises(ValueError, match="pr_interval_ms in 12-lead ECG out of range: 100 \(expected between 120 and 300\)"):
        validate_ecg_12lead_input(data)

    data['pr_interval_ms'] = 400
    with pytest.raises(ValueError, match="pr_interval_ms in 12-lead ECG out of range: 400 \(expected between 120 and 300\)"):
        validate_ecg_12lead_input(data)


def test_validate_ecg_12lead_input_boolean_flags():
    """Test boolean flags are valid."""
    for field in ['st_elevation', 'lvh_criteria_met', 'pathological_q_waves', 't_wave_inversion']:
        data = {field: "yes"}
        with pytest.raises(ValueError, match=f"{field} must be True or False"):
            validate_ecg_12lead_input(data)


def test_validate_ecg_12lead_input_missing_leads():
    """Test required leads when findings are present."""
    data = {'st_elevation': True}
    with pytest.raises(ValueError, match="st_elevation_leads is required when st_elevation is True"):
        validate_ecg_12lead_input(data)

    data = {'pathological_q_waves': True}
    with pytest.raises(ValueError, match="q_wave_leads is required when pathological_q_waves is True"):
        validate_ecg_12lead_input(data)


def test_validate_ecg_12lead_input_non_string_leads():
    """Test lead fields are strings."""
    data = {
        'st_elevation': True,
        'st_elevation_leads': 123
    }
    with pytest.raises(ValueError, match="st_elevation_leads must be a string"):
        validate_ecg_12lead_input(data)

    data = {
        'pathological_q_waves': True,
        'q_wave_leads': 999
    }
    with pytest.raises(ValueError, match="q_wave_leads must be a string"):
        validate_ecg_12lead_input(data)