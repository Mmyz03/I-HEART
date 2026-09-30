"""
Automated Test Suite for Input Validation & Clinical Boundary Enforcement
AI-Based Explainable Health Risk Prediction System (I-HEART)
Tests schema constraints, missing fields, type errors, impossible clinical values,
boundary conditions, and safe rejection without application crashes.
"""

import sys
from pathlib import Path
# Ensure backend is on sys.path
from pydantic import ValidationError

# Ensure backend is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from schemas import (
    UnifiedPatientProfile,
    Demographics,
    PhysicalMeasurements,
    VitalSigns,
    LaboratoryData,
    LifestyleData,
    MedicalHistory,
)
from integration.emr_schemas import (
    MockEMRPayload,
    EMRPatientIdentity,
    EMRPhysicalMeasurements,
    EMRClinicalVitals,
    EMRLaboratoryResults,
    EMRLifestyleHistory,
    EMRDiagnosesAndHistory,
)


def get_base_valid_profile_dict():
    return {
        "patient_id": "TEST-VAL-001",
        "demographics": {"age": 45, "gender": "Female"},
        "physical": {"height_cm": 165.0, "weight_kg": 65.0, "bmi": 23.9},
        "vitals": {"systolic_bp": 120, "diastolic_bp": 80, "heart_rate": 72},
        "laboratory": {"glucose": 95.0},
        "lifestyle": {
            "smoking": "Never",
            "physical_activity": "Moderate",
            "alcohol": "None",
        },
        "medical_history": {
            "hypertension": False,
            "existing_diabetes": False,
            "family_history_diabetes": False,
            "family_history_cvd": False,
        },
    }


# =============================================================================
# 1. Demographics Validation
# =============================================================================

def test_demographics_valid():
    d = Demographics(age=35, gender="Male")
    assert d.age == 35
    assert d.gender == "Male"


def test_demographics_age_boundary_valid():
    d_min = Demographics(age=1, gender="Female")
    assert d_min.age == 1
    d_max = Demographics(age=125, gender="Male")
    assert d_max.age == 125


def test_demographics_age_boundary_invalid():
    # Negative age
    try:
        Demographics(age=-1, gender="Male")
        assert False, "Should reject negative age"
    except ValidationError:
        pass

    # Zero age
    try:
        Demographics(age=0, gender="Male")
        assert False, "Should reject zero age"
    except ValidationError:
        pass

    # Impossible high age
    try:
        Demographics(age=126, gender="Female")
        assert False, "Should reject age > 125"
    except ValidationError:
        pass


def test_demographics_gender_empty():
    try:
        Demographics(age=30, gender="")
        assert False, "Should reject empty gender"
    except ValidationError:
        pass


def test_demographics_wrong_types():
    try:
        Demographics(age="thirty", gender="Male")
        assert False, "Should reject string age"
    except ValidationError:
        pass


# =============================================================================
# 2. Physical Measurements & BMI Consistency
# =============================================================================

def test_physical_valid():
    # 170cm, 70kg -> expected BMI = 70 / (1.7^2) = 24.22
    p = PhysicalMeasurements(height_cm=170.0, weight_kg=70.0, bmi=24.2)
    assert p.height_cm == 170.0
    assert p.weight_kg == 70.0
    assert p.bmi == 24.2


def test_physical_boundaries():
    # Min boundaries (height 40cm, weight 15kg, BMI 9.4 -> consistent with 15/(0.4^2)=93.75, let's pick 40cm, 15kg, BMI=9.4? no, expected=15/0.16=93.75)
    # Let's test boundary values with consistent BMI:
    # 100cm, 15kg -> expected BMI = 15.0
    p1 = PhysicalMeasurements(height_cm=100.0, weight_kg=15.0, bmi=15.0)
    assert p1.weight_kg == 15.0

    # Height too small
    try:
        PhysicalMeasurements(height_cm=39.0, weight_kg=50.0, bmi=20.0)
        assert False, "Should reject height < 40"
    except ValidationError:
        pass

    # Height too large
    try:
        PhysicalMeasurements(height_cm=261.0, weight_kg=80.0, bmi=20.0)
        assert False, "Should reject height > 260"
    except ValidationError:
        pass

    # Weight too small
    try:
        PhysicalMeasurements(height_cm=160.0, weight_kg=14.0, bmi=20.0)
        assert False, "Should reject weight < 15"
    except ValidationError:
        pass

    # Weight too large
    try:
        PhysicalMeasurements(height_cm=180.0, weight_kg=351.0, bmi=30.0)
        assert False, "Should reject weight > 350"
    except ValidationError:
        pass


