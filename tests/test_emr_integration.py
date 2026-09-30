"""
Automated Test Suite for Hospital / EMR Integration Foundation
Verifies EMR schemas, EMRAdapter normalization, validation constraints,
privacy logging safeguards, and pipeline continuity.
"""

import sys
import logging
import io
from pathlib import Path
from pydantic import ValidationError

# Ensure project root and backend are in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from schemas import UnifiedPatientProfile
from services.prediction_service import analyze_unified_patient
from integration.emr_schemas import (
    MockEMRPayload,
    EMRPatientIdentity,
    EMRPhysicalMeasurements,
    EMRClinicalVitals,
    EMRLaboratoryResults,
    EMRLifestyleHistory,
    EMRDiagnosesAndHistory,
)
from integration.emr_adapter import EMRAdapter
from integration.emr_service import process_emr_patient


def get_sample_emr_payload():
    """Returns a valid synthetic EMR patient payload for testing."""
    return MockEMRPayload(
        resource_type="MockEMRPatientRecord",
        emr_system_id="HOSP-GENERAL-01",
        patient_identity=EMRPatientIdentity(
            mrn="EMR-TEST-001",
            age=52,
            gender="Male"
        ),
        physical_measurements=EMRPhysicalMeasurements(
            height_cm=175.0,
            weight_kg=82.0,
            bmi=None  # Triggers automatic calculation
        ),
        clinical_vitals=EMRClinicalVitals(
            systolic_bp=138,
            diastolic_bp=88,
            heart_rate=76
        ),
        laboratory_results=EMRLaboratoryResults(
            fasting_glucose=118.0,
            hba1c=6.1,
            total_cholesterol=215.0,
            hdl=44.0,
            ldl=138.0,
            triglycerides=165.0
        ),
        lifestyle_history=EMRLifestyleHistory(
            smoking_status="Current Smoker",
            physical_activity_level="Moderate",
            alcohol_consumption="Moderate"
        ),
        diagnoses_and_history=EMRDiagnosesAndHistory(
            hypertension_diagnosed=True,
            existing_diabetes_diagnosed=False,
            family_history_diabetes=True,
            family_history_cvd=True
        )
    )


def test_1_valid_mock_emr_payload():
    """1. Test that valid mock EMR payload instantiates cleanly."""
    payload = get_sample_emr_payload()
    assert payload.emr_system_id == "HOSP-GENERAL-01"
    assert payload.patient_identity.mrn == "EMR-TEST-001"
    assert payload.patient_identity.age == 52
    assert payload.clinical_vitals.systolic_bp == 138


def test_2_emr_to_internal_schema_mapping():
    """2. Test EMR -> UnifiedPatientProfile mapping and BMI calculation."""
    payload = get_sample_emr_payload()
    unified = EMRAdapter.emr_to_unified(payload)

    assert isinstance(unified, UnifiedPatientProfile)
    assert unified.patient_id == "EMR-TEST-001"
    assert unified.demographics.age == 52
    assert unified.demographics.gender == "Male"
    # Height 175cm, Weight 82kg -> BMI: 82 / (1.75^2) = 26.7755 -> 26.8
    assert unified.physical.bmi == 26.8
    assert unified.vitals.systolic_bp == 138
    assert unified.laboratory.glucose == 118.0
    assert unified.lifestyle.smoking == "Current"
    assert unified.medical_history.hypertension is True


def test_3_missing_required_fields():
    """3. Test that missing required fields in EMR payload raise validation errors."""
    # Missing fasting_glucose
    try:
        EMRLaboratoryResults()  # fasting_glucose is required
        assert False, "Should have raised ValidationError for missing fasting_glucose"
    except ValidationError:
        pass

    # Missing patient age
    try:
        EMRPatientIdentity(mrn="P-01", gender="Female")
        assert False, "Should have raised ValidationError for missing age"
    except ValidationError:
        pass


def test_4_invalid_field_types():
    """4. Test that invalid data types raise validation errors."""
    try:
        EMRPatientIdentity(mrn="P-01", age="fifty-two", gender="Male")
        assert False, "Should have raised ValidationError for string age"
    except ValidationError:
        pass

    try:
        EMRClinicalVitals(systolic_bp="high", diastolic_bp=80, heart_rate=72)
        assert False, "Should have raised ValidationError for string systolic_bp"
    except ValidationError:
        pass


