"""
Diabetes Prediction Service
AI-Based Explainable Health Risk Prediction System
Maps UnifiedPatientProfile to diabetes features, applies trained preprocessor & model,
and returns real model-estimated risk probabilities and factor attributions.
"""

from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import joblib

try:
    from schemas import UnifiedPatientProfile, DiseaseRiskResult
except ImportError:
    from ..schemas import UnifiedPatientProfile, DiseaseRiskResult

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "models" / "diabetes" / "diabetes_model.joblib"
PREPROCESSOR_PATH = BASE_DIR / "models" / "diabetes" / "diabetes_preprocessor.joblib"

# Lazy-loaded model & preprocessor cache
_diabetes_model = None
_diabetes_preprocessor = None


def get_diabetes_artifacts():
    global _diabetes_model, _diabetes_preprocessor
    if _diabetes_model is None or _diabetes_preprocessor is None:
        if not MODEL_PATH.exists() or not PREPROCESSOR_PATH.exists():
            raise FileNotFoundError(f"Diabetes model artifacts missing at {MODEL_PATH}. Run ml/diabetes/train.py.")
        _diabetes_model = joblib.load(MODEL_PATH)
        _diabetes_preprocessor = joblib.load(PREPROCESSOR_PATH)
    return _diabetes_model, _diabetes_preprocessor


def map_unified_to_diabetes_features(patient: UnifiedPatientProfile) -> pd.DataFrame:
    """
    Extracts and maps ONLY the features required by the Diabetes ML model
    from the Unified Patient Health Profile.
    """
    # Map smoking status to dataset categories
    smoking_raw = (patient.lifestyle.smoking or "never").lower()
    if "current" in smoking_raw:
        smoking_hist = "current"
    elif "former" in smoking_raw:
        smoking_hist = "former"
    elif "never" in smoking_raw:
        smoking_hist = "never"
    else:
        smoking_hist = "never"

    # Map gender
    gender_val = patient.demographics.gender
    if gender_val not in ["Female", "Male", "Other"]:
        gender_val = "Female" if "fem" in gender_val.lower() else "Male"

    # Map heart disease (family history or diagnosed)
    heart_dis = 1 if patient.medical_history.family_history_cvd else 0
    hyp_val = 1 if patient.medical_history.hypertension else 0

    # HbA1c handling (if missing/None, fallback to median baseline 5.5)
    hba1c_val = patient.laboratory.hba1c if patient.laboratory.hba1c is not None else 5.5

    data = {
        "gender": [gender_val],
        "age": [patient.demographics.age],
        "hypertension": [hyp_val],
        "heart_disease": [heart_dis],
        "smoking_history": [smoking_hist],
        "bmi": [patient.physical.bmi],
        "HbA1c_level": [hba1c_val],
        "blood_glucose_level": [patient.laboratory.glucose]
    }

    return pd.DataFrame(data)


def explain_diabetes_factors(patient: UnifiedPatientProfile, prob: float) -> List[str]:
    """Generates clinical factor contribution notes based on evaluated inputs."""
    factors = []
    glucose = patient.laboratory.glucose
    hba1c = patient.laboratory.hba1c
    bmi = patient.physical.bmi
    age = patient.demographics.age

    if glucose >= 140:
        factors.append(f"Elevated fasting plasma glucose ({glucose:.0f} mg/dL)")
    elif glucose >= 100:
        factors.append(f"Pre-diabetic fasting glucose range ({glucose:.0f} mg/dL)")
    else:
        factors.append(f"Optimal fasting glucose ({glucose:.0f} mg/dL)")

    if hba1c is not None:
        if hba1c >= 6.5:
            factors.append(f"Elevated HbA1c ({hba1c:.1f}%) in diabetic range")
        elif hba1c >= 5.7:
            factors.append(f"Borderline HbA1c ({hba1c:.1f}%) in pre-diabetic range")

    if bmi >= 30:
        factors.append(f"High Body Mass Index (BMI: {bmi:.1f} kg/m² - Obese)")
    elif bmi >= 25:
        factors.append(f"Elevated Body Mass Index (BMI: {bmi:.1f} kg/m² - Overweight)")

    if age >= 50:
        factors.append(f"Age demographic risk factor ({age} years)")

    if patient.medical_history.hypertension:
        factors.append("Diagnosed hypertension comorbidity")

    if patient.medical_history.family_history_diabetes:
        factors.append("Documented family history of diabetes")

    return factors[:4]


def predict_diabetes(patient: UnifiedPatientProfile) -> DiseaseRiskResult:
    """Executes the trained Diabetes ML pipeline on the unified patient record."""
    model, preprocessor = get_diabetes_artifacts()
    df_features = map_unified_to_diabetes_features(patient)

    # Preprocess & Predict
    X_trans = preprocessor.transform(df_features)
    prob = float(model.predict_proba(X_trans)[0, 1])
    pred = int(model.predict(X_trans)[0])

    pct = int(min(max(round(prob * 100), 1), 99))

    if pct >= 70 or pred == 1:
        risk_level = "High"
        summary_note = "Model-estimated high risk profile based on glycemic indicators, adiposity, and metabolic parameters."
    elif pct >= 35:
        risk_level = "Moderate"
        summary_note = "Model-estimated moderate risk profile with intermediate metabolic or glycemic metrics."
    else:
        risk_level = "Low"
        summary_note = "Model-estimated low risk profile with physiological indicators within standard baseline limits."

    try:
        factors = explain_diabetes_factors(patient, prob)
    except Exception:
        factors = ["Clinical risk factor attributions temporarily unavailable."]

    return DiseaseRiskResult(
        risk_percentage=pct,
        risk_level=risk_level,
        contributing_factors=factors,
        summary_note=summary_note
    )
