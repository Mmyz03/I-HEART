"""
Automated Test Suite for Machine Learning Pipelines & Backend API
AI-Based Explainable Health Risk Prediction System
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from schemas import (
    UnifiedPatientProfile,
    Demographics,
    PhysicalMeasurements,
    VitalSigns,
    LaboratoryData,
    LifestyleData,
    MedicalHistory
)
from services.diabetes_predictor import get_diabetes_artifacts, map_unified_to_diabetes_features, predict_diabetes
from services.cvd_predictor import get_cvd_artifacts, map_unified_to_cvd_features, predict_cvd
from services.prediction_service import analyze_unified_patient


def get_sample_patient(glucose=115.0, sbp=135, dbp=85, age=50):
    return UnifiedPatientProfile(
        patient_id="TEST-PATIENT-001",
        demographics=Demographics(age=age, gender="Male"),
        physical=PhysicalMeasurements(height_cm=175.0, weight_kg=80.0, bmi=26.1),
        vitals=VitalSigns(systolic_bp=sbp, diastolic_bp=dbp, heart_rate=72),
        laboratory=LaboratoryData(
            glucose=glucose,
            hba1c=6.0,
            total_cholesterol=210.0,
            hdl=45.0,
            ldl=130.0,
            triglycerides=150.0
        ),
        lifestyle=LifestyleData(
            smoking="Current",
            physical_activity="Sedentary",
            alcohol="Moderate"
        ),
        medical_history=MedicalHistory(
            hypertension=True,
            existing_diabetes=False,
            family_history_diabetes=True,
            family_history_cvd=True
        )
    )


def test_diabetes_artifacts_load():
    """Test that saved diabetes model and preprocessor load correctly."""
    model, preprocessor = get_diabetes_artifacts()
    assert model is not None
    assert preprocessor is not None
    assert hasattr(model, "predict_proba")
    assert hasattr(preprocessor, "transform")


def test_cvd_artifacts_load():
    """Test that saved CVD model and preprocessor load correctly."""
    model, preprocessor = get_cvd_artifacts()
    assert model is not None
    assert preprocessor is not None
    assert hasattr(model, "predict_proba")
    assert hasattr(preprocessor, "transform")


def test_diabetes_feature_mapping():
    """Test mapping unified patient object to diabetes feature DataFrame."""
    patient = get_sample_patient()
    df = map_unified_to_diabetes_features(patient)
    assert len(df) == 1
    assert "gender" in df.columns
    assert "blood_glucose_level" in df.columns
    assert "HbA1c_level" in df.columns
    assert df["blood_glucose_level"].iloc[0] == 115.0


def test_cvd_feature_mapping():
    """Test mapping unified patient object to CVD feature DataFrame."""
    patient = get_sample_patient()
    df = map_unified_to_cvd_features(patient)
    assert len(df) == 1
    assert "ap_hi" in df.columns
    assert "ap_lo" in df.columns
    assert "cholesterol" in df.columns
    assert df["ap_hi"].iloc[0] == 135


def test_diabetes_prediction_service():
    """Test diabetes prediction returns probability, classification, risk level, and contributing factors."""
    patient = get_sample_patient(glucose=170.0)
    result = predict_diabetes(patient)
    assert result.risk_percentage >= 0 and result.risk_percentage <= 100
    assert result.risk_level in ["Low", "Moderate", "High"]
    assert len(result.contributing_factors) > 0
    assert isinstance(result.summary_note, str)


def test_cvd_prediction_service():
    """Test CVD prediction returns probability, classification, risk level, and contributing factors."""
    patient = get_sample_patient(sbp=160, dbp=100)
    result = predict_cvd(patient)
    assert result.risk_percentage >= 0 and result.risk_percentage <= 100
    assert result.risk_level in ["Low", "Moderate", "High"]
    assert len(result.contributing_factors) > 0
    assert isinstance(result.summary_note, str)


def test_unified_analyze_orchestrator():
    """Test analyze_unified_patient returns full AnalysisResponse with both predictions."""
    patient = get_sample_patient()
    response = analyze_unified_patient(patient)
    assert response.status == "success"
    assert response.prediction_source == "trained_ml_models"
    assert response.predictions.diabetes.risk_level in ["Low", "Moderate", "High"]
    assert response.predictions.cardiovascular.risk_level in ["Low", "Moderate", "High"]
    assert "academic" in response.disclaimer.lower()


def test_diabetes_probability_range_and_classes():
    """Verify diabetes probability is between 0 and 1, risk percentage between 1 and 99, valid class."""
    patient = get_sample_patient(glucose=190.0)
    model, preprocessor = get_diabetes_artifacts()
    df = map_unified_to_diabetes_features(patient)
    X_trans = preprocessor.transform(df)
    prob = float(model.predict_proba(X_trans)[0, 1])
    pred = int(model.predict(X_trans)[0])
    assert 0.0 <= prob <= 1.0, f"Probability {prob} out of bounds"
    assert pred in [0, 1], f"Predicted class {pred} invalid"

    res = predict_diabetes(patient)
    assert 1 <= res.risk_percentage <= 99
    assert res.risk_level in ["Low", "Moderate", "High"]


def test_cvd_probability_range_and_classes():
    """Verify CVD probability is between 0 and 1, risk percentage between 1 and 99, valid class."""
    patient = get_sample_patient(sbp=165, dbp=105)
    model, preprocessor = get_cvd_artifacts()
    df = map_unified_to_cvd_features(patient)
    X_trans = preprocessor.transform(df)
    prob = float(model.predict_proba(X_trans)[0, 1])
    pred = int(model.predict(X_trans)[0])
    assert 0.0 <= prob <= 1.0, f"Probability {prob} out of bounds"
    assert pred in [0, 1], f"Predicted class {pred} invalid"

    res = predict_cvd(patient)
    assert 1 <= res.risk_percentage <= 99
    assert res.risk_level in ["Low", "Moderate", "High"]


def test_diabetes_missing_optional_hba1c():
    """Verify pipeline safely handles patient with missing optional HbA1c."""
    patient = get_sample_patient()
    patient.laboratory.hba1c = None
    res = predict_diabetes(patient)
    assert res.risk_percentage >= 0
    assert res.risk_level in ["Low", "Moderate", "High"]


def test_cvd_missing_optional_lipids():
    """Verify pipeline safely handles patient with missing optional lipid panel."""
    patient = get_sample_patient()
    patient.laboratory.total_cholesterol = None
    patient.laboratory.hdl = None
    patient.laboratory.ldl = None
    patient.laboratory.triglycerides = None
    res = predict_cvd(patient)
    assert res.risk_percentage >= 0
    assert res.risk_level in ["Low", "Moderate", "High"]


if __name__ == "__main__":
    print("Running ML Pipeline & Backend Tests...")
    test_diabetes_artifacts_load()
    print("PASS: Diabetes artifacts load test")
    test_cvd_artifacts_load()
    print("PASS: CVD artifacts load test")
    test_diabetes_feature_mapping()
    print("PASS: Diabetes feature mapping test")
    test_cvd_feature_mapping()
    print("PASS: CVD feature mapping test")
    test_diabetes_prediction_service()
    print("PASS: Diabetes prediction service test")
    test_cvd_prediction_service()
    print("PASS: CVD prediction service test")
    test_unified_analyze_orchestrator()
    print("PASS: Unified analysis orchestrator test")
    test_diabetes_probability_range_and_classes()
    print("PASS: Diabetes probability range & classes test")
    test_cvd_probability_range_and_classes()
    print("PASS: CVD probability range & classes test")
    test_diabetes_missing_optional_hba1c()
    print("PASS: Diabetes missing optional HbA1c test")
    test_cvd_missing_optional_lipids()
    print("PASS: CVD missing optional lipids test")
    print("\nALL AUTOMATED TESTS PASSED SUCCESSFULLY (11/11)")