def test_5_invalid_clinical_values():
    """5. Test that out-of-range clinical values raise validation errors."""
    # Systolic BP < 60
    try:
        EMRClinicalVitals(systolic_bp=30, diastolic_bp=80, heart_rate=72)
        assert False, "Should have raised ValidationError for out-of-bounds systolic_bp"
    except ValidationError:
        pass

    # Fasting glucose > 500
    try:
        EMRLaboratoryResults(fasting_glucose=650.0)
        assert False, "Should have raised ValidationError for glucose > 500"
    except ValidationError:
        pass

    # Age > 125
    try:
        EMRPatientIdentity(mrn="P-01", age=150, gender="Male")
        assert False, "Should have raised ValidationError for age > 125"
    except ValidationError:
        pass


def test_6_existing_manual_prediction_flow_still_works():
    """6. Test that existing manual frontend intake contract continues to work."""
    payload = get_sample_emr_payload()
    unified = EMRAdapter.emr_to_unified(payload)

    # Call standard prediction orchestrator directly
    res = analyze_unified_patient(unified)
    assert res.status == "success"
    assert res.predictions.diabetes is not None
    assert res.predictions.cardiovascular is not None


def test_7_diabetes_prediction_still_works():
    """7. Test that Diabetes prediction pipeline processes EMR-sourced patient."""
    payload = get_sample_emr_payload()
    response = process_emr_patient(payload)

    diab = response.predictions.diabetes
    assert 0 <= diab.risk_percentage <= 100
    assert diab.risk_level in ["Low", "Moderate", "High"]
    assert len(diab.summary_note) > 0


def test_8_cvd_prediction_still_works():
    """8. Test that CVD prediction pipeline processes EMR-sourced patient."""
    payload = get_sample_emr_payload()
    response = process_emr_patient(payload)

    cvd = response.predictions.cardiovascular
    assert 0 <= cvd.risk_percentage <= 100
    assert cvd.risk_level in ["Low", "Moderate", "High"]
    assert len(cvd.summary_note) > 0


def test_9_xai_output_remains_available():
    """9. Test that explainable factor attributions are returned for EMR patient."""
    payload = get_sample_emr_payload()
    response = process_emr_patient(payload)

    # Check contributing factors list is populated for both models
    assert len(response.predictions.diabetes.contributing_factors) > 0
    assert len(response.predictions.cardiovascular.contributing_factors) > 0

    # Ensure clinical summary notes are present
    assert "risk" in response.predictions.diabetes.summary_note.lower()
    assert "risk" in response.predictions.cardiovascular.summary_note.lower()


def test_10_no_raw_patient_data_logged():
    """10. Test that raw patient clinical data is not emitted to logger output."""
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    logger = logging.getLogger("iheart.integration.emr")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    payload = get_sample_emr_payload()
    process_emr_patient(payload)

    log_output = log_capture.getvalue()
    logger.removeHandler(handler)

    # Check that private vitals/labs were NOT logged
    assert "138" not in log_output, "Systolic BP should not be logged"
    assert "118.0" not in log_output, "Glucose level should not be logged"
    assert "82.0" not in log_output, "Weight should not be logged"
    assert "HOSP-GENERAL-01" in log_output, "System ID should be logged as operational metadata"


if __name__ == "__main__":
    print("=" * 70)
    print("RUNNING HOSPITAL / EMR INTEGRATION TEST SUITE (10 TESTS)")
    print("=" * 70)

    tests = [
        test_1_valid_mock_emr_payload,
        test_2_emr_to_internal_schema_mapping,
        test_3_missing_required_fields,
        test_4_invalid_field_types,
        test_5_invalid_clinical_values,
        test_6_existing_manual_prediction_flow_still_works,
        test_7_diabetes_prediction_still_works,
        test_8_cvd_prediction_still_works,
        test_9_xai_output_remains_available,
        test_10_no_raw_patient_data_logged,
    ]

    passed = 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"FAIL: {t.__name__} - {str(e)}")

    print("=" * 70)
    print(f"RESULT: {passed}/{len(tests)} TESTS PASSED")
    print("=" * 70)

    if passed != len(tests):
        sys.exit(1)
