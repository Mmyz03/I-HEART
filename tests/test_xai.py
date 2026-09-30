"""
Automated Test Suite for Explainable AI (XAI) & Factor Attribution Resilience
AI-Based Explainable Health Risk Prediction System (I-HEART)
Tests dynamic factor generation, human-understandable clinical terminology,
directional impact, summary note integrity, and failure-isolation resilience.
"""

import sys
from pathlib import Path
from unittest.mock import patch

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
import services.diabetes_predictor as diabetes_module
from services.diabetes_predictor import predict_diabetes, explain_diabetes_factors
import services.cvd_predictor as cvd_module
from services.cvd_predictor import predict_cvd, explain_cvd_factors
from services.prediction_service import analyze_unified_patient


def make_patient(
    age=35,
    gender="Female",
    height=165.0,
    weight=None,
    bmi=22.0,
    sbp=115,
    dbp=75,
    hr=70,
    glucose=88.0,
    hba1c=5.1,
    chol=175.0,
    smoking="Never",
    activity="Active",
    alcohol="None",
    hyp=False,
    hist_diab=False,
    hist_cvd=False,
):
    if weight is None:
        weight = round(bmi * ((height / 100.0) ** 2), 1)

    return UnifiedPatientProfile(
        patient_id="XAI-TEST-001",
        demographics=Demographics(age=age, gender=gender),
        physical=PhysicalMeasurements(height_cm=height, weight_kg=weight, bmi=bmi),
        vitals=VitalSigns(systolic_bp=sbp, diastolic_bp=dbp, heart_rate=hr),
        laboratory=LaboratoryData(
            glucose=glucose,
            hba1c=hba1c,
            total_cholesterol=chol,
        ),
        lifestyle=LifestyleData(
            smoking=smoking,
            physical_activity=activity,
            alcohol=alcohol,
        ),
        medical_history=MedicalHistory(
            hypertension=hyp,
            existing_diabetes=False,
            family_history_diabetes=hist_diab,
            family_history_cvd=hist_cvd,
        ),
    )


# =============================================================================
# 1. Diabetes XAI Factor Dynamic Generation
# =============================================================================

def test_diabetes_xai_optimal_indicators():
    p = make_patient(glucose=85.0, hba1c=5.0, bmi=21.0, age=30)
    factors = explain_diabetes_factors(p, 0.05)
    assert any("Optimal fasting glucose" in f for f in factors)
    assert not any("Elevated" in f for f in factors)


def test_diabetes_xai_elevated_indicators():
    p = make_patient(glucose=175.0, hba1c=7.8, bmi=33.5, age=55, hyp=True, hist_diab=True)
    factors = explain_diabetes_factors(p, 0.85)
    factor_text = " ".join(factors)
    assert "Elevated fasting plasma glucose" in factor_text
    assert "Elevated HbA1c" in factor_text
    assert "High Body Mass Index" in factor_text
    assert "Obese" in factor_text


def test_diabetes_xai_prediabetic_indicators():
    p = make_patient(glucose=115.0, hba1c=6.0, bmi=27.2, age=52)
    factors = explain_diabetes_factors(p, 0.40)
    factor_text = " ".join(factors)
    assert "Pre-diabetic fasting glucose range" in factor_text
    assert "Borderline HbA1c" in factor_text
    assert "Overweight" in factor_text


# =============================================================================
# 2. Cardiovascular Disease XAI Factor Dynamic Generation
# =============================================================================

def test_cvd_xai_optimal_indicators():
    p = make_patient(sbp=115, dbp=72, chol=170.0, smoking="Never", age=32)
    factors = explain_cvd_factors(p, 0.06)
    factor_text = " ".join(factors)
    assert "Optimal resting blood pressure" in factor_text
    assert "Stage" not in factor_text


def test_cvd_xai_stage1_hypertension_and_smoking():
    p = make_patient(sbp=136, dbp=86, chol=215.0, smoking="Current", age=50)
    factors = explain_cvd_factors(p, 0.55)
    factor_text = " ".join(factors)
    assert "Stage 1 Hypertension" in factor_text
    assert "Active tobacco smoking" in factor_text
    assert "Borderline total cholesterol" in factor_text


def test_cvd_xai_stage2_hypertension_and_high_cholesterol():
    p = make_patient(sbp=162, dbp=98, chol=265.0, smoking="Never", age=62, hist_cvd=True)
    factors = explain_cvd_factors(p, 0.90)
    factor_text = " ".join(factors)
    assert "Stage 2 Hypertension" in factor_text
    assert "High total cholesterol" in factor_text
    assert "Age demographic risk" in factor_text
    assert "Family history of cardiovascular disease" in factor_text


# =============================================================================
# 3. Clinical Terminology & Human Understandability
# =============================================================================