def test_physical_bmi_inconsistency_rejection():
    # Height 180cm, Weight 60kg -> Expected BMI ~ 18.5
    # Providing inconsistent BMI of 40.0 should be rejected by model_validator
    try:
        PhysicalMeasurements(height_cm=180.0, weight_kg=60.0, bmi=40.0)
        assert False, "Should reject inconsistent BMI (> 5.0 discrepancy)"
    except ValidationError as e:
        assert "inconsistent" in str(e).lower()


# =============================================================================
# 3. Vital Signs Validation
# =============================================================================

def test_vitals_valid():
    v = VitalSigns(systolic_bp=120, diastolic_bp=80, heart_rate=72)
    assert v.systolic_bp == 120
    assert v.diastolic_bp == 80
    assert v.heart_rate == 72


def test_vitals_boundaries():
    # Boundary valid: min valid SBP 60, DBP 40, HR 35 (with SBP > DBP)
    v_min = VitalSigns(systolic_bp=65, diastolic_bp=40, heart_rate=35)
    assert v_min.systolic_bp == 65

    # Out of range SBP
    try:
        VitalSigns(systolic_bp=59, diastolic_bp=40, heart_rate=70)
        assert False, "Should reject SBP < 60"
    except ValidationError:
        pass

    try:
        VitalSigns(systolic_bp=261, diastolic_bp=100, heart_rate=70)
        assert False, "Should reject SBP > 260"
    except ValidationError:
        pass

    # Out of range DBP
    try:
        VitalSigns(systolic_bp=120, diastolic_bp=39, heart_rate=70)
        assert False, "Should reject DBP < 40"
    except ValidationError:
        pass

    try:
        VitalSigns(systolic_bp=180, diastolic_bp=161, heart_rate=70)
        assert False, "Should reject DBP > 160"
    except ValidationError:
        pass

    # Out of range Heart Rate
    try:
        VitalSigns(systolic_bp=120, diastolic_bp=80, heart_rate=34)
        assert False, "Should reject HR < 35"
    except ValidationError:
        pass

    try:
        VitalSigns(systolic_bp=120, diastolic_bp=80, heart_rate=221)
        assert False, "Should reject HR > 220"
    except ValidationError:
        pass


def test_vitals_diastolic_greater_than_systolic():
    # Clinically impossible: Diastolic BP >= Systolic BP
    try:
        VitalSigns(systolic_bp=110, diastolic_bp=120, heart_rate=75)
        assert False, "Should reject DBP >= SBP"
    except ValidationError as e:
        assert "strictly lower than" in str(e)


def test_vitals_equal_blood_pressure():
    # Clinically impossible: SBP == DBP
    try:
        VitalSigns(systolic_bp=100, diastolic_bp=100, heart_rate=75)
        assert False, "Should reject SBP == DBP"
    except ValidationError as e:
        assert "strictly lower than" in str(e)


# =============================================================================
# 4. Laboratory Data Validation
# =============================================================================

def test_laboratory_optional_fields_none():
    # Glucose is required; other lipid and HbA1c fields can be None
    lab = LaboratoryData(glucose=100.0)
    assert lab.glucose == 100.0
    assert lab.hba1c is None
    assert lab.total_cholesterol is None
    assert lab.hdl is None
    assert lab.ldl is None
    assert lab.triglycerides is None


def test_laboratory_missing_required_glucose():
    try:
        LaboratoryData()
        assert False, "Should reject missing glucose"
    except ValidationError:
        pass


def test_laboratory_glucose_boundaries():
    # Valid boundaries: 30.0 to 500.0
    l_min = LaboratoryData(glucose=30.0)
    assert l_min.glucose == 30.0
    l_max = LaboratoryData(glucose=500.0)
    assert l_max.glucose == 500.0

    # Below min
    try:
        LaboratoryData(glucose=29.9)
        assert False, "Should reject glucose < 30"
    except ValidationError:
        pass

    # Above max
    try:
        LaboratoryData(glucose=500.1)
        assert False, "Should reject glucose > 500"
    except ValidationError:
        pass


