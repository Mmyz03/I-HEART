"""
Diabetes Standalone Prediction Harness
AI-Based Explainable Health Risk Prediction System
Validates prediction capability on individual patient feature vectors.
"""

from pathlib import Path
import pandas as pd
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "models" / "diabetes"


def predict_diabetes_risk(feature_dict: dict) -> dict:
    """
    Takes a raw feature dictionary, transforms using fitted preprocessor,
    and returns prediction class (0/1), probability, and estimated risk level.
    """
    model_path = MODEL_DIR / "diabetes_model.joblib"
    preprocessor_path = MODEL_DIR / "diabetes_preprocessor.joblib"

    if not model_path.exists() or not preprocessor_path.exists():
        raise FileNotFoundError(f"Trained artifacts missing in {MODEL_DIR}. Run ml/diabetes/train.py first.")

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)

    # Convert single dict to DataFrame
    df = pd.DataFrame([feature_dict])

    X_trans = preprocessor.transform(df)
    prob = float(model.predict_proba(X_trans)[0, 1])
    pred = int(model.predict(X_trans)[0])

    pct = int(round(prob * 100))
    if pct >= 70 or pred == 1:
        risk_level = "High"
    elif pct >= 35:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    return {
        "prediction": pred,
        "probability": round(prob, 4),
        "risk_percentage": pct,
        "risk_level": risk_level
    }


if __name__ == "__main__":
    sample_low_risk = {
        "gender": "Female",
        "age": 28,
        "hypertension": 0,
        "heart_disease": 0,
        "smoking_history": "never",
        "bmi": 21.5,
        "HbA1c_level": 5.2,
        "blood_glucose_level": 88
    }

    sample_high_risk = {
        "gender": "Male",
        "age": 58,
        "hypertension": 1,
        "heart_disease": 1,
        "smoking_history": "current",
        "bmi": 32.4,
        "HbA1c_level": 7.1,
        "blood_glucose_level": 168
    }

    print("Sample Low Risk Patient Result:")
    print(predict_diabetes_risk(sample_low_risk))

    print("\nSample High Risk Patient Result:")
    print(predict_diabetes_risk(sample_high_risk))
