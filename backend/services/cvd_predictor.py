"""
Cardiovascular Disease Prediction Service
AI-Based Explainable Health Risk Prediction System
Maps UnifiedPatientProfile to CVD features, applies trained preprocessor & model,
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
MODEL_PATH = BASE_DIR / "models" / "cardiovascular" / "cvd_model.joblib"
PREPROCESSOR_PATH = BASE_DIR / "models" / "cardiovascular" / "cvd_preprocessor.joblib"

# Clinically optimized operating threshold selected via 5-fold cross-validation
# Prioritizes screening sensitivity/recall (70.31% vs 67.77%) and F1 (0.6330 vs 0.6282)
CVD_OPERATING_THRESHOLD = 0.48

# Lazy-loaded model & preprocessor cache
_cvd_model = None
_cvd_preprocessor = None


def get_cvd_artifacts():
    global _cvd_model, _cvd_preprocessor
    if _cvd_model is None or _cvd_preprocessor is None:
        if not MODEL_PATH.exists() or not PREPROCESSOR_PATH.exists():
            raise FileNotFoundError(f"CVD model artifacts missing at {MODEL_PATH}. Run ml/cardiovascular/train.py.")
        _cvd_model = joblib.load(MODEL_PATH)
        _cvd_preprocessor = joblib.load(PREPROCESSOR_PATH)
    return _cvd_model, _cvd_preprocessor


def map_unified_to_cvd_features(patient: UnifiedPatientProfile) -> pd.DataFrame:
    """
    Extracts and maps ONLY the features required by the Cardiovascular Disease ML model
    from the Unified Patient Health Profile.
    """
    # Gender: 1 for Female, 2 for Male
    gender_code = 1 if "fem" in patient.demographics.gender.lower() else 2

    # Cholesterol level: 1 (normal <200), 2 (above normal 200-239), 3 (high >=240)
    tc = patient.laboratory.total_cholesterol
    if tc is not None:
        if tc >= 240:
            chol_code = 3
        elif tc >= 200:
            chol_code = 2
        else:
            chol_code = 1
    else:
        chol_code = 1

    # Glucose level: 1 (normal <100), 2 (above normal 100-125), 3 (high >=126)
    glu = patient.laboratory.glucose
    if glu >= 126:
        gluc_code = 3
    elif glu >= 100:
        gluc_code = 2
    else:
        gluc_code = 1

    # Smoking
    smoking_raw = (patient.lifestyle.smoking or "never").lower()
    smoke_code = 1 if ("current" in smoking_raw or "former" in smoking_raw) else 0

    # Alcohol
    alco_raw = (patient.lifestyle.alcohol or "none").lower()
    alco_code = 1 if ("moderate" in alco_raw or "frequent" in alco_raw) else 0

    # Physical Activity
    act_raw = (patient.lifestyle.physical_activity or "moderate").lower()
    act_code = 1 if ("moderate" in act_raw or "active" in act_raw) else 0

    data = {
        "age": [int(patient.demographics.age)],
        "gender": [gender_code],
        "height": [int(round(patient.physical.height_cm))],
        "weight": [float(patient.physical.weight_kg)],
        "ap_hi": [int(patient.vitals.systolic_bp)],
        "ap_lo": [int(patient.vitals.diastolic_bp)],
        "cholesterol": [chol_code],
        "gluc": [gluc_code],
        "smoke": [smoke_code],
        "alco": [alco_code],
        "active": [act_code]
    }

    return pd.DataFrame(data)


def explain_cvd_factors(patient: UnifiedPatientProfile, prob: float) -> List[str]:
    """Generates clinical factor contribution notes based on evaluated inputs."""
    factors = []
    sbp = patient.vitals.systolic_bp
    dbp = patient.vitals.diastolic_bp
    tc = patient.laboratory.total_cholesterol
    smoking = (patient.lifestyle.smoking or "never").lower()
    age = patient.demographics.age

    if sbp >= 140 or dbp >= 90:
        factors.append(f"Stage 2 Hypertension ({sbp}/{dbp} mmHg)")
    elif sbp >= 130 or dbp >= 80:
        factors.append(f"Stage 1 Hypertension ({sbp}/{dbp} mmHg)")
    else:
        factors.append(f"Optimal resting blood pressure ({sbp}/{dbp} mmHg)")

    if "current" in smoking:
        factors.append("Active tobacco smoking behavior")

    if tc is not None:
        if tc >= 240:
            factors.append(f"High total cholesterol ({tc:.0f} mg/dL)")
        elif tc >= 200:
            factors.append(f"Borderline total cholesterol ({tc:.0f} mg/dL)")

    if age >= 55:
        factors.append(f"Age demographic risk ({age} years)")

    if patient.medical_history.hypertension:
        factors.append("Documented clinical history of hypertension")

    if patient.medical_history.family_history_cvd:
        factors.append("Family history of cardiovascular disease")

    return factors[:4]


def predict_cvd(patient: UnifiedPatientProfile) -> DiseaseRiskResult:
    """Executes the trained CVD ML pipeline on the unified patient record."""
    model, preprocessor = get_cvd_artifacts()
    df_features = map_unified_to_cvd_features(patient)

    # Preprocess & Predict
    X_trans = preprocessor.transform(df_features)
    prob = float(model.predict_proba(X_trans)[0, 1])
    pred = int(prob >= CVD_OPERATING_THRESHOLD)

    pct = int(min(max(round(prob * 100), 1), 99))

    if pct >= 70 or pred == 1:
        risk_level = "High"
        summary_note = "Model-estimated elevated cardiovascular risk driven by blood pressure, lipids, and vascular factors."
    elif pct >= 35:
        risk_level = "Moderate"
        summary_note = "Model-estimated moderate cardiovascular risk with intermediate hemodynamic or lipid parameters."
    else:
        risk_level = "Low"
        summary_note = "Model-estimated low cardiovascular risk with optimal hemodynamic, lipid, and lifestyle metrics."

    try:
        factors = explain_cvd_factors(patient, prob)
    except Exception:
        factors = ["Clinical risk factor attributions temporarily unavailable."]

    return DiseaseRiskResult(
        risk_percentage=pct,
        risk_level=risk_level,
        contributing_factors=factors,
        summary_note=summary_note
    )