def test_laboratory_optional_field_boundaries():
    # HbA1c range: 3.0 to 18.0
    try:
        LaboratoryData(glucose=100.0, hba1c=2.9)
        assert False, "Should reject HbA1c < 3.0"
    except ValidationError:
        pass

    try:
        LaboratoryData(glucose=100.0, hba1c=18.1)
        assert False, "Should reject HbA1c > 18.0"
    except ValidationError:
        pass

    # Total cholesterol range: 50.0 to 500.0
    try:
        LaboratoryData(glucose=100.0, total_cholesterol=49.0)
        assert False, "Should reject TC < 50"
    except ValidationError:
        pass


# =============================================================================
# 5. Full UnifiedPatientProfile Validation
# =============================================================================

def test_unified_profile_valid():
    data = get_base_valid_profile_dict()
    profile = UnifiedPatientProfile(**data)
    assert profile.patient_id == "TEST-VAL-001"
    assert profile.demographics.age == 45
    assert profile.physical.bmi == 23.9


def test_unified_profile_missing_sections():
    data = get_base_valid_profile_dict()
    del data["demographics"]
    try:
        UnifiedPatientProfile(**data)
        assert False, "Should reject missing demographics section"
    except ValidationError:
        pass


def test_unified_profile_empty_patient_id():
    data = get_base_valid_profile_dict()
    data["patient_id"] = ""
    try:
        UnifiedPatientProfile(**data)
        assert False, "Should reject empty patient_id"
    except ValidationError:
        pass


def test_unified_profile_wrong_nested_types():
    data = get_base_valid_profile_dict()
    data["vitals"]["systolic_bp"] = "high"
    try:
        UnifiedPatientProfile(**data)
        assert False, "Should reject string systolic_bp"
    except ValidationError:
        pass


# =============================================================================
# 6. EMR Schemas Validation
# =============================================================================

def test_emr_vitals_bp_consistency():
    try:
        EMRClinicalVitals(systolic_bp=90, diastolic_bp=100, heart_rate=70)
        assert False, "EMR should reject DBP >= SBP"
    except ValidationError:
        pass


def test_emr_identity_boundary_age():
    try:
        EMRPatientIdentity(mrn="M-1", age=150, gender="Male")
        assert False, "EMR should reject age > 125"
    except ValidationError:
        pass


# =============================================================================
# Runner
# =============================================================================

TESTS = [
    test_demographics_valid,
    test_demographics_age_boundary_valid,
    test_demographics_age_boundary_invalid,
    test_demographics_gender_empty,
    test_demographics_wrong_types,
    test_physical_valid,
    test_physical_boundaries,
    test_physical_bmi_inconsistency_rejection,
    test_vitals_valid,
    test_vitals_boundaries,
    test_vitals_diastolic_greater_than_systolic,
    test_vitals_equal_blood_pressure,
    test_laboratory_optional_fields_none,
    test_laboratory_missing_required_glucose,
    test_laboratory_glucose_boundaries,
    test_laboratory_optional_field_boundaries,
    test_unified_profile_valid,
    test_unified_profile_missing_sections,
    test_unified_profile_empty_patient_id,
    test_unified_profile_wrong_nested_types,
    test_emr_vitals_bp_consistency,
    test_emr_identity_boundary_age,
]


def run_tests():
    print("=" * 70)
    print("RUNNING INPUT VALIDATION & CLINICAL BOUNDARY TEST SUITE")
    print("=" * 70)
    passed = 0
    failed = 0
    for t in TESTS:
        try:
            t()
            print(f"PASS: {t.__name__}")
            passed += 1
        except Exception as exc:
            print(f"FAIL: {t.__name__} - {str(exc)}")
            failed += 1

    print("=" * 70)
    print(f"INPUT VALIDATION RESULTS: {passed} PASSED, {failed} FAILED (TOTAL {len(TESTS)})")
    print("=" * 70)
    return passed, failed, 0


if __name__ == "__main__":
    passed, failed, skipped = run_tests()
    if failed > 0:
        sys.exit(1)
