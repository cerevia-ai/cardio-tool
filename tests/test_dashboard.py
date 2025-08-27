# tests/test_dashboard_logic.py
import pytest
from app.calculators.ascvd import ascvd
from app.calculators.bp_category import bp_category
from app.calculators.cha2ds2vasc import cha2ds2vasc
from app.calculators.ecg_interpret import (
    interpret_rhythm,
    interpret_12lead_findings,
    interpret_ecg_comprehensive,
)
from app.validators.patient_input import (
    validate_ascvd_input,
    validate_bp_input,
    validate_cha2ds2vasc_input,
    validate_ecg_rhythm_input,
    validate_ecg_12lead_input,
)

class TestDashboardLogic:
    """
    Test the logic used in the Streamlit dashboard.
    These tests verify that the underlying functions behave as expected.
    """

    # -----------------------------
    # ASCVD Risk Calculator Tests
    # -----------------------------

    def test_ascvd_low_risk(self):
        data = {
            "age": 55,
            "sex": "Male",
            "race": "White",
            "total_cholesterol": 180,
            "hdl": 50,
            "sbp": 120,
            "on_htn_meds": False,
            "smoker": False,
            "diabetes": False,
        }
        validate_ascvd_input(data)
        risk = ascvd(data)
        assert 0.0 <= risk < 0.05

    def test_ascvd_intermediate_risk(self):
        data = {
            "age": 58,
            "sex": "Female",
            "race": "White",
            "total_cholesterol": 220,
            "hdl": 50,
            "sbp": 130,
            "on_htn_meds": False,
            "smoker": False,
            "diabetes": True,  # Only significant risk factor
        }
        validate_ascvd_input(data)
        risk = ascvd(data)
        assert 0.075 <= risk < 0.20

    def test_ascvd_high_risk(self):
        data = {
            "age": 70,
            "sex": "Female",
            "race": "Black",
            "total_cholesterol": 260,
            "hdl": 30,
            "sbp": 160,
            "on_htn_meds": True,
            "smoker": True,
            "diabetes": True,
        }
        validate_ascvd_input(data)
        risk = ascvd(data)
        assert risk >= 0.20

    def test_ascvd_invalid_input(self):
        data = {
            "age": 30,  # too young
            "sex": "Male",
            "race": "White",
            "total_cholesterol": 200,
            "hdl": 50,
            "sbp": 120,
            "on_htn_meds": False,
            "smoker": False,
            "diabetes": False,
        }
        with pytest.raises(ValueError):
            validate_ascvd_input(data)

    # -----------------------------
    # BP Category Tests
    # -----------------------------

    def test_bp_normal(self):
        category = bp_category(110, 70)
        assert category == "🟢 Normal"

    def test_bp_elevated(self):
        category = bp_category(125, 70)
        assert category == "🟡 Elevated"

    def test_bp_stage1_hypertension(self):
        category = bp_category(135, 85)
        assert category == "🟠 Stage 1 Hypertension"

    def test_bp_stage2_hypertension(self):
        category = bp_category(150, 95)
        assert category == "🔴 Stage 2 Hypertension"

    def test_bp_invalid_input(self):
        with pytest.raises(ValueError):
            validate_bp_input(300, 80)

    # -----------------------------
    # CHA₂DS₂-VASc Tests
    # -----------------------------

    def test_cha2ds2vasc_low_risk(self):
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
        validate_cha2ds2vasc_input(data)
        score = cha2ds2vasc(data)
        assert score == 0

    def test_cha2ds2vasc_high_risk(self):
        data = {
            "chf": 1,
            "hypertension": 1,
            "age_ge_75": 1,
            "diabetes": 1,
            "stroke": 1,
            "vascular": 0,
            "age_65_74": 0,
            "female": 1,
        }
        validate_cha2ds2vasc_input(data)
        score = cha2ds2vasc(data)
        assert score >= 2

    # -----------------------------
    # ECG Interpretation Tests
    # -----------------------------

    def test_ecg_rhythm_sinus_tachycardia(self):
        rhythm = interpret_rhythm(110, True, True)
        assert rhythm == "Sinus tachycardia"

    def test_ecg_rhythm_atrial_fibrillation(self):
        rhythm = interpret_rhythm(110, False, False)
        assert rhythm == "Atrial fibrillation"

    def test_ecg_12lead_st_elevation(self):
        data = {
            "st_elevation": True,
            "st_elevation_leads": "V1-V4"
        }
        validate_ecg_12lead_input(data)
        findings = interpret_12lead_findings(data)
        assert any("STEMI" in f for f in findings["findings"])
        assert findings["risk_level"] == "High"

    def test_ecg_12lead_qt_prolongation(self):
        data = {
            "qt_interval_ms": 520,
            "rr_interval_ms": 1000
        }
        validate_ecg_12lead_input(data)
        findings = interpret_12lead_findings(data)
        assert any("Torsades" in f for f in findings["findings"])

    def test_ecg_comprehensive(self):
        rhythm_data = {"rate": 75, "regular": True, "p_waves_present": True}
        ecg_data = {**rhythm_data, "st_elevation": False}
        comprehensive = interpret_ecg_comprehensive(ecg_data)
        assert comprehensive["rhythm"]["interpretation"] == "Normal sinus rhythm"
        assert comprehensive["overall_risk"] in ["Low", "Moderate", "High"]

    def test_ecg_invalid_rhythm_input(self):
        data = {"rate": -50}
        with pytest.raises(ValueError):
            validate_ecg_rhythm_input(data)

    def test_ecg_invalid_12lead_input(self):
        data = {"qt_interval_ms": "invalid"}
        with pytest.raises(ValueError):
            validate_ecg_12lead_input(data)