def test_xai_feature_names_are_human_understandable():
    """Verify explanations use clear medical terms, never cryptic ML column names."""
    p = make_patient(glucose=160.0, sbp=150, dbp=95, chol=250.0, smoking="Current")
    d_res = predict_diabetes(p)
    c_res = predict_cvd(p)

    all_factors = d_res.contributing_factors + c_res.contributing_factors
    for factor in all_factors:
        # Must not contain raw dataset column names
        assert "ap_hi" not in factor
        assert "ap_lo" not in factor
        assert "gluc" not in factor or "glucose" in factor.lower()
        assert "cholesterol" in factor.lower() or "chol" not in factor
        assert "smoke_1" not in factor
        assert "alco" not in factor
        assert "hb_a1c" not in factor


def test_xai_summary_note_integrity():
    """Verify summary notes are populated with clinical narrative across risk levels."""
    p_low = make_patient(glucose=85.0, sbp=110, dbp=70)
    res_low_d = predict_diabetes(p_low)
    res_low_c = predict_cvd(p_low)
    assert "low" in res_low_d.summary_note.lower()
    assert "low" in res_low_c.summary_note.lower()

    p_high = make_patient(glucose=185.0, sbp=165, dbp=105, age=65, weight=95.0, bmi=33.0)
    res_high_d = predict_diabetes(p_high)
    res_high_c = predict_cvd(p_high)
    assert len(res_high_d.summary_note) > 20
    assert len(res_high_c.summary_note) > 20


# =============================================================================
# 4. Dynamic Connection to Model (Not Static / Hardcoded)
# =============================================================================

def test_xai_dynamically_reflects_patient_changes():
    """Verify that changing a clinical parameter directly changes the XAI factors."""
    p1 = make_patient(glucose=85.0)
    factors1 = explain_diabetes_factors(p1, 0.1)

    p2 = make_patient(glucose=180.0)
    factors2 = explain_diabetes_factors(p2, 0.8)

    assert factors1 != factors2
    assert "Optimal" in factors1[0]
    assert "Elevated" in factors2[0]


# =============================================================================
# 5. XAI Failure Isolation & Prediction Resilience
# =============================================================================

def test_diabetes_prediction_resilience_on_xai_failure():
    """Verify predict_diabetes returns valid prediction even if XAI throws an exception."""
    patient = make_patient(glucose=150.0)
    with patch("services.diabetes_predictor.explain_diabetes_factors", side_effect=RuntimeError("Simulated XAI Failure")):
        res = predict_diabetes(patient)
        assert res is not None
        assert 0 <= res.risk_percentage <= 100
        assert res.risk_level in ["Low", "Moderate", "High"]
        assert len(res.summary_note) > 0
        assert len(res.contributing_factors) > 0
        assert "temporarily unavailable" in res.contributing_factors[0].lower()


def test_cvd_prediction_resilience_on_xai_failure():
    """Verify predict_cvd returns valid prediction even if XAI throws an exception."""
    patient = make_patient(sbp=155, dbp=95)
    with patch("services.cvd_predictor.explain_cvd_factors", side_effect=RuntimeError("Simulated XAI Failure")):
        res = predict_cvd(patient)
        assert res is not None
        assert 0 <= res.risk_percentage <= 100
        assert res.risk_level in ["Low", "Moderate", "High"]
        assert len(res.summary_note) > 0
        assert len(res.contributing_factors) > 0
        assert "temporarily unavailable" in res.contributing_factors[0].lower()


def test_orchestrator_resilience_on_dual_xai_failure():
    """Verify analyze_unified_patient completes successfully even if BOTH XAI routines fail."""
    patient = make_patient()
    with patch("services.diabetes_predictor.explain_diabetes_factors", side_effect=Exception("XAI Fail 1")), \
         patch("services.cvd_predictor.explain_cvd_factors", side_effect=Exception("XAI Fail 2")):
        response = analyze_unified_patient(patient)
        assert response.status == "success"
        assert response.predictions.diabetes.risk_percentage >= 0
        assert response.predictions.cardiovascular.risk_percentage >= 0


# =============================================================================
# Runner
# =============================================================================

TESTS = [
    test_diabetes_xai_optimal_indicators,
    test_diabetes_xai_elevated_indicators,
    test_diabetes_xai_prediabetic_indicators,
    test_cvd_xai_optimal_indicators,
    test_cvd_xai_stage1_hypertension_and_smoking,
    test_cvd_xai_stage2_hypertension_and_high_cholesterol,
    test_xai_feature_names_are_human_understandable,
    test_xai_summary_note_integrity,
    test_xai_dynamically_reflects_patient_changes,
    test_diabetes_prediction_resilience_on_xai_failure,
    test_cvd_prediction_resilience_on_xai_failure,
    test_orchestrator_resilience_on_dual_xai_failure,
]


def run_tests():
    print("=" * 70)
    print("RUNNING XAI EXPLAINABILITY & FAILURE RESILIENCE TEST SUITE")
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
    print(f"XAI TEST RESULTS: {passed} PASSED, {failed} FAILED (TOTAL {len(TESTS)})")
    print("=" * 70)
    return passed, failed, 0


if __name__ == "__main__":
    passed, failed, skipped = run_tests()
    if failed > 0:
        sys.exit(1)
