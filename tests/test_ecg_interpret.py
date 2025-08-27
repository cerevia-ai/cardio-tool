# tests/test_ecg_interpret.py

import pytest
from app.calculators.ecg_interpret import (
    interpret_rhythm,
    ecg_interpret_detailed,
    interpret_12lead_findings,
    interpret_ecg_comprehensive,
)
from app.validators.patient_input import (
    validate_ecg_rhythm_input,
    validate_ecg_12lead_input,
)
from unittest.mock import patch


# -----------------------------
# 1. TEST: Basic Rhythm Interpretation
# -----------------------------

class TestECGInterpret:
    """Test basic rhythm interpretation logic."""

    def test_normal_sinus_rhythm(self):
        assert interpret_rhythm(75, True, True) == "Normal sinus rhythm"

    def test_sinus_bradycardia(self):
        assert interpret_rhythm(50, True, True) == "Sinus bradycardia"
        assert interpret_rhythm(58, True, True) == "Sinus bradycardia"

    def test_sinus_tachycardia(self):
        assert interpret_rhythm(110, True, True) == "Sinus tachycardia"
        assert interpret_rhythm(101, True, True) == "Sinus tachycardia"

    def test_atrial_fibrillation(self):
        assert interpret_rhythm(115, False, False) == "Atrial fibrillation"
        assert interpret_rhythm(130, False, False) == "Atrial fibrillation"

    def test_uncertain_tachycardia(self):
        assert interpret_rhythm(110, True, False) == "Tachycardia, uncertain rhythm"
        assert interpret_rhythm(110, False, True) == "Tachycardia, uncertain rhythm"

    def test_irregular_without_pwaves(self):
        assert interpret_rhythm(80, False, False) == "Possible AFib or arrhythmia"

    def test_undetermined_rhythm(self):
        assert interpret_rhythm(80, True, False) == "Undetermined"


# -----------------------------
# 2. TEST: Detailed Rhythm Interpretation
# -----------------------------

class TestECGInterpretDetailed:
    """Test detailed ECG rhythm interpretation with validation and notes."""

    def test_valid_normal_rhythm(self):
        data = {"rate": 75, "regular": True, "p_waves_present": True}
        result = ecg_interpret_detailed(data)
        assert result["rhythm"] == "Normal sinus rhythm"
        assert result["confidence"] == "High"
        assert "athletic training" not in result["notes"]

    def test_sinus_tachycardia_with_notes(self):
        data = {"rate": 110, "regular": True, "p_waves_present": True}
        result = ecg_interpret_detailed(data)
        assert result["rhythm"] == "Sinus tachycardia"
        assert "Evaluate for fever, pain, anemia" in result["notes"]

    def test_atrial_fibrillation_notes(self):
        data = {"rate": 120, "regular": False, "p_waves_present": False}
        result = ecg_interpret_detailed(data)
        assert result["rhythm"] == "Atrial fibrillation"
        assert "Confirm with 12-lead ECG" in result["notes"]

    def test_invalid_rate(self):
        result = ecg_interpret_detailed({"rate": -50})
        assert result["rhythm"] == "Invalid input"
        assert result["confidence"] == "Low"
        assert "positive integer" in result["notes"]

        result = ecg_interpret_detailed({"rate": None})
        assert result["rhythm"] == "Invalid input"

    def test_missing_optional_fields(self):
        """When optional fields are missing, defaults lead to 'Possible AFib or arrhythmia'."""
        data = {"rate": 60}
        result = ecg_interpret_detailed(data)
        assert result["rhythm"] == "Possible AFib or arrhythmia"
        assert result["confidence"] == "Low"
        assert "Irregular rhythm without clear P-waves" in result["notes"]


# -----------------------------
# 3. TEST: 12-Lead Findings
# -----------------------------

