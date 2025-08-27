# tests/test_bp_category.py
import pytest

from app.calculators.bp_category import bp_category
from app.validators.patient_input import validate_bp_input

# ------------------------
# Normal
# ------------------------

@pytest.mark.parametrize("sbp,dbp", [
    (110, 70),
    (119, 79),
    (100, 60),
])
def test_bp_category_normal(sbp, dbp):
    """SBP <120 AND DBP <80 → Normal"""
    assert bp_category(sbp, dbp) == "🟢 Normal"


# ------------------------
# Elevated
# ------------------------

@pytest.mark.parametrize("sbp,dbp", [
    (120, 70),
    (125, 75),
    (129, 79),
])
def test_bp_category_elevated(sbp, dbp):
    """SBP 120–129 AND DBP <80 → Elevated"""
    assert bp_category(sbp, dbp) == "🟡 Elevated"


# ------------------------
# Stage 1 Hypertension
# ------------------------

@pytest.mark.parametrize("sbp,dbp", [
    (130, 79),  # SBP >=130, DBP <80
    (135, 75),  # SBP 130–139
    (125, 85),  # DBP 80–89
    (135, 85),  # Both in Stage 1 range
    (139, 89),
])
def test_bp_category_stage_1_hypertension(sbp, dbp):
    """SBP 130–139 OR DBP 80–89 → Stage 1 (if not Stage 2)"""
    assert bp_category(sbp, dbp) == "🟠 Stage 1 Hypertension"


# ------------------------
# Stage 2 Hypertension
# ------------------------

@pytest.mark.parametrize("sbp,dbp", [
    (140, 70),   # SBP >=140
    (150, 75),
    (130, 90),   # DBP >=90
    (140, 90),   # Both high
    (160, 100),
])
def test_bp_category_stage_2_hypertension(sbp, dbp):
    """SBP >=140 OR DBP >=90 → Stage 2"""
    assert bp_category(sbp, dbp) == "🔴 Stage 2 Hypertension"


# ------------------------
# Boundary Tests
# ------------------------

def test_bp_category_boundary_normal_to_elevated():
    """119/79 → Normal, 120/79 → Elevated"""
    assert bp_category(119, 79) == "🟢 Normal"
    assert bp_category(120, 79) == "🟡 Elevated"

def test_bp_category_boundary_elevated_to_stage1():
    """129/79 → Elevated, 130/79 → Stage 1"""
    assert bp_category(129, 79) == "🟡 Elevated"
    assert bp_category(130, 79) == "🟠 Stage 1 Hypertension"

def test_bp_category_boundary_stage1_to_stage2():
    """139/89 → Stage 1, 140/89 → Stage 2"""
    assert bp_category(139, 89) == "🟠 Stage 1 Hypertension"
    assert bp_category(140, 89) == "🔴 Stage 2 Hypertension"


# ------------------------
# Input Validation (if you add it later)
# ------------------------

def test_bp_category_accepts_float_inputs():
    """Ensure bp_category accepts valid float values for SBP and DBP."""
    # This should be Elevated: SBP in 120–129, DBP < 80
    assert bp_category(125.7, 79.9) == "🟡 Elevated"

    # This should be Stage 1: DBP >= 80
    assert bp_category(120.5, 80.2) == "🟠 Stage 1 Hypertension"

    # Edge: both just above cutoff
    assert bp_category(130.0, 80.0) == "🟠 Stage 1 Hypertension"

@pytest.mark.parametrize("sbp,dbp", [
    ("120", 80),
    (120, "80"),
    ("120", "80"),
    (None, 80),
    (120, True),
    ([120], 80),
    ({"sbp": 120}, 80),
])
def test_bp_category_rejects_non_numeric_types(sbp, dbp):
    """Ensure non-numeric types (str, None, bool, etc.) raise ValueError."""
    with pytest.raises(ValueError, match=r"must be a number"):
        bp_category(sbp, dbp)

def test_bp_category_extreme_but_valid():
    """Extremely high but valid blood pressures should still be classified correctly."""
    assert bp_category(200, 120) == "🔴 Stage 2 Hypertension"
    assert bp_category(250, 150) == "🔴 Stage 2 Hypertension"
    assert bp_category(140, 90) == "🔴 Stage 2 Hypertension"