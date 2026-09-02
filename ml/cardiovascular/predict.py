"""
Cardiovascular Disease Standalone Prediction Harness
AI-Based Explainable Health Risk Prediction System
Validates prediction capability on individual patient feature vectors.
"""

from pathlib import Path
import pandas as pd
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "models" / "cardiovascular"


def predict_cvd_risk(feature_dict: dict) -> dict:
    """
    Takes a raw feature dictionary, transforms using fitted preprocessor,
    and returns prediction class (0/1), probability, and estimated risk level.
    """
    model_path = MODEL_DIR / "cvd_model.joblib"
    preprocessor_path = MODEL_DIR / "cvd_preprocessor.joblib"

    if not model_path.exists() or not preprocessor_path.exists():
        raise FileNotFoundError(f"Trained artifacts missing in {MODEL_DIR}. Run ml/cardiovascular/train.py first.")

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
        "age": 35,
        "gender": 1,
        "height": 165,
        "weight": 60.0,
        "ap_hi": 115,
        "ap_lo": 75,
        "cholesterol": 1,
        "gluc": 1,
        "smoke": 0,
        "alco": 0,
        "active": 1
    }

    sample_high_risk = {
        "age": 62,
        "gender": 2,
        "height": 178,
        "weight": 98.0,
        "ap_hi": 155,
        "ap_lo": 98,
        "cholesterol": 3,
        "gluc": 2,
        "smoke": 1,
        "alco": 1,
        "active": 0
    }

    print("Sample Low CVD Risk Patient Result:")
    print(predict_cvd_risk(sample_low_risk))

    print("\nSample High CVD Risk Patient Result:")
    print(predict_cvd_risk(sample_high_risk))