class TestInterpret12LeadFindings:
    """Test 12-lead ECG findings interpretation."""

    def test_st_elevation(self):
        data = {"st_elevation": True, "st_elevation_leads": "II, III, aVF"}
        result = interpret_12lead_findings(data)
        assert any("ST elevation in II, III, aVF" in f for f in result["findings"])
        assert result["risk_level"] == "High"

    def test_qtc_prolongation_high_risk(self):
        # QTc = 520 / sqrt(1.0) = 520 → High risk
        data = {"qt_interval_ms": 520, "rr_interval_ms": 1000}
        result = interpret_12lead_findings(data)
        assert any("QTc = 520 ms → High risk of Torsades" in f for f in result["findings"])
        assert result["risk_level"] == "High"

    def test_qtc_prolongation_moderate(self):
        # QTc = 460 / sqrt(0.81) = 460 / 0.9 ≈ 511 → Still high risk
        data = {"qt_interval_ms": 460, "rr_interval_ms": 810}
        result = interpret_12lead_findings(data)
        assert any("High risk of Torsades" in f for f in result["findings"])
        assert result["risk_level"] == "High"

    def test_qtc_normal(self):
        # QTc = 400 / sqrt(0.81) ≈ 444 → Normal
        data = {"qt_interval_ms": 400, "rr_interval_ms": 810}
        result = interpret_12lead_findings(data)
        assert not any("QTc" in f for f in result["findings"])

    def test_lvh_criteria(self):
        data = {"lvh_criteria_met": True}
        result = interpret_12lead_findings(data)
        assert any("LVH by voltage criteria" in f for f in result["findings"])
        assert result["risk_level"] == "Moderate"

    def test_pathological_q_waves(self):
        data = {"pathological_q_waves": True, "q_wave_leads": "V1-V3"}
        result = interpret_12lead_findings(data)
        assert any("Pathological Q waves in V1-V3" in f for f in result["findings"])
        assert result["risk_level"] == "High"

    def test_pr_interval_av_block(self):
        data = {"pr_interval_ms": 220}
        result = interpret_12lead_findings(data)
        assert any("PR = 220 ms → First-degree AV block" in f for f in result["findings"])

    def test_t_wave_inversion(self):
        data = {"t_wave_inversion": True}
        result = interpret_12lead_findings(data)
        assert any("T-wave inversion → Possible ischemia" in f for f in result["findings"])

    def test_multiple_findings_risk_level(self):
        data = {
            "st_elevation": True,
            "st_elevation_leads": "V2-V4",
            "lvh_criteria_met": True,
            "t_wave_inversion": True
        }
        result = interpret_12lead_findings(data)
        assert result["risk_level"] == "High"
        assert len(result["findings"]) >= 3

    def test_no_findings(self):
        result = interpret_12lead_findings({})
        assert result["findings"] == []
        assert result["risk_level"] == "Low"
        assert len(result["recommendations"]) == 4


# -----------------------------
# 4. TEST: Comprehensive Interpretation
# -----------------------------

class TestInterpretECGComprehensive:
    """Test combined ECG interpretation."""

    def test_full_comprehensive_normal(self):
        data = {
            "rate": 75,
            "regular": True,
            "p_waves_present": True,
            "st_elevation": False,
            "lvh_criteria_met": False,
            "pathological_q_waves": False,
            "t_wave_inversion": False,
            "pr_interval_ms": 160
        }
        result = interpret_ecg_comprehensive(data)
        assert result["rhythm"]["interpretation"] == "Normal sinus rhythm"
        assert result["overall_risk"] == "Low"
        assert "Correlate with clinical picture" in result["recommendations"]

    def test_high_risk_case(self):
        data = {
            "rate": 120,
            "regular": False,
            "p_waves_present": False,
            "st_elevation": True,
            "st_elevation_leads": "V1-V6",
            "qt_interval_ms": 550,
            "rr_interval_ms": 1000,
            "lvh_criteria_met": True
        }
        result = interpret_ecg_comprehensive(data)
        assert result["rhythm"]["interpretation"] == "Atrial fibrillation"
        assert any("ST elevation in V1-V6" in f for f in result["12_lead_findings"])
        assert any("QTc = 550 ms" in f for f in result["12_lead_findings"])
        assert result["overall_risk"] == "High"


# -----------------------------
# 5. TEST: Input Validation Integration
# -----------------------------

class TestECGValidationIntegration:
    @patch("app.calculators.ecg_interpret.validate_ecg_rhythm_input")
    def test_detailed_calls_validator(self, mock_validate):
        ecg_interpret_detailed({"rate": 70})
        mock_validate.assert_called_once_with({"rate": 70})

    @patch("app.calculators.ecg_interpret.validate_ecg_12lead_input")
    def test_12lead_calls_validator(self, mock_validate):
        data = {"st_elevation": False}
        interpret_12lead_findings(data)
        mock_validate.assert_called_once_with(data)

    @patch("app.calculators.ecg_interpret.validate_ecg_rhythm_input")
    @patch("app.calculators.ecg_interpret.validate_ecg_12lead_input")
    def test_comprehensive_calls_both_validators(self, mock_12lead, mock_rhythm):
        data = {
            "rate": 70,
            "regular": True,
            "p_waves_present": True,
            "st_elevation": False
        }
        interpret_ecg_comprehensive(data)
        mock_rhythm.assert_called_once_with({
            "rate": 70,
            "regular": True,
            "p_waves_present": True
        })
        mock_12lead.assert_called_once_with(data)

    def test_validation_error_propagation(self):
        """Ensure ecg_interpret_detailed handles validation errors gracefully."""
        with patch("app.calculators.ecg_interpret.validate_ecg_rhythm_input") as mock:
            mock.side_effect = ValueError("Invalid rate")
            result = ecg_interpret_detailed({"rate": -10})
            assert result["rhythm"] == "Invalid input"
            assert "Invalid rate" in result["notes"